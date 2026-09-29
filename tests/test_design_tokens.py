"""The shared design system stays the only source of styling for site pages.

Repeated spacing, weight, tracking, line-height, rule and layer values live as tokens in
the :root block of static/css/main.css. Templates, articles and site scripts style through
classes, never inline. The few values that remain raw are listed here by name, so a new
one-off fails loudly instead of accumulating.

Out of scope here: the standalone iframe visuals in static/visuals/ cannot inherit
main.css and carry their own <style> blocks.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_DIR = ROOT / "static" / "css"
STYLESHEETS = sorted(CSS_DIR.glob("*.css"))
SPACING = re.compile(
    r"(?:^|[{;])\s*(?:margin|padding|gap|row-gap|column-gap|top|right|bottom|left|inset|scroll-margin-top)"
    r"(?:-[a-z-]+)?\s*:\s*([^;{}]+)"
)

# Single-use values that sit off the spacing scale by more than a rounding error.
# Snapping them would visibly move the component, so each is kept and named.
RAW_SPACING_EXCEPTIONS = {
    ("main.css", "padding: 7rem 0 5.5rem"),       # .hero: homepage first-screen rhythm
    ("main.css", "margin-top: 2.75rem"),          # .page-content-legal h2
    ("main.css", "padding: 0.45rem"),             # .page-row-controls select
    ("main.css", "margin: 0.45rem 0 0 var(--space-1-5)"),  # .toc ul ul
    ("main.css", "gap: 0.55rem"),                 # .article-summary ul
    ("main.css", "padding-left: 1.2rem"),         # .article-summary ul bullet indent
    ("main.css", "margin-top: 3.25rem"),          # .post-content h3
    ("main.css", "margin-top: 2.25rem"),          # .post-content h4
    ("main.css", "margin: 0.8rem 5% 0"),          # .visual-caption
    ("main.css", "margin-top: 0.45rem"),          # .task-status-dot optical alignment
    ("main.css", "margin-top: 0.15rem"),          # .task-badge optical alignment
}
RAW_LINE_HEIGHT_EXCEPTIONS = {
    ("main.css", "0"),      # .tcard-quote::before decorative glyph
    ("main.css", "1.7"),    # .footer-desc
    ("flowcharts.css", "1.45"),  # .flowchart-node strong, sized with the diagram geometry
}


def css_without_tokens(path):
    """A stylesheet's rules with comments and the :root token definitions removed."""
    css = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
    return re.sub(r"(?m)^\s*--[\w-]+\s*:[^;]*;", "", css)


class TokenUsageTests(unittest.TestCase):
    def test_spacing_uses_the_scale_or_a_named_exception(self):
        for path in STYLESHEETS:
            for match in SPACING.finditer(css_without_tokens(path)):
                value = " ".join(match.group(1).split())
                if not re.search(r"(?<![\w-])\d*\.?\d+rem\b", re.sub(r"var\([^)]*\)", "", value)):
                    continue
                declaration = match.group(0).lstrip("{; \n").split(":")[0].strip() + ": " + value
                with self.subTest(file=path.name, declaration=declaration):
                    self.assertIn((path.name, declaration), RAW_SPACING_EXCEPTIONS)

    def test_font_weight_and_letter_spacing_use_tokens(self):
        raw = re.compile(r"font-weight:\s*\d|letter-spacing:\s*-?\d|\bfont:\s*\d{3}\b")
        for path in STYLESHEETS:
            with self.subTest(file=path.name):
                self.assertEqual(raw.findall(css_without_tokens(path)), [])

    def test_line_height_uses_tokens_or_a_named_exception(self):
        for path in STYLESHEETS:
            for value in re.findall(r"line-height:\s*([\d.]+)\s*[;}]", css_without_tokens(path)):
                with self.subTest(file=path.name, value=value):
                    self.assertIn((path.name, value), RAW_LINE_HEIGHT_EXCEPTIONS)

    def test_repeated_rules_and_page_layers_use_tokens(self):
        raw = re.compile(
            r"1px solid var\(--border(?:-2)?\)|3px solid var\(--accent\)|2px solid var\(--accent\)"
            r"|z-index:\s*(?:100|200|300|999|1000)\b|\b0\.2s\b|\b0\.25s\b"
        )
        for path in STYLESHEETS:
            with self.subTest(file=path.name):
                self.assertEqual(raw.findall(css_without_tokens(path)), [])

    def test_no_selector_sets_a_property_twice_in_one_context(self):
        """A second declaration for the same selector, property and media query makes the
        first one dead weight. Grouped selectors are split so a shared rule is caught too."""
        for path in STYLESHEETS:
            seen = {}
            for context, selector, body in _rules(css_without_tokens(path)):
                for declaration in body.split(";"):
                    if ":" not in declaration:
                        continue
                    prop = declaration.split(":", 1)[0].strip()
                    for single in selector.split(","):
                        key = (context, " ".join(single.split()), prop)
                        with self.subTest(file=path.name, rule=key):
                            self.assertNotIn(key, seen)
                        seen[key] = True


