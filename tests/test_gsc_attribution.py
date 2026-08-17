"""Deterministic tests for the attribution logic.

Two defects the first draft shipped with are pinned here, because both produced numbers
that looked like findings:

  * A voice sweep rewrote sixty long-lived articles in one commit, and treating a rewrite
    as a publish gave a median days-to-first-impression of **-15** and the line "41 of 1
    observable articles reached an impression". A page shipped before tracking began is
    pre-existing however heavily it was just edited.
  * The aged comparison called 65d against 67d "tools reached a first impression faster",
    on a sample of one tool. Medians within INDISTINGUISHABLE_DAYS are one figure.

The three-state reporting is also pinned. A missing measurement must never render as a
zero, because a zero reads as "it happened on day zero". Pagination, exact withholding
bounds, and one authoritative same-day report are pinned too: truncation or duplicate
sections would turn one incomplete observation into a confident-looking trend.
"""

from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import gsc_attribution as at  # noqa: E402


def series(pairs: dict[str, tuple[float, float]]) -> dict[str, dict]:
    """{date: (impressions, clicks)} -> the shape the module consumes."""
    return {d: {"impressions": i, "clicks": c, "position": 10.0}
            for d, (i, c) in pairs.items()}


class FakeSearchAnalytics:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []
        self.body = None

    def query(self, siteUrl, body):
        self.calls.append(body["startRow"])
        self.body = body
        return self

    def execute(self):
        start = self.body["startRow"]
        return {"rows": self.pages.get(start, [])}


class FakeService:
    def __init__(self, pages):
        self.api = FakeSearchAnalytics(pages)

    def searchanalytics(self):
        return self.api


class TestCompletePull(unittest.TestCase):
    def test_fetch_rows_paginates_past_the_api_row_limit(self):
        svc = FakeService({
            0: [{"keys": ["a"]}, {"keys": ["b"]}],
            2: [{"keys": ["c"]}],
        })
        got = at.fetch_rows(svc, {"dimensions": ["page"]}, row_limit=2)
        self.assertEqual([row["keys"][0] for row in got], ["a", "b", "c"])
        self.assertEqual(svc.api.calls, [0, 2])


class TestWithholdingBounds(unittest.TestCase):
    def test_build_exposes_exact_floor_ceiling_and_coverage(self):
        url = "https://ninadpathak.com/test-tool/"
        pages = [{
            "kind": "tool", "url": url, "slug": "test-tool",
            "cluster": "ai-search-optimization", "shipped": "2026-08-01",
            "rewritten": None, "basis": "new", "title": "/test-tool/",
        }]
        page_daily = {url: {
            "2026-08-05": {"clicks": 0, "impressions": 10, "position": 12.0}
        }}
        query_daily = {
            "named": {url: {
                "2026-08-05": {"clicks": 0, "impressions": 4}
            }},
            "human": {url: {
                "2026-08-05": {"clicks": 0, "impressions": 2}
            }},
        }
        with mock.patch.object(at, "tracked_pages", return_value=pages), \
             mock.patch.object(at, "daily_by_page", return_value=page_daily), \
             mock.patch.object(at, "daily_queries_by_page", return_value=query_daily):
            data = at.build(None, dt.date(2026, 8, 1), dt.date(2026, 8, 10))

        page = data["pages"][0]
        self.assertEqual(page["named_query_impressions"], 4)
        self.assertEqual(page["human_impressions"], 2)
        self.assertEqual(page["withheld_impressions"], 6)
        self.assertEqual(page["human_impressions_upper"], 8)
        self.assertEqual(page["query_coverage_pct"], 40.0)
        self.assertEqual(data["coverage"], {
            "page_impressions": 10,
            "named_query_impressions": 4,
            "pct": 40.0,
            "human_floor": 2,
            "human_upper": 8,
            "withheld_impressions": 6,
        })

    def test_render_calls_the_ceiling_an_error_bound_not_an_estimate(self):
        url = "https://ninadpathak.com/test-tool/"
        pages = [{
            "kind": "tool", "url": url, "slug": "test-tool",
            "cluster": "ai-search-optimization", "shipped": "2026-08-01",
            "rewritten": None, "basis": "new", "title": "/test-tool/",
        }]
        page_daily = {url: {
            "2026-08-05": {"clicks": 0, "impressions": 10, "position": 12.0}
        }}
        query_daily = {
            "named": {url: {"2026-08-05": {"clicks": 0, "impressions": 4}}},
            "human": {url: {"2026-08-05": {"clicks": 0, "impressions": 2}}},
        }
        with mock.patch.object(at, "tracked_pages", return_value=pages), \
             mock.patch.object(at, "daily_by_page", return_value=page_daily), \
             mock.patch.object(at, "daily_queries_by_page", return_value=query_daily):
            data = at.build(None, dt.date(2026, 8, 1), dt.date(2026, 8, 10))
        data["verdict"] = at.verdict(data)
        data["aged_verdict"] = at.aged_verdict(data)
        report = at.render(data)
        self.assertIn("2–8", report)
        self.assertIn("error bound, not an estimate", report)
        self.assertIn("6 are withheld", report)


