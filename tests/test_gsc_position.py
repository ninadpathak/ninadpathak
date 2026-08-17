"""Deterministic tests for the position analysis.

Three things are pinned because each would turn a non-result into a finding:

  * Position must be compared per (page, query) pair. A page's average position moves when
    its query mix moves, and that confound has already produced two false readings here.
  * Intervention must stay three-valued. A legacy URL has no source file, so nothing can be
    checked; collapsing "unknowable" into "no" would claim 82 of 84 movers improved without
    intervention.
  * Clicks on the injected `/products/` spam pages are real people but not readers of this
    site. Nine of the twenty human clicks in the record land there, so leaving them in
    materially overstates the baseline.

Every line in the limits section must state a number. Two drafts failed that: one described
the click sample in words, and one called the pull's coverage "roughly a fifth" when it is
measurable and is in fact about half.
"""

from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import gsc_position as gp  # noqa: E402

BASE = "https://ninadpathak.com"


def row(page: str, query: str, date: str, position: float,
        impressions: float = 10, clicks: float = 0) -> dict:
    return {"keys": [query], "page": BASE + page, "date": date, "position": position,
            "impressions": impressions, "clicks": clicks}


class TestSlugExtraction(unittest.TestCase):
    def test_both_path_prefixes_resolve_to_a_slug(self):
        self.assertEqual(gp.slug_of(BASE + "/articles/a-post/"), "a-post")
        self.assertEqual(gp.slug_of(BASE + "/blog/a-post/"), "a-post")

    def test_non_post_urls_have_no_slug(self):
        for p in ("/", "/about/", "/glossary/term/", "/products/12201711", "/linter/"):
            self.assertIsNone(gp.slug_of(BASE + p), p)


class TestSpamPagesAreExcluded(unittest.TestCase):
    """The query separator passes these because the searchers were real people."""

    def test_injected_product_pages_are_foreign(self):
        for p in ("/products/12201711", "/shop/", "/cart/", "/jukyuban/"):
            self.assertTrue(gp.fx.is_foreign(BASE + p), p)

    def test_the_sites_own_pages_are_not_foreign(self):
        for p in ("/articles/a-post/", "/blog/a-post/", "/glossary/term/", "/linter/"):
            self.assertFalse(gp.fx.is_foreign(BASE + p), p)


class TestTrajectoryIsPerPair(unittest.TestCase):
    POSTS = {"a-post": {"cluster": "ai-engineering", "words": 1500,
                        "shipped": dt.date(2026, 4, 1), "inbound": 3}}

    def test_a_pair_improving_reports_a_positive_delta(self):
        rows = [row("/blog/a-post/", "q1", "2026-05-01", 40.0),
                row("/blog/a-post/", "q1", "2026-06-15", 10.0)]
        got = gp.trajectories(rows, self.POSTS)
        self.assertEqual(got["all"]["n"], 1)
        self.assertEqual(got["pairs"][0]["delta"], 30.0)

    def test_a_pair_worsening_reports_a_negative_delta(self):
        rows = [row("/blog/a-post/", "q1", "2026-05-01", 10.0),
                row("/blog/a-post/", "q1", "2026-06-15", 40.0)]
        self.assertEqual(gp.trajectories(rows, self.POSTS)["pairs"][0]["delta"], -30.0)

    def test_a_short_span_is_not_measured(self):
        rows = [row("/blog/a-post/", "q1", "2026-05-01", 40.0),
                row("/blog/a-post/", "q1", "2026-05-05", 10.0)]
        self.assertEqual(gp.trajectories(rows, self.POSTS)["all"]["n"], 0)

    def test_query_mix_alone_does_not_create_a_trend(self):
        """A page gaining a deep second query would move a per-PAGE average and must not
        register as a position change on either pair."""
        rows = [row("/blog/a-post/", "q1", "2026-05-01", 10.0),
                row("/blog/a-post/", "q1", "2026-06-15", 10.0),
                row("/blog/a-post/", "q2", "2026-06-15", 90.0)]
        got = gp.trajectories(rows, self.POSTS)
        self.assertEqual(got["all"]["n"], 1)               # only q1 has a span
        self.assertEqual(got["pairs"][0]["delta"], 0.0)    # and it did not move

    def test_campaign_and_legacy_are_split(self):
        rows = [row("/blog/a-post/", "q1", "2026-05-01", 40.0),
                row("/blog/a-post/", "q1", "2026-06-15", 10.0),
                row("/todoist-vs-any-do/", "q2", "2026-05-01", 40.0),
                row("/todoist-vs-any-do/", "q2", "2026-06-15", 10.0)]
        got = gp.trajectories(rows, self.POSTS)
        self.assertEqual(got["campaign"]["n"], 1)
        self.assertEqual(got["legacy"]["n"], 1)

    def test_deltas_are_impression_weighted_within_a_third(self):
        rows = [row("/blog/a-post/", "q1", "2026-05-01", 10.0, impressions=90),
                row("/blog/a-post/", "q1", "2026-05-02", 100.0, impressions=10),
                row("/blog/a-post/", "q1", "2026-06-15", 20.0, impressions=10)]
        early = gp.trajectories(rows, self.POSTS)["pairs"][0]["early_position"]
        self.assertLess(early, 30)     # weighted toward the 90-impression day, not (10+100)/2


