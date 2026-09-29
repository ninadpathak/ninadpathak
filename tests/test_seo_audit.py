"""Redirect and internal-link checks in seo_audit.py, run against a throwaway output/.

Cloudflare Pages matches a _redirects source exactly and 308s a slashless page path to
its trailing-slash form. Fifteen aliases were written only as /old/ and 404ed as /old,
and eight article links paid a 308 hop to reach /work/. These tests prove the audit
fails on each shape, and stays quiet on a correct rule set.
"""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import seo_audit

PAGE = """<!DOCTYPE html><html><head><title>T</title>
<meta name="description" content="D"><meta property="og:url" content="https://ninadpathak.com{path}">
<link rel="canonical" href="https://ninadpathak.com{path}"></head>
<body><h1>H</h1>{body}</body></html>"""


class RedirectAndLinkAuditTests(unittest.TestCase):
    def audit(self, redirects, home_body=""):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "index.html").write_text(PAGE.format(path="/", body=home_body))
            (output / "work").mkdir()
            (output / "work" / "index.html").write_text(PAGE.format(path="/work/", body=""))
            (output / "sitemap.xml").write_text(
                '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                "<url><loc>https://ninadpathak.com/</loc></url>"
                "<url><loc>https://ninadpathak.com/work/</loc></url></urlset>"
            )
            (output / "robots.txt").write_text("Sitemap: https://ninadpathak.com/sitemap.xml\n")
            (output / "llms.txt").write_text("# Site\n")
            (output / "feed.xml").write_text("<rss/>")
            (output / "_routes.json").write_text('{"version": 1, "include": ["/api/*"]}')
            (output / "_redirects").write_text(redirects)
            stdout = io.StringIO()
            with mock.patch.object(seo_audit, "OUTPUT", output), contextlib.redirect_stdout(stdout):
                status = seo_audit.main()
        return status, stdout.getvalue()

    def test_correct_rules_and_links_pass(self):
        status, report = self.audit(
            "/old /work/ 301\n/old/ /work/ 301\n",
            home_body='<a href="/work/">Work</a><a href="/feed.xml">RSS</a>',
        )
        self.assertEqual(status, 0, report)

    def test_slash_only_source_fails(self):
        status, report = self.audit("/old/ /work/ 301\n")
        self.assertEqual(status, 1)
        self.assertIn("/old/ has no rule for /old", report)

    def test_redirect_chain_and_missing_target_fail(self):
        status, report = self.audit(
            "/a /b/ 301\n/a/ /b/ 301\n/b /work/ 301\n/b/ /work/ 301\n/c /gone/ 301\n/c/ /gone/ 301\n"
        )
        self.assertEqual(status, 1)
        self.assertIn("redirect chain /a -> /b/ -> /work/", report)
        self.assertIn("/c redirects to a missing page: /gone/", report)

    def test_source_shadowing_a_generated_page_fails(self):
        status, report = self.audit("/work /old/ 301\n/work/ /old/ 301\n")
        self.assertEqual(status, 1)
        self.assertIn("/work/ shadows a generated page", report)

    def test_slashless_and_redirected_internal_links_fail(self):
        status, report = self.audit(
            "/old /work/ 301\n/old/ /work/ 301\n",
            home_body='<a href="/work">Work</a><a href="/old/">Old</a>',
        )
        self.assertEqual(status, 1)
        self.assertIn("internal link lacks its trailing slash and 308s: /work", report)
        self.assertIn("internal link goes through a redirect: /old/ -> /work/", report)


if __name__ == "__main__":
    unittest.main()
