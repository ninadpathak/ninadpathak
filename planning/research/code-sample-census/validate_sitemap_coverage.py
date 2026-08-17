#!/usr/bin/env python3
"""Challenge sitemap populations against their own landing-page links."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from discover_page_populations import (  # noqa: E402
    MAX_ROOT_BYTES,
    fetch_bytes,
    in_root_scope,
    normalize_page_url,
    public_fetch_record,
)


def sitemap_graph(seed_urls: list[str], records: dict[str, dict[str, object]]) -> tuple[set[str], set[str]]:
    """Return fetched documents and unfetched children of fetched indexes.

    An unfetched conventional seed is not truncation: it may be deliberately
    skipped after a robots denial. Only a child named by a fetched sitemap index
    proves that the bounded traversal stopped early.
    """
    queue = [(url, False) for url in seed_urls]
    seen: set[str] = set()
    absent: set[str] = set()
    missing: set[str] = set()
    while queue:
        url, referenced_by_index = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        record = records.get(url)
        if record is None:
            absent.add(url)
            if referenced_by_index:
                missing.add(url)
            continue
        if record.get("kind") == "sitemapindex":
            queue.extend((str(location), True) for location in record.get("locations", []))
    return seen - absent, missing


def landing_links(raw: bytes, final_url: str, root_url: str) -> list[str]:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--coverage-snapshot", type=Path)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--delay-ms", type=int, default=100)
    args = parser.parse_args()

    input_bytes = args.input.read_bytes()
    source = json.loads(input_bytes)
    sitemap_records = source["sitemaps"]
    snapshot_bytes = args.coverage_snapshot.read_bytes() if args.coverage_snapshot else None
    snapshot_rows = {}
    if snapshot_bytes is not None:
        snapshot = json.loads(snapshot_bytes)
        snapshot_rows = {int(row["rank"]): row for row in snapshot["rows"]}

    graph_by_origin: dict[str, dict[str, object]] = {}
    for site_origin, robots in source["robots"].items():
        seeds = sorted(set(list(robots.get("declared_sitemaps", [])) + [site_origin + "/sitemap.xml"]))
        fetched, missing = sitemap_graph(seeds, sitemap_records)
        graph_by_origin[site_origin] = {
            "seeds": seeds,
            "reachable_fetched_documents": len(fetched),
            "referenced_unfetched_documents": len(missing),
            "referenced_unfetched_examples": sorted(missing)[:10],
            "truncated": bool(missing),
        }

    rows: list[dict[str, object]] = []
    network_attempts_this_run = 0
    for source_row in source["rows"]:
        if source_row["acquisition"] != "sitemap":
            continue
        if int(source_row["rank"]) in snapshot_rows:
            rows.append(dict(snapshot_rows[int(source_row["rank"])]))
            continue
        root_url = str(source_row["root_url"])
        population = set(str(url) for url in source_row["population_urls"])
        row: dict[str, object] = {
            "rank": source_row["rank"],
            "project": source_row["project"],
            "root_url": root_url,
            "sitemap_population_size": len(population),
            "origin_truncated": graph_by_origin[source_row["robots_origin"]]["truncated"],
        }
        try:
            fetched = fetch_bytes(root_url, args.timeout, MAX_ROOT_BYTES)
            network_attempts_this_run += int(fetched.get("attempts", 0))
            row["fetch"] = public_fetch_record(fetched)
            if int(fetched["status"]) != 200:
                row["coverage_status"] = "coverage-unverified"
                row["coverage_error"] = fetched.get("error", f"HTTP status {fetched['status']}")
            else:
                links = landing_links(fetched["raw"], str(fetched["final_url"]), root_url)  # type: ignore[arg-type]
                missing_links = sorted(set(links) - population)
                row["eligible_landing_links"] = len(links)
                row["missing_landing_links"] = missing_links
                if row["origin_truncated"]:
                    row["coverage_status"] = "sitemap-truncated"
                elif missing_links:
                    row["coverage_status"] = "coverage-failed"
                else:
                    row["coverage_status"] = "coverage-not-falsified"
        except Exception as exc:  # Preserve a row; later stages must not silently substitute.
            row["coverage_status"] = "coverage-unverified"
            row["coverage_error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)
        if args.delay_ms:
            time.sleep(args.delay_ms / 1000)

    counts: dict[str, int] = {}
    for row in rows:
        key = str(row["coverage_status"])
        counts[key] = counts.get(key, 0) + 1
    attempts = sum(int(row.get("fetch", {}).get("attempts", 0)) for row in rows if isinstance(row.get("fetch"), dict))
    redirects = sum(len(row.get("fetch", {}).get("redirects", [])) for row in rows if isinstance(row.get("fetch"), dict))
    result = {
        "study": "code-sample-validity-census",
        "stage": "sitemap-coverage-challenge",
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "input_path": str(args.input),
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "coverage_snapshot": str(args.coverage_snapshot) if args.coverage_snapshot else None,
        "coverage_snapshot_sha256": hashlib.sha256(snapshot_bytes).hexdigest() if snapshot_bytes is not None else None,
        "summary": {
            "sitemap_roots_challenged": len(rows),
            "coverage": dict(sorted(counts.items())),
            "request_attempts": attempts,
            "network_attempts_this_run": network_attempts_this_run,
            "redirect_hops": redirects,
        },
        "origin_graphs": graph_by_origin,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