class TestInterventionIsThreeValued(unittest.TestCase):
    def test_a_legacy_pair_is_unknowable_not_no(self):
        pair = {"campaign": False, "slug": None, "first_seen": "2026-05-01"}
        self.assertIsNone(gp.intervened(pair))

    def test_an_unknown_slug_is_unknowable(self):
        pair = {"campaign": True, "slug": "no-such-post-anywhere",
                "first_seen": "2026-05-01"}
        self.assertIsNone(gp.intervened(pair))

    def test_unknowable_is_distinct_from_false(self):
        """The distinction is the whole point: 82 of 84 movers are unknowable."""
        self.assertIsNot(gp.intervened({"campaign": False, "slug": None,
                                        "first_seen": "2026-05-01"}), False)


class TestThresholds(unittest.TestCase):
    def test_material_move_is_bigger_than_daily_position_noise(self):
        self.assertGreaterEqual(gp.MATERIAL_MOVE, 3)

    def test_top_and_deep_bands_do_not_overlap(self):
        self.assertLess(gp.TOP_BAND, gp.DEEP_BAND)

    def test_min_span_is_at_least_three_weeks(self):
        self.assertGreaterEqual(gp.MIN_SPAN_DAYS, 21)

    def test_underpowered_threshold_exists(self):
        self.assertGreaterEqual(gp.UNDERPOWERED, 20)


class TestTrajectoryVerdict(unittest.TestCase):
    def cohort(self, n, median=0.0, improved=0, worsened=0, flat=0):
        return {"n": n, "median_delta": median, "mean_delta": median,
                "improved": improved, "worsened": worsened, "flat": flat}

    def test_a_tiny_campaign_sample_refuses_to_answer(self):
        t = {"campaign": self.cohort(2, -2.8, 1, 1, 0),
             "legacy": self.cohort(245, 1.0, 79, 57, 109),
             "all": self.cohort(247, 1.0)}
        s = gp.trajectory_verdict(t)
        self.assertIn("cannot answer this: n=2", s)
        self.assertIn("site that no longer exists", s)

    def test_a_flat_legacy_median_is_called_a_random_walk_not_a_climb(self):
        t = {"campaign": self.cohort(2), "legacy": self.cohort(245, 1.0, 79, 57, 109),
             "all": self.cohort(247, 1.0)}
        s = gp.trajectory_verdict(t)
        self.assertIn("random walk", s)
        self.assertIn("land near where they will stay", s)

    def test_neither_cohort_large_enough_says_nothing_supported(self):
        t = {"campaign": self.cohort(2), "legacy": self.cohort(5), "all": self.cohort(7)}
        self.assertIn("Not answerable at this sample", gp.trajectory_verdict(t))


class TestLimitsAlwaysStateTheSample(unittest.TestCase):
    def frame(self, clicks=0):
        return {
            "features": {"top20": {"n": 14}, "deep": {"n": 18},
                         "posts_total": 90, "posts_with_human_impression": 33,
                         "posts_with_human_click": clicks},
            "trajectory": {"campaign": {"n": 2}, "legacy": {"n": 245}},
            "movers": {"unattributable": 82},
            "excluded": {"joined_impressions": 17120, "sitewide_impressions": 33549,
                         "coverage_pct": 51.0},
        }

    def test_every_limit_line_names_a_number(self):
        for line in gp.limits(self.frame()):
            self.assertTrue(any(ch.isdigit() for ch in line), line)

    def test_an_empty_click_sample_is_called_empty_not_small(self):
        out = " ".join(gp.limits(self.frame(clicks=0)))
        self.assertIn("not a small sample, an empty one", out)

    def test_a_nonzero_click_sample_drops_that_line(self):
        out = " ".join(gp.limits(self.frame(clicks=3)))
        self.assertNotIn("an empty one", out)


class TestDatedReportIsIdempotent(unittest.TestCase):
    def test_same_date_is_replaced_not_appended(self):
        existing = (
            "# Position analysis\n\n"
            "## 2026-08-10 — what moves position\nold week\n\n"
            "## 2026-08-17 — what moves position\nstale run\n"
        )
        report = "\n## 2026-08-17 — what moves position\nfresh run\n"

        got = gp.upsert_dated_report(existing, report, "2026-08-17")

        self.assertEqual(got.count("## 2026-08-17 — what moves position"), 1)
        self.assertIn("fresh run", got)
        self.assertNotIn("stale run", got)
        self.assertIn("old week", got)

    def test_preexisting_same_date_duplicates_collapse_to_one(self):
        existing = (
            "# Position analysis\n\n"
            "## 2026-08-17 — what moves position\nfirst\n\n"
            "## 2026-08-17 — what moves position\nsecond\n"
        )
        report = "## 2026-08-17 — what moves position\nauthoritative\n"

        got = gp.upsert_dated_report(existing, report, "2026-08-17")

        self.assertEqual(got.count("## 2026-08-17 — what moves position"), 1)
        self.assertIn("authoritative", got)
        self.assertNotIn("first", got)
        self.assertNotIn("second", got)

    def test_a_new_date_appends_without_touching_nested_headings(self):
        existing = (
            "# Position analysis\n\n"
            "## 2026-08-10 — what moves position\n"
            "### Where the sample is too small\nlimits\n"
        )
        report = "## 2026-08-17 — what moves position\nnew week\n"

        got = gp.upsert_dated_report(existing, report, "2026-08-17")

        self.assertIn("### Where the sample is too small\nlimits", got)
        self.assertEqual(got.count("— what moves position"), 2)


if __name__ == "__main__":
    unittest.main()
