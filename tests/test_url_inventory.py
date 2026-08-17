"""Deterministic tests for the URL inventory guard.

The guard exists because the March 2026 rebuild 404ed the entire previous site and nobody
noticed for five months. Its whole value is being right about which dead URLs matter, so
these tests pin the classification and, more importantly, the three false-positive classes
found while building it. Each of those would have reported live pages as leaks:

  1. Reading static/_redirects instead of the built output/_redirects. build.py generates
     183 /blog/ rules at build time; the source file holds 25. Reported 65 phantom leaks.
  2. Appending a trailing slash to extension-less paths, so /static/visuals/agent-taxonomy
     never matched the agent-taxonomy.html the build produces. Reported 12 phantom leaks.
  3. Not modelling Cloudflare's extension-less serving, verified against production:
     /static/visuals/agent-taxonomy returns 200, and the .html and trailing-slash forms
     return 308 to it.

No test here needs credentials or a network. Everything runs against fixtures in a temp
directory, which is the same property that lets the guard run in CI.
"""

import datetime as dt
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import url_inventory as ui  # noqa: E402


def inventory(*rows) -> dict:
    return {
        "refreshed": "2026-08-17T00:00:00Z",
        "site": "sc-domain:example.com",
        "span": {"earliest_with_data": "2025-04-21", "end": "2026-08-14"},
        "windows": {"gsc_lag_days": 3, "alarm_days": 28, "watch_days": 84},
        "url_count": len(rows),
        "urls": list(rows),
    }


def row(path, total=10, alarm=0, watch=0, clicks=0) -> dict:
    return {"path": path, "clicks_total": clicks, "impressions_total": total,
            "impressions_watch": watch, "impressions_alarm": alarm, "clicks_alarm": 0}


def allow(exact=None, prefixes=None, redirects=None, problems=None) -> dict:
    return {"exact": exact or {}, "prefixes": prefixes or [],
            "redirects": redirects or {}, "problems": problems or []}


NO_REDIRECTS = {"exact": {}, "wildcard": []}


class PathNormalisationTests(unittest.TestCase):
    def test_strips_origin_query_and_fragment(self):
        self.assertEqual(ui._norm("https://ninadpathak.com/articles/?a=1#x"), "/articles/")

    def test_does_not_append_a_trailing_slash(self):
        """Regression: appending one stopped extension-less paths matching the build."""
        self.assertEqual(ui._norm("/static/visuals/agent-taxonomy"),
                         "/static/visuals/agent-taxonomy")

    def test_adds_a_leading_slash(self):
        self.assertEqual(ui._norm("articles/"), "/articles/")

    def test_empty_becomes_root(self):
        self.assertEqual(ui._norm(""), "/")

    def test_variants_cover_both_slash_forms(self):
        self.assertEqual(ui._variants("/articles/"), {"/articles", "/articles/"})

    def test_variants_cover_extension_less_serving(self):
        """Cloudflare serves foo.html at /foo; verified against production 2026-08-17."""
        got = ui._variants("/static/visuals/a.html")
        self.assertIn("/static/visuals/a.html", got)
        self.assertIn("/static/visuals/a", got)
        self.assertIn("/static/visuals/a/", got)

    def test_root_variants_stay_root(self):
        self.assertEqual(ui._variants("/"), {"/"})


class BuiltPathsTests(unittest.TestCase):
    def test_index_html_and_standalone_files_are_both_registered(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp)
            (out / "articles" / "foo").mkdir(parents=True)
            (out / "articles" / "foo" / "index.html").write_text("x")
            (out / "index.html").write_text("x")
            (out / "static" / "visuals").mkdir(parents=True)
            (out / "static" / "visuals" / "bar.html").write_text("x")
            (out / "llms.txt").write_text("x")

            built = ui.built_paths(out)

        self.assertIn("/", built)
        self.assertIn("/articles/foo/", built)
        self.assertIn("/articles/foo", built)
        self.assertIn("/static/visuals/bar.html", built)
        self.assertIn("/static/visuals/bar", built)
        self.assertIn("/llms.txt", built)

    def test_missing_output_is_empty_not_an_error(self):
        self.assertEqual(ui.built_paths(pathlib.Path("/nonexistent-xyz")), set())


