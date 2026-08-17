"""Deterministic tests for the weekly scoreboard logic.

The scoreboard's job is to be un-misreadable, so most of these tests are about what it
refuses to do: quote a multiple of zero, quote a percentage change from zero, present an
average position over two disjoint query sets as movement, or let a cluster's zero be read
as failure when nothing has shipped there.

The zero cases are not edge cases here. Human non-brand clicks have been zero for ten
months, so the zero path is the normal path and it has to read correctly.
"""

from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import gsc_scoreboard as sb  # noqa: E402


def q(query: str, impressions: int, clicks: int = 0, position: float = 10.0) -> dict:
    return {"query": query, "impressions": impressions, "clicks": clicks,
            "position": position}


class TestWindows(unittest.TestCase):
    def test_windows_end_at_the_lag_and_do_not_overlap(self):
        w = sb.week_windows(dt.date(2026, 8, 17))
        self.assertEqual(w["this_week"], ("2026-08-08", "2026-08-14"))
        self.assertEqual(w["last_week"], ("2026-08-01", "2026-08-07"))

    def test_weeks_are_seven_days(self):
        w = sb.week_windows(dt.date(2026, 8, 17))
        for key in ("this_week", "last_week"):
            a, b = (dt.date.fromisoformat(x) for x in w[key])
            self.assertEqual((b - a).days + 1, sb.WEEK)

    def test_month_windows_are_28_days_and_adjacent(self):
        w = sb.week_windows(dt.date(2026, 8, 17))
        ts, te = (dt.date.fromisoformat(x) for x in w["trailing_28"])
        ps, pe = (dt.date.fromisoformat(x) for x in w["prior_28"])
        self.assertEqual((te - ts).days + 1, sb.DAYS_IN_MONTH)
        self.assertEqual((pe - ps).days + 1, sb.DAYS_IN_MONTH)
        self.assertEqual((ts - pe).days, 1)

    def test_this_week_ends_where_the_trailing_month_ends(self):
        w = sb.week_windows(dt.date(2026, 8, 17))
        self.assertEqual(w["this_week"][1], w["trailing_28"][1])


class TestVerdictAtZero(unittest.TestCase):
    """Zero is the normal state on this site, so it must read as a standing start."""

    def test_no_multiple_is_invented_from_zero(self):
        v = sb.verdict({}, {"clicks": 0}, dt.date(2026, 8, 17))
        self.assertIsNone(v["multiple_to_target"])
        self.assertFalse(v["reaches_target"])
        self.assertFalse(v["reaches_band_floor"])

    def test_zero_verdict_says_no_without_hedging(self):
        s = sb.verdict({}, {"clicks": 0}, dt.date(2026, 8, 17))["sentence"]
        self.assertTrue(s.startswith("No."))
        for hedge in ("could", "might", "may ", "possibly", "hopefully", "on track"):
            self.assertNotIn(hedge, s.lower())

    def test_zero_verdict_names_the_band_ceiling_gap(self):
        # Derived from the constants, not pinned: the band gets re-derived and a literal
        # here would break on every restatement while testing nothing extra.
        s = sb.verdict({}, {"clicks": 0}, dt.date(2026, 8, 17))["sentence"]
        expected = f"{sb.TARGET_MONTHLY / sb.BAND_HIGH:.1f}x"
        self.assertIn(expected, s)
        self.assertIn(str(sb.BAND_LOW), s)

    def test_days_remaining_are_counted_to_day_90(self):
        v = sb.verdict({}, {"clicks": 0}, dt.date(2026, 8, 17))
        self.assertEqual(v["days_to_day_90"], (sb.DAY_90 - dt.date(2026, 8, 17)).days)


class TestVerdictAboveZero(unittest.TestCase):
    def test_a_real_rate_produces_a_multiple(self):
        v = sb.verdict({}, {"clicks": 500}, dt.date(2026, 8, 17))
        self.assertEqual(v["multiple_to_target"], 20.0)
        self.assertTrue(v["reaches_band_floor"])
        self.assertFalse(v["reaches_target"])
        self.assertTrue(v["sentence"].startswith("No."))

    def test_hitting_the_target_says_yes(self):
        v = sb.verdict({}, {"clicks": 10_000}, dt.date(2026, 8, 17))
        self.assertTrue(v["reaches_target"])
        self.assertTrue(v["sentence"].startswith("Yes."))

    def test_below_the_band_floor_is_reported_as_below(self):
        v = sb.verdict({}, {"clicks": 100}, dt.date(2026, 8, 17))
        self.assertFalse(v["reaches_band_floor"])
        self.assertIn("below", v["sentence"])


