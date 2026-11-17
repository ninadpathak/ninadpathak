"""An agent that lands on any page can say what he sells and how to hire him.

The 2026-11-16 audit found the offer and the contact route missing from every page an
agent reaches first: no services page, the email on /contact/ only, a booking link that
renders nothing without JavaScript, and an llms.txt that listed pages without stating an
offer. These tests hold the fixes in place, and they hold the fact rules too: no price
field, no placeholder, and neither of the two unverified homepage figures on a hiring
surface.
"""
import json
import os
import re
import tempfile
import unittest
from pathlib import Path

from build import SiteBuilder

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"
BUILDER = SiteBuilder()
CONTACT = BUILDER.config["contact"]
HIRE = BUILDER.config["hire"]
BASE = BUILDER.config["site"]["url"].rstrip("/")
LD_JSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
SERVICE_ROUTES = ("services", "services/freelance-technical-writer-for-ai-companies", "services/ai-ready-documentation-audit",
                  "services/developer-documentation", "services/technical-tutorials", "services/technical-articles",
                  "services/changelogs-and-release-notes", "services/technical-content-programs")
# On Ninad's claims-to-check list. Existing instances stay; no hiring surface repeats them.
UNVERIFIED = ("30+", "740%")


def schema_objects(path):
    return [json.loads(block) for block in LD_JSON.findall(path.read_text(encoding="utf-8"))]


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def site_pages():
    return [path for path in sorted(OUTPUT.rglob("*.html")) if path.relative_to(OUTPUT).parts[0] != "static"]


class ServiceLoaderTests(unittest.TestCase):
    def _load(self, files, include_drafts=False):
        builder = SiteBuilder(include_drafts=include_drafts)
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            for name, text in files.items():
                target = Path(tmp) / "content" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")
            os.chdir(tmp)
            try:
                return builder.load_service_pages()
            finally:
                os.chdir(cwd)

    def test_index_and_child_pages_get_their_routes(self):
        pages = self._load({
            "services.md": "---\ntitle: S\nstatus: published\n---\n\n<!-- service-list -->\n\n## FAQ\n\n### Q?\n\nA.\n",
            "services/audit.md": "---\ntitle: A\nkind: service\nglyph: checks\ncard: A check.\nstatus: published\n---\n\nBody.\n",
            "service-glyphs.json": '{"checks": "<svg></svg>"}',
        })
        self.assertEqual([page["url"] for page in pages], ["/services/", "/services/audit/"])
        self.assertTrue(pages[0]["is_index"])
        # The text copies of the index get the list the HTML page shows as boxes.
        self.assertIn("- [A](https://ninadpathak.com/services/audit/): A check.", pages[0]["markdown"])
        self.assertNotIn("service-list", pages[0]["markdown"])
        self.assertEqual(pages[0]["faqs"], [{"question": "Q?", "answer": "A."}])

    def test_a_child_page_needs_its_box_fields(self):
        """Every page under /services/ is shown as a box on the index, so it must say
        whether it is a service or an audience and carry the box's line and icon."""
        glyphs = {"service-glyphs.json": '{"checks": "<svg></svg>"}'}
        index = {"services.md": "---\ntitle: S\nstatus: published\n---\n\n<!-- service-list -->\n\nBody.\n"}
        for front in ("title: A\nstatus: published",
                      "title: A\nkind: service\nglyph: checks\nstatus: published",
                      "title: A\nkind: service\ncard: A check.\nglyph: missing\nstatus: published",
                      "title: A\nkind: other\ncard: A check.\nglyph: checks\nstatus: published"):
            with self.subTest(front=front), self.assertRaises(ValueError):
                self._load({**index, **glyphs, "services/audit.md": f"---\n{front}\n---\n\nBody.\n"})

    def test_a_todo_marker_fails_the_build(self):
        with self.assertRaises(ValueError):
            self._load({"services.md": "---\ntitle: S\nstatus: published\n---\n\nPrice: [TODO: rates]\n"})

    def test_a_draft_is_skipped_by_a_normal_build(self):
        files = {"services.md": "---\ntitle: S\nstatus: draft\n---\n\nBody.\n"}
        self.assertEqual(self._load(files), [])
        self.assertFalse(self._load(files, include_drafts=True)[0]["published"])

    def test_the_paragraph_cap_applies(self):
        with self.assertRaises(ValueError):
            self._load({"services.md": "---\ntitle: S\nstatus: published\n---\n\nOne is here. Two is here. Three is here.\n"})

    def test_shipped_pages_carry_no_placeholder_or_unverified_figure(self):
        for path in [ROOT / "content/services.md", *sorted((ROOT / "content/services").glob("*.md"))]:
            text = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name):
                self.assertNotIn("[TODO", text)
                self.assertNotIn("—", text)
                for figure in UNVERIFIED:
                    self.assertNotIn(figure, text.replace("50+", ""))


