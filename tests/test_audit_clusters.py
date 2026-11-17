"""tools/audit_clusters.py against a small fixture site, one test per rule.

The fixture is three hubs of five new posts each, built so the audit reports nothing.
Each test breaks one thing and expects the matching error, so a rule that stops firing
fails here. The audit also has to refuse to run without a built site: a missing output/
must never read as a pass.
"""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import audit_clusters  # noqa: E402

BASE = "https://example.com"
HUBS = ("alpha", "beta", "gamma")


def post_source(hub, n, date="2026-12-01"):
    nxt, after = (n % 5) + 1, ((n + 1) % 5) + 1
    return (
        f"---\ntitle: Post {hub} {n}\nslug: {hub}-{n}\ncategory: {hub}\nstatus: published\n"
        f"date: {date}\nprimary_query: query {hub} {n}\nsiblings:\n- {hub}-{nxt}\n- {hub}-{after}\n---\n\n"
        f"This page belongs to the [{hub} hub](/articles/{hub}/) and opens there.\n\n"
        f"See [topic {hub} {nxt}](/articles/{hub}-{nxt}/) and [topic {hub} {after}](/articles/{hub}-{after}/).\n"
    )


def post_html(hub, n):
    return (
        f'<html><head><script type="application/ld+json">'
        + json.dumps({"@type": "BreadcrumbList", "itemListElement": [
            {"item": f"{BASE}/"}, {"item": f"{BASE}/articles/"},
            {"item": f"{BASE}/articles/{hub}/"}, {"item": f"{BASE}/articles/{hub}-{n}/"}]})
        + f'</script></head><body><main><nav aria-label="Breadcrumb"><a href="/articles/{hub}/">{hub}</a></nav>'
        f'<section class="post-related"><a href="/articles/{hub}-{(n % 5) + 1}/">x</a></section>'
        f'<a href="/services/">hire</a></main></body></html>'
    )


def hub_html(hub):
    items = [{"url": f"{BASE}/articles/{hub}-{n}/"} for n in range(1, 6)]
    links = "".join(f'<li><a href="/articles/{hub}-{n}/">p</a></li>' for n in range(1, 6))
    return (
        '<html><head><meta name="robots" content="index, follow"><script type="application/ld+json">'
        + json.dumps({"@type": "CollectionPage", "mainEntity": {"@type": "ItemList", "itemListElement": items}})
        + f'</script></head><body><main>{links}<a href="/services/">hire</a></main></body></html>'
    )


def make_site(root: pathlib.Path):
    others = {hub: [h for h in HUBS if h != hub] for hub in HUBS}
    config = f'[site]\nurl = "{BASE}"\n\n[content]\n'
    for hub in HUBS:
        config += (f'[[content.categories]]\nslug = "{hub}"\ntitle = "Hub {hub}"\n'
                   f'primary_query = "hub {hub}"\nmoney_page = "/services/"\n\n')
    (root / "config.toml").write_text(config)
    (root / "content" / "posts").mkdir(parents=True)
    (root / "content" / "pillars").mkdir()
    (root / "content" / "services").mkdir()
    (root / "content" / "services.md").write_text(
        "---\ntitle: Services\nstatus: published\nprimary_query: services\n---\n\nHire me.\n")
    out = root / "output"
    sitemap = [f"{BASE}/", f"{BASE}/services/"]
    llms = ["# Site", ""]
    money_links = ""
    for hub in HUBS:
        spokes = "".join(f"      - post: {hub}-{n}\n        note: Context for {n}.\n" for n in range(1, 6))
        bridges = "".join(f"  - hub: {o}\n    text: \"See the [{o} hub](/articles/{o}/) for more.\"\n" for o in others[hub])
        (root / "content" / "pillars" / f"{hub}.yaml").write_text(
            f"lead: {'word ' * 60}\nintro: {'word ' * 60}\nargument: {'word ' * 40}\n"
            f"sections:\n  - heading: One\n    spokes:\n{spokes}bridges:\n{bridges}")
        (out / "articles" / hub).mkdir(parents=True)
        (out / "articles" / hub / "index.html").write_text(hub_html(hub))
        sitemap.append(f"{BASE}/articles/{hub}/")
        llms += [f"## Hub {hub}", "", f"- [Hub {hub}]({BASE}/articles/{hub}/): hub"]
        money_links += f'<a href="/articles/{hub}/">{hub}</a>'
        for n in range(1, 6):
            (root / "content" / "posts" / f"{hub}-{n}.md").write_text(post_source(hub, n))
            (out / "articles" / f"{hub}-{n}").mkdir()
            (out / "articles" / f"{hub}-{n}" / "index.html").write_text(post_html(hub, n))
            sitemap.append(f"{BASE}/articles/{hub}-{n}/")
            llms.append(f"- [Post {hub} {n}]({BASE}/articles/{hub}-{n}/): post")
        llms.append("")
    (out / "services").mkdir()
    (out / "services" / "index.html").write_text(f"<html><body><main>{money_links}</main></body></html>")
    (out / "sitemap.xml").write_text("".join(f"<url><loc>{loc}</loc></url>" for loc in sitemap))
    (out / "llms.txt").write_text("\n".join(llms))
    (out / "_redirects").write_text("/old /articles/alpha/ 301\n/old/ /articles/alpha/ 301\n")


class AuditFixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = pathlib.Path(self._tmp.name)
        make_site(self.root)

    def errors(self, rule=None):
        findings, _report = audit_clusters.audit(audit_clusters.Site(self.root))
        return [f for f in findings if f.level == "error" and (rule is None or f.rule == rule)]

    def warnings(self, rule):
        findings, _report = audit_clusters.audit(audit_clusters.Site(self.root))
        return [f for f in findings if f.level == "warning" and f.rule == rule]

    def run_main(self, *args):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = audit_clusters.main(["--root", str(self.root), *args])
        return code, out.getvalue()

    def edit(self, relative, old, new):
        path = self.root / relative
        text = path.read_text()
        self.assertIn(old, text, f"fixture drifted: {old!r} not in {relative}")
        path.write_text(text.replace(old, new))

    def assertRule(self, rule, fragment):
        messages = [f"{f.subject}: {f.message}" for f in self.errors(rule)]
        self.assertTrue(any(fragment in m for m in messages), f"no {rule} error containing {fragment!r}: {messages}")


class CleanFixtureTests(AuditFixture):
    def test_the_fixture_passes(self):
        self.assertEqual([str(f) for f in self.errors()], [])
        self.assertEqual(self.run_main("--strict")[0], 0)

    def test_strict_exits_one_on_an_error_and_zero_without_strict(self):
        self.edit("content/posts/alpha-1.md", "category: alpha", "category: nowhere")
        self.assertEqual(self.run_main("--strict")[0], 1)
        self.assertEqual(self.run_main()[0], 0)


class FailClosedTests(AuditFixture):
    def test_refuses_without_a_built_site(self):
        (self.root / "output" / "sitemap.xml").unlink()
        code, out = self.run_main("--strict")
        self.assertEqual(code, 2)
        self.assertIn("run `python build.py` first", out)

    def test_refuses_outside_a_repository(self):
        with tempfile.TemporaryDirectory() as empty, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(audit_clusters.main(["--root", empty, "--strict"]), 2)

    def test_missing_llms_txt_and_redirects_are_errors(self):
        (self.root / "output" / "llms.txt").unlink()
        (self.root / "output" / "_redirects").unlink()
        self.assertRule("llms", "is not built")
        self.assertRule("redirect", "is not built")

    def test_an_unbuilt_spoke_or_hub_is_an_error(self):
        (self.root / "output" / "articles" / "alpha-1" / "index.html").unlink()
        (self.root / "output" / "articles" / "beta" / "index.html").unlink()
        self.assertRule("L3", "alpha-1: is not built")
        self.assertRule("L1", "/articles/beta/ is not built")


class MembershipAndQueryTests(AuditFixture):
    def test_missing_and_unknown_category(self):
        self.edit("content/posts/alpha-1.md", "category: alpha\n", "")
        self.edit("content/posts/alpha-2.md", "category: alpha", "category: nowhere")
        self.assertRule("category", "alpha-1: has no category")
        self.assertRule("category", "alpha-2: category 'nowhere'")

    def test_missing_primary_query(self):
        self.edit("content/posts/alpha-1.md", "primary_query: query alpha 1\n", "")
        self.assertRule("query", "alpha-1: has no primary_query")

    def test_duplicate_query_between_two_posts(self):
        self.edit("content/posts/alpha-1.md", "primary_query: query alpha 1", "primary_query:  Query Alpha 2")
        self.assertRule("query", "query alpha 2: is the primary_query of 2 URLs")

    def test_duplicate_query_between_a_post_and_a_hub_or_service(self):
        self.edit("content/posts/alpha-1.md", "primary_query: query alpha 1", "primary_query: hub beta")
        self.edit("content/posts/alpha-2.md", "primary_query: query alpha 2", "primary_query: services")
        self.assertRule("query", "hub beta: is the primary_query of 2 URLs")
        self.assertRule("query", "services: is the primary_query of 2 URLs")

    def test_none_is_exempt_from_uniqueness(self):
        self.edit("content/posts/alpha-1.md", "primary_query: query alpha 1", "primary_query: none")
        self.edit("content/posts/alpha-2.md", "primary_query: query alpha 2", "primary_query: none")
        self.assertEqual(self.errors("query"), [])

    def test_a_service_page_without_a_query(self):
        self.edit("content/services.md", "primary_query: services\n", "")
        self.assertRule("query", "/services/: has no primary_query")


