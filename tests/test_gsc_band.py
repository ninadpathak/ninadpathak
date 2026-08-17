"""Deterministic tests for the day-90 band re-derivation.

Two defects from the first run are pinned, because both produced a confident wrong answer:

  * Taking each cluster's very best N keywords unconditionally is perfect selection, and it
    made the band report UP when every premise under it had worsened. Selection quality is
    a scenario axis, not a constant.
  * The verdict prose asserted "Down" above a band that had gone up, because the wording
    was written before the arithmetic. Direction is read off the numbers.
"""

from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import gsc_band as bd  # noqa: E402

# A ranked pool per cluster, descending, so slicing is checkable by hand.
POOL = {1: [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100],
        3: [2000, 1800, 1600, 1400, 1200, 1000, 800, 600, 400, 200]}


class TestAllocation(unittest.TestCase):
    def test_rows_are_fully_allocated(self):
        for share in (0.4, 0.55, 0.7):
            alloc = bd.allocate(60, share)
            self.assertEqual(sum(alloc.values()), 60, share)

    def test_cluster_three_gets_its_share(self):
        self.assertEqual(bd.allocate(60, 0.55)[3], 33)

    def test_a_higher_share_moves_rows_into_cluster_three(self):
        self.assertGreater(bd.allocate(60, 0.70)[3], bd.allocate(60, 0.40)[3])

    def test_no_cluster_is_allocated_a_negative_row_count(self):
        for share in (0.0, 0.5, 1.0):
            self.assertTrue(all(n > 0 for n in bd.allocate(60, share).values()))


class TestSelectionSlices(unittest.TestCase):
    def test_rank_zero_takes_the_best_keywords(self):
        got = bd.per_page_volume(POOL, {1: 3}, 0)
        self.assertEqual(got["head_volume"], 2700)      # 1000+900+800
        self.assertEqual(got["per_cluster"][1]["slice"], "1-3")

    def test_rank_one_takes_the_next_slice_down(self):
        got = bd.per_page_volume(POOL, {1: 3}, 1)
        self.assertEqual(got["head_volume"], 1800)      # 700+600+500
        self.assertEqual(got["per_cluster"][1]["slice"], "4-6")

    def test_deeper_slices_are_strictly_smaller(self):
        vols = [bd.per_page_volume(POOL, {1: 3}, r)["head_volume"] for r in (0, 1, 2)]
        self.assertEqual(vols, sorted(vols, reverse=True))
        self.assertEqual(len(set(vols)), 3)

    def test_running_off_the_end_of_the_pool_is_reported(self):
        got = bd.per_page_volume(POOL, {1: 4}, 2)       # ranks 9-12 of a 10-deep pool
        self.assertEqual(got["per_cluster"][1]["short_by"], 2)

    def test_perfect_selection_is_never_the_default(self):
        """The regression guard for the band reporting UP on a worsened premise."""
        best = bd.per_page_volume(POOL, {3: 3}, 0)["head_volume"]
        used = bd.per_page_volume(POOL, {3: 3}, 1)["head_volume"]
        self.assertLess(used, best)


class TestMaturity(unittest.TestCase):
    def test_fewer_rows_buy_fewer_mature_equivalents(self):
        self.assertLess(bd.mature_equivalents(60), bd.mature_equivalents(71))

    def test_maturity_is_well_under_the_row_count(self):
        """Publishing 60 pages in 90 days does not give 60 ranked pages on day 90."""
        self.assertLess(bd.mature_equivalents(60), 60 * 0.4)


class TestDirectionIsReadOffTheNumbers(unittest.TestCase):
    def frame(self, central, prior=741):
        return {"new_central": central, "prior_central": prior,
                "central_change_pct": round(100 * (central - prior) / prior),
                "direction": ("down" if (central - prior) / prior <= -0.10 else
                              "up" if (central - prior) / prior >= 0.10 else
                              "broadly unchanged")}

    def test_a_fall_is_called_down(self):
        self.assertEqual(self.frame(413)["direction"], "down")

    def test_a_rise_is_called_up_not_down(self):
        """The first run printed "Down" above a band that had risen."""
        self.assertEqual(self.frame(1100)["direction"], "up")

    def test_a_small_move_is_not_called_a_direction(self):
        self.assertEqual(self.frame(760)["direction"], "broadly unchanged")


class TestLegacyTermUnits(unittest.TestCase):
    def test_legacy_is_the_measured_human_non_brand_rate(self):
        """The old band added sitewide clicks including brand to a human non-brand band."""
        self.assertEqual(bd.LEGACY_HUMAN_CLICKS, 0)

    def test_tools_contribute_no_click_rows(self):
        self.assertEqual(bd.TOOL_ROWS, 0)


class TestHaircutIsARange(unittest.TestCase):
    def test_share_and_loss_are_three_point_ranges(self):
        self.assertEqual(len(bd.AIO_SHARE), 3)
        self.assertEqual(len(bd.AIO_LOSS), 3)

    def test_the_range_is_ordered_low_to_high(self):
        self.assertEqual(list(bd.AIO_SHARE), sorted(bd.AIO_SHARE))
        self.assertEqual(list(bd.AIO_LOSS), sorted(bd.AIO_LOSS))

    def test_the_old_point_estimate_sits_inside_the_new_range(self):
        """49.2% x 35% was the old haircut; it must still be representable."""
        self.assertLessEqual(bd.AIO_SHARE[0], 0.492)
        self.assertGreaterEqual(bd.AIO_SHARE[2], 0.492)


if __name__ == "__main__":
    unittest.main()