class PersonOfferTests(unittest.TestCase):
    def test_person_carries_email_contact_point_and_offers(self):
        person = BUILDER.person_schema()
        self.assertEqual(person["email"], CONTACT["email"])
        self.assertEqual(person["contactPoint"]["email"], CONTACT["email"])
        self.assertEqual(person["contactPoint"]["url"], f"{BASE}/contact/")
        offered = [offer["itemOffered"] for offer in person["makesOffer"]]
        self.assertEqual([item["name"] for item in offered], [offer["name"] for offer in HIRE["offers"]])
        for item in offered:
            self.assertEqual(item["@type"], "Service")
            self.assertEqual(item["audience"]["audienceType"], HIRE["audience"])
            self.assertTrue(item["url"].startswith(f"{BASE}/services/"))

    def test_no_price_is_published_anywhere_in_the_offer(self):
        for node in walk(BUILDER.person_schema()):
            for field in ("price", "priceCurrency", "priceRange", "priceSpecification"):
                self.assertNotIn(field, node)

    def test_one_audience_wording(self):
        self.assertEqual(HIRE["audience"], "AI and developer-tool companies")
        self.assertIn(HIRE["audience"], HIRE["statement"])
        self.assertIn(HIRE["audience"], BUILDER.config["identity"]["description"])
        for template in ("post.html", "contact.html", "index.html", "base.html"):
            markup = (ROOT / "templates" / template).read_text(encoding="utf-8")
            with self.subTest(template=template):
                self.assertNotIn("B2B SaaS companies", markup)
                self.assertNotIn("DevTools companies", markup)


class BuiltSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (OUTPUT / "sitemap.xml").is_file():
            # CI builds before it tests. A missing build there means these checks did
            # not run, which must read as a failure and not as a skip.
            if os.environ.get("CI"):
                raise AssertionError("output/ is missing in CI: build.py must run before the tests")
            raise unittest.SkipTest("run `python build.py` first: these read the built site")
        cls.sitemap = (OUTPUT / "sitemap.xml").read_text(encoding="utf-8")
        cls.llms = (OUTPUT / "llms.txt").read_text(encoding="utf-8")

    def page(self, route):
        return (OUTPUT / route / "index.html").read_text(encoding="utf-8")

    def test_every_page_states_the_email_and_booking_url_as_text(self):
        """One fetch from any page. The address and the booking URL are visible text,
        not only an href, because the booking page renders nothing without JavaScript."""
        for path in site_pages():
            html = path.read_text(encoding="utf-8")
            with self.subTest(page=str(path.relative_to(OUTPUT))):
                self.assertIn(f'>{CONTACT["email"]}</a>', html)
                self.assertIn(f'>{CONTACT["booking_url"]}</a>', html)
                self.assertIn('href="/services/"', html)
                self.assertNotIn("/cdn-cgi/l/email-protection", html)

    def test_service_pages_are_built_indexable_and_listed(self):
        for route in SERVICE_ROUTES:
            html = self.page(route)
            with self.subTest(route=route):
                self.assertIn('content="index, follow', html)
                self.assertIn(f"<loc>{BASE}/{route}/</loc>", self.sitemap)
                self.assertIn(f"]({BASE}/{route}/)", self.llms)
                self.assertNotIn("[TODO", html)
                types = [obj.get("@type") for obj in schema_objects(OUTPUT / route / "index.html")]
                self.assertIn("Service", types)
                self.assertIn("FAQPage", types)

    def test_hiring_surfaces_publish_no_price_and_no_unverified_figure(self):
        for route in (*SERVICE_ROUTES, "contact"):
            path = OUTPUT / route / "index.html"
            with self.subTest(route=route):
                for obj in schema_objects(path):
                    for node in walk(obj):
                        self.assertFalse({"price", "priceRange", "priceSpecification"} & set(node))
                main = path.read_text(encoding="utf-8").split("<main", 1)[1].split("</main>", 1)[0]
                for figure in UNVERIFIED:
                    self.assertNotIn(figure, main.replace("50+", ""))
        for name in ("llms.txt", "llms-full.txt", "404.html"):
            text = (OUTPUT / name).read_text(encoding="utf-8")
            with self.subTest(file=name):
                for figure in UNVERIFIED:
                    self.assertNotIn(figure, text.replace("50+", ""))

    def test_article_cta_states_the_offer_and_links_the_hiring_pages(self):
        html = self.page("articles/api-documentation")
        cta = html[html.index("<!-- CTA -->"):html.index("</main>")]
        self.assertIn("freelance technical writer for AI and developer-tool companies", cta)
        for target in ('href="/services/"', 'href="/work/"', f'href="mailto:{CONTACT["email"]}"'):
            self.assertIn(target, cta)

    def test_home_and_contact_say_what_he_sells(self):
        for route, path in (("home", OUTPUT / "index.html"), ("contact", OUTPUT / "contact/index.html")):
            html = path.read_text(encoding="utf-8")
            title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
            description = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
            with self.subTest(route=route):
                self.assertRegex(title, r"Freelance Technical Writer|Work with Ninad Pathak")
                self.assertIn("AI and developer-tool companies", description)
                self.assertIn(f'{BASE}/static/images/diagrams/services/og.png', html)
                self.assertNotIn('property="og:image"       content="' + BASE + '/static/favicon.png"', html)
        self.assertTrue((OUTPUT / "static/images/diagrams/services/og.png").is_file())

    def test_contact_work_and_portfolio_schema(self):
        contact = [obj for obj in schema_objects(OUTPUT / "contact/index.html") if obj.get("@type") == "ContactPage"]
        self.assertEqual(len(contact), 1)
        self.assertEqual(contact[0]["mainEntity"]["@id"], f"{BASE}/#person")
        for route, minimum in (("work", 5), ("portfolio", 10)):
            page = next(obj for obj in schema_objects(OUTPUT / route / "index.html") if obj.get("@type") == "CollectionPage")
            items = page["mainEntity"]["itemListElement"]
            with self.subTest(route=route):
                self.assertEqual(page["mainEntity"]["@type"], "ItemList")
                self.assertEqual(page["mainEntity"]["numberOfItems"], len(items))
                self.assertGreaterEqual(len(items), minimum)
                for item in items:
                    self.assertTrue(item["item"]["url"].startswith("http"), item)

    def test_llms_txt_states_the_offer_above_the_first_section(self):
        preamble = self.llms.split("\n## ", 1)[0]
        self.assertIn(HIRE["statement"], preamble)
        self.assertIn(CONTACT["email"], preamble)
        self.assertIn(CONTACT["booking_url"], preamble)
        for client in HIRE["clients"]:
            self.assertIn(client, preamble)
        about = self.llms.split("## About", 1)[1].split("\n## ", 1)[0]
        self.assertIn(f"]({BASE}/services/)", about)
        # Prose inside a section is what this site's own validator flags.
        for section in self.llms.split("\n## ")[1:]:
            for line in section.splitlines()[1:]:
                self.assertTrue(not line.strip() or line.startswith("- "), line)

    def test_llms_full_txt_covers_the_money_pages_only(self):
        text = (OUTPUT / "llms-full.txt").read_text(encoding="utf-8")
        self.assertIn(BUILDER.hire_line(), text)
        for route in SERVICE_ROUTES:
            self.assertIn(f"Source: {BASE}/{route}/", text)
        self.assertIn(f"Source: {BASE}/about/", text)
        self.assertNotIn(f"{BASE}/articles/api-documentation/)", text.split("## Case studies")[1])
        self.assertLess(len(text), 40_000)

    def test_every_article_has_a_markdown_alternate(self):
        articles = [path for path in (OUTPUT / "articles").glob("*/index.html")
                    if any(obj.get("@type") == "TechArticle" for obj in schema_objects(path))]
        self.assertTrue(articles)
        for path in articles:
            slug = path.parent.name
            markdown = path.with_name("index.md")
            with self.subTest(slug=slug):
                self.assertIn(f'<link rel="alternate" type="text/markdown" title=', path.read_text(encoding="utf-8"))
                self.assertIn(f'href="/articles/{slug}/index.md"', path.read_text(encoding="utf-8"))
                text = markdown.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("# "))
                self.assertIn(f"Canonical: {BASE}/articles/{slug}/", text)
                self.assertIn(BUILDER.hire_line(), text)

    def test_service_pages_have_markdown_alternates(self):
        for route in SERVICE_ROUTES:
            html = self.page(route)
            text = (OUTPUT / route / "index.md").read_text(encoding="utf-8")
            with self.subTest(route=route):
                self.assertIn(f'<link rel="alternate" type="text/markdown" title=', html)
                self.assertIn(f'href="/{route}/index.md"', html)
                self.assertTrue(text.startswith("# "))
                self.assertIn(f"Canonical: {BASE}/{route}/", text)
                self.assertIn(BUILDER.hire_line(), text)
                self.assertNotIn("](/", text)

    def test_markdown_alternates_carry_no_root_relative_url(self):
        """Raw HTML figures, images and iframes too: the file is read away from the site."""
        pattern = re.compile(r"""\]\(/(?!/)|\b(?:src|href|poster|srcset)=["']/(?!/)|,\s*/static/""")
        for path in sorted(OUTPUT.rglob("index.md")):
            with self.subTest(file=str(path.relative_to(OUTPUT))):
                self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")))

    def test_no_redirect_chain_or_loop(self):
        rules = [line.split() for line in (OUTPUT / "_redirects").read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.startswith("#")]
        sources = {rule[0] for rule in rules}
        for source, target, *_ in rules:
            with self.subTest(source=source):
                self.assertNotIn(target, sources, "a redirect target is itself redirected")
                self.assertNotEqual(source.rstrip("/"), target.rstrip("/"))

    def test_hiring_aliases_redirect_to_services(self):
        redirects = (OUTPUT / "_redirects").read_text(encoding="utf-8").splitlines()
        aliases = {
            "/services/": ("/hire", "/hire-me", "/work-with-me", "/pricing", "/technical-writing-services"),
            "/about/": ("/about-us", "/about-me"),
            "/contact/": ("/contact-us", "/contact-me", "/contact-form"),
        }
        for target, sources in aliases.items():
            self.assertTrue((OUTPUT / target.strip("/") / "index.html").is_file())
            for alias in sources:
                for source in (alias, alias + "/"):
                    with self.subTest(source=source):
                        self.assertIn(f"{source} {target} 301", redirects)
                        self.assertFalse((OUTPUT / alias.strip("/")).exists(), "the alias shadows a built page")

    def test_home_page_answers_the_hiring_question_in_one_fetch(self):
        """Zone analytics show user-triggered agents land on / more than anywhere else,
        so the offer, the audience, named proof and the contact route are in its body."""
        main = (OUTPUT / "index.html").read_text(encoding="utf-8").split("<main", 1)[1].split("</main>", 1)[0]
        self.assertIn(HIRE["statement"], main)
        self.assertIn(HIRE["audience"], main)
        for proof in ('href="/work/centus/"', 'href="/work/mem0/"', "Centus", "Mem0", "Firecrawl"):
            self.assertIn(proof, main)
        self.assertIn(f'>{CONTACT["email"]}</a>', main)
        self.assertIn(f'>{CONTACT["booking_url"]}</a>', main)
        self.assertIn('href="/services/"', main)

    def test_each_money_page_gets_contextual_links_with_descriptive_anchors(self):
        """Ranking needs internal links whose anchor names the page's query, from the
        pages on the same subject: the cluster page, its articles, the tools, home."""
        audit = ('href="/services/ai-ready-documentation-audit/">AI-ready documentation audit', (
            "articles/ai-search-optimization", "tools", "ai-overviews-checker", "ai-crawler-checker",
            "llms-txt-validator", "llms-txt-generator", "services", ""))
        ai = ('href="/services/freelance-technical-writer-for-ai-companies/">freelance technical writer for AI companies', (
            "articles/ai-engineering", "articles/writing-for-ai-products", "articles/agent-harnesses",
            "services", "services/ai-ready-documentation-audit", ""))
        services = ('href="/services/">technical writing services', (
            "articles/devtools-documentation", "work/centus", "about", "services/ai-ready-documentation-audit",
            "services/freelance-technical-writer-for-ai-companies", ""))
        for anchor, sources in (audit, ai, services):
            for route in sources:
                html = (OUTPUT / route / "index.html").read_text(encoding="utf-8")
                main = html.split("<main", 1)[1].split("</main>", 1)[0]
                with self.subTest(anchor=anchor, source=route or "/"):
                    self.assertIn(anchor.lower(), main.lower())

    def test_article_cta_links_services_once(self):
        """A cluster without its own hiring page gets no second sentence to /services/."""
        html = self.page("articles/api-documentation")
        cta = html[html.index("<!-- CTA -->"):html.index("</main>")]
        self.assertEqual(cta.count('href="/services/"'), 1)

    def test_services_index_shows_each_service_as_its_own_box(self):
        """Six service boxes fill a three-column grid evenly (3 x 2, then 2 x 3), and the
        audience page sits apart in one full-width box. Each box links a built page."""
        main = self.page("services").split("<main", 1)[1].split("</main>", 1)[0]
        grids = re.findall(r'<ul class="topic-grid (topic-grid-\d)">(.*?)</ul>', main, re.S)
        self.assertEqual([name for name, _ in grids], ["topic-grid-3", "topic-grid-1"])
        services = re.findall(r'<a href="(/services/[a-z-]+/)" class="topic-card">', grids[0][1])
        audiences = re.findall(r'<a href="(/services/[a-z-]+/)" class="topic-card">', grids[1][1])
        self.assertEqual(len(services), 6, "six boxes fill the grid with no stranded box")
        self.assertEqual(len(set(services)), 6)
        self.assertEqual(audiences, ["/services/freelance-technical-writer-for-ai-companies/"])
        self.assertEqual({url.strip("/") for url in services + audiences}, set(SERVICE_ROUTES[1:]))
        for _, body in grids:
            self.assertEqual(body.count('<svg class="topic-glyph"'), body.count('class="topic-card"'))
        css = (Path(__file__).resolve().parent.parent / "static" / "css" / "main.css").read_text(encoding="utf-8")
        self.assertIn(".topic-grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); grid-auto-rows: 1fr; }", css)

    def test_no_service_page_states_a_price_or_says_hire(self):
        for route in SERVICE_ROUTES:
            html = self.page(route)
            with self.subTest(route=route):
                self.assertNotRegex(html, r'"price[A-Za-z]*"')
                self.assertNotRegex(html, r"(?i)hire me|hire ninad")

    def test_services_page_states_the_contact_route_once_per_place(self):
        main = self.page("services").split("<main", 1)[1].split("</main>", 1)[0]
        # The hire line under the H1, the "How we'd work together" section and the CTA band.
        self.assertEqual(main.count(f'>{CONTACT["email"]}</a>'), 3)
        for route in SERVICE_ROUTES[1:]:
            child = self.page(route).split("<main", 1)[1].split("</main>", 1)[0]
            with self.subTest(route=route):
                self.assertEqual(child.count(f'>{CONTACT["email"]}</a>'), 3)

    def test_services_page_states_no_pricing_method(self):
        text = (ROOT / "content/services.md").read_text(encoding="utf-8")
        self.assertIn("This page lists no rate", text)
        for phrase in ("I quote each project", "from its scope", "fixed rate"):
            self.assertNotIn(phrase, text)

    def test_one_primary_query_per_money_page(self):
        """The query wording sits in the slug, title, H1, description and first sentence,
        and no two money pages share a title or an H1."""
        targets = {
            "services": "technical writing services",
            "services/freelance-technical-writer-for-ai-companies": "freelance technical writer for ai companies",
            "services/ai-ready-documentation-audit": "ai-ready documentation audit",
        }
        seen = set()
        for route, query in targets.items():
            html = self.page(route).lower()
            title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
            h1 = re.sub(r"<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", html, re.S).group(1))
            description = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
            lead = re.search(r'<p class="lead">(.*?)</p>', html, re.S).group(1)
            with self.subTest(route=route):
                for place in (title, h1, description, lead.split(". ")[0]):
                    self.assertIn(query, place)
                if route != "services":
                    self.assertIn(query.replace(" ", "-"), route)
                self.assertNotIn(title, seen)
                self.assertNotIn(h1, seen)
                seen.update((title, h1))

    def test_preview_deployments_are_noindex_and_the_production_alias_is_not(self):
        """The form in Cloudflare's Pages headers documentation. A rule that starts with
        a path instead of https:// would apply to ninadpathak.com too. The production
        alias stays indexable: it holds rankings a noindex would drop, and it waits on a
        301 instead."""
        headers = (OUTPUT / "_headers").read_text(encoding="utf-8")
        self.assertRegex(headers, r"(?m)^" + re.escape("https://:version.:project.pages.dev/*") + r"\n\s+X-Robots-Tag: noindex$")
        self.assertNotRegex(headers, r"(?m)^https://:project\.pages\.dev/")
        self.assertNotRegex(headers, r"(?m)^/\*\n\s+X-Robots-Tag")
        for rule in ("/articles/:slug/index.md", "/services/index.md", "/services/:slug/index.md"):
            with self.subTest(rule=rule):
                self.assertRegex(headers, r"(?m)^" + re.escape(rule) + r"\n\s+Content-Type: text/markdown; charset=utf-8\n\s+X-Robots-Tag: noindex$")


if __name__ == "__main__":
    unittest.main()
