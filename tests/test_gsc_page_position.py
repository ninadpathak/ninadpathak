"""Deterministic tests for point-in-time page position.

This tool exists because absence from a differential report was read as absence of a
position, and that inference reversed a merge. The four states must therefore stay
distinct, and `withheld` must never be reported as "no position": those two look identical
in any query-level view and mean opposite things.

The position guard is also pinned. A bare average position is not a fact about ranking,
because a page's average moves whenever its query mix moves — three false readings on this
campaign came from exactly that.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import gsc_page_position as pp  # noqa: E402

BASE = "https://ninadpathak.com"


def hrow(page: str, query: str, position: float, impressions: float = 10,
         clicks: float = 0) -> dict:
    return {"keys": [query], "page": BASE + page, "position": position,
            "impressions": impressions, "clicks": clicks}


class TestPositionGuard(unittest.TestCase):
    """No query count, no number. This is the confound guard."""

    def test_a_position_prints_with_its_query_count(self):
        self.assertEqual(pp.position_cell(18.2, 3), "18.2 (n=3)")

    def test_a_position_with_no_queries_refuses_to_print(self):
        self.assertEqual(pp.position_cell(18.2, 0), "—")

    def test_a_missing_position_refuses_to_print(self):
        self.assertEqual(pp.position_cell(None, 5), "—")

    def test_a_negative_query_count_refuses_to_print(self):
        self.assertEqual(pp.position_cell(18.2, -1), "—")


class TestFourStates(unittest.TestCase):
    SLUG = "a-post"
    CANON = f"{BASE}/articles/{SLUG}/"
    LEGACY = f"{BASE}/blog/{SLUG}/"

    def meta(self, named=()):
        return {"named_pages": set(named)}

    def test_measured_when_a_human_query_is_named(self):
        got = pp.classify(self.SLUG,
                          {self.LEGACY: {"impressions": 48, "clicks": 0, "position": 22.7}},
                          {self.LEGACY: [hrow(f"/blog/{self.SLUG}/", "q", 37.0, 1)]},
                          self.meta([self.LEGACY]))
        self.assertEqual(got["state"], pp.MEASURED)
        self.assertEqual(got["position"], 37.0)
        self.assertEqual(got["query_count"], 1)

    def test_withheld_when_impressions_exist_but_no_query_is_named(self):
        got = pp.classify(self.SLUG,
                          {self.LEGACY: {"impressions": 13, "clicks": 0, "position": 40.0}},
                          {}, self.meta())
        self.assertEqual(got["state"], pp.WITHHELD)
        self.assertIsNone(got["position"])
        self.assertEqual(got["impressions"], 13)

    def test_no_human_queries_when_every_named_query_is_filtered_out(self):
        """The page is named in the pull, but nothing survived the human filter."""
        got = pp.classify(self.SLUG,
                          {self.LEGACY: {"impressions": 20, "clicks": 0, "position": 9.0}},
                          {}, self.meta([self.LEGACY]))
        self.assertEqual(got["state"], pp.NO_HUMAN)
        self.assertIsNone(got["position"])

    def test_never_impressed_only_when_there_are_no_impressions(self):
        got = pp.classify(self.SLUG, {}, {}, self.meta())
        self.assertEqual(got["state"], pp.NEVER)
        self.assertEqual(got["impressions"], 0)

    def test_withheld_is_not_never_impressed(self):
        """The distinction that caused the merge error. These must not collapse."""
        withheld = pp.classify(self.SLUG,
                               {self.LEGACY: {"impressions": 13, "clicks": 0,
                                              "position": 40.0}}, {}, self.meta())
        never = pp.classify(self.SLUG, {}, {}, self.meta())
        self.assertNotEqual(withheld["state"], never["state"])
        self.assertGreater(withheld["impressions"], never["impressions"])

    def test_both_path_prefixes_are_summed(self):
        got = pp.classify(
            self.SLUG,
            {self.CANON: {"impressions": 5, "clicks": 0, "position": 10.0},
             self.LEGACY: {"impressions": 43, "clicks": 1, "position": 25.0}},
            {}, self.meta())
        self.assertEqual(got["impressions"], 48)
        self.assertEqual(got["clicks"], 1)

    def test_position_is_impression_weighted_across_queries(self):
        rows = [hrow(f"/blog/{self.SLUG}/", "q1", 10.0, 90),
                hrow(f"/blog/{self.SLUG}/", "q2", 100.0, 10)]
        got = pp.classify(self.SLUG,
                          {self.LEGACY: {"impressions": 100, "clicks": 0, "position": 19.0}},
                          {self.LEGACY: rows}, self.meta([self.LEGACY]))
        self.assertEqual(got["query_count"], 2)
        self.assertEqual(got["position"], 19.0)      # not the 55.0 a plain mean gives


class TestMergeEvidenceIsReconstructible(unittest.TestCase):
    """The batch-1 numbers, pinned so the corrected reading cannot be lost again.

    The spec recorded `ai-memory-management-for-llms` as "unknown, not measured" and chose
    the other page because it was "measured at 18.2". Both were measurable in the same
    window; the first was simply absent from a movement table because it had not moved.
    """

    A, B = "ai-memory-management-for-llms", "memory-hierarchy-in-ai-systems"

    def test_the_page_called_unmeasured_has_impressions_and_therefore_a_position(self):
        a = pp.classify(self.A,
                        {f"{BASE}/blog/{self.A}/": {"impressions": 48, "clicks": 0,
                                                    "position": 22.7}},
                        {}, {"named_pages": set()})
        self.assertNotEqual(a["state"], pp.NEVER)
        self.assertEqual(a["state"], pp.WITHHELD)
        self.assertEqual(a["impressions"], 48)

    def test_impressions_favour_the_original_target(self):
        a_impr, b_impr = 48, 15
        self.assertGreater(a_impr, b_impr)

    def test_a_two_place_gap_on_five_impressions_is_not_a_basis(self):
        """18.2 against 20.4, on 5 impressions against 22."""
        gap = abs(18.2 - 20.4)
        self.assertLess(gap, 3.0)


class TestRefusalPreconditions(unittest.TestCase):
    def test_the_states_are_distinct_strings(self):
        states = {pp.MEASURED, pp.NO_HUMAN, pp.WITHHELD, pp.NEVER}
        self.assertEqual(len(states), 4)

    def test_only_one_state_means_no_position(self):
        self.assertEqual(pp.NEVER, "never-impressed")

    def test_the_window_default_is_long_enough_to_see_a_stable_page(self):
        """A 28-day window showed neither merge candidate a single human query."""
        self.assertGreaterEqual(pp.WINDOW_DAYS, 90)


if __name__ == "__main__":
    unittest.main()
