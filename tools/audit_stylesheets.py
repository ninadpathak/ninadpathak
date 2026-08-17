#!/usr/bin/env python3
"""Assert every page that uses a CSS class actually links the stylesheet defining it.

On 2026-08-17 all 25 glossary term pages shipped with correct flowchart markup and no
`flowcharts.css`, so every `span`, `strong` and `small` rendered inline and ran together:
"ASSEMBLYContext is selected for one task stepAvailability does not justify inclusion."
Source review passed it, because the markup was perfect. Only rendering catches a missing
stylesheet, and nothing was rendering.

The full extent was 31 pages across three stylesheets and three separate root causes:

  1. `glossary_term.html` had no `extra_css` block at all — 25 pages.
  2. `post.html` gated `visuals.css` on `"<iframe" in html`, so a `.visual-container`
     wrapping an `<img>` or `<picture>` was missed — 5 pages.
  3. `llms_txt_generator.html` used the `.tool-panel` kit and never linked `linter.css`,
     unstyled since it shipped — 1 page.

This is the cheap deterministic half of the render gate. It cannot judge layout, but it
catches exactly this failure and it runs on every build. The expensive half is a computed
style read in a real browser: a `.flowchart-node` computing to `display: inline` is broken,
`block` or `grid` is fine.

    tools/audit_stylesheets.py            # report
    tools/audit_stylesheets.py --strict   # exit 1 if any page is missing a stylesheet
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

OUTPUT = pathlib.Path("output")

# Class prefix -> the stylesheet that defines it. Keyed on what appears in a class
# attribute, because that is what needs the styles; the element inside is irrelevant.
REQUIREMENTS = {
    "flowcharts.css": re.compile(r'class="[^"]*\bflowchart[a-z-]*\b'),
    "visuals.css": re.compile(r'class="[^"]*\bvisual-(?:wrapper|container|title|caption)\b'),
    "linter.css": re.compile(r'class="[^"]*\btool-(?:panel|section|actions|status|hint)\b'),
}


def audit():
    missing = collections.defaultdict(list)
    served = collections.Counter()
    for page in sorted(OUTPUT.rglob("index.html")):
        html = page.read_text(encoding="utf-8", errors="replace")
        for sheet, pattern in REQUIREMENTS.items():
            if not pattern.search(html):
                continue
            if f"/static/css/{sheet}" in html:
                served[sheet] += 1
            else:
                missing[sheet].append(str(page.relative_to(OUTPUT)).removesuffix("/index.html"))
    return missing, served


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if not (OUTPUT / "sitemap.xml").is_file():
        print("output/ is missing or unbuilt — run `python build.py` first. Refusing to report.")
        return 2

    missing, served = audit()

    # Every stylesheet a page might need must exist in the build, or a correct link 404s.
    absent = [sheet for sheet in REQUIREMENTS
              if not (OUTPUT / "static" / "css" / sheet).is_file()]
    for sheet in absent:
        print(f"MISSING FROM BUILD: static/css/{sheet} is referenced by these rules but is "
              f"not in output/")

    total = sum(len(pages) for pages in missing.values())
    if total:
        print(f"UNSTYLED: {total} page(s) use a class whose stylesheet they never link.\n")
        for sheet, pages in sorted(missing.items()):
            print(f"  {sheet} — {len(pages)} page(s):")
            for path in pages:
                print(f"      /{path}/")
    else:
        print("every page that uses a class links the stylesheet defining it")

    print(f"\nserved correctly: {dict(served)}")
    print("This checks linkage only. It cannot see layout — a computed style read in a")
    print("browser is the other half, and `.flowchart-node` computing to display:inline")
    print("is the signature of this failure.")

    return 1 if (args.strict and (total or absent)) else 0


if __name__ == "__main__":
    sys.exit(main())
