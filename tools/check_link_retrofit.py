#!/usr/bin/env python3
"""Deterministic publish gate for internal linking. Charter 2e.

The publish prompt used to *ask* for an inbound retrofit. Asking does not work: the
run self-reported the result and the site accumulated 20 orphan pages, 23% of the
corpus, five of them shipped in the last week. This script is the check the run
cannot pass by claiming it passed.

It inspects the actual staged changeset, not the run's description of it.

    python3 tools/check_link_retrofit.py --slug <new-article-slug>

Exit 0 only when all of these hold:

  1. The new article is staged.
  2. At least one OTHER existing post is staged in the same changeset.
  3. That other post now contains a link to the new article.
  4. The retrofit link sits in a sentence, not a list dump, and its anchor text is
     not "click here", "this article", or the bare slug.
  5. The new article carries at least two outbound article links.
  6. Every outbound target resolves in the freshly built output/sitemap.xml.
  7. Cross-cluster links are reported so a reader can apply the subject test.

Run it after staging and before committing.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
SITEMAP = ROOT / "output" / "sitemap.xml"

ARTICLE_LINK = re.compile(r"\[([^\]]+)\]\((/articles/([a-z0-9][a-z0-9-]*)/)\)")
LAZY_ANCHORS = {
    "click here", "here", "this article", "this post", "read more",
    "learn more", "this guide", "link", "see here",
}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False
    )
    return result.stdout


def staged_files() -> list[str]:
    return [line for line in git("diff", "--cached", "--name-only").splitlines() if line]


def frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{key}:\s*[\"']?([^\"'\n]+)[\"']?\s*$", text, re.M)
    return match.group(1).strip() if match else None


def body_of(text: str) -> str:
    parts = text.split("---", 2)
    return parts[2] if len(parts) > 2 else text


def sitemap_slugs() -> set[str]:
    if not SITEMAP.exists():
        return set()
    root = ET.parse(SITEMAP).getroot()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    slugs = set()
    for node in root.findall("s:url", namespace):
        loc = node.find("s:loc", namespace)
        if loc is None or not loc.text:
            continue
        match = re.search(r"/articles/([a-z0-9][a-z0-9-]*)/$", loc.text)
        if match:
            slugs.add(match.group(1))
    return slugs


def post_path_for(slug: str) -> Path | None:
    direct = POSTS / f"{slug}.md"
    if direct.exists():
        return direct
    for path in POSTS.glob("*.md"):
        if frontmatter_value(path.read_text(encoding="utf-8"), "slug") == slug:
            return path
    return None


def links_in(text: str) -> list[tuple[str, str, str]]:
    """(anchor, url, slug) for every /articles/ link in the prose body."""
    body = body_of(text)
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    return [(m.group(1), m.group(2), m.group(3)) for m in ARTICLE_LINK.finditer(body)]


def line_containing(text: str, url: str) -> str:
    for line in body_of(text).splitlines():
        if url in line:
            return line.strip()
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True, help="slug of the article being published")
    parser.add_argument(
        "--min-outbound", type=int, default=2, help="minimum outbound article links"
    )
    args = parser.parse_args()
    slug = args.slug.strip().strip("/")

    failures: list[str] = []
    notes: list[str] = []

    new_path = post_path_for(slug)
    if new_path is None:
        print(f"FAIL  no post found for slug '{slug}' under content/posts/")
        return 1
    new_text = new_path.read_text(encoding="utf-8")
    new_rel = str(new_path.relative_to(ROOT))

    staged = staged_files()
    if new_rel not in staged:
        failures.append(f"the new article {new_rel} is not staged")

    # --- 2 + 3: a different existing post must be staged AND link to the new slug ---
    other_posts = [
        f for f in staged
        if f.startswith("content/posts/") and f.endswith(".md") and f != new_rel
    ]
    if not other_posts:
        failures.append(
            "no existing post was edited in this changeset. Charter 2e requires an "
            "inbound retrofit: an existing published article must be edited to link "
            "to the new piece. Outbound links alone are half a link."
        )

    retrofit_sources: list[tuple[str, str, str]] = []
    for rel in other_posts:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for anchor, url, target in links_in(text):
            if target == slug:
                retrofit_sources.append((rel, anchor, line_containing(text, url)))

    if other_posts and not retrofit_sources:
        failures.append(
            f"{len(other_posts)} existing post(s) were staged but none links to "
            f"/articles/{slug}/. Editing an unrelated file does not satisfy the retrofit."
        )

    # --- 4: the retrofit link must read as a sentence, not a dump ---
    for rel, anchor, line in retrofit_sources:
        if anchor.strip().lower() in LAZY_ANCHORS:
            failures.append(f"{rel}: anchor text '{anchor}' is a lazy anchor")
        if anchor.strip().lower().replace(" ", "-") == slug:
            failures.append(f"{rel}: anchor text is the bare slug")
        stripped = line.lstrip()
        if stripped.startswith(("- ", "* ", "+ ")) or re.match(r"^\d+[.)]\s", stripped):
            failures.append(
                f"{rel}: the retrofit link sits in a list item, not a sentence. "
                "Charter 2e forbids related-posts dumps."
            )
        else:
            prose = len(re.sub(ARTICLE_LINK, "", line).strip())
            if prose < 40:
                failures.append(
                    f"{rel}: the retrofit link carries only {prose} characters of "
                    "surrounding prose. It must sit in a sentence that helps a reader "
                    "go deeper, not stand alone."
                )

    # --- 5 + 6: outbound links, resolved against the built sitemap ---
    outbound = [(a, u, t) for a, u, t in links_in(new_text) if t != slug]
    unique_targets = sorted({t for _, _, t in outbound})
    if len(unique_targets) < args.min_outbound:
        failures.append(
            f"{len(unique_targets)} outbound article link(s), minimum is {args.min_outbound}"
        )

    live = sitemap_slugs()
    if not live:
        failures.append(
            "output/sitemap.xml is missing or empty. Run build.py first: links must come "
            "from the built output, never from memory."
        )
    else:
        for target in unique_targets:
            if target not in live:
                failures.append(
                    f"outbound link /articles/{target}/ is not in the built sitemap. "
                    "This is exactly how the site accumulated hard-404 internal links."
                )

    for anchor, _url, _t in outbound:
        if anchor.strip().lower() in LAZY_ANCHORS:
            failures.append(f"outbound anchor text '{anchor}' is a lazy anchor")

    # --- 7: cluster isolation, reported for the subject test ---
    new_cluster = frontmatter_value(new_text, "category")
    if new_cluster:
        for target in unique_targets:
            path = post_path_for(target)
            if path is None:
                continue
            other_cluster = frontmatter_value(path.read_text(encoding="utf-8"), "category")
            if other_cluster and other_cluster != new_cluster:
                notes.append(
                    f"cross-cluster link to /articles/{target}/ "
                    f"({new_cluster} -> {other_cluster}). Permitted only when the "
                    "connection is the subject of the sentence."
                )
    else:
        notes.append(
            "the new article declares no `category`, so cluster isolation could not be "
            "checked. Charter 2c-bis requires exactly one declared cluster per piece."
        )

    print(f"link retrofit gate for /articles/{slug}/")
    print(f"  staged files          : {len(staged)}")
    print(f"  inbound retrofit from : "
          f"{', '.join(r for r, _, _ in retrofit_sources) or 'NONE'}")
    print(f"  outbound targets      : {len(unique_targets)} "
          f"({', '.join(unique_targets) or 'none'})")
    for note in notes:
        print(f"  NOTE  {note}")

    if failures:
        print()
        for failure in failures:
            print(f"  FAIL  {failure}")
        print(f"\nFAILED: {len(failures)} problem(s). Publication is blocked.")
        return 1

    print("\nPASSED: inbound retrofit and outbound links verified against the built sitemap.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
