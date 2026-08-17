"""Contract tests for the AI Overview citation-versus-ranking instrument.

No test reaches DataForSEO. The suite pins the distinction that decides the campaign:
the same *page* must rank and be cited. Merely sharing a domain is not overlap. It also
pins the spend gate so a refactor cannot turn a cache read into an unapproved paid call.
"""

import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import ai_overview_citations as aio  # noqa: E402


def payload(*items):
    return {"tasks": [{"result": [{"items": list(items)}]}]}


def organic(rank, url, domain="example.com"):
    return {"type": "organic", "rank_absolute": rank, "url": url,
            "domain": domain}


def overview(*references, nested=()):
    item = {"type": "ai_overview", "references": list(references)}
    if nested:
        item["items"] = [{"references": list(nested)}]
    return item


def reference(url, domain="example.com", title="Source"):
    return {"url": url, "domain": domain, "title": title}


class ParseTests(unittest.TestCase):
    def test_top_level_and_nested_references_are_deduplicated_by_url(self):
        same = reference("https://example.com/a")
        parsed = aio.parse(payload(overview(same, nested=(same, reference(
            "https://other.test/b", "other.test")))))
        self.assertTrue(parsed["overview_present"])
        self.assertEqual([c["url"] for c in parsed["citations"]], [
            "https://example.com/a", "https://other.test/b"])

    def test_no_overview_is_not_confused_with_an_empty_overview(self):
        absent = aio.parse(payload(organic(1, "https://example.com/a")))
        empty = aio.parse(payload(overview()))
        self.assertFalse(absent["overview_present"])
        self.assertTrue(empty["overview_present"])
        self.assertEqual(empty["citations"], [])


class PageIdentityTests(unittest.TestCase):
    def test_scheme_www_query_fragment_and_trailing_slash_do_not_split_a_page(self):
        self.assertEqual(
            aio.normalized_page("https://www.Example.com/a/?utm_source=x#answer"),
            "example.com/a",
        )
        self.assertEqual(aio.normalized_page("http://example.com/a"), "example.com/a")

    def test_different_paths_on_one_domain_are_not_page_overlap(self):
        parsed = aio.parse(payload(
            organic(1, "https://example.com/tool"),
            overview(reference("https://example.com/research")),
        ))
        result = aio.overlap(parsed)
        self.assertEqual(result["page_overlap_pct"], 0.0)
        self.assertEqual(result["domain_overlap_pct"], 100.0)
        self.assertEqual(result["pages_in_both"], [])
        self.assertEqual(result["cited_pages_not_ranking"], ["example.com/research"])

    def test_the_same_normalized_page_is_overlap(self):
        parsed = aio.parse(payload(
            organic("3", "http://www.example.com/guide/"),
            overview(reference("https://example.com/guide?ref=aio")),
        ))
        result = aio.overlap(parsed)
        self.assertEqual(result["page_overlap_pct"], 100.0)
        self.assertEqual(result["pages_in_both"], ["example.com/guide"])

    def test_invalid_and_out_of_range_ranks_are_not_top_ten(self):
        parsed = aio.parse(payload(
            organic(None, "https://example.com/a"),
            organic("unknown", "https://example.com/b"),
            organic(11, "https://example.com/c"),
            overview(reference("https://example.com/a")),
        ))
        self.assertEqual(aio.overlap(parsed)["ranked_top_n_pages"], 0)

    def test_report_names_page_and_domain_overlap_separately(self):
        parsed = aio.parse(payload(
            organic(1, "https://example.com/tool"),
            overview(reference("https://example.com/research")),
        ))
        text = aio.report("query", parsed, aio.overlap(parsed))
        self.assertIn("Page overlap: 0.0%", text)
        self.assertIn("Same-domain overlap is 100.0%", text)
        self.assertNotIn("Pages ranking AND cited", text)


class CacheIdentityTests(unittest.TestCase):
    def test_slug_collisions_do_not_share_a_cache_file(self):
        self.assertNotEqual(
            aio.cache_path("llms.txt", "United States"),
            aio.cache_path("llms txt", "United States"),
        )

    def test_location_is_part_of_the_cache_identity(self):
        self.assertNotEqual(
            aio.cache_path("docs as code", "United States"),
            aio.cache_path("docs as code", "India"),
        )


