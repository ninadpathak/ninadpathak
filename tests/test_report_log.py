"""Regression tests for campaign report-log idempotence."""

from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import report_log as rl  # noqa: E402


class TestDatedReportUpsert(unittest.TestCase):
    def test_same_day_retry_replaces_instead_of_appending(self):
        existing = (
            "# Instrument\n\n"
            "## 2026-08-17 — result\nstale\n"
        )
        report = "## 2026-08-17 — result\nfresh\n"

        got = rl.upsert_dated_report(existing, report, "2026-08-17")

        self.assertEqual(got.count("## 2026-08-17"), 1)
        self.assertIn("fresh", got)
        self.assertNotIn("stale", got)

    def test_old_duplicates_collapse_to_the_last_appended_observation(self):
        existing = (
            "# Instrument\n\n"
            "## 2026-08-16 — result\nold first\n\n"
            "## 2026-08-16 — result\nold authoritative\n\n"
            "## 2026-08-17 — result\nyesterday\n"
        )
        report = "## 2026-08-18 — result\ntoday\n"

        got = rl.upsert_dated_report(existing, report, "2026-08-18")

        self.assertEqual(got.count("## 2026-08-16"), 1)
        self.assertNotIn("old first", got)
        self.assertIn("old authoritative", got)
        self.assertLess(got.index("2026-08-16"), got.index("2026-08-17"))
        self.assertLess(got.index("2026-08-17"), got.index("2026-08-18"))

    def test_nested_headings_stay_inside_their_section(self):
        existing = (
            "# Instrument\n\n"
            "## 2026-08-16 — result\n"
            "### Limits\nwithholding applies\n"
        )
        report = "## 2026-08-17 — result\nnew\n"

        got = rl.upsert_dated_report(existing, report, "2026-08-17")

        self.assertIn("### Limits\nwithholding applies", got)
        self.assertEqual(got.count("## 2026-08-"), 2)

    def test_heading_suffix_can_change_between_retries(self):
        existing = "# Instrument\n\n## 2026-08-17 — old label\nstale\n"
        report = "## 2026-08-17 — corrected label\nfresh\n"

        got = rl.upsert_dated_report(existing, report, "2026-08-17")

        self.assertNotIn("old label", got)
        self.assertIn("corrected label", got)

    def test_header_only_file_gets_its_first_section(self):
        got = rl.upsert_dated_report(
            "# Instrument\n", "## 2026-08-17 — result\nfirst\n", "2026-08-17"
        )
        self.assertEqual(got, "# Instrument\n\n## 2026-08-17 — result\nfirst\n")


class TestCampaignLogsUseTheContract(unittest.TestCase):
    REPORTS = (
        "planning/daily-cycle.md",
        "planning/gsc-report.md",
        "planning/scoreboard.md",
        "planning/leading-indicators.md",
        "planning/gsc-human-baseline.md",
        "planning/band.md",
        "planning/gsc-collapse-forensics.md",
        "planning/page-position.md",
        "planning/position.md",
        "planning/merge-guard.md",
        "planning/attribution.md",
    )
    WRITERS = (
        "tools/daily_cycle.py",
        "tools/gsc_report.py",
        "tools/gsc_scoreboard.py",
        "tools/gsc_leading.py",
        "tools/gsc_human_baseline.py",
        "tools/gsc_band.py",
        "tools/gsc_collapse_forensics.py",
        "tools/gsc_page_position.py",
        "tools/gsc_position.py",
        "tools/gsc_merge_guard.py",
        "tools/gsc_attribution.py",
    )

    def test_no_durable_report_contains_duplicate_dates(self):
        for relative in self.REPORTS:
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            dates = [match.group("date") for match in rl.DATED_SECTION.finditer(text)]
            duplicates = sorted(date for date, count in Counter(dates).items() if count > 1)
            self.assertEqual(duplicates, [], relative)

    def test_no_report_writer_opens_its_log_in_append_mode(self):
        for relative in self.WRITERS:
            source = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn('.open("a"', source, relative)
            self.assertNotIn(".open('a'", source, relative)


if __name__ == "__main__":
    unittest.main()
