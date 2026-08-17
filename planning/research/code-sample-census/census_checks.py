from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

STUDY_DIR = Path(__file__).resolve().parent
ROOT = STUDY_DIR.parents[2]
MODULE_PATH = STUDY_DIR / "extract_code_samples.py"
SPEC = importlib.util.spec_from_file_location("extract_code_samples", MODULE_PATH)
extractor = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = extractor
SPEC.loader.exec_module(extractor)


def page(body: str, generator: str | None = None) -> str:
    meta = f'<meta name="generator" content="{generator}">' if generator else ""
    return f"<!doctype html><html><head>{meta}</head><body>{body}</body></html>"


class GeneratorDetectionTests(unittest.TestCase):
    def test_declared_generators(self):
        cases = {
            "Sphinx 8.2.3": "sphinx",
            "mkdocs-1.6.1, mkdocs-material-9.5.47": "mkdocs",
            "Docusaurus v3": "docusaurus",
            "Mintlify": "mintlify",
            "Astro v7.1.3, Starlight v0.41.4": "starlight",
        }
        for declaration, expected in cases.items():
            with self.subTest(declaration=declaration):
                soup = extractor.BeautifulSoup(page("", declaration), "html.parser")
                self.assertEqual(extractor.detect_generator(soup), expected)

    def test_sphinx_asset_marker(self):
        html = '<script src="../_static/documentation_options.js"></script>'
        soup = extractor.BeautifulSoup(page(html), "html.parser")
        self.assertEqual(extractor.detect_generator(soup), "sphinx")

    def test_unknown_is_not_guessed(self):
        html = page('<pre><code class="language-python">x = 1</code></pre>')
        generator, samples, counts = extractor.iter_samples(html, "https://example.test/")
        self.assertEqual(generator, "unknown")
        self.assertEqual(samples, [])
        self.assertEqual(counts, {"pre_blocks": 1, "included": 0, "excluded": 1})


class ExtractionTests(unittest.TestCase):
    def test_sphinx_ancestor_class_is_language_evidence(self):
        html = page(
            '<div class="highlight-python notranslate"><div class="highlight"><pre>x = 1\n</pre></div></div>',
            "Sphinx 8",
        )
        _, samples, counts = extractor.iter_samples(html, "https://example.test/docs")
        self.assertEqual(counts["included"], 1)
        self.assertEqual(samples[0].kind, "python")
        self.assertEqual(samples[0].evidence, "class:highlight-python")
        self.assertTrue(samples[0].parses)

    def test_requests_style_default_highlight_uses_console_prompt(self):
        html = page(
            '<div class="highlight-default"><div class="highlight"><pre>'
            '&gt;&gt;&gt; import requests\n&gt;&gt;&gt; requests.__name__\n\'requests\'\n'
            "</pre></div></div>",
            "Sphinx 8",
        )
        _, samples, _ = extractor.iter_samples(html, "https://example.test/quickstart")
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].kind, "pycon")
        self.assertEqual(samples[0].evidence, "prompt:>>>")
        self.assertTrue(samples[0].parses, samples[0].parse_error)

    def test_console_output_is_not_parsed_as_source(self):
        source = ">>> value = {\"ok\": True}\n>>> value\n{'ok': True}\n"
        self.assertEqual(extractor.parse_pycon(source), (True, None))

    def test_mkdocs_prompt_is_included_without_language_class(self):
        html = page('<div class="highlight"><pre>&gt;&gt;&gt; import httpx\n</pre></div>', "mkdocs-1.6.1")
        _, samples, _ = extractor.iter_samples(html, "https://example.test/")
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].kind, "pycon")

    def test_starlight_explicit_python_code(self):
        html = page(
            '<pre class="astro-token"><code class="language-python"><span>x = 1</span>\n<span>print(x)</span></code></pre>',
            "Astro v7, Starlight v0.41",
        )
        _, samples, _ = extractor.iter_samples(html, "https://example.test/")
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].source, "x = 1\nprint(x)\n")
        self.assertTrue(samples[0].parses)

    def test_shell_and_output_blocks_are_excluded(self):
        html = page(
            '<div class="highlight-default"><pre>$ pip install thing\n</pre></div>'
            '<div class="highlight-json"><pre>{"ok": true}\n</pre></div>',
            "Sphinx 8",
        )
        _, samples, counts = extractor.iter_samples(html, "https://example.test/")
        self.assertEqual(samples, [])
        self.assertEqual(counts["excluded"], 2)

    def test_syntax_failure_remains_unclassified(self):
        html = page(
            '<div class="highlight-python"><pre>if True print("broken")\n</pre></div>',
            "Sphinx 8",
        )
        _, samples, _ = extractor.iter_samples(html, "https://example.test/")
        self.assertFalse(samples[0].parses)
        self.assertIn("SyntaxError", samples[0].parse_error)
        self.assertIsNone(samples[0].audit_classification)

    def test_overlapping_language_evidence_emits_one_block(self):
        html = page(
            '<div class="highlight-python"><pre><code class="language-python">x = 1\n</code></pre></div>',
            "Sphinx 8",
        )
        _, samples, _ = extractor.iter_samples(html, "https://example.test/")
        self.assertEqual(len(samples), 1)

    def test_identifiers_are_stable_and_content_sensitive(self):
        first = page('<div class="highlight-python"><pre>x = 1\n</pre></div>', "Sphinx 8")
        changed = page('<div class="highlight-python"><pre>x = 2\n</pre></div>', "Sphinx 8")
        _, a, _ = extractor.iter_samples(first, "https://example.test/")
        _, b, _ = extractor.iter_samples(first, "https://example.test/")
        _, c, _ = extractor.iter_samples(changed, "https://example.test/")
        self.assertEqual(a[0].block_id, b[0].block_id)
        self.assertNotEqual(a[0].block_id, c[0].block_id)


