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
    python3 lastmod.py --check    # exit 1 if any entry is stale (CI warns on it)
    python3 lastmod.py --reseed   # recompute every entry from git history

Each entry stores a hash of the page's sources. The build uses an entry only while
the hash still matches, so a stale manifest can never pin an edited page to an old
date silently: the build falls back to frontmatter and warns, and so does CI.

A refresh dates a changed entry by the newest commit that changed what its sources
say, and with today's date when the working copy says something HEAD does not,
which is the normal case when it is run just before a commit. On main, the lastmod
workflow runs the refresh after every push and commits the manifest, so a publish
that skipped it is dated from its own commit.

A page's sources are its post file, its figure sources in content/diagrams/<slug>/,
every interactive visual it embeds from static/visuals/, and, when it declares a
video, content/videos/<video>/ and the captions and transcripts in
static/videos/<video>/. Share-card sources (og.mmd), rendered images and video
media (the encoded file, the poster) are left out: a restyle of every card or a
re-encode is not a change to what any article says.

The hash covers what the files say, not where they live, so a pure rename leaves an
entry untouched. A rename that changes the slug moves the old entry's date to the
new slug when the content is identical. Without both, the "refresh before commit"
workflow saw renamed files as uncommitted changes and dated them today.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parent
MANIFEST = Path("content/lastmod.json")
POSTS = Path("content/posts")


# Frontmatter a reader can see on the page. Anything else (seo_title, og_image,
# tags, status, internal notes) can change without the page changing. `updated` is
# left out because it already acts as a floor on the date in build.py.
VISIBLE_FIELDS = ("title", "description", "date", "category", "video", "takeaways", "work_note")

# Files under static/videos/<video>/ that carry words. The encoded video and its
# poster are media: re-encoding them (the WebP poster switch, say) says nothing new.
VIDEO_TEXT_SUFFIXES = {".vtt", ".srt", ".txt", ".json"}


def post_slug(path: Path, meta: dict) -> str:
    # The same rule build.py uses, from build.py, so a filename with capitals or
    # underscores maps to the same key in both. Imported here because build.py
    # imports this module.
    from build import slugify
    return str(meta.get("slug") or slugify(path.stem))


def ignored(path: Path) -> bool:
    """Share-card sources (og.mmd) are not article content: one commit that restyled
    every card would otherwise date 60-odd unchanged articles to the same day."""
    if path.name == ".DS_Store" or path.stem == "og" or path.stem.startswith("og."):
        return True
    parts = path.as_posix().split("/")
    return parts[:2] == ["static", "videos"] and path.suffix.lower() not in VIDEO_TEXT_SUFFIXES


VISUAL_REF = re.compile(r"/static/visuals/([A-Za-z0-9_-]+)(?:\.html)?(?![A-Za-z0-9_.-])")


def embedded_visuals(post_path: Path) -> list[Path]:
    """The static/visuals/*.html files a post embeds, in .html or extensionless form."""
    text = post_path.read_text(encoding="utf-8")
    found = (Path("static/visuals") / f"{name}.html" for name in VISUAL_REF.findall(text))
    return [path for path in found if path.is_file()]


def source_paths(post_path: Path, slug: str, video) -> list[Path]:
    """Every file whose change counts as a change to the page, sorted."""
    roots = [Path("content/diagrams") / slug]
    if video:
        roots += [Path("content/videos") / str(video), Path("static/videos") / str(video)]
    files = [post_path, *embedded_visuals(post_path)]
    for root in roots:
        if root.is_dir():
            files.extend(p for p in root.rglob("*") if p.is_file() and not ignored(p))
    return sorted(set(files), key=lambda p: p.as_posix())


def is_post(path: Path) -> bool:
    return path.suffix == ".md" and path.as_posix().startswith("content/posts/")


