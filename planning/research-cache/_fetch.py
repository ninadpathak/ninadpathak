#!/usr/bin/env python3
"""Paid Ahrefs fetch harness for the addressable-universe recompute.

Calls the same Ahrefs API v3 endpoint the MCP server wraps, using the same
credential, but writes the raw JSON straight to the research cache instead of
routing ~100KB per call through an agent context.

Prints only a compact summary. Never prints the credential.

Usage: _fetch.py <cache-name> <seed1,seed2,...> [--volmin N] [--kdmax N] [--limit N]
"""
import json
import os
import re
import sys
import datetime
import urllib.parse
import urllib.request

CACHE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://api.ahrefs.com/v3/keywords-explorer/matching-terms"
SELECT = "keyword,volume,difficulty,cpc,traffic_potential,parent_topic,intents,serp_features"


def token():
    d = json.load(open(os.path.expanduser("~/.claude.json")))
    auth = d["mcpServers"]["ahrefs"]["headers"]["Authorization"]
    return auth.split(None, 1)[1] if auth.lower().startswith("bearer") else auth


def units_used():
    """Free endpoint - snapshot workspace unit meter."""
    req = urllib.request.Request(
        "https://api.ahrefs.com/v3/subscription-info/limits-and-usage",
        headers={"Authorization": f"Bearer {token()}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
    return d["limits_and_usage"]["units_usage_workspace"]


def fetch(name, seeds, volmin=30, kdmax=45, limit=250, country="us",
          match_mode="terms", terms="all"):
    where = {"and": [{"field": "volume", "is": ["gte", volmin]},
                     {"field": "difficulty", "is": ["lte", kdmax]}]}
    params = {
        "select": SELECT, "country": country, "keywords": seeds,
        "match_mode": match_mode, "terms": terms, "limit": str(limit),
        "order_by": "volume:desc", "where": json.dumps(where, separators=(",", ":")),
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token()}", "Accept": "application/json"})

    before = units_used()
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            payload = json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        print(f"HTTP {e.code} :: {body}")
        print(f"LOGROW|{ts}|{name}|{seeds}|FAILED|0|none - HTTP {e.code}: {body[:120]}")
        return None
    after = units_used()

    rows = payload.get("keywords", [])
    path = os.path.join(CACHE, f"{name}.json")
    with open(path, "w") as f:
        json.dump(rows, f, indent=1)

    vol = sum(r.get("volume") or 0 for r in rows)
    kd20 = [r for r in rows if r.get("difficulty") is not None and r["difficulty"] <= 20]
    print(f"{name}: rows={len(rows)} vol={vol} kd<=20={len(kd20)}/{sum(r.get('volume') or 0 for r in kd20)} units={after-before}")
    if rows:
        print("  top: " + " | ".join(f"{r['keyword']}({r.get('volume')},KD{r.get('difficulty')})"
                                     for r in rows[:6]))
    print(f"LOGROW|{ts}|{name}|{seeds}|{len(rows)}|{after-before}|{name}.json")
    return rows


if __name__ == "__main__":
    a = sys.argv[1:]
    name, seeds = a[0], a[1]
    kw = {}
    for i, x in enumerate(a):
        if x == "--volmin": kw["volmin"] = int(a[i + 1])
        if x == "--kdmax": kw["kdmax"] = int(a[i + 1])
        if x == "--limit": kw["limit"] = int(a[i + 1])
    fetch(name, seeds, **kw)
