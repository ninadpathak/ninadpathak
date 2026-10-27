"""lastmod tracks when a page really changed, and every date on the page agrees.

The sitemap, Article dateModified and the visible "Updated" line all read frontmatter
`updated`, which no edit ever bumped: /articles/speculative-decoding/ said 2026-03-07
after its video landed on 2026-10-27. Dates now come from content/lastmod.json,
which lastmod.py computes from git history where full history exists (Cloudflare
Pages clones shallow, so the build cannot ask git itself).
"""
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import lastmod  # noqa: E402
from build import SiteBuilder  # noqa: E402

OUTPUT = ROOT / "output"


def git(cwd, *args, date=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", *args],
                   cwd=cwd, env=env, check=True, capture_output=True)


class SourceHashTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = os.getcwd()
        os.chdir(self.tmp.name)
        self.addCleanup(os.chdir, self.cwd)
        pathlib.Path("content/posts").mkdir(parents=True)
        pathlib.Path("content/diagrams/demo").mkdir(parents=True)
        pathlib.Path("content/posts/demo.md").write_text("---\ntitle: Demo\n---\nBody\n")
        pathlib.Path("content/diagrams/demo/figure.mmd").write_text("graph LR\n")
        pathlib.Path("content/diagrams/demo/og.mmd").write_text("card\n")

    def sources(self, video=None):
        return lastmod.source_paths(pathlib.Path("content/posts/demo.md"), "demo", video)

    def test_figure_sources_count_and_share_cards_do_not(self):
        names = [p.name for p in self.sources()]
        self.assertEqual(names, ["figure.mmd", "demo.md"])

    def test_video_folders_count_when_the_post_declares_one(self):
        pathlib.Path("content/videos/clip").mkdir(parents=True)
        pathlib.Path("content/videos/clip/video.yaml").write_text("name: x\n")
        pathlib.Path("static/videos/clip").mkdir(parents=True)
        pathlib.Path("static/videos/clip/captions.vtt").write_text("WEBVTT\n")
        names = {p.as_posix() for p in self.sources(video="clip")}
        self.assertIn("content/videos/clip/video.yaml", names)
        self.assertIn("static/videos/clip/captions.vtt", names)

    def test_hash_moves_with_content_and_not_with_a_share_card(self):
        before = lastmod.sources_hash(self.sources())
        pathlib.Path("content/diagrams/demo/og.mmd").write_text("restyled card\n")
        self.assertEqual(lastmod.sources_hash(self.sources()), before)
        pathlib.Path("content/diagrams/demo/figure.mmd").write_text("graph TD\n")
        self.assertNotEqual(lastmod.sources_hash(self.sources()), before)