def normalize(data: bytes, post: bool, blank_lines_matter: bool = True) -> bytes:
    """What a file says, without the edits a reader cannot see.

    Line endings are unified, trailing whitespace is dropped, and runs of blank lines
    count as one, so a CRLF conversion, stray spaces or an extra blank line do not
    date a page. In HTML and Mermaid sources a blank line never renders, so there
    they are dropped altogether; in Markdown one can split a paragraph, so it counts. Spaces inside a line are kept: indentation is meaningful in code
    blocks and YAML. For a post, only VISIBLE_FIELDS of the frontmatter count.
    Bytes that are not UTF-8 text are compared as they are.
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if post:
        try:
            parsed = frontmatter.loads(text)
        except Exception:
            # An old version in history with frontmatter YAML cannot parse. Compare
            # it as plain text, which makes it differ from its neighbours, as it did
            # for readers: the build fails on it.
            parsed = None
        if parsed is not None:
            visible = {key: parsed.metadata[key] for key in VISIBLE_FIELDS if key in parsed.metadata}
            text = json.dumps(visible, sort_keys=True, default=str) + "\n" + parsed.content
    lines = [line.rstrip() for line in text.split("\n")]
    if not blank_lines_matter:
        lines = [line for line in lines if line]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip("\n")
    return text.encode("utf-8")


BLANK_LINES_INVISIBLE = {".html", ".htm", ".mmd", ".svg"}


def content_digest(data: bytes, path: Path) -> str:
    blank_lines_matter = path.suffix.lower() not in BLANK_LINES_INVISIBLE
    return hashlib.sha256(normalize(data, is_post(path), blank_lines_matter)).hexdigest()


def sources_hash(paths: list[Path]) -> str:
    """A hash of what the files say. Paths are left out on purpose: moving or
    renaming a file is not a change to what the page says."""
    contents = sorted(content_digest(path.read_bytes(), path) for path in paths)
    return hashlib.sha256("\n".join(contents).encode("ascii")).hexdigest()


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


def _blobs(shas: list[str]) -> dict[str, bytes]:
    """Read many blobs in one `git cat-file --batch` call."""
    if not shas:
        return {}
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, check=True,
                          input="".join(f"{sha}\n" for sha in shas).encode("ascii"),
                          capture_output=True)
    out, blobs, pos = proc.stdout, {}, 0
    for sha in shas:
        header_end = out.index(b"\n", pos)
        header = out[pos:header_end].split()
        size = int(header[2])
        blobs[sha] = out[header_end + 1:header_end + 1 + size]
        pos = header_end + 1 + size + 1
    return blobs


def is_shallow() -> bool:
    return _git("rev-parse", "--is-shallow-repository") == "true"


def changed_since_head(paths: list[Path]) -> bool:
    """True when the working copy says something HEAD does not, after normalizing.

    Only reached for a page whose manifest hash no longer matches. A pure rename
    never gets here (the hash ignores paths, and a slug change inherits its orphaned
    entry), so a path that HEAD lacks means new content and counts as a change.
    """
    if not _git("status", "--porcelain", "--", *[p.as_posix() for p in paths]):
        return False
    shas = []
    for path in paths:
        try:
            shas.append(_git("rev-parse", f"HEAD:{path.as_posix()}"))
        except subprocess.CalledProcessError:
            return True
    blobs = _blobs(shas)
    head = sorted(content_digest(blobs[sha], path) for sha, path in zip(shas, paths))
    current = sorted(content_digest(path.read_bytes(), path) for path in paths)
    return head != current


def file_versions(path: Path) -> list[tuple[str, str]]:
    """(date, blob) for each commit that touched the file, newest first, following
    renames. The date is the committer's, in the committer's own timezone, so a
    commit made just after midnight in Mumbai keeps its local date."""
    log = _git("log", "--follow", "-M", "--no-abbrev", "--format=%x00%cI", "--raw", "--",
               path.as_posix())
    versions = []
    for record in log.split("\0")[1:]:
        lines = [line for line in record.splitlines() if line.strip()]
        if not lines:
            continue
        raws = [line for line in lines[1:] if line.startswith(":")]
        if not raws:
            continue
        new_sha = raws[-1].split()[3]
        if set(new_sha) == {"0"}:
            continue  # deleted in this commit
        versions.append((lines[0][:10], new_sha))
    return versions


def file_last_changed(path: Path) -> str | None:
    """Date of the newest commit that changed what the file says.

    Commits whose normalized content equals the version before them are skipped: a
    pure rename (on 2026-10-04 one commit renamed 60 post files), a CRLF conversion,
    a whitespace tidy, or a frontmatter key no reader sees. With no such commit, the
    date the file was added.
    """
    versions = file_versions(path)
    if not versions:
        return None
    blobs = _blobs(sorted({sha for _, sha in versions}))
    digests = [content_digest(blobs[sha], path) for _, sha in versions]
    for i in range(len(versions) - 1):
        if digests[i] != digests[i + 1]:
            return versions[i][0]
    return versions[-1][0]


def last_commit_date(paths: list[Path]) -> str | None:
    """The newest change in what any of a page's sources say."""
    dates = [d for d in (file_last_changed(p) for p in paths) if d]
    return max(dates) if dates else None


def date_for(paths: list[Path], today: str) -> str:
    if changed_since_head(paths):
        return today
    return last_commit_date(paths) or today


def refresh(manifest: dict, pages: dict, reseed: bool, today: str) -> tuple[dict, list[str]]:
    if is_shallow():
        sys.exit("lastmod.py needs full git history: run `git fetch --unshallow` first")
    updated, changed = {}, []
    # Entries whose slug no longer exists, by content hash: a post renamed to a new
    # slug with nothing else changed takes its old date with it.
    orphans = {entry.get("sources"): entry for slug, entry in manifest.items() if slug not in pages}
    for slug, paths in pages.items():
        digest = sources_hash(paths)
        entry = manifest.get(slug)
        if entry and entry.get("sources") == digest and not reseed:
            updated[slug] = entry
            continue
        if entry is None and digest in orphans and not reseed:
            new = dict(orphans[digest])
        else:
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
