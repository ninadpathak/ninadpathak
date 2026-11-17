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

    def test_hub_copy_does_not_assert_the_engineer_to_writer_career_story(self):
        # The repo does not back that history (voice context, engineer-to-writer is held),
        # so the hub may describe the page and may not claim the story in first person.
        text = (ROOT / "content" / "pillars" / "developer-experience.yaml").read_text(encoding="utf-8")
        for claim in ("My account", "I dropped", "I kept", "engineer-to-writer page"):
            self.assertNotIn(claim, text)

    def test_no_sentence_repeats_across_hub_openings(self):
        seen = {}
        for slug in HUBS:
            data = pillar(slug)
            self.assertNotIn("parallel breaks", data["intro"])
            opening = f"{data['lead']} {data['intro']} {data['argument']}"
            for sentence in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", opening)):
                key = sentence.strip().lower()
                if len(key.split()) < 4:
                    continue
                self.assertNotIn(key, seen, f"{slug} repeats a sentence from {seen.get(key)}")
                seen[key] = slug
            # The argument is also the CollectionPage abstract, so it has to stand alone.
            self.assertNotRegex(data["argument"], r"^(So|Therefore|That|This)\b")
            self.assertNotIn("therefore", data["argument"].split(",")[0])

    def test_each_faq_answer_links_a_spoke_and_no_question_restates_the_lead(self):
        for slug in HUBS:
            data = pillar(slug)
            members = {s for s, post in self.posts.items() if post["category"] == slug}
            self.assertTrue(data["faqs"], slug)
            lead_opening = data["lead"].split(". ")[0]
            for faq in data["faqs"]:
                linked = set(re.findall(r"\]\(/articles/([^/)]+)/\)", faq["a"]))
                self.assertTrue(linked and linked <= members, f"{slug}: {faq['q']} links {linked}")
                self.assertNotIn(lead_opening, faq["a"], f"{slug}: {faq['q']} repeats the lead")


class HubPageTests(BuiltSite):
    def test_each_hub_page_links_every_spoke_once_in_a_section(self):
        for slug, hub in HUBS.items():
            main = main_of(page(f"/articles/{slug}/"))
            members = [s for s, post in self.posts.items() if post["category"] == slug]
            self.assertGreaterEqual(len(members), 4, slug)
            for member in members:
                self.assertEqual(main.count(f'<li><a href="/articles/{member}/"'), 1, f"{slug} -> {member}")
            for section in pillar(slug)["sections"]:
                self.assertIn(f">{section['heading']}</h2>", main)
            self.assertNotIn("More in this topic", main, f"{slug} has a spoke outside its sections")

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
            visible = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"</?a\b[^>]*>", "", main_of(html))))
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



