"""Deterministic tests for the referring-domain measurement.

The campaign decided the five tools are measured on referring domains rather than sessions.
That decision needed something to report the number, and nothing did. These tests pin the two
properties that make the report trustworthy:

  1. It says UNKNOWN when the authoritative figure has never been read, instead of quietly
     substituting a number it can reach. No automated path to Search Console's Links report
     exists — the API has no links resource and the browser account lacks property access —
     so the honest output is an admission, and it has to survive refactoring.
  2. It never adds a rel=canonical to an href. A canonical consolidates a duplicate; an href
     passes an endorsement. Summing them would inflate the only metric the tools are now
     judged on.

No test here touches the network. Every one runs against fixtures.
"""

import datetime as dt
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import link_inventory as li  # noqa: E402


def baseline(**over):
    data = {
        "refreshed": "2026-08-17T00:00:00Z",
        "domain": "ninadpathak.com",
        "authoritative_referring_domains": {"value": None, "read_on": None,
                                            "source": "Search Console > Links"},
        "devto_syndication": {"articles": 96, "canonical_to_us": 14,
                              "canonical_elsewhere": 82,
                              "elsewhere_hosts": ["pathak.ventures"],
                              "target_paths": ["/articles/a/"], "target_tool_paths": []},
        "sources": [{"id": "github-profile", "url": "https://github.com/ninadpathak",
                     "status": 200, "href_links": 1, "mentions": 4, "links_to_us": True,
                     "tool_links": []}],
        "unfetchable_sources": [{"id": "linkedin-profile", "url": "x", "reason": "HTTP 999"}],
        "caveat": "A rel=canonical is counted separately from an href.",
    }
    data.update(over)
    return data


class LinkCountingTests(unittest.TestCase):
    def test_an_href_to_the_domain_is_counted(self):
        html = '<a href="https://ninadpathak.com/linter/">tool</a>'
        self.assertEqual(li.count_domain_links(html), 1)

    def test_www_and_http_variants_count(self):
        html = ('<a href="http://www.ninadpathak.com/">a</a>'
                '<a href="https://ninadpathak.com/b/">b</a>')
        self.assertEqual(li.count_domain_links(html), 2)

    def test_a_bare_text_mention_is_not_an_href(self):
        """A domain printed in prose is not a link and must not be counted as one."""
        html = "<p>See ninadpathak.com for details</p>"
        self.assertEqual(li.count_domain_links(html), 0)
        self.assertEqual(li.count_domain_mentions(html), 1)

    def test_a_link_to_another_domain_is_not_counted(self):
        self.assertEqual(li.count_domain_links('<a href="https://example.com/">x</a>'), 0)


class HonestyTests(unittest.TestCase):
    """The properties that make this report worth reading."""

    def test_an_unread_authoritative_figure_reports_unknown(self):
        text = "\n".join(li.evaluate(baseline())["lines"])
        self.assertIn("REFERRING DOMAINS: UNKNOWN", text)
        self.assertIn("never been recorded", text)

    def test_a_recorded_figure_is_reported_with_its_date(self):
        data = baseline(authoritative_referring_domains={
            "value": 7, "read_on": "2026-08-18", "source": "Search Console > Links"})
        text = "\n".join(li.evaluate(data)["lines"])
        self.assertIn("referring domains: 7", text)
        self.assertIn("2026-08-18", text)
        self.assertNotIn("UNKNOWN", text)

    def test_canonicals_are_never_added_to_the_referring_domain_count(self):
        """14 dev.to canonicals must not become 14 referring domains."""
        summary = li.evaluate(baseline())["summary"]
        self.assertIsNone(summary["referring_domains"])
        self.assertEqual(summary["devto_canonical_here"], 14)

    def test_the_canonical_versus_href_caveat_is_always_printed(self):
        text = "\n".join(li.evaluate(baseline())["lines"])
        self.assertIn("canonical", text.lower())
        self.assertIn("endorsement", text.lower())

    def test_a_missing_baseline_fails_rather_than_reporting_zero(self):
        outcome = li.evaluate({})
        self.assertTrue(outcome["failures"])
        self.assertIn("NO LINK BASELINE", "\n".join(outcome["lines"]))

    def test_zero_tool_links_is_stated_as_a_number_not_as_silence(self):
        text = "\n".join(li.evaluate(baseline())["lines"])
        self.assertIn("per-tool verified inbound links:", text)
        self.assertIn("every tool is at zero", text)
        for path in li.TOOL_PATHS:
            self.assertIn(path, text)