class TestDescribeThreeStates(unittest.TestCase):
    """A missing number must never look like a zero."""

    def test_younger_than_the_lag_is_no_data_yet(self):
        self.assertEqual(at.describe(None, -1), "no data yet")
        self.assertEqual(at.describe(None, -3), "no data yet")

    def test_observable_but_silent_is_a_measurement(self):
        self.assertEqual(at.describe(None, 14), "not yet, 14d")

    def test_zero_observable_days_is_still_a_measurement_not_no_data(self):
        self.assertEqual(at.describe(None, 0), "not yet, 0d")

    def test_a_real_answer_is_a_day_count(self):
        self.assertEqual(at.describe(6, 20), "6d")

    def test_day_zero_renders_as_a_day_count_not_as_absence(self):
        self.assertEqual(at.describe(0, 5), "0d")

    def test_no_state_ever_renders_as_a_bare_zero(self):
        for days, obs in ((None, -1), (None, 0), (None, 9)):
            self.assertNotEqual(at.describe(days, obs), "0")


class TestFirstDay(unittest.TestCase):
    START = dt.date(2026, 8, 1)

    def test_days_are_counted_from_the_start_date(self):
        s = series({"2026-08-01": (0, 0), "2026-08-04": (3, 0)})
        self.assertEqual(at.first_day(s, self.START, "impressions"), 3)

    def test_a_silent_series_returns_none_not_zero(self):
        s = series({"2026-08-02": (0, 0), "2026-08-03": (0, 0)})
        self.assertIsNone(at.first_day(s, self.START, "impressions"))

    def test_an_empty_series_returns_none(self):
        self.assertIsNone(at.first_day({}, self.START, "impressions"))

    def test_clicks_and_impressions_are_tracked_separately(self):
        s = series({"2026-08-02": (5, 0), "2026-08-09": (5, 1)})
        self.assertEqual(at.first_day(s, self.START, "impressions"), 1)
        self.assertEqual(at.first_day(s, self.START, "clicks"), 8)

    def test_impressions_predating_the_start_give_a_negative_day(self):
        """A recovered URL earns before its current source file exists; that is detectable."""
        s = series({"2026-07-20": (4, 0)})
        self.assertEqual(at.first_day(s, self.START, "impressions"), -12)


class TestTrajectory(unittest.TestCase):
    def test_position_is_impression_weighted_per_week(self):
        s = {"2026-08-03": {"impressions": 90, "clicks": 0, "position": 10.0},
             "2026-08-04": {"impressions": 10, "clicks": 0, "position": 20.0}}
        got = at.trajectory(s)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["impressions"], 100)
        self.assertEqual(got[0]["position"], 11.0)   # not the 15.0 a plain mean gives

    def test_weeks_are_separated_and_ordered(self):
        s = series({"2026-08-03": (5, 0), "2026-08-12": (7, 0)})
        got = at.trajectory(s)
        self.assertEqual([w["impressions"] for w in got], [5, 7])

    def test_an_empty_series_has_no_weeks(self):
        self.assertEqual(at.trajectory({}), [])


class TestAgedVerdict(unittest.TestCase):
    """The regression guard for calling a 2-day gap on one page a finding."""

    def frame(self, tool: dict, article: dict) -> dict:
        return {"aged": {"tool": tool, "article": article}, "aged_days": at.AGED_DAYS}

    def aged(self, pages, first=None, impressions=0, human=0, any_human=0):
        return {"pages": pages, "reached_impression": pages if first is not None else 0,
                "median_days_to_first": first, "median_impressions": impressions,
                "total_impressions": impressions, "total_human_impressions": human,
                "with_any_human_impression": any_human, "examples": []}

    def test_a_two_day_gap_on_one_tool_is_called_indistinguishable(self):
        d = self.frame(self.aged(1, first=65, impressions=9),
                       self.aged(65, first=67, impressions=4658, human=320, any_human=26))
        s = at.aged_verdict(d)
        self.assertIn("indistinguishable", s)
        self.assertNotIn("faster than articles", s)

    def test_a_large_gap_on_a_real_sample_is_called_a_difference(self):
        d = self.frame(self.aged(8, first=20, impressions=900),
                       self.aged(40, first=70, impressions=4000))
        self.assertIn("faster than", at.aged_verdict(d))

    def test_a_large_gap_on_a_tiny_sample_is_still_indistinguishable(self):
        d = self.frame(self.aged(2, first=10, impressions=100),
                       self.aged(40, first=70, impressions=4000))
        self.assertIn("indistinguishable", at.aged_verdict(d))

    def test_no_aged_tool_says_so_rather_than_concluding(self):
        d = self.frame(self.aged(0), self.aged(30, first=50, impressions=1000))
        s = at.aged_verdict(d)
        self.assertIn("no aged evidence about tools yet", s)

    def test_the_sample_size_caveat_is_always_present(self):
        d = self.frame(self.aged(1, first=65, impressions=9),
                       self.aged(65, first=67, impressions=4658))
        self.assertIn("not a basis for a decision on sixty rows", at.aged_verdict(d))


