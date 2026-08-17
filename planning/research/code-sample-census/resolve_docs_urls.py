#!/usr/bin/env python3
"""Resolve declared documentation URLs for the frozen PyPI sample frame."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

USER_AGENT = "ninadpathak-code-census/0.1 (+https://ninadpathak.com)"


def normalize_label(label: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", label.lower()).split())


def label_priority(label: str) -> int | None:
    normalized = normalize_label(label)
    if normalized == "documentation":
        return 0
    if normalized == "docs":
        return 1
    if normalized.endswith(" documentation"):
        return 2
    if normalized.endswith(" docs"):
        return 3
    return None


def valid_web_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def choose_docs_url(project_urls: object) -> dict[str, object] | None:
    if not isinstance(project_urls, dict):
        return None
    candidates: list[tuple[int, str, str, str]] = []
    for raw_label, raw_url in project_urls.items():
        label = str(raw_label).strip()
        url = str(raw_url).strip()
        priority = label_priority(label)
        if priority is not None and valid_web_url(url):
            candidates.append((priority, normalize_label(label), label, url))
    if not candidates:
        return None
    priority, normalized, label, url = sorted(candidates)[0]
    return {
        "label": label,
        "normalized_label": normalized,
        "priority": priority,
        "url": url,
        "candidate_count": len(candidates),
    }


def fetch_project(project: str, timeout: int, attempts: int = 3) -> tuple[bytes, str]:
    url = f"https://pypi.org/pypi/{quote(project, safe='')}/json"
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urlopen(request, timeout=timeout) as response:
                return response.read(), response.geturl()
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == attempts:
                raise
            retry_after = exc.headers.get("Retry-After")
            delay = min(float(retry_after), 5.0) if retry_after and retry_after.isdigit() else float(attempt)
            time.sleep(delay)
        except URLError:
            if attempt == attempts:
                raise
            time.sleep(float(attempt))
    raise AssertionError("retry loop exhausted")


def resolve_one(rank: int, project: str, downloads: int, raw: bytes, source_url: str) -> dict[str, object]:
    payload = json.loads(raw)
    info = payload.get("info") or {}
    project_urls = info.get("project_urls") or {}
    selected = choose_docs_url(project_urls)
    return {
        "rank": rank,
        "project": project,
        "downloads": downloads,
        "source_url": source_url,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "last_serial": payload.get("last_serial"),
        "canonical_name": info.get("name"),
        "version": info.get("version"),
        "project_urls": project_urls,
        "selected_docs": selected,
        "resolution": "declared-docs" if selected else "no-declared-docs",
    }


def load_frame(path: Path) -> list[tuple[int, str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [(rank, row["project"], int(row["downloads"])) for rank, row in enumerate(rows, start=1)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--delay-ms", type=int, default=100)
    args = parser.parse_args()

    resolved: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    for rank, project, downloads in load_frame(args.sample):
        try:
            raw, source_url = fetch_project(project, args.timeout)
            resolved.append(resolve_one(rank, project, downloads, raw, source_url))
        except (HTTPError, URLError, json.JSONDecodeError) as exc:
            errors.append({"rank": rank, "project": project, "error": f"{type(exc).__name__}: {exc}"})
        if args.delay_ms:
            time.sleep(args.delay_ms / 1000)

    declared = sum(row["resolution"] == "declared-docs" for row in resolved)
    result = {
        "study": "code-sample-validity-census",
        "stage": "documentation-url-resolution",
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sample_path": str(args.sample),
        "sample_sha256": hashlib.sha256(args.sample.read_bytes()).hexdigest(),
        "selection_rule": [
            "exact documentation",
            "exact docs",
            "label ending documentation",
            "label ending docs",
        ],
        "summary": {
            "frame_rows": len(resolved) + len(errors),
            "metadata_fetched": len(resolved),
            "declared_docs": declared,
            "no_declared_docs": len(resolved) - declared,
            "fetch_errors": len(errors),
        },
        "rows": resolved,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())

