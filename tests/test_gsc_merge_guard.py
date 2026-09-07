"""Deterministic contract tests for the pre-merge Search Console guard."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import gsc_merge_guard as mg  # noqa: E402

BASE = "https://ninadpathak.com"


def period(page_rows=(), human_by_page=None, named_by_page=None, pq_rows=()):
    rows = list(page_rows)
    return {
        "page_rows": rows,
        "by_page": {row["keys"][0]: row for row in rows},
        "human_by_page": human_by_page or {},
        "named_by_page": named_by_page or {},
        "pq_rows": list(pq_rows),
    }


def page(slug, impressions=10, position=20, clicks=0, prefix="/blog/"):
    return {"keys": [f"{BASE}{prefix}{slug}/"], "impressions": impressions,
            "clicks": clicks, "position": position}


def query(slug, text, impressions=3, position=15, prefix="/blog/"):
    return {"keys": [text], "page": f"{BASE}{prefix}{slug}/",
            "impressions": impressions, "clicks": 0, "position": position}


class TestAuditParser(unittest.TestCase):
    def test_parses_merge_and_retirement_only_from_disposition_table(self):
        text = """before
### Merge, 2 pages
| `source-a` | 5 | 0 | `target-a` | carry this |
| `source-b` | 0 | 1 | `target-b` | **CORRECTED: RETIRE.** |
### Keep but repoint
| `not-a-source` | 10 | 2 | `not-a-target` | ignore |
"""
        got = mg.parse_dispositions(text)
        self.assertEqual(len(got), 2)
        self.assertEqual(got[0]["disposition"], "merge")
        self.assertEqual(got[1]["disposition"], "retire")

    def test_real_audit_has_nineteen_merges_and_one_retirement(self):
        got = mg.parse_dispositions(mg.AUDIT.read_text())
        self.assertEqual(len(got), 20)
        self.assertEqual(sum(row["disposition"] == "merge" for row in got), 19)
        self.assertEqual(sum(row["disposition"] == "retire" for row in got), 1)
        self.assertEqual(len({row["source"] for row in got}), 20)
        self.assertNotIn(
            "how-memory-works-in-hyperagents",
            {row["source"] for row in got},
        )

    def test_real_audit_sources_and_targets_exist_even_after_status_changes(self):
        rows = mg.parse_dispositions(mg.AUDIT.read_text())
        statuses = mg.load_post_statuses()
        self.assertFalse({row["source"] for row in rows} - statuses.keys())
        self.assertFalse({row["target"] for row in rows} - statuses.keys())
        self.assertTrue(all(statuses[row["target"]] == "published" for row in rows))


class TestQueryCombination(unittest.TestCase):
    def test_combines_legacy_and_canonical_query_rows_weighted_by_impressions(self):
        rows = [query("a", "same query", 9, 10, "/blog/"),
                query("a", "same query", 1, 100, "/articles/")]
        got = mg.combine_queries(rows)
        self.assertEqual(got, [{"query": "same query", "impressions": 10,
                                "clicks": 0, "position": 19.0}])

    def test_page_query_fetch_paginates_instead_of_accepting_a_cap(self):
        calls = []

        class Request:
            def __init__(self, body):
                self.body = body

            def execute(self):
                start = self.body["startRow"]
                return {"rows": ([{"id": 1}, {"id": 2}] if start == 0
                                 else [{"id": 3}] if start == 2 else [])}

        class SearchAnalytics:
            def query(self, siteUrl, body):
                calls.append(body["startRow"])
                return Request(body)

        class Service:
            def searchanalytics(self):
                return SearchAnalytics()

        got = mg.fetch_page_queries(Service(), "2026-01-01", "2026-01-31", row_limit=2)
        self.assertEqual([row["id"] for row in got], [1, 2, 3])
        self.assertEqual(calls, [0, 2])


class TestFourStates(unittest.TestCase):
    def test_measured(self):
        row = page("a")
        q = query("a", "human query")
        got = mg.page_stats("a", period([row], {row["keys"][0]: [q]}))
        self.assertEqual(got["state"], mg.MEASURED)
        self.assertEqual(got["human_query_count"], 1)

    def test_withheld_is_not_never(self):
        withheld = mg.page_stats("a", period([page("a")]))
        never = mg.page_stats("b", period())
        self.assertEqual(withheld["state"], mg.WITHHELD)
        self.assertEqual(never["state"], mg.NEVER)

    def test_no_human_when_named_rows_exist_but_none_survive_filtering(self):
        row = page("a")
        url = row["keys"][0]
        got = mg.page_stats("a", period([row], named_by_page={url: [{"x": 1}]}))
        self.assertEqual(got["state"], mg.NO_HUMAN)

    def test_page_paths_are_combined_and_position_is_impression_weighted(self):
        rows = [page("a", 9, 10, prefix="/blog/"),
                page("a", 1, 100, prefix="/articles/")]
        got = mg.page_stats("a", period(rows))
        self.assertEqual(got["impressions"], 10)
        self.assertEqual(got["position"], 19.0)


class TestVerdicts(unittest.TestCase):
    def stats(self, state, impressions=10, queries=()):
        return {"state": state, "impressions": impressions,
                "human_queries": [{"query": q} for q in queries]}

    def test_shared_named_demand_is_positive_overlap_evidence(self):
        src = self.stats(mg.MEASURED, queries=["same"])
        tgt = self.stats(mg.MEASURED, queries=["same", "other"])
        self.assertEqual(mg.verdict("merge", src, tgt), "shared-named-demand")

    def test_visible_source_demand_without_overlap_requires_review(self):
        src = self.stats(mg.MEASURED, queries=["source job"])
        tgt = self.stats(mg.MEASURED, queries=["target job"])
        self.assertEqual(mg.verdict("merge", src, tgt), "review-source-demand")

    def test_withheld_source_stays_unknown(self):
        src = self.stats(mg.WITHHELD)
        tgt = self.stats(mg.MEASURED, queries=["target"])
        self.assertEqual(mg.verdict("merge", src, tgt), "withheld-source-demand")

    def test_filtered_source_is_not_called_human_demand(self):
        src = self.stats(mg.NO_HUMAN)
        tgt = self.stats(mg.MEASURED, queries=["target"])
        self.assertEqual(mg.verdict("merge", src, tgt), "no-human-source-demand")

    def test_no_impressions_does_not_become_overlap_support(self):
        src = self.stats(mg.NEVER, impressions=0)
        tgt = self.stats(mg.MEASURED, queries=["target"])
        self.assertEqual(mg.verdict("merge", src, tgt), "no-source-demand-observed")

    def test_retirement_holds_if_any_demand_exists(self):
        src = self.stats(mg.WITHHELD, impressions=1)
        tgt = self.stats(mg.NEVER, impressions=0)
        self.assertEqual(mg.verdict("retire", src, tgt), "hold-retirement")

    def test_retirement_can_only_say_no_demand_observed(self):
        src = self.stats(mg.NEVER, impressions=0)
        tgt = self.stats(mg.NEVER, impressions=0)
        self.assertEqual(mg.verdict("retire", src, tgt),
                         "retire-no-demand-observed")


class TestCoverageAndRendering(unittest.TestCase):
    def test_coverage_uses_page_dimension_as_denominator(self):
        p = period([page("a", 20)], pq_rows=[{"keys": [f"{BASE}/blog/a/", "q"],
                                                       "impressions": 5}])
        self.assertEqual(mg.coverage(p), {"page_impressions": 20,
                                          "pq_impressions": 5, "pct": 25.0})

    def test_position_never_prints_without_impressions(self):
        self.assertEqual(mg.position_cell({"position": 18.2, "impressions": 0}), "—")
        self.assertEqual(mg.position_cell({"position": 18.2, "impressions": 5}),
                         "18.2 (5 impr)")

    def test_report_calls_query_counts_floors_and_absence_not_proof(self):
        data = {
            "generated": "2026-08-17", "window_days": 90,
            "current_window": ["2026-05-17", "2026-08-14"],
            "history_window": ["2025-04-04", "2026-08-14"],
            "current_coverage": {"sitewide": {"pq_impressions": 1,
                                                 "page_impressions": 10, "pct": 10.0},
                                 "merge_pages": {"pq_impressions": 1,
                                                 "page_impressions": 5, "pct": 20.0}},
            "history_coverage": {"sitewide": {"pq_impressions": 2,
                                                 "page_impressions": 20, "pct": 10.0},
                                 "merge_pages": {"pq_impressions": 1,
                                                 "page_impressions": 10, "pct": 10.0}},
            "pairs": [],
        }
        report = mg.render(data)
        self.assertIn("FLOORS", report)
        self.assertIn("no observed overlap is not evidence", report)
        self.assertIn("Content equivalence", report)

    def test_same_day_rerun_replaces_instead_of_appending(self):
        existing = (
            "# Guard\n\n"
            "## 2026-08-16 — pre-merge Search Console guard\nold day\n\n"
            "## 2026-08-17 — pre-merge Search Console guard\nstale\n"
        )
        report = "## 2026-08-17 — pre-merge Search Console guard\nfresh\n"
        got = mg.upsert_dated_report(existing, report, "2026-08-17")
        self.assertEqual(got.count("## 2026-08-17 — pre-merge Search Console guard"), 1)
        self.assertIn("fresh", got)
        self.assertNotIn("stale", got)
        self.assertIn("old day", got)

    def test_new_day_preserves_nested_headings_in_old_report(self):
        existing = (
            "# Guard\n\n"
            "## 2026-08-16 — pre-merge Search Console guard\n"
            "### What this guard can and cannot decide\nlimits\n"
        )
        report = "## 2026-08-17 — pre-merge Search Console guard\nnew\n"
        got = mg.upsert_dated_report(existing, report, "2026-08-17")
        self.assertIn("### What this guard can and cannot decide\nlimits", got)
        self.assertEqual(got.count("— pre-merge Search Console guard"), 2)


if __name__ == "__main__":
    unittest.main()
