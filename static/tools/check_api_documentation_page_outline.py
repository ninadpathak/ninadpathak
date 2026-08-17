#!/usr/bin/env python3
"""Check that an API documentation page outline owns every reader decision."""
from pathlib import Path
import sys

REQUIRED_HEADINGS = [
    "## 1. Documentation homepage",
    "## 2. Quickstart",
    "## 3. Authentication guide",
    "## 4. API reference",
    "## 5. Error and troubleshooting guide",
    "## 6. Webhooks or event guide",
    "## 7. Version and change guide",
]


def main(path: str) -> int:
    text = Path(path).read_text(encoding="utf-8")
    missing = [heading[3:] for heading in REQUIRED_HEADINGS if heading not in text]
    if missing:
        print("FAIL: missing page sections")
        print("\n".join(f"- {heading}" for heading in missing))
        return 1
    print("PASS: homepage, quickstart, authentication, reference, recovery, events, and changes are owned")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_api_documentation_page_outline.py <outline.md>")
    raise SystemExit(main(sys.argv[1]))
