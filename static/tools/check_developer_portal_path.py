#!/usr/bin/env python3
"""Validate that a developer portal supports an inspectable first request."""

import json
import sys
from pathlib import Path

REQUIRED = {
    "quickstart": {"credentials", "request", "expected_response", "next_route"},
    "reference": {"endpoint", "parameters", "responses", "errors"},
    "recovery": {"failure", "cause", "action"},
}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_developer_portal_path.py portal-path.json")
        return 2
    data = json.loads(Path(sys.argv[1]).read_text())
    missing = []
    for page, fields in REQUIRED.items():
        current = set(data.get(page, {}))
        absent = sorted(fields - current)
        if absent:
            missing.append(f"{page}: {', '.join(absent)}")
    if missing:
        print("FAIL: " + "; ".join(missing))
        return 1
    print("PASS: the portal connects credentials, a working request, exact behavior, and recovery.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
