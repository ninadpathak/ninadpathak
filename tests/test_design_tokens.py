"""The shared design system stays the only source of styling for site pages.

Repeated spacing, weight, tracking, line-height, rule and layer values live as tokens in
the :root block of static/css/main.css. Templates, articles and site scripts style through
classes, never inline. The few values that remain raw are listed here by name, so a new
one-off fails loudly instead of accumulating.

The standalone iframe visuals in static/visuals/ cannot inherit main.css. build.py writes
their shared palette, visual-embed.css, from main.css's tokens, so the palette is written
once. Artwork geometry and chart-specific colors stay in each visual.
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

    def test_no_raw_border_value_is_repeated(self):
        """A border or outline written twice with a literal width belongs in a --rule token."""
        counts = {}
        for path in STYLESHEETS:
            for value in re.findall(r"(?:border(?:-[a-z]+)?|outline)\s*:\s*([^;{}]*\d+px[^;{}]*)", css_without_tokens(path)):
                value = " ".join(value.split())
                counts.setdefault(value, []).append(path.name)
        repeated = {value: files for value, files in counts.items() if len(files) > 1}
        self.assertEqual(repeated, {})

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


def _palette(css):
    """(light, dark) custom properties from :root and its prefers-color-scheme twin."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    light, dark = {}, {}
    for context, selector, body in _rules(css):
        if selector != ":root":
            continue
        target = light if not context else dark if "prefers-color-scheme" in context else None
        if target is not None:
            for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+)", body):
                value = re.sub(r"#([0-9a-f])([0-9a-f])([0-9a-f])\b", r"#\1\1\2\2\3\3", " ".join(value.split()).lower())
                target[name] = value
    return light, dark


class VisualEmbedPaletteTests(unittest.TestCase):
    VISUALS = ROOT / "static" / "visuals"
    LINK = '<link rel="stylesheet" href="/static/css/visual-embed.css">'
    # Three.js and canvas scenes with fixed artwork colors, or palettes of their own.
    UNLINKED = {
        "beam-benchmark.html", "claude-code-memory.html", "context-memory.html", "deerflow-memory.html",
        "hyperagents-memory.html", "memory-hierarchy.html", "memory-management.html", "rag-vs-memory.html",
        "short-term-memory.html", "state-memory.html", "voice-memory.html",
        "embedding-space.html", "matryoshka-truncation.html",
        # References --text-3 and --border without defining them; linking would change it.
        "vector-space.html",
    }

    @classmethod
    def setUpClass(cls):
        import tempfile
        from build import SiteBuilder
        builder = SiteBuilder.__new__(SiteBuilder)
        with tempfile.TemporaryDirectory() as directory:
            builder.output = Path(directory)
            builder.build_visual_embed_css()
            cls.shared_css = (builder.output / "static" / "css" / "visual-embed.css").read_text(encoding="utf-8")
        light, dark = _palette(cls.shared_css)
        cls.shared = {name: (light[name], dark.get(name, light[name])) for name in light}

    def test_generated_palette_matches_main_css_in_both_themes(self):
        css = (CSS_DIR / "main.css").read_text(encoding="utf-8")
        light = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", re.search(r":root\s*\{(.*?)\}", css, re.S).group(1)))
        dark = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", re.search(r"\[data-theme=\"dark\"\]\s*\{(.*?)\}", css, re.S).group(1)))
        for name, (shared_light, shared_dark) in self.shared.items():
            with self.subTest(token=name):
                self.assertEqual(shared_light, light[name].strip().lower())
                self.assertEqual(shared_dark, dark.get(name, light[name]).strip().lower())

    def test_visuals_link_the_shared_palette_instead_of_pasting_it(self):
        for path in sorted(self.VISUALS.glob("*.html")):
            html = path.read_text(encoding="utf-8")
            linked = self.LINK in html
            with self.subTest(visual=path.name):
                self.assertEqual(linked, path.name not in self.UNLINKED)
            if not linked:
                continue
            styles = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
            self.assertLess(html.index(self.LINK), html.index("<style"), path.name)
            light, dark = _palette(styles)
            for name in set(light) | set(dark):
                local = (light.get(name), dark.get(name, light.get(name)))
                with self.subTest(visual=path.name, token=name):
                    self.assertNotEqual(local, self.shared.get(name), "duplicates visual-embed.css")


