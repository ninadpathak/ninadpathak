#!/usr/bin/env python3
"""Validate that an API docs package contains the path to a working request."""
import json
import sys
from pathlib import Path

REQUIRED = {
    "quickstart": ["prerequisites", "request", "expected_response"],
    "reference": ["endpoint", "authentication", "parameters", "responses"],
    "errors": ["status", "cause", "recovery"],
}

def main(path):
    data = json.loads(Path(path).read_text())
    errors = []
    for page, fields in REQUIRED.items():
        value = data.get(page, {})
        for field in fields:
            if not value.get(field):
                errors.append(f"{page}.{field} is missing")
    if errors:
        print("FAIL")
        print("\n".join(errors))
        return 1
    print("PASS: quickstart, reference, and error recovery form a complete request path")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