class RedirectLoadingTests(unittest.TestCase):
    def test_prefers_the_built_file_over_the_source_file(self):
        """Regression: reading static/_redirects reported 65 phantom leaks."""
        source = ui.REDIRECTS_SOURCE
        built = ui.REDIRECTS_BUILT
        self.assertNotEqual(source, built)
        if built.exists() and source.exists():
            self.assertGreater(len(ui.load_redirects(built)["exact"]),
                               len(ui.load_redirects(source)["exact"]),
                               "the built file should carry the generated rules")

    def test_exact_and_wildcard_rules_are_separated(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = pathlib.Path(tmp) / "_redirects"
            f.write_text("# comment\n/a/ /b/ 301\n/old/* /new/:splat 301\n\nnot-a-rule\n")
            got = ui.load_redirects(f)
        self.assertEqual(got["exact"], {"/a/": "/b/"})
        self.assertEqual(got["wildcard"], [("/old/*", "/new/:splat")])

    def test_missing_file_is_empty(self):
        got = ui.load_redirects(pathlib.Path("/nonexistent-xyz/_redirects"))
        self.assertEqual(got["exact"], {})


class ClassificationTests(unittest.TestCase):
    def test_a_built_url_is_not_classified_at_all(self):
        result = ui.classify(inventory(row("/articles/a/", alarm=99)),
                             {"/articles/a/"}, NO_REDIRECTS, allow())
        self.assertEqual(sum(len(v) for v in result.values()), 0)

    def test_dead_and_still_earning_is_an_alarm(self):
        """The expensive case: an active leak."""
        result = ui.classify(inventory(row("/gone/", alarm=5, watch=20)),
                             set(), NO_REDIRECTS, allow())
        self.assertEqual([r["path"] for r in result["alarm"]], ["/gone/"])
        self.assertEqual(result["watch"], [])

    def test_dropped_inside_84_days_is_watch_not_alarm(self):
        result = ui.classify(inventory(row("/gone/", alarm=0, watch=20)),
                             set(), NO_REDIRECTS, allow())
        self.assertEqual([r["path"] for r in result["watch"]], ["/gone/"])
        self.assertEqual(result["alarm"], [])

    def test_zero_in_84_days_is_a_write_off_and_never_an_alarm(self):
        """A URL Google has dropped must not fail the build forever."""
        result = ui.classify(inventory(row("/gone/", total=5000, alarm=0, watch=0)),
                             set(), NO_REDIRECTS, allow())
        self.assertEqual([r["path"] for r in result["writeoff"]], ["/gone/"])
        self.assertEqual(result["alarm"], [])

    def test_redirect_to_a_real_page_is_a_pass(self):
        result = ui.classify(
            inventory(row("/blog/a/", alarm=50)),
            {"/articles/a/", "/articles/a"},
            {"exact": {"/blog/a/": "/articles/a/"}, "wildcard": []},
            allow())
        self.assertEqual(result["alarm"], [])
        self.assertEqual([r["path"] for r in result["redirected"]], ["/blog/a/"])
        self.assertEqual(result["soft404"], [])

    def test_redirect_to_a_bare_listing_is_reported_as_a_soft_404(self):
        result = ui.classify(
            inventory(row("/blog/a/", alarm=50)),
            {"/articles/", "/articles"},
            {"exact": {"/blog/a/": "/articles/"}, "wildcard": []},
            allow())
        self.assertEqual([r["path"] for r in result["soft404"]], ["/blog/a/"])
        self.assertTrue(result["soft404"][0]["target_is_listing"])

    def test_redirect_to_a_missing_page_is_reported(self):
        result = ui.classify(
            inventory(row("/blog/a/", alarm=50)),
            set(),
            {"exact": {"/blog/a/": "/articles/nope/"}, "wildcard": []},
            allow())
        self.assertEqual([r["path"] for r in result["soft404"]], ["/blog/a/"])
        self.assertFalse(result["soft404"][0]["target_is_built"])

    def test_a_soft_404_never_becomes_an_alarm(self):
        """Reporting beats blocking where equivalence cannot be judged mechanically."""
        result = ui.classify(
            inventory(row("/blog/a/", alarm=500)),
            {"/articles/"},
            {"exact": {"/blog/a/": "/articles/"}, "wildcard": []},
            allow())
        self.assertEqual(result["alarm"], [])

    def test_a_human_approved_listing_redirect_is_not_reported_forever(self):
        result = ui.classify(
            inventory(row("/blog/", watch=35)),
            {"/articles/"},
            {"exact": {"/blog/": "/articles/"}, "wildcard": []},
            allow(redirects={"/blog/": {
                "target": "/articles/", "reason": "listing replaced listing"
            }}),
        )
        self.assertEqual(result["soft404"], [])
        self.assertEqual([r["path"] for r in result["redirected"]], ["/blog/"])
        self.assertTrue(result["redirected"][0]["equivalence_approved"])

    def test_redirect_approval_does_not_survive_a_target_change(self):
        result = ui.classify(
            inventory(row("/blog/", watch=35)),
            {"/articles/"},
            {"exact": {"/blog/": "/articles/"}, "wildcard": []},
            allow(redirects={"/blog/": {
                "target": "/tools/", "reason": "old decision"
            }}),
        )
        self.assertEqual([r["path"] for r in result["soft404"]], ["/blog/"])

    def test_equivalent_redirect_without_a_reason_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "allow.yaml"
            path.write_text(
                "equivalent_redirects:\n"
                "  - path: /blog/\n"
                "    target: /articles/\n"
            )
            got = ui.load_allowlist(path)
        self.assertEqual(got["redirects"], {})
        self.assertEqual(len(got["problems"]), 1)

    def test_redirect_matches_across_slash_variants(self):
        result = ui.classify(
            inventory(row("/blog/a", alarm=5)),
            {"/articles/a/"},
            {"exact": {"/blog/a/": "/articles/a/"}, "wildcard": []},
            allow())
        self.assertEqual([r["path"] for r in result["redirected"]], ["/blog/a"])

    def test_extension_less_serving_is_not_a_leak(self):
        """Regression: this reported 12 live visual pages as leaks."""
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp)
            (out / "static" / "visuals").mkdir(parents=True)
            (out / "static" / "visuals" / "agent-taxonomy.html").write_text("x")
            built = ui.built_paths(out)
        result = ui.classify(inventory(row("/static/visuals/agent-taxonomy/", alarm=1)),
                             built, NO_REDIRECTS, allow())
        self.assertEqual(result["alarm"], [])


