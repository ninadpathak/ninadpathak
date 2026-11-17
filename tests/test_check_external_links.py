"""The link checker's judgments, tested without the network.

The checker itself is a hand-run tool. These tests cover the parts that decide what a response
means, and they prove the build and the test suite never reach for the network through it.
"""
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_external_links", ROOT / "tools/check_external_links.py")
links = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(links)

CAPTURE = "https://web.archive.org/web/20260813143601/https://graphite.com/blog/code-review-best-practices"


class ClassifyTests(unittest.TestCase):
    def test_a_live_article_is_ok_even_after_a_redirect_that_keeps_the_slug(self):
        url = "https://mem0.ai/blog/claude-code-memory"
        self.assertEqual(links.classify(url, 200, url)[0], "ok")
        self.assertEqual(
            links.classify(url, 200, "https://mem0.ai/library/coding-agents/claude-code-memory")[0], "ok")

    def test_a_renamed_slug_that_contains_the_old_one_is_the_same_article(self):
        url = "https://mem0.ai/blog/long-term-memory-ai-agents"
        self.assertEqual(links.classify(url, 200, "https://mem0.ai/library/agent-memory/long-term-memory")[0], "ok")
        self.assertEqual(links.classify(url, 200, "https://mem0.ai/")[0], "moved")

    def test_a_404_and_a_soft_404_are_dead(self):
        url = "https://graphite.dev/blog/stacked-prs"
        self.assertEqual(links.classify(url, 404, url)[0], "dead")
        self.assertEqual(links.classify(url, 410, url)[0], "dead")
        self.assertEqual(links.classify(url, 200, url, title="Page not found")[0], "dead")
        self.assertEqual(links.classify(url, 200, url, heading="404 !!")[0], "dead")

    def test_a_redirect_that_drops_the_slug_is_moved(self):
        url = "https://opencomputer.dev/guides/python-sandbox"
        verdict, reason = links.classify(url, 200, "https://opencomputer.dev/compare/")
        self.assertEqual(verdict, "moved")
        self.assertIn("/compare/", reason)

    def test_a_refusal_is_never_reported_as_dead(self):
        url = "https://linkedin.com/in/ninadwrites"
        for status in (0, 401, 403, 429, 999, 500, 504):
            with self.subTest(status=status):
                self.assertEqual(links.classify(url, status, url)[0], "blocked")

    def test_a_capture_must_answer_at_its_own_timestamp(self):
        self.assertEqual(links.classify(CAPTURE, 200, CAPTURE)[0], "ok")
        other = CAPTURE.replace("20260813143601", "20260407232030")
        self.assertEqual(links.classify(CAPTURE, 200, other)[0], "moved")
        self.assertEqual(links.classify(CAPTURE, 404, CAPTURE)[0], "dead")


class CollectTests(unittest.TestCase):
    def test_collect_skips_original_url_template_expressions_and_non_portfolio_hosts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "content").mkdir()
            (root / "templates").mkdir()
            (root / "content/portfolio.yaml").write_text(
                f'entries:\n  - title: "A"\n    url: "{CAPTURE}"\n'
                '    original_url: "https://graphite.dev/blog/code-review-best-practices"\n'
                '  - title: "B"\n    url: "https://centus.com/blog/yaml-translation"\n', encoding="utf-8")
            (root / "templates/base.html").write_text(
                '<link href="https://fonts.googleapis.com/css2"><a href="https://x.com/ninadwrites">X</a>'
                '<a href="https://ninadpathak.com/work/">w</a>', encoding="utf-8")
            found = links.collect(root)
        self.assertEqual(sorted(found), sorted([
            CAPTURE, "https://centus.com/blog/yaml-translation", "https://x.com/ninadwrites"]))
        self.assertEqual(found[CAPTURE], ["content/portfolio.yaml"])

    def test_the_repo_has_links_to_check_and_every_archive_link_is_timestamped(self):
        found = links.collect()
        self.assertGreater(len(found), 40)
        for url in found:
            if "web.archive.org" in url:
                with self.subTest(url=url):
                    self.assertRegex(url, r"^https://web\.archive\.org/web/\d{14}/https://")


class IsolationTests(unittest.TestCase):
    def test_the_build_and_ci_do_not_run_the_checker(self):
        for path in ("build.py", "seo_audit.py", ".github/workflows/quality.yml"):
            with self.subTest(path=path):
                self.assertNotIn("check_external_links", (ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
