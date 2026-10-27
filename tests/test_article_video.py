import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import frontmatter

import build
from build import SiteBuilder, load_video


def write_video(root: Path, slug: str, **overrides) -> None:
    meta = {
        "name": "A film", "description": "What it shows.", "upload_date": "2026-10-27",
        "duration_seconds": 75, "width": 1920, "height": 1080, "file": "film.mp4",
        "poster": "poster.png", "captions": "captions.vtt", "transcript": "Spoken words.",
        "line_offsets": {"L1": 0.0},
    }
    meta.update(overrides)
    (root / "content" / "videos" / slug).mkdir(parents=True)
    (root / "content" / "videos" / slug / "video.yaml").write_text(
        "\n".join(f"{key}: {json.dumps(value)}" for key, value in meta.items() if value is not None),
        encoding="utf-8",
    )
    static = root / "static" / "videos" / slug
    static.mkdir(parents=True)
    (static / "film.mp4").write_bytes(b"\0")
    (static / "poster.png").write_bytes(b"\0")
    (static / "captions.vtt").write_text("WEBVTT\n", encoding="utf-8")


class LoadVideoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        patcher = mock.patch.object(build, "ROOT", self.tmp)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_no_video_is_optional(self):
        self.assertIsNone(load_video(None))
        self.assertIsNone(load_video(""))

    def test_resolves_urls_and_iso_duration(self):
        write_video(self.tmp, "demo")
        video = load_video("demo")
        self.assertEqual(video["src"], "/static/videos/demo/film.mp4")
        self.assertEqual(video["captions"], "/static/videos/demo/captions.vtt")
        self.assertEqual(video["duration_iso"], "PT1M15S")

    def test_missing_metadata_field_fails_the_build(self):
        write_video(self.tmp, "demo", transcript=None)
        with self.assertRaisesRegex(ValueError, "transcript"):
            load_video("demo")

    def test_missing_file_or_bad_captions_fails_the_build(self):
        write_video(self.tmp, "demo")
        (self.tmp / "static/videos/demo/film.mp4").unlink()
        with self.assertRaisesRegex(ValueError, "film.mp4"):
            load_video("demo")
        shutil.rmtree(self.tmp / "content")
        shutil.rmtree(self.tmp / "static")
        write_video(self.tmp, "demo")
        (self.tmp / "static/videos/demo/captions.vtt").write_text("not vtt", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "WebVTT"):
            load_video("demo")

    def test_unknown_or_unsafe_slug_fails(self):
        for value in ("missing", "../etc", "Bad Slug", 3):
            with self.subTest(value=value), self.assertRaises(ValueError):
                load_video(value)


class PublishedVideoTests(unittest.TestCase):
    def test_every_declared_video_resolves_and_its_captions_are_current(self):
        for path in Path("content/posts").glob("*.md"):
            slug = frontmatter.load(path).get("video")
            if not slug:
                continue
            with self.subTest(post=path.name):
                self.assertIsNotNone(load_video(slug))
                result = subprocess.run(
                    [sys.executable, "tools/build_video_captions.py", slug, "--check"],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_template_renders_player_track_transcript_and_nested_video_object(self):
        builder = SiteBuilder()
        post = next(p for p in builder.load_posts() if p["slug"] == "speculative-decoding")
        html = builder.env.get_template("post.html").render(
            post=post, site=builder.config["site"], contact=builder.config["contact"],
            related=[], latest_posts=[], build_year=2026,
        )
        self.assertRegex(html, r'<video controls preload="none" playsinline width="1920" height="1080" poster="/static/videos/speculative-decoding/poster.png"')
        # The film burns condensed captions into the picture, so the verbatim track is
        # offered in the player's captions menu but not switched on over them.
        self.assertIn('<track kind="captions" src="/static/videos/speculative-decoding/captions.vtt" srclang="en" label="English">', html)
        self.assertLess(html.index("<video"), html.index('class="post-content"'))
        self.assertIn("<summary>Transcript</summary>", html)
        self.assertIn("figures.css", html)
        articles = [json.loads(block) for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        article = next(block for block in articles if block.get("@type") == "TechArticle")
        video = article["video"]
        self.assertEqual(video["@type"], "VideoObject")
        self.assertEqual(video["duration"], "PT40S")
        self.assertTrue(video["contentUrl"].endswith("/static/videos/speculative-decoding/speculative-decoding.mp4"))
        for field in ("name", "description", "thumbnailUrl", "uploadDate", "transcript"):
            self.assertTrue(video[field], field)

    def test_page_without_video_has_no_player_or_video_object(self):
        builder = SiteBuilder()
        post = next(p for p in builder.load_posts() if not p["video"])
        html = builder.env.get_template("post.html").render(
            post=post, site=builder.config["site"], contact=builder.config["contact"],
            related=[], latest_posts=[], build_year=2026,
        )
        self.assertNotIn("<video", html)
        self.assertNotIn("VideoObject", html)


if __name__ == "__main__":
    unittest.main()