class AllowlistTests(unittest.TestCase):
    def test_an_exact_entry_retires_a_url(self):
        result = ui.classify(inventory(row("/old/", alarm=99)), set(), NO_REDIRECTS,
                             allow(exact={"/old/": {"reason": "legacy"}}))
        self.assertEqual([r["path"] for r in result["retired"]], ["/old/"])
        self.assertEqual(result["alarm"], [])

    def test_a_prefix_entry_retires_children(self):
        result = ui.classify(inventory(row("/products/a/")), set(), NO_REDIRECTS,
                             allow(prefixes=[("/products/", {"reason": "legacy"})]))
        self.assertEqual([r["path"] for r in result["retired"]], ["/products/a/"])

    def test_a_prefix_does_not_retire_its_own_base(self):
        """So retiring the old glossary's children cannot retire the live /glossary/."""
        result = ui.classify(inventory(row("/glossary/", alarm=0, watch=5)), set(),
                             NO_REDIRECTS,
                             allow(prefixes=[("/glossary/", {"reason": "legacy children"})]))
        self.assertEqual(result["retired"], [])
        self.assertEqual([r["path"] for r in result["watch"]], ["/glossary/"])

    def test_an_entry_with_no_reason_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = pathlib.Path(tmp) / "a.yaml"
            f.write_text('retired:\n  - path: "/x/"\n  - path: "/y/"\n    reason: "stated"\n')
            got = ui.load_allowlist(f)
        self.assertIn("/y/", got["exact"])
        self.assertNotIn("/x/", got["exact"])
        self.assertEqual(len(got["problems"]), 1)

    def test_a_reasonless_entry_fails_the_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            (tmp / "inv.json").write_text(json.dumps(inventory(row("/a/"))))
            (tmp / "allow.yaml").write_text('retired:\n  - path: "/a/"\n')
            (tmp / "out").mkdir()
            outcome = ui.check(inventory_path=tmp / "inv.json", output_path=tmp / "out",
                               redirects_path=tmp / "none", allowlist_path=tmp / "allow.yaml",
                               today=dt.date(2026, 8, 17))
        self.assertTrue(any("no reason" in f for f in outcome["failures"]))

    def test_the_shipped_allowlist_gives_every_entry_a_reason(self):
        got = ui.load_allowlist()
        self.assertEqual(got["problems"], [], got["problems"])
        self.assertTrue(got["exact"] or got["prefixes"], "allowlist should be seeded")

    def test_the_shipped_allowlist_cites_evidence_and_a_date(self):
        import yaml
        data = yaml.safe_load(ui.ALLOWLIST.read_text(encoding="utf-8"))
        for entry in data["retired"] + data["equivalent_redirects"]:
            label = entry.get("path") or entry.get("prefix")
            self.assertTrue(str(entry.get("evidence", "")).strip(), f"{label} has no evidence")
            self.assertTrue(str(entry.get("decided", "")).strip(), f"{label} has no decided date")

    def test_the_shipped_allowlist_retires_the_2025_legacy_top_page(self):
        """The best URL this domain ever had is written off, with the evidence."""
        got = ui.load_allowlist()
        entry = ui._allowed_entry("/guides/css-grid-layouts-webflow-table/", got)
        self.assertIsNotNone(entry)
        self.assertIn("84 days", entry["evidence"])


