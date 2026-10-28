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


# A VP8X header for a 1344x756 image: enough for the magic and size checks.
TINY_WEBP = b"RIFF" + (22).to_bytes(4, "little") + b"WEBPVP8X" + (10).to_bytes(4, "little") + bytes(4) + (1343).to_bytes(3, "little") + (755).to_bytes(3, "little")


def write_video(root: Path, slug: str, **overrides) -> None:
    meta = {
        "name": "A film", "description": "What it shows.", "upload_date": "2026-10-27T14:25:00+05:30",
        "duration_seconds": 75, "width": 1920, "height": 1080, "file": "film.mp4",
        "poster": "poster.png", "poster_webp": "poster.webp", "captions": "captions.vtt", "transcript": "Spoken words.",
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
    (static / "poster.webp").write_bytes(TINY_WEBP)
    (static / "captions.vtt").write_text("WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nSpoken words.\n", encoding="utf-8")


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


class VideoReviewFixTests(unittest.TestCase):
    """Codex review of feat-article-video: each test failed on 0c64b28a/a776cbcd."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        patcher = mock.patch.object(build, "ROOT", self.tmp)
        patcher.start()
        self.addCleanup(patcher.stop)

    def reset(self):
        for name in ("content", "static", "outside"):
            shutil.rmtree(self.tmp / name, ignore_errors=True)

    # (2) asset paths stay inside static/videos/<slug>/
    def test_asset_paths_must_stay_in_the_slug_directory(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        (outside / "film.mp4").write_bytes(b"\0")
        for value in (str(outside / "film.mp4"), "../../outside/film.mp4", "sub/film.mp4"):
            with self.subTest(file=value):
                self.reset()
                outside.mkdir()
                (outside / "film.mp4").write_bytes(b"\0")
                write_video(self.tmp, "demo", file=value)
                with self.assertRaises(ValueError):
                    load_video("demo")
        self.reset()
        outside.mkdir()
        (outside / "film.mp4").write_bytes(b"\0")
        write_video(self.tmp, "demo", file="link.mp4")
        (self.tmp / "static/videos/demo/link.mp4").symlink_to(outside / "film.mp4")
        with self.assertRaisesRegex(ValueError, "link.mp4"):
            load_video("demo")

    # (3) values are validated
    def test_upload_date_needs_iso_time_and_zone(self):
        for value in ("not-a-date", "2026-10-27", "2026-10-27T14:25:00", "2026-13-01T00:00:00+05:30"):
            with self.subTest(upload_date=value):
                self.reset()
                write_video(self.tmp, "demo", upload_date=value)
                with self.assertRaisesRegex(ValueError, "upload_date"):
                    load_video("demo")
        self.reset()
        write_video(self.tmp, "demo", upload_date="2026-10-27T14:25:00+05:30")
        self.assertEqual(load_video("demo")["upload_date"], "2026-10-27T14:25:00+05:30")

    def test_dimensions_and_duration_must_be_positive_integers(self):
        for field, value in (("width", 0), ("height", -1080), ("width", "wide"), ("width", 19.5),
                             ("duration_seconds", -1), ("duration_seconds", 0), ("height", True)):
            with self.subTest(field=field, value=value):
                self.reset()
                write_video(self.tmp, "demo", **{field: value})
                with self.assertRaisesRegex(ValueError, field):
                    load_video("demo")

    def test_captions_need_ordered_cues_inside_the_video(self):
        bad = {
            "no cues": "WEBVTT\n\ndefinitely not captions\n",
            "end before start": "WEBVTT\n\n00:00:05.000 --> 00:00:04.000\nHi\n",
            "out of order": "WEBVTT\n\n00:00:05.000 --> 00:00:06.000\nB\n\n00:00:01.000 --> 00:00:02.000\nA\n",
            "past the end": "WEBVTT\n\n00:01:20.000 --> 00:01:30.000\nLate\n",
        }
        for name, vtt in bad.items():
            with self.subTest(case=name):
                self.reset()
                write_video(self.tmp, "demo")
                (self.tmp / "static/videos/demo/captions.vtt").write_text(vtt, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "captions"):
                    load_video("demo")


class PosterTests(unittest.TestCase):
    """Poster follow-up: the player shows a small WebP and the page preloads it."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        patcher = mock.patch.object(build, "ROOT", self.tmp)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_poster_webp_is_required_a_webp_and_within_budget(self):
        write_video(self.tmp, "demo", poster_webp=None)
        with self.assertRaisesRegex(ValueError, "poster_webp"):
            load_video("demo")
        shutil.rmtree(self.tmp / "content"); shutil.rmtree(self.tmp / "static")
        write_video(self.tmp, "demo")
        (self.tmp / "static/videos/demo/poster.webp").write_bytes(b"\x89PNG not a webp")
        with self.assertRaisesRegex(ValueError, "not a WebP"):
            load_video("demo")
        (self.tmp / "static/videos/demo/poster.webp").write_bytes(TINY_WEBP + bytes(41 * 1024))
        with self.assertRaisesRegex(ValueError, "budget"):
            load_video("demo")


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
                poster = subprocess.run(
                    [sys.executable, "tools/build_video_poster.py", slug, "--check"],
                    capture_output=True, text=True,
                )
                self.assertEqual(poster.returncode, 0, poster.stderr)

    def test_template_renders_player_track_transcript_and_nested_video_object(self):
        builder = SiteBuilder()
        post = next(p for p in builder.load_posts() if p["slug"] == "speculative-decoding")
        html = builder.env.get_template("post.html").render(
            post=post, site=builder.config["site"], contact=builder.config["contact"],
            related=[], latest_posts=[], build_year=2026,
        )
        self.assertRegex(html, r'<video controls preload="none" playsinline width="1920" height="1080" poster="/static/videos/speculative-decoding/poster.webp"')
        # The film burns condensed captions into the picture, so the verbatim track is
        # offered in the player's captions menu but not switched on over them.
        self.assertIn('<track kind="captions" src="/static/videos/speculative-decoding/captions.vtt" srclang="en" label="English">', html)
        self.assertLess(html.index("<video"), html.index('class="post-content"'))
        self.assertIn("<summary>Transcript</summary>", html)
        self.assertIn("figures.css", html)
        # The player shows the WebP, the head preloads it at high priority, and the
        # VideoObject names the same WebP so search sees one thumbnail URL.
        self.assertIn('poster="/static/videos/speculative-decoding/poster.webp"', html)
        self.assertIn('<link rel="preload" as="image" href="/static/videos/speculative-decoding/poster.webp" type="image/webp" fetchpriority="high">', html)
        self.assertLess(html.index('rel="preload" as="image"'), html.index("</head>"))
        articles = [json.loads(block) for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        article = next(block for block in articles if block.get("@type") == "TechArticle")
        video = article["video"]
        self.assertEqual(video["@type"], "VideoObject")
        self.assertEqual(video["duration"], "PT40S")
        self.assertEqual(video["thumbnailUrl"], "https://ninadpathak.com/static/videos/speculative-decoding/poster.webp")
        self.assertTrue(video["contentUrl"].endswith("/static/videos/speculative-decoding/speculative-decoding.mp4"))
        for field in ("name", "description", "thumbnailUrl", "uploadDate", "transcript"):
            self.assertTrue(video[field], field)

    # Codex fix (1): the transcript is escaped (failed on a776cbcd)
    def test_transcript_markup_is_escaped(self):
        builder = SiteBuilder()
        post = next(p for p in builder.load_posts() if p["slug"] == "speculative-decoding")
        post = dict(post, video=dict(post["video"], transcript='Use the <video> element & "quote".'))
        html = builder.env.get_template("post.html").render(
            post=post, site=builder.config["site"], contact=builder.config["contact"],
            related=[], latest_posts=[], build_year=2026,
        )
        self.assertIn("Use the &lt;video&gt; element &amp;", html)
        self.assertEqual(html.count("<video"), 1)

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


class WrittenCaptionTests(unittest.TestCase):
    """Captions show the script's written words, timed by the words the voice said."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_video_captions", Path(__file__).resolve().parents[1] / "tools/build_video_captions.py")
        self.captions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.captions)

    def test_voiced_file_name_takes_the_span_of_its_spoken_words(self):
        line = {"text": "My CLAUDE.md starts with @AGENTS.md.", "words": [
            {"w": "My", "start": 0.0, "end": 0.2}, {"w": "Claude", "start": 0.2, "end": 0.5},
            {"w": "dot", "start": 0.5, "end": 0.6}, {"w": "MD", "start": 0.6, "end": 0.9},
            {"w": "starts", "start": 0.9, "end": 1.2}, {"w": "with", "start": 1.2, "end": 1.4},
            {"w": "at", "start": 1.4, "end": 1.5}, {"w": "agents", "start": 1.5, "end": 1.8},
            {"w": "dot", "start": 1.8, "end": 1.9}, {"w": "MD.", "start": 1.9, "end": 2.2}]}
        timed = self.captions.written_words(line)
        self.assertEqual([w["w"] for w in timed], ["My", "CLAUDE.md", "starts", "with", "@AGENTS.md."])
        self.assertEqual((timed[1]["start"], timed[1]["end"]), (0.2, 0.9))
        self.assertEqual((timed[4]["start"], timed[4]["end"]), (1.4, 2.2))

    def test_line_whose_text_matches_its_words_is_unchanged(self):
        words = [{"w": "Same", "start": 0.0, "end": 0.3}, {"w": "words.", "start": 0.3, "end": 0.6}]
        self.assertIs(self.captions.written_words({"text": "Same words.", "words": words}), words)
        self.assertIs(self.captions.written_words({"words": words}), words)

    def test_written_word_the_voice_never_said_fails(self):
        line = {"text": "Two extra words.", "words": [{"w": "Words.", "start": 0.0, "end": 0.4}]}
        with self.assertRaisesRegex(ValueError, "did not say"):
            self.captions.written_words(line)


class CaptionClauseTests(unittest.TestCase):
    """Short trailing fragments join the clause before them, and no clause is lost."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_video_captions", Path(__file__).resolve().parents[1] / "tools/build_video_captions.py")
        self.captions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.captions)

    def words(self, text):
        return [{"w": w, "start": float(i), "end": i + 0.5} for i, w in enumerate(text.split())]

    def test_short_last_fragment_joins_the_clause_before_it(self):
        # The agent-memory-types line: the first clause was overwritten by the merged last two.
        groups = self.captions.clauses(self.words(
            "An agent kept events in memory, so asking what changed returned edits by topic, not time."))
        self.assertEqual([" ".join(w["w"] for w in g) for g in groups], [
            "An agent kept events in memory,",
            "so asking what changed returned edits by topic, not time.",
        ])

    def test_two_clauses_with_a_short_tail_become_one(self):
        groups = self.captions.clauses(self.words("It keeps what it agrees with, every time."))
        self.assertEqual([" ".join(w["w"] for w in g) for g in groups], ["It keeps what it agrees with, every time."])
