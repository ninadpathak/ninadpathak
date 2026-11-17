"""The hub-and-spoke model in the built site.

Eight hubs, each a written page that links every one of its spokes once; every post on
exactly one hub; breadcrumbs, related cards and structured data that agree with the
hub a post declares; llms.txt, the sitemap and the redirects that reflect the hubs.
tools/audit_clusters.py enforces the same model and has its own fixture tests. These
read the real build, so a template or config change that breaks a hub page fails here.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest

import frontmatter
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"
CONFIG = tomllib.loads((ROOT / "config.toml").read_text(encoding="utf-8"))
BASE = CONFIG["site"]["url"].rstrip("/")
HUBS = {raw["slug"]: raw for raw in CONFIG["content"]["categories"]}
TOOLS = {raw["slug"]: raw for raw in CONFIG["content"]["tools"]}
EXPECTED_HUBS = ["technical-documentation", "ai-search-optimization", "developer-experience", "ai-agents",
                 "agent-memory", "rag", "coding-agents", "ai-engineering"]


def posts():
    found = {}
    for path in sorted((ROOT / "content" / "posts").glob("*.md")):
        data = frontmatter.load(path)
        if data.get("status") == "published":
            found[data.get("slug") or path.stem] = data
    return found


def page(url):
    return (OUTPUT / url.strip("/") / "index.html").read_text(encoding="utf-8")


def main_of(html):
    return re.search(r"<main\b.*?</main>", html, re.S).group(0)


def schema(html):
    return [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def pillar(slug):
    return yaml.safe_load((ROOT / "content" / "pillars" / f"{slug}.yaml").read_text(encoding="utf-8"))


class BuiltSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (OUTPUT / "sitemap.xml").is_file():
            # CI builds before it tests, so a missing build there is a failure, not a skip.
            raise AssertionError("run `python build.py` first: these tests read the built site")
        cls.posts = posts()


class HubModelTests(BuiltSite):
    def test_the_eight_hubs_and_their_fields(self):
        self.assertEqual(list(HUBS), EXPECTED_HUBS)
        for slug, hub in HUBS.items():
            for field in ("title", "label", "description", "primary_query", "money_page", "hire_note"):
                self.assertTrue(hub.get(field), f"{slug} has no {field}")
            self.assertIn(f'href=\\"{hub["money_page"]}\\"'.replace("\\", ""), hub["hire_note"])

    def test_pillar_files_match_the_hubs_exactly(self):
        files = sorted(p.stem for p in (ROOT / "content" / "pillars").glob("*.yaml"))
        self.assertEqual(files, sorted(HUBS))

    def test_every_post_is_on_exactly_one_hub(self):
        listed = {}
        for slug in HUBS:
            for section in pillar(slug)["sections"]:
                for entry in section["spokes"]:
                    if "post" in entry:
                        self.assertNotIn(entry["post"], listed, f"{entry['post']} is on two hubs")
                        listed[entry["post"]] = slug
        self.assertEqual(sorted(listed), sorted(self.posts))
        for slug, post in self.posts.items():
            self.assertEqual(listed[slug], post["category"], slug)

    def test_every_spoke_has_one_sentence_of_context(self):
        for slug in HUBS:
            for section in pillar(slug)["sections"]:
                for entry in section["spokes"]:
                    note = entry["note"].strip()
                    self.assertTrue(note.endswith("."), note)
                    self.assertEqual(len(re.findall(r"[.!?](?:\s|$)", note)), 1, f"{slug}: {note}")

    def test_primary_queries_are_unique_across_indexable_urls(self):
        queries = [str(post["primary_query"]).lower() for post in self.posts.values()]
        queries += [hub["primary_query"] for hub in HUBS.values()]
        queries += [tool["primary_query"] for tool in TOOLS.values()]
        service_files = [ROOT / "content" / "services.md", *sorted((ROOT / "content" / "services").glob("*.md"))]
        queries += [frontmatter.load(path)["primary_query"] for path in service_files]
        owned = [query for query in queries if query != "none"]
        self.assertEqual(len(owned), len(set(owned)), sorted(q for q in owned if owned.count(q) > 1))
        self.assertEqual(len(queries), len(self.posts) + len(HUBS) + len(TOOLS) + len(service_files))

    def test_hub_copy_keeps_the_claims_that_were_ruled_out(self):
        for slug in HUBS:
            text = (ROOT / "content" / "pillars" / f"{slug}.yaml").read_text(encoding="utf-8")
            for banned in ("30+", "740%", "[TODO"):
                self.assertNotIn(banned, text, slug)
            for mention in re.findall(r"[^.\n]*Mem0[^.\n]*", text):
                self.assertIn("I ran a team of 13 writers at Mem0", mention, slug)


class HubPageTests(BuiltSite):
    def test_each_hub_page_links_every_spoke_once_in_a_section(self):
        for slug, hub in HUBS.items():
            main = main_of(page(f"/articles/{slug}/"))
            members = [s for s, post in self.posts.items() if post["category"] == slug]
            self.assertGreaterEqual(len(members), 4, slug)
            for member in members:
                self.assertEqual(main.count(f'href="/articles/{member}/"'), 1, f"{slug} -> {member}")
            for section in pillar(slug)["sections"]:
                self.assertIn(f">{section['heading']}</h2>", main)
            self.assertNotIn("More in this hub", main, f"{slug} has a spoke outside its sections")

    def test_each_hub_opens_with_its_lead_and_argument_before_the_map(self):
        for slug in HUBS:
            main = main_of(page(f"/articles/{slug}/"))
            data = pillar(slug)
            first_section = main.index(f">{data['sections'][0]['heading']}</h2>")
            self.assertIn('<p class="lead">', main[:first_section])
            argument = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", data["argument"])
            self.assertIn(argument, main[:first_section], slug)
            opening = re.sub(r"<[^>]+>", " ", main[main.index('<p class="lead">'):first_section])
            self.assertGreaterEqual(len(opening.split()), 150, slug)

    def test_each_hub_links_its_money_page_and_its_bridges(self):
        for slug, hub in HUBS.items():
            main = main_of(page(f"/articles/{slug}/"))
            self.assertIn(f'href="{hub["money_page"]}"', main, slug)
            bridges = pillar(slug)["bridges"]
            self.assertIn(len(bridges), (2, 3), slug)
            for bridge in bridges:
                self.assertIn(bridge["hub"], HUBS)
                self.assertEqual(main.count(f'href="/articles/{bridge["hub"]}/"'), 1, f"{slug} -> {bridge['hub']}")

    def test_money_pages_link_their_hubs_and_three_proof_spokes(self):
        for money in {hub["money_page"] for hub in HUBS.values()}:
            main = main_of(page(money))
            fed_by = [slug for slug, hub in HUBS.items() if hub["money_page"] == money]
            for slug in fed_by:
                self.assertIn(f'href="/articles/{slug}/"', main, f"{money} does not link hub {slug}")
            spokes = {target for target in re.findall(r'href="/articles/([^/"]+)/"', main)
                      if target in self.posts and self.posts[target]["category"] in fed_by}
            self.assertGreaterEqual(len(spokes), 3, f"{money}: {sorted(spokes)}")
            service = next(b for b in schema(page(money)) if b.get("@type") == "Service")
            self.assertEqual(sorted(item["url"] for item in service["subjectOf"]),
                             sorted(f"{BASE}/articles/{slug}/" for slug in fed_by))

    def test_hub_structured_data(self):
        for slug, hub in HUBS.items():
            html = page(f"/articles/{slug}/")
            blocks = schema(html)
            collection = next(b for b in blocks if b.get("@type") == "CollectionPage")
            self.assertEqual(collection["@id"], f"{BASE}/articles/{slug}/#hub")
            items = collection["mainEntity"]["itemListElement"]
            order = [entry.get("post") and f"{BASE}/articles/{entry['post']}/" or f"{BASE}/{entry['tool']}/"
                     for section in pillar(slug)["sections"] for entry in section["spokes"]]
            self.assertEqual([item["url"] for item in items], order, slug)
            self.assertEqual([item["position"] for item in items], list(range(1, len(items) + 1)))
            self.assertTrue(all(item["name"] for item in items))
            crumbs = next(b for b in blocks if b.get("@type") == "BreadcrumbList")["itemListElement"]
            self.assertEqual([c["item"] for c in crumbs], [f"{BASE}/", f"{BASE}/articles/", f"{BASE}/articles/{slug}/"])
            faq = next(b for b in blocks if b.get("@type") == "FAQPage")
            visible = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", main_of(html)))
            for question in faq["mainEntity"]:
                self.assertIn(question["name"], visible)
                self.assertIn(question["acceptedAnswer"]["text"], visible, f"{slug}: FAQ answer is not visible")

    def test_hub_pages_are_indexable_canonical_and_free_of_inline_style(self):
        for slug in HUBS:
            html = page(f"/articles/{slug}/")
            self.assertIn(f'<link rel="canonical" href="{BASE}/articles/{slug}/">', html)
            self.assertNotIn("noindex", re.search(r'<meta name="robots" content="([^"]*)"', html).group(1))
            self.assertNotIn(" style=", main_of(html))
            self.assertEqual(len(re.findall(r"<h1\b", html)), 1)

    def test_articles_index_lists_the_hubs(self):
        html = page("/articles/")
        for slug in HUBS:
            self.assertIn(f'href="/articles/{slug}/"', main_of(html))
        item_list = next(b for b in schema(html) if b.get("@type") == "ItemList")
        self.assertEqual([item["url"] for item in item_list["itemListElement"]],
                         [f"{BASE}/articles/{slug}/" for slug in HUBS])
        self.assertNotIn('"ItemList"', page("/articles/page/2/"))


class SpokePageTests(BuiltSite):
    def test_breadcrumb_part_of_line_and_schema_name_the_hub(self):
        for slug, post in self.posts.items():
            hub = HUBS[post["category"]]
            html = page(f"/articles/{slug}/")
            url = f"/articles/{post['category']}/"
            crumb = re.search(r'<nav aria-label="Breadcrumb".*?</nav>', html, re.S).group(0)
            self.assertIn(f'<a href="{url}">{hub["title"]}</a>', crumb, slug)
            header = re.search(r'<header class="post-header">.*?</header>', html, re.S).group(0)
            self.assertIn(f'Part of <a href="{url}" class="tag">{hub["title"]}</a>', header, slug)
            self.assertLess(header.index("Part of"), header.index("<h1"), slug)
            blocks = schema(html)
            crumbs = next(b for b in blocks if b.get("@type") == "BreadcrumbList")["itemListElement"]
            self.assertEqual([(c["position"], c["name"]) for c in crumbs[:3]],
                             [(1, "Home"), (2, "Articles"), (3, hub["title"])], slug)
            self.assertEqual(crumbs[3]["item"], f"{BASE}/articles/{slug}/")
            article = next(b for b in blocks if b.get("@type") == "TechArticle")
            self.assertEqual(article["isPartOf"]["@id"], f"{BASE}{url}#hub", slug)

    def test_related_cards_come_from_the_same_hub_siblings_first(self):
        for slug, post in self.posts.items():
            related = re.search(r'<section class="post-related".*?</section>', page(f"/articles/{slug}/"), re.S)
            self.assertIsNotNone(related, slug)
            targets = re.findall(r'href="/articles/([^/]+)/"', related.group(0))
            self.assertEqual(len(targets), 3, slug)
            self.assertNotIn(slug, targets)
            for target in targets:
                self.assertEqual(self.posts[target]["category"], post["category"], f"{slug} -> {target}")
            siblings = [s for s in post.get("siblings") or [] if s in self.posts][:3]
            self.assertEqual(targets[:len(siblings)], siblings, slug)

    def test_hire_note_under_an_article_links_the_hub_money_page(self):
        for slug, post in self.posts.items():
            money = HUBS[post["category"]]["money_page"]
            cta = page(f"/articles/{slug}/").split('<h2 class="cta-title-compact">', 1)[1].split("</section>", 1)[0]
            self.assertIn(f'href="{money}"', cta, slug)
            self.assertEqual(cta.count('href="/services/"'), 1, f"{slug} links /services/ twice in its CTA")

    def test_markdown_alternate_names_the_hub(self):
        for slug, post in self.posts.items():
            hub = HUBS[post["category"]]
            lines = (OUTPUT / "articles" / slug / "index.md").read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[2], f"Part of: [{hub['title']}]({BASE}/articles/{post['category']}/)", slug)


class GlossaryTests(BuiltSite):
    def test_a_term_that_shares_a_slug_with_an_article_links_it(self):
        terms = yaml.safe_load((ROOT / "content" / "data" / "glossary.yaml").read_text(encoding="utf-8"))["terms"]
        twins = [term for term in terms if term["slug"] in self.posts]
        self.assertTrue(twins)
        for term in twins:
            self.assertEqual(term.get("canonical_article"), term["slug"])
            self.assertIn(f'<strong>Full guide:</strong> <a href="/articles/{term["slug"]}/">',
                          main_of(page(f"/glossary/{term['slug']}/")))

    def test_build_fails_on_a_twin_without_canonical_article(self):
        sys.path.insert(0, str(ROOT))
        import build
        builder = build.SiteBuilder.__new__(build.SiteBuilder)
        with self.assertRaisesRegex(ValueError, "must set canonical_article"):
            builder.link_glossary_owners([{"slug": "x"}], [{"slug": "x"}])
        with self.assertRaisesRegex(ValueError, "is not a published post"):
            builder.link_glossary_owners([{"slug": "y", "canonical_article": "gone"}], [{"slug": "x"}])


class HubLoaderTests(unittest.TestCase):
    """build.py must stop on a hub that would render as a bare list, and must never
    leave a published post off its hub page."""

    OPENING = "lead: " + "word " * 60 + "\nintro: " + "word " * 60 + "\nargument: " + "word " * 40 + "\n"
    SECTION = "sections:\n  - heading: One\n    spokes:\n      - post: a\n        note: Context for a.\n"

    def load(self, pillar_text, posts=("a",)):
        sys.path.insert(0, str(ROOT))
        import build
        builder = build.SiteBuilder(str(ROOT / "config.toml"))
        category = {"slug": "h", "posts": [{"slug": s, "url": f"/articles/{s}/", "title": s.upper(),
                                            "description": f"About {s}."} for s in posts]}
        other = {"slug": "other", "posts": []}
        with tempfile.TemporaryDirectory() as tmp:
            pillars = pathlib.Path(tmp) / "content" / "pillars"
            pillars.mkdir(parents=True)
            if pillar_text is not None:
                (pillars / "h.yaml").write_text(pillar_text, encoding="utf-8")
            (pillars / "other.yaml").write_text(self.OPENING, encoding="utf-8")
            previous = os.getcwd()
            os.chdir(tmp)
            try:
                builder.load_hubs([category, other], category["posts"])
            finally:
                os.chdir(previous)
        return category

    def test_a_hub_without_a_pillar_file_fails(self):
        with self.assertRaisesRegex(ValueError, "has no content/pillars/h.yaml"):
            self.load(None)

    def test_a_hub_without_an_argument_fails(self):
        with self.assertRaisesRegex(ValueError, "has no argument"):
            self.load(self.OPENING.replace("argument: " + "word " * 40, "argument: ''") + self.SECTION)

    def test_an_opening_under_150_words_fails(self):
        with self.assertRaisesRegex(ValueError, "is 101 words, under 150"):
            self.load(self.OPENING.replace("intro: " + "word " * 60, "intro: short") + self.SECTION)

    def test_a_paragraph_over_two_sentences_fails(self):
        text = self.OPENING.replace("intro: " + "word " * 60, "intro: " + "One two three four. " * 3 + "word " * 60)
        with self.assertRaisesRegex(ValueError, "two-sentence paragraph rule"):
            self.load(text + self.SECTION)

    def test_a_spoke_without_a_note_or_listed_twice_fails(self):
        with self.assertRaisesRegex(ValueError, "has no note"):
            self.load(self.OPENING + self.SECTION.replace("note: Context for a.", "note: ''"))
        with self.assertRaisesRegex(ValueError, "listed twice"):
            self.load(self.OPENING + self.SECTION + "      - post: a\n        note: Again.\n")

    def test_a_bridge_must_name_another_hub_and_link_it(self):
        with self.assertRaisesRegex(ValueError, "bridge to unknown hub"):
            self.load(self.OPENING + self.SECTION + "bridges:\n  - hub: nowhere\n    text: See [x](/articles/nowhere/).\n")
        with self.assertRaisesRegex(ValueError, "must link /articles/other/"):
            self.load(self.OPENING + self.SECTION + "bridges:\n  - hub: other\n    text: See the other hub.\n")

    def test_a_post_missing_from_the_sections_still_gets_a_link(self):
        category = self.load(self.OPENING + self.SECTION, posts=("a", "b"))
        self.assertEqual([s["heading"] for s in category["sections"]], ["One", "More in this hub"])
        self.assertEqual([spoke["url"] for spoke in category["spokes"]], ["/articles/a/", "/articles/b/"])
        self.assertEqual(category["sections"][1]["spokes"][0]["note"], "About b.")

    def test_a_hub_under_five_spokes_is_incubating(self):
        self.assertTrue(self.load(self.OPENING + self.SECTION)["incubating"])


class DiscoveryFileTests(BuiltSite):
    def test_llms_txt_has_one_section_per_hub_in_map_order(self):
        text = (OUTPUT / "llms.txt").read_text(encoding="utf-8")
        sections = {part.split("\n", 1)[0]: part for part in text.split("\n## ")[1:]}
        for slug, hub in HUBS.items():
            links = re.findall(r"\]\(" + re.escape(BASE) + r"(/[^)]*)\)", sections[hub["title"]])
            data = pillar(slug)
            posts_in_order = [f"/articles/{e['post']}/" for s in data["sections"] for e in s["spokes"] if "post" in e]
            tools_in_order = [f"/{e['tool']}/" for s in data["sections"] for e in s["spokes"] if "tool" in e]
            self.assertEqual(links, [f"/articles/{slug}/", *posts_in_order, *tools_in_order], slug)
            self.assertIn("Hiring page for this topic:", sections[hub["title"]].splitlines()[2])

    def test_llms_txt_lists_every_tool_and_url_once(self):
        text = (OUTPUT / "llms.txt").read_text(encoding="utf-8")
        links = re.findall(r"\]\((https?://[^)]+)\)", text)
        self.assertEqual(len(links), len(set(links)), sorted(u for u in links if links.count(u) > 1))
        for slug in TOOLS:
            self.assertIn(f"{BASE}/{slug}/", links)
        self.assertIn(f"{BASE}/tools/", links)

    def test_sitemap_lists_each_hub_with_its_newest_spoke_date(self):
        sitemap = (OUTPUT / "sitemap.xml").read_text(encoding="utf-8")
        entries = dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", sitemap))
        for slug in HUBS:
            members = [f"{BASE}/articles/{s}/" for s, post in self.posts.items() if post["category"] == slug]
            self.assertEqual(entries[f"{BASE}/articles/{slug}/"], max(entries[m] for m in members), slug)
        self.assertNotIn("/articles/distribution/", sitemap)


class RedirectTests(BuiltSite):
    RETARGETS = {"/ai-agent-memory": "/articles/agent-memory/", "/rag": "/articles/rag/",
                 "/ai-agent-architecture": "/articles/ai-agents/", "/ai-workflows": "/articles/coding-agents/",
                 "/llm-inference": "/articles/ai-engineering/", "/docs-as-code": "/articles/technical-documentation/",
                 "/articles/distribution": "/articles/developer-experience/"}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rules = {}
        for line in (OUTPUT / "_redirects").read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 3 and not line.startswith("#"):
                assert parts[0] not in cls.rules, f"duplicate redirect source {parts[0]}"
                cls.rules[parts[0]] = parts[1]

    def test_retargets_and_the_distribution_fold_in_both_slash_forms(self):
        for source, target in self.RETARGETS.items():
            self.assertEqual(self.rules.get(source), target, source)
            self.assertEqual(self.rules.get(source + "/"), target, source + "/")

    def test_no_loop_chain_missing_target_or_shadowed_page(self):
        sitemap = {loc[len(BASE):] for loc in re.findall(
            r"<loc>([^<]+)</loc>", (OUTPUT / "sitemap.xml").read_text(encoding="utf-8"))}
        for source, target in self.rules.items():
            self.assertIn(target, sitemap, f"{source} -> {target} is not a page in the sitemap")
            self.assertNotIn(target, self.rules, f"{source} -> {target} is redirected again")
            self.assertNotIn(target.rstrip("/"), self.rules, f"{source} -> {target} is redirected again")
            self.assertFalse((OUTPUT / source.strip("/") / "index.html").is_file(), f"{source} shadows a built page")

    def test_no_article_url_is_redirected_away(self):
        for slug in self.posts:
            for source in (f"/articles/{slug}", f"/articles/{slug}/"):
                self.assertNotIn(source, self.rules)
        self.assertFalse((OUTPUT / "articles" / "distribution").exists())


class AuditTests(BuiltSite):
    def test_the_strict_audit_passes_on_the_real_site(self):
        result = subprocess.run([sys.executable, "tools/audit_clusters.py", "--strict", "--quiet"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout[-3000:])
        self.assertIn("--- errors: 0 ---", result.stdout)


if __name__ == "__main__":
    unittest.main()
