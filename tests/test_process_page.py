"""The process page at /technical-writing-process/.

The page follows one docs page the way a code change ships, as eight scenes. Everything
that moves is optional: these tests hold what a search engine, an agent or a reader
without scripts gets. Every word of every scene is in the HTML, the page states only the
timings and counts Ninad confirmed, the terminal shows only output that was produced by
a real run, and motion is opted into by one line in the head.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

import frontmatter

from build import SiteBuilder

REPO = Path(__file__).resolve().parent.parent
URL = "/technical-writing-process/"
REPRO = REPO / "planning" / "research" / "process-page-repro-2026-11"


def visible_text(html: str) -> str:
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    for entity, char in (("&amp;", "&"), ("&#39;", "'"), ("&quot;", '"'), ("&nbsp;", " "), ("&gt;", ">"), ("&lt;", "<"), ("&#34;", '"')):
        text = text.replace(entity, char)
    return re.sub(r" ([,.;:]|'s\b)", r"\1", " ".join(text.split()))


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
        for field in ("title", "seo_title", "description"):
            with self.subTest(field=field):
                self.assertIn(self.page["primary_query"], self.page[field].lower())
        self.assertIn(f"<h1>{self.page['title']}</h1>", self.html)
        self.assertIn(f'<link rel="canonical" href="https://ninadpathak.com{URL}">', self.html)

    def test_the_stages_are_the_steps_a_change_ships_through(self):
        self.assertEqual([stage["label"] for stage in self.page["stages"]],
                         ["Issue", "Spec", "Repro", "Diff", "Checks", "Review", "Deploy", "Metrics"])
        for stage in self.page["stages"]:
            with self.subTest(stage=stage["id"]):
                self.assertEqual(len(stage["beats"]), 3)

    def test_every_word_of_every_scene_is_in_the_html_without_scripts(self):
        for part in (self.page["tagline"], self.page["lead"]):
            self.assertIn(part, self.text)
        for stage in self.page["stages"]:
            for part in [stage["title"], *stage["beats"], *stage["object"]]:
                with self.subTest(stage=stage["id"], text=part[:40]):
                    self.assertIn(" ".join(plain(part).split()), self.text)
            if stage.get("quote"):
                self.assertIn(stage["quote"], self.text)
                self.assertIn(stage["quote_by"], self.text)
        for faq in self.page["faqs"]:
            with self.subTest(question=faq["question"]):
                self.assertIn(faq["question"], self.text)
                self.assertIn(faq["answer"], self.text)

    def test_each_scene_has_an_anchor_a_heading_and_a_described_object(self):
        for stage in self.page["stages"]:
            with self.subTest(stage=stage["id"]):
                self.assertRegex(self.html, rf'<section class="pp-scene[^"]*" id="{stage["id"]}"')
                self.assertIn(f'<h2 class="pp-head" id="{stage["id"]}-title">{stage["title"]}</h2>', self.html)
                self.assertIn(f'aria-label="{stage["alt"]}"', self.html)
                self.assertIn(f'href="#{stage["id"]}"', self.html)

    def test_reading_order_is_heading_then_object_then_captions(self):
        for stage in self.page["stages"]:
            with self.subTest(stage=stage["id"]):
                heading = self.html.index(f'id="{stage["id"]}-title"')
                thing = self.html.index(f'aria-label="{stage["alt"]}"')
                caption = self.html.index(plain(stage["beats"][0])[:30], heading)
                self.assertLess(heading, thing)
                self.assertLess(thing, caption)

    def test_the_terminal_shows_only_what_a_real_run_printed(self):
        """Every terminal line on the page is a command in the repro folder's README or a
        line of its recorded transcript."""
        transcript = (REPRO / "transcript.txt").read_text(encoding="utf-8")
        readme = (REPRO / "README.md").read_text(encoding="utf-8")
        repro = next(stage for stage in self.page["stages"] if stage["id"] == "repro")
        for line in repro["object"][1:]:
            with self.subTest(line=line):
                if line.startswith("$ npm"):
                    self.assertIn(line[2:], readme)
                else:
                    self.assertIn(line, transcript)
        for name in ("plurals.mjs", "locales/ar.json", "locales-fixed/ar.json"):
            self.assertTrue((REPRO / name).exists(), name)

    def test_the_example_is_labelled_and_never_passed_off_as_a_call_quote(self):
        self.assertIn(self.page["example_label"], self.text)
        self.assertIn(f'href="{self.page["example_url"]}"', self.html)
        self.assertTrue(self.page["example_label"].startswith("example:"))
        issue = self.page["stages"][0]
        self.assertNotRegex(" ".join(issue["beats"]).lower(), r"react-i18next|plurals")

    def test_the_shipping_frame_is_stated_as_a_comparison_and_claims_no_client_ci(self):
        self.assertIn("though some teams get it as a Google Doc", self.page["lead"])
        checks = next(stage for stage in self.page["stages"] if stage["id"] == "checks")
        self.assertIn("this site's checks", checks["object"])
        self.assertIn("On this site those are scripts", checks["beats"][1])
        self.assertIn("On this site, the review of 17 November 2026", checks["beats"][2])
        self.assertNotRegex(self.text.lower(), r"your (ci|pipeline) runs")

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
        for banned in ("hire me", "i sell", "30+ companies", "740%", "$34", "1,240%", "i start by", "goes live",
                       "found by people", "whatsapp"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, lowered)
        self.assertNotIn("—", self.text)

    def test_it_states_only_the_confirmed_timings_and_counts(self):
        """Ninad's answers of 2026-11-17: spec within 24 hours, about 5 days to a draft,
        about 2 for revision, 4 days later on, never a third review round, a paid trial."""
        for phrase in ("within 24 hours of the call", "about 5 days from the spec", "It never takes a third round",
                       "Revisions take about 2 days", "The first piece is a paid trial", "comes down to 4 days",
                       "a demo account, API keys and an account with real data in it"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_statements_about_this_sites_loop_say_so(self):
        metrics = next(stage for stage in self.page["stages"] if stage["id"] == "metrics")
        for beat in metrics["beats"][1:]:
            with self.subTest(beat=beat[:40]):
                self.assertIn("this site", beat.lower())
        answer = next(faq["answer"] for faq in self.page["faqs"] if "measure" in faq["question"].lower())
        self.assertTrue(answer.startswith("On this site"))

    def test_results_name_their_source_and_years_and_show_no_site_search_console_figures(self):
        self.assertIn("Semrush", self.source["results_note"])
        for row in self.source["results"]:
            with self.subTest(client=row["client"]):
                self.assertRegex(row["period"], r"20\d\d")
                self.assertIn(f"Semrush, {row['period']}", self.html)
        self.assertNotRegex(self.text.lower(), r"\d[\d,.]*\s+(?:weekly |daily |monthly )?(?:impressions|clicks)")
        self.assertNotRegex(self.text.lower(), r"(?:impressions|clicks|position)\s+(?:of|at|was|were|is)\s+\d")

    def test_internal_links_resolve_to_built_pages(self):
        built = {URL, "/", "/articles/", "/work/", "/services/", "/about/", "/tools/", "/llms.txt", "/ai-overviews-checker/"}
        built |= {f"/work/{path.stem}/" for path in (REPO / "content" / "work").glob("*.md")}
        links = set(re.findall(r'href="(/[^"#]*)', self.html))
        links = {link for link in links if not link.startswith("/static/") and link != "/feed.xml"}
        chrome = {"/portfolio/", "/projects/", "/glossary/", "/contact/", "/terms/", "/privacy/"}
        for link in sorted(links - chrome):
            with self.subTest(link=link):
                self.assertIn(link.split("index.md")[0], built)

    def test_libraries_load_on_this_page_only_and_are_the_approved_three(self):
        scripts = [src.split("?")[0] for src in re.findall(r'<script[^>]*\bsrc="(/static/js/[^"]+)"', self.html)]
        self.assertEqual(scripts, ["/static/js/vendor/gsap.min.js", "/static/js/vendor/ScrollTrigger.min.js",
                                   "/static/js/vendor/SplitText.min.js", "/static/js/process.js", "/static/js/main.js"])
        self.assertEqual(self.html.count('href="/static/css/process.css'), 1)
        external = [src for src in re.findall(r'<script[^>]*\bsrc="(https?://[^"]+)"', self.html) if "googletagmanager" not in src]
        self.assertEqual(external, [])
        for path in sorted((REPO / "templates").glob("*.html")):
            if path.name != "process.html":
                with self.subTest(template=path.name):
                    self.assertNotIn("vendor/gsap", path.read_text(encoding="utf-8"))
        for name in ("gsap", "ScrollTrigger", "SplitText"):
            head = (REPO / "static" / "js" / "vendor" / f"{name}.min.js").read_text(encoding="utf-8")[:400]
            with self.subTest(library=name):
                self.assertIn("3.15.1", head)
                self.assertIn("gsap.com/standard-license", head)
        self.assertNotRegex(self.html.lower(), r"three(\.module)?(\.min)?\.js|webgl")

    def test_motion_is_opt_in_and_the_page_recovers_without_its_script(self):
        """One line in the head adds .pp-js when motion is welcome. Every rule that pins a
        stage or hides a scene hangs off that class, and the line takes it off again if
        process.js never reports in."""
        script = self.html[self.html.index("<script data-cfasync"):]
        script = script[:script.index("</script>")]
        self.assertIn("prefers-reduced-motion: no-preference", script)
        self.assertIn("classList.remove('pp-js')", script)
        self.assertIn("data-pp-ready", script)
        self.assertIn("setAttribute('data-pp-ready'", (REPO / "static" / "js" / "process.js").read_text(encoding="utf-8"))
        css = re.sub(r"/\*.*?\*/", "", (REPO / "static" / "css" / "process.css").read_text(encoding="utf-8"), flags=re.S)
        screen = css[:css.index("@media print")]
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", screen):
            if re.search(r"position:\s*(sticky|fixed)|visibility:\s*hidden|height:\s*\d+vh", body):
                with self.subTest(selector=" ".join(selector.split())[:60]):
                    self.assertTrue(all(".pp-js" in part for part in selector.split(",")), selector)
        self.assertNotIn("@keyframes", css)
        self.assertIn("@media print", css)


class ProcessPageBuildTests(unittest.TestCase):
    """What build.py writes beside the page."""

    @classmethod
    def setUpClass(cls):
        cls.builder = SiteBuilder()
        cls.page = cls.builder.load_process_page()

    def test_markdown_alternate_carries_every_scene_and_the_contact_route(self):
        text = self.builder.markdown_alternate(self.page["title"], f"{self.page['tagline']} {self.page['lead']}", URL,
                                               self.page["markdown"])
        for stage in self.page["stages"]:
            with self.subTest(stage=stage["id"]):
                self.assertIn(f"## {int(stage['number'])}. {stage['title']}", text)
                for beat in stage["beats"]:
                    self.assertIn(self.builder.absolute_links(beat), text)
                for line in stage["object"]:
                    self.assertIn(line, text)
        self.assertIn("## Working together", text)
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

    def test_a_stage_with_a_missing_caption_stops_the_build(self):
        original = (REPO / "content" / "process.md").read_text(encoding="utf-8")
        beat = re.search(r'      - "We talk for 30 minutes[^\n]*\n', original).group(0)
        with tempfile.TemporaryDirectory() as scratch:
            copy = Path(scratch) / "process.md"
            copy.write_text(original.replace(beat, ""), encoding="utf-8")
            with self.assertRaises(ValueError):
                SiteBuilder().load_process_page(copy)


if __name__ == "__main__":
    unittest.main()
