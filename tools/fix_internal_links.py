#!/usr/bin/env python3
"""Repoint legacy /blog/<slug>/ internal links at their /articles/<slug>/ home.

The site moved its article path from /blog/ to /articles/. Body links written before
that move still say /blog/, which costs a redirect hop when the target is published
and hard-404s when it is not. `build.py` reports both as broken internal links.

This rewrites only links whose target resolves to a currently published post, and
reports the rest so a real decision gets made about them instead of a silent 301
into nothing.

    tools/fix_internal_links.py content/posts/*.md
    tools/fix_internal_links.py --check content/posts/*.md
"""
import argparse
import collections
import pathlib
import re
import sys

import frontmatter

LEGACY = re.compile(r'(?<=[\(\"\'])/blog/([a-z0-9][a-z0-9\-\.]*)/?(?=[\)\"\'#])')


def published_slugs(posts_dir: pathlib.Path) -> set[str]:
    slugs = set()
    for path in posts_dir.glob("*.md"):
        data = frontmatter.load(path)
        if data.get("status") == "published":
            slugs.add(data.get("slug") or path.stem)
    return slugs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    live = published_slugs(pathlib.Path("content/posts"))
    unresolved: collections.Counter[str] = collections.Counter()
    rewritten = 0
    touched = 0

    for path in args.paths:
        post = frontmatter.load(path)
        count = 0

        def repl(match: re.Match) -> str:
            nonlocal count
            slug = match.group(1)
            if slug not in live:
                unresolved[slug] += 1
                return match.group(0)
            count += 1
            return f"/articles/{slug}/"

        content = LEGACY.sub(repl, post.content)
        if count:
            rewritten += count
            touched += 1
            if not args.check:
                post.content = content
                path.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")
            print(f"{path}: {count} link(s)")

    verb = "would rewrite" if args.check else "rewrote"
    print(f"\n{verb} {rewritten} link(s) across {touched} file(s)")
    if unresolved:
        print(f"\n{sum(unresolved.values())} link(s) point at {len(unresolved)} "
              f"slug(s) that are not published — decide per target:")
        for slug, n in unresolved.most_common():
            print(f"  {n:>3}x  {slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
