#!/usr/bin/env python3
"""Resolve and validate the prepared brief for one live queue row.

The Hermes CSV is the calendar, while ``planning/content-briefs`` carries the evidence,
scope, and linking decisions that make a row safe to write.  A publisher that reads only
the CSV can silently discard those decisions.  This checker joins the two sources without
copying or changing queue state::

    python tools/check_content_brief.py \
        --queue /root/.hermes/knowledge/ninadpathak/content-queue.csv \
        --order 20

It prints the single matching brief path on success and exits 2 when the brief is missing,
duplicated, or disagrees with a fixed queue field.  Subcluster is compared when the brief
declares it; older briefs may omit it, but may never contradict it.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_BRIEFS = ROOT / "planning" / "content-briefs"

TITLE_RE = re.compile(r"(?m)^# Brief:\s*(?P<value>.+?)\s*$")
SLOT_RE = re.compile(r"\*\*Slot:\*\*\s*(?P<value>\d{4}-\d{2}-\d{2})")
ORDER_RE = re.compile(r"\|\s*(?:Queue order|Order):?\s*(?:\*\*)?(?P<value>\d+)\b",
                      re.IGNORECASE)
EXPERIENCE_RE = re.compile(r"\*\*Experience:\s*(?P<value>[ABC])(?:\*\*)?\b",
                           re.IGNORECASE)


def clean(value: str) -> str:
    """Normalize display whitespace without weakening exact field comparison."""
    return re.sub(r"\s+", " ", value).strip().rstrip("*").strip()


def labelled_value(metadata: str, label: str) -> str | None:
    """Read a bold metadata field, including values wrapped onto the next line."""
    flattened = clean(metadata)
    match = re.search(
        rf"\*\*{re.escape(label)}:\*\*\s*(?P<value>.+?)"
        rf"(?=\s*\|\s*\*\*|\s+\*\*(?:Experience|Slot|Order|Type):|$)",
        flattened,
        re.IGNORECASE,
    )
    return clean(match.group("value")) if match else None


def parse_brief(path: pathlib.Path) -> dict[str, str | None]:
    text = path.read_text(encoding="utf-8")
    metadata = text.split("\n## ", 1)[0]

    def required(pattern: re.Pattern[str], name: str) -> str:
        match = pattern.search(metadata)
        if not match:
            raise ValueError(f"missing {name}")
        return clean(match.group("value"))

    return {
        "path": str(path),
        "title": required(TITLE_RE, "title"),
        "date": required(SLOT_RE, "slot date"),
        "order": required(ORDER_RE, "order"),
        "cluster": labelled_value(metadata, "Cluster"),
        "subcluster": labelled_value(metadata, "Subcluster"),
        "experience": required(EXPERIENCE_RE, "Experience").upper(),
    }


def load_row(queue: pathlib.Path, order: str) -> dict[str, str]:
    with queue.open(newline="", encoding="utf-8") as handle:
        matches = [row for row in csv.DictReader(handle) if row.get("Order") == order]
    if len(matches) != 1:
        raise ValueError(f"queue order {order} matched {len(matches)} rows")
    return matches[0]


def resolve_brief(brief_root: pathlib.Path, order: str) -> dict[str, str | None]:
    matches = []
    malformed = []
    for path in sorted(brief_root.glob("brief-*.md")):
        try:
            brief = parse_brief(path)
        except ValueError as exc:
            malformed.append(f"{path}: {exc}")
            continue
        if brief["order"] == order:
            matches.append(brief)
    if len(matches) != 1:
        detail = f"; malformed: {', '.join(malformed)}" if malformed else ""
        raise ValueError(f"brief order {order} matched {len(matches)} files{detail}")
    return matches[0]


def mismatches(row: dict[str, str], brief: dict[str, str | None]) -> list[str]:
    pairs = (
        ("title", row.get("Title", ""), brief["title"]),
        ("date", row.get("Release Date", ""), brief["date"]),
        ("cluster", row.get("Cluster", ""), brief["cluster"]),
        ("Experience", row.get("Experience", "").upper(), brief["experience"]),
    )
    problems = [f"{name}: queue={expected!r}, brief={actual!r}"
                for name, expected, actual in pairs if clean(expected) != clean(actual or "")]
    if brief["subcluster"] is not None:
        expected = clean(row.get("Subcluster", ""))
        actual = clean(brief["subcluster"] or "")
        if expected != actual:
            problems.append(f"subcluster: queue={expected!r}, brief={actual!r}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", required=True, type=pathlib.Path)
    parser.add_argument("--order", required=True)
    parser.add_argument("--brief-root", type=pathlib.Path, default=DEFAULT_BRIEFS)
    args = parser.parse_args()

    try:
        row = load_row(args.queue, str(args.order))
        brief = resolve_brief(args.brief_root, str(args.order))
    except (OSError, ValueError) as exc:
        print(f"REFUSING: {exc}")
        return 2

    problems = mismatches(row, brief)
    if problems:
        print(f"REFUSING: queue/brief mismatch for order {args.order}")
        for problem in problems:
            print(f"- {problem}")
        return 2

    print(f"BRIEF OK: order {args.order}: {brief['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
