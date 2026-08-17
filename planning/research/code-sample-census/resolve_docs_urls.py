#!/usr/bin/env python3
"""Resolve declared documentation URLs for the frozen PyPI sample frame."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_code_samples import detect_generator  # noqa: E402

USER_AGENT = "ninadpathak-code-census/0.1 (+https://ninadpathak.com)"
NON_DOC_LABEL_TOKENS = {"changelog", "history", "release", "releases", "contact", "funding"}
CODE_HOSTS = {"github.com", "www.github.com", "gitlab.com", "www.gitlab.com", "bitbucket.org", "pypi.org"}
MAX_HOMEPAGE_BYTES = 5_000_000
GITHUB_LABEL_PRIORITY = {"source": 0, "repository": 1, "github repo": 2, "github": 3, "homepage": 4}


def normalize_label(label: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", label.lower()).split())


def label_priority(label: str) -> int | None:
    normalized = normalize_label(label)
    tokens = normalized.split()
    if normalized == "documentation":
        return 0
    if normalized == "docs":
        return 1
    if set(tokens) & NON_DOC_LABEL_TOKENS:
        return None
    if "documentation" in tokens:
        return 2
    if tokens and tokens[0] == "docs":
        return 3
    if "docs" in tokens:
        return 4
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


def choose_homepage(project_urls: object) -> str | None:
    if not isinstance(project_urls, dict):
        return None
    candidates = []
    for raw_label, raw_url in project_urls.items():
        url = str(raw_url).strip()
        if normalize_label(str(raw_label)) != "homepage" or not valid_web_url(url):
            continue
        hostname = (urlparse(url).hostname or "").lower()
        if hostname in CODE_HOSTS or hostname.endswith(".github.com"):
            continue
        candidates.append(url)
    return sorted(candidates)[0] if candidates else None


def choose_github_repo(project_urls: object) -> str | None:
    if not isinstance(project_urls, dict):
        return None
    candidates: list[tuple[int, str]] = []
    for raw_label, raw_url in project_urls.items():
        label = normalize_label(str(raw_label))
        url = str(raw_url).strip()
        parsed = urlparse(url)
        if (parsed.hostname or "").lower() not in {"github.com", "www.github.com"}:
            continue
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            continue
        owner, repo = parts[:2]
        repo = repo.removesuffix(".git")
        if not owner or not repo:
            continue
        priority = GITHUB_LABEL_PRIORITY.get(label, 5)
        candidates.append((priority, f"https://github.com/{owner}/{repo}"))
    return sorted(candidates)[0][1] if candidates else None


def fetch_github_repository(repo_url: str, timeout: int) -> dict[str, object]:
    parsed = urlparse(repo_url)
    owner, repo = [part for part in parsed.path.split("/") if part][:2]
    api_url = f"https://api.github.com/repos/{quote(owner, safe='')}/{quote(repo, safe='')}"
    request = Request(
        api_url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"},
    )
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
        payload = json.loads(raw)
        return {
            "repo_url": repo_url,
            "api_url": api_url,
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "full_name": payload.get("full_name"),
            "archived": payload.get("archived"),
            "homepage": payload.get("homepage"),
            "default_branch": payload.get("default_branch"),
        }


def verify_homepage(url: str, timeout: int) -> dict[str, object]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get_content_type().lower()
        if content_type not in {"text/html", "application/xhtml+xml"}:
            raise ValueError(f"non-HTML content type: {content_type}")
        raw = response.read(MAX_HOMEPAGE_BYTES + 1)
        if len(raw) > MAX_HOMEPAGE_BYTES:
            raise ValueError(f"homepage exceeds {MAX_HOMEPAGE_BYTES} bytes")
        generator = detect_generator(BeautifulSoup(raw, "html.parser"))
        if generator == "unknown":
            raise ValueError("unsupported documentation generator")
        return {
            "declared_url": url,
            "url": response.geturl(),
            "generator": generator,
            "content_type": content_type,
            "bytes": len(raw),
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
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


def load_metadata_snapshot(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("metadata snapshot has no rows")
    return rows


def load_frame(path: Path) -> list[tuple[int, str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [(rank, row["project"], int(row["downloads"])) for rank, row in enumerate(rows, start=1)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata-snapshot", type=Path)
    parser.add_argument("--validate-homepages", action="store_true")
    parser.add_argument("--validate-repository-homepages", action="store_true")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--delay-ms", type=int, default=100)
    args = parser.parse_args()

    resolved: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    if args.metadata_snapshot:
        for prior in load_metadata_snapshot(args.metadata_snapshot):
            row = dict(prior)
            selected = choose_docs_url(row.get("project_urls"))
            row["selected_docs"] = selected
            row["resolution"] = "label-resolved" if selected else "unresolved"
            resolved.append(row)
    else:
        for rank, project, downloads in load_frame(args.sample):
            try:
                raw, source_url = fetch_project(project, args.timeout)
                row = resolve_one(rank, project, downloads, raw, source_url)
                row["resolution"] = "label-resolved" if row["selected_docs"] else "unresolved"
                resolved.append(row)
            except (HTTPError, URLError, json.JSONDecodeError) as exc:
                errors.append({"rank": rank, "project": project, "error": f"{type(exc).__name__}: {exc}"})
            if args.delay_ms:
                time.sleep(args.delay_ms / 1000)

    homepage_attempts = 0
    homepage_errors = 0
    if args.validate_homepages:
        for row in resolved:
            if row["resolution"] != "unresolved":
                continue
            homepage = choose_homepage(row.get("project_urls"))
            row["homepage_candidate"] = homepage
            if homepage is None:
                continue
            homepage_attempts += 1
            try:
                verified = verify_homepage(homepage, args.timeout)
                row["selected_docs"] = verified
                row["resolution"] = "homepage-resolved"
            except (HTTPError, URLError, ValueError) as exc:
                homepage_errors += 1
                row["homepage_error"] = f"{type(exc).__name__}: {exc}"
            if args.delay_ms:
                time.sleep(args.delay_ms / 1000)

    repository_attempts = 0
    repository_homepages = 0
    repository_resolved = 0
    repository_errors = 0
    if args.validate_repository_homepages:
        for row in resolved:
            if row["resolution"] != "unresolved":
                continue
            repo_url = choose_github_repo(row.get("project_urls"))
            row["repository_candidate"] = repo_url
            if repo_url is None:
                continue
            repository_attempts += 1
            try:
                repository = fetch_github_repository(repo_url, args.timeout)
                row["repository_metadata"] = repository
                homepage = repository.get("homepage")
                if not isinstance(homepage, str) or not valid_web_url(homepage):
                    continue
                if (urlparse(homepage).hostname or "").lower() in CODE_HOSTS:
                    continue
                repository_homepages += 1
                verified = verify_homepage(homepage, args.timeout)
                verified["repository"] = repo_url
                row["selected_docs"] = verified
                row["resolution"] = "repository-homepage-resolved"
                repository_resolved += 1
            except (HTTPError, URLError, ValueError, json.JSONDecodeError) as exc:
                repository_errors += 1
                row["repository_error"] = f"{type(exc).__name__}: {exc}"
            if args.delay_ms:
                time.sleep(args.delay_ms / 1000)

    label_resolved = sum(row["resolution"] == "label-resolved" for row in resolved)
    homepage_resolved = sum(row["resolution"] == "homepage-resolved" for row in resolved)
    repository_resolved = sum(row["resolution"] == "repository-homepage-resolved" for row in resolved)
    unresolved = sum(row["resolution"] == "unresolved" for row in resolved)
    result = {
        "study": "code-sample-validity-census",
        "stage": "documentation-url-resolution",
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sample_path": str(args.sample),
        "sample_sha256": hashlib.sha256(args.sample.read_bytes()).hexdigest(),
        "metadata_snapshot": str(args.metadata_snapshot) if args.metadata_snapshot else None,
        "selection_rule": {
            "label": "documentation/docs token excluding changelog, history, release, contact, funding",
            "homepage": "non-code-host Homepage accepted only when a supported docs generator is detected",
        },
        "summary": {
            "frame_rows": len(resolved) + len(errors),
            "metadata_fetched": len(resolved),
            "label_resolved": label_resolved,
            "homepage_attempts": homepage_attempts,
            "homepage_resolved": homepage_resolved,
            "homepage_errors": homepage_errors,
            "repository_attempts": repository_attempts,
            "repository_homepages": repository_homepages,
            "repository_resolved": repository_resolved,
            "repository_errors": repository_errors,
            "unresolved": unresolved,
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
