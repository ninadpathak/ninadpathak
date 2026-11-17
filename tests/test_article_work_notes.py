import re
import unittest
from pathlib import Path

import frontmatter
import yaml

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

    def test_services_pages_are_allowed_destinations(self):
        published = ["/services/"] + [f"/services/{path.stem}/" for path in sorted(Path("content/services").glob("*.md"))
                                      if frontmatter.load(path).get("status") == "published"]
        self.assertGreater(len(published), 1)
        for url in published:
            with self.subTest(url=url):
                self.assertEqual(render_work_note(f"I take this on as [a service]({url})."),
                                 f'I take this on as <a href="{url}">a service</a>.')

    def test_a_services_link_must_name_a_published_page(self):
        for value in (
            "[hire me](/services/no-such-page/)",
            "[hire me](/services/ai-ready-documentation-audit)",
            "[hire me](/services/ai-ready-documentation-audit/extra/)",
            "[hire me](/services/../contact/)",
            "[hire me](/services/#pricing)",
            "[one](/services/) [two](/contact/)",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                render_work_note(value)

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
# A first-person introduction, "I'm Ninad Pathak" or "I am Ninad Pathak", is the one place
# the name may appear, and SELF_INTRODUCTION removes it before the bio check runs.
SELF_INTRODUCTION = re.compile(r"\bI(?:['’]m| am) Ninad Pathak\b(?!['’]s)")
THIRD_PERSON_BIO = re.compile(
    r"(?i)\bNinad\b|\bPathak\b|\b(?:he|she|his|hers|him|himself|herself)\b"
    r"|\b(?:writer|author|freelancer|creator|strategist|consultant|owner)(?: \w+){0,3} "
    r"(?:writes|wrote|creates|documents|documented|explains|develops|plans|edits|reviews|builds|turns"
    r"|connects|takes|took|has (?:written|documented|worked))\b"
)
LINK = re.compile(r"\[([^]]+)\]\([^)]+\)")


def note_text(note: str) -> str:
    return LINK.sub(r"\1", note)


def note_outside_link(note: str) -> str:
    """The note with its link label removed. First person has to appear here, because
    nearly every note links "my portfolio" and the label alone would satisfy the rule."""
    return LINK.sub(" ", note)


# What a note may offer and where it may point. These rules fail closed: a note passes only
# when it says "freelance", carries a hiring phrase, links a services page or the contact
# page, names no company or person outside ALLOWED_NAMES, and gives no figure.
SELLING = re.compile(r"(?i)\b(?:sell|sells|selling|sold|seller|sellers|sale|sales)\b")
HIRING = re.compile(r"(?i)\bhire\b|\bwork with me\b|\bget in touch\b|\b(?:tell|ask|talk to) me\b")
NOTE_TARGET = re.compile(r"\]\((?:/contact/|/services/(?:[a-z0-9-]+/)?)\)")
# Work no services page offers. A first-person verb followed in the same sentence by one
# of these subjects is an offer the site cannot back.
UNBACKED_OFFER = re.compile(
    r"(?i)\bI(?:['’]ll)?(?: also)? (?:run|do|offer|write|handle|take on|provide|manage)\b[^.?!]*"
    r"\b(?:accessibility|SEO|design docs?|runbooks?)\b"
)
FIGURE = re.compile(r"(?i)\d|\byears?\b")
ALLOWED_NAMES = {"I", "Ninad", "Pathak", "AI", "API", "LLM", "SEO", "README", "OpenAPI"}


def unknown_names(text: str) -> list:
    """Capitalised words that do not start a sentence and are not on the allowed list."""
    found = []
    for match in re.finditer(r"\b[A-Z][A-Za-z]*\b", text):
        starts_sentence = match.start() == 0 or re.search(r"[.?!:] $", text[:match.start()])
        if not starts_sentence and match.group(0) not in ALLOWED_NAMES:
            found.append(match.group(0))
    return found


def offer_problems(note: str) -> list:
    problems = []
    text = note_text(note)
    if SELLING.search(text):
        problems.append("a form of sell")
    if "freelance" not in text.lower():
        problems.append("does not say freelance")
    if not HIRING.search(text):
        problems.append("no hiring phrase")
    if not NOTE_TARGET.search(note):
        problems.append("link is not a services page or the contact page")
    if UNBACKED_OFFER.search(text):
        problems.append("offers work no services page backs")
    if FIGURE.search(text):
        problems.append("a figure or a count of years")
    if unknown_names(text):
        problems.append("names outside the allowed list: " + ", ".join(unknown_names(text)))
    return problems
def voice_problems(note: str) -> list:
    problems = []
    if not FIRST_PERSON.search(note_outside_link(note)):
        problems.append("no first person outside the link label")
    if THIRD_PERSON_BIO.search(SELF_INTRODUCTION.sub("I am", note_text(note), count=1)):
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
            "I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. [See how I work](/services/).",
            "Handed the docs along with everything else? I am Ninad Pathak, a freelance technical writer, and [you can hire me](/services/).",
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
            "I'm Ninad Pathak. Ninad writes technical documentation, and [the work is here](/services/).",
            "I'm Ninad Pathak, and I'm Ninad Pathak again in [the same note](/services/).",
            "I work with Ninad Pathak, who writes documentation. [Get in touch](/contact/).",
            "The author of this site documents developer products, as [my page](/services/) shows.",
            "A freelance technical writer for AI companies wrote this post, in my view. [Hire me](/services/).",
            "This site's writer has documented fifty products, and my inbox is open. [Hire me](/services/).",
            "I'm Ninad Pathak's biggest fan, and I say so often. [Hire me](/services/).",
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


class WorkNoteOfferRuleTests(unittest.TestCase):
    GOOD = "I'm Ninad Pathak, a freelance technical writer, and I run the product before I write about it. [Hire me](/services/)."

    def test_a_backed_offer_passes(self):
        self.assertEqual(offer_problems(self.GOOD), [])
        self.assertEqual(voice_problems(self.GOOD), [])

    def test_unbacked_or_unhirable_notes_fail(self):
        cases = {
            "I'm Ninad Pathak, a freelance technical writer, and I run accessibility audits and SEO campaigns. [Hire me](/services/).": "offers work no services page backs",
            "I'm Ninad Pathak, a freelance technical writer. I write runbooks for your team. [Hire me](/services/).": "offers work no services page backs",
            "I'm Ninad Pathak, a freelance writer with documentation for Stripe and Google behind me. [Hire me](/services/).": "names outside the allowed list: Stripe, Google",
            "I'm Ninad Pathak, a freelance writer for twenty years. [Hire me](/services/).": "a figure or a count of years",
            "I'm Ninad Pathak, a freelance writer, and I sold documentation packages. [Hire me](/services/).": "a form of sell",
            "I'm Ninad Pathak, a freelance writer and a seller of documentation. [Hire me](/services/).": "a form of sell",
            "I'm Ninad Pathak, a freelance writer, and my sales pitch is short. [Hire me](/services/).": "a form of sell",
            "I'm Ninad Pathak, a freelance writer. [Hire me](/portfolio/).": "link is not a services page or the contact page",
            "I'm Ninad Pathak, and I write for AI companies. [See what I do](/services/).": "does not say freelance",
            "I'm Ninad Pathak, a freelance technical writer. [See what I do](/services/).": "no hiring phrase",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertIn(expected, offer_problems(value))


class PublishedWorkNoteTests(unittest.TestCase):
    # Topics whose posts are about work clients hire for. Each of their notes is written
    # for its post, so none may repeat anywhere on the site.
    WRITTEN_PER_POST = {"technical-documentation", "developer-experience", "ai-search-optimization"}
    MOST_POSTS_PER_NOTE = 7

    def test_published_notes_are_present_short_first_person_and_backed(self):
        self.assertTrue(self.published_notes())

    def published_notes(self):
        notes = {}
        for path in Path("content/posts").glob("*.md"):
            post = frontmatter.load(path)
            if post.get("status") != "published":
                continue
            with self.subTest(path=path):
                note = post.get("work_note")
                self.assertIsInstance(note, str)
                self.assertTrue(render_work_note(note))
                text = note_text(note)
                self.assertLessEqual(len(text.split()), 70)
                self.assertGreaterEqual(len(text.split()), 15)
                self.assertEqual(voice_problems(note), [])
                self.assertEqual(offer_problems(note), [])
                notes[post.get("slug") or path.stem] = (str(post.get("category")), note)
        return notes

    def test_notes_differ_from_the_next_post_on_the_topic_page(self):
        """A pitch may repeat across the site, as a company's pitch does on its blog. The
        reader meets posts in the order a topic page lists them, so that order decides
        which notes are neighbours."""
        notes = self.published_notes()
        pillars = sorted(Path("content/pillars").glob("*.yaml"))
        self.assertTrue(pillars)
        listed = set()
        for pillar in pillars:
            spokes = [spoke["post"] for section in yaml.safe_load(pillar.read_text())["sections"]
                      for spoke in section.get("spokes", []) if "post" in spoke]
            listed.update(spokes)
            for earlier, later in zip(spokes, spokes[1:]):
                self.assertIn(earlier, notes)
                self.assertIn(later, notes)
                self.assertNotEqual(notes[earlier][1], notes[later][1],
                                    f"{earlier} and {later} sit together on {pillar.stem} and share a note")
        self.assertEqual(listed, set(notes), "every published post must sit on a topic page")

    def test_notes_written_for_a_post_are_unique_and_no_note_is_overused(self):
        notes = self.published_notes()
        uses = {}
        for slug, (category, note) in notes.items():
            uses.setdefault(note, []).append((slug, category))
        for note, posts in uses.items():
            self.assertLessEqual(len(posts), self.MOST_POSTS_PER_NOTE, note)
            if len(posts) > 1:
                shared = [slug for slug, category in posts if category in self.WRITTEN_PER_POST]
                self.assertEqual(shared, [], f"a note written for one post is reused: {note}")


if __name__ == "__main__":
    unittest.main()
