#!/usr/bin/env python3
"""Check a design doc written from design-doc-template.md before review.

Usage:
  python3 check_design_doc.py design-doc.md            # structure only
  python3 check_design_doc.py --filled design-doc.md   # also fail on unfilled {{placeholders}}

Reads the file and nothing else. Exit status is 0 when the doc passes and 1 when it
fails, so the check can run in CI on a docs/design/ folder.
"""
from datetime import date
from pathlib import Path
import re
import sys

HEADER_FIELDS = ("Status", "Author", "Reviewers", "Date")
SECTIONS = ("Problem", "Goals", "Non-goals", "Proposal", "Alternatives considered",
            "Risks and rollout", "Open questions", "Decision")
STATUSES = ("Draft", "In review", "Accepted", "Rejected", "Superseded by")
PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
COMMENT = re.compile(r"<!--.*?-->", re.S)
ISO_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def field(text, name):
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.*)$", text, flags=re.M)
    return match.group(1).strip() if match else None


def split(text, level):
    marker = "#" * level
    parts = re.split(rf"^{marker} (.+)$", text, flags=re.M)
    return parts[0], [(title.strip(), body) for title, body in zip(parts[1::2], parts[2::2])]


def is_date(value):
    match = ISO_DATE.match(value)
    if not match:
        return False
    try:
        date(*map(int, match.groups()))
    except ValueError:
        return False
    return True


def check(text, filled):
    errors = []
    text = COMMENT.sub("", text)
    header, sections = split(text, 2)
    found = dict(sections)

    for name in HEADER_FIELDS:
        value = field(header, name)
        if value is None:
            errors.append(f"header is missing '{name}:'")
        elif not value:
            errors.append(f"header '{name}:' is empty")
    status = field(header, "Status") or ""
    if status and not PLACEHOLDER.fullmatch(status) and not status.startswith(STATUSES):
        errors.append(f"Status must start with one of {', '.join(STATUSES)}: {status!r}")
    when = field(header, "Date") or ""
    if when and not PLACEHOLDER.fullmatch(when) and not is_date(when):
        errors.append(f"Date is not a calendar date (YYYY-MM-DD): {when!r}")

    for name in SECTIONS:
        if name not in found:
            errors.append(f"missing section '## {name}'")
        elif not found[name].strip():
            errors.append(f"section '## {name}' is empty (write None if it has nothing to say)")

    _, alternatives = split(found.get("Alternatives considered", ""), 3)
    if not any(title.lower().startswith("do nothing") for title, _ in alternatives):
        errors.append("'Alternatives considered' has no '### Do nothing' entry")
    for title, body in alternatives:
        if not field(body, "Rejected because"):
            errors.append(f"alternative '{title}' has no 'Rejected because:' reason")

    if status.startswith(("Accepted", "Rejected")):
        questions = found.get("Open questions", "").strip().lstrip("- ").strip()
        if questions and questions != "None":
            errors.append(f"Status is {status} but 'Open questions' is not None")
        if PLACEHOLDER.search(found.get("Decision", "")):
            errors.append(f"Status is {status} but 'Decision' is not filled in")

    placeholders = PLACEHOLDER.findall(text)
    if filled and placeholders:
        errors.append(f"{len(placeholders)} unfilled placeholder(s), first: {placeholders[0]}")
    return errors, len(alternatives), len(placeholders)


def main(argv):
    filled = "--filled" in argv
    paths = [a for a in argv if not a.startswith("--")]
    path = Path(paths[0]) if paths else Path(__file__).with_name("design-doc-template.md")
    errors, alternatives, placeholders = check(path.read_text(encoding="utf-8"), filled)
    if errors:
        print(f"{path.name}: FAIL ({len(errors)} problem(s))")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"{path.name}: PASS")
    print(f"  sections: {len(SECTIONS)}/{len(SECTIONS)}")
    print(f"  alternatives with a reason: {alternatives}")
    print(f"  unfilled placeholders: {placeholders}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
