#!/usr/bin/env python3
"""Audit cluster isolation and link connectivity across published posts.

CHARTER 2c-bis makes cluster isolation a hard structural rule, and says to audit the
map every cycle. A rule nobody can check is a rule that decays, so this is the check.

Reports four things:

1. Posts with no declared cluster. Tag inference is only a fallback and it put 85 of
   88 posts in the wrong cluster, so an undeclared post is a defect.
2. Cross-cluster links. Clusters do not link across boundaries, with one exception:
   when the link is the actual subject of the sentence. That exception cannot be
   decided mechanically, so every crossing is reported with its sentence for a human
   or a reviewing agent to judge. This tool never auto-fixes one.
3. Orphans. CHARTER 2e requires at least one inbound link from an existing page and
   at least two outbound. A page with no inbound link ranks for nothing.
4. Cluster sizes, so a cluster quietly collapsing to one page is visible.

    tools/audit_clusters.py            # full report
    tools/audit_clusters.py --strict   # exit 1 if any undeclared post or orphan
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

import frontmatter

POSTS = pathlib.Path("content/posts")
OUTPUT = pathlib.Path("output")
# Body links to another article. Captures the anchor text so a crossing can be judged.
LINK = re.compile(r"\[([^\]]+)\]\(/articles/([a-z0-9][a-z0-9\-\.]*)/?\)")
HREF = re.compile(r'href="/articles/([a-z0-9][a-z0-9\-\.]*)/"')
# Outbound links to non-article internal destinations: the tools and hand-written pages.
# A link to /llms-txt-validator/ sends a reader somewhere genuinely useful, so it counts
# toward CHARTER 2e's two-outbound minimum even though it is not an article.
INTERNAL = re.compile(r"\[([^\]]+)\]\((/[a-z0-9][a-z0-9/\-\.]*)/?\)")
NON_ARTICLE_TARGETS = ("/linter/", "/llms-txt-generator/", "/llms-txt-validator/",
                       "/ai-overviews-checker/", "/glossary/", "/work/", "/projects/",
                       "/portfolio/", "/about/")

# Listing pages link every post they list, so counting them would make every page look
# connected. CHARTER 2e is explicit that a related-posts dump is not a link, so inbound
# connectivity is measured from editorial pages only: article bodies, tool pages, and
# hand-written pages. These are the built paths that are listings.
def is_listing(path: pathlib.Path) -> bool:
    rel = path.relative_to(OUTPUT).as_posix()
    if rel in ("index.html", "articles/index.html"):
        return True
    if rel.startswith("articles/page/"):
        return True
    # A category archive is output/articles/<slug>/index.html where <slug> is a cluster.
    return False


def load() -> dict[str, dict]:
    posts = {}
    for path in sorted(POSTS.glob("*.md")):
        data = frontmatter.load(path)
        if data.get("status") != "published":
            continue
        slug = data.get("slug") or path.stem
        posts[slug] = {
            "path": path,
            "cluster": data.get("category"),
            "content": data.content,
            "title": data.get("title", slug),
        }
    return posts


def sentence_around(content: str, anchor: str) -> str:
    """The sentence containing a link, so the subject-of-the-sentence test is judgeable."""
    for line in content.splitlines():
        if anchor in line:
            return re.sub(r"\s+", " ", line).strip()[:200]
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    posts = load()
    if not posts:
        print("no published posts found — run from the repo root")
        return 1

    undeclared = [s for s, p in posts.items() if not p["cluster"]]
    inbound: dict[str, int] = collections.Counter()
    template_inbound: dict[str, int] = collections.Counter()
    outbound: dict[str, int] = collections.Counter()
    crossings = []

    for slug, post in posts.items():
        for _anchor, target in INTERNAL.findall(post["content"]):
            if target.rstrip("/") + "/" in NON_ARTICLE_TARGETS:
                outbound[slug] += 1
        for anchor, target in LINK.findall(post["content"]):
            if target == slug or target not in posts:
                continue
            outbound[slug] += 1
            inbound[target] += 1
            src, dst = post["cluster"], posts[target]["cluster"]
            if src and dst and src != dst:
                crossings.append((slug, src, target, dst, anchor,
                                  sentence_around(post["content"], anchor)))

    # Inbound links that do not come from an article body — tool pages, hand-written
    # pages, anything in the built site that is not a listing. Without these, a page
    # linked only from /llms-txt-validator/ reads as an orphan when it is not.
    clusters = {p["cluster"] for p in posts.values() if p["cluster"]}
    if OUTPUT.exists():
        for page in OUTPUT.rglob("*.html"):
            if is_listing(page):
                continue
            rel = page.relative_to(OUTPUT).as_posix()
            source_slug = rel[len("articles/"):-len("/index.html")] if rel.startswith("articles/") and rel.endswith("/index.html") else None
            if source_slug in posts or source_slug in clusters:
                continue  # article bodies and category archives already handled above
            try:
                html = page.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for target in set(HREF.findall(html)):
                if target in posts:
                    template_inbound[target] += 1

    for slug, n in template_inbound.items():
        inbound[slug] += n

    sizes = collections.Counter(p["cluster"] or "(undeclared)" for p in posts.values())
    print(f"{len(posts)} published posts across {len(sizes)} clusters\n")
    for cluster, n in sizes.most_common():
        print(f"  {n:>3}  {cluster}")

    print(f"\n--- undeclared cluster: {len(undeclared)} ---")
    for slug in undeclared:
        print(f"  {slug}")

    orphans = [s for s in posts if inbound[s] == 0]
    thin = [s for s in posts if outbound[s] < 2]
    print(f"\n--- no inbound link: {len(orphans)} ---")
    print("Counts article bodies plus non-listing built pages. Listings are excluded:")
    print("CHARTER 2e says a related-posts dump is not a link.")
    for slug in orphans:
        print(f"  [{posts[slug]['cluster']}] {slug}")
    print(f"\n--- fewer than 2 outbound links: {len(thin)} ---")
    print("Counts links to articles and to the tools and standing pages, since a link to")
    print("a tool sends a reader somewhere useful and satisfies 2e just as well.")
    for slug in thin:
        print(f"  [{posts[slug]['cluster']}] {slug}  ({outbound[slug]} out)")

    print(f"\n--- cross-cluster links: {len(crossings)} ---")
    print("Each needs the subject-of-the-sentence test applied by a reader. Not auto-fixable.")
    for src, sc, dst, dc, anchor, sentence in crossings:
        print(f"\n  {src}  [{sc}]\n    -> {dst}  [{dc}]\n    anchor: {anchor}\n    {sentence}")

    if args.strict and (undeclared or orphans):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