class SampleFrameTests(unittest.TestCase):
    def test_query_uses_inclusive_n_day_window(self):
        module_path = STUDY_DIR / "freeze_sample_frame.py"
        spec = importlib.util.spec_from_file_location("freeze_sample_frame", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        query = module.build_query(module.date(2026, 8, 16), 30, 100)
        self.assertIn("2026-07-18", query)
        self.assertIn("2026-08-16", query)
        self.assertIn("LIMIT 100", query)
        self.assertIn("project ASC", query)


class DocumentationResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module_path = STUDY_DIR / "resolve_docs_urls.py"
        spec = importlib.util.spec_from_file_location("resolve_docs_urls", module_path)
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def test_selection_priority_is_deterministic(self):
        urls = {
            "API Docs": "https://example.test/api/",
            "Docs": "https://example.test/docs/",
            "Documentation": "https://example.test/documentation/",
        }
        selected = self.module.choose_docs_url(urls)
        self.assertEqual(selected["label"], "Documentation")
        self.assertEqual(selected["priority"], 0)
        self.assertEqual(selected["candidate_count"], 3)

    def test_normalizes_punctuation_and_case(self):
        selected = self.module.choose_docs_url({"Project Documentation": "https://example.test/"})
        self.assertEqual(selected["normalized_label"], "project documentation")
        self.assertEqual(selected["priority"], 2)

    def test_homepage_and_invalid_urls_are_not_fallbacks(self):
        urls = {"Homepage": "https://example.test/", "Docs": "javascript:alert(1)"}
        self.assertIsNone(self.module.choose_docs_url(urls))

    def test_candidate_order_does_not_depend_on_mapping_order(self):
        a = {"API Docs": "https://b.test/", "User Docs": "https://a.test/"}
        b = dict(reversed(list(a.items())))
        self.assertEqual(self.module.choose_docs_url(a), self.module.choose_docs_url(b))

    def test_docs_rtd_wins_without_selecting_changelog(self):
        selected = self.module.choose_docs_url(
            {
                "Docs: Changelog": "https://example.test/changes/",
                "Docs: RTD": "https://example.test/docs/",
            }
        )
        self.assertEqual(selected["label"], "Docs: RTD")
        self.assertEqual(selected["priority"], 3)
        self.assertEqual(selected["candidate_count"], 1)

    def test_only_negative_docs_labels_do_not_resolve(self):
        self.assertIsNone(self.module.choose_docs_url({"Docs: Changelog": "https://example.test/changes/"}))

    def test_homepage_rejects_code_hosts(self):
        self.assertIsNone(self.module.choose_homepage({"Homepage": "https://github.com/acme/pkg"}))
        self.assertEqual(
            self.module.choose_homepage({"Homepage": "https://docs.example.test/pkg"}),
            "https://docs.example.test/pkg",
        )

    def test_github_repository_is_normalized_to_root(self):
        urls = {
            "Homepage": "https://github.com/acme/pkg/tree/main/python",
            "Source": "https://github.com/acme/pkg.git",
        }
        self.assertEqual(self.module.choose_github_repo(urls), "https://github.com/acme/pkg")

    def test_non_github_source_is_not_a_repository_candidate(self):
        self.assertIsNone(self.module.choose_github_repo({"Source": "https://gitlab.com/acme/pkg"}))


if __name__ == "__main__":
    unittest.main()
