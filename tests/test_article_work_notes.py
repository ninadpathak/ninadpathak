import re
import unittest
from pathlib import Path

import frontmatter

from build import SiteBuilder, render_work_note


class WorkNoteRenderingTests(unittest.TestCase):
    def test_absent_note_is_optional_for_legacy_content(self):
        self.assertEqual(render_work_note(None), "")
        self.assertEqual(render_work_note(""), "")

    def test_one_internal_link_renders_inline(self):
        self.assertEqual(
            render_work_note("Write [the guide](/portfolio/) with me."),
            'Write <a href="/portfolio/">the guide</a> with me.',
        )

    def test_plain_text_and_link_label_are_escaped(self):
        rendered = render_work_note('<script>x</script> [A & <B>](/contact/) "quoted"')
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("A &amp; &lt;B&gt;", rendered)
        self.assertIn("&quot;quoted&quot;", rendered)

    def test_unapproved_destinations_and_multiple_links_are_rejected(self):
        for value in (
            "[click](javascript:alert)",
            "[click](https://example.com/)",
            "[click](/portfolio/evil)",
            "[one](/portfolio/) [two](/contact/)",
            "unlinked copy",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                render_work_note(value)

    def test_multiline_and_nonstrings_are_rejected(self):
        for value in ([], 1, "First\n[second](/contact/)"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                render_work_note(value)

    def test_template_places_note_before_body_without_changing_first_paragraph(self):
        builder = SiteBuilder()
        post = builder.load_posts()[0]
        post["content"] = "<p>Original opening.</p>"
        post["work_note"] = render_work_note("A [writing service](/portfolio/).")
        html = builder.env.get_template("post.html").render(
            post=post, site=builder.config["site"], contact=builder.config["contact"],
            related=[], latest_posts=[], build_year=2026,
        )
        self.assertEqual(html.count('class="article-work-note"'), 1)
        self.assertLess(html.index('class="article-work-note"'), html.index('class="post-content"'))
        self.assertRegex(html, r'class="post-content">\s*<p>Original opening\.</p>')
        post.pop("work_note")
        legacy = builder.env.get_template("post.html").render(
            post=post, site=builder.config["site"], contact=builder.config["contact"],
            related=[], latest_posts=[], build_year=2026,
        )
        self.assertNotIn('class="article-work-note"', legacy)
        self.assertIn("Original opening.", legacy)


class PublishedWorkNoteTests(unittest.TestCase):
    def test_published_notes_are_present_unique_and_short(self):
        notes = []
        for path in Path("content/posts").glob("*.md"):
            post = frontmatter.load(path)
            if post.get("status") != "published":
                continue
            with self.subTest(path=path):
                note = post.get("work_note")
                self.assertIsInstance(note, str)
                self.assertTrue(render_work_note(note))
                text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", note)
                self.assertLessEqual(len(text.split()), 50)
                self.assertGreaterEqual(len(text.split()), 15)
                notes.append(note)
        self.assertTrue(notes)
        self.assertEqual(len(notes), len(set(notes)))


if __name__ == "__main__":
    unittest.main()
