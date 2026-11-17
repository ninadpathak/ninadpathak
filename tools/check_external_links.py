#!/usr/bin/env python3
"""Report the health of the external links on the portfolio and hiring pages.

    python tools/check_external_links.py            # report, always exits 0
    python tools/check_external_links.py --strict   # exit 1 if any link is dead or moved
    python tools/check_external_links.py --json out.json

WHY THIS IS NOT PART OF THE BUILD

Publishers take bylined posts down and block scripts. A network check inside build.py or the
test suite would fail a deploy because someone else's server had a bad minute. This tool is
run by hand or on a schedule, and nothing imports it.

WHAT IT CAN AND CANNOT JUDGE

A plain fetch with a browser user agent settles four cases:

  ok       200 at the same article (a redirect that keeps the slug counts)
  dead     404 or 410, or a 200 whose title or first heading says the page is missing
  moved    a redirect that drops the slug, for example to a homepage or an index page
  blocked  401, 403, 429, 999 or a 5xx. The server refused or failed, which says nothing
           about the page. Open these in a browser before changing anything.

It reads the response as served. A byline drawn by JavaScript, or a page that swaps its
author, needs a browser and a person. The 2026-11-17 sweep that produced the first archive
links used a headless browser for those and is recorded outside the repo.

Wayback Machine links are checked the same way, with one extra rule: the capture must answer
at the timestamp in the link. If the archive redirects to a different capture, the link is
reported as moved.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = (
    "content/portfolio.yaml",
    "content/projects.yaml",
    "content/about.md",
    "content/services.md",
    "content/services/*.md",
    "content/work/*.md",
    "templates/*.html",
    "config.toml",
)
# Fonts, analytics, schema vocabulary, placeholders and the site itself are not portfolio links.
SKIP_HOSTS = {
    "fonts.googleapis.com", "fonts.gstatic.com", "www.googletagmanager.com", "schema.org",
    "example.com", "ninadpathak.com", "www.w3.org",
}
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
URL = re.compile(r"https?://[^\s\"'<>)\]}]+")
WAYBACK = re.compile(r"https?://web\.archive\.org/web/(\d{14})(?:[a-z]{2}_)?/(.+)")
MISSING = re.compile(r"\b(404|not found|page slipped|no longer available)\b", re.I)
BLOCKED = {401, 403, 429, 999}


def collect(root: pathlib.Path = ROOT) -> dict[str, list[str]]:
    """Map each external URL to the source files that carry it."""
    found: dict[str, list[str]] = {}
    for pattern in SOURCES:
        for path in sorted(root.glob(pattern)):
            for line in path.read_text(encoding="utf-8").splitlines():
                # original_url records a publisher address that is known to be gone.
                if line.lstrip().startswith("original_url:"):
                    continue
                for url in URL.findall(line):
                    url = url.rstrip(".,;")
                    if "{{" in url or urllib.parse.urlsplit(url).hostname in SKIP_HOSTS:
                        continue
                    found.setdefault(url, [])
                    rel = str(path.relative_to(root))
                    if rel not in found[url]:
                        found[url].append(rel)
    return found


def slug(url: str) -> str:
    parts = [p for p in urllib.parse.urlsplit(url).path.split("/") if p]
    return parts[-1].lower() if parts else ""


def classify(url: str, status: int, final: str, title: str = "", heading: str = "") -> tuple[str, str]:
    """Return (verdict, reason) for one fetched URL. Pure, so the tests need no network."""
    if status == 0:
        return "blocked", "no response"
    if status in BLOCKED or status >= 500:
        return "blocked", f"HTTP {status}, open it in a browser"
    if status in (404, 410):
        return "dead", f"HTTP {status}"
    if status != 200:
        return "blocked", f"HTTP {status}"
    if MISSING.search(title) or MISSING.search(heading):
        return "dead", "200 with a missing-page title or heading"
    capture = WAYBACK.match(url)
    if capture:
        answered = WAYBACK.match(final)
        if not answered or answered.group(1) != capture.group(1):
            return "moved", "the archive answered with a different capture"
        return "ok", "capture answers at its timestamp"
    # A publisher may shorten or extend a slug when it moves an article, so either slug
    # containing the other counts as the same piece. A homepage has no slug at all.
    wanted, landed = slug(url), slug(final)
    if wanted and not (landed and (landed in wanted or wanted in landed)):
        return "moved", f"redirects to {final}"
    return "ok", "200" if final.rstrip("/") == url.rstrip("/") else f"200 via {final}"


def fetch_all(urls: list[str]) -> list[dict]:
    """Fetch publishers in parallel and the archive one request at a time.

    The Wayback Machine answers 429 to a burst, which would report every capture as blocked.
    """
    archived = [u for u in urls if WAYBACK.match(u)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(fetch, [u for u in urls if u not in archived]))
    for url in archived:
        result = fetch(url, timeout=90)
        for wait in (20, 60):
            if result["status"] not in (0, 429) and result["status"] < 500:
                break
            time.sleep(wait)
            result = fetch(url, timeout=90)
        results.append(result)
        time.sleep(4)
    return sorted(results, key=lambda r: r["url"])


def fetch(url: str, timeout: int = 40) -> dict:
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status, final, body = response.status, response.geturl(), response.read(2_000_000)
    except urllib.error.HTTPError as error:
        status, final, body = error.code, error.geturl() or url, error.read(300_000)
    except Exception as error:  # DNS failure, timeout, TLS error: nothing was learned
        return {"url": url, "status": 0, "final": url, "verdict": "blocked", "reason": type(error).__name__}
    text = body.decode("utf-8", "replace")

    def first(tag: str) -> str:
        match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", text, re.S | re.I)
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", match.group(1))).strip()[:120] if match else ""

    title, heading = first("title"), first("h1")
    verdict, reason = classify(url, status, final, title, heading)
    return {"url": url, "status": status, "final": final, "title": title, "verdict": verdict, "reason": reason}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--strict", action="store_true", help="exit 1 when a link is dead or moved")
    parser.add_argument("--json", type=pathlib.Path, help="also write the full results here")
    args = parser.parse_args(argv)

    sources = collect()
    results = fetch_all(sorted(sources))
    for result in results:
        result["sources"] = sources[result["url"]]

    for verdict in ("dead", "moved", "blocked"):
        for result in results:
            if result["verdict"] == verdict:
                print(f"{verdict.upper():8}{result['url']}\n        {result['reason']} ({', '.join(result['sources'])})")
    counts = {v: sum(r["verdict"] == v for r in results) for v in ("ok", "dead", "moved", "blocked")}
    print(f"{len(results)} links: {counts['ok']} ok, {counts['dead']} dead, {counts['moved']} moved, "
          f"{counts['blocked']} blocked and not judged")
    if args.json:
        args.json.write_text(json.dumps(results, indent=1), encoding="utf-8")
    return 1 if args.strict and (counts["dead"] or counts["moved"]) else 0


if __name__ == "__main__":
    sys.exit(main())
