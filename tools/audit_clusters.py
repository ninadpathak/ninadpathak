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
# Body links to another article. Captures the anchor text so a crossing can be judged.
LINK = re.compile(r"\[([^\]]+)\]\(/articles/([a-z0-9][a-z0-9\-\.]*)/?\)")


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
    outbound: dict[str, int] = collections.Counter()
    crossings = []

    for slug, post in posts.items():
        for anchor, target in LINK.findall(post["content"]):
            if target == slug or target not in posts:
                continue
            outbound[slug] += 1
            inbound[target] += 1
            src, dst = post["cluster"], posts[target]["cluster"]
            if src and dst and src != dst:
                crossings.append((slug, src, target, dst, anchor,
                                  sentence_around(post["content"], anchor)))

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
    for slug in orphans:
        print(f"  [{posts[slug]['cluster']}] {slug}")
    print(f"\n--- fewer than 2 outbound links: {len(thin)} ---")
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
