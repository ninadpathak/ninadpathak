"""Read event lines of the form '<timestamp> <name>'."""
from timeutil import parse_ts


def read_events(lines):
    events = []
    for line in lines:
        stamp, name = line.split(" ", 1)
        events.append((parse_ts(stamp), name.strip()))
    return events
