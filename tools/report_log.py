"""Idempotent dated Markdown report logs.

Campaign instruments are routinely invoked by the scheduler, manual verification, and
retry on the same day. Those runs revise one lagged observation; appending each one makes
them look like independent samples. ``upsert_dated_report`` keeps the newest section for
every historical date, replaces today's section with the supplied report, and preserves
the file preamble plus nested headings.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


DATED_SECTION = re.compile(
    r"(?m)^## (?P<date>\d{4}-\d{2}-\d{2})[^\r\n]*\r?$"
)


def collapse_dated_reports(existing: str) -> str:
    """Collapse every repeated date to its last appended section without adding one."""
    matches = list(DATED_SECTION.finditer(existing))
    if not matches:
        return existing.rstrip() + "\n"

    preamble = existing[:matches[0].start()].rstrip()
    order: list[str] = []
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        date = match.group("date")
        if date not in sections:
            order.append(date)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(existing)
        sections[date] = existing[match.start():end].strip() + "\n"

    body = "\n\n".join(sections[date].strip() for date in order)
    return f"{preamble}\n\n{body}\n" if preamble else f"{body}\n"


def upsert_dated_report(existing: str, report: str, generated: str) -> str:
    """Return one authoritative top-level dated section per calendar date.

    Existing duplicates are collapsed to their last (latest appended) section, including
    duplicates from earlier dates. The supplied report is authoritative for ``generated``.
    Date order follows first appearance so cleaning a file does not rewrite its history.
    """
    existing = collapse_dated_reports(existing)
    matches = list(DATED_SECTION.finditer(existing))
    clean_report = report.strip() + "\n"
    if not matches:
        return existing.rstrip() + "\n\n" + clean_report

    targets = [
        (match.start(), matches[index + 1].start()
         if index + 1 < len(matches) else len(existing))
        for index, match in enumerate(matches)
        if match.group("date") == generated
    ]
    if not targets:
        return existing.rstrip() + "\n\n" + clean_report

    start, end = targets[0]
    return (existing[:start] + clean_report + existing[end:]).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collapse duplicate top-level dated sections to the last observation."
    )
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    parser.add_argument("--check", action="store_true", help="report only; write nothing")
    args = parser.parse_args()

    changed = []
    for path in args.paths:
        existing = path.read_text(encoding="utf-8")
        cleaned = collapse_dated_reports(existing)
        if cleaned == existing:
            continue
        changed.append(path)
        if not args.check:
            path.write_text(cleaned, encoding="utf-8")
    for path in changed:
        print(f"{'DUPLICATE' if args.check else 'REPAIRED'}: {path}")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