class StalenessTests(unittest.TestCase):
    def test_age_is_measured_from_the_refreshed_stamp(self):
        inv = inventory()
        self.assertEqual(ui.inventory_age_days(inv, dt.date(2026, 8, 20)), 3)

    def test_a_missing_stamp_reads_as_ancient(self):
        self.assertGreater(ui.inventory_age_days({}, dt.date(2026, 8, 20)), 1000)

    def test_a_stale_inventory_fails_the_check(self):
        """A guard nobody refreshes is the failure mode this tool exists to prevent."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            (tmp / "inv.json").write_text(json.dumps(inventory(row("/a/"))))
            (tmp / "out").mkdir()
            outcome = ui.check(inventory_path=tmp / "inv.json", output_path=tmp / "out",
                               redirects_path=tmp / "none", allowlist_path=tmp / "none.yaml",
                               today=dt.date(2026, 8, 17) + dt.timedelta(days=ui.STALE_FAIL_DAYS))
        self.assertTrue(any("stale" in f for f in outcome["failures"]))

    def test_a_fresh_inventory_does_not_fail_on_staleness(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            (tmp / "inv.json").write_text(json.dumps(inventory(row("/a/", alarm=0, watch=0))))
            (tmp / "out").mkdir()
            outcome = ui.check(inventory_path=tmp / "inv.json", output_path=tmp / "out",
                               redirects_path=tmp / "none", allowlist_path=tmp / "none.yaml",
                               today=dt.date(2026, 8, 17))
        self.assertFalse(any("stale" in f for f in outcome["failures"]), outcome["failures"])

    def test_a_missing_inventory_is_a_failure_not_a_silent_pass(self):
        outcome = ui.check(inventory_path=pathlib.Path("/nonexistent-xyz.json"),
                           output_path=pathlib.Path("/nonexistent-xyz"),
                           redirects_path=pathlib.Path("/nonexistent-xyz"),
                           allowlist_path=pathlib.Path("/nonexistent-xyz.yaml"))
        self.assertTrue(any("no URL inventory" in f for f in outcome["failures"]))


class ReportingTests(unittest.TestCase):
    def _make(self, *rows, **kw):
        inv = inventory(*rows)
        built = kw.get("built", set())
        result = ui.classify(inv, built, NO_REDIRECTS, kw.get("allowed", allow()))
        result["allowlist_problems"] = []
        return {"inventory": inv, "result": result, "age_days": 0,
                "lines": ui.report(inv, result, 0)}

    def test_the_report_always_states_the_floor_caveat(self):
        """Search Console withholds low-volume pages, so no count here is a total."""
        text = "\n".join(self._make(row("/a/", alarm=1))["lines"])
        self.assertIn("floors", text)

    def test_the_report_names_the_alarm_urls(self):
        text = "\n".join(self._make(row("/gone/", alarm=7))["lines"])
        self.assertIn("/gone/", text)
        self.assertIn("ALARM", text)

    def test_a_clean_run_says_so_explicitly(self):
        text = "\n".join(self._make(row("/a/", alarm=0, watch=0),
                                      allowed=allow(exact={"/a/": {"reason": "x"}}))["lines"])
        self.assertIn("no dead URL is still earning impressions", text)

    def test_a_retired_url_still_earning_is_named_not_hidden(self):
        """An allowlist must not become the place leaks go to hide."""
        text = "\n".join(self._make(
            row("/retired/", alarm=4),
            allowed=allow(exact={"/retired/": {"reason": "deliberate"}}))["lines"])
        self.assertIn("/retired/", text)
        self.assertIn("still earned impressions", text)

    def test_summary_line_is_one_line_and_leads_with_the_alarm(self):
        line = ui.summary_line(self._make(row("/gone/", alarm=9)))
        self.assertEqual(len(line.splitlines()), 1)
        self.assertIn("ALARM", line)
        self.assertIn("floors", line)

    def test_summary_line_reports_a_missing_inventory(self):
        self.assertIn("NO INVENTORY", ui.summary_line(
            {"inventory": {}, "result": {}, "age_days": 0, "lines": []}))


class ShippedInventoryTests(unittest.TestCase):
    """The committed data file is the guard. If it is malformed the guard is not running."""

    def test_the_inventory_is_committed_and_parses(self):
        self.assertTrue(ui.INVENTORY.exists(), "planning/url-inventory.json must be committed")
        data = ui.load_inventory()
        self.assertGreater(data.get("url_count", 0), 0)
        self.assertEqual(data["url_count"], len(data["urls"]))

    def test_the_inventory_records_when_it_was_refreshed(self):
        data = ui.load_inventory()
        self.assertRegex(data.get("refreshed", ""), r"^\d{4}-\d{2}-\d{2}T")

    def test_the_inventory_records_its_span_and_windows(self):
        data = ui.load_inventory()
        self.assertRegex(data["span"]["earliest_with_data"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(data["windows"]["alarm_days"], ui.ALARM_DAYS)
        self.assertEqual(data["windows"]["watch_days"], ui.WATCH_DAYS)

    def test_the_inventory_states_the_floor_caveat_in_the_data(self):
        self.assertIn("floors", ui.load_inventory().get("caveat", ""))

    def test_the_inventory_covers_the_2025_legacy_traffic(self):
        """The whole point: the URLs the March 2026 rebuild dropped are in the record."""
        paths = {r["path"] for r in ui.load_inventory()["urls"]}
        self.assertIn("/guides/css-grid-layouts-webflow-table/", paths)

    def test_every_row_carries_the_fields_the_check_reads(self):
        for r in ui.load_inventory()["urls"]:
            for field in ("path", "impressions_total", "impressions_watch", "impressions_alarm"):
                self.assertIn(field, r, r.get("path"))


class WindowPolicyTests(unittest.TestCase):
    def test_the_alarm_window_matches_the_rest_of_the_toolchain(self):
        """28 days is the window daily_cycle.py and gsc_report.py already use."""
        self.assertEqual(ui.ALARM_DAYS, 28)

    def test_the_write_off_window_matches_the_evidence_standard(self):
        """84 days is the twelve weeks the 2025 legacy write-off was argued on."""
        self.assertEqual(ui.WATCH_DAYS, 84)

    def test_windows_end_before_the_search_console_lag(self):
        self.assertGreaterEqual(ui.GSC_LAG_DAYS, 3)

    def test_the_alarm_window_is_inside_the_write_off_window(self):
        self.assertLess(ui.ALARM_DAYS, ui.WATCH_DAYS)


class DeployGraceWindowTests(unittest.TestCase):
    """The WAITING-versus-ALARM convention this guard was asked to match.

    It landed on main from another agent while this was being built, and that version is
    kept: its discriminator is the age of the newest commit that changed something the
    build renders, so a docs-only commit does not reset the clock. These tests pin the
    behaviour the URL guard relies on rather than re-litigating the implementation.
    """

    def setUp(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import daily_cycle
        self.dc = daily_cycle

    def test_a_grace_window_exists_and_is_short(self):
        self.assertTrue(0 < self.dc.DEPLOY_GRACE_SECONDS <= 60 * 60)

    def test_a_clean_deploy_reads_as_live(self):
        self.assertEqual(self.dc._deploy_line([], [], 0), "LIVE, matches the build")

    def test_a_mismatch_inside_the_window_is_waiting_not_an_alarm(self):
        line = self.dc._deploy_line(["sitemap mismatch"], ["sitemap mismatch"], 60)
        self.assertIn("WAITING", line)
        self.assertNotIn("ALARM", line)

    def test_a_mismatch_past_the_window_is_an_alarm(self):
        line = self.dc._deploy_line(["sitemap mismatch"], [], 60 * 60)
        self.assertIn("ALARM", line)

    def test_an_unknown_commit_age_is_stated_rather_than_guessed(self):
        self.assertIn("unknown age", self.dc._deploy_line(["mismatch"], [], None))


class GuardWiringTests(unittest.TestCase):
    def test_daily_cycle_calls_the_guard_and_can_fail_on_it(self):
        source = (ROOT / "tools" / "daily_cycle.py").read_text(encoding="utf-8")
        self.assertIn("def url_inventory_check", source)
        self.assertIn("url_failures", source)
        self.assertIn("URL inventory:", source)

    def test_the_guard_runs_after_the_build_in_the_gate(self):
        """It must read the build's generated output/_redirects, not the source file."""
        source = (ROOT / "tools" / "daily_cycle.py").read_text(encoding="utf-8")
        self.assertLess(source.index('run(python, "build.py")'),
                        source.index("url_failures, _ = url_inventory_check()"))


if __name__ == "__main__":
    unittest.main()