class HubTests(AuditFixture):
    def test_a_hub_under_five_spokes_must_be_incubating(self):
        self.edit("content/posts/alpha-5.md", "status: published", "status: draft")
        self.assertRule("spokes", "hub alpha: has 4 spokes")

    def test_an_incubating_hub_must_be_noindex_and_unlisted(self):
        self.edit("config.toml", 'slug = "alpha"\n', 'slug = "alpha"\nincubating = true\n')
        self.assertRule("spokes", "hub alpha: is incubating and must be noindex")

    def test_l1_unknown_slug_and_missing_spoke(self):
        self.edit("content/pillars/alpha.yaml", "- post: alpha-5", "- post: ghost")
        self.assertRule("L1", "names 'ghost'")
        self.assertRule("L1", "published spoke 'alpha-5' is in no section")

    def test_l1_spoke_listed_twice_and_without_context(self):
        self.edit("content/pillars/alpha.yaml", "- post: alpha-5\n        note: Context for 5.",
                  "- post: alpha-4\n        note: ''")
        self.assertRule("L1", "lists 'alpha-4' in 2 sections")
        self.assertRule("L1", "has no sentence of context")

    def test_l1_built_page_links_each_spoke_once(self):
        self.edit("output/articles/alpha/index.html", '<li><a href="/articles/alpha-1/">p</a></li>', "")
        self.edit("output/articles/beta/index.html", '<li><a href="/articles/beta-1/">p</a></li>',
                  '<li><a href="/articles/beta-1/">p</a></li><li><a href="/articles/beta-1/">again</a></li>')
        self.assertRule("L1", "links /articles/alpha-1/ 0 times")
        self.assertRule("L1", "links /articles/beta-1/ 2 times")

    def test_l1_a_second_link_outside_the_map_is_allowed(self):
        self.edit("output/articles/alpha/index.html", "</main>", '<p><a href="/articles/alpha-1/">in an answer</a></p></main>')
        self.assertEqual(self.errors("L1"), [])

    def test_l3_a_tool_spoke_must_link_its_hub(self):
        self.edit("config.toml", "[content]\n", '[content]\n[[content.tools]]\nslug = "checker"\nprimary_query = "checker"\n\n')
        self.edit("content/pillars/alpha.yaml", "bridges:", "      - tool: checker\n        note: Runs the check.\nbridges:")
        self.edit("output/articles/alpha/index.html", '{"url": "https://example.com/articles/alpha-5/"}',
                  '{"url": "https://example.com/articles/alpha-5/"}, {"url": "https://example.com/checker/"}')
        self.assertRule("L3", "tool checker: is not built")
        (self.root / "output" / "checker").mkdir()
        (self.root / "output" / "checker" / "index.html").write_text("<html><body><main>tool</main></body></html>")
        self.assertRule("L3", "tool checker: is a spoke of hub alpha and does not link /articles/alpha/")
        (self.root / "output" / "checker" / "index.html").write_text(
            '<html><body><main><a href="/articles/alpha/">Part of alpha</a></main></body></html>')
        self.assertEqual(self.errors("L3"), [])

    def test_l2_argument_and_opening_length(self):
        self.edit("content/pillars/alpha.yaml", "argument: " + "word " * 40, "argument: ''")
        self.edit("content/pillars/beta.yaml", "intro: " + "word " * 60, "intro: short")
        self.assertRule("L2", "hub alpha: states no argument")
        self.assertRule("L2", "hub beta: opens with 101 words")

    def test_l8_bridge_count_and_target(self):
        self.edit("content/pillars/alpha.yaml", '  - hub: gamma\n    text: "See the [gamma hub](/articles/gamma/) for more."\n', "")
        self.edit("content/pillars/beta.yaml", "- hub: gamma", "- hub: nowhere")
        self.assertRule("L8", "hub alpha: declares 1 bridges")
        self.assertRule("L8", "hub beta: bridge to 'nowhere'")

    def test_l9_money_links_both_ways(self):
        self.edit("output/articles/alpha/index.html", '<a href="/services/">hire</a>', "")
        self.edit("output/services/index.html", '<a href="/articles/beta/">beta</a>', "")
        self.assertRule("L9", "hub alpha: the built page does not link its money page")
        self.assertRule("L9", "hub beta: money page /services/ does not link the hub back")

    def test_item_list_count_matches_spokes(self):
        self.edit("output/articles/alpha/index.html", '{"url": "https://example.com/articles/alpha-5/"}', '{"url": "x"}, {"url": "y"}')
        self.assertRule("schema", "ItemList has 6 items and the hub has 5 spokes")


