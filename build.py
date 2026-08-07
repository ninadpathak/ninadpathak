#!/usr/bin/env python3
"""
Ninad Pathak | Static Site Generator
Requires Python 3.9+

Usage:
  python build.py           Build site to /output
  python build.py --serve   Build then serve at localhost:8000
  python build.py --drafts  Include draft posts
"""

import os
import re
import struct
import sys
import shutil
import http.server
import threading
import xml.etree.ElementTree as ET
from datetime import datetime, date, time, timezone
from email.utils import format_datetime as format_rfc2822_date
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import frontmatter
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from pygments.formatters import HtmlFormatter
from rule_checker import paragraph_sentence_violations

# Always resolve paths relative to this script's directory
ROOT = Path(__file__).parent.resolve()
os.chdir(ROOT)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return re.sub(r"^-+|-+$", "", text)


def format_date(d) -> str:
    if isinstance(d, str):
        try:
            d = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            return d
    if isinstance(d, (datetime,)):
        d = d.date()
    if isinstance(d, date):
        return d.strftime("%b %d, %Y")
    return str(d)


def format_date_iso(d) -> str:
    if isinstance(d, str):
        return d
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d")
    if isinstance(d, date):
        return d.strftime("%Y-%m-%d")
    return str(d)


def estimate_reading_time(content: str) -> int:
    words = len(content.split())
    return max(1, round(words / 200))


def count_words(content: str) -> int:
    return len(content.split())


def _png_dimensions(path: Path):
    """Return a PNG's intrinsic dimensions without adding an image dependency."""
    try:
        with path.open("rb") as image:
            header = image.read(24)
    except OSError:
        return None

    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", header[16:24])


def optimize_content_images(html: str) -> str:
    """Add lazy decoding and intrinsic sizing to local PNGs in rendered content."""
    image_pattern = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
    source_pattern = re.compile(r"\bsrc\s*=\s*(['\"])(.*?)\1", re.IGNORECASE)

    def optimize(match: re.Match) -> str:
        tag = match.group(0)
        source_match = source_pattern.search(tag)
        if not source_match:
            return tag

        source = source_match.group(2).split("?", 1)[0].split("#", 1)[0]
        if not source.startswith("/static/"):
            return tag

        attributes = []
        if not re.search(r"\bloading\s*=", tag, re.IGNORECASE):
            attributes.append('loading="lazy"')
        if not re.search(r"\bdecoding\s*=", tag, re.IGNORECASE):
            attributes.append('decoding="async"')

        if not re.search(r"\b(?:width|height)\s*=", tag, re.IGNORECASE):
            image_path = (ROOT / source.lstrip("/")).resolve()
            try:
                image_path.relative_to((ROOT / "static").resolve())
            except ValueError:
                image_path = None

            dimensions = _png_dimensions(image_path) if image_path else None
            if dimensions:
                width, height = dimensions
                attributes.extend((f'width="{width}"', f'height="{height}"'))

        if not attributes:
            return tag

        suffix = " />" if tag.endswith("/>") else ">"
        body = tag[:-2].rstrip() if tag.endswith("/>") else tag[:-1].rstrip()
        return f"{body} {' '.join(attributes)}{suffix}"

    return image_pattern.sub(optimize, html)


def _clean_inline_md(text: str) -> str:
    """Strip inline markdown so a string is safe/clean for JSON-LD text fields."""
    text = text.strip()
    # links: [label](url) -> label
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # bold/italic markers and inline code backticks
    text = re.sub(r"(\*\*|__|\*|_|`)", "", text)
    # collapse whitespace
    return re.sub(r"\s+", " ", text).strip()


