#!/usr/bin/env python3
"""Audit the hub-and-spoke model: hub membership, links, queries and the built pages.

The model is declared once. config.toml names the eight hubs, each post's frontmatter
names its hub (`category`), its `primary_query`, its `siblings` and its `bridges`, and
content/pillars/<hub>.yaml holds the hub's curated map. This tool reads those files and
the built site in output/, and reports where they disagree.

Rules, by the numbers the plan gives them (hub-and-spoke plan, 2026-11-17, section 4):

  L1   a hub lists every one of its spokes once, in a named section
  L2   a hub opens with 150 words or more and states an argument
  L3   a spoke shows its hub in the breadcrumb
  L4   a spoke links its hub in its first 200 words
  L5   a spoke names two or three siblings and links them, and has two or more body
       links to and from its own hub
  L6   a link to a post in another hub is declared under `bridges`
  L7   a post has no more bridges than same-hub links
  L8   a hub declares two or three bridges to hubs that exist
  L9   a hub links its money page, and the money page links the hub
  L10  a post flagged `money_link: true` links the money page in its body
  L11  related cards under a post come from its own hub
  L12  a glossary term that shares a slug with an article links that article

Plus: every post has a category and a `primary_query`, no two indexable URLs share a
query, a hub has five spokes or is marked incubating, anchors follow the anchor rules,
llms.txt lists each spoke under its own hub, and every redirect lands on a page in the
sitemap without a loop, a chain or a clash with a built page.

The hand-written rules (L4 to L7, L10, anchors) are errors on a post dated on or after
NEW_FROM and warnings on older posts, until the body retrofit reaches them. Everything
else is an error for every post.

    tools/audit_clusters.py            # full report
    tools/audit_clusters.py --strict   # exit 1 on any error

`primary_query: none` declares that a URL targets no query (an essay). It is exempt
from the uniqueness check.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import pathlib
import re
import sys

try:
    import tomllib
except ImportError:  # Python 3.10
    import tomli as tomllib

import frontmatter
import yaml

# Posts dated from this day are held to the hand-written rules as errors.
NEW_FROM = datetime.date(2026, 11, 18)
MIN_SPOKES = 5
MIN_OPENING_WORDS = 150
HUB_LINK_WORDS = 200

LINK = re.compile(r"\[([^\]]+)\]\(/articles/([a-z0-9][a-z0-9\-\.]*)/?(?:#[^)\s]*)?\)")
INTERNAL = re.compile(r"\[([^\]]+)\]\((/[a-z0-9][a-z0-9/\-\.]*?)/?(?:#[^)\s]*)?\)")
HREF = re.compile(r'href="/articles/([a-z0-9][a-z0-9\-\.]*)/"')
# A link to a tool or a standing page sends a reader somewhere useful, so it counts
# toward the two-outbound minimum even though it is not an article.
NON_ARTICLE_TARGETS = ("/linter/", "/llms-txt-generator/", "/llms-txt-validator/",
                       "/ai-overviews-checker/", "/ai-crawler-checker/", "/glossary/",
                       "/work/", "/projects/", "/portfolio/", "/about/", "/services/")
MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"
BANNED_ANCHORS = re.compile(
    rf"^(this article|this post|here|click here|read more|a separate essay|piece|"
    rf"(?:{MONTHS})(?: (?:article|post|essay))?)$|\bpiece$", re.IGNORECASE)


class Finding:
    def __init__(self, level: str, rule: str, subject: str, message: str):
        self.level, self.rule, self.subject, self.message = level, rule, subject, message

    def __str__(self) -> str:
        return f"{self.level.upper():7} {self.rule:8} {self.subject}: {self.message}"


def normalise_query(query) -> str:
    return re.sub(r"\s+", " ", str(query or "")).strip().lower()


def as_date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def body_text_before(content: str, position: int) -> str:
    """The prose before a position, with comments, tags and link targets removed."""
    text = re.sub(r"<!--.*?-->", " ", content[:position], flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\]\([^)]*\)", "]", text)


def sentence_around(content: str, anchor: str) -> str:
    for line in content.splitlines():
        if anchor in line:
            return re.sub(r"\s+", " ", line).strip()[:200]
    return ""


def main_html(html: str) -> str:
    match = re.search(r"<main\b.*?</main>", html, re.S)
    return match.group(0) if match else html


def json_ld(html: str) -> list:
    blocks = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        blocks.append(json.loads(raw))
    return blocks


class Site:
    """Everything the audit reads, loaded from one root so tests can point it at a fixture."""

    def __init__(self, root: pathlib.Path):
        self.root = root
        self.output = root / "output"
        config = tomllib.loads((root / "config.toml").read_text(encoding="utf-8"))
        self.base = config["site"]["url"].rstrip("/")
        self.hubs = {raw["slug"]: raw for raw in config["content"].get("categories", [])}
        self.tools = {raw["slug"]: raw for raw in config["content"].get("tools", [])}
        aliases = root / "content" / "post-slug-aliases.json"
        self.aliases = json.loads(aliases.read_text()) if aliases.exists() else {}

        self.posts: dict[str, dict] = {}
        for path in sorted((root / "content" / "posts").glob("*.md")):
            data = frontmatter.load(path)
            if data.get("status") != "published":
                continue
            slug = data.get("slug") or path.stem
            published = as_date(data.get("date"))
            self.posts[slug] = {
                "hub": data.get("category"),
                "query": data.get("primary_query"),
                "siblings": data.get("siblings") or [],
                "bridges": [b.get("slug") for b in data.get("bridges") or [] if isinstance(b, dict)],
                "bridge_reasons": all(isinstance(b, dict) and str(b.get("reason") or "").strip()
                                      for b in data.get("bridges") or []),
                "money_link": bool(data.get("money_link")),
                "content": data.content,
                "title": str(data.get("title", slug)),
                "new": bool(published and published >= NEW_FROM),
            }

        self.pillars: dict[str, dict] = {}
        for slug in self.hubs:
            path = root / "content" / "pillars" / f"{slug}.yaml"
            self.pillars[slug] = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.is_file() else None

        self.services: dict[str, dict] = {}
        index = root / "content" / "services.md"
        for path in ([index] if index.is_file() else []) + sorted((root / "content" / "services").glob("*.md")):
            data = frontmatter.load(path)
            if data.get("status") != "published":
                continue
            url = "/services/" if path == index else f"/services/{data.get('slug') or path.stem}/"
            self.services[url] = {"query": data.get("primary_query")}

    def page(self, url: str) -> str | None:
        path = self.output / url.strip("/") / "index.html"
        return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else None

    def hub_posts(self, hub: str) -> list[str]:
        return [slug for slug, post in self.posts.items() if post["hub"] == hub]

    def pillar_spokes(self, hub: str) -> tuple[list[str], list[str]]:
        """(post slugs, tool slugs) a hub's pillar file lists, in order, with repeats."""
        posts, tools = [], []
        for section in (self.pillars.get(hub) or {}).get("sections") or []:
            for entry in section.get("spokes") or []:
                if "post" in entry:
                    posts.append(entry["post"])
                elif "tool" in entry:
                    tools.append(entry["tool"])
        return posts, tools


