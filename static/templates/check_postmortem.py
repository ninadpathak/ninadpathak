#!/usr/bin/env python3
"""Check a postmortem written from postmortem-template.md before it is reviewed.

Usage:
  python3 check_postmortem.py postmortem.md            # structure only
  python3 check_postmortem.py --filled postmortem.md   # also fail on unfilled {{placeholders}}

Reads the file and nothing else. Exit status is 0 when the postmortem passes and 1 when
it fails, so the check can run in CI on a folder of postmortems.
"""
from datetime import date, datetime, timedelta
from pathlib import Path
import re
import sys

HEADER_FIELDS = ("Status", "Service", "Incident date", "Authors")
STATUSES = ("Draft", "In review", "Final")
SECTIONS = ("Summary", "Impact", "Timeline", "Detection and response", "Root cause",
            "Lessons learned", "Action items")
IMPACT_FIELDS = ("What users saw", "Scope", "Duration", "Data loss")
RESPONSE_FIELDS = ("Detected by", "Time to detect", "Mitigation", "Resolution")
CAUSE_FIELDS = ("Trigger", "Mechanism", "Believed before")
LESSONS = ("What went well", "What went wrong", "Where we got lucky")
TAGS = ("Impact starts", "Detected", "Mitigated", "Resolved")
ACTION_COLUMNS = ("Action", "Type", "Owner", "Due", "Status")
ACTION_TYPES = ("prevent", "detect", "mitigate", "process")
NO_OWNER = ("", "-", "?", "tbd", "none", "n/a", "everyone", "team", "the team")
EMPTY_WORDS = ("none", "n/a", "unknown", "tbd")
# Openings the action-item table in Lunney, Lueder and Beyer's ";login:" article rewrites.
OPEN_ENDED = ("investigate", "make sure")
# Phrases that are written about a person. The list cannot tell whether a sentence
# blames someone, and a postmortem can blame a person without using any of them.
BLAME = (r"human error", r"operator error", r"careless", r"negligen", r"incompeten",
         r"forgot to", r"should have known", r"more careful", r"\b\w+['’]s fault")

PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
COMMENT = re.compile(r"<!--.*?-->", re.S)
FENCE = re.compile(r"^```[^\n]*\n.*?^```[ \t]*$", re.M | re.S)
ISO_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
ROW_TIME = re.compile(r"^(?:(\d{4}-\d{2}-\d{2})[ T])?(\d{2}):(\d{2})(?::(\d{2}))?$")
ZONE = re.compile(r"^UTC(?:[+-]\d{2}:\d{2})?$")
COUNT = re.compile(r"\d[\d,.]*\s*(?:%|(?:of\s+[\d,.]+\s+)?[A-Za-z][A-Za-z-]+)")
SPAN = re.compile(r"(\d+)\s*(days?|d|hours?|hrs?|h|minutes?|mins?|m|seconds?|secs?|s)\b")
UNIT_SECONDS = {"d": 86400, "h": 3600, "m": 60, "s": 1}


def field(text, name):
    """Return the value of a 'Name: value' line, or None when the line is missing."""
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.*)$", text, flags=re.M)
    return match.group(1).strip() if match else None


def split(text, level):
    marker = "#" * level
    parts = re.split(rf"^{marker} (.+)$", text, flags=re.M)
    return parts[0], [(title.strip(), body) for title, body in zip(parts[1::2], parts[2::2])]


def unfilled(value):
    return bool(PLACEHOLDER.search(value or ""))


def parse_date(value):
    match = ISO_DATE.match(value or "")
    if not match:
        return None
    try:
        return date(*map(int, match.groups()))
    except ValueError:
        return None


def parse_span(value):
    """Turn '1 h 12 min' or '21 s (19:54:08 to 19:54:29)' into seconds, or None."""
    found = SPAN.findall(value.split("(")[0])
    if not found:
        return None
    return sum(int(number) * UNIT_SECONDS[unit[0]] for number, unit in found)


