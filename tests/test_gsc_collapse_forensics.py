"""Deterministic tests for the collapse-forensics logic.

The foreign-URL detector is the part that settled the September 2025 question, and it is
also the part most able to mislead: it is an allowlist, so anything it does not recognise
reads as an injection. Four legitimate old-site sections were false positives during the
original analysis - /category/, /tags/, /productivity/ and /project/ - and each cost real
accuracy before being caught. They are pinned here so they cannot regress.

The step detector is pinned against the real 2025 numbers, where ranking by proportion
picked 56 -> 10 (82%) while the actual event was 791 -> 260. Both are reported now, and
the tests assert they can disagree.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import gsc_collapse_forensics as f  # noqa: E402

BASE = "https://ninadpathak.com"

# The real injected paths, from Search Console, September-October 2025.
INJECTED = ["/products/12201711", "/products/15408300", "/shop/", "/cart/",
            "/jukyuban/", "/hg/", "/pw/", "/contents/", "/home/", "/item/x/"]

# Legitimate paths across every incarnation of the site.
LEGIT = ["/", "/about/", "/blog/how-memory-works-in-deerflow/",
         "/articles/the-taxonomy-of-ai-agents/", "/glossary/late-chunking/",
         "/work/kiwisizing/", "/portfolio/", "/guides/css-grid-layouts-webflow-table/",
         "/marketing-research/stripe-documentation-case-study/",
         "/essays/notion-api-documentation-case-study/", "/customers/delightchat/",
         "/linter/", "/topics/", "/terms/", "/static/css/main.css",
         # the four that were wrongly flagged first time round
         "/category/blog/", "/tags/notion/", "/productivity/ticktick/",
         "/project/augue-lacus-viverra/",
         # root-level posts from the old site
         "/todoist-vs-any-do/", "/wordpress-6-7-rollins/", "/ticktick-vs-any-do/"]


class TestSection(unittest.TestCase):
    def test_root_is_named_not_empty(self):
        self.assertEqual(f.section(BASE + "/"), "(root)")

    def test_first_segment_wins(self):
        self.assertEqual(f.section(BASE + "/products/12201711"), "products")


class TestPostSlug(unittest.TestCase):
    def test_hyphenated_single_segment_is_a_post(self):
        self.assertTrue(f.is_post_slug(BASE + "/todoist-vs-any-do/"))
        self.assertTrue(f.is_post_slug(BASE + "/wordpress-6-7-rollins/"))

    def test_bare_word_is_not_a_post(self):
        for p in ("/hg/", "/pw/", "/jukyuban/", "/shop/"):
            self.assertFalse(f.is_post_slug(BASE + p), p)

    def test_nested_path_is_not_a_root_post(self):
        self.assertFalse(f.is_post_slug(BASE + "/products/12201711"))

    def test_purely_numeric_segment_is_not_a_post(self):
        self.assertFalse(f.is_post_slug(BASE + "/12201711/"))


class TestForeignDetection(unittest.TestCase):
    def test_every_injected_path_is_flagged(self):
        for p in INJECTED:
            self.assertTrue(f.is_foreign(BASE + p), f"missed injection: {p}")

    def test_no_legitimate_path_is_flagged(self):
        for p in LEGIT:
            self.assertFalse(f.is_foreign(BASE + p), f"false positive: {p}")

    def test_the_four_original_false_positives_stay_fixed(self):
        """Regression guard: these cost accuracy in the first pass of the analysis."""
        for p in ("/category/blog/", "/tags/notion/", "/productivity/ticktick/",
                  "/project/augue-lacus-viverra/"):
            self.assertFalse(f.is_foreign(BASE + p), p)

    def test_products_and_productivity_are_not_confused(self):
        self.assertTrue(f.is_foreign(BASE + "/products/12201711"))
        self.assertFalse(f.is_foreign(BASE + "/productivity/ticktick/"))

    def test_an_unknown_section_reads_as_foreign_by_design(self):
        """The allowlist exists to catch the next injection, whose paths are unknown."""
        self.assertTrue(f.is_foreign(BASE + "/some-new-spam-section/deep/"))


class TestLargestStep(unittest.TestCase):
    # The real 2025 weekly series, legitimate impressions only.
    SERIES = [{"week": w, "legit_impressions": v} for w, v in [
        ("2025-08-04", 1055), ("2025-08-11", 911), ("2025-08-18", 863),
        ("2025-08-25", 718), ("2025-09-01", 791), ("2025-09-08", 260),
        ("2025-09-15", 56), ("2025-09-22", 10), ("2025-09-29", 11)]]

    def test_absolute_loss_finds_the_actual_event(self):
        step = f.largest_step(self.SERIES)["by_absolute_loss"]
        self.assertEqual((step["from_week"], step["before"], step["after"]),
                         ("2025-09-01", 791, 260))

    def test_proportion_picks_a_different_and_less_useful_week(self):
        step = f.largest_step(self.SERIES)["by_proportion"]
        self.assertEqual(step["from_week"], "2025-09-15")
        self.assertEqual((step["before"], step["after"]), (56, 10))

    def test_the_two_measures_disagree_here(self):
        s = f.largest_step(self.SERIES)
        self.assertNotEqual(s["by_absolute_loss"]["from_week"],
                            s["by_proportion"]["from_week"])

    def test_tiny_weeks_are_excluded_from_the_proportional_measure(self):
        """A fall from 8 to 0 is 100% and means nothing."""
        series = [{"week": "a", "legit_impressions": 8},
                  {"week": "b", "legit_impressions": 0},
                  {"week": "c", "legit_impressions": 400},
                  {"week": "d", "legit_impressions": 100}]
        self.assertEqual(f.largest_step(series)["by_proportion"]["from_week"], "c")

    def test_a_rising_series_reports_no_fall(self):
        series = [{"week": "a", "legit_impressions": 10},
                  {"week": "b", "legit_impressions": 20}]
        got = f.largest_step(series)
        self.assertIsNone(got["by_absolute_loss"])
        self.assertIsNone(got["by_proportion"])

    def test_a_flat_series_reports_no_fall(self):
        series = [{"week": "a", "legit_impressions": 50},
                  {"week": "b", "legit_impressions": 50}]
        self.assertIsNone(f.largest_step(series)["by_absolute_loss"])


if __name__ == "__main__":
    unittest.main()