class GitDatingTests(unittest.TestCase):
    """Runs against a throwaway repository with fixed commit dates."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = pathlib.Path(self.tmp.name)
        self.old_root = lastmod.ROOT
        lastmod.ROOT = self.repo
        self.addCleanup(setattr, lastmod, "ROOT", self.old_root)
        self.cwd = os.getcwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, self.cwd)
        git(self.repo, "init", "-q")
        pathlib.Path("content/posts").mkdir(parents=True)
        pathlib.Path("content/posts/old-name.md").write_text("first\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "add", date="2026-03-07T10:00:00+05:30")
        pathlib.Path("content/posts/old-name.md").write_text("first, edited\n")
        git(self.repo, "commit", "-qam", "edit", date="2026-05-01T10:00:00+05:30")
        git(self.repo, "mv", "content/posts/old-name.md", "content/posts/new-name.md")
        git(self.repo, "commit", "-qm", "rename", date="2026-10-04T01:43:00+05:30")

    def test_a_pure_rename_does_not_date_the_page(self):
        path = pathlib.Path("content/posts/new-name.md")
        self.assertEqual(lastmod.file_last_changed(path), "2026-05-01")

    def test_an_edit_after_the_rename_does(self):
        path = pathlib.Path("content/posts/new-name.md")
        path.write_text("first, edited again\n")
        git(self.repo, "commit", "-qam", "edit", date="2026-10-27T00:30:00+05:30")
        # The committer's local date, not UTC (which would still be 10-26).
        self.assertEqual(lastmod.file_last_changed(path), "2026-10-27")

    def test_uncommitted_edits_are_dated_today(self):
        path = pathlib.Path("content/posts/new-name.md")
        path.write_text("work in progress\n")
        self.assertEqual(lastmod.date_for([path], "2026-11-02"), "2026-11-02")

    def test_newest_source_wins(self):
        figure = pathlib.Path("content/diagrams/new-name/figure.mmd")
        figure.parent.mkdir(parents=True)
        figure.write_text("graph LR\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "figure", date="2026-10-20T12:00:00+05:30")
        self.assertEqual(
            lastmod.last_commit_date([pathlib.Path("content/posts/new-name.md"), figure]),
            "2026-10-20")


class ResolveUpdatedTests(unittest.TestCase):
    """The build trusts a manifest entry only while its sources hash matches."""

    def setUp(self):
        self.cwd = os.getcwd()
        os.chdir(ROOT)
        self.addCleanup(os.chdir, self.cwd)
        self.builder = SiteBuilder()
        self.path = ROOT / "content" / "posts" / "speculative-decoding.md"
        import frontmatter
        self.meta = frontmatter.load(self.path).metadata
        self.sources = lastmod.source_paths(pathlib.Path("content/posts/speculative-decoding.md"),
                                            "speculative-decoding", self.meta.get("video"))

    def resolve(self, entry):
        self.builder.lastmod_manifest = {"speculative-decoding": entry} if entry else {}
        self.builder.stale_lastmod = []
        return self.builder.resolve_updated(pathlib.Path("content/posts/speculative-decoding.md"),
                                            "speculative-decoding", self.meta)

    def test_a_matching_entry_sets_the_date(self):
        entry = {"lastmod": "2026-10-27", "sources": lastmod.sources_hash(self.sources)}
        self.assertEqual(self.resolve(entry), dt.date(2026, 10, 27))
        self.assertEqual(self.builder.stale_lastmod, [])

    def test_a_stale_entry_falls_back_to_frontmatter_and_is_reported(self):
        entry = {"lastmod": "2026-10-27", "sources": "not-the-current-hash"}
        floor = lastmod_floor(self.meta)
        self.assertEqual(self.resolve(entry), floor)
        self.assertEqual(self.builder.stale_lastmod, ["speculative-decoding"])

    def test_never_earlier_than_the_publish_date(self):
        entry = {"lastmod": "2020-01-01", "sources": lastmod.sources_hash(self.sources)}
        self.assertEqual(self.resolve(entry), lastmod_floor(self.meta))


def lastmod_floor(meta):
    from build import latest
    return latest([meta.get("date"), meta.get("updated")])


class ManifestIsCurrentTests(unittest.TestCase):
    def test_every_post_has_a_current_entry(self):
        cwd = os.getcwd()
        os.chdir(ROOT)
        try:
            problems = lastmod.stale_entries(lastmod.load_manifest(), lastmod.discover())
        finally:
            os.chdir(cwd)
        self.assertEqual(problems, [], "run `python3 lastmod.py` and commit content/lastmod.json")


class BuiltDatesAgreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (OUTPUT / "sitemap.xml").is_file():
            raise unittest.SkipTest("run `python build.py` first — these read the built site")
        xml = (OUTPUT / "sitemap.xml").read_text(encoding="utf-8")
        cls.lastmods = dict(re.findall(
            r"<loc>https://ninadpathak\.com([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", xml))

    def test_sitemap_date_modified_and_visible_updated_agree(self):
        for page in (OUTPUT / "articles").glob("*/index.html"):
            html = page.read_text(encoding="utf-8")
            modified = re.search(r'"dateModified": "([^"]+)"', html)
            if not modified:
                continue  # a category archive, not an article
            path = f"/articles/{page.parent.name}/"
            self.assertEqual(self.lastmods[path], modified.group(1), path)
            visible = re.search(r'Updated <time datetime="([^"]+)"', html)
            if visible:
                self.assertEqual(visible.group(1), modified.group(1), path)

    def test_speculative_decoding_carries_its_video_date(self):
        self.assertGreaterEqual(self.lastmods["/articles/speculative-decoding/"], "2026-10-27")

    def test_home_and_sections_are_the_newest_of_their_articles(self):
        articles = {p: d for p, d in self.lastmods.items()
                    if (OUTPUT / p.strip("/") / "index.html").is_file()
                    and '"dateModified"' in (OUTPUT / p.strip("/") / "index.html").read_text(encoding="utf-8")}
        newest = max(articles.values())
        self.assertEqual(self.lastmods["/"], newest)
        self.assertEqual(self.lastmods["/articles/"], newest)


if __name__ == "__main__":
    unittest.main()
