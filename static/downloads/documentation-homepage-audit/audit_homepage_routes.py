#!/usr/bin/env python3
"""Audit a documentation homepage route inventory."""
import json
import sys
from pathlib import Path

REQUIRED_JOBS = {"first action", "returning task", "recovery", "exploration"}


def main(path: str) -> int:
    data = json.loads(Path(path).read_text())
    routes = data.get("routes", [])
    jobs = [route.get("job", "") for route in routes]
    labels = [route.get("label", "").strip().lower() for route in routes]
    errors = []
    missing = sorted(REQUIRED_JOBS - set(jobs))
    if missing:
        errors.append("missing route jobs: " + ", ".join(missing))
    if len(labels) != len(set(labels)):
        errors.append("duplicate route labels")
    for index, route in enumerate(routes, start=1):
        if not route.get("label") or not route.get("url") or not route.get("audience"):
            errors.append(f"route {index} needs label, url, and audience")
    if errors:
        print("FAIL")
        print("\n".join(errors))
        return 1
    print("PASS")
    print(f"{len(routes)} routes cover: " + ", ".join(sorted(REQUIRED_JOBS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
