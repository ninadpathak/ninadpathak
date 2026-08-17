#!/usr/bin/env python3
"""Find CSS declarations the browser silently discards.

`audit_stylesheets.py` proves a page LINKS the stylesheet it needs. It cannot prove the rules
inside that stylesheet do anything. On 2026-08-17, with every stylesheet correctly linked and
every audit green, this was live:

    .flowchart-outcome .flowchart-edge-label { margin-bottom: var(--space-1); }

The element is `<span class="flowchart-edge-label">`, a span is inline by default, and
**vertical margin on an inline box has no layout effect**. The stylesheet asked for 4px and
the browser discarded it. Source review passes this every time, because the CSS reads
correctly — it was found by reading computed style in a real browser.

WHY THIS IS CONTEXT-AWARE, which cost two wrong attempts. The first version keyed on the
class name and reported `.btn-block { width: 100% }` as inert on an `<a>`; false, because the
same element carries `.btn`, which sets `display: inline-flex`. Fixing that by unioning the
classes on the element then made the checker blind to its own founding case, because
`.flowchart-edge-label` IS blockified — by `.flowchart-branch > .flowchart-edge-label`, in a
DIFFERENT context. One class, two contexts, opposite answers. Any check that asks "is this
class blockified" rather than "is this ELEMENT blockified" gets one of those two cases wrong.

So this resolves real elements. It builds a DOM from the built HTML with stdlib html.parser,
matches the simple selector grammar this codebase actually uses (class and tag, descendant
and child), and for each element asks whether ANY matching rule gives it a box.

It refuses to judge selectors outside that grammar — pseudo-classes and attribute selectors
are counted and reported as unexamined rather than silently assumed harmless, because a gate
that hides its own blind spot is worse than no gate.

    tools/audit_inert_css.py            # report
    tools/audit_inert_css.py --strict   # exit 1 on any inert declaration
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

OUTPUT = pathlib.Path("output")
CSS_DIR = pathlib.Path("static/css")

INLINE_TAGS = {"span", "a", "em", "strong", "small", "code", "label", "b", "i", "abbr",
               "cite", "kbd", "samp", "var", "sub", "sup", "time", "mark", "q", "s", "u"}

# An inline box ignores these. Horizontal margin and all padding DO apply, so they are absent.
INERT_ON_INLINE = ("margin-top", "margin-bottom", "width", "height", "max-height",
                   "min-height")

# A flex or grid PARENT blockifies its children, so their vertical margin works and their
# width applies. Checked against the parent element, not the child's own classes: the third
# false positive this checker produced was `<span class="tool-hint">` inside
# `<div class="tool-actions">`, where .tool-actions is display:flex.
FLEX_OR_GRID = re.compile(r"display\s*:\s*(?:inline-)?(?:flex|grid)")

BLOCKIFIES = re.compile(
    r"display\s*:\s*(?!inline\s*[;}]|inline\s*$)"
    r"|position\s*:\s*(?:absolute|fixed)"
    r"|float\s*:\s*(?:left|right)")

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "param", "source", "track", "wbr"}

COMMENT = re.compile(r"/\*.*?\*/", re.S)
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
SIMPLE = re.compile(r"^(?:[.#]?[A-Za-z0-9_-]+)(?:\s*[>\s]\s*[.#]?[A-Za-z0-9_-]+)*$")


class Node:
    __slots__ = ("tag", "classes", "parent", "page")

    def __init__(self, tag, classes, parent, page):
        self.tag, self.classes, self.parent, self.page = tag, classes, parent, page

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent


class Tree(HTMLParser):
    """Every element in one page, each knowing its parent. Enough for descendant matching."""

    def __init__(self, page):
        super().__init__(convert_charrefs=True)
        self.page, self.stack, self.nodes = page, [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = frozenset((attrs.get("class") or "").split())
        node = Node(tag, classes, self.stack[-1] if self.stack else None, self.page)
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return


def parse_selector(selector: str):
    """`.a > .b c` -> [('.a', False), ('.b', True), ('c', False)] as (token, is_child)."""
    parts, child = [], False
    for token in re.split(r"\s*(>)\s*|\s+", selector.strip()):
        if token is None or token == "":
            continue
        if token == ">":
            child = True
            continue
        parts.append((token, child))
        child = False
    return parts


def matches_token(node: Node, token: str) -> bool:
    if token.startswith("."):
        return token[1:] in node.classes
    if token.startswith("#"):
        return False  # ids are not tracked; such rules are reported as unexamined
    return node.tag == token.lower()


def matches(node: Node, compound) -> bool:
    """Right-to-left match of a descendant/child chain against this node's ancestry."""
    token, is_child = compound[-1]
    if not matches_token(node, token):
        return False
    current, remaining = node, list(compound[:-1])
    while remaining:
        token, is_child = remaining[-1]
        if is_child:
            parent = current.parent
            if parent is None or not matches_token(parent, token):
                return False
            current, remaining = parent, remaining[:-1]
        else:
            for ancestor in current.ancestors():
                if matches_token(ancestor, token):
                    current, remaining = ancestor, remaining[:-1]
                    break
            else:
                return False
    return True


