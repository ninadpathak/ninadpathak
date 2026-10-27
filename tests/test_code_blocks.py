"""Code blocks: the theme meets AA, the build frames every block, inline code keeps tokens whole.

The theme is checked for every Pygments token type, not just the ones today's articles
use, so a new language can't introduce an unreadable color. The built-site checks skip
when output/ is absent, like the other build tests.
"""
import re
import unittest
from pathlib import Path

from pygments import token as T

from code_blocks import DARK_STYLE, LIGHT_STYLE, PALETTES, soften_inline_code

ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / "output"


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def all_tokens(style):
    """Every token type the style resolves: all of Pygments' types when the style was built.

    Lexers can mint new subtypes when they are imported (LilyPond adds
    Name.Builtin.GrobProperty), and a style built before that raises KeyError for them,
    so walking Token's live subtypes would depend on test order.
    """
    return [tok for tok, _ in style]


def css_var(css: str, scope: str, name: str) -> str:
    block = re.search(re.escape(scope) + r"\s*\{(.*?)\}", css, re.S).group(1)
    return re.search(r"--" + re.escape(name) + r":\s*(#[0-9a-fA-F]{6})", block).group(1)


class ThemeContrastTests(unittest.TestCase):
    def test_every_token_type_meets_aa_in_both_themes(self):
        for style, name in ((LIGHT_STYLE, "light"), (DARK_STYLE, "dark")):
            bg = PALETTES[name]["bg"]
            for tok in all_tokens(style):
                color = style.style_for_token(tok)["color"]
                with self.subTest(theme=name, token=str(tok)):
                    self.assertIsNotNone(color, "every token resolves to a palette color")
                    self.assertGreaterEqual(contrast("#" + color, bg), 4.5)

    def test_head_strip_text_meets_aa(self):
        main = (ROOT / "static/css/main.css").read_text(encoding="utf-8")
        blocks = (ROOT / "static/css/code-blocks.css").read_text(encoding="utf-8")
        for theme, site_scope, block_scope in (
            ("light", ":root", ".code-block"),
            ("dark", '[data-theme="dark"]', '[data-theme="dark"] .code-block'),
        ):
            head = css_var(blocks, block_scope, "code-head")
            for role in ("text-3", "text-1", "status-success"):
                with self.subTest(theme=theme, role=role):
                    self.assertGreaterEqual(contrast(css_var(main, site_scope, role), head), 4.5)

    def test_code_background_is_the_site_surface(self):
        main = (ROOT / "static/css/main.css").read_text(encoding="utf-8")
        self.assertEqual(PALETTES["light"]["bg"], css_var(main, ":root", "bg-1"))
        self.assertEqual(PALETTES["dark"]["bg"], css_var(main, '[data-theme="dark"]', "bg-1"))


class InlineCodeTests(unittest.TestCase):
    def test_short_inline_code_is_left_alone(self):
        html = "<p>Put the name before <code>-e</code>.</p>"
        self.assertEqual(soften_inline_code(html), html)

    def test_long_inline_code_breaks_only_between_words_and_after_delimiters(self):
        out = soften_inline_code("<p><code>claude mcp add --scope project docs-search</code></p>")
        self.assertIn('<code class="code-long">', out)
        self.assertIn('<span class="code-seg">--scope</span>', out)
        self.assertIn('<span class="code-seg">docs-search</span>', out)

    def test_long_path_gets_break_points_after_slashes(self):
        out = soften_inline_code("<p><code>static/images/diagrams/agent-harnesses/harness-layers.svg</code></p>")
        self.assertIn('static/</span><wbr><span class="code-seg">images/', out)

    def test_entities_survive(self):
        out = soften_inline_code("<p><code>if a &lt; b &amp;&amp; c &gt; d then return value</code></p>")
        self.assertIn("&lt;", out)
        self.assertIn("&amp;&amp;", out)
        self.assertNotIn("&amp;lt;", out)

    def test_code_inside_pre_is_untouched(self):
        html = '<pre><span></span><code>a very long line of plain text inside a block\n</code></pre>'
        self.assertEqual(soften_inline_code(html), html)


@unittest.skipUnless((OUTPUT / "articles").exists(), "run python build.py first")
class BuiltCodeBlockTests(unittest.TestCase):
    def pages(self):
        for page in sorted((OUTPUT / "articles").glob("*/index.html")):
            html = page.read_text(encoding="utf-8")
            if "<pre" in html:
                yield page.parent.name, html

    def test_every_block_is_framed_with_a_language_label(self):
        count = 0
        for slug, html in self.pages():
            frames = re.findall(
                r'<div class="code-block code-block--(scroll|wrap)" data-lang="([a-z0-9+#-]+)">'
                r'<div class="code-block-head"><span class="code-block-lang">([^<]+)</span></div>'
                r'<div class="highlight"><pre>', html)
            with self.subTest(slug=slug):
                self.assertEqual(len(frames), html.count("<pre"), "every <pre> sits in a frame")
                for mode, lang, label in frames:
                    self.assertEqual(lang, label)
                    self.assertEqual(mode == "wrap", lang in {"text", "markdown", "md", "prompt", "plaintext", "txt"})
                self.assertIn("/static/css/code-blocks.css", html)
                self.assertIn("/static/css/highlight.css", html)
            count += len(frames)
        self.assertGreater(count, 100)

    def test_no_copy_button_ships_in_the_html(self):
        for slug, html in self.pages():
            with self.subTest(slug=slug):
                self.assertNotIn('class="code-copy"', html)