def _rules(css, context=""):
    rules, index = [], 0
    while True:
        match = re.search(r"([^{}]+)\{", css[index:])
        if not match:
            return rules
        selector = " ".join(match.group(1).split())
        start = index + match.end()
        depth, end = 1, start
        while depth and end < len(css):
            depth += css[end] == "{"
            depth -= css[end] == "}"
            end += 1
        body = css[start:end - 1]
        if selector.startswith(("@media", "@supports")):
            rules.extend(_rules(body, context + selector))
        elif not selector.startswith("@"):
            rules.append((context, selector, body))
        index = end


class InlineStyleTests(unittest.TestCase):
    INLINE_ATTRIBUTE = re.compile(r"\sstyle\s*=\s*[\"']", re.I)

    def test_templates_and_articles_carry_no_inline_style_attributes(self):
        sources = [*sorted((ROOT / "templates").glob("*.html")), *sorted((ROOT / "content").rglob("*.md")),
                   *sorted((ROOT / "content").rglob("*.yaml"))]
        for path in sources:
            with self.subTest(file=str(path.relative_to(ROOT))):
                self.assertIsNone(self.INLINE_ATTRIBUTE.search(path.read_text(encoding="utf-8")))

    def test_site_scripts_style_through_classes(self):
        """The reading-progress width is the one per-frame value no class can hold."""
        allowed = {("main.js", "bar.style.width")}
        for path in sorted((ROOT / "static" / "js").glob("*.js")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name, check="generated markup"):
                self.assertIsNone(self.INLINE_ATTRIBUTE.search(source))
            for write in re.findall(r"[\w.]+\.style(?:\.[\w]+|\.cssText|\.setProperty)", source):
                with self.subTest(file=path.name, write=write):
                    self.assertIn((path.name, write), allowed)

    def test_the_critical_theme_style_is_the_only_style_element(self):
        """base.html paints the themed background before main.css loads, so it cannot use
        tokens. Its two colors must stay equal to --bg in both themes."""
        base = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
        self.assertEqual(base.count("<style"), 1)
        css = (CSS_DIR / "main.css").read_text(encoding="utf-8")
        light = re.search(r":root\s*\{[^}]*?--bg:\s*(#[0-9a-f]+)", css).group(1)
        dark = re.search(r"\[data-theme=\"dark\"\]\s*\{[^}]*?--bg:\s*(#[0-9a-f]+)", css).group(1)
        critical = base.split("<style>", 1)[1].split("</style>", 1)[0]
        self.assertRegex(critical, r"html \{\s*background: " + light)
        self.assertRegex(critical, r"html\[data-theme=\"dark\"\] \{\s*background: " + dark)
        for template in sorted((ROOT / "templates").glob("*.html")):
            if template.name != "base.html":
                with self.subTest(template=template.name):
                    self.assertNotIn("<style", template.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
