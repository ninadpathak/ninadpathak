#!/usr/bin/env python3
"""Classify documentation subjects as internal, external, split, or review."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

REQUIRED = {
    "artifact",
    "external_reader_task",
    "sensitive_internal_context",
    "internal_operator_task",
    "owner",
    "update_trigger",
}
BOOLEAN_FIELDS = {
    "external_reader_task",
    "sensitive_internal_context",
    "internal_operator_task",
}


def validate(item: dict) -> None:
    missing = sorted(REQUIRED - set(item))
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")
    blank = [field for field in ("artifact", "owner", "update_trigger") if not str(item[field]).strip()]
    if blank:
        raise ValueError(f"blank required field(s): {', '.join(blank)}")
    bad_bools = [field for field in BOOLEAN_FIELDS if not isinstance(item[field], bool)]
    if bad_bools:
        raise ValueError(f"field(s) must be true or false: {', '.join(sorted(bad_bools))}")


def classify(item: dict) -> dict[str, str]:
    validate(item)
    external = item["external_reader_task"]
    sensitive = item["sensitive_internal_context"]
    internal = item["internal_operator_task"]

    if external and (sensitive or internal):
        placement = "split"
        reason = "External readers need an answer, but internal operating or sensitive context needs a separate private source."
    elif external:
        placement = "external"
        reason = "An external reader needs this information to evaluate, use, integrate with, or recover the product."
    elif sensitive or internal:
        placement = "internal"
        reason = "The artifact exists for internal operation or contains context that should not cross the public boundary."
    else:
        placement = "review"
        reason = "No owned reader task establishes where this artifact belongs."

    return {
        "artifact": str(item["artifact"]),
        "placement": placement,
        "reason": reason,
        "owner": str(item["owner"]),
        "update_trigger": str(item["update_trigger"]),
    }


def run(input_path: Path, output_path: Path) -> Counter:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    items = payload.get("artifacts", [])
    if not items:
        raise ValueError("input must contain at least one artifact")
    results = [classify(item) for item in items]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["artifact", "placement", "reason", "owner", "update_trigger"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(results)
    return Counter(row["placement"] for row in results)


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=here / "documentation-placement-audit.json")
    parser.add_argument("--output", type=Path, default=here / "documentation-placement-audit-report.csv")
    args = parser.parse_args()
    try:
        counts = run(args.input, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"AUDIT FAILED: {exc}", file=sys.stderr)
        return 1
    ordered = ", ".join(f"{key}={counts.get(key, 0)}" for key in ("internal", "external", "split", "review"))
    print(f"AUDIT PASSED: {sum(counts.values())} artifacts, {ordered}")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
