import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

from build import (
    SiteBuilder,
    estimate_reading_time,
    extract_faqs,
    format_date_iso,
    optimize_content_images,
    slugify,
    sort_key,
)


class BuildHelperTests(unittest.TestCase):
    def test_slugify_normalizes_punctuation_and_spacing(self):
        self.assertEqual(slugify("  LLM Context: A Practical Guide  "), "llm-context-a-practical-guide")

    def test_reading_time_has_one_minute_minimum(self):
        self.assertEqual(estimate_reading_time("short post"), 1)
        self.assertEqual(estimate_reading_time("word " * 400), 2)

    def test_format_date_iso_accepts_dates_and_datetimes(self):
        self.assertEqual(format_date_iso(date(2026, 7, 31)), "2026-07-31")
        self.assertEqual(format_date_iso(datetime(2026, 7, 31, 12, 30)), "2026-07-31")

    def test_sort_key_falls_back_for_invalid_dates(self):
        self.assertEqual(sort_key({"date": "2026-07-31", "slug": "alpha"}), (date(2026, 7, 31), "alpha"))
        self.assertEqual(sort_key({"date": "not-a-date", "slug": "zeta"}), (date.min, "zeta"))

    def test_sort_key_breaks_same_date_ties_by_slug(self):
        posts = [
            {"date": "2026-07-31", "slug": "zeta"},
            {"date": "2026-07-31", "slug": "alpha"},
        ]
        self.assertEqual([post["slug"] for post in sorted(posts, key=sort_key, reverse=True)], ["zeta", "alpha"])

    def test_extract_faqs_supports_heading_and_bold_questions(self):
        markdown = """## FAQ

### What is llms.txt?

It is a plain-text discovery file.

**Who is it for?**

People and AI systems reading a site.

## Next section

Ignored.
"""
        self.assertEqual(
            extract_faqs(markdown),
            [
                {"question": "What is llms.txt?", "answer": "It is a plain-text discovery file."},
                {"question": "Who is it for?", "answer": "People and AI systems reading a site."},
            ],
        )

    def test_content_images_get_lazy_loading_and_intrinsic_dimensions(self):
        rendered = optimize_content_images(
            '<p><img src="/static/favicon.png?v=1" alt="Ninad Pathak"></p>'
        )

        self.assertIn('loading="lazy"', rendered)
        self.assertIn('decoding="async"', rendered)
        self.assertIn('width="512"', rendered)
        self.assertIn('height="512"', rendered)

    def test_content_image_optimization_preserves_explicit_loading(self):
        rendered = optimize_content_images(
            '<img src="/static/favicon.png" alt="Ninad Pathak" loading="eager">'
        )

        self.assertEqual(rendered.count("loading="), 1)


class SitemapTests(unittest.TestCase):
    def test_static_tool_page_does_not_get_build_date_as_lastmod(self):
        builder = SiteBuilder.__new__(SiteBuilder)
        builder.config = {"site": {"url": "https://example.com"}}

        with tempfile.TemporaryDirectory() as directory:
            builder.output = Path(directory)
            builder.build_sitemap([], [], [])
            root = ET.parse(builder.output / "sitemap.xml").getroot()
            namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            entries = {
                node.find("s:loc", namespace).text: node.find("s:lastmod", namespace)
                for node in root.findall("s:url", namespace)
            }

        self.assertIn("https://example.com/llms-txt-generator/", entries)
        self.assertIsNone(entries["https://example.com/llms-txt-generator/"])


class DesignSystemTests(unittest.TestCase):
    css_files = (
        Path("static/css/main.css"),
        Path("static/css/linter.css"),
        Path("static/css/visuals.css"),
        Path("static/css/flowcharts.css"),
    )

    def test_handwritten_css_uses_color_tokens(self):
        raw_color = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(")

        for css_file in self.css_files:
            for line_number, line in enumerate(css_file.read_text().splitlines(), 1):
                if line.lstrip().startswith("--"):
                    continue
                with self.subTest(file=css_file, line=line_number):
                    self.assertIsNone(raw_color.search(line))

    def test_fixed_type_sizes_use_tokens(self):
        fixed_size = re.compile(r"\d+(?:\.\d+)?(?:rem|em|px)\b")

        for css_file in self.css_files:
            for line_number, line in enumerate(css_file.read_text().splitlines(), 1):
                if line.lstrip().startswith("--font"):
                    continue
                declarations = re.findall(r"\b(?:font-size|font):\s*([^;]+)", line)
                for declaration in declarations:
                    if "clamp(" in declaration:
                        continue
                    with self.subTest(file=css_file, line=line_number):
                        self.assertIsNone(fixed_size.search(declaration))

    def test_article_visual_styles_stay_out_of_global_css(self):
        global_css = Path("static/css/main.css").read_text()
        self.assertNotIn(".visual-wrapper", global_css)
        self.assertNotIn(".flowchart {", global_css)

    def test_latest_article_uses_responsive_svg_flowchart_instead_of_raster(self):
        article = Path("content/posts/internal-vs-external-documentation.md").read_text()
        self.assertIn('class="flowchart-image"', article)
        self.assertIn("documentation-placement-flowchart-mobile.svg", article)
        self.assertIn("documentation-placement-flowchart.svg", article)
        self.assertNotIn(".png", article)
        self.assertNotIn("documentation-placement-decision-tree", article)

    def test_flowchart_svgs_include_dark_theme_and_accessible_titles(self):
        directory = Path("static/images/articles/internal-vs-external-documentation")
        for filename in (
            "documentation-placement-flowchart.svg",
            "documentation-placement-flowchart-mobile.svg",
        ):
            svg = (directory / filename).read_text()
            with self.subTest(file=filename):
                self.assertIn("prefers-color-scheme:dark", svg)
                self.assertIn("<title", svg)
                self.assertIn("<desc", svg)
                self.assertIn("role=\"img\"", svg)


if __name__ == "__main__":
    unittest.main()