def show_span(seconds):
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    parts = [f"{hours} h" if hours else "", f"{minutes} min" if minutes else "", f"{secs} s" if secs else ""]
    return " ".join(part for part in parts if part) or "0 s"


def table(body):
    """Return (header cells, rows) of the first Markdown table in a section."""
    lines = [line.strip() for line in body.splitlines() if line.strip().startswith("|")]
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    rows = [row for row in rows if not all(set(cell) <= set("-: ") for cell in row)]
    return (rows[0], rows[1:]) if rows else ([], [])


def labelled_lists(body, labels):
    """Return {label: [items]} for each 'Label:' line that is followed by '- ' items."""
    found, current = {}, None
    for line in body.splitlines():
        line = line.strip()
        if line.endswith(":") and line[:-1] in labels:
            current = line[:-1]
            found[current] = []
        elif current and line.startswith("- "):
            found[current].append(line[2:].strip())
        elif line and current and not line.startswith("- "):
            current = None
    return found


def check_timeline(body, incident_date, errors):
    """Check the timeline table and return the time of each tagged row."""
    zone = field(body, "Time zone")
    if zone is None:
        errors.append("Timeline is missing 'Time zone:'")
    elif not unfilled(zone) and not ZONE.match(zone):
        errors.append(f"'Time zone:' must be UTC or an offset such as UTC+05:30: {zone!r}")
    header, rows = table(body)
    if [cell.lower() for cell in header] != ["time", "event", "evidence"]:
        errors.append("Timeline needs a table with the columns Time, Event and Evidence")
        return {}, 0
    tagged, day, previous, checked, undated = {}, incident_date, None, 0, False
    for number, row in enumerate(rows, start=1):
        row = row + [""] * (3 - len(row))
        when, event, evidence = row[0], row[1], row[2]
        for tag in TAGS:
            if f"**{tag}**" in event:
                tagged.setdefault(tag, []).append(None)
        if unfilled(when):
            continue
        checked += 1
        match = ROW_TIME.match(when)
        if not match:
            errors.append(f"timeline row {number}: {when!r} is not HH:MM, HH:MM:SS or YYYY-MM-DD HH:MM")
            continue
        day = parse_date(match.group(1)) if match.group(1) else day
        if day is None:
            if not undated:
                errors.append(f"timeline row {number}: no date for {when!r} (fill in 'Incident date:' or write the date in the row)")
            undated = True
            continue
        try:
            stamp = datetime(day.year, day.month, day.day, int(match.group(2)), int(match.group(3)),
                             int(match.group(4) or 0))
        except ValueError:
            errors.append(f"timeline row {number}: {when!r} is not a real time")
            continue
        if previous and stamp < previous:
            errors.append(f"timeline row {number}: {when} is earlier than the row above it "
                          "(past midnight, write the date in the row)")
        previous = max(previous, stamp) if previous else stamp
        if not evidence or evidence.lower() in EMPTY_WORDS:
            errors.append(f"timeline row {number} ({when}) has no evidence")
        for tag in TAGS:
            if f"**{tag}**" in event:
                tagged[tag][-1] = stamp
    for tag in TAGS:
        count = len(tagged.get(tag, []))
        if count > 1:
            errors.append(f"timeline tags {count} rows **{tag}**; tag one")
        elif count == 0 and tag != "Resolved":
            errors.append(f"timeline has no row tagged **{tag}**")
    times = {tag: stamps[0] for tag, stamps in tagged.items() if len(stamps) == 1 and stamps[0]}
    for earlier, later in (("Impact starts", "Detected"), ("Impact starts", "Mitigated"), ("Mitigated", "Resolved")):
        if earlier in times and later in times and times[later] < times[earlier]:
            errors.append(f"timeline puts **{later}** before **{earlier}**")
    return times, checked


