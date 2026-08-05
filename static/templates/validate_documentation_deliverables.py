#!/usr/bin/env python3
"""Validate that a documentation-deliverables manifest assigns complete reader coverage."""
from pathlib import Path
import sys
import yaml

required = {"deliverable", "reader", "reader_task", "must_include", "success_signal", "owner", "update_trigger", "defer_if"}
path = Path(__file__).with_name("documentation-deliverables-manifest.yaml")
data = yaml.safe_load(path.read_text(encoding="utf-8"))
rows = data.get("deliverables", [])
errors = []
seen_tasks = set()
for index, row in enumerate(rows, 1):
    missing = required - set(row)
    if missing:
        errors.append(f"row {index}: missing {', '.join(sorted(missing))}")
    task = row.get("reader_task")
    if task in seen_tasks:
        errors.append(f"row {index}: duplicate reader task: {task}")
    seen_tasks.add(task)
if len(rows) < 3:
    errors.append("need at least orientation, a success path, and stable supporting information")
if errors:
    print("MANIFEST INVALID")
    print("\n".join(errors))
    raise SystemExit(1)
print(f"MANIFEST VALID: {len(rows)} deliverables, {len(seen_tasks)} owned reader tasks")
