"""Deterministic contract tests for the pre-merge Search Console guard."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import gsc_merge_guard as mg  # noqa: E402

BASE = "https://ninadpathak.com"


def period(page_rows=(), human_by_page=None, named_by_page=None, pq_rows=()):
    rows = list(page_rows)
    return {
        "page_rows": rows,
        "by_page": {row["keys"][0]: row for row in rows},
        "human_by_page": human_by_page or {},
        "named_by_page": named_by_page or {},
        "pq_rows": list(pq_rows),
    }


def page(slug, impressions=10, position=20, clicks=0, prefix="/blog/"):
    return {"keys": [f"{BASE}{prefix}{slug}/"], "impressions": impressions,
            "clicks": clicks, "position": position}


def query(slug, text, impressions=3, position=15, prefix="/blog/"):
    return {"keys": [text], "page": f"{BASE}{prefix}{slug}/",
            "impressions": impressions, "clicks": 0, "position": position}


class TestAuditParser(unittest.TestCase):
    def test_parses_merge_and_retirement_only_from_disposition_table(self):
        text = """before
### Merge, 2 pages
