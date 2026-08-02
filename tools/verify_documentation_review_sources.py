#!/usr/bin/env python3
"""Verify the three live documentation sources used in the review article.

Run: python3 tools/verify_documentation_review_sources.py

The check only asserts that each first-party page is reachable and still exposes
terms discussed in the article. It does not claim to execute an API request or
validate a product integration.
"""
from __future__ import annotations

import sys
import urllib.request

SOURCES = {
    "fastapi": (
        "https://fastapi.tiangolo.com/tutorial/handling-errors/",
        ("HTTPException", "detail"),
    ),
    "stripe": (
        "https://docs.stripe.com/api/idempotent_requests",
        ("Idempotency-Key", "same key"),
    ),
    "github": (
        "https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api",
        ("x-ratelimit-remaining", "secondary rate limits"),
    ),
}


def main() -> int:
    failures = []
    for name, (url, terms) in SOURCES.items():
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "ninadpathak-documentation-review/1.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8", "replace")
                status = response.status
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {name}: {exc}")
            failures.append(name)
            continue

        missing = [term for term in terms if term.lower() not in body.lower()]
        if status != 200 or missing:
            print(f"FAIL {name}: status={status} missing={','.join(missing) or '-'}")
            failures.append(name)
            continue
        print(f"PASS {name}: status=200 terms={','.join(terms)}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