class TestNewPageVerdict(unittest.TestCase):
    def frame(self, tool, article):
        return {"comparison": {"tool": tool, "article": article}}

    def side(self, tracked, eligible, observable, reached, median):
        return {"tracked": tracked, "eligible": eligible, "observable": observable,
                "reached_impression": reached, "median_days": median,
                "impressions": 0, "human_impressions": 0, "clicks": 0,
                "excluded_pre_existing": 0, "excluded_recovered": 0}

    def test_nothing_observable_is_not_answerable_yet(self):
        d = self.frame(self.side(5, 3, 0, 0, None), self.side(73, 7, 0, 0, None))
        self.assertIn("Not answerable yet", at.verdict(d))

    def test_observable_but_silent_is_called_a_measurement(self):
        d = self.frame(self.side(5, 3, 2, 0, None), self.side(73, 7, 4, 0, None))
        s = at.verdict(d)
        self.assertIn("measurement rather than a wait", s)

    def test_articles_ahead_is_not_read_as_the_bet_being_wrong(self):
        d = self.frame(self.side(5, 3, 2, 0, None), self.side(73, 7, 4, 3, 5))
        s = at.verdict(d)
        self.assertIn("not evidence it is wrong", s)

    def test_a_real_two_sided_comparison_refuses_to_call_it_a_trend(self):
        d = self.frame(self.side(5, 5, 5, 4, 9), self.side(20, 20, 20, 18, 30))
        s = at.verdict(d)
        self.assertIn("directional", s)
        self.assertIn("do not reweight sixty calendar rows", s)


class TestToolsAreAllTracked(unittest.TestCase):
    def test_every_tool_template_maps_to_a_cluster_four_url(self):
        for url in at.TOOLS.values():
            self.assertIn(url, at.gr.TOOL_PATHS, url)
            self.assertEqual(at.gr.TOOL_PATHS[url], "ai-search-optimization")

    def test_the_tool_set_is_not_silently_empty(self):
        self.assertGreaterEqual(len(at.TOOLS), 4)


class TestDatedReportIsIdempotent(unittest.TestCase):
    def test_same_date_is_replaced_not_appended(self):
        existing = (
            "# Attribution\n\n"
            "## 2026-08-16 — attribution since 2026-08-14\nold day\n\n"
            "## 2026-08-17 — attribution since 2026-08-14\nstale\n"
        )
        report = "## 2026-08-17 — attribution since 2026-08-14\nfresh\n"

        got = at.upsert_dated_report(existing, report, "2026-08-17")

        self.assertEqual(got.count("## 2026-08-17 — attribution since"), 1)
        self.assertIn("fresh", got)
        self.assertNotIn("stale", got)
        self.assertIn("old day", got)

    def test_preexisting_same_date_duplicates_collapse_to_one(self):
        existing = (
            "# Attribution\n\n"
            "## 2026-08-17 — attribution since 2026-08-14\nfirst\n\n"
            "## 2026-08-17 — attribution since 2026-08-14\nsecond\n"
        )
        report = "## 2026-08-17 — attribution since 2026-08-14\nauthoritative\n"

        got = at.upsert_dated_report(existing, report, "2026-08-17")

        self.assertEqual(got.count("## 2026-08-17 — attribution since"), 1)
        self.assertIn("authoritative", got)
        self.assertNotIn("first", got)
        self.assertNotIn("second", got)

    def test_new_date_preserves_nested_headings(self):
        existing = (
            "# Attribution\n\n"
            "## 2026-08-16 — attribution since 2026-08-14\n"
            "### The bet: do tools reach search sooner than articles?\nlimits\n"
        )
        report = "## 2026-08-17 — attribution since 2026-08-14\nnew\n"

        got = at.upsert_dated_report(existing, report, "2026-08-17")

        self.assertIn("### The bet: do tools reach search sooner", got)
        self.assertEqual(got.count("— attribution since"), 2)


if __name__ == "__main__":
    unittest.main()
