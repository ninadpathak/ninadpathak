#!/usr/bin/env python3
"""Freeze robots and sitemap populations without parsing any code samples."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import posixpath
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, build_opener
from urllib.robotparser import RobotFileParser

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_docs_roots import (  # noqa: E402
    MAX_ROOT_BYTES,
    RETRYABLE_STATUS,
    USER_AGENT,
    RecordingRedirectHandler,
)

ROBOTS_AGENT = "ninadpathak-code-census"
MAX_SITEMAP_BYTES = 20_000_000
MAX_SITEMAP_DOCUMENTS_PER_ORIGIN = 200
ASSET_SUFFIXES = {
    ".7z", ".avif", ".bz2", ".css", ".csv", ".doc", ".docx", ".eot",
    ".gif", ".gz", ".ico", ".jpeg", ".jpg", ".js", ".json", ".map",
    ".mp3", ".mp4", ".pdf", ".png", ".rar", ".rss", ".svg", ".tar",
    ".tgz", ".ttf", ".txt", ".webm", ".webp", ".woff", ".woff2", ".xml",
    ".xz", ".zip",
}


class FetchFailure(Exception):
    def __init__(self, cause: Exception, attempts: int, redirects: list[dict[str, object]]) -> None:
        super().__init__(f"{type(cause).__name__}: {cause}")
        self.attempts = attempts
        self.redirects = redirects


def origin(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"not an HTTP URL: {url}")
    host = parsed.hostname.lower()
    port = parsed.port
    if port and not ((parsed.scheme == "http" and port == 80) or (parsed.scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    return f"{parsed.scheme.lower()}://{host}"


def normalize_page_url(url: str) -> str | None:
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return None
    scheme = parsed.scheme.lower()
    host = parsed.hostname.lower()
    port = parsed.port
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path = parsed.path or "/"
    suffix = posixpath.splitext(path.rstrip("/").lower())[1]
    if suffix in ASSET_SUFFIXES:
        return None
    return urlunsplit((scheme, host, path, "", ""))


def root_scope(root_url: str) -> dict[str, str]:
    parsed = urlsplit(root_url)
    path = parsed.path or "/"
    basename = posixpath.basename(path.rstrip("/")).lower()
    if basename in {"index.htm", "index.html", "contents.htm", "contents.html"}:
        return {"kind": "prefix", "path": posixpath.dirname(path.rstrip("/")) + "/"}
    if posixpath.splitext(basename)[1] in {".htm", ".html"}:
        return {"kind": "exact", "path": path}
    return {"kind": "prefix", "path": path if path.endswith("/") else path + "/"}


def in_root_scope(url: str, root_url: str) -> bool:
    candidate = urlsplit(url)
    root = urlsplit(root_url)
    if (candidate.hostname or "").lower() != (root.hostname or "").lower():
        return False
    scope = root_scope(root_url)
    if scope["kind"] == "exact":
        return candidate.path == scope["path"]
    return candidate.path.startswith(scope["path"])


def sitemap_directives(raw: bytes, robots_url: str) -> list[str]:
    urls = []
    for line in raw.decode("utf-8", errors="replace").splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip().lower() == "sitemap" and value.strip():
            urls.append(urljoin(robots_url, value.strip()))
    return sorted(set(urls))


def parse_sitemap(raw: bytes, url: str) -> tuple[str, list[str]]:
    if urlsplit(url).path.lower().endswith(".gz"):
        raw = gzip.decompress(raw)
        if len(raw) > MAX_SITEMAP_BYTES:
            raise ValueError(f"expanded sitemap exceeds {MAX_SITEMAP_BYTES} bytes")
    root = ET.fromstring(raw)
    tag = root.tag.rsplit("}", 1)[-1].lower()
    if tag not in {"urlset", "sitemapindex"}:
        raise ValueError(f"unexpected sitemap root: {tag}")
    locations = []
    child_name = "url" if tag == "urlset" else "sitemap"
    for child in root:
        if child.tag.rsplit("}", 1)[-1].lower() != child_name:
            continue
        for element in child:
            if element.tag.rsplit("}", 1)[-1].lower() == "loc" and element.text:
                locations.append(element.text.strip())
                break
    return tag, sorted(set(location for location in locations if location))


def fetch_bytes(url: str, timeout: int, max_bytes: int, attempts: int = 3) -> dict[str, object]:
    total_redirects: list[dict[str, object]] = []
    for attempt in range(1, attempts + 1):
        handler = RecordingRedirectHandler()
        opener = build_opener(handler)
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
        try:
            with opener.open(request, timeout=timeout) as response:
                total_redirects.extend(handler.chain)
                raw = response.read(max_bytes + 1)
                if len(raw) > max_bytes:
                    raise ValueError(f"response exceeds {max_bytes} bytes")
                return {
                    "requested_url": url,
                    "final_url": response.geturl(),
                    "status": getattr(response, "status", response.getcode()),
                    "content_type": response.headers.get_content_type().lower(),
                    "bytes": len(raw),
                    "response_sha256": hashlib.sha256(raw).hexdigest(),
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "attempts": attempt,
                    "redirects": total_redirects,
                    "raw": raw,
                }
        except HTTPError as exc:
            total_redirects.extend(handler.chain)
            if exc.code not in RETRYABLE_STATUS or attempt == attempts:
                return {
                    "requested_url": url,
                    "final_url": exc.geturl(),
                    "status": exc.code,
                    "content_type": exc.headers.get_content_type().lower(),
                    "bytes": 0,
                    "attempts": attempt,
                    "redirects": total_redirects,
                    "error": f"HTTPError: {exc}",
                    "raw": b"",
                }
            time.sleep(float(attempt))
        except URLError as exc:
            total_redirects.extend(handler.chain)
            if attempt == attempts:
                raise FetchFailure(exc, attempt, total_redirects) from exc
            time.sleep(float(attempt))
    raise AssertionError("retry loop exhausted")


def public_fetch_record(record: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in record.items() if key != "raw"}


def robots_policy(record: dict[str, object], robots_url: str) -> tuple[str, RobotFileParser | None, list[str]]:
    status = int(record["status"])
    raw = record["raw"]
    assert isinstance(raw, bytes)
    if status == 200:
        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(raw.decode("utf-8", errors="replace").splitlines())
        return "available", parser, sitemap_directives(raw, robots_url)
    if status in {404, 410}:
        return "absent", None, []
    if status in {401, 403}:
        return "denied", None, []
    return "unavailable", None, []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--delay-ms", type=int, default=100)
    args = parser.parse_args()

    input_bytes = args.input.read_bytes()
    source = json.loads(input_bytes)
    eligible = [
        row for row in source["rows"]
        if isinstance(row.get("inspection"), dict) and row["inspection"].get("supported_generator") is True
    ]
    roots = {str(row["inspection"]["final_url"]): origin(str(row["inspection"]["final_url"])) for row in eligible}

    robots_records: dict[str, dict[str, object]] = {}
    robot_parsers: dict[str, RobotFileParser | None] = {}
    sitemap_seeds: dict[str, list[str]] = {}
    for site_origin in sorted(set(roots.values())):
        robots_url = site_origin + "/robots.txt"
        try:
            fetched = fetch_bytes(robots_url, args.timeout, MAX_ROOT_BYTES)
            policy, robot_parser, declared = robots_policy(fetched, robots_url)
            robots_records[site_origin] = {**public_fetch_record(fetched), "policy": policy, "declared_sitemaps": declared}
            robot_parsers[site_origin] = robot_parser
            sitemap_seeds[site_origin] = sorted(set(declared + [site_origin + "/sitemap.xml"]))
        except (FetchFailure, ValueError) as exc:
            robots_records[site_origin] = {"requested_url": robots_url, "policy": "unavailable", "error": str(exc)}
            robot_parsers[site_origin] = None
            sitemap_seeds[site_origin] = []
        if args.delay_ms:
            time.sleep(args.delay_ms / 1000)

    sitemap_records: dict[str, dict[str, object]] = {}
    origin_sitemap_urls: dict[str, list[str]] = {}
    for site_origin, seeds in sorted(sitemap_seeds.items()):
        if robots_records[site_origin]["policy"] in {"denied", "unavailable"}:
            origin_sitemap_urls[site_origin] = []
            continue
        queue = list(seeds)
        seen: set[str] = set()
        documents: list[str] = []
        while queue and len(seen) < MAX_SITEMAP_DOCUMENTS_PER_ORIGIN:
            sitemap_url = queue.pop(0)
            if sitemap_url in seen:
                continue
            seen.add(sitemap_url)
            try:
                fetched = fetch_bytes(sitemap_url, args.timeout, MAX_SITEMAP_BYTES)
                record = public_fetch_record(fetched)
                if int(fetched["status"]) == 200:
                    kind, locations = parse_sitemap(fetched["raw"], str(fetched["final_url"]))  # type: ignore[arg-type]
                    record["kind"] = kind
                    record["locations"] = locations
                    documents.append(sitemap_url)
                    if kind == "sitemapindex":
                        queue.extend(location for location in locations if location not in seen)
                sitemap_records[sitemap_url] = record
            except (FetchFailure, ValueError, ET.ParseError, gzip.BadGzipFile) as exc:
                sitemap_records[sitemap_url] = {"requested_url": sitemap_url, "error": f"{type(exc).__name__}: {exc}"}
            if args.delay_ms:
                time.sleep(args.delay_ms / 1000)
        origin_sitemap_urls[site_origin] = documents

    rows: list[dict[str, object]] = []
    for source_row in eligible:
        inspection = source_row["inspection"]
        assert isinstance(inspection, dict)
        root_url = str(inspection["final_url"])
        site_origin = roots[root_url]
        robots = robots_records[site_origin]
        robot_parser = robot_parsers[site_origin]
        policy = str(robots["policy"])
        root_allowed = policy == "absent" or (policy == "available" and robot_parser is not None and robot_parser.can_fetch(ROBOTS_AGENT, root_url))
        population: set[str] = set()
        if root_allowed:
            for sitemap_url in origin_sitemap_urls[site_origin]:
                record = sitemap_records[sitemap_url]
                if record.get("kind") != "urlset":
                    continue
                for raw_url in record.get("locations", []):
                    normalized = normalize_page_url(str(raw_url))
                    if normalized is None or not in_root_scope(normalized, root_url):
                        continue
                    if policy == "available" and robot_parser is not None and not robot_parser.can_fetch(ROBOTS_AGENT, normalized):
                        continue
                    population.add(normalized)
        if not root_allowed:
            acquisition = "robots-denied" if policy == "denied" or (policy == "available" and not root_allowed) else "robots-unavailable"
        elif population:
            acquisition = "sitemap"
        else:
            acquisition = "crawl-fallback-required"
        rows.append(
            {
                "rank": source_row["rank"],
                "project": source_row["project"],
                "resolution": source_row["resolution"],
                "generator": inspection["generator"],
                "root_url": root_url,
                "root_scope": root_scope(root_url),
                "robots_origin": site_origin,
                "robots_policy": policy,
                "root_allowed": root_allowed,
                "acquisition": acquisition,
                "population_size": len(population),
                "population_urls": sorted(population),
            }
        )

    counts: dict[str, int] = {}
    for row in rows:
        key = str(row["acquisition"])
        counts[key] = counts.get(key, 0) + 1
    attempts = sum(int(record.get("attempts", 0)) for record in robots_records.values())
    attempts += sum(int(record.get("attempts", 0)) for record in sitemap_records.values())
    redirects = sum(len(record.get("redirects", [])) for record in robots_records.values())
    redirects += sum(len(record.get("redirects", [])) for record in sitemap_records.values())
    result = {
        "study": "code-sample-validity-census",
        "stage": "robots-and-sitemap-population",
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "input_path": str(args.input),
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "limits": {
            "max_sitemap_bytes": MAX_SITEMAP_BYTES,
            "max_sitemap_documents_per_origin": MAX_SITEMAP_DOCUMENTS_PER_ORIGIN,
        },
        "summary": {
            "eligible_roots": len(rows),
            "unique_origins": len(robots_records),
            "acquisition": dict(sorted(counts.items())),
            "robots_reads": len(robots_records),
            "sitemap_reads": len(sitemap_records),
            "request_attempts": attempts,
            "redirect_hops": redirects,
        },
        "robots": robots_records,
        "sitemaps": sitemap_records,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
