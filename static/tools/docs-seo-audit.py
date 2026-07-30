#!/usr/bin/env python3
"""Audit one documentation page for crawlability, indexability, and page identity.

Usage:
  python3 docs-seo-audit.py https://developers.cloudflare.com/workers/get-started/guide/
  python3 docs-seo-audit.py URL --json receipt.json

The script uses Python's standard library and makes read-only HTTP requests.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

USER_AGENT = "NinadPathak-Docs-SEO-Audit/1.0"
TIMEOUT = 20
GENERIC_ANCHORS = {"click here", "here", "learn more", "read more", "more"}


@dataclass
class Finding:
    check: str
    level: str
    result: str
    evidence: str


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.robots = ""
        self.canonical = ""
        self.lang = ""
        self.h1s: list[str] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str | None]] = []
        self._in_title = False
        self._in_h1 = False
        self._h1_parts: list[str] = []
        self._link: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        tag = tag.lower()
        if tag == "html":
            self.lang = values.get("lang", "").strip()
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self._in_h1 = True
            self._h1_parts = []
        elif tag == "meta":
            name = values.get("name", "").lower()
            if name == "description":
                self.description = values.get("content", "").strip()
            elif name in {"robots", "googlebot"}:
                self.robots = f"{self.robots}, {values.get('content', '')}".strip(", ")
        elif tag == "link":
            rels = {item.lower() for item in values.get("rel", "").split()}
            if "canonical" in rels:
                self.canonical = values.get("href", "").strip()
        elif tag == "a":
            self._link = {"href": values.get("href", "").strip(), "text": ""}
        elif tag == "img":
            self.images.append({"src": values.get("src", "").strip(), "alt": values.get("alt")})

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
            text = " ".join("".join(self._h1_parts).split())
            if text:
                self.h1s.append(text)
        elif tag == "a" and self._link is not None:
            self._link["text"] = " ".join(self._link["text"].split())
            self.links.append(self._link)
            self._link = None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._in_h1:
            self._h1_parts.append(data)
        if self._link is not None:
            self._link["text"] += data


def request(url: str) -> tuple[int, str, dict[str, str], bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
        return response.status, response.geturl(), {k.lower(): v for k, v in response.headers.items()}, response.read()


def comparable(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urllib.parse.urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.query, ""))


def discover_sitemaps(base_url: str, robots_body: str) -> list[str]:
    found = []
    for line in robots_body.splitlines():
        if line.lower().startswith("sitemap:"):
            found.append(line.split(":", 1)[1].strip())
    default = urllib.parse.urljoin(base_url, "/sitemap.xml")
    if not found:
        found.append(default)
    return list(dict.fromkeys(found))


def sitemap_contains(sitemap_url: str, target: str, depth: int = 0) -> tuple[bool, str]:
    if depth > 1:
        return False, "nested sitemap depth exceeded"
    try:
        status, _, _, body = request(sitemap_url)
        if status != 200:
            return False, f"HTTP {status}"
        root = ET.fromstring(body)
    except Exception as exc:
        return False, f"unreadable: {exc}"
    urls = [node.text.strip() for node in root.iter() if node.tag.endswith("loc") and node.text]
    if root.tag.endswith("sitemapindex"):
        for child in urls[:25]:
            present, _ = sitemap_contains(child, target, depth + 1)
            if present:
                return True, f"listed via {child}"
        return False, f"not found in {min(len(urls), 25)} child sitemaps checked"
    normalized = {comparable(item) for item in urls}
    return comparable(target) in normalized, f"{len(urls)} URLs checked"


def audit(url: str) -> dict[str, Any]:
    findings: list[Finding] = []
    status, final_url, headers, body = request(url)
    content_type = headers.get("content-type", "")
    findings.append(Finding("HTTP response", "pass" if status == 200 else "error", f"HTTP {status}", final_url))
    if "text/html" not in content_type:
        findings.append(Finding("HTML response", "error", "Expected HTML", content_type or "No Content-Type"))
        return result(url, final_url, findings, {})

    parser = PageParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    parser.title = " ".join(parser.title.split())

    origin = urllib.parse.urlsplit(final_url)
    robots_url = urllib.parse.urlunsplit((origin.scheme, origin.netloc, "/robots.txt", "", ""))
    robots_text = ""
    try:
        _, _, _, robots_body = request(robots_url)
        robots_text = robots_body.decode("utf-8", errors="replace")
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.parse(robots_text.splitlines())
        allowed = rp.can_fetch(USER_AGENT, final_url)
        findings.append(Finding("robots.txt access", "pass" if allowed else "error", "Allowed" if allowed else "Blocked", robots_url))
    except Exception as exc:
        findings.append(Finding("robots.txt access", "warning", "Could not verify", str(exc)))

    robots_directives = ", ".join(
        value for value in (parser.robots, headers.get("x-robots-tag", "")) if value
    ).lower()
    noindex = bool(re.search(r"(?:^|[,\s])noindex(?:$|[,\s])", robots_directives))
    findings.append(Finding("Indexing directive", "error" if noindex else "pass", "noindex present" if noindex else "No noindex directive", robots_directives or "none"))
    findings.append(Finding("Page title", "pass" if parser.title else "error", "Present" if parser.title else "Missing", parser.title or "none"))
    findings.append(Finding("Meta description", "pass" if parser.description else "warning", "Present" if parser.description else "Missing", parser.description or "none"))

    if parser.canonical:
        absolute_canonical = urllib.parse.urljoin(final_url, parser.canonical)
        same = comparable(absolute_canonical) == comparable(final_url)
        findings.append(Finding("Canonical", "pass" if same else "warning", "Self-referencing" if same else "Points elsewhere", absolute_canonical))
    else:
        findings.append(Finding("Canonical", "warning", "Missing", "No rel=canonical in source HTML"))

    h1_level = "pass" if len(parser.h1s) == 1 else "warning" if len(parser.h1s) > 1 else "error"
    findings.append(Finding("Main heading", h1_level, f"{len(parser.h1s)} H1 element(s)", " | ".join(parser.h1s) or "none"))
    findings.append(Finding("Document language", "pass" if parser.lang else "warning", parser.lang or "Missing", "html[lang]"))

    internal_links = []
    generic = []
    for link in parser.links:
        href = link["href"]
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute = urllib.parse.urljoin(final_url, href)
        if urllib.parse.urlsplit(absolute).netloc == origin.netloc:
            internal_links.append(absolute)
        if link["text"].strip().lower() in GENERIC_ANCHORS:
            generic.append(link["text"])
    findings.append(Finding("Crawlable internal links", "pass" if internal_links else "warning", f"{len(internal_links)} links", f"{len(set(internal_links))} unique targets"))
    findings.append(Finding("Generic anchor text", "warning" if generic else "pass", f"{len(generic)} generic anchors", ", ".join(generic[:10]) or "none"))

    missing_alt = [image["src"] for image in parser.images if image["alt"] is None]
    findings.append(Finding("Image alt attributes", "warning" if missing_alt else "pass", f"{len(missing_alt)} missing of {len(parser.images)} images", ", ".join(str(item) for item in missing_alt[:5]) or "none"))

    sitemap_evidence = []
    sitemap_present = False
    for sitemap in discover_sitemaps(final_url, robots_text)[:5]:
        present, evidence = sitemap_contains(sitemap, final_url)
        sitemap_evidence.append(f"{sitemap}: {evidence}")
        if present:
            sitemap_present = True
            break
    findings.append(Finding("Sitemap membership", "pass" if sitemap_present else "warning", "Listed" if sitemap_present else "Not confirmed", " | ".join(sitemap_evidence)))

    facts = {
        "title": parser.title,
        "description": parser.description,
        "canonical": parser.canonical,
        "h1": parser.h1s,
        "internal_links": len(internal_links),
        "images": len(parser.images),
    }
    return result(url, final_url, findings, facts)


def result(requested_url: str, final_url: str, findings: list[Finding], facts: dict[str, Any]) -> dict[str, Any]:
    counts = {level: sum(item.level == level for item in findings) for level in ("pass", "warning", "error")}
    return {
        "requested_url": requested_url,
        "final_url": final_url,
        "summary": counts,
        "findings": [asdict(item) for item in findings],
        "facts": facts,
        "limitations": [
            "This is a single-page source-HTML audit, not a full crawl.",
            "It does not replace Search Console URL Inspection or rendered-JavaScript testing.",
            "Warnings identify review work, not confirmed ranking penalties.",
        ],
    }


def print_report(data: dict[str, Any]) -> None:
    print("Documentation SEO audit")
    print(f"URL: {data['final_url']}")
    summary = data["summary"]
    print(f"Result: {summary['pass']} pass, {summary['warning']} warning, {summary['error']} error")
    print()
    for finding in data["findings"]:
        marker = {"pass": "PASS", "warning": "WARN", "error": "FAIL"}[finding["level"]]
        print(f"[{marker}] {finding['check']}: {finding['result']}")
        print(f"       {finding['evidence']}")
    print()
    print("Scope: single-page source HTML. Confirm rendering and index state separately.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    try:
        data = audit(args.url)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 2
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print_report(data)
    return 1 if data["summary"]["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
