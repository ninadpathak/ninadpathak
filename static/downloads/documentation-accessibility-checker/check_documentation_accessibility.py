#!/usr/bin/env python3
"""Flag documentation HTML that loses useful accessibility semantics.

Usage: python3 check_documentation_accessibility.py path/to/page.html

This checker is intentionally narrow. It detects inspectable markup problems,
then leaves keyboard behavior, screen-reader output, contrast, and visual order
for a human review.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import TypedDict

VAGUE_LINKS = {"click here", "here", "learn more", "more", "read more"}


class Link(TypedDict):
    text: list[str]


class Table(TypedDict):
    has_header: bool


class DocumentationAccessibilityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.issues: list[str] = []
        self.headings: list[int] = []
        self.stack: list[Link] = []
        self.images = 0
        self.tables: list[Table] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if tag == "img":
            self.images += 1
            if "alt" not in attr:
                self.issues.append("image is missing an alt attribute")
        if tag == "a":
            self.stack.append({"text": []})
        if tag == "table":
            self.tables.append({"has_header": False})
        if tag == "th" and self.tables:
            self.tables[-1]["has_header"] = True
        if tag == "code" and not (attr.get("class") or "").startswith("language-"):
            self.issues.append("code element has no declared language class")

    def handle_data(self, data: str) -> None:
        if self.stack:
            self.stack[-1]["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.stack:
            link = self.stack.pop()
            text = " ".join("".join(link["text"]).split()).lower()
            if text in VAGUE_LINKS:
                self.issues.append(f"link text is too vague: {text!r}")

    def finish(self) -> list[str]:
        if self.headings.count(1) != 1:
            self.issues.append(f"expected one h1, found {self.headings.count(1)}")
        for previous, current in zip(self.headings, self.headings[1:]):
            if current > previous + 1:
                self.issues.append(f"heading level jumps from h{previous} to h{current}")
        for index, table in enumerate(self.tables, start=1):
            if not table["has_header"]:
                self.issues.append(f"table {index} has no th header cells")
        return self.issues


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_documentation_accessibility.py path/to/page.html", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    parser = DocumentationAccessibilityParser()
    parser.feed(path.read_text(encoding="utf-8"))
    issues = parser.finish()
    if issues:
        print(f"FAIL {path}")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS {path}: structural documentation accessibility checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
