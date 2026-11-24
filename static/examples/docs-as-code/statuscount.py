#!/usr/bin/env python3
"""Count the HTTP status codes in an access log in Common Log Format."""
import argparse
import sys
from collections import Counter


def status_of(line):
    """Return the status code on one log line, or None when the line has none."""
    parts = line.split('"')
    if len(parts) < 3:
        return None
    fields = parts[2].split()
    if fields and len(fields[0]) == 3 and fields[0].isdigit():
        return int(fields[0])
    return None


def count_statuses(lines, min_status=0):
    """Return (status, count) pairs, highest count first."""
    statuses = (status_of(line) for line in lines)
    counts = Counter(status for status in statuses if status is not None and status >= min_status)
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="statuscount", description=__doc__)
    parser.add_argument("file", help="path to the access log")
    parser.add_argument("--min-status", type=int, default=0, metavar="N",
                        help="leave out status codes below N")
    args = parser.parse_args(argv)
    try:
        with open(args.file, encoding="utf-8", errors="replace") as handle:
            rows = count_statuses(handle, args.min_status)
    except OSError:
        print(f"statuscount: cannot read {args.file}", file=sys.stderr)
        return 2
    for status, count in rows:
        print(f"{status}  {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
