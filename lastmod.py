"""When each article last changed, recorded in content/lastmod.json.

Sitemap lastmod, the visible "Updated" date and Article dateModified all came from
frontmatter `updated` or `date`, which nobody bumps. /articles/speculative-decoding/
said 2026-03-07 after its video landed on 2026-10-27, and last week's fact fixes and
retitles left their dates where they were. A lastmod that never moves teaches a
crawler to ignore it.

The real answer is the date of the last commit to a page's sources, but the build
cannot ask git for it: Cloudflare Pages clones shallow, and in a shallow clone every
file's last commit is the tip commit, so every page would claim to be new. So the
dates are computed where full history exists and committed:

    python3 lastmod.py            # refresh entries whose sources changed
    python3 lastmod.py --check    # exit 1 if any entry is stale (CI runs this)
    python3 lastmod.py --reseed   # recompute every entry from git history

Each entry stores a hash of the page's sources. The build uses an entry only while
the hash still matches, so a stale manifest can never pin an edited page to an old
date silently: the build falls back to frontmatter and warns, and CI goes red.

A refresh dates a changed entry from git when its sources are committed, and with
today's date when they carry uncommitted edits, which is the normal case when it is
run just before a commit.

A page's sources are its post file, its figure sources in content/diagrams/<slug>/,
and, when it declares a video, content/videos/<video>/ and static/videos/<video>/.
Share-card sources (og.mmd) and rendered images are left out: a restyle of every
card is not a change to what any article says.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parent
MANIFEST = Path("content/lastmod.json")
POSTS = Path("content/posts")


def post_slug(path: Path, meta: dict) -> str:
    # Mirrors build.py: frontmatter slug wins, else the file stem.
    return str(meta.get("slug") or path.stem)


def ignored(path: Path) -> bool:
    """Share-card sources (og.mmd) are not article content: one commit that restyled
    every card would otherwise date 60-odd unchanged articles to the same day."""
    return path.name == ".DS_Store" or path.stem == "og" or path.stem.startswith("og.")


def source_paths(post_path: Path, slug: str, video) -> list[Path]:
    """Every file whose change counts as a change to the page, sorted."""
    roots = [Path("content/diagrams") / slug]
    if video:
        roots += [Path("content/videos") / str(video), Path("static/videos") / str(video)]
    files = [post_path]
    for root in roots:
        if root.is_dir():
            files.extend(p for p in root.rglob("*") if p.is_file() and not ignored(p))
    return sorted(set(files), key=lambda p: p.as_posix())


def sources_hash(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def discover() -> dict[str, list[Path]]:
    """slug -> sources, for every post file, drafts included, so a draft that is
    published later already has an entry."""
    pages = {}
    for post_path in sorted(POSTS.rglob("*.md")):
        meta = frontmatter.load(post_path).metadata
        slug = post_slug(post_path, meta)
        pages[slug] = source_paths(post_path, slug, meta.get("video"))
    return pages


def load_manifest(path: Path = MANIFEST) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


def is_shallow() -> bool:
    return _git("rev-parse", "--is-shallow-repository") == "true"


def has_uncommitted(paths: list[Path]) -> bool:
    return bool(_git("status", "--porcelain", "--", *[p.as_posix() for p in paths]))


def file_last_changed(path: Path) -> str | None:
    """Date of the newest commit that changed this file's content, following renames.

    A pure rename (R100) is skipped: on 2026-10-04 one commit renamed 60 post files to
    their canonical slugs without changing a byte or a URL, and a plain `git log`
    would date all 60 pages to that day. The date is the committer's, in the
    committer's own timezone, so a commit made just after midnight in Mumbai keeps
    its local date.
    """
    log = _git("log", "--follow", "-M", "--format=%x00%cI", "--name-status", "--",
               path.as_posix())
    for record in log.split("\0")[1:]:
        lines = [line for line in record.splitlines() if line.strip()]
        if not lines:
            continue
        stamp, statuses = lines[0], [line.split("\t")[0] for line in lines[1:]]
        if statuses and all(status == "R100" for status in statuses):
            continue
        return stamp[:10]
    return None


def last_commit_date(paths: list[Path]) -> str | None:
    """The newest content change across a page's sources."""
    dates = [d for d in (file_last_changed(p) for p in paths) if d]
    return max(dates) if dates else None


def date_for(paths: list[Path], today: str) -> str:
    if has_uncommitted(paths):
        return today
    return last_commit_date(paths) or today


def refresh(manifest: dict, pages: dict, reseed: bool, today: str) -> tuple[dict, list[str]]:
    if is_shallow():
        sys.exit("lastmod.py needs full git history: run `git fetch --unshallow` first")
    updated, changed = {}, []
    for slug, paths in pages.items():
        digest = sources_hash(paths)
        entry = manifest.get(slug)
        if entry and entry.get("sources") == digest and not reseed:
            updated[slug] = entry
            continue
        new = {"lastmod": date_for(paths, today), "sources": digest}
        if new != entry:
            changed.append(f"{slug}: {entry and entry.get('lastmod')} -> {new['lastmod']}")
        updated[slug] = new
    return dict(sorted(updated.items())), changed


def stale_entries(manifest: dict, pages: dict) -> list[str]:
    problems = []
    for slug, paths in pages.items():
        entry = manifest.get(slug)
        if entry is None:
            problems.append(f"{slug}: no entry")
        elif entry.get("sources") != sources_hash(paths):
            problems.append(f"{slug}: sources changed since {entry.get('lastmod')}")
    for slug in manifest:
        if slug not in pages:
            problems.append(f"{slug}: entry for a post that no longer exists")
    return problems


def write_manifest(manifest: dict, path: Path = MANIFEST) -> None:
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if any entry is stale")
    mode.add_argument("--reseed", action="store_true", help="recompute every entry from git")
    args = parser.parse_args()

    import os
    os.chdir(ROOT)
    pages = discover()
    manifest = load_manifest()

    if args.check:
        problems = stale_entries(manifest, pages)
        for line in problems:
            print(f"STALE {line}")
        if problems:
            print(f"{len(problems)} stale lastmod entr(ies). Run `python3 lastmod.py` and commit "
                  "content/lastmod.json with the change.")
            return 1
        print(f"lastmod manifest current: {len(pages)} pages")
        return 0

    updated, changed = refresh(manifest, pages, args.reseed, dt.date.today().isoformat())
    for line in changed:
        print(line)
    if updated != manifest:
        write_manifest(updated)
    print(f"{len(changed)} entr(ies) changed, {len(updated)} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
