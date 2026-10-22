#!/usr/bin/env python3
"""Check a release note written from release-notes-template.md before it ships.

Usage:
  python3 check_release_notes.py release-notes.md            # structure only
  python3 check_release_notes.py --filled release-notes.md   # also fail on unfilled [placeholders]

Exit status is 0 when the note passes and 1 when it fails, so the check can run in CI.
"""
from datetime import date
from pathlib import Path
import re
import sys

SUMMARY_FIELDS = ("Version", "Date", "Compatibility", "Affected", "Action", "Rollback")
BREAKING_FIELDS = ("What changed", "Migration", "Verify", "Deadline")
ISSUE_FIELDS = ("Workaround", "Tracking", "Fixed in")
PLACEHOLDER = re.compile(r"\[[^\]]+\](?!\()")
ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")


def sections(text):
    """Split the note into {"summary": str, "<h2 title>": str}."""
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    found = {"summary": parts[0]}
    for title, body in zip(parts[1::2], parts[2::2]):
        found[title.strip()] = body
    return found


def entries(body):
    """Split a section into its ### entries."""
    parts = re.split(r"^### (.+)$", body, flags=re.M)
    return list(zip(parts[1::2], parts[2::2]))


def field(body, name):
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.*)$", body, flags=re.M)
    return match.group(1).strip() if match else None


def valid_date(value):
    match = ISO_DATE.search(value or "")
    if not match:
        return False
    try:
        date(*map(int, match.groups()))
    except ValueError:
        return False
    return True


def check(text, filled):
    errors = []
    found = sections(text)
    summary = found["summary"]
    for name in SUMMARY_FIELDS:
        if field(summary, name) is None:
            errors.append(f"summary is missing '{name}:'")
    when = field(summary, "Date")
    if when is not None and not PLACEHOLDER.fullmatch(when) and not valid_date(when):
        errors.append(f"summary Date is not a calendar date (YYYY-MM-DD): {when!r}")

    compatibility = (field(summary, "Compatibility") or "").lower()
    breaking = entries(found.get("Breaking changes", ""))
    if compatibility.startswith("breaking") and not breaking:
        errors.append("Compatibility says breaking, but 'Breaking changes' has no ### entry")
    for title, body in breaking:
        for name in BREAKING_FIELDS:
            value = field(body, name)
            if not value:
                errors.append(f"breaking change '{title.strip()}' is missing '{name}:'")
        deadline = field(body, "Deadline")
        if deadline and deadline != "None" and not PLACEHOLDER.search(deadline) and not valid_date(deadline):
            errors.append(f"breaking change '{title.strip()}' has a Deadline without a calendar date: {deadline!r}")

    for title, body in entries(found.get("Known issues", "")):
        for name in ISSUE_FIELDS:
            if not field(body, name):
                errors.append(f"known issue '{title.strip()}' is missing '{name}:'")

    placeholders = [m.group(0) for m in PLACEHOLDER.finditer(re.sub(r"<!--.*?-->", "", text, flags=re.S))]
    if filled and placeholders:
        errors.append(f"{len(placeholders)} unfilled placeholder(s), first: {placeholders[0]}")
    return errors, len(breaking), len(placeholders)


def main(argv):
    filled = "--filled" in argv
    paths = [a for a in argv if not a.startswith("--")]
    path = Path(paths[0]) if paths else Path(__file__).with_name("release-notes-template.md")
    errors, breaking, placeholders = check(path.read_text(encoding="utf-8"), filled)
    if errors:
        print(f"{path.name}: FAIL ({len(errors)} problem(s))")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"{path.name}: PASS")
    print(f"  summary fields: {len(SUMMARY_FIELDS)}/{len(SUMMARY_FIELDS)}")
    print(f"  breaking changes checked: {breaking}")
    print(f"  unfilled placeholders: {placeholders}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
