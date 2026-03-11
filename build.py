#!/usr/bin/env python3
"""
Ninad Pathak | Static Site Generator
Requires Python 3.11+

Usage:
  python build.py           Build site to /output
  python build.py --serve   Build then serve at localhost:8000
  python build.py --drafts  Include draft posts
"""

import os
import re
import sys
import shutil
import http.server
import threading
import xml.etree.ElementTree as ET
from datetime import datetime, date
from pathlib import Path

try:
    import tomllib
except ImportError:
    print("Error: Python 3.11+ required (for tomllib).")
    sys.exit(1)

import frontmatter
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from pygments.formatters import HtmlFormatter

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


def sort_key(post: dict):
    d = post.get("date")
    if isinstance(d, (datetime,)):
        return d.date()
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            pass
    return date.min


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
                }
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

            self.md.reset()
            html = self.md.convert(post.content)
            # Extract TOC from markdown if available
            toc_html = getattr(self.md, 'toc', '') if hasattr(self.md, 'toc') else ''
            slug = post.get("slug") or slugify(md_file.stem)

            posts.append({
                "title": post.get("title", md_file.stem),
                "date": post.get("date"),
                "description": post.get("description", ""),
                "tags": post.get("tags", []),
                "status": status,
                "content": html,
                "slug": slug,
                "reading_time": estimate_reading_time(post.content),
                "url": f"/blog/{slug}/",
                "toc": toc_html,
            })

        return sorted(posts, key=sort_key, reverse=True)

    def load_work(self) -> list[dict]:
        work_dir = Path("content/work")
        cases = []
        for md_file in sorted(work_dir.glob("*.md")):
            post = frontmatter.load(md_file)
            self.md.reset()
            html = self.md.convert(post.content)
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

    def load_md_content(self, path: str) -> tuple[dict, str]:
        post = frontmatter.load(path)
        self.md.reset()
        return post.metadata, self.md.convert(post.content)

    # ------------------------------------------------------------------
    # Render helper
    # ------------------------------------------------------------------

    def render(self, template_name: str, output_path: str, page: str = "", **ctx):
        template = self.env.get_template(template_name)
        ctx["site"] = self.config["site"]
        ctx["contact"] = self.config["contact"]
        ctx["current_page"] = page
        ctx["build_year"] = datetime.now().year

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

    def build_blog_list(self, posts):
        self.render(
            "blog_list.html", "blog/index.html",
            page="blog",
            posts=posts,
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
                f"blog/{post['slug']}/index.html",
                page="blog",
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

    def build_tasks(self, posts):
        with open("content/tasks.yaml") as f:
            data = yaml.safe_load(f)

        published_slugs = {p["slug"] for p in posts}

        categories = []
        published_count = 0
        total_count = 0

        for cat in data.get("categories", []):
            tasks = []
            for t in cat.get("tasks", []):
                slug = t.get("slug")
                is_published = bool(slug and slug != "~" and slug in published_slugs)
                url = f"/blog/{slug}/" if is_published else None
                tasks.append({
                    "title": t["title"],
                    "tags": t.get("tags", []),
                    "published": is_published,
                    "url": url,
                })
                total_count += 1
                if is_published:
                    published_count += 1
            categories.append({"name": cat["name"], "tasks": tasks})

        queued_count = total_count - published_count
        progress_pct = round(published_count / total_count * 100) if total_count else 0

        self.render(
            "tasks.html", "tasks/index.html",
            page="tasks",
            categories=categories,
            published_count=published_count,
            queued_count=queued_count,
            total_count=total_count,
            progress_pct=progress_pct,
        )

    def build_sitemap(self, posts, work_cases):
        base = self.config["site"]["url"].rstrip("/")
        urls = [
            ("", "1.0", "weekly"),
            ("/blog/", "0.9", "daily"),
            ("/work/", "0.8", "monthly"),
            ("/portfolio/", "0.7", "monthly"),
            ("/about/", "0.6", "monthly"),
            ("/contact/", "0.5", "yearly"),
        ]
        for post in posts:
            urls.append((post["url"], "0.9", "monthly"))
        for case in work_cases:
            urls.append((case["url"], "0.8", "monthly"))

        root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for path, priority, freq in urls:
            url_el = ET.SubElement(root, "url")
            ET.SubElement(url_el, "loc").text = base + path
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
                ET.SubElement(item, "pubDate").text = format_date(post["date"])

        tree = ET.ElementTree(rss)
        ET.indent(tree, space="  ")
        feed_path = self.output / "feed.xml"
        tree.write(feed_path, xml_declaration=True, encoding="utf-8")

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
            # Copy robots.txt to root if it exists
            robots_src = Path("static") / "robots.txt"
            robots_dst = self.output / "robots.txt"
            if robots_src.exists():
                shutil.copy2(robots_src, robots_dst)
        else:
            (self.output / "static" / "css").mkdir(parents=True)

        posts = self.load_posts()
        work_cases = self.load_work()
        portfolio = self.load_portfolio()

        self.build_homepage(posts, work_cases)
        self.build_blog_list(posts)
        self.build_posts(posts)
        self.build_work_list(work_cases)
        self.build_work_pages(work_cases)
        self.build_portfolio(portfolio)
        self.build_about()
        self.build_contact()
        self.build_tasks(posts)
        self.build_sitemap(posts, work_cases)
        self.build_rss(posts)
        self.build_pygments_css()

        print(f"  {len(posts)} blog post(s)")
        print(f"  {len(work_cases)} case stud(ies)")
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

    if "--serve" in sys.argv:
        serve()