def check_span(name, body, derived, errors):
    """Compare a stated duration with the one the timeline gives."""
    value = field(body, name)
    if not value or unfilled(value):
        return
    stated = parse_span(value)
    if stated is None:
        errors.append(f"'{name}:' needs a number and a unit, such as '21 s' or '1 h 12 min': {value!r}")
    elif derived is not None and derived >= 0 and stated != derived:
        errors.append(f"'{name}:' says {show_span(stated)}, and the timeline gives {show_span(derived)}")


def check_actions(body, errors):
    header, rows = table(body)
    if tuple(header) != ACTION_COLUMNS:
        errors.append("Action items needs a table with the columns " + ", ".join(ACTION_COLUMNS))
        return 0, 0
    live = dropped = fixes = 0
    for number, row in enumerate(rows, start=1):
        row = row + [""] * (5 - len(row))
        action, kind, owner, due, status = row[:5]
        if any(unfilled(cell) for cell in row[:5]):
            continue
        label = f"action item {number}"
        if not action:
            errors.append(f"{label} has no action")
        elif action.lower().startswith(OPEN_ENDED):
            opening = next(start for start in OPEN_ENDED if action.lower().startswith(start))
            errors.append(f"{label} starts with '{opening.capitalize()}' and has no finish line; say what will exist when it is done")
        if kind.lower() not in ACTION_TYPES:
            errors.append(f"{label}: Type must be one of {', '.join(ACTION_TYPES)}: {kind!r}")
        if status.lower().startswith(("won't do", "won’t do")):
            dropped += 1
            if not status.split(":", 1)[-1].strip() or ":" not in status:
                errors.append(f"{label} is marked Won't do with no reason after a colon")
            continue
        live += 1
        fixes += kind.lower() in ("prevent", "mitigate")
        if owner.lower() in NO_OWNER:
            errors.append(f"{label} has no owner: {owner!r}")
        if parse_date(due) is None:
            errors.append(f"{label}: Due is not a date (YYYY-MM-DD): {due!r}")
        if not status.startswith(("Open", "Done")):
            errors.append(f"{label}: Status must start with Open, Done or Won't do: {status!r}")
    if not rows:
        errors.append("Action items has no rows")
    elif live and not fixes:
        errors.append("no open or done action item has the type prevent or mitigate")
    return live, dropped


