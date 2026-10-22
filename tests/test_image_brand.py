"""Share cards and article figures from tools/image-brand, checked against the built site.

The image pipeline itself (contrast, stroke and radius tokens, word budget, staleness)
is checked by `node tools/image-brand/render.mjs --check` in CI. These tests check the
site side: every published post points its og:image at a real 1200x630 card, and every
figure an article embeds exists.
"""
import re
import struct
import unittest
from pathlib import Path

import frontmatter

ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / "output"
SITE = "https://ninadpathak.com"


def published_posts():
    for path in sorted((ROOT / "content/posts").glob("*.md")):
        post = frontmatter.load(path)
        if post.get("status") == "published":
            yield post.get("slug") or path.stem, post


def png_size(path):
    with path.open("rb") as handle:
        header = handle.read(24)
    return struct.unpack(">II", header[16:24])


@unittest.skipUnless((OUTPUT / "articles").exists(), "run python build.py first")
class ShareCardTests(unittest.TestCase):
    def test_posts_with_a_card_use_it_and_posts_without_keep_the_default(self):
        """A missing card is not an error: publishing a post must never turn CI red."""
        for slug, post in published_posts():
            card = post.get("og_image") or f"/static/images/diagrams/{slug}/og.png"
            html = (OUTPUT / "articles" / slug / "index.html").read_text(encoding="utf-8")
            with self.subTest(slug=slug):
                if post.get("og_image") or (ROOT / card.lstrip("/")).exists():
                    url = card if card.startswith("http") else f"{SITE}{card}"
                    self.assertIn(f'<meta property="og:image"       content="{url}">', html)
                    self.assertIn('<meta name="twitter:card"        content="summary_large_image">', html)
                    self.assertIn(f'<meta name="twitter:image"       content="{url}">', html)
                    if not post.get("og_image"):
                        self.assertIn('<meta property="og:image:width" content="1200">', html)
                        self.assertEqual(png_size(ROOT / card.lstrip("/")), (1200, 630))
                else:
                    self.assertIn(f'<meta property="og:image"       content="{SITE}/static/favicon.png">', html)
                    self.assertIn('<meta name="twitter:card"        content="summary">', html)

    def test_pages_without_a_card_keep_the_site_default(self):
        html = (OUTPUT / "index.html").read_text(encoding="utf-8")
        self.assertIn(f'<meta property="og:image"       content="{SITE}/static/favicon.png">', html)
        self.assertIn('<meta name="twitter:card"        content="summary">', html)


@unittest.skipUnless((OUTPUT / "articles").exists(), "run python build.py first")
class ArticleFigureTests(unittest.TestCase):
    def test_every_embedded_figure_exists_and_loads_its_stylesheet(self):
        for slug, _ in published_posts():
            html = (OUTPUT / "articles" / slug / "index.html").read_text(encoding="utf-8")
            figures = re.findall(r'<figure class="np-figure">.*?<img src="([^"]+)"', html, re.S)
            for src in figures:
                with self.subTest(slug=slug, src=src):
                    self.assertTrue((ROOT / src.lstrip("/")).exists())
            if figures:
                with self.subTest(slug=slug, stylesheet="figures.css"):
                    self.assertIn("/static/css/figures.css", html)

    def test_figures_carry_alt_text(self):
        for slug, _ in published_posts():
            html = (OUTPUT / "articles" / slug / "index.html").read_text(encoding="utf-8")
            for tag in re.findall(r'<figure class="np-figure">.*?(<img [^>]+>)', html, re.S):
                with self.subTest(slug=slug):
                    alt = re.search(r'alt="([^"]*)"', tag)
                    self.assertTrue(alt and len(alt.group(1)) > 40)

    def test_narrow_variants_exist_and_swap_below_the_breakpoint(self):
        for slug, _ in published_posts():
            html = (OUTPUT / "articles" / slug / "index.html").read_text(encoding="utf-8")
            for src in re.findall(r'<source media="\(max-width: 780px\)" srcset="([^"]+)"', html):
                with self.subTest(slug=slug, src=src):
                    self.assertTrue(src.endswith(".narrow.svg"))
                    self.assertTrue((ROOT / src.lstrip("/")).exists())


if __name__ == "__main__":
    unittest.main()