def load_rules(css_files):
    simple, unexamined = [], 0
    for path in css_files:
        css = COMMENT.sub(" ", path.read_text(encoding="utf-8"))
        for match in RULE.finditer(css):
            selectors, body = match.group(1), match.group(2)
            if "@" in selectors:
                selectors = selectors.rsplit("{", 1)[-1]
            for selector in selectors.split(","):
                selector = selector.strip()
                if not selector or selector.startswith("@"):
                    continue
                if not SIMPLE.match(selector) or "#" in selector:
                    unexamined += 1
                    continue
                simple.append((path.name, selector, parse_selector(selector), body))
    return simple, unexamined


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if not (OUTPUT / "sitemap.xml").is_file():
        print("output/ is missing or unbuilt — run `python build.py` first. Refusing to report.")
        return 2
    css_files = sorted(CSS_DIR.glob("*.css"))
    if not css_files:
        print(f"no stylesheets in {CSS_DIR} — refusing to report.")
        return 2

    rules, unexamined = load_rules(css_files)
    inert_rules = [r for r in rules
                   if any(re.search(rf"(?<![-\w]){prop}\s*:", r[3]) for prop in INERT_ON_INLINE)]
    box_rules = [r for r in rules if BLOCKIFIES.search(r[3])]
    flex_rules = [r for r in rules if FLEX_OR_GRID.search(r[3])]

    findings, pages_scanned = {}, 0
    for page in sorted(OUTPUT.rglob("*.html")):
        tree = Tree(page.relative_to(OUTPUT).as_posix())
        try:
            tree.feed(page.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        pages_scanned += 1
        for node in tree.nodes:
            if node.tag not in INLINE_TAGS:
                continue
            hits = [r for r in inert_rules if matches(node, r[2])]
            if not hits:
                continue
            if any(matches(node, r[2]) for r in box_rules):
                continue  # something gives this element a box, so the declaration is live
            if node.parent is not None and any(
                    matches(node.parent, r[2]) for r in flex_rules):
                continue  # a flex or grid parent makes it an item, so the declaration is live
            for name, selector, _, body in hits:
                props = [p for p in INERT_ON_INLINE
                         if re.search(rf"(?<![-\w]){p}\s*:", body)]
                key = (name, selector, tuple(props), node.tag)
                findings.setdefault(key, []).append(tree.page)

    if findings:
        print(f"INERT: {len(findings)} rule(s) set a property the browser discards.\n")
        for (name, selector, props, tag) in sorted(findings):
            pages = findings[(name, selector, props, tag)]
            print(f"  {name}: {selector}")
            print(f"      matches <{tag}>, which is inline here, so these do nothing: "
                  f"{', '.join(props)}")
            print(f"      on {len(pages)} page(s), e.g. /{pages[0].removesuffix('index.html')}")
            print("      fix: give the element a box (display: block or inline-block), or "
                  "drop the declaration.\n")
    else:
        print("no inert declaration found on any inline element")

    print(f"scanned {pages_scanned} page(s) against {len(rules)} resolvable rule(s); "
          f"{len(inert_rules)} carry a vertical-spacing or sizing property")
    print(f"UNEXAMINED: {unexamined} selector(s) use pseudo-classes, attributes or ids and "
          f"were not judged.")
    print("Stated rather than hidden: a gate that conceals its blind spot is worse than none.")
    return 1 if (args.strict and findings) else 0


if __name__ == "__main__":
    sys.exit(main())