class VisualInlineStyleTests(unittest.TestCase):
    """Visual markup styles through classes: shared ones in visual-utilities.css, the rest
    in the visual's own <style>. State changes toggle classes.

    Scripts in the listed visuals still write computed geometry: a bar width taken from
    data, a tooltip or packet position, a label placed from the scene. Those are runtime
    values, and no other visual may add one without being listed here.
    """
    VISUALS = ROOT / "static" / "visuals"
    RUNTIME_STYLE_WRITERS = {
        "context-compression.html",
        "context-window-sliding.html",
        "embedding-space.html",
        "evaluation-funnel.html",
        "json-vs-yaml-tokens.html",
        "latency-tradeoff.html",
        "lost-in-the-middle.html",
        "matryoshka-truncation.html",
        "mcp-architecture.html",
        "memory-finetuning-decision.html",
        "memory-hierarchy.html",
        "onboarding-path.html",
        "rag-eval-metrics.html",
        "rag-finetuning-decision.html",
        "release-hierarchy.html",
        "semantic-cache.html",
        "state-memory.html",
        "token-byte-pair.html",
        "trust-hierarchy.html",
        "ttft-chain.html",
        "voice-memory.html",
    }

    def test_visual_markup_carries_no_inline_style_attributes(self):
        for path in sorted(self.VISUALS.glob("*.html")):
            with self.subTest(visual=path.name):
                self.assertIsNone(re.search(r"\sstyle\s*=\s*\\?[\"']", path.read_text(encoding="utf-8")))

    UTILITIES = ROOT / "static" / "css" / "visual-utilities.css"
    UTILITY_LINK = '<link rel="stylesheet" href="/static/css/visual-utilities.css">'
    UTILITY_RULE = re.compile(r"((?:\.u-[\w-]+)+)\s*\{([^}]*)\}")

    def test_each_utility_is_defined_once(self):
        """A utility used by two visuals lives in the shared file, never in both visuals."""
        definitions = {}
        for match in self.UTILITY_RULE.finditer(self.UTILITIES.read_text(encoding="utf-8")):
            definitions.setdefault(match.group(1).split(".")[1], []).append("visual-utilities.css")
        users = {}
        for path in sorted(self.VISUALS.glob("*.html")):
            html = path.read_text(encoding="utf-8")
            for match in self.UTILITY_RULE.finditer(html):
                definitions.setdefault(match.group(1).split(".")[1], []).append(path.name)
            for name in set(re.findall(r"\bu-[\w-]+(?=[\s\"'])", html)):
                users.setdefault(name, set()).add(path.name)
        for name, places in definitions.items():
            with self.subTest(utility=name):
                self.assertEqual(len(places), 1, places)
                if len(users.get(name, ())) > 1:
                    self.assertEqual(places, ["visual-utilities.css"])
        for name in users:
            with self.subTest(utility=name, check="defined"):
                self.assertIn(name, definitions)

    def test_visuals_using_shared_utilities_link_them_before_their_own_style(self):
        shared = {m.group(1).split(".")[1] for m in self.UTILITY_RULE.finditer(self.UTILITIES.read_text(encoding="utf-8"))}
        for path in sorted(self.VISUALS.glob("*.html")):
            html = path.read_text(encoding="utf-8")
            uses = shared & set(re.findall(r"\bu-[\w-]+(?=[\s\"'])", html))
            with self.subTest(visual=path.name):
                self.assertEqual(self.UTILITY_LINK in html, bool(uses))
                if uses:
                    self.assertLess(html.index(self.UTILITY_LINK), html.index("<style"))

    def test_only_listed_visuals_write_runtime_styles(self):
        for path in sorted(self.VISUALS.glob("*.html")):
            scripts = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", path.read_text(encoding="utf-8"), re.S))
            writes = re.search(r"\.style\.[a-zA-Z]+\s*=(?!=)|\.style\.cssText", scripts)
            with self.subTest(visual=path.name):
                self.assertEqual(bool(writes), path.name in self.RUNTIME_STYLE_WRITERS)


class InlineStyleTests(unittest.TestCase):
    INLINE_ATTRIBUTE = re.compile(r"\sstyle\s*=\s*[\"']", re.I)

    def test_templates_and_articles_carry_no_inline_style_attributes(self):
        sources = [*sorted((ROOT / "templates").glob("*.html")), *sorted((ROOT / "content").rglob("*.md")),
                   *sorted((ROOT / "content").rglob("*.yaml"))]
        for path in sources:
            with self.subTest(file=str(path.relative_to(ROOT))):
                self.assertIsNone(self.INLINE_ATTRIBUTE.search(path.read_text(encoding="utf-8")))

    def test_site_scripts_style_through_classes(self):
        """Two values are data no class can hold: the reading-progress width, set per
        scroll, and an embedded visual's height, reported by the visual itself."""
        allowed = {("main.js", "bar.style.width"), ("post.html", "iframes[i].style.height")}
        scripts = [(path, path.read_text(encoding="utf-8")) for path in sorted((ROOT / "static" / "js").glob("*.js"))]
        for template in sorted((ROOT / "templates").glob("*.html")):
            inline = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", template.read_text(encoding="utf-8"), re.S)
            scripts.append((template, "\n".join(inline)))
        for path, source in scripts:
            with self.subTest(file=path.name, check="generated markup"):
                self.assertIsNone(self.INLINE_ATTRIBUTE.search(source))
            for write in re.findall(r"[\w.\[\]]+\.style(?:\.[\w]+|\.cssText|\.setProperty)", source):
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
