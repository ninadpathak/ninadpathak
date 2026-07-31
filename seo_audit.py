#!/usr/bin/env python3
"""Fail the build handoff when generated SEO fundamentals are inconsistent."""

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).parent.resolve()
OUTPUT = ROOT / "output"
SITE_HOST = "ninadpathak.com"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_parts = []
        self.in_title = False
        self.h1_count = 0
        self.meta = {}
        self.canonical = []
        self.links = []
        self.assets = []
        self.json_ld = []
        self.in_json_ld = False
        self.json_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            key = attrs.get("name") or attrs.get("property")
            if key:
                self.meta.setdefault(key.lower(), []).append(attrs.get("content", ""))
        elif tag == "link":
            if attrs.get("rel") == "canonical":
                self.canonical.append(attrs.get("href", ""))
            if attrs.get("href"):
                self.assets.append(attrs["href"])
        elif tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        elif tag in {"script", "img"} and attrs.get("src"):
            self.assets.append(attrs["src"])

        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_json_ld = True
            self.json_parts = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_json_ld:
            self.json_ld.append("".join(self.json_parts).strip())
            self.in_json_ld = False
            self.json_parts = []

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if self.in_json_ld:
            self.json_parts.append(data)

    @property
    def title(self):
        return " ".join("".join(self.title_parts).split())


def local_file_for_url(url):
    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != SITE_HOST:
        return None
    path = parsed.path or "/"
    if path == "/":
        return OUTPUT / "index.html"
    if path.endswith("/"):
        return OUTPUT / path.lstrip("/") / "index.html"
    direct = OUTPUT / path.lstrip("/")
    if direct.suffix:
        return direct
    return direct / "index.html"


def main():
    errors = []
    pages = {}

    if not OUTPUT.exists():
        print("output/ does not exist. Run python3 build.py first.")
        return 1

    html_files = sorted(path for path in OUTPUT.rglob("*.html") if "static" not in path.parts)
    for path in html_files:
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8"))
        pages[path] = parser
        label = path.relative_to(OUTPUT)

        if not parser.title:
            errors.append(f"{label}: missing title")
        if len(parser.meta.get("description", [])) != 1 or not parser.meta.get("description", [""])[0].strip():
            errors.append(f"{label}: needs one non-empty meta description")
        if len(parser.canonical) != 1:
            errors.append(f"{label}: needs exactly one canonical URL")
        if parser.h1_count != 1:
            errors.append(f"{label}: expected one h1, found {parser.h1_count}")

        if parser.canonical:
            canonical = parser.canonical[0]
            og_urls = parser.meta.get("og:url", [])
            if len(og_urls) != 1 or og_urls[0] != canonical:
                errors.append(f"{label}: og:url does not match canonical")
            canonical_file = local_file_for_url(canonical)
            if canonical_file is not None and not canonical_file.exists() and label != Path("404.html"):
                errors.append(f"{label}: canonical target does not exist: {canonical}")

        for block in parser.json_ld:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{label}: invalid JSON-LD: {exc}")

        for href in parser.links:
            if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            target = local_file_for_url(href)
            if target is not None and not target.exists():
                errors.append(f"{label}: broken internal link: {href}")

        for asset_url in parser.assets:
            if asset_url.startswith(("data:", "//")):
                continue
            target = local_file_for_url(asset_url)
            if target is not None and asset_url.startswith("/static/") and not target.exists():
                errors.append(f"{label}: missing static asset: {asset_url}")

    indexable_canonicals = {}
    for path, parser in pages.items():
        robots = ",".join(parser.meta.get("robots", [])).lower()
        if "noindex" in robots or not parser.canonical:
            continue
        canonical = parser.canonical[0]
        if canonical in indexable_canonicals:
            errors.append(
                f"duplicate canonical {canonical}: "
                f"{indexable_canonicals[canonical].relative_to(OUTPUT)} and {path.relative_to(OUTPUT)}"
            )
        indexable_canonicals[canonical] = path

    sitemap_path = OUTPUT / "sitemap.xml"
    if not sitemap_path.exists():
        errors.append("missing sitemap.xml")
        sitemap_urls = set()
    else:
        sitemap_root = ET.parse(sitemap_path).getroot()
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = {node.text for node in sitemap_root.findall("sm:url/sm:loc", namespace)}
        for url in sitemap_urls:
            target = local_file_for_url(url)
            if target is None or not target.exists():
                errors.append(f"sitemap URL has no generated page: {url}")

    for canonical, path in indexable_canonicals.items():
        if canonical not in sitemap_urls:
            errors.append(f"{path.relative_to(OUTPUT)}: indexable canonical missing from sitemap")

    robots_path = OUTPUT / "robots.txt"
    if not robots_path.exists() or "Sitemap: https://ninadpathak.com/sitemap.xml" not in robots_path.read_text(encoding="utf-8"):
        errors.append("robots.txt is missing the canonical sitemap declaration")

    llms_path = OUTPUT / "llms.txt"
    if not llms_path.exists():
        errors.append("missing llms.txt")
    else:
        for url in re.findall(r"\]\((https?://[^)]+)\)", llms_path.read_text(encoding="utf-8")):
            target = local_file_for_url(url)
            if target is not None and not target.exists():
                errors.append(f"llms.txt links to a missing page: {url}")

    redirects_path = OUTPUT / "_redirects"
    if not redirects_path.exists():
        errors.append("missing root _redirects file")
    else:
        for number, line in enumerate(redirects_path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) != 3 or parts[2] not in {"301", "302", "303", "307", "308"}:
                errors.append(f"_redirects line {number}: unsupported Cloudflare Pages rule: {line}")

    routes_path = OUTPUT / "_routes.json"
    if not routes_path.exists():
        errors.append("missing Cloudflare Pages _routes.json")
    else:
        try:
            routes = json.loads(routes_path.read_text(encoding="utf-8"))
            if routes.get("version") != 1 or routes.get("include") != ["/api/*"]:
                errors.append("_routes.json must limit Pages Functions to /api/*")
        except json.JSONDecodeError as exc:
            errors.append(f"invalid _routes.json: {exc}")

    for duplicate in (OUTPUT / "static" / "robots.txt", OUTPUT / "static" / "_redirects", OUTPUT / "static" / "_routes.json"):
        if duplicate.exists():
            errors.append(f"deployment control file is misplaced: {duplicate.relative_to(OUTPUT)}")

    if errors:
        print(f"SEO audit failed with {len(errors)} issue(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"SEO audit passed: {len(pages)} HTML pages, "
        f"{len(sitemap_urls)} sitemap URLs, {len(indexable_canonicals)} unique canonicals."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
