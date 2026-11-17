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


FIRST_PERSON = re.compile(r"\b(?:I|I['’](?:ve|m|d|ll)|[Mm]y|me)\b")
# The banned form: a bio line that names the author and describes him from outside,
# such as "Technical writer Ninad Pathak writes ...".
THIRD_PERSON_BIO = re.compile(
    r"(?i)\bNinad\b|\bPathak\b|\b(?:he|his|him|himself)\b|\bthe (?:author|writer)\b"
)


def note_text(note: str) -> str:
    return re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", note)


class WorkNoteVoiceRuleTests(unittest.TestCase):
    def test_first_person_notes_pass(self):
        for value in (
            "I wrote Mem0's guide to vector embeddings, and the guide is in my portfolio.",
            "At Mem0 I ran a team of 13 writers.",
            "I've written about agent tools for Firecrawl.",
            "This page is about headings. My portfolio links to published work.",
        ):
            with self.subTest(value=value):
                self.assertRegex(value, FIRST_PERSON)
                self.assertNotRegex(value, THIRD_PERSON_BIO)

    def test_third_person_bio_lines_fail(self):
        for value in (
            "Technical writer Ninad Pathak writes technical documentation for developer products.",
            "Ninad Pathak's developer content covers the first query.",
            "The author documents agent API errors for developers.",
            "A technical writer who explains his process in my portfolio.",
        ):
            with self.subTest(value=value):
                self.assertRegex(value, THIRD_PERSON_BIO)

    def test_a_note_with_no_first_person_fails(self):
        for value in (
            "Reference pages and tutorials serve different tasks for developers.",
            "Documentation that explains what the software decides.",
        ):
            with self.subTest(value=value):
                self.assertNotRegex(value, FIRST_PERSON)


class PublishedWorkNoteTests(unittest.TestCase):
    def test_published_notes_are_present_unique_short_and_first_person(self):
        notes = []
        for path in Path("content/posts").glob("*.md"):
            post = frontmatter.load(path)
            if post.get("status") != "published":
                continue
            with self.subTest(path=path):
                note = post.get("work_note")
                self.assertIsInstance(note, str)
                self.assertTrue(render_work_note(note))
                text = note_text(note)
                self.assertLessEqual(len(text.split()), 50)
                self.assertGreaterEqual(len(text.split()), 15)
                self.assertRegex(text, FIRST_PERSON)
                self.assertNotRegex(text, THIRD_PERSON_BIO)
                notes.append(note)
        self.assertTrue(notes)
        self.assertEqual(len(notes), len(set(notes)))

if __name__ == "__main__":
    unittest.main()