class DevtoSyndicationTests(unittest.TestCase):
    def test_canonicals_pointing_elsewhere_are_reported(self):
        text = "\n".join(li.evaluate(baseline())["lines"])
        self.assertIn("82 canonicalised elsewhere", text)
        self.assertIn("pathak.ventures", text)

    def test_a_majority_pointing_elsewhere_raises_a_note(self):
        """82 of 96 syndicated articles pointing at another property is worth saying."""
        text = "\n".join(li.evaluate(baseline())["lines"])
        self.assertIn("point their canonical at another", text)

    def test_a_majority_pointing_here_raises_no_note(self):
        data = baseline(devto_syndication={"articles": 96, "canonical_to_us": 90,
                                           "canonical_elsewhere": 6, "elsewhere_hosts": [],
                                           "target_paths": [], "target_tool_paths": []})
        text = "\n".join(li.evaluate(data)["lines"])
        self.assertNotIn("point their canonical at another", text)

    def test_a_tool_canonical_is_counted_per_tool(self):
        data = baseline(devto_syndication={"articles": 1, "canonical_to_us": 1,
                                           "canonical_elsewhere": 0, "elsewhere_hosts": [],
                                           "target_paths": ["/linter/"],
                                           "target_tool_paths": ["/linter/"]})
        summary = li.evaluate(data)["summary"]
        self.assertEqual(summary["per_tool"]["/linter/"], 1)

    def test_an_unreadable_devto_api_is_reported_not_swallowed(self):
        data = baseline(devto_syndication={"error": "URLError: timed out", "articles": 0})
        self.assertIn("dev.to syndication unreadable", "\n".join(li.evaluate(data)["lines"]))


class UnmeasurableTests(unittest.TestCase):
    """What cannot be seen is recorded as a fact, with how it was established."""

    def test_the_gsc_api_really_has_no_links_resource(self):
        """Verified by enumeration rather than asserted, because the whole design rests on it."""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError:
            self.skipTest("google api client not installed")
        cred = pathlib.Path("/Users/ninad/Development/.google-service-account/"
                            "google-workspace-service-account.json")
        if not cred.exists():
            self.skipTest("no Search Console credential available")
        creds = service_account.Credentials.from_service_account_file(
            str(cred), scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
        svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
        self.assertEqual([n for n in dir(svc) if "link" in n.lower()], [],
                         "a links resource appeared — the tool's central premise changed")

    def test_the_shipped_baseline_records_what_cannot_be_measured(self):
        data = li.load_baseline()
        if not data:
            self.skipTest("no baseline committed yet")
        blocked = data.get("cannot_measure") or {}
        for key in ("gsc_links_api", "gsc_links_ui", "ga4_referrals", "ahrefs"):
            self.assertIn(key, blocked)
            self.assertTrue(str(blocked[key]).strip(), key)

    def test_unfetchable_sources_are_surfaced_in_the_report(self):
        self.assertIn("cannot verify linkedin-profile", "\n".join(li.evaluate(baseline())["lines"]))


class StalenessTests(unittest.TestCase):
    def test_age_is_measured_from_the_refreshed_stamp(self):
        self.assertEqual(li.baseline_age_days(baseline(), dt.date(2026, 8, 20)), 3)

    def test_a_missing_stamp_reads_as_ancient(self):
        self.assertGreater(li.baseline_age_days({}, dt.date(2026, 8, 20)), 1000)


class SummaryLineTests(unittest.TestCase):
    def test_the_summary_is_one_line_and_leads_with_the_unknown(self):
        line = li.summary_line(li.evaluate(baseline()))
        self.assertEqual(len(line.splitlines()), 1)
        self.assertIn("UNKNOWN", line)

    def test_the_summary_reports_a_missing_baseline(self):
        self.assertIn("NO LINK BASELINE", li.summary_line(li.evaluate({})))

    def test_the_summary_carries_the_tool_link_total(self):
        line = li.summary_line(li.evaluate(baseline()))
        self.assertIn("verified inbound links to tools: 0", line)


class ShippedBaselineTests(unittest.TestCase):
    def test_a_baseline_is_committed_and_parses(self):
        self.assertTrue(li.BASELINE.exists(),
                        "planning/link-inventory.json must be committed")
        data = li.load_baseline()
        self.assertIn("refreshed", data)
        self.assertIn("devto_syndication", data)

    def test_the_committed_baseline_covers_every_tool(self):
        outcome = li.check()
        for path in li.TOOL_PATHS:
            self.assertIn(path, outcome["summary"]["per_tool"])

    def test_the_check_runs_offline_against_the_committed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "b.json"
            path.write_text(json.dumps(baseline()))
            outcome = li.check(baseline_path=path, today=dt.date(2026, 8, 17))
        self.assertEqual(outcome["failures"], [])
        self.assertIn("per-tool verified inbound links:", "\n".join(outcome["lines"]))


class DailyCycleWiringTests(unittest.TestCase):
    def test_the_daily_cycle_reports_the_link_baseline(self):
        source = (ROOT / "tools" / "daily_cycle.py").read_text(encoding="utf-8")
        self.assertIn("link_inventory", source)
        self.assertIn("Referring domains:", source)


if __name__ == "__main__":
    unittest.main()
