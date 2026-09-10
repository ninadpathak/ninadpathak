#!/usr/bin/env python3
"""Validate public-corpus inventory and catch mechanically repeated openings.

This structural guard cannot approve point of view, evidence, or editorial quality.
Those remain separate human review decisions recorded in the audit register.
"""

from __future__ import annotations

import argparse
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "planning/research/opinionated-site-2026-09-11/page-pov-audit.md"
POSTS = ROOT / "content/posts"
REVIEW_STATES = {
    "PHASE_A_EDITED",
    "EVIDENCE_REQUIRED",
    "REWRITE_BATCH",
    "PROVISIONAL_REVIEW",
}
GENERIC_OPENERS = re.compile(
    r"\b(in today'?s|rapidly evolving|digital landscape|delve into|at its core|"
    r"in this (?:article|guide|post)|by the end of this)\b",
    re.I,
)


def frontmatter_and_body(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not match:
        return {}, text
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "-")):
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip("'\"")
    return metadata, match.group(2)


def opening(body: str) -> str:
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    for block in re.split(r"\n\s*\n", body):
        candidate = re.sub(r"<[^>]+>", " ", block).strip()
        if candidate and not candidate.startswith(("#", "|", "-", ">")):
            return re.sub(r"\s+", " ", candidate)
    return ""


def audit_rows() -> dict[str, str]:
    text = AUDIT.read_text(encoding="utf-8")
    section = text.split("## Published articles", 1)[1].split("## Non-rendered", 1)[0]
    rows: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"\| Article \| `([^`]+)` \| ([A-Z_]+) \|", line)
        if not match:
            continue
        name, state = match.groups()
        if name in rows:
            raise ValueError(f"duplicate article audit row: {name}")
        rows[name] = state
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail on inventory, disposition, generic-opening, or repeated-opening findings",
    )
    args = parser.parse_args()
    problems: list[str] = []
    rows = audit_rows()
    published: dict[str, Path] = {}

    for path in sorted(POSTS.glob("*.md")):
        metadata, _ = frontmatter_and_body(path)
        if metadata.get("status") == "published":
            published[path.name] = path

    missing = sorted(set(published) - set(rows))
    stale = sorted(set(rows) - set(published))
    if missing:
        problems.append("published articles missing from audit: " + ", ".join(missing))
    if stale:
        problems.append("audit rows that are not published articles: " + ", ".join(stale))

    openings: list[tuple[str, str]] = []
    for name, path in published.items():
        state = rows.get(name)
        if state not in REVIEW_STATES:
            problems.append(f"{name}: unknown or absent disposition {state!r}")
            continue
        _, body = frontmatter_and_body(path)
        intro = opening(body)
        if not intro:
            problems.append(f"{name}: no prose opening before the outline")
        if GENERIC_OPENERS.search(intro):
            problems.append(f"{name}: interchangeable opening phrase")
        openings.append((name, intro.lower()))

    for index, (left_name, left) in enumerate(openings):
        for right_name, right in openings[index + 1 :]:
            ratio = SequenceMatcher(None, left[:260], right[:260]).ratio()
            if ratio >= 0.82:
                problems.append(
                    f"{left_name} and {right_name}: openings are {ratio:.0%} interchangeable"
                )

    print(f"Content inventory: {len(published)} published articles, {len(rows)} audit rows")
    print(
        "Human editorial review remains separate; this command does not approve "
        "thesis, evidence, or point of view"
    )
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1 if args.strict else 0
    print("PASS: inventory is complete and no mechanically interchangeable opening was found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