class SpokeTests(AuditFixture):
    def test_l3_breadcrumb_and_schema(self):
        self.edit("output/articles/alpha-1/index.html", '<nav aria-label="Breadcrumb"><a href="/articles/alpha/">', '<nav aria-label="Breadcrumb"><a href="/articles/">')
        self.edit("output/articles/alpha-2/index.html", '{"item": "https://example.com/articles/alpha/"}, ', "")
        self.assertRule("L3", "alpha-1: breadcrumb does not link its hub")
        self.assertRule("L3", "alpha-2: BreadcrumbList does not include its hub")

    def test_l4_hub_link_in_the_first_200_words(self):
        self.edit("content/posts/alpha-1.md", "This page belongs to the [alpha hub](/articles/alpha/) and opens there.",
                  "filler " * 201 + "then the [alpha hub](/articles/alpha/).")
        self.edit("content/posts/alpha-2.md", "[alpha hub](/articles/alpha/)", "alpha hub")
        self.assertRule("L4", "alpha-1: does not link /articles/alpha/")
        self.assertRule("L4", "alpha-2: does not link /articles/alpha/")

    def test_l5_siblings_must_be_linked_and_in_the_hub(self):
        self.edit("content/posts/alpha-1.md", "siblings:\n- alpha-2\n- alpha-3", "siblings:\n- alpha-4\n- beta-1")
        self.assertRule("L5", "sibling 'alpha-4' is not linked in the body")
        self.assertRule("L5", "sibling 'beta-1' is not a published post in hub alpha")

    def test_l5_two_links_in_and_out(self):
        self.edit("content/posts/alpha-1.md", "[topic alpha 3](/articles/alpha-3/)", "topic alpha 3")
        self.assertRule("L5", "alpha-1: links 1 post(s) in its own hub")
        self.assertRule("L5", "alpha-3: has 1 inbound body link(s)")

    def test_l6_undeclared_bridge_then_declared(self):
        path = self.root / "content/posts/alpha-1.md"
        path.write_text(path.read_text() + "\nAlso [topic beta 1](/articles/beta-1/).\n")
        self.assertRule("L6", "alpha-1: links /articles/beta-1/ in hub beta without a `bridges` entry")
        self.edit("content/posts/alpha-1.md", "siblings:", "bridges:\n- slug: beta-1\n  reason: Why.\nsiblings:")
        self.assertEqual(self.errors("L6"), [])

    def test_l6_bridge_needs_a_reason_and_a_body_link(self):
        self.edit("content/posts/alpha-1.md", "siblings:", "bridges:\n- slug: beta-1\nsiblings:")
        self.assertRule("L6", "has a bridge with no reason")
        self.assertRule("L6", "declares a bridge to 'beta-1' that the body does not link")

    def test_l7_more_bridges_than_same_hub_links(self):
        path = self.root / "content/posts/alpha-1.md"
        path.write_text(path.read_text() + "\n" + " ".join(
            f"[topic {hub} {n}](/articles/{hub}-{n}/)" for hub, n in (("beta", 1), ("beta", 2), ("gamma", 1))) + "\n")
        self.assertRule("L7", "alpha-1: has 3 bridges and 2 same-hub links")

    def test_l10_money_link_flag_needs_the_body_link(self):
        self.edit("content/posts/alpha-1.md", "siblings:", "money_link: true\nsiblings:")
        self.assertRule("L10", "alpha-1: is flagged money_link")

    def test_l11_related_card_from_another_hub(self):
        self.edit("output/articles/alpha-1/index.html", '<section class="post-related"><a href="/articles/alpha-2/">',
                  '<section class="post-related"><a href="/articles/beta-2/">')
        self.assertRule("L11", "alpha-1: related card /articles/beta-2/ is from hub beta")

    def test_l12_glossary_twin_must_link_the_article(self):
        term = self.root / "output" / "glossary" / "alpha-1"
        term.mkdir(parents=True)
        (term / "index.html").write_text("<html><body><main>definition</main></body></html>")
        self.assertRule("L12", "/glossary/alpha-1/: shares a slug with an article")
        (term / "index.html").write_text('<html><body><main><a href="/articles/alpha-1/">guide</a></main></body></html>')
        self.assertRule("L12", "alpha-1: does not link its glossary term /glossary/alpha-1/")
        path = self.root / "content/posts/alpha-1.md"
        path.write_text(path.read_text() + "\nThe [term](/glossary/alpha-1/) is defined there.\n")
        self.assertEqual(self.errors("L12"), [])

    def test_anchor_rules(self):
        self.edit("content/posts/alpha-1.md", "[topic alpha 2](/articles/alpha-2/)", "[this article](/articles/alpha-2/)")
        self.edit("content/posts/alpha-2.md", "[topic alpha 3](/articles/alpha-3/)", "[October article](/articles/alpha-3/)")
        self.edit("content/posts/alpha-3.md", "[topic alpha 4](/articles/alpha-4/)", "[the alpha piece](/articles/alpha-4/)")
        self.edit("content/posts/alpha-4.md", "[topic alpha 5](/articles/alpha-5/)", "[Post alpha 5](/articles/alpha-5/)")
        self.assertRule("anchor", "banned anchor 'this article'")
        self.assertRule("anchor", "banned anchor 'October article'")
        self.assertRule("anchor", "banned anchor 'the alpha piece'")
        self.assertRule("anchor", "alpha-4: anchor is the full title of /articles/alpha-5/")

    def test_repeated_target_and_one_anchor_for_two_urls(self):
        path = self.root / "content/posts/alpha-1.md"
        path.write_text(path.read_text() + "\nAgain [the second topic](/articles/alpha-2/).\n")
        self.edit("content/posts/beta-1.md", "[topic beta 2](/articles/beta-2/)", "[topic alpha 2](/articles/beta-2/)")
        self.assertRule("anchor", "alpha-1: links /articles/alpha-2/ 2 times")
        self.assertRule("anchor", "'topic alpha 2': is the anchor for 2 URLs")

    def test_hand_written_rules_warn_on_a_post_dated_before_the_cutoff(self):
        self.edit("content/posts/alpha-1.md", "date: 2026-12-01", "date: 2026-11-17")
        self.edit("content/posts/alpha-1.md", "[alpha hub](/articles/alpha/)", "alpha hub")
        self.assertEqual(self.errors("L4"), [])
        self.assertEqual([f.subject for f in self.warnings("L4")], ["alpha-1"])
        self.edit("content/posts/alpha-1.md", "date: 2026-11-17", "date: 2026-11-18")
        self.assertRule("L4", "alpha-1")

    def test_orphan(self):
        for n in (4, 5):
            self.edit(f"content/posts/alpha-{n}.md", "[topic alpha 1](/articles/alpha-1/)", "topic alpha 1")
        self.assertRule("orphan", "alpha-1")


