#!/usr/bin/env python3
"""Check a runbook written from runbook-template.md before it goes on call.

Usage:
  python3 check_runbook.py runbook.md                       # structure only
  python3 check_runbook.py --filled runbook.md              # also fail on unfilled {{placeholders}}
  python3 check_runbook.py --filled --max-age 90 runbook.md # also fail if Last tested is older

Exit status is 0 when the runbook passes and 1 when it fails, so the check can run in CI.
"""
from datetime import date
from pathlib import Path
import re
import sys

HEADER_FIELDS = ("Service", "Alert", "Owner", "Last tested", "Impact")
STEP_SECTIONS = ("Diagnose", "Mitigate", "Verify")
STEP_FIELDS = ("Expect", "If not")
ESCALATE_FIELDS = ("Escalate to", "Escalate after", "Include")
PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
ISO_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
FENCE = re.compile(r"^```[^\n]*\n(.*?)^```", flags=re.M | re.S)


def sections(text):
    """Split the runbook into {"header": str, "<h2 title>": str}."""
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    found = {"header": parts[0]}
    for title, body in zip(parts[1::2], parts[2::2]):
        found[title.strip()] = body
    return found


def steps(body):
    """Split a section into its ### steps."""
    parts = re.split(r"^### (.+)$", body, flags=re.M)
    return [(title.strip(), step) for title, step in zip(parts[1::2], parts[2::2])]


def field(body, name):
    """Return a Field: value from outside code blocks, or None if the line is missing."""
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.*)$", FENCE.sub("", body), flags=re.M)
    return match.group(1).strip() if match else None


def parse_date(value):
    match = ISO_DATE.match(value or "")
    if not match:
        return None
    try:
        return date(*map(int, match.groups()))
    except ValueError:
        return None


def check(text, filled, max_age=None, today=None):
    errors = []
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    found = sections(text)

    for name in HEADER_FIELDS:
        value = field(found["header"], name)
        if value is None:
            errors.append(f"header is missing '{name}:'")
        elif not value:
            errors.append(f"header '{name}:' is empty")
    tested = field(found["header"], "Last tested")
    if tested and not PLACEHOLDER.search(tested):
        when = parse_date(tested)
        if when is None:
            errors.append(f"'Last tested:' is not a calendar date (YYYY-MM-DD): {tested!r}")
        elif max_age is not None and ((today or date.today()) - when).days > max_age:
            errors.append(f"'Last tested:' {tested} is more than {max_age} days old")

    before = found.get("Before you start")
    if before is None:
        errors.append("missing '## Before you start'")
    elif not field(before, "Stop and escalate if"):
        errors.append("'Before you start' is missing 'Stop and escalate if:'")

    checked = 0
    for section in STEP_SECTIONS:
        if section not in found:
            errors.append(f"missing '## {section}'")
            continue
        section_steps = steps(found[section])
        if not section_steps:
            errors.append(f"'{section}' has no ### step")
        for title, body in section_steps:
            checked += 1
            if not any(block.strip() for block in FENCE.findall(body)):
                errors.append(f"step '{title}' has no command in a code block")
            names = STEP_FIELDS + (("Undo",) if section == "Mitigate" else ())
            for name in names:
                if not field(body, name):
                    errors.append(f"step '{title}' is missing '{name}:'")

    escalate = found.get("Escalate")
    if escalate is None:
        errors.append("missing '## Escalate'")
    else:
        for name in ESCALATE_FIELDS:
            if not field(escalate, name):
                errors.append(f"'Escalate' is missing '{name}:'")
        after = field(escalate, "Escalate after") or ""
        if after and not PLACEHOLDER.search(after) and not re.search(r"\d+\s*min", after):
            errors.append(f"'Escalate after:' needs a time limit in minutes: {after!r}")

    placeholders = PLACEHOLDER.findall(text)
    if filled and placeholders:
        errors.append(f"{len(placeholders)} unfilled placeholder(s), first: {placeholders[0]}")
    return errors, checked, len(placeholders)


def main(argv):
    filled = "--filled" in argv
    max_age = None
    if "--max-age" in argv:
        max_age = int(argv[argv.index("--max-age") + 1])
        argv = argv[:argv.index("--max-age")] + argv[argv.index("--max-age") + 2:]
    paths = [a for a in argv if not a.startswith("--")]
    path = Path(paths[0]) if paths else Path(__file__).with_name("runbook-template.md")
    errors, checked, placeholders = check(path.read_text(encoding="utf-8"), filled, max_age)
    if errors:
        print(f"{path.name}: FAIL ({len(errors)} problem(s))")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"{path.name}: PASS")
    print(f"  steps checked: {checked}")
    print(f"  unfilled placeholders: {placeholders}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
