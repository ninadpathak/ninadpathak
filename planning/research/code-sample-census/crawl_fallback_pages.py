#!/usr/bin/env python3
"""Breadth-first fallback acquisition with content-addressed response snapshots."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from discover_page_populations import (  # noqa: E402
    FetchFailure,
    MAX_ROOT_BYTES,
    ROBOTS_AGENT,
    fetch_bytes,
    in_root_scope,
    normalize_page_url,
    public_fetch_record,
    robots_policy,
)
from inspect_docs_roots import canonical_url  # noqa: E402


def eligible_links(raw: bytes, final_url: str, root_url: str) -> list[str]:
    soup = BeautifulSoup(raw, "html.parser")
    links: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href")
        if not isinstance(href, str):
            continue
        normalized = normalize_page_url(urljoin(final_url, href))
        if normalized is not None and in_root_scope(normalized, root_url):
            links.add(normalized)
    return sorted(links)


def write_blob(raw: bytes, body_dir: Path) -> tuple[str, int, str]:
    digest = hashlib.sha256(raw).hexdigest()
    relative = Path(digest[:2]) / f"{digest}.html.gz"
    target = body_dir / relative
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    if target.exists():
        if target.read_bytes() != compressed:
            raise ValueError(f"content-addressed blob mismatch: {target}")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(compressed)
    return digest, len(compressed), str(relative)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--body-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--delay-ms", type=int, default=75)
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--project-ranks", help="comma-separated frozen ranks; omit for all fallback projects")
    parser.add_argument("--page-snapshot", type=Path, help="prior crawler output whose page records may be reused")
    args = parser.parse_args()

    input_bytes = args.input.read_bytes()
    source = json.loads(input_bytes)
    snapshot_bytes = args.page_snapshot.read_bytes() if args.page_snapshot else None
    snapshot = json.loads(snapshot_bytes) if snapshot_bytes is not None else None
    requested_ranks = None
    if args.project_ranks:
        requested_ranks = {int(value) for value in args.project_ranks.split(",") if value.strip()}
    fallback_rows = [
        row for row in source["rows"]
        if row["acquisition"] == "crawl-fallback-required"
        and (requested_ranks is None or int(row["rank"]) in requested_ranks)
    ]
    if requested_ranks is not None and {int(row["rank"]) for row in fallback_rows} != requested_ranks:
        missing = sorted(requested_ranks - {int(row["rank"]) for row in fallback_rows})
        raise ValueError(f"requested ranks are not crawl fallbacks: {missing}")

    origins = sorted({str(row["robots_origin"]) for row in fallback_rows})
    robots: dict[str, dict[str, object]] = {}
    robot_parsers: dict[str, object] = {}
    for site_origin in origins:
        prior = source["robots"][site_origin]
        if prior["policy"] == "absent":
            robots[site_origin] = {"policy": "absent", "reused_prior_absence": True}
            robot_parsers[site_origin] = None
            continue
        robots_url = site_origin + "/robots.txt"
        try:
            fetched = fetch_bytes(robots_url, args.timeout, MAX_ROOT_BYTES)
            policy, robot_parser, declared = robots_policy(fetched, robots_url)
            robots[site_origin] = {**public_fetch_record(fetched), "policy": policy, "declared_sitemaps": declared}
            robot_parsers[site_origin] = robot_parser
        except Exception as exc:
            robots[site_origin] = {"requested_url": robots_url, "policy": "unavailable", "error": f"{type(exc).__name__}: {exc}"}
            robot_parsers[site_origin] = None
        if args.delay_ms:
            time.sleep(args.delay_ms / 1000)

    page_cache: dict[str, dict[str, object]] = {
        str(url): dict(record) for url, record in (snapshot.get("pages", {}) if snapshot else {}).items()
    }
    rows: list[dict[str, object]] = []
    page_requests = 0
    cache_hits = 0
    for source_row in fallback_rows:
        root_url = str(source_row["root_url"])
        root_normalized = normalize_page_url(root_url)
        if root_normalized is None:
            raise ValueError(f"root cannot be normalized: {root_url}")
        site_origin = str(source_row["robots_origin"])
        policy = str(robots[site_origin]["policy"])
        robot_parser = robot_parsers[site_origin]
        row: dict[str, object] = {
            "rank": source_row["rank"],
            "project": source_row["project"],
            "root_url": root_url,
            "robots_origin": site_origin,
            "robots_policy": policy,
            "max_pages": args.max_pages,
        }
        if policy not in {"available", "absent"}:
            row["status"] = "robots-unavailable"
            row["selected_urls"] = []
            rows.append(row)
            continue

        queue = deque([root_normalized])
        queued = {root_normalized}
        attempted: list[str] = []
        selected: list[str] = []
        exclusions: list[dict[str, str]] = []
        while queue and len(attempted) < args.max_pages:
            url = queue.popleft()
            if policy == "available" and robot_parser is not None and not robot_parser.can_fetch(ROBOTS_AGENT, url):
                exclusions.append({"url": url, "reason": "robots-denied"})
                continue
            attempted.append(url)
            if url in page_cache:
                page = page_cache[url]
                cache_hits += 1
            else:
                try:
                    fetched = fetch_bytes(url, args.timeout, MAX_ROOT_BYTES)
                    page_requests += int(fetched.get("attempts", 0))
                    page = public_fetch_record(fetched)
                    raw = fetched["raw"]
                    assert isinstance(raw, bytes)
                    if int(fetched["status"]) == 200 and fetched["content_type"] in {"text/html", "application/xhtml+xml"}:
                        digest, compressed_bytes, blob_path = write_blob(raw, args.body_dir)
                        page["response_sha256"] = digest
                        page["compressed_bytes"] = compressed_bytes
                        page["blob_path"] = blob_path
                        soup = BeautifulSoup(raw, "html.parser")
                        page["canonical_url"] = canonical_url(soup, str(fetched["final_url"]))
                        page["links"] = eligible_links(raw, str(fetched["final_url"]), root_url)
                except Exception as exc:
                    page_requests += exc.attempts if isinstance(exc, FetchFailure) else 1
                    page = {"requested_url": url, "status": 0, "error": f"{type(exc).__name__}: {exc}", "links": []}
                page_cache[url] = page
                if args.delay_ms:
                    time.sleep(args.delay_ms / 1000)

            final_normalized = normalize_page_url(str(page.get("final_url", url)))
            if int(page.get("status", 0)) != 200:
                exclusions.append({"url": url, "reason": f"status-{page.get('status', 'error')}"})
                continue
            if page.get("content_type") not in {"text/html", "application/xhtml+xml"}:
                exclusions.append({"url": url, "reason": "not-html"})
                continue
            if final_normalized is None or not in_root_scope(final_normalized, root_url):
                exclusions.append({"url": url, "reason": "redirect-out-of-scope"})
                continue
            selected.append(url)
            for link in page.get("links", []):
                link = str(link)
                if link not in queued:
                    queued.add(link)
                    queue.append(link)

        row["status"] = "capped" if queue else "complete"
        row["attempted_urls"] = attempted
        row["selected_urls"] = selected
        row["selected_pages"] = len(selected)
        row["queue_remaining"] = len(queue)
        row["exclusions"] = exclusions
        rows.append(row)

    robots_requests = sum(int(record.get("attempts", 0)) for record in robots.values())
    body_files = list(args.body_dir.glob("*/*.html.gz")) if args.body_dir.exists() else []
    result = {
        "study": "code-sample-validity-census",
        "stage": "crawl-fallback-acquisition",
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "input_path": str(args.input),
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "page_snapshot": str(args.page_snapshot) if args.page_snapshot else None,
        "page_snapshot_sha256": hashlib.sha256(snapshot_bytes).hexdigest() if snapshot_bytes is not None else None,
        "body_dir": str(args.body_dir),
        "summary": {
            "projects": len(rows),
            "complete": sum(row["status"] == "complete" for row in rows),
            "capped": sum(row["status"] == "capped" for row in rows),
            "robots_unavailable": sum(row["status"] == "robots-unavailable" for row in rows),
            "selected_page_attachments": sum(int(row.get("selected_pages", 0)) for row in rows),
            "unique_page_records": len(page_cache),
            "robots_requests": robots_requests,
            "page_request_attempts": page_requests,
            "cache_hits": cache_hits,
            "body_blobs": len(body_files),
            "compressed_body_bytes": sum(path.stat().st_size for path in body_files),
        },
        "robots": robots,
        "pages": page_cache,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
