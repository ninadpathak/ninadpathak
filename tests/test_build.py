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


if __name__ == "__main__":
    unittest.main()
