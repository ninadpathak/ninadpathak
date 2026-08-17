#!/usr/bin/env python3
"""Freeze and verify a top-project sample frame from ClickPy.

This script has no third-party dependencies. It writes a CSV plus a JSON receipt
containing the exact query and response hash so a rerun can be compared without
silently replacing the study population.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_ENDPOINT = "https://sql-clickhouse.clickhouse.com/"


def build_query(end_date: date, days: int, limit: int) -> str:
    if days < 1:
        raise ValueError("days must be positive")
    if limit < 1:
        raise ValueError("limit must be positive")
    start_date = end_date - timedelta(days=days - 1)
    return f"""SELECT
    project,
    sum(count) AS downloads
FROM pypi.pypi_downloads_per_day
WHERE date BETWEEN toDate('{start_date.isoformat()}') AND toDate('{end_date.isoformat()}')
GROUP BY project
ORDER BY downloads DESC, project ASC
LIMIT {limit}
FORMAT CSVWithNames
"""


def fetch_csv(endpoint: str, query: str, timeout: int) -> bytes:
    auth = base64.b64encode(b"demo:").decode("ascii")
    request = Request(
        endpoint,
        data=query.encode("utf-8"),
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "text/plain; charset=utf-8",
            "User-Agent": "ninadpathak-code-census/0.1 (+https://ninadpathak.com)",
        },
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"ClickPy returned HTTP {response.status}")
        return response.read()


def validate_csv(raw: bytes, expected_rows: int) -> list[dict[str, object]]:
    text = raw.decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))
    if len(rows) != expected_rows:
        raise ValueError(f"expected {expected_rows} rows, received {len(rows)}")
    if not rows or set(rows[0]) != {"project", "downloads"}:
        raise ValueError("unexpected CSV columns")

    parsed: list[dict[str, object]] = []
    seen: set[str] = set()
    previous: tuple[int, str] | None = None
    for row in rows:
        project = row["project"].strip()
        downloads = int(row["downloads"])
        if not project or project in seen:
            raise ValueError(f"blank or duplicate project: {project!r}")
        seen.add(project)
        current = (downloads, project)
        if previous is not None:
            if downloads > previous[0]:
                raise ValueError("download counts are not descending")
            if downloads == previous[0] and project < previous[1]:
                raise ValueError("project tie-break is not ascending")
        previous = current
        parsed.append({"project": project, "downloads": downloads})
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--end-date", type=date.fromisoformat, required=True)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    query = build_query(args.end_date, args.days, args.limit)
    raw = fetch_csv(args.endpoint, query, args.timeout)
    rows = validate_csv(raw, args.limit)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.csv.write_bytes(raw)

    receipt = {
        "study": "code-sample-validity-census",
        "source": "ClickPy mirror of PyPI Linehaul download data",
        "endpoint": args.endpoint,
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "window_days": args.days,
        "end_date": args.end_date.isoformat(),
        "start_date": (args.end_date - timedelta(days=args.days - 1)).isoformat(),
        "limit": args.limit,
        "query": query,
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "row_count": len(rows),
        "first_project": rows[0],
        "last_project": rows[-1],
        "validation": {
            "unique_projects": True,
            "downloads_descending": True,
            "project_tiebreak_ascending": True,
        },
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
