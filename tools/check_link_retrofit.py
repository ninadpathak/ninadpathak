#!/usr/bin/env python3
"""Require each new article to receive a contextual inbound link from another post."""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS_ROOT = ROOT / "content" / "posts"


def check_inbound_link(slug: str, posts_root: pathlib.Path) -> list[str]:
    """Return gate failures unless another Markdown post links to the article slug."""
    target = posts_root / f"{slug}.md"
    if not target.is_file():
        return [f"target post is missing: {target}"]
    link = re.compile(r"\]\(/articles/" + re.escape(slug) + r"/?(?:[)#?])")
    for post in posts_root.glob("*.md"):
        if post == target:
            continue
        if link.search(post.read_text(encoding="utf-8")):
            return []
    return [f"no inbound link to /articles/{slug}/ from another post"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--posts-root", type=pathlib.Path, default=POSTS_ROOT)
    args = parser.parse_args()
    failures = check_inbound_link(args.slug, args.posts_root)
    if failures:
        print("LINK RETROFIT BLOCKED: " + "; ".join(failures))
        return 2
    print(f"LINK RETROFIT OK: inbound link to /articles/{args.slug}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
