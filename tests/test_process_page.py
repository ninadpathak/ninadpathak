"""The process page at /technical-writing-process/.

The page is a set of scroll scenes, and everything that moves is optional: the tests hold
what a search engine, an agent or a reader without scripts gets. Every stage's full text
is in the HTML, the page states only the timings and counts Ninad confirmed, and the
figures stay inside the site's rules (no inline styles, one page-only stylesheet and
script, no library).
"""
import json
import re
import unittest
from pathlib import Path

import frontmatter

from build import SiteBuilder

REPO = Path(__file__).resolve().parent.parent
URL = "/technical-writing-process/"


def visible_text(html: str) -> str:
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    for entity, char in (("&amp;", "&"), ("&#39;", "'"), ("&quot;", '"'), ("&nbsp;", " ")):
        text = text.replace(entity, char)
    return re.sub(r" ([,.;:])", r"\1", " ".join(text.split()))


def plain(markdown: str) -> str:
    return " ".join(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", markdown).split())


class ProcessPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = SiteBuilder()
        cls.page = cls.builder.load_process_page()
        template = cls.builder.env.get_template("process.html")
        cls.html = template.render(
            site=cls.builder.config["site"], contact=cls.builder.config["contact"],
            current_page="process", build_year=2026, latest_posts=[], process=cls.page,
        )
        cls.text = visible_text(cls.html)
        cls.source = frontmatter.load(REPO / "content" / "process.md")

    def test_it_is_published_at_its_query(self):
        self.assertEqual(self.page["url"], URL)
        self.assertTrue(self.page["published"])
        for field in ("title", "seo_title", "description", "lead"):
            with self.subTest(field=field):
                self.assertIn(self.page["primary_query"], self.page[field].lower())
        self.assertIn(f'<link rel="canonical" href="https://ninadpathak.com{URL}">', self.html)

    def test_there_are_eight_stages_of_three_beats(self):
        self.assertEqual(len(self.page["stages"]), 8)
        self.assertEqual(len({stage["id"] for stage in self.page["stages"]}), 8)
        for stage in self.page["stages"]:
            with self.subTest(stage=stage["id"]):
                self.assertEqual(len(stage["beats"]), 3)

    def test_every_word_of_every_stage_is_in_the_html_without_scripts(self):
        for stage in self.page["stages"]:
            for part in [stage["title"], *stage["beats"], stage["evidence"]]:
                with self.subTest(stage=stage["id"], text=part[:40]):
                    self.assertIn(plain(part), self.text)
        for faq in self.page["faqs"]:
            with self.subTest(question=faq["question"]):
                self.assertIn(faq["question"], self.text)
                self.assertIn(faq["answer"], self.text)

    def test_each_figure_carries_a_description_and_each_stage_an_anchor(self):
        for stage in self.page["stages"]:
            with self.subTest(stage=stage["id"]):
                self.assertIn(f'<section class="pp-scene pp-n{int(stage["number"])}" id="{stage["id"]}"', self.html)
                self.assertIn(f'role="img" aria-label="{stage["alt"]}"', self.html)
                self.assertIn(f'href="#{stage["id"]}"', self.html)

    def test_reading_order_is_heading_then_beats_then_figure(self):
        for stage in self.page["stages"]:
            with self.subTest(stage=stage["id"]):
                heading = self.html.index(f'id="{stage["id"]}-title"')
                beat = self.html.index(plain(stage["beats"][0])[:30], heading)
                figure = self.html.index(f'data-figure="{stage["id"]}"')
                self.assertLess(heading, beat)
                self.assertLess(beat, figure)

    def test_figures_keep_to_the_word_budget(self):
        """tools/image-brand/GUIDELINE.md: a diagram carries at most 15 words, where a
        word is any token of two or more letters. The head band is exempt."""
        for figure in re.findall(r'<div class="pf-stage">(.*?)</div>\s*</div>\s*<div class="pf-foot">', self.html, re.S):
            words = re.findall(r"[A-Za-z]{2,}", visible_text(figure))
            with self.subTest(words=" ".join(words)):
                self.assertLessEqual(len(words), 15)

    def test_structured_data_is_valid_and_lists_the_stages(self):
        blocks = [json.loads(block) for block in
                  re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.html, re.S)]
        types = {block.get("@type"): block for block in blocks}
        items = types["WebPage"]["mainEntity"]["itemListElement"]
        self.assertEqual([item["position"] for item in items], list(range(1, 9)))
        self.assertEqual([item["name"] for item in items], [stage["title"] for stage in self.page["stages"]])
        for item, stage in zip(items, self.page["stages"]):
            self.assertEqual(item["url"], f"https://ninadpathak.com{URL}#{stage['id']}")
        answers = {q["name"]: q["acceptedAnswer"]["text"] for q in types["FAQPage"]["mainEntity"]}
        self.assertEqual(answers, {faq["question"]: faq["answer"] for faq in self.page["faqs"]})
        self.assertNotIn("HowTo", types)

    def test_copy_keeps_the_voice_rules(self):
        lowered = (self.text + " " + self.page["markdown"]).lower()
        for banned in ("hire me", "i sell", "30+ companies", "740%", "$34", "1,240%"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, lowered)
        self.assertNotIn("—", self.text)

    def test_it_states_only_the_confirmed_timings_and_counts(self):
        """Ninad's answers of 2026-11-17: brief within 24 hours, about 5 days to a draft,
        2 days for revision, 4 days later on, two review rounds at most, a paid trial."""
        for phrase in ("Within 24 hours", "about 5 days from brief to draft", "two rounds of review at most",
                       "paid trial piece", "4 days end to end", "demo account and API keys"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_results_name_their_source_and_years_and_show_no_site_search_console_figures(self):
        note = self.source["results_note"]
        self.assertIn("Semrush", note)
        for row in self.source["results"]:
            with self.subTest(client=row["client"]):
                self.assertRegex(row["period"], r"20\d\d")
                self.assertIn(f"Semrush, {row['period']}", self.html)
        self.assertNotIn("chart", self.source.metadata)
        self.assertNotRegex(self.text.lower(), r"\d[\d,]* (weekly )?impressions")

    def test_internal_links_resolve_to_built_pages(self):
        built = {URL, "/", "/articles/", "/work/", "/services/", "/about/", "/tools/", "/linter/", "/llms.txt",
                 "/ai-overviews-checker/", "/ai-crawler-checker/", "/services/ai-ready-documentation-audit/"}
        built |= {f"/work/{path.stem}/" for path in (REPO / "content" / "work").glob("*.md")}
        links = set(re.findall(r'href="(/[^"#]*)', self.html))
        links = {link for link in links if not link.startswith("/static/") and link != "/feed.xml"}
        chrome = {"/portfolio/", "/projects/", "/glossary/", "/contact/", "/terms/", "/privacy/"}
        for link in sorted(links - chrome):
            with self.subTest(link=link):
                self.assertIn(link.split("index.md")[0], built)
        self.assertIn('href="/services/#how-wed-work-together"', self.html)
        self.assertIn('id="how-wed-work-together"', self.builder.load_service_pages()[0]["content"])

    def test_the_page_loads_its_own_stylesheet_and_script_and_no_library(self):
        self.assertEqual(self.html.count('href="/static/css/process.css'), 1)
        self.assertEqual(self.html.count('src="/static/js/process.js'), 1)
        external = [src for src in re.findall(r'<script[^>]*\bsrc="([^"]+)"', self.html)
                    if not src.startswith("/static/js/") and "googletagmanager" not in src]
        self.assertEqual(external, [])
        for other in ("services.html", "post.html", "index.html", "about.html"):
            with self.subTest(template=other):
                self.assertNotIn("process.", (REPO / "templates" / other).read_text(encoding="utf-8").replace("process.html", ""))

    def test_motion_is_opt_in_and_moves_transform_and_opacity_only(self):
        css = re.sub(r"/\*.*?\*/", "", (REPO / "static" / "css" / "process.css").read_text(encoding="utf-8"), flags=re.S)
        for name, body in re.findall(r"@keyframes ([\w-]+)\s*\{((?:[^{}]*\{[^{}]*\})*)", css):
            properties = set(re.findall(r"([a-z-]+)\s*:", re.sub(r"var\([^)]*\)|calc\([^;]*", "", body)))
            with self.subTest(keyframes=name):
                self.assertLessEqual(properties, {"opacity", "transform"})
        for transition in re.findall(r"transition:\s*([^;]+);", css):
            with self.subTest(transition=transition[:40]):
                self.assertNotRegex(transition, r"\b(all|width|height|top|left|margin|padding)\b")
        # Nothing animates until the page opts in, so no script and reduced motion both
        # leave every figure finished.
        for rule in re.findall(r"([^{}]+)\{[^{}]*\banimation(?:-name|-timeline)?\s*:", css):
            selector = " ".join(rule.split())
            with self.subTest(selector=selector[:60]):
                self.assertTrue(all(".pp-live" in part or ".pp-n" in part for part in selector.split(",")), selector)
        script = self.html[self.html.index("<script data-cfasync"):]
        self.assertIn("prefers-reduced-motion: no-preference", script[:script.index("</script>")])


class ProcessPageBuildTests(unittest.TestCase):
    """What build.py writes beside the page."""

    @classmethod
    def setUpClass(cls):
        cls.builder = SiteBuilder()
        cls.page = cls.builder.load_process_page()

    def test_markdown_alternate_carries_every_stage_and_the_contact_route(self):
        text = self.builder.markdown_alternate(self.page["title"], self.page["lead"], URL, self.page["markdown"])
        for stage in self.page["stages"]:
            with self.subTest(stage=stage["id"]):
                self.assertIn(f"## {int(stage['number'])}. {stage['title']}", text)
                for beat in stage["beats"]:
                    self.assertIn(self.builder.absolute_links(beat), text)
        self.assertIn("## How an engagement starts", text)
        self.assertIn(self.builder.hire_line(), text)
        self.assertNotIn("](/", text)

    def test_other_pages_link_to_it(self):
        base = (REPO / "templates" / "base.html").read_text(encoding="utf-8")
        self.assertIn(f'<a href="{URL}" class="footer-link">Process</a>', base)
        for path in ("content/services.md", "content/about.md", "templates/work.html", "templates/services.html"):
            with self.subTest(path=path):
                self.assertIn(URL, (REPO / path).read_text(encoding="utf-8"))

    def test_the_short_address_redirects(self):
        redirects = (REPO / "static" / "_redirects").read_text(encoding="utf-8")
        self.assertIn(f"/process/ {URL} 301", redirects)

    def test_a_stage_with_a_missing_beat_stops_the_build(self):
        source = REPO / "content" / "process.md"
        original = source.read_text(encoding="utf-8")
        beat = re.search(r'      - "We talk for 30 minutes[^\n]*\n', original).group(0)
        try:
            source.write_text(original.replace(beat, ""), encoding="utf-8")
            with self.assertRaises(ValueError):
                SiteBuilder().load_process_page()
        finally:
            source.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
