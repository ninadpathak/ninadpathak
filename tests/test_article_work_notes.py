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


# A first-person subject or possessive: "I wrote", "I've", "I'm", "my", "me". A bare capital I
# is not enough, so "part I" and "disk I/O" do not count.
FIRST_PERSON = re.compile(
    r"(?<![Pp]art )(?<![Pp]hase )(?<![Tt]ype )\bI(?:['’](?:ve|m|d|ll)\b| (?=[a-z]))|\b[Mm]y\b|\bme\b"
)
# The banned form is a bio line that describes the author from outside, such as
# "Technical writer Ninad Pathak writes ...". The name, third-person pronouns for a
# person, and a job title followed by a third-person verb all mark it. "The author of a
# design doc" and "the writer who reviews a draft" are ordinary nouns and stay allowed.
THIRD_PERSON_BIO = re.compile(
    r"(?i)\bNinad\b|\bPathak\b|\b(?:he|she|his|hers|him|himself|herself)\b"
    r"|\b(?:writer|creator|strategist|consultant|owner)(?: \w+){0,2} "
    r"(?:writes|creates|documents|explains|develops|plans|edits|reviews|builds|turns|connects)\b"
)
LINK = re.compile(r"\[([^]]+)\]\([^)]+\)")


def note_text(note: str) -> str:
    return LINK.sub(r"\1", note)


def note_outside_link(note: str) -> str:
    """The note with its link label removed. First person has to appear here, because
    nearly every note links "my portfolio" and the label alone would satisfy the rule."""
    return LINK.sub(" ", note)


def voice_problems(note: str) -> list:
    problems = []
    if not FIRST_PERSON.search(note_outside_link(note)):
        problems.append("no first person outside the link label")
    if THIRD_PERSON_BIO.search(note_text(note)):
        problems.append("third-person bio wording")
    return problems


class WorkNoteVoiceRuleTests(unittest.TestCase):
    def test_first_person_notes_pass(self):
        for value in (
            "I wrote Firecrawl's roundup of semantic search APIs, and [the roundup is in my portfolio](/portfolio/).",
            "At Mem0 I ran a team of 13 writers. [My portfolio](/portfolio/) has the case study.",
            "I've written about agent tools for Firecrawl. [Those guides](/portfolio/) are online.",
            "My rule for headings fits in three sentences. [The portfolio](/portfolio/) has examples.",
            "I wrote this template so the author of a design doc argues with the proposal before review. [My portfolio](/portfolio/) has more.",
            "I wrote this page for the writer who has to review an engineer's draft. [My portfolio](/portfolio/) has more.",
        ):
            with self.subTest(value=value):
                self.assertEqual(voice_problems(value), [])

    def test_third_person_bio_lines_fail(self):
        for value in (
            "Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for developer products.",
            "I agree, and [Ninad Pathak](/portfolio/)'s developer content covers the first query.",
            "This site's owner writes technical documentation for developer products, and I link it from [my portfolio](/portfolio/).",
            "I know that she writes technical documentation, and her work is in [my portfolio](/portfolio/).",
            "A technical writer who explains his process, as I do in [my portfolio](/portfolio/).",
        ):
            with self.subTest(value=value):
                self.assertIn("third-person bio wording", voice_problems(value))

    def test_first_person_in_the_link_label_alone_fails(self):
        for value in (
            "A freelance technical writer with eight years of developer content for Firecrawl. See [my portfolio](/portfolio/) for the published work.",
            "This page is about headings. [My portfolio](/portfolio/) links to published work.",
            "Reference pages and tutorials serve different tasks for developers. [Get in touch](/contact/).",
            "Developers will find that part I of this page covers disk I/O. [Get in touch](/contact/) to hear more about it.",
        ):
            with self.subTest(value=value):
                self.assertIn("no first person outside the link label", voice_problems(value))


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
                self.assertEqual(voice_problems(note), [])
                notes.append(note)
        self.assertTrue(notes)
        self.assertEqual(len(notes), len(set(notes)))


if __name__ == "__main__":
    unittest.main()