class CliSpendGateTests(unittest.TestCase):
    def run_main(self, argv, cache, credentials=True):
        env = ({"DATAFORSEO_LOGIN": "login", "DATAFORSEO_PASSWORD": "password"}
               if credentials else {})
        stdout = io.StringIO()
        with mock.patch.object(aio, "CACHE", cache), \
                mock.patch.object(aio, "CALL_LOG", cache / "calls.md"), \
                mock.patch.object(sys, "argv", ["tool"] + argv), \
                mock.patch.dict(os.environ, env, clear=True), \
                contextlib.redirect_stdout(stdout):
            code = aio.main()
        return code, stdout.getvalue()

    def test_missing_credentials_costs_only_uncached_keywords_and_never_fetches(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(aio, "fetch") as fetch:
            cache = pathlib.Path(tmp)
            watchlist = cache / "watchlist.txt"
            watchlist.write_text("already\nnew\n", encoding="utf-8")
            with mock.patch.object(aio, "CACHE", cache):
                aio.cache_path("already", "United States").write_text("{}", encoding="utf-8")
            code, text = self.run_main(
                ["--file", str(watchlist)], cache, credentials=False)
            self.assertEqual(code, 0)
            self.assertIn("2 keyword(s); 1 uncached", text)
            fetch.assert_not_called()

    def test_uncached_request_without_decision_is_refused_before_fetch(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(aio, "fetch") as fetch:
            code, text = self.run_main(["--keyword", "query"], pathlib.Path(tmp))
            self.assertEqual(code, 1)
            self.assertIn("--decision is required before spending", text)
            fetch.assert_not_called()

    def test_cached_result_needs_no_spend_decision(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(aio, "fetch") as fetch:
            cache = pathlib.Path(tmp)
            with mock.patch.object(aio, "CACHE", cache):
                path = aio.cache_path("query", "United States")
                path.write_text(json.dumps(payload(
                    organic(1, "https://example.com/a"),
                    overview(reference("https://example.com/a")),
                )), encoding="utf-8")
            code, text = self.run_main(["--keyword", "query"], cache)
            self.assertEqual(code, 0)
            self.assertIn("Page overlap: 100.0%", text)
            fetch.assert_not_called()

    def test_dry_run_with_credentials_never_fetches(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(aio, "fetch") as fetch:
            code, text = self.run_main(
                ["--keyword", "query", "--dry-run"], pathlib.Path(tmp))
            self.assertEqual(code, 0)
            self.assertIn("1 uncached", text)
            fetch.assert_not_called()

    def test_approved_fetch_is_cached_and_logged_once(self):
        fixture = payload(
            organic(1, "https://example.com/a"),
            overview(reference("https://example.com/a")),
        )
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
                aio, "fetch", return_value=fixture) as fetch:
            cache = pathlib.Path(tmp)
            code, text = self.run_main(
                ["--keyword", "query", "--decision", "choose the owner"], cache)
            self.assertEqual(code, 0)
            self.assertIn("Page overlap: 100.0%", text)
            fetch.assert_called_once_with(
                "query", "United States", ("login", "password"))
            with mock.patch.object(aio, "CACHE", cache):
                self.assertTrue(aio.cache_path("query", "United States").is_file())
            log = (cache / "calls.md").read_text(encoding="utf-8")
            self.assertIn("$0.004", log)
            self.assertIn("decision: choose the owner", log)

    def test_strict_mode_fails_an_empty_api_response(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
                aio, "fetch", return_value={"tasks": []}):
            code, text = self.run_main([
                "--keyword", "query", "--decision", "choose the owner", "--strict"
            ], pathlib.Path(tmp))
            self.assertEqual(code, 1)
            self.assertIn("EMPTY: no organic results and no Overview", text)
            self.assertIn("FAILED: 1 keyword(s) unresolved", text)


if __name__ == "__main__":
    unittest.main()