def check(text, filled):
    errors = []
    text = COMMENT.sub("", text)
    prose = FENCE.sub("", text)
    header, sections = split(prose, 2)
    found = dict(sections)

    for name in HEADER_FIELDS:
        value = field(header, name)
        if value is None:
            errors.append(f"header is missing '{name}:'")
        elif not value:
            errors.append(f"header '{name}:' is empty")
    status = field(header, "Status") or ""
    if status and not unfilled(status) and status not in STATUSES:
        errors.append(f"Status must be one of {', '.join(STATUSES)}: {status!r}")
    when = field(header, "Incident date") or ""
    incident_date = parse_date(when)
    if when and not unfilled(when) and incident_date is None:
        errors.append(f"'Incident date:' is not a calendar date (YYYY-MM-DD): {when!r}")

    titles = [title for title, _ in sections if title in SECTIONS]
    for name in SECTIONS:
        if name not in found:
            errors.append(f"missing section '## {name}'")
        elif not found[name].strip():
            errors.append(f"section '## {name}' is empty")
    if all(name in found for name in SECTIONS) and titles != list(SECTIONS):
        errors.append("sections are out of order; keep " + ", ".join(SECTIONS))

    summary = found.get("Summary", "").strip()
    if summary and not unfilled(summary) and not COUNT.search(summary):
        errors.append("Summary has no count with a unit (how many requests, users or minutes)")

    impact = found.get("Impact", "")
    for name in IMPACT_FIELDS:
        if "Impact" in found and not field(impact, name):
            errors.append(f"Impact is missing '{name}:'")
    scope = field(impact, "Scope") or ""
    if scope and not unfilled(scope) and not COUNT.search(scope):
        errors.append(f"'Scope:' needs a count and its unit, such as '155 of 156 write requests': {scope!r}")

    times, rows = ({}, 0)
    if "Timeline" in found:
        times, rows = check_timeline(found["Timeline"], incident_date, errors)

    def between(start, end):
        if start in times and end in times:
            return int((times[end] - times[start]) / timedelta(seconds=1))
        return None

    to_detect, to_mitigate = between("Impact starts", "Detected"), between("Impact starts", "Mitigated")
    check_span("Duration", impact, to_mitigate, errors)

    response = found.get("Detection and response", "")
    for name in RESPONSE_FIELDS:
        if "Detection and response" in found and not field(response, name):
            errors.append(f"Detection and response is missing '{name}:'")
    check_span("Time to detect", response, to_detect, errors)

    cause = found.get("Root cause", "")
    for name in CAUSE_FIELDS:
        value = field(cause, name)
        if "Root cause" not in found:
            break
        if not value:
            errors.append(f"Root cause is missing '{name}:'")
        elif not unfilled(value) and value.lower().rstrip(".") in EMPTY_WORDS:
            errors.append(f"Root cause '{name}:' says {value!r}; write what is known so far")
    mechanism = field(cause, "Mechanism") or ""
    if mechanism and not unfilled(mechanism) and mechanism.lower().rstrip(".") not in EMPTY_WORDS:
        if len(mechanism.split()) < 15:
            errors.append(f"'Mechanism:' is {len(mechanism.split())} words; explain it in at least 15")
        if not re.search(r"`[^`]+`", mechanism):
            errors.append("'Mechanism:' names no setting, file, function or error text in backticks")
    lists = {"Root cause": labelled_lists(cause, ("Contributing factors",)),
             "Lessons learned": labelled_lists(found.get("Lessons learned", ""), LESSONS)}
    for section, names in (("Root cause", ("Contributing factors",)), ("Lessons learned", LESSONS)):
        for name in names:
            if section not in found:
                break
            if name not in lists[section]:
                errors.append(f"{section} is missing '{name}:'")
            elif not lists[section][name]:
                errors.append(f"'{name}:' has no list item (write '- None' if there is nothing)")

    live, dropped = check_actions(found["Action items"], errors) if "Action items" in found else (0, 0)

    for line in prose.splitlines():
        for pattern in BLAME:
            match = re.search(pattern, line, flags=re.I)
            if match:
                errors.append(f"blame phrase {match.group(0)!r} in: {line.strip()[:80]}")

    placeholders = PLACEHOLDER.findall(text)
    if filled and placeholders:
        errors.append(f"{len(placeholders)} unfilled placeholder(s), first: {placeholders[0]}")
    report = {"rows": rows, "zone": field(found.get("Timeline", ""), "Time zone") or "",
              "to_detect": to_detect, "to_mitigate": to_mitigate,
              "live": live, "dropped": dropped, "placeholders": len(placeholders)}
    return errors, report


def main(argv):
    filled = "--filled" in argv
    paths = [a for a in argv if not a.startswith("--")]
    path = Path(paths[0]) if paths else Path(__file__).with_name("postmortem-template.md")
    errors, report = check(path.read_text(encoding="utf-8"), filled)
    if errors:
        print(f"{path.name}: FAIL ({len(errors)} problem(s))")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"{path.name}: PASS")
    zone = "not filled in" if unfilled(report["zone"]) else report["zone"]
    print(f"  timeline rows checked: {report['rows']}, time zone {zone}")
    for label, value in (("time to detect", report["to_detect"]), ("time to mitigate", report["to_mitigate"])):
        print(f"  {label}: {show_span(value) if value is not None else 'not derived (times are placeholders)'}")
    print(f"  action items with an owner and a due date: {report['live']}")
    print(f"  action items marked Won't do, with a reason: {report['dropped']}")
    print(f"  unfilled placeholders: {report['placeholders']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
