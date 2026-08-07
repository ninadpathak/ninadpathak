#!/usr/bin/env python3
"""Validate the minimum sections and editorial evidence in this style-guide template."""
from pathlib import Path
import re
import sys

REQUIRED_HEADINGS = (
    "## 1. Product names and terminology",
    "## 2. Voice, headings, and procedures",
    "## 3. Code and command examples",
    "## 4. UI references and release checks",
)
REQUIRED_MARKERS = (
    "| Concept | Approved term | Avoid | Definition | Owner | Last verified |",
    "| Runtime and version | [for example, Python 3.13.5] |",
    "| UI reference | Approved wording | Verification source | Last verified |",
    "- [ ] Every command has a starting state and expected result.",
)

def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("developer-documentation-style-guide-template.md")
    text = path.read_text(encoding="utf-8")
    errors = [f"missing required section: {item}" for item in REQUIRED_HEADINGS if item not in text]
    errors += [f"missing required evidence marker: {item}" for item in REQUIRED_MARKERS if item not in text]
    empty_cells = len(re.findall(r"\|\s*\[([^\]]+)\]\s*\|", text))
    if errors:
        print(f"Style-guide validation failed: {len(errors)} error(s)")
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print("Style-guide validation passed")
    print(f"File: {path.name}")
    print(f"Required sections: {len(REQUIRED_HEADINGS)}/{len(REQUIRED_HEADINGS)}")
    print(f"Required evidence markers: {len(REQUIRED_MARKERS)}/{len(REQUIRED_MARKERS)}")
    print(f"Editable bracketed cells: {empty_cells}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