def audit(site: Site) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    posts, hubs = site.posts, site.hubs

    def add(level, rule, subject, message):
        findings.append(Finding(level, rule, subject, message))

    def hand_written(slug, rule, message):
        """A hand-written rule: an error on a new post, a warning on an old one."""
        add("error" if posts[slug]["new"] else "warning", rule, slug, message)

    # --- membership and queries -------------------------------------------------
    for slug, post in posts.items():
        if not post["hub"]:
            add("error", "category", slug, "has no category")
        elif post["hub"] not in hubs:
            add("error", "category", slug, f"category {post['hub']!r} is not a hub in config.toml")
        if not normalise_query(post["query"]):
            add("error", "query", slug, "has no primary_query (use `none` for a page that targets no query)")

    owners = collections.defaultdict(list)
    for slug, post in posts.items():
        owners[normalise_query(post["query"])].append(f"/articles/{slug}/")
    for slug, hub in hubs.items():
        if not normalise_query(hub.get("primary_query")):
            add("error", "query", f"hub {slug}", "has no primary_query in config.toml")
        owners[normalise_query(hub.get("primary_query"))].append(f"/articles/{slug}/")
    for slug, tool in site.tools.items():
        if not normalise_query(tool.get("primary_query")):
            add("error", "query", f"tool {slug}", "has no primary_query in config.toml")
        owners[normalise_query(tool.get("primary_query"))].append(f"/{slug}/")
    for url, service in site.services.items():
        if not normalise_query(service["query"]):
            add("error", "query", url, "has no primary_query in its frontmatter")
        owners[normalise_query(service["query"])].append(url)
    for query, urls in sorted(owners.items()):
        if query and query != "none" and len(urls) > 1:
            add("error", "query", query, f"is the primary_query of {len(urls)} URLs: {', '.join(sorted(urls))}")

    # --- link graph from post bodies -------------------------------------------
    same_out = collections.defaultdict(list)      # slug -> same-hub targets, in body order
    cross_out = collections.defaultdict(list)     # slug -> other-hub targets
    same_in = collections.Counter()
    inbound = collections.Counter()
    outbound = collections.Counter()
    anchors = collections.defaultdict(set)        # anchor text -> {target URL}
    anchor_users = collections.defaultdict(set)
    crossings = []
    for slug, post in posts.items():
        seen_targets = collections.Counter()
        for _anchor, target in INTERNAL.findall(post["content"]):
            if (target.rstrip("/") + "/").startswith(NON_ARTICLE_TARGETS):
                outbound[slug] += 1
        for anchor, target in LINK.findall(post["content"]):
            target = site.aliases.get(target, target)
            if target == slug or (target not in posts and target not in hubs):
                continue
            url = f"/articles/{target}/"
            text = re.sub(r"[*_`]", "", anchor).strip()
            anchors[text.lower()].add(url)
            anchor_users[text.lower()].add(slug)
            seen_targets[url] += 1
            if BANNED_ANCHORS.search(text):
                hand_written(slug, "anchor", f"banned anchor {text!r} on {url}")
            if target in posts and text.lower() == posts[target]["title"].lower():
                hand_written(slug, "anchor", f"anchor is the full title of {url}")
            if target in hubs:
                outbound[slug] += 1
                continue
            if seen_targets[url] > 1:
                continue
            outbound[slug] += 1
            inbound[target] += 1
            if posts[target]["hub"] == post["hub"]:
                same_out[slug].append(target)
                same_in[target] += 1
            else:
                cross_out[slug].append(target)
                declared = target in post["bridges"]
                crossings.append((slug, post["hub"], target, posts[target]["hub"], anchor, declared,
                                  sentence_around(post["content"], anchor)))
                if not declared:
                    hand_written(slug, "L6", f"links {url} in hub {posts[target]['hub']} without a `bridges` entry")
        for url, count in seen_targets.items():
            if count > 1:
                hand_written(slug, "anchor", f"links {url} {count} times in one body")
    for text, targets in sorted(anchors.items()):
        if len(targets) > 1:
            users = sorted(anchor_users[text])
            level = "error" if any(posts[user]["new"] for user in users) else "warning"
            add(level, "anchor", repr(text), f"is the anchor for {len(targets)} URLs "
                f"({', '.join(sorted(targets))}) in {', '.join(users)}")

    # --- per-post hand-written rules ---------------------------------------------
    for slug, post in posts.items():
        hub = post["hub"]
        if hub not in hubs:
            continue
        hub_link = re.search(rf"\]\(/articles/{re.escape(hub)}/?(?:#[^)\s]*)?\)", post["content"])
        if not hub_link or len(body_text_before(post["content"], hub_link.start()).split()) > HUB_LINK_WORDS:
            hand_written(slug, "L4", f"does not link /articles/{hub}/ in its first {HUB_LINK_WORDS} words")
        siblings = post["siblings"]
        if not 2 <= len(siblings) <= 3:
            hand_written(slug, "L5", f"declares {len(siblings)} siblings; it needs two or three")
        for sibling in siblings:
            if sibling not in posts or posts[sibling]["hub"] != hub:
                hand_written(slug, "L5", f"sibling {sibling!r} is not a published post in hub {hub}")
            elif sibling not in same_out[slug]:
                hand_written(slug, "L5", f"sibling {sibling!r} is not linked in the body")
        if len(same_out[slug]) < 2:
            hand_written(slug, "L5", f"links {len(same_out[slug])} post(s) in its own hub; it needs two")
        if same_in[slug] < 2:
            hand_written(slug, "L5", f"has {same_in[slug]} inbound body link(s) from its own hub; it needs two")
        for target in post["bridges"]:
            if target not in posts:
                add("error", "L6", slug, f"bridge {target!r} is not a published post")
            elif posts[target]["hub"] == hub:
                add("error", "L6", slug, f"bridge {target!r} is in the same hub; list it under siblings")
            elif target not in cross_out[slug]:
                hand_written(slug, "L6", f"declares a bridge to {target!r} that the body does not link")
        if not post["bridge_reasons"]:
            add("error", "L6", slug, "has a bridge with no reason")
        if len(cross_out[slug]) > len(same_out[slug]):
            hand_written(slug, "L7", f"has {len(cross_out[slug])} bridges and {len(same_out[slug])} same-hub links")
        money = hubs[hub].get("money_page")
        if post["money_link"] and money and f"]({money})" not in post["content"]:
            hand_written(slug, "L10", f"is flagged money_link and does not link {money} in its body")

    # --- hubs: pillar file, built page, money page -------------------------------
    sitemap_paths = set()
    sitemap = site.output / "sitemap.xml"
    if sitemap.is_file():
        sitemap_paths = {loc[len(site.base):] for loc in
                         re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8"))}
    table = {}
    for hub, raw in hubs.items():
        members = site.hub_posts(hub)
        pillar = site.pillars[hub]
        listed_posts, listed_tools = site.pillar_spokes(hub)
        spoke_count = len(members) + len(listed_tools)
        table[hub] = {
            "spokes": spoke_count,
            "inside": sum(len(same_out[slug]) for slug in members),
            "bridges": sum(len(cross_out[slug]) for slug in members),
            "L4": sum(1 for f in findings if f.rule == "L4" and f.subject in members),
            "L5": len({f.subject for f in findings if f.rule == "L5" and f.subject in members}),
        }
        if not members:
            continue
        if pillar is None:
            add("error", "L1", f"hub {hub}", f"has no content/pillars/{hub}.yaml")
            continue
        if spoke_count < MIN_SPOKES and not raw.get("incubating"):
            add("error", "spokes", f"hub {hub}", f"has {spoke_count} spokes, under {MIN_SPOKES}, and is not marked incubating")
        for slug in listed_posts:
            if slug not in posts or posts[slug]["hub"] != hub:
                add("error", "L1", f"hub {hub}", f"a section names {slug!r}, which is not a published post of this hub")
        for slug, count in collections.Counter(listed_posts).items():
            if count > 1:
                add("error", "L1", f"hub {hub}", f"lists {slug!r} in {count} sections")
        for slug in members:
            if slug not in listed_posts:
                add("error", "L1", f"hub {hub}", f"published spoke {slug!r} is in no section")
        for tool in listed_tools:
            if tool not in site.tools:
                add("error", "L1", f"hub {hub}", f"a section names unknown tool {tool!r}")
        for section in pillar.get("sections") or []:
            for entry in section.get("spokes") or []:
                if not str(entry.get("note") or "").strip():
                    add("error", "L1", f"hub {hub}", f"spoke {entry.get('post') or entry.get('tool')!r} has no sentence of context")

        if not str(pillar.get("argument") or "").strip():
            add("error", "L2", f"hub {hub}", "states no argument")
        opening = " ".join(str(pillar.get(key) or "") for key in ("lead", "intro", "argument"))
        words = len(re.sub(r"\]\([^)]*\)", "]", opening).split())
        if words < MIN_OPENING_WORDS:
            add("error", "L2", f"hub {hub}", f"opens with {words} words, under {MIN_OPENING_WORDS}")

        bridges = pillar.get("bridges") or []
        if not 2 <= len(bridges) <= 3:
            add("error", "L8", f"hub {hub}", f"declares {len(bridges)} bridges; it needs two or three")
        for bridge in bridges:
            target = bridge.get("hub")
            if target not in hubs or target == hub:
                add("error", "L8", f"hub {hub}", f"bridge to {target!r}, which is not another hub")
            elif f"](/articles/{target}/)" not in str(bridge.get("text") or ""):
                add("error", "L8", f"hub {hub}", f"the bridge to {target!r} does not link it in a sentence")

        flagged = [slug for slug in members if posts[slug]["money_link"]]
        if not 2 <= len(flagged) <= 5:
            add("warning", "L10", f"hub {hub}", f"has {len(flagged)} posts flagged money_link; the target is two to five")

        url = f"/articles/{hub}/"
        html = site.page(url)
        if html is None:
            add("error", "L1", f"hub {hub}", f"{url} is not built")
            continue
        main = main_html(html)
        for slug in members:
            count = main.count(f'href="/articles/{slug}/"')
            if count != 1:
                add("error", "L1", f"hub {hub}", f"the built page links /articles/{slug}/ {count} times; it must be once")
        money = raw.get("money_page")
        if not money:
            add("error", "L9", f"hub {hub}", "has no money_page in config.toml")
        else:
            if f'href="{money}"' not in main:
                add("error", "L9", f"hub {hub}", f"the built page does not link its money page {money}")
            money_html = site.page(money)
            if money_html is None:
                add("error", "L9", f"hub {hub}", f"money page {money} is not built")
            elif f'href="{url}"' not in main_html(money_html):
                add("error", "L9", f"hub {hub}", f"money page {money} does not link the hub back")
        lists = [block["mainEntity"].get("itemListElement", []) for block in json_ld(html)
                 if isinstance(block, dict) and block.get("@type") == "CollectionPage"
                 and isinstance(block.get("mainEntity"), dict)]
        if not lists:
            add("error", "schema", f"hub {hub}", "the built page has no CollectionPage with an ItemList")
        elif len(lists[0]) != spoke_count:
            add("error", "schema", f"hub {hub}", f"ItemList has {len(lists[0])} items and the hub has {spoke_count} spokes")
        indexable = "noindex" not in (re.search(r'<meta name="robots" content="([^"]*)"', html) or [None, ""])[1]
        if raw.get("incubating") or spoke_count < MIN_SPOKES:
            if indexable or url in sitemap_paths:
                add("error", "spokes", f"hub {hub}", "is incubating and must be noindex and out of the sitemap")
        elif sitemap_paths and url not in sitemap_paths:
            add("error", "spokes", f"hub {hub}", f"{url} is missing from the sitemap")

    # --- built spokes: breadcrumb and related cards -------------------------------
    for slug, post in posts.items():
        hub = post["hub"]
        if hub not in hubs:
            continue
        html = site.page(f"/articles/{slug}/")
        if html is None:
            add("error", "L3", slug, "is not built")
            continue
        crumb = re.search(r'<nav aria-label="Breadcrumb".*?</nav>', html, re.S)
        if not crumb or f'href="/articles/{hub}/"' not in crumb.group(0):
            add("error", "L3", slug, f"breadcrumb does not link its hub /articles/{hub}/")
        crumbs = [block for block in json_ld(html) if isinstance(block, dict) and block.get("@type") == "BreadcrumbList"]
        if not crumbs or f"{site.base}/articles/{hub}/" not in [item.get("item") for item in crumbs[0].get("itemListElement", [])]:
            add("error", "L3", slug, "BreadcrumbList does not include its hub")
        related = re.search(r'<section class="post-related".*?</section>', html, re.S)
        for target in HREF.findall(related.group(0)) if related else []:
            if target in posts and posts[target]["hub"] != hub:
                add("error", "L11", slug, f"related card /articles/{target}/ is from hub {posts[target]['hub']}")

    # --- glossary twins -----------------------------------------------------------
    for slug in posts:
        term = site.page(f"/glossary/{slug}/")
        if term is not None and f'href="/articles/{slug}/"' not in main_html(term):
            add("error", "L12", f"/glossary/{slug}/", f"shares a slug with an article and does not link /articles/{slug}/")

    # --- llms.txt -------------------------------------------------------------------
    llms = site.output / "llms.txt"
    if llms.is_file():
        heading, under = "", {}
        for line in llms.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                heading = line[3:].strip()
            for target in re.findall(r"\]\(" + re.escape(site.base) + r"/articles/([^/)]+)/\)", line):
                under.setdefault(target, []).append(heading)
        for slug, post in posts.items():
            want = hubs.get(post["hub"], {}).get("title")
            if under.get(slug) != [want]:
                add("error", "llms", slug, f"llms.txt lists it under {under.get(slug) or 'no heading'}, not once under {want!r}")
    else:
        add("error", "llms", "llms.txt", "is not built")

    # --- redirects --------------------------------------------------------------------
    redirects = site.output / "_redirects"
    rules = {}
    if redirects.is_file():
        for line in redirects.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) < 2 or line.lstrip().startswith("#"):
                continue
            source, target = parts[0], parts[1]
            if source in rules and rules[source] != target:
                add("error", "redirect", source, f"has two targets: {rules[source]} and {target}")
            rules[source] = target
        for source, target in rules.items():
            if target.startswith("http"):
                continue
            if target not in sitemap_paths:
                add("error", "redirect", source, f"target {target} is not in the built sitemap")
            if target in rules or target.rstrip("/") in rules:
                add("error", "redirect", source, f"target {target} is itself redirected (a chain or a loop)")
            if (site.output / source.strip("/") / "index.html").is_file():
                add("error", "redirect", source, "shadows a built page")
    else:
        add("error", "redirect", "_redirects", "is not built")

    # --- orphans, as before: inbound from editorial pages only -------------------------
    template_inbound = collections.Counter()
    for page in site.output.rglob("*.html"):
        rel = page.relative_to(site.output).as_posix()
        if rel in ("index.html", "articles/index.html") or rel.startswith("articles/page/"):
            continue
        source = rel[len("articles/"):-len("/index.html")] if rel.startswith("articles/") and rel.endswith("/index.html") else None
        if source in posts or source in hubs:
            continue  # bodies are counted above; a hub lists every spoke by design
        html = page.read_text(encoding="utf-8", errors="replace")
        for target in set(HREF.findall(html)):
            target = site.aliases.get(target, target)
            if target in posts:
                template_inbound[target] += 1
    orphans = [slug for slug in posts if inbound[slug] + template_inbound[slug] == 0]
    for slug in orphans:
        add("error", "orphan", slug, "no article body or hand-written page links it")
    thin = [slug for slug in posts if outbound[slug] < 2]
    for slug in thin:
        hand_written(slug, "outbound", f"has {outbound[slug]} outbound internal link(s); it needs two")

    glossary_unlinked = []
    if (site.output / "glossary" / "index.html").is_file():
        terms = sorted(d.name for d in (site.output / "glossary").iterdir() if (d / "index.html").is_file())
        linked = set()
        for page in site.output.rglob("*.html"):
            rel = page.relative_to(site.output).as_posix()
            if rel.startswith("glossary/") or rel in ("index.html", "articles/index.html"):
                continue
            linked.update(re.findall(r'href="/glossary/([a-z0-9-]+)/"', page.read_text(encoding="utf-8", errors="replace")))
        glossary_unlinked = [term for term in terms if term not in linked]

    return findings, {"table": table, "crossings": crossings, "orphans": orphans, "thin": thin,
                      "glossary_unlinked": glossary_unlinked, "same_out": same_out, "same_in": same_in,
                      "cross_out": cross_out}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="exit 1 on any error")
    ap.add_argument("--root", default=".", help="repository root (default: the current directory)")
    ap.add_argument("--quiet", action="store_true", help="print errors and the hub table only")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.root)
    if not (root / "config.toml").is_file() or not (root / "content" / "posts").is_dir():
        print("config.toml or content/posts is missing: run from the repo root")
        return 2
    # Breadcrumbs, related cards, llms.txt and redirects exist only in the built site.
    # Without a build every one of those checks would report a false failure or, worse,
    # nothing at all, so refuse instead of guessing.
    if not (root / "output" / "sitemap.xml").is_file():
        print("output/ is missing or unbuilt: run `python build.py` first.")
        return 2
    site = Site(root)
    if not site.posts:
        print("no published posts found: run from the repo root")
        return 2

    findings, report = audit(site)
    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    print(f"{len(site.posts)} published posts in {len(site.hubs)} hubs\n")
    print(f"  {'hub':28} {'spokes':>6} {'inside':>6} {'bridges':>7} {'fail L4':>7} {'fail L5':>7}")
    for hub, row in report["table"].items():
        print(f"  {hub:28} {row['spokes']:>6} {row['inside']:>6} {row['bridges']:>7} {row['L4']:>7} {row['L5']:>7}")
    print("\n  spokes: posts plus the tools the hub lists. inside: body links between posts of the hub.")
    print("  bridges: body links to posts in other hubs. fail L4, fail L5: posts failing each rule.")

    print(f"\n--- errors: {len(errors)} ---")
    for finding in errors:
        print(f"  {finding}")
    if not args.quiet:
        print(f"\n--- warnings: {len(warnings)} (posts dated before {NEW_FROM}, until the body retrofit) ---")
        for finding in warnings:
            print(f"  {finding}")
        print(f"\n--- glossary terms nothing outside /glossary/ links: {len(report['glossary_unlinked'])} ---")
        for term in report["glossary_unlinked"]:
            print(f"  {term}")
        undeclared = [c for c in report["crossings"] if not c[5]]
        print(f"\n--- links between hubs: {len(report['crossings'])}, {len(undeclared)} undeclared ---")
        for src, sh, dst, dh, anchor, _declared, sentence in undeclared:
            print(f"\n  {src}  [{sh}]\n    -> {dst}  [{dh}]\n    anchor: {anchor}\n    {sentence}")
    else:
        print(f"\n{len(warnings)} warning(s) not shown")

    return 1 if args.strict and errors else 0


if __name__ == "__main__":
    sys.exit(main())