class TopicGridTests(BuiltSite):
    """/articles/ opens with one box per hub, called Topics on the page, then the list."""

    GLYPHS = json.loads((ROOT / "content" / "topic-glyphs.json").read_text(encoding="utf-8"))

    def cards(self):
        grid = re.search(r'<ul class="topic-grid">(.*?)</ul>', main_of(page("/articles/")), re.S).group(1)
        return re.findall(r"<li>\s*(<a\b.*?</a>)\s*</li>", grid, re.S)

    def test_the_grid_has_one_box_per_hub_in_config_order(self):
        cards = self.cards()
        self.assertEqual([re.search(r'href="([^"]+)"', card).group(1) for card in cards],
                         [f"/articles/{slug}/" for slug in HUBS])
        for card, (slug, hub) in zip(cards, HUBS.items()):
            self.assertEqual(len(re.findall(r"<a\b", card)), 1, f"{slug}: the box is one link")
            self.assertIn(f'<h3 class="blog-row-title">{hub["label"]}</h3>', card)
            self.assertIn(f'<p class="blog-row-desc">{hub["card"]}</p>', card)
            count = sum(1 for post in self.posts.values() if post["category"] == slug)
            self.assertIn(f'<span class="read-time">{count} articles</span>', card)
            self.assertIn(self.GLYPHS[slug], card, f"{slug}: glyph missing")

    def test_each_hub_is_linked_once_and_the_page_says_topics(self):
        main = main_of(page("/articles/"))
        for slug in HUBS:
            self.assertEqual(main.count(f'href="/articles/{slug}/"'), 1, slug)
        self.assertEqual(re.findall(r'<h2 class="label">([^<]+)</h2>', main), ["Topics", "All articles"])
        self.assertNotRegex(re.sub(r"<[^>]+>", " ", main), r"\b[Hh]ubs?\b")
        self.assertNotIn(" style=", main)

    def test_item_list_matches_the_grid_and_only_page_one_has_it(self):
        html = page("/articles/")
        item_list = next(b for b in schema(html) if b.get("@type") == "ItemList")
        self.assertEqual(item_list["name"], "Article topics")
        self.assertEqual([(item["position"], item["url"], item["name"]) for item in item_list["itemListElement"]],
                         [(i, f"{BASE}/articles/{slug}/", hub["title"]) for i, (slug, hub) in enumerate(HUBS.items(), 1)])
        second = page("/articles/page/2/")
        self.assertNotIn('"ItemList"', second)
        self.assertNotIn("topic-grid", second)

    def test_the_article_list_still_links_every_post_once_across_its_pages(self):
        per_page = CONFIG["content"]["posts_per_page"]
        total = -(-len(self.posts) // per_page)
        linked = []
        for number in range(1, total + 1):
            url = "/articles/" if number == 1 else f"/articles/page/{number}/"
            html = page(url)
            self.assertIn(f'<link rel="canonical" href="{BASE}{url}">', html)
            rows = re.findall(r'<a href="/articles/([^/"]+)/" class="blog-row">(.*?)</a>', main_of(html), re.S)
            self.assertEqual(len(rows), per_page if number < total else len(self.posts) - per_page * (total - 1))
            for slug, row in rows:
                self.assertIn(f'<span class="tag">{HUBS[self.posts[slug]["category"]]["label"]}</span>', row, slug)
                self.assertIn(f'datetime="{str(self.posts[slug]["date"])[:10]}"', row, slug)
            linked += [slug for slug, _ in rows]
            self.assertIn(f"Page {number} of {total}", html)
        self.assertEqual(sorted(linked), sorted(self.posts))
        self.assertFalse((OUTPUT / "articles" / "page" / str(total + 1)).exists())

    def test_each_topic_has_its_own_decorative_glyph_at_a_fixed_size(self):
        self.assertEqual(list(self.GLYPHS), list(HUBS))
        names = [hub["glyph"] for hub in HUBS.values()]
        self.assertEqual(len(set(names)), len(names), "two topics share a glyph")
        self.assertEqual(len(set(self.GLYPHS.values())), len(HUBS))
        icon_set = (ROOT / "tools" / "image-brand" / "lib" / "topic-icons.mjs").read_text(encoding="utf-8")
        for name in names:
            self.assertRegex(icon_set, rf"(?m)^  {name}: \[", f"{name} is not in lib/topic-icons.mjs")
        for slug, svg in self.GLYPHS.items():
            # Fixed width and height reserve the box, so the icon cannot shift the layout.
            # Every icon shares one view box, which starts at the painted left edge so the
            # drawing lines up with the text under it.
            self.assertRegex(svg, r'^<svg class="topic-glyph" viewBox="2\.25 0 24 24" width="28" height="28" '
                                  r'aria-hidden="true" focusable="false">', slug)
            for banned in ("<script", "<style", " style=", "<text", "<image", "href="):
                self.assertNotIn(banned, svg, slug)

    def test_topic_icons_are_plain_line_drawings_coloured_by_one_rule(self):
        """The icons are chrome: one stroke, no fill, no accent, no figure-glyph classes."""
        for slug, svg in self.GLYPHS.items():
            inner = svg[svg.index(">") + 1:-len("</svg>")]
            # Only bare paths: nothing that can carry its own colour, fill or pattern.
            self.assertRegex(inner, r'^(<path d="[MLHVCSAZmlhvcsaz0-9 .,-]+"/>)+$', slug)
        css = (ROOT / "static" / "css" / "main.css").read_text(encoding="utf-8")
        rules = re.findall(r"(?m)^\.topic-glyph[^{]*\{([^}]*)\}", css)
        self.assertEqual(len(rules), 1, "one rule draws the icons outside the phone layout")
        for declaration in ("fill: none;", "stroke: var(--text-2);", "stroke-width: 1.5;"):
            self.assertIn(declaration, rules[0])
        # The figure treatment these icons replaced must not come back into the stylesheet.
        for gone in (".gl-", "np-hatch", "--glyph-detail"):
            self.assertNotIn(gone, css)

    def test_the_figure_pipeline_does_not_hash_the_topic_icons(self):
        """A topic icon edit must not make all the article figures stale."""
        render = (ROOT / "tools" / "image-brand" / "render.mjs").read_text(encoding="utf-8")
        self.assertNotIn("topic-icons", render)

    def test_the_committed_glyphs_match_the_library(self):
        result = subprocess.run(["node", str(ROOT / "tools" / "image-brand" / "topics.mjs"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_card_lines_are_one_plain_sentence_that_keeps_the_primary_query(self):
        for slug, hub in HUBS.items():
            line = hub["card"]
            self.assertEqual(len(re.findall(r"[.!?](?:\s|$)", line)), 1, f"{slug}: {line}")
            self.assertTrue(line.endswith("."), line)
            self.assertNotIn("\u2014", line)
            self.assertLessEqual(len(line), 120, f"{slug}: the line has to fit a box")
            self.assertIn(hub["primary_query"], f"{hub['label']} {line}".lower(), slug)
            self.assertFalse(line.lower().startswith(hub["label"].lower()[:-1]), f"{slug}: the line repeats the box name")


class SpokePageTests(BuiltSite):
    def test_breadcrumb_part_of_line_and_schema_name_the_hub(self):
        for slug, post in self.posts.items():
            hub = HUBS[post["category"]]
            html = page(f"/articles/{slug}/")
            url = f"/articles/{post['category']}/"
            crumb = re.search(r'<nav aria-label="Breadcrumb".*?</nav>', html, re.S).group(0)
            self.assertIn(f'<a href="{url}">{hub["title"]}</a>', crumb, slug)
            header = re.search(r'<header class="post-header">.*?</header>', html, re.S).group(0)
            self.assertIn(f'<a href="{url}" class="tag">Part of {hub["label"]}</a>', header, slug)
            self.assertLess(header.index("Part of"), header.index("<h1"), slug)
            blocks = schema(html)
            crumbs = next(b for b in blocks if b.get("@type") == "BreadcrumbList")["itemListElement"]
            self.assertEqual([(c["position"], c["name"]) for c in crumbs[:3]],
                             [(1, "Home"), (2, "Articles"), (3, hub["title"])], slug)
            self.assertEqual(crumbs[3]["item"], f"{BASE}/articles/{slug}/")
            article = next(b for b in blocks if b.get("@type") == "TechArticle")
            self.assertEqual(article["isPartOf"]["@id"], f"{BASE}{url}#hub", slug)

    def body_links(self, slug):
        aliases = json.loads((ROOT / "content" / "post-slug-aliases.json").read_text(encoding="utf-8"))
        found = re.findall(r"\]\(/articles/([a-z0-9][a-z0-9\-\.]*)/?(?:#[^)\s]*)?\)", self.posts[slug].content)
        return {aliases.get(s, s) for s in found} & set(self.posts) - {slug}

    def test_related_cards_stay_in_the_hub_and_add_links_the_body_lacks(self):
        """Rule L11 as changed in review: cards come from the post's own hub and go to
        posts the body does not already link, so each card is a new path."""
        card_inbound = dict.fromkeys(self.posts, 0)
        repeats = 0
        for slug, post in self.posts.items():
            related = re.search(r'<section class="post-related".*?</section>', page(f"/articles/{slug}/"), re.S)
            self.assertIsNotNone(related, slug)
            targets = re.findall(r'href="/articles/([^/]+)/"', related.group(0))
            self.assertEqual(len(targets), 3, slug)
            self.assertEqual(len(set(targets)), 3, slug)
            self.assertNotIn(slug, targets)
            linked = self.body_links(slug)
            hub = [s for s, other in self.posts.items() if other["category"] == post["category"] and s != slug]
            unlinked = [s for s in hub if s not in linked]
            for target in targets:
                self.assertEqual(self.posts[target]["category"], post["category"], f"{slug} -> {target}")
                card_inbound[target] += 1
                if target in linked:
                    repeats += 1
                    # Allowed only where the hub has too few posts the body does not link.
                    self.assertLess(len(unlinked), 3, f"{slug} repeats body link {target}")
        self.assertEqual([s for s, n in card_inbound.items() if n == 0], [], "posts no related card points at")
        self.assertLess(repeats, 25)

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


class ToolPageTests(BuiltSite):
    def test_each_tool_a_hub_lists_links_that_hub_above_its_title(self):
        listed = {}
        for slug in HUBS:
            for section in pillar(slug)["sections"]:
                for entry in section["spokes"]:
                    if "tool" in entry:
                        listed[entry["tool"]] = slug
        self.assertEqual(sorted(listed), sorted(TOOLS))
        for tool, hub in listed.items():
            main = main_of(page(f"/{tool}/"))
            link = f'<a href="/articles/{hub}/" class="tag">Part of {HUBS[hub]["label"]}</a>'
            self.assertEqual(main.count(link), 1, tool)
            self.assertLess(main.index(link), main.index("<h1"), tool)
            self.assertNotIn(" style=", main[:main.index("<h1")])

    def test_template_index_links_use_the_template_name(self):
        main = main_of(page("/articles/technical-documentation/"))
        for row in pillar("technical-documentation")["templates"]:
            self.assertIn(f'<a href="{row["file"]}">{row["name"]}</a>', main)
            self.assertTrue((ROOT / row["file"].lstrip("/")).is_file(), row["file"])
        self.assertNotIn(">Download<", main)


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
        self.assertEqual([s["heading"] for s in category["sections"]], ["One", "More in this topic"])
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
