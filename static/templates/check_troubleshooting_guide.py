#!/usr/bin/env python3
"""Check a troubleshooting guide written from troubleshooting-guide-template.md before it ships.

Usage:
  python3 check_troubleshooting_guide.py guide.md                        # structure only
  python3 check_troubleshooting_guide.py --filled guide.md               # also fail on unfilled {{placeholders}}
  python3 check_troubleshooting_guide.py --filled --max-age 180 guide.md # also fail if Last reproduced is older

Exit status is 0 when the guide passes and 1 when it fails, so the check can run in CI.
"""
from datetime import date
from pathlib import Path
import re
import sys

HEADER_FIELDS = ("Applies to", "Last reproduced")
LAST_SECTION = "Still stuck?"
LAST_SECTION_FIELDS = ("Collect", "Contact")
CAUSE_BLOCKS = ("Check", "Fix", "Verify")
CAUSE_FIELDS = ("Why", "Your cause if", "Fixed when")
PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
ISO_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
CODE_SPAN = re.compile(r"`([^`]+)`")


def split(lines, marker):
    """Split lines at headings that start with marker, ignoring lines inside code blocks.

    Returns (lines before the first heading, [(heading text, lines under it), ...]).
    """
    before, parts, fenced = [], [], False
    for line in lines:
        if line.startswith("```"):
            fenced = not fenced
        if not fenced and line.startswith(marker):
            parts.append((line[len(marker):].strip(), []))
        elif parts:
            parts[-1][1].append(line)
        else:
            before.append(line)
    return before, parts


def field(lines, name):
    """Return the value of a 'Name: value' line outside code blocks, or None if the line is missing."""
    fenced = False
    for line in lines:
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith(name + ":"):
            return line[len(name) + 1:].strip()
    return None


def block(lines, name):
    """Return the code block that directly follows a 'Name:' line, or None if there is none."""
    fenced = False
    for index, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and line.strip() == name + ":":
            rest = list(lines[index + 1:])
            while rest and not rest[0].strip():
                rest.pop(0)
            if not rest or not rest[0].startswith("```"):
                return None
            body = []
            for later in rest[1:]:
                if later.startswith("```"):
                    return "\n".join(body)
                body.append(later)
            return None
    return None


def squash(text):
    return " ".join(text.split())


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
    if sum(line.startswith("```") for line in text.splitlines()) % 2:
        errors.append("a code block is opened with ``` and never closed")
    header, sections = split(text.splitlines(), "## ")

    for name in HEADER_FIELDS:
        value = field(header, name)
        if value is None:
            errors.append(f"header is missing '{name}:'")
        elif not value:
            errors.append(f"header '{name}:' is empty")
    reproduced = field(header, "Last reproduced")
    if reproduced and not PLACEHOLDER.search(reproduced):
        when = parse_date(reproduced)
        if when is None:
            errors.append(f"'Last reproduced:' is not a calendar date (YYYY-MM-DD): {reproduced!r}")
        elif max_age is not None and ((today or date.today()) - when).days > max_age:
            errors.append(f"'Last reproduced:' {reproduced} is more than {max_age} days old")

    entries = [(title, body) for title, body in sections if title != LAST_SECTION]
    if not entries:
        errors.append("no entry found (an entry is a '## ' heading with the error text or symptom)")

    seen, causes_checked, quoted = set(), 0, 0
    for title, body in entries:
        if title in seen:
            errors.append(f"entry '{title}' appears twice (give one entry two causes instead)")
        seen.add(title)

        lead, causes = split(body, "### ")
        first = next((line.strip() for line in lead if line.strip()), "")
        symptom = block(lead, "Symptom")
        if first != "Symptom:":
            errors.append(f"entry '{title}' does not start with 'Symptom:'")
        elif not (symptom or "").strip():
            errors.append(f"entry '{title}' has no output in a code block under 'Symptom:'")

        spans = [span for span in CODE_SPAN.findall(title) if not PLACEHOLDER.search(span)]
        if spans:
            quoted += 1
        for span in spans:
            wanted = squash(span[:-3] if span.endswith("...") else span)
            if symptom is not None and wanted not in squash(symptom):
                errors.append(f"entry '{title}': the heading quotes `{span}`, which is not in its Symptom block")

        if not causes:
            errors.append(f"entry '{title}' has no '### ' cause")
        for cause, steps in causes:
            causes_checked += 1
            where = f"cause '{cause}' of entry '{title}'"
            for name in CAUSE_FIELDS:
                if not field(steps, name):
                    errors.append(f"{where} is missing '{name}:'")
            for name in CAUSE_BLOCKS:
                if not (block(steps, name) or "").strip():
                    errors.append(f"{where} has no command in a code block under '{name}:'")

    last = dict(sections).get(LAST_SECTION)
    if last is None:
        errors.append(f"missing '## {LAST_SECTION}'")
    else:
        for name in LAST_SECTION_FIELDS:
            if not field(last, name):
                errors.append(f"'{LAST_SECTION}' is missing '{name}:'")

    placeholders = PLACEHOLDER.findall(text)
    if filled and placeholders:
        errors.append(f"{len(placeholders)} unfilled placeholder(s), first: {placeholders[0]}")
    return errors, len(entries), causes_checked, quoted, len(placeholders)


def main(argv):
    filled = "--filled" in argv
    max_age = None
    if "--max-age" in argv:
        max_age = int(argv[argv.index("--max-age") + 1])
        argv = argv[:argv.index("--max-age")] + argv[argv.index("--max-age") + 2:]
    paths = [a for a in argv if not a.startswith("--")]
    path = Path(paths[0]) if paths else Path(__file__).with_name("troubleshooting-guide-template.md")
    errors, entries, causes, quoted, placeholders = check(path.read_text(encoding="utf-8"), filled, max_age)
    if errors:
        print(f"{path.name}: FAIL ({len(errors)} problem(s))")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"{path.name}: PASS")
    print(f"  entries checked: {entries}")
    print(f"  causes checked: {causes}")
    print(f"  entries whose heading quotes the error text: {quoted} of {entries}")
    print(f"  unfilled placeholders: {placeholders}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
