#!/usr/bin/env python3
"""Validate the documentation starter's small, intentional contract."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CONFIG = ROOT / "mkdocs.yml"


def fail(message: str) -> None:
    print(f"FAIL {message}")
    raise SystemExit(1)


def nav_targets(text: str) -> list[str]:
    return re.findall(r":\s*([\w./-]+\.md)\s*$", text, flags=re.M)


def local_links(text: str) -> list[str]:
    return re.findall(r"\]\(([^)#]+\.md)(?:#[^)]+)?\)", text)


def resolve(page: Path, target: str) -> Path:
    return (page.parent / target).resolve()


def main() -> None:
    if not CONFIG.exists():
        fail("mkdocs.yml is missing")
    pages = sorted(DOCS.rglob("*.md"))
    if not pages:
        fail("docs contains no Markdown pages")

    config = CONFIG.read_text(encoding="utf-8")
    nav = nav_targets(config)
    for target in nav:
        if not (DOCS / target).is_file():
            fail(f"navigation target missing: {target}")

    for page in pages:
        text = page.read_text(encoding="utf-8")
        h1_count = len(re.findall(r"^# (?!#)", text, flags=re.M))
        if h1_count != 1:
            fail(f"{page.relative_to(ROOT)} has {h1_count} H1 headings")
        for target in local_links(text):
            if not resolve(page, target).is_file():
                fail(f"{page.relative_to(ROOT)} links to missing file: {target}")

    print(f"PASS navigation targets: {len(nav)}")
    print(f"PASS Markdown pages: {len(pages)}")
    print("PASS one H1 and resolvable local Markdown links")


if __name__ == "__main__":
    main()
