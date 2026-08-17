#!/usr/bin/env python3
"""Inspect every mechanically resolved documentation root before crawling pages."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_code_samples import detect_generator  # noqa: E402

USER_AGENT = "ninadpathak-code-census/0.1 (+https://ninadpathak.com)"
MAX_ROOT_BYTES = 5_000_000
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class RecordingRedirectHandler(HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self.chain: list[dict[str, object]] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        self.chain.append({"status": code, "from": req.full_url, "to": newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def selected_url(row: dict[str, object]) -> str:
    selected = row.get("selected_docs")
    if not isinstance(selected, dict):
        raise ValueError("resolved row has no selected_docs object")
    url = selected.get("url")
    if not isinstance(url, str) or not url:
        raise ValueError("resolved row has no selected_docs.url")
    return url


def canonical_url(soup: BeautifulSoup, final_url: str) -> str | None:
    for link in soup.find_all("link"):
        rel = link.get("rel") or []
        if isinstance(rel, str):
            rel = rel.split()
        if "canonical" not in [str(value).lower() for value in rel]:
            continue
        href = link.get("href")
        if isinstance(href, str) and href.strip():
            return urljoin(final_url, href.strip())
    return None


def normalized_host(url: str | None) -> str | None:
    if not url:
        return None
    return (urlparse(url).hostname or "").lower() or None


def inspect_url(url: str, timeout: int, attempts: int = 3) -> dict[str, object]:
    request_attempts = 0
    all_redirects: list[dict[str, object]] = []
    for attempt in range(1, attempts + 1):
        request_attempts += 1
        handler = RecordingRedirectHandler()
        opener = build_opener(handler)
        request = Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        )
        try:
            with opener.open(request, timeout=timeout) as response:
                all_redirects.extend(handler.chain)
                raw = response.read(MAX_ROOT_BYTES + 1)
                if len(raw) > MAX_ROOT_BYTES:
                    raise ValueError(f"root exceeds {MAX_ROOT_BYTES} bytes")
                content_type = response.headers.get_content_type().lower()
                final_url = response.geturl()
                is_html = content_type in {"text/html", "application/xhtml+xml"}
                soup = BeautifulSoup(raw, "html.parser") if is_html else None
                generator = detect_generator(soup) if soup is not None else "not-html"
                canonical = canonical_url(soup, final_url) if soup is not None else None
                return {
                    "status": getattr(response, "status", response.getcode()),
                    "final_url": final_url,
                    "redirects": all_redirects,
                    "redirect_count": len(all_redirects),
                    "request_attempts": request_attempts,
                    "content_type": content_type,
                    "bytes": len(raw),
                    "response_sha256": hashlib.sha256(raw).hexdigest(),
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "generator": generator,
                    "supported_generator": generator not in {"unknown", "not-html"},
                    "canonical_url": canonical,
                    "final_host": normalized_host(final_url),
                    "canonical_host": normalized_host(canonical),
                }
        except HTTPError as exc:
            all_redirects.extend(handler.chain)
            if exc.code not in RETRYABLE_STATUS or attempt == attempts:
                raise RootInspectionError(exc, request_attempts, all_redirects) from exc
            retry_after = exc.headers.get("Retry-After")
            delay = min(float(retry_after), 5.0) if retry_after and retry_after.isdigit() else float(attempt)
            time.sleep(delay)
        except URLError as exc:
            all_redirects.extend(handler.chain)
            if attempt == attempts:
                raise RootInspectionError(exc, request_attempts, all_redirects) from exc
            time.sleep(float(attempt))
    raise AssertionError("retry loop exhausted")


class RootInspectionError(Exception):
    def __init__(self, cause: Exception, request_attempts: int, redirects: list[dict[str, object]]) -> None:
        super().__init__(f"{type(cause).__name__}: {cause}")
        self.request_attempts = request_attempts
        self.redirects = redirects


def candidate_shared_hosts(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        inspection = row.get("inspection")
        if not isinstance(inspection, dict):
            continue
        host = inspection.get("canonical_host") or inspection.get("final_host")
        if not isinstance(host, str):
            continue
        groups.setdefault(host, []).append(
            {
                "rank": row["rank"],
                "project": row["project"],
                "final_url": inspection.get("final_url"),
                "canonical_url": inspection.get("canonical_url"),
            }
        )
    return [
        {"host": host, "projects": sorted(projects, key=lambda item: int(item["rank"]))}
        for host, projects in sorted(groups.items())
        if len(projects) > 1
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--delay-ms", type=int, default=150)
    args = parser.parse_args()

    input_bytes = args.input.read_bytes()
    source = json.loads(input_bytes)
    source_rows = source.get("rows")
    if not isinstance(source_rows, list):
        raise ValueError("input has no rows")

    rows: list[dict[str, object]] = []
    for source_row in source_rows:
        if not isinstance(source_row, dict) or source_row.get("resolution") == "unresolved":
            continue
        row: dict[str, object] = {
            "rank": source_row["rank"],
            "project": source_row["project"],
            "resolution": source_row["resolution"],
            "declared_url": selected_url(source_row),
        }
        try:
            row["inspection"] = inspect_url(str(row["declared_url"]), args.timeout)
        except (RootInspectionError, ValueError) as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
            if isinstance(exc, RootInspectionError):
                row["request_attempts"] = exc.request_attempts
                row["redirects"] = exc.redirects
        rows.append(row)
        if args.delay_ms:
            time.sleep(args.delay_ms / 1000)

    inspected = [row for row in rows if "inspection" in row]
    errors = [row for row in rows if "error" in row]
    supported = [row for row in inspected if row["inspection"]["supported_generator"]]  # type: ignore[index]
    generators: dict[str, int] = {}
    request_attempts = 0
    redirects = 0
    for row in rows:
        inspection = row.get("inspection")
        if isinstance(inspection, dict):
            generator = str(inspection["generator"])
            generators[generator] = generators.get(generator, 0) + 1
            request_attempts += int(inspection["request_attempts"])
            redirects += int(inspection["redirect_count"])
        else:
            request_attempts += int(row.get("request_attempts", 0))
            redirects += len(row.get("redirects", [])) if isinstance(row.get("redirects"), list) else 0

    result = {
        "study": "code-sample-validity-census",
        "stage": "documentation-root-inspection",
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "input_path": str(args.input),
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "summary": {
            "selected_roots": len(rows),
            "inspected": len(inspected),
            "errors": len(errors),
            "supported_generators": len(supported),
            "unsupported_or_non_html": len(inspected) - len(supported),
            "request_attempts": request_attempts,
            "redirect_hops": redirects,
            "generators": dict(sorted(generators.items())),
        },
        "candidate_shared_hosts": candidate_shared_hosts(rows),
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"summary": result["summary"], "candidate_shared_hosts": result["candidate_shared_hosts"]}, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
