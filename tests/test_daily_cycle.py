"""Timing contracts for the durable daily campaign gate."""

from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import daily_cycle as dc  # noqa: E402


class TestPublishDeadline(unittest.TestCase):
    def no_publish(self, *args, **kwargs):
        if args[:2] == ("git", "log"):
            return 0, "abc|2026-08-17|content: publish yesterday"
        return 0, ""

    @mock.patch.object(dc, "run")
    def test_missing_publish_before_slot_is_not_due_not_an_alarm(self, run):
        run.side_effect = self.no_publish
        now = dt.datetime(2026, 8, 17, 18, 31, tzinfo=dt.timezone.utc)
        self.assertEqual(
            dc.todays_publish(now), "NOT DUE — scheduled for 04:30 UTC"
        )

    @mock.patch.object(dc, "run")
    def test_missing_publish_after_slot_is_an_alarm(self, run):
        run.side_effect = self.no_publish
        now = dt.datetime(2026, 8, 18, 4, 31, tzinfo=dt.timezone.utc)
        self.assertIn("NO PUBLISH FOUND", dc.todays_publish(now))

    @mock.patch.object(dc, "run")
    def test_a_shipped_commit_wins_even_before_the_slot(self, run):
        def result(*args, **kwargs):
            if args[:2] == ("git", "log"):
                return 0, "def123|2026-08-18|content: publish early"
            return 0, ""

        run.side_effect = result
        now = dt.datetime(2026, 8, 17, 18, 31, tzinfo=dt.timezone.utc)
        self.assertEqual(dc.todays_publish(now), "shipped def123 content: publish early")

    def test_naive_datetime_is_refused(self):
        with self.assertRaises(ValueError):
            dc.todays_publish(dt.datetime(2026, 8, 18, 4, 31))


if __name__ == "__main__":
    unittest.main()