def extract_faqs(md_content: str) -> list[dict]:
    """Pull Q&A pairs from a markdown FAQ section.

    Recognises a section heading like '## FAQ' or '## Frequently Asked Questions'
    and parses questions written either as '### Question' or as a bold-only line
    '**Question?**', with the following paragraphs as the answer. Returns a list of
    {"question", "answer"} dicts (empty if no FAQ section is present).
    """
    lines = md_content.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^##\s+(FAQ|Frequently\s+Asked\s+Questions?)\s*$", line.strip(), re.IGNORECASE):
            start = i + 1
            break
    if start is None:
        return []

    faqs = []
    question = None
    answer_parts: list[str] = []

    def flush():
        if question and answer_parts:
            faqs.append({
                "question": _clean_inline_md(question),
                "answer": _clean_inline_md(" ".join(answer_parts)),
            })

    for line in lines[start:]:
        stripped = line.strip()
        # End of the FAQ section: next h2 (that isn't another question)
        if re.match(r"^##\s+", stripped) and not re.match(r"^##\s+(FAQ|Frequently)", stripped, re.IGNORECASE):
            break
        # Question forms
        m_h3 = re.match(r"^###\s+(.*\S)\s*$", stripped)
        m_bold = re.match(r"^\*\*(.+?)\*\*:?\s*$", stripped)
        if m_h3 or m_bold:
            flush()
            question = (m_h3 or m_bold).group(1)
            answer_parts = []
            continue
        if question and stripped:
            answer_parts.append(stripped)
    flush()
    return faqs


