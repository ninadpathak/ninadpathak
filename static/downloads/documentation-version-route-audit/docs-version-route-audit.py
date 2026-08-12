#!/usr/bin/env python3
"""Validate a documentation version's URL policy from a JSON route inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {"path", "version", "status", "canonical", "redirect_to"}


def audit(inventory: dict) -> list[str]:
    errors = []
    routes = inventory.get("routes", [])
    paths = {route.get("path") for route in routes}
    current = inventory.get("current_version")
    for index, route in enumerate(routes, 1):
        missing = REQUIRED - route.keys()
        if missing:
            errors.append(f"route {index}: missing {', '.join(sorted(missing))}")
            continue
        path = route["path"]
        status = route["status"]
        canonical = route["canonical"]
        target = route["redirect_to"]
        if status == "supported":
            if canonical != path:
                errors.append(f"{path}: supported versions need a self-canonical")
            if target:
                errors.append(f"{path}: supported versions must not redirect")
        elif status == "retired":
            if not target or target not in paths:
                errors.append(f"{path}: retired versions need a route-inventory redirect target")
            if canonical:
                errors.append(f"{path}: redirected pages must not publish a canonical")
        elif status == "historical":
            if canonical != path:
                errors.append(f"{path}: historical versions need a self-canonical")
            if target:
                errors.append(f"{path}: historical versions must remain directly reachable")
        else:
            errors.append(f"{path}: unknown status {status!r}")
        if route["version"] == current and status != "supported":
            errors.append(f"{path}: current version must be supported")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    args = parser.parse_args()
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    errors = audit(inventory)
    if errors:
        print("FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("PASS")
    print(f"{len(inventory['routes'])} routes follow the declared version policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
