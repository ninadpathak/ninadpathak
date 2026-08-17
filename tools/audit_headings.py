#!/usr/bin/env python3
"""Audit heading structure against the nested-heading rule.

CHARTER 2c-quater: a flat run of `h2`s gives an answer engine no way to tell where one
idea ends and the next begins, so extraction boundaries land arbitrarily. Each `h2` is one
complete chain of thought, the `h3`s under it are the steps within that chain, and the next
`h2` starts the next chain. Never skip a level. Never head a single short paragraph. Never
leave an `h2` with exactly one `h3`, because one sub-step is not a sub-step.

The rule became binding on 2026-08-17 with nothing able to check it. First run over 90
published posts: 64 of them were entirely flat, including the highest-impression page on
the site and both cluster-4 articles written that same day under the previous skill
version. A rule nobody can check decays, and this one was 71% unmet on arrival.

Deliberately NOT a CI gate yet. Failing 64 of 90 posts on arrival is the mistake this
campaign has already made twice — a gate that cannot go green stops being read. Gate on
regressions once the corpus is closer, the same way the claim and rule_checker gates work.

    tools/audit_headings.py                 # full report
    tools/audit_headings.py --count         # one line per offending post
    tools/audit_headings.py --paths a.md b.md   # restrict, for a regression check
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import frontmatter

POSTS = pathlib.Path("content/posts")
HEADING = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
FENCE = ("```", "~~~")

# A heading over this little prose is heading a paragraph, not a section.
THIN_SECTION_WORDS = 40


def headings_and_bodies(content: str):
    """Every markdown heading outside a code fence, with the prose that follows it.

    Fenced blocks are skipped because a `## ` inside a shell example or a YAML sample is
    not a document heading, and counting it would report structure that does not exist.
    """
    items = []
    in_fence = False
    current = None
    for number, line in enumerate(content.splitlines(), start=1):
        if line.lstrip().startswith(FENCE):
            in_fence = not in_fence
            if current:
                current["body"].append(line)
            continue
        if in_fence:
            if current:
                current["body"].append(line)
            continue
        match = HEADING.match(line)
        if match:
            current = {"line": number, "level": len(match.group(1)),
                       "text": match.group(2), "body": []}
            items.append(current)
        elif current:
            current["body"].append(line)
    return items


def audit(path: pathlib.Path):
    data = frontmatter.load(path)
    if data.get("status") != "published":
        return None

    items = headings_and_bodies(data.content)
    levels = [h["level"] for h in items]
    problems = []

    if levels and all(level == 2 for level in levels) and len(levels) >= 3:
        problems.append(("flat", f"all {len(levels)} headings are h2 — no chain has steps"))

    # An h2 owning exactly one h3.
    index = 0
    while index < len(levels):
        if levels[index] == 2:
            cursor = index + 1
            children = 0
            while cursor < len(levels) and levels[cursor] > 2:
                if levels[cursor] == 3:
                    children += 1
                cursor += 1
            if children == 1:
                problems.append(("solo-h3", f'h2 "{items[index]["text"][:52]}" has exactly one h3'))
            index = cursor
        else:
            index += 1

    for previous, nxt in zip(items, items[1:]):
        if nxt["level"] > previous["level"] + 1:
            problems.append(("skipped-level",
                             f'h{previous["level"]} to h{nxt["level"]} at "{nxt["text"][:40]}"'))

    for heading in items:
        words = len(" ".join(heading["body"]).split())
        if words and words < THIN_SECTION_WORDS:
            problems.append(("thin-section",
                             f'"{heading["text"][:44]}" heads only {words} words'))

    return {"slug": data.get("slug") or path.stem,
            "cluster": data.get("category") or "(none)",
            "headings": len(items), "problems": problems}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", action="store_true")
    parser.add_argument("--paths", nargs="*", default=None)
    args = parser.parse_args()

    if args.paths is not None:
        candidates = [pathlib.Path(p) for p in args.paths if p.endswith(".md")]
    else:
        candidates = sorted(POSTS.glob("*.md"))

    reports = [r for r in (audit(p) for p in candidates if p.exists()) if r]
    offending = [r for r in reports if r["problems"]]
    total = sum(len(r["problems"]) for r in offending)

    kinds: dict[str, int] = {}
    for report in offending:
        for kind, _ in report["problems"]:
            kinds[kind] = kinds.get(kind, 0) + 1

    if args.count:
        print(f"{'issues':>7}  {'headings':>8}  {'cluster':<26} slug")
        for report in sorted(offending, key=lambda r: -len(r["problems"])):
            print(f"{len(report['problems']):>7}  {report['headings']:>8}  "
                  f"{report['cluster']:<26} {report['slug']}")
    else:
        for report in sorted(offending, key=lambda r: -len(r["problems"])):
            print(f"\n## [{report['cluster']}] {report['slug']}  "
                  f"({report['headings']} headings, {len(report['problems'])} issue(s))")
            for kind, detail in report["problems"]:
                print(f"  {kind:<14} {detail}")

    print(f"\n{total} issue(s) across {len(offending)} of {len(reports)} published posts")
    for kind, count in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"  {count:>4}  {kind}")
    print("\nNot a CI gate: too much of the corpus predates the rule. Gate on regressions")
    print("once the backlog is closer, the way the claim and rule_checker gates do.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