def sort_key(post: dict):
    d = post.get("date")
    if isinstance(d, datetime):
        published = d.date()
    elif isinstance(d, date):
        published = d
    elif isinstance(d, str):
        try:
            published = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            published = date.min
    else:
        published = date.min
    # Date ties are common. A stable slug tie-breaker keeps generated pages
    # identical across filesystems and CI runners.
    return published, post.get("slug", "")


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class SiteBuilder:
    def __init__(self, config_path: str = "config.toml", include_drafts: bool = False):
        with open(config_path, "rb") as f:
            self.config = tomllib.load(f)

        self.include_drafts = include_drafts
        self.output = Path("output")

        self.env = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.filters["format_date"] = format_date
        self.env.filters["format_date_iso"] = format_date_iso
        self.env.filters["slugify"] = slugify

        self.md = markdown.Markdown(
            extensions=["extra", "codehilite", "toc", "tables"],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "guess_lang": False,
                },
                "toc": {
                    "toc_depth": "2-3",
                },
            },
        )

    # ------------------------------------------------------------------
    # Data loaders
    # ------------------------------------------------------------------

    def load_posts(self) -> list[dict]:
        obsidian = self.config["content"].get("obsidian_path", "").strip()
        posts_dir = Path(obsidian) if obsidian and Path(obsidian).exists() else Path("content/posts")
        posts_dir.mkdir(parents=True, exist_ok=True)

        posts = []
        for md_file in posts_dir.rglob("*.md"):
            post = frontmatter.load(md_file)
            status = post.get("status", "draft")
            if status != "published" and not self.include_drafts:
                continue

            paragraph_issues = paragraph_sentence_violations(post.content)
            if paragraph_issues:
                details = "\n".join(
                    f"    line {line}: {count} sentences — {snippet}"
                    for line, count, snippet in paragraph_issues
                )
                raise ValueError(
                    f"{md_file} violates the two-sentence paragraph rule:\n{details}"
                )
            self.md.reset()
            html = optimize_content_images(self.md.convert(post.content))
            # Extract TOC from markdown if available
            toc_html = getattr(self.md, 'toc', '') if hasattr(self.md, 'toc') else ''
            slug = post.get("slug") or slugify(md_file.stem)

            posts.append({
                "title": post.get("title", md_file.stem),
                "date": post.get("date"),
                "updated": post.get("updated") or post.get("date"),
                "description": post.get("description", ""),
                "tags": post.get("tags", []),
                "declared_category": post.get("category", ""),
                "takeaways": post.get("takeaways", []),
                "status": status,
                "content": html,
                "slug": slug,
                "reading_time": estimate_reading_time(post.content),
                "word_count": count_words(post.content),
                "url": f"/articles/{slug}/",
                "toc": toc_html,
                "faqs": extract_faqs(post.content),
                "has_code": 'class="highlight"' in html,
                "has_visuals": "<iframe" in html,
                "has_flowchart": 'class="flowchart' in html,
            })

        return sorted(posts, key=sort_key, reverse=True)

    def load_categories(self, posts: list[dict]) -> list[dict]:
        """Resolve one editorial category per post without changing article URLs."""
        configured = self.config["content"].get("categories", [])
        categories = []
        by_slug = {}
        for raw in configured:
            category = {
                "slug": raw["slug"],
                "title": raw["title"],
                "description": raw["description"],
                "intro": raw.get("intro", raw["description"]),
                "tag_matches": {str(tag).lower() for tag in raw.get("tag_matches", [])},
                "posts": [],
            }
            category["url"] = f"/articles/{category['slug']}/"
            categories.append(category)
            by_slug[category["slug"]] = category

        for post in posts:
            explicit = post.get("declared_category", post.get("category", ""))
            if isinstance(explicit, dict):
                explicit = explicit.get("slug", "")
            category = by_slug.get(str(explicit)) if explicit else None
            if category is None:
                post_tags = {str(tag).lower() for tag in post.get("tags", [])}
                category = next((candidate for candidate in categories if post_tags & candidate["tag_matches"]), None)
            if category is not None:
                category["posts"].append(post)
                post["category"] = category
            else:
                post["category"] = None
        return categories

    def load_work(self) -> list[dict]:
        work_dir = Path("content/work")
        cases = []
        for md_file in sorted(work_dir.glob("*.md")):
            post = frontmatter.load(md_file)
            self.md.reset()
            html = optimize_content_images(self.md.convert(post.content))
            slug = md_file.stem
            cases.append({
                **post.metadata,
                "content": html,
                "slug": slug,
                "url": f"/work/{slug}/",
            })
        return cases

    def load_portfolio(self) -> dict:
        with open("content/portfolio.yaml") as f:
            return yaml.safe_load(f)

    def load_projects(self) -> list[dict]:
        with open("content/projects.yaml") as f:
            data = yaml.safe_load(f)
        return data.get("projects", [])

    def load_md_content(self, path: str) -> tuple[dict, str]:
        post = frontmatter.load(path)
        self.md.reset()
        return post.metadata, optimize_content_images(self.md.convert(post.content))

    def load_legal_pages(self) -> list[dict]:
        pages = []
        legal_dir = Path("content/legal")
        if not legal_dir.exists():
            return pages

        for md_file in sorted(legal_dir.glob("*.md")):
            meta, content = self.load_md_content(str(md_file))
            slug = meta.get("slug") or md_file.stem
            pages.append({
                "title": meta.get("title", md_file.stem.replace("-", " ").title()),
                "description": meta.get("description", self.config["site"]["description"]),
                "slug": slug,
                "label": meta.get("label", meta.get("title", md_file.stem.replace("-", " ").title())),
                "intro": meta.get("intro", ""),
                "content": content,
                "url": f"/{slug}/",
            })
        return pages

    def load_pillars(self, posts) -> list[dict]:
        """Load topic pillar/hub pages from content/pillars/*.yaml and resolve
        their curated post-slug lists against the live post set."""
        pillars_dir = Path("content/pillars")
        if not pillars_dir.exists():
            return []
        by_slug = {p["slug"]: p for p in posts}

        pillars = []
        for f in sorted(pillars_dir.glob("*.yaml")):
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            if data.get("status", "published") != "published" and not self.include_drafts:
                continue

            self.md.reset()
            data["intro_html"] = self.md.convert(data["intro"]) if data.get("intro") else ""

            resolved = []
            all_posts = []
            seen = set()
            for sec in data.get("sections", []):
                sec_posts = []
                for slug in sec.get("posts", []):
                    p = by_slug.get(slug)
                    if not p:
                        print(f"  ! pillar '{data['slug']}': unknown post slug '{slug}'")
                        continue
                    sec_posts.append(p)
                    if slug not in seen:
                        all_posts.append(p)
                        seen.add(slug)
                resolved.append({
                    "heading": sec["heading"],
                    "blurb": sec.get("blurb", ""),
                    "posts": sec_posts,
                })
            data["resolved_sections"] = resolved
            data["all_posts"] = all_posts
            data["post_count"] = len(all_posts)
            data["url"] = f"/articles/#{data['slug']}"
            data.setdefault("h1", data.get("title", data["slug"]))
            pillars.append(data)
        return pillars

    def load_glossary(self) -> list[dict]:
        glossary_path = Path("content/data/glossary.yaml")
        if not glossary_path.exists():
            return []
        with open(glossary_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data.get("status", "published") != "published":
            return []

        terms = data.get("terms", [])
        for term in terms:
            term["url"] = f"/glossary/{term['slug']}/"
            
        return terms

    # ------------------------------------------------------------------
    # Render helper
    # ------------------------------------------------------------------

    def render(self, template_name: str, output_path: str, page: str = "", **ctx):
        template = self.env.get_template(template_name)
        ctx["site"] = self.config["site"]
        ctx["contact"] = self.config["contact"]
        ctx["current_page"] = page
        ctx["build_year"] = datetime.now().year
        ctx["latest_posts"] = getattr(self, "latest_posts", [])

        html = template.render(**ctx)
        out = self.output / output_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")

    # ------------------------------------------------------------------
    # Page builders
    # ------------------------------------------------------------------

    def build_homepage(self, posts, work_cases):
        self.render(
            "index.html", "index.html",
            page="home",
            recent_posts=posts[:4],
            featured_cases=work_cases[:3],
        )

    def build_blog_list(self, posts, categories):
        posts_per_page = 20
        total_pages = (len(posts) + posts_per_page - 1) // posts_per_page if posts else 1

        for i in range(total_pages):
            page_num = i + 1
            start = i * posts_per_page
            end = start + posts_per_page
            page_posts = posts[start:end]

            # Determine output path
            if page_num == 1:
                output_path = "articles/index.html"
            else:
                output_path = f"articles/page/{page_num}/index.html"

            # Pagination URLs
            prev_url = None
            if page_num > 1:
                prev_url = "/articles/" if page_num == 2 else f"/articles/page/{page_num - 1}/"

            next_url = None
            if page_num < total_pages:
                next_url = f"/articles/page/{page_num + 1}/"

            self.render(
                "blog_list.html", output_path,
                page="articles",
                posts=page_posts,
                categories=categories,
                current_page_num=page_num,
                total_pages=total_pages,
                prev_url=prev_url,
                next_url=next_url,
            )

    def build_category_archives(self, categories):
        for category in categories:
            self.render(
                "category_archive.html",
                f"articles/{category['slug']}/index.html",
                page="articles",
                category=category,
                posts=category["posts"],
            )

    def build_posts(self, posts):
        for post in posts:
            # find related posts (same tag, different slug)
            related = [
                p for p in posts
                if p["slug"] != post["slug"]
                and any(t in post.get("tags", []) for t in p.get("tags", []))
            ][:3]
            self.render(
                "post.html",
                f"articles/{post['slug']}/index.html",
                page="articles",
                post=post,
                related=related,
            )

    def build_work_list(self, work_cases):
        self.render(
            "work.html", "work/index.html",
            page="work",
            cases=work_cases,
        )

    def build_work_pages(self, work_cases):
        for case in work_cases:
            self.render(
                "work_single.html",
                f"work/{case['slug']}/index.html",
                page="work",
                case=case,
            )

    def build_portfolio(self, portfolio):
        self.render(
            "portfolio.html", "portfolio/index.html",
            page="portfolio",
            portfolio=portfolio,
        )

    def build_projects(self, projects):
        self.render(
            "projects.html", "projects/index.html",
            page="projects",
            projects=projects,
        )

    def build_about(self):
        meta, content = self.load_md_content("content/about.md")
        self.render(
            "about.html", "about/index.html",
            page="about",
            meta=meta,
            content=content,
        )

    def build_contact(self):
        self.render(
            "contact.html", "contact/index.html",
            page="contact",
        )

    def build_404(self):
        self.render(
            "404.html", "404.html",
            page="404",
        )

    def build_linter(self):
        self.render(
            "linter.html", "linter/index.html",
            page="linter",
        )

    def build_llms_txt_generator(self):
        self.render(
            "llms_txt_generator.html", "llms-txt-generator/index.html",
            page="llms-txt-generator",
        )

    def build_legal_pages(self, legal_pages):
        for legal_page in legal_pages:
            self.render(
                "page.html",
                f"{legal_page['slug']}/index.html",
                page=legal_page["slug"],
                legal_page=legal_page,
            )

    def build_glossary(self, terms):
        if not terms:
            return
            
        # Build index
        self.render(
            "glossary_index.html", "glossary/index.html",
            page="glossary",
            terms=terms,
        )
        
        # Build individual term pages
        for term in terms:
            self.render(
                "glossary_term.html",
                f"glossary/{term['slug']}/index.html",
                page="glossary",
                term=term,
            )

    def build_sitemap(self, posts, work_cases, glossary_terms, pillars=None, categories=None):
        base = self.config["site"]["url"].rstrip("/")
        pillars = pillars or []
        categories = categories or []
        # Site-freshness proxy: the most recent post's date drives lastmod on
        # listing/static pages so crawlers re-fetch them when new content ships.
        site_lastmod = format_date_iso(posts[0].get("updated") or posts[0].get("date")) if posts else None

        # (path, priority, changefreq, lastmod)
        urls = [
            ("/", "1.0", "weekly", site_lastmod),
            ("/articles/", "0.9", "daily", site_lastmod),
            ("/work/", "0.8", "monthly", None),
            ("/portfolio/", "0.7", "monthly", None),
            ("/projects/", "0.7", "monthly", None),
            ("/about/", "0.6", "monthly", None),
            ("/contact/", "0.5", "yearly", None),
            ("/linter/", "0.9", "monthly", None),
            ("/llms-txt-generator/", "0.9", "monthly", None),
            ("/privacy/", "0.3", "yearly", None),
            ("/terms/", "0.3", "yearly", None),
        ]
        if glossary_terms:
            urls.append(("/glossary/", "0.8", "weekly", site_lastmod))
        article_page_count = (len(posts) + 19) // 20
        for page_num in range(2, article_page_count + 1):
            urls.append((f"/articles/page/{page_num}/", "0.6", "daily", site_lastmod))
        for category in categories:
            category_posts = category.get("posts", [])
            lastmod = format_date_iso(category_posts[0].get("updated") or category_posts[0].get("date")) if category_posts else None
            urls.append((category["url"], "0.8", "weekly", lastmod))
        for post in posts:
            urls.append((post["url"], "0.9", "monthly", format_date_iso(post.get("updated") or post.get("date"))))
        for case in work_cases:
            case_date = case.get("updated") or case.get("date")
            urls.append((case["url"], "0.8", "monthly", format_date_iso(case_date) if case_date else None))
        for term in glossary_terms:
            term_date = term.get("last_updated")
            urls.append((term["url"], "0.8", "monthly", format_date_iso(term_date) if term_date else None))

        root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for path, priority, freq, lastmod in urls:
            url_el = ET.SubElement(root, "url")
            ET.SubElement(url_el, "loc").text = base + path
            if lastmod:
                ET.SubElement(url_el, "lastmod").text = lastmod
            ET.SubElement(url_el, "changefreq").text = freq
            ET.SubElement(url_el, "priority").text = priority

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        sitemap_path = self.output / "sitemap.xml"
        tree.write(sitemap_path, xml_declaration=True, encoding="utf-8")

    def build_rss(self, posts):
        base = self.config["site"]["url"].rstrip("/")
        site = self.config["site"]

        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = site["title"]
        ET.SubElement(channel, "link").text = base
        ET.SubElement(channel, "description").text = site["description"]
        ET.SubElement(channel, "language").text = "en-us"

        for post in posts[:20]:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = post["title"]
            ET.SubElement(item, "link").text = base + post["url"]
            ET.SubElement(item, "description").text = post.get("description", "")
            if post.get("date"):
                published = post["date"]
                if isinstance(published, str):
                    published = datetime.strptime(published, "%Y-%m-%d").date()
                if isinstance(published, datetime):
                    published = published.date()
                published_at = datetime.combine(published, time.min, tzinfo=timezone.utc)
                ET.SubElement(item, "pubDate").text = format_rfc2822_date(published_at)
            ET.SubElement(item, "guid", isPermaLink="true").text = base + post["url"]

        tree = ET.ElementTree(rss)
        ET.indent(tree, space="  ")
        feed_path = self.output / "feed.xml"
        tree.write(feed_path, xml_declaration=True, encoding="utf-8")

    def build_llms_txt(self, posts, glossary_terms, work_cases, pillars=None):
        """Emit /llms.txt — a clean, link-first map of the site for AI crawlers
        and answer engines. Follows the llms.txt convention (H1, summary
        blockquote, then sectioned bullet links)."""
        base = self.config["site"]["url"].rstrip("/")
        site = self.config["site"]

        # Tag -> cluster, first match wins (order defines precedence).
        clusters = [
            ("Documentation", {"documentation", "technical-writing"}),
            ("API Documentation", {"api-documentation", "api"}),
            ("Docs as Code", {"docs-as-code", "documentation-workflow"}),
            ("Documentation SEO", {"documentation-seo", "seo"}),
            ("AI-Ready Documentation", {"ai-ready-documentation", "retrieval"}),
            ("Technical Content", {"technical-content", "tutorials", "developer-experience"}),
        ]

        def cluster_for(post):
            tags = {str(t).lower() for t in post.get("tags", [])}
            for name, keys in clusters:
                if tags & keys:
                    return name
            return "Other Writing"

        grouped: dict[str, list[dict]] = {}
        for post in posts:
            grouped.setdefault(cluster_for(post), []).append(post)

        lines = [
            f"# {site['author']}",
            "",
            f"> {site['description']}",
            "",
            ("Technical writer and former engineer publishing in-depth, benchmark-backed "
             "writing on developer documentation, API docs, docs-as-code, documentation "
             "SEO, AI retrieval, and technical content. Articles below are grouped by "
             "topic; each links to the canonical URL."),
            "",
        ]

        cluster_order = [name for name, _ in clusters] + ["Other Writing"]
        for name in cluster_order:
            items = grouped.get(name)
            if not items:
                continue
            lines.append(f"## {name}")
            lines.append("")
            for post in items:
                desc = (post.get("description") or "").strip().replace("\n", " ")
                lines.append(f"- [{post['title']}]({base}{post['url']}): {desc}")
            lines.append("")

        if glossary_terms:
            lines.append("## Glossary")
            lines.append("")
            for term in glossary_terms:
                desc = (term.get("short_definition") or term.get("description") or "").strip().replace("\n", " ")
                lines.append(f"- [{term['name']}]({base}{term['url']}): {desc}")
            lines.append("")

        if work_cases:
            lines.append("## Work & Case Studies")
            lines.append("")
            for case in work_cases:
                desc = (case.get("description") or case.get("summary") or "").strip().replace("\n", " ")
                title = case.get("title", case["slug"])
                lines.append(f"- [{title}]({base}{case['url']}): {desc}")
            lines.append("")

        lines.append("## Pages")
        lines.append("")
        lines.append(f"- [About]({base}/about/): Background, expertise, and how I work.")
        lines.append(f"- [Articles]({base}/articles/): Documentation, DevRel, tutorials, technical writing, and developer education.")
        lines.append(f"- [Projects]({base}/projects/): Working tools and software.")
        lines.append(f"- [llms.txt Generator]({base}/llms-txt-generator/): Create and download a valid llms.txt file in the browser.")
        lines.append(f"- [Contact]({base}/contact/): Get in touch or book a call.")
        lines.append("")

        (self.output / "llms.txt").write_text("\n".join(lines), encoding="utf-8")

    def build_redirects(self, posts):
        """Write Cloudflare Pages redirects at the deployment root.

        Only published articles receive legacy /blog/ redirects. Removed URLs are
        allowed to return the site's real 404 instead of redirecting to a missing
        destination or an unrelated listing page.
        """
        lines = [
            "# Generated by build.py. Static aliases come first.",
            "/blog /articles/ 301",
            "/blog/ /articles/ 301",
        ]
        for post in sorted(posts, key=lambda item: item["slug"]):
            slug = post["slug"]
            lines.append(f"/blog/{slug} /articles/{slug}/ 301")
            lines.append(f"/blog/{slug}/ /articles/{slug}/ 301")

        redirects_src = Path("static/_redirects")
        if redirects_src.exists():
            static_lines = [
                line for line in redirects_src.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            ]
            if static_lines:
                lines.extend(["", "# Static aliases", *static_lines])

        (self.output / "_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def build_pygments_css(self):
        # Light mode: use 'default' style (good contrast on light backgrounds)
        light_formatter = HtmlFormatter(style="default")
        light_css = light_formatter.get_style_defs("[data-theme='light'] .highlight")
        
        # Dark mode: use 'monokai' style (good contrast on dark backgrounds)
        dark_formatter = HtmlFormatter(style="monokai")
        dark_css = dark_formatter.get_style_defs("[data-theme='dark'] .highlight")
        
        # Combine with base pre styles
        base_css = """pre { line-height: 1.6; overflow-x: auto; }
.highlight { border-radius: 4px; padding: 1rem; }
"""
        
        css_content = base_css + "\n" + light_css + "\n" + dark_css
        css_path = self.output / "static" / "css" / "highlight.css"
        css_path.write_text(css_content, encoding="utf-8")

    # ------------------------------------------------------------------
    # Main build
    # ------------------------------------------------------------------

    def build(self):
        print("Building site...")

        if self.output.exists():
            shutil.rmtree(self.output)
        self.output.mkdir()

        if Path("static").exists():
            shutil.copytree("static", self.output / "static")
            # Copy platform control files to the deployment root.
            for control_file in ("robots.txt", "_routes.json"):
                control_src = Path("static") / control_file
                if control_src.exists():
                    shutil.copy2(control_src, self.output / control_file)
            # Cloudflare reads deployment controls only from the output root.
            # Remove source copies from /static after copying/generating them.
            for control_file in ("robots.txt", "_redirects", "_routes.json"):
                copied_control = self.output / "static" / control_file
                if copied_control.exists():
                    copied_control.unlink()
        else:
            (self.output / "static" / "css").mkdir(parents=True)

        posts = self.load_posts()
        self.latest_posts = posts[:3]
        work_cases = self.load_work()
        portfolio = self.load_portfolio()
        projects = self.load_projects()
        legal_pages = self.load_legal_pages()
        glossary_terms = self.load_glossary()
        pillars = self.load_pillars(posts)
        categories = self.load_categories(posts)

        self.build_homepage(posts, work_cases)
        self.build_blog_list(posts, categories)
        self.build_category_archives(categories)
        self.build_posts(posts)
        self.build_work_list(work_cases)
        self.build_work_pages(work_cases)
        self.build_portfolio(portfolio)
        self.build_projects(projects)
        self.build_about()
        self.build_contact()
        self.build_404()
        self.build_linter()
        self.build_llms_txt_generator()
        self.build_legal_pages(legal_pages)
        self.build_glossary(glossary_terms)

        self.build_sitemap(posts, work_cases, glossary_terms, pillars, categories)
        self.build_rss(posts)
        self.build_llms_txt(posts, glossary_terms, work_cases, pillars)
        self.build_redirects(posts)
        self.build_pygments_css()

        print(f"  {len(posts)} blog post(s)")
        print(f"  {len(pillars)} article focus area(s)")
        print(f"  {len(work_cases)} case stud(ies)")
        print(f"  {len(projects)} project(s)")
        print(f"  {len(glossary_terms)} glossary term(s)")
        print(f"Done → output/")


# ---------------------------------------------------------------------------
# Local server
# ---------------------------------------------------------------------------

def serve(port: int = 8000):
    os.chdir("output")
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None  # silence logs
    server = http.server.HTTPServer(("", port), handler)
    print(f"Serving at http://localhost:{port}/")
    server.serve_forever()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    include_drafts = "--drafts" in sys.argv
    builder = SiteBuilder(include_drafts=include_drafts)
    builder.build()

    from seo_audit import main as run_seo_audit
    if run_seo_audit() != 0:
        sys.exit(1)

    if "--serve" in sys.argv:
        serve()
