#!/usr/bin/env python3
"""Detect template convergence in diagrams, across a cluster rather than within a page.

A diagram earns its place by showing a shape the prose cannot. If the shape is identical for
"context engineering", "semantic caching" and "model context protocol", the shape is telling
the reader nothing — it is a frame with words dropped into it, and both a reader and an
answer engine can tell. Pages that look identical read as programmatic output.

On 2026-08-17 all 25 glossary entries shared **one** skeleton: the same ordered class
sequence with exactly 5 nodes, 2 branches and 2 outcomes. Only the strings differed. And
every term had a diagram, when most terms should have none.

This is the same defect this campaign diagnosed in the Hermes writer — template convergence,
where a prompt specific enough to act as a template converges on identical output — and then
reproduced by hand. The failure survived being diagnosed, which is the argument for making
the check mechanical instead of a judgement call. The slop reviewer's brief already said to
compare structure across the last five pieces; it did not catch this.

    tools/audit_structure.py             # report
    tools/audit_structure.py --strict    # exit 1 when a group shares a skeleton
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

OUTPUT = pathlib.Path("output")
MAIN = re.compile(r"<main.*?</main>", re.S)
FLOWCHART_CLASS = re.compile(r'class="(flowchart[a-z-]*)[^"]*"')

# A group is a set of pages a reader would compare. Identical shapes inside one are the
# defect; two clusters happening to share a shape is not.
GROUPS = {"glossary": re.compile(r"^glossary/[^/]+/index\.html$")}


def skeleton(html: str):
    """The shape, not the words: ordered class sequence plus node/branch/outcome counts."""
    main = MAIN.search(html)
    if not main:
        return None
    sequence = [c for c in FLOWCHART_CLASS.findall(main.group(0))]
    if not sequence:
        return None
    shape = ">".join(c.replace("flowchart-", "") or "ROOT" for c in sequence)
    return (shape,
            sequence.count("flowchart-node"),
            sequence.count("flowchart-branch"),
            sequence.count("flowchart-outcome"))


def group_of(rel: str, clusters: dict[str, str]) -> str | None:
    for name, pattern in GROUPS.items():
        if pattern.match(rel):
            return name
    if rel.startswith("articles/") and rel.endswith("/index.html"):
        slug = rel[len("articles/"):-len("/index.html")]
        return clusters.get(slug)
    return None


def post_clusters() -> dict[str, str]:
    import frontmatter
    clusters = {}
    for path in pathlib.Path("content/posts").glob("*.md"):
        data = frontmatter.load(path)
        if data.get("status") == "published":
            clusters[data.get("slug") or path.stem] = data.get("category") or "(none)"
    return clusters


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if not (OUTPUT / "sitemap.xml").is_file():
        print("output/ is missing or unbuilt — run `python build.py` first. Refusing to report.")
        return 2

    clusters = post_clusters()
    by_group: dict[str, dict] = collections.defaultdict(
        lambda: {"skeletons": collections.defaultdict(list), "total": 0})

    for page in sorted(OUTPUT.rglob("index.html")):
        rel = page.relative_to(OUTPUT).as_posix()
        group = group_of(rel, clusters)
        if group is None:
            continue
        by_group[group]["total"] += 1
        shape = skeleton(page.read_text(encoding="utf-8", errors="replace"))
        if shape:
            slug = rel.split("/")[-2]
            by_group[group]["skeletons"][shape].append(slug)

    problems = 0
    for group, data in sorted(by_group.items()):
        drawn = sum(len(v) for v in data["skeletons"].values())
        if not drawn:
            continue
        share = drawn / data["total"] if data["total"] else 0
        print(f"\n## {group}: {drawn} of {data['total']} pages carry a diagram "
              f"({share:.0%}), {len(data['skeletons'])} distinct shape(s)")

        for (shape, nodes, branches, outcomes), slugs in sorted(
                data["skeletons"].items(), key=lambda kv: -len(kv[1])):
            marker = "CONVERGED" if len(slugs) > 1 else "distinct"
            print(f"  [{marker}] {len(slugs)} page(s) — nodes={nodes} branches={branches} "
                  f"outcomes={outcomes}")
            print(f"      {shape[:104]}")
            print(f"      {', '.join(slugs[:6])}{' ...' if len(slugs) > 6 else ''}")
            if len(slugs) > 1:
                problems += 1

        # "Most terms should have no diagram at all." A cluster where nearly every page has
        # one is applying a house style rather than drawing when the relationship needs it.
        if share > 0.5:
            print(f"  [SATURATED] {share:.0%} of this group carries a diagram. A diagram is")
            print("      warranted when prose handles a relationship badly, which is a minority")
            print("      of pages. This reads as a house style applied everywhere.")
            problems += 1

    # Always print the count line, including on a clean run. Printing prose instead made
    # the daily corpus-health line report "?" for a healthy state, which reads as unknown
    # when it means none — the same failure as a gate that cannot go green.
    print(f"\n{problems} structural problem(s).", end=" ")
    if problems:
        print("A shape that does not come from the subject tells the reader nothing.")
    else:
        print("No group shares a diagram skeleton, and none is saturated.")
    return 1 if (args.strict and problems) else 0


if __name__ == "__main__":
    sys.exit(main())