class LlmsAndRedirectTests(AuditFixture):
    def test_spoke_under_the_wrong_heading(self):
        llms = self.root / "output" / "llms.txt"
        line = f"- [Post alpha 1]({BASE}/articles/alpha-1/): post\n"
        text = llms.read_text()
        llms.write_text(text.replace(line, "").replace("## Hub beta\n\n", "## Hub beta\n\n" + line))
        self.assertRule("llms", "alpha-1: llms.txt lists it under ['Hub beta']")

    def test_spoke_missing_or_listed_twice(self):
        llms = self.root / "output" / "llms.txt"
        line = f"- [Post alpha 1]({BASE}/articles/alpha-1/): post\n"
        llms.write_text(llms.read_text().replace(line, line + line))
        self.assertRule("llms", "alpha-1")
        llms.write_text(llms.read_text().replace(line, ""))
        self.assertRule("llms", "alpha-1: llms.txt lists it under no heading")

    def test_redirect_target_outside_the_sitemap(self):
        self.edit("output/_redirects", "/old /articles/alpha/ 301", "/old /articles/retired/ 301")
        self.assertRule("redirect", "/old: target /articles/retired/ is not in the built sitemap")

    def test_redirect_chain_loop_clash_and_shadow(self):
        redirects = self.root / "output" / "_redirects"
        redirects.write_text(redirects.read_text()
                             + "/articles/alpha/ /articles/beta/ 301\n/older /old/ 301\n/older /articles/gamma/ 301\n")
        self.assertRule("redirect", "/articles/alpha/: shadows a built page")
        self.assertRule("redirect", "target /articles/alpha/ is itself redirected")
        self.assertRule("redirect", "/older: has two targets")


if __name__ == "__main__":
    unittest.main()