class TestTopMovement(unittest.TestCase):
    THIS = [q("code documentation template", 19), q("technical tutorial", 3), q("ans", 1)]
    LAST = [q("seo documentation", 5), q("technical tutorial", 3), q("stripe tech blog", 1)]

    def test_entered_and_left_are_computed_against_the_other_week(self):
        m = sb.top_movement(self.THIS, self.LAST)
        self.assertEqual([x["query"] for x in m["entered"]],
                         ["code documentation template", "ans"])
        self.assertEqual([x["query"] for x in m["left"]],
                         ["seo documentation", "stripe tech blog"])
        self.assertEqual([x["query"] for x in m["held"]], ["technical tutorial"])

    def test_movement_carries_impressions_so_churn_can_be_weighed(self):
        m = sb.top_movement(self.THIS, self.LAST)
        self.assertEqual(m["entered_impressions"], 20)
        self.assertEqual(m["left_impressions"], 6)

    def test_a_short_list_is_not_called_a_ranking(self):
        self.assertFalse(sb.top_movement(self.THIS, self.LAST)["is_a_ranking"])

    def test_a_full_list_is_a_ranking(self):
        big = [q(f"query {i}", 50) for i in range(sb.TOP_N + 5)]
        self.assertTrue(sb.top_movement(big, big)["is_a_ranking"])

    def test_only_the_top_n_are_considered(self):
        big = [q(f"a{i}", 100 - i) for i in range(sb.TOP_N + 3)]
        m = sb.top_movement(big, [])
        self.assertEqual(len(m["entered"]), sb.TOP_N)

    def test_single_impression_share_flags_noise(self):
        noisy = [q("x", 1), q("y", 1), q("z", 1)]
        self.assertEqual(sb.top_movement(noisy, noisy)["single_impression_share"], 1.0)
        solid = [q("x", 40), q("y", 30)]
        self.assertEqual(sb.top_movement(solid, solid)["single_impression_share"], 0.0)

    def test_two_empty_weeks_do_not_divide_by_zero(self):
        m = sb.top_movement([], [])
        self.assertIsNone(m["single_impression_share"])
        self.assertEqual((m["entered"], m["left"], m["held"]), ([], [], []))


class TestBandConstantsMatchTheCampaignDoc(unittest.TestCase):
    """The band has been restated three times as premises under it changed.

    A scoreboard measuring against a stale band is worse than one measuring against none,
    so the live figures are pinned here and `tools/gsc_band.py` is the derivation.
    """

    def test_band_is_the_re_derived_band(self):
        self.assertEqual((sb.BAND_LOW, sb.BAND_HIGH), (149, 1525))
        self.assertEqual(sb.BAND_CENTRAL, 413)

    def test_the_central_sits_inside_the_band(self):
        self.assertLess(sb.BAND_LOW, sb.BAND_CENTRAL)
        self.assertLess(sb.BAND_CENTRAL, sb.BAND_HIGH)

    def test_the_re_derivation_date_is_recorded(self):
        """A reader must be able to tell which premise a band figure belongs to."""
        self.assertEqual(sb.BAND_REDERIVED, "2026-08-17")

    def test_target_and_day_90(self):
        self.assertEqual(sb.TARGET_MONTHLY, 10_000)
        self.assertEqual(sb.DAY_90, dt.date(2026, 11, 15))

    def test_the_band_ceiling_is_short_of_the_target(self):
        """If this ever stops being true the verdict wording needs revisiting."""
        self.assertLess(sb.BAND_HIGH, sb.TARGET_MONTHLY)


class TestLivePagesPerCluster(unittest.TestCase):
    def test_every_cluster_appears(self):
        live = sb.live_pages_per_cluster()
        for _, slug, _ in sb.gr.CLUSTERS:
            self.assertIn(slug, live)

    def test_tools_count_toward_their_cluster(self):
        """The five shipped tools all belong to cluster 4, so it can never be zero."""
        live = sb.live_pages_per_cluster()
        self.assertGreaterEqual(live["ai-search-optimization"],
                                len(set(sb.gr.TOOL_PATHS)))


if __name__ == "__main__":
    unittest.main()
