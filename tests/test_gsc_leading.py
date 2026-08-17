"""Deterministic tests for the leading-indicator logic.

The defect this suite exists to prevent is the one the tool was almost built around:
grouping time-to-first-impression by cluster across ship eras reported documentation at 9
days against AI-engineering at 65, a seven-fold effect that does not exist. The clusters
shipped at different times and the domain's indexing speed changed underneath them. Within
the one shared era they land within ten days of each other.

Also pinned: a page that earned nothing before a rewrite cannot demonstrate that the
rewrite moved anything, so zero-to-zero must not read as a null result about revision.
"""

from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import gsc_leading as ld  # noqa: E402


class TestQuarter(unittest.TestCase):
    def test_quarters_are_derived_from_the_month(self):
        cases = {dt.date(2026, 1, 5): "2026-Q1", dt.date(2026, 3, 31): "2026-Q1",
                 dt.date(2026, 4, 1): "2026-Q2", dt.date(2026, 6, 30): "2026-Q2",
                 dt.date(2026, 8, 17): "2026-Q3", dt.date(2026, 12, 1): "2026-Q4"}
        for d, q in cases.items():
            self.assertEqual(ld.quarter(d), q)


class TestMergedSeries(unittest.TestCase):
    """A post's history spans both path prefixes; reading one loses most of it."""

    DAILY = {
        "https://ninadpathak.com/articles/a-post/": {"2026-08-01": 5},
        "https://ninadpathak.com/blog/a-post/": {"2026-08-01": 20, "2026-08-02": 7},
    }

    def test_both_prefixes_are_summed(self):
        got = ld.merged_series(self.DAILY, "a-post")
        self.assertEqual(got, {"2026-08-01": 25, "2026-08-02": 7})

    def test_an_unknown_slug_is_empty_not_an_error(self):
        self.assertEqual(ld.merged_series(self.DAILY, "nope"), {})


class TestEraConfoundIsTheHeadline(unittest.TestCase):
    """The regression guard for a seven-fold cluster effect that is a ship-date artifact."""

    def test_cross_era_cluster_grouping_would_invert_the_answer(self):
        # Documentation shipped late into a fast-indexing domain; AI shipped early into a
        # slow one. Grouped by cluster the fast one looks better; grouped by era it is the
        # era that differs, and within an era they are close.
        import statistics as st
        docs_q3 = [4, 3, 8]                 # documentation, shipped 2026-Q3
        ai_q2 = [62, 60, 64]                # AI-engineering, shipped 2026-Q2
        docs_q2 = [72, 70, 74]              # documentation, shipped 2026-Q2

        # Pooling documentation across eras is what produces the artifact: it drags the
        # documentation median down toward its 2026-Q3 pages and makes the cluster look fast.
        docs_pooled = docs_q3 + docs_q2
        pooled_advantage = st.median(ai_q2) - st.median(docs_pooled)
        within_era_gap = abs(st.median(docs_q2) - st.median(ai_q2))

        # Pooled, documentation appears materially faster than AI-engineering.
        self.assertGreater(pooled_advantage, 15)
        # Within a shared era that advantage disappears — documentation is in fact slower.
        self.assertLess(within_era_gap, 15)
        self.assertGreater(st.median(docs_q2), st.median(ai_q2))
        # And the era series is the thing that actually moves.
        self.assertLess(st.median(docs_q3), st.median(docs_q2) / 5)

    def test_comparable_eras_needs_more_than_one_cluster(self):
        """An era holding one cluster supports no cluster comparison at all."""
        within = {"2026-Q1": {"ai-engineering": {"n": 12}},
                  "2026-Q2": {"ai-engineering": {"n": 40}, "technical-documentation": {"n": 5}}}
        comparable = [q for q, v in within.items() if len(v) > 1]
        self.assertEqual(comparable, ["2026-Q2"])


class TestEarnRateFloor(unittest.TestCase):
    def test_the_age_floor_exists_and_is_at_least_two_weeks(self):
        """Counting pages younger than the floor as failures invented a survivorship story."""
        self.assertGreaterEqual(ld.MIN_AGE_FOR_EARN_RATE, 14)


class TestRecoveryWatchlistThresholds(unittest.TestCase):
    def test_silence_threshold_is_longer_than_the_gsc_lag(self):
        """A page silent for three days is not recovering, it is just recent."""
        self.assertGreater(ld.SILENCE_DAYS, ld.gr.GSC_LAG_DAYS * 3)

    def test_revision_compare_window_is_at_least_a_week(self):
        self.assertGreaterEqual(ld.REVISION_COMPARE, 7)


class TestRevisionInformativeness(unittest.TestCase):
    """Zero-to-zero is a page with no signal, not evidence that rewriting does nothing."""

    def classify(self, observable: int, before: int) -> dict:
        return {"observable": observable >= 1, "informative": observable >= 1 and before > 0}

    def test_a_page_inside_the_lag_is_not_observable(self):
        got = self.classify(-3, 40)
        self.assertFalse(got["observable"])
        self.assertFalse(got["informative"])

    def test_an_observable_page_with_no_prior_impressions_is_not_informative(self):
        got = self.classify(4, 0)
        self.assertTrue(got["observable"])
        self.assertFalse(got["informative"])

    def test_an_observable_page_that_was_earning_is_informative(self):
        got = self.classify(4, 40)
        self.assertTrue(got["informative"])


class TestCannotAnswer(unittest.TestCase):
    def frame(self, readable=0, observable=0, count=76, silent=None, comparable=None):
        return {
            "first_impression": {"comparable_eras": comparable or []},
            "recovery": {"silent": silent if silent is not None else []},
            "revision": {"readable": readable, "observable": observable, "count": count,
                         "days_until_readable": 1},
        }

    def test_clicks_are_always_named_as_unanswerable(self):
        out = ld.cannot_answer(self.frame())
        self.assertTrue(any("clicks" in x.lower() for x in out))

    def test_revision_is_unanswerable_when_nothing_is_informative(self):
        out = ld.cannot_answer(self.frame(readable=0, observable=3))
        self.assertTrue(any("revision" in x.lower() for x in out))

    def test_the_reason_distinguishes_lag_from_no_prior_signal(self):
        inside_lag = " ".join(ld.cannot_answer(self.frame(readable=0, observable=0)))
        no_signal = " ".join(ld.cannot_answer(self.frame(readable=0, observable=3)))
        self.assertIn("inside the Search Console lag", inside_lag)
        self.assertIn("earned nothing beforehand", no_signal)

    def test_recovery_wording_depends_on_whether_the_watchlist_is_populated(self):
        empty = " ".join(ld.cannot_answer(self.frame(silent=[])))
        full = " ".join(ld.cannot_answer(self.frame(silent=[{"path": "/glossary/x/"}])))
        self.assertIn("nothing we serve is currently silent", empty)
        self.assertIn("watchlist is populated", full)

    def test_no_era_comparison_is_reported_when_none_is_possible(self):
        out = " ".join(ld.cannot_answer(self.frame(comparable=[])))
        self.assertIn("no era holds two clusters yet", out)


if __name__ == "__main__":
    unittest.main()
