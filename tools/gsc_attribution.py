#!/usr/bin/env python3
"""Per-page attribution: does anything the campaign ships actually earn?

Every other Search Console tool here reports the site. This one reports individual
shipped pages against their own publish date, which is the only way to tell which lever
works while the sitewide numbers are all zero. A zero sitewide says nothing about whether
tools beat articles; that question is per-page and time-since-publish, not sitewide.

For each page published or substantially changed since TRACK_FROM, and for every tool
regardless of age:

    days to first impression
    days to first human impression
    days to first human click
    position trajectory since publish
    cluster

THE BET THIS IS BUILT TO TEST, AND WHAT IT CANNOT TEST
------------------------------------------------------
The campaign originally weighted tools over articles because the keyword research said no
build-a-tool keyword carried an AI Overview while all 15 top keywords did. Live SERP reads
later falsified that premise and tool building stopped at five. **That was a claim about
other people's SERPs, and this tool could never verify it.** Search Console has no AI
Overview dimension: there is no first-party way to see whether one appeared above our
result. Anything claiming otherwise would be invented.

What is measurable is the bet's downstream consequence. If tool pages are less exposed to
AI Overview click suppression, they should reach impressions sooner and convert
impressions to clicks better than articles at comparable positions. Days-to-first-impression
is measurable now. The click comparison needs clicks, and the site has none, so that column
stays empty and says so.

HOW A MISSING NUMBER IS REPORTED
--------------------------------
Three states, never collapsed into a zero:

    no data yet     the page is younger than the Search Console lag, so absence of an
                    impression is not evidence of anything
    not yet, N days observable for N days and still no impression - this IS a measurement
    a number        days from publish to the first impression

A zero would read as "it happened on day zero", which is the opposite of "we cannot know".

    tools/gsc_attribution.py              # upsert today's planning/attribution.md section
    tools/gsc_attribution.py --dry-run
    tools/gsc_attribution.py --track-from 2026-08-01
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gsc_report as gr  # noqa: E402

LOG = gr.ROOT / "planning" / "attribution.md"
TRACK_FROM = dt.date(2026, 8, 14)
# A commit touching a post by at least this many lines counts as a republish for
# attribution: a reader-visible rewrite resets what Google is being asked to rank.
SUBSTANTIAL_LINES = 30
# A page needs at least this many observable days before its lifetime performance says
# anything. Below it, silence is just youth.
AGED_DAYS = 30
# Median days-to-first-impression within this many days of each other is one figure, not
# two. Guards against reading a 2-day gap on a sample of one as a finding.
INDISTINGUISHABLE_DAYS = 7
BASE = "https://ninadpathak.com"

# The tools are tracked regardless of age because they are the priority lever and the
# whole calendar weighting rests on them. Template path -> live URL.
TOOLS = {
    "templates/linter.html": "/linter/",
    "templates/llms_txt_generator.html": "/llms-txt-generator/",
    "templates/llms_txt_validator.html": "/llms-txt-validator/",
    "templates/ai_overviews_checker.html": "/ai-overviews-checker/",
    "templates/ai_crawler_checker.html": "/ai-crawler-checker/",
}
DATED_SECTION = re.compile(
    r"(?m)^## (?P<date>\d{4}-\d{2}-\d{2}) — attribution since \d{4}-\d{2}-\d{2}\s*$"
)


def git(*args: str) -> str:
    p = subprocess.run(("git", *args), cwd=gr.ROOT, capture_output=True, text=True)
    return p.stdout.strip()


def first_added(path: str, ref: str = "origin/main") -> dt.date | None:
    out = git("log", ref, "--diff-filter=A", "--format=%ad", "--date=short", "-1",
              "--", path)
    return dt.date.fromisoformat(out.splitlines()[-1]) if out else None


def last_substantial_change(path: str, since: dt.date,
                            ref: str = "origin/main") -> dt.date | None:
    """Most recent commit since `since` that changed the file by SUBSTANTIAL_LINES+."""
    out = git("log", ref, f"--since={since.isoformat()}", "--format=%H|%ad",
              "--date=short", "--", path)
    best = None
    for line in out.splitlines():
        sha, _, date = line.partition("|")
        stat = git("show", "--numstat", "--format=", sha, "--", path)
        changed = 0
        for row in stat.splitlines():
            parts = row.split("\t")
            if len(parts) >= 2:
                added, removed = (int(x) if x.isdigit() else 0 for x in parts[:2])
                changed += added + removed
        if changed >= SUBSTANTIAL_LINES:
            d = dt.date.fromisoformat(date)
            if best is None or d > best:
                best = d
    return best


def tracked_pages(track_from: dt.date) -> list[dict]:
    """Posts shipped or substantially rewritten since track_from, plus every tool."""
    import frontmatter

    out = []
    for path in sorted((gr.ROOT / "content" / "posts").glob("*.md")):
        rel = str(path.relative_to(gr.ROOT))
        data = frontmatter.load(path)
        if data.get("status") != "published":
            continue
        added = first_added(rel)
        changed = last_substantial_change(rel, track_from)
        if added is None:
            continue
        if added < track_from and changed is None:
            continue
        slug = str(data.get("slug") or path.stem)
        category = data.get("category")
        out.append({
            "kind": "article",
            "url": f"{BASE}/articles/{slug}/",
            "slug": slug,
            "cluster": gr.RETIRED_CLUSTER_SLUGS.get(category, category),
            "shipped": added.isoformat(),
            "rewritten": changed.isoformat() if changed and changed > added else None,
            # A page shipped before tracking began is pre-existing however heavily it was
            # just rewritten. Conflating the two produced a median of -15 days, because a
            # voice sweep touched sixty articles that had been live for months.
            "basis": "new" if added >= track_from else "pre-existing",
            "title": str(data.get("title", slug))[:60],
        })

    for template, url in TOOLS.items():
        added = first_added(template)
        if added is None:
            continue
        changed = last_substantial_change(template, track_from)
        out.append({
            "kind": "tool",
            "url": BASE + url,
            "slug": url.strip("/"),
            "cluster": gr.TOOL_PATHS.get(url),
            "shipped": added.isoformat(),
            "rewritten": changed.isoformat() if changed and changed > added else None,
            "basis": "new" if added >= track_from else "pre-existing",
            "title": url,
        })
    return sorted(out, key=lambda r: (r["kind"], r["shipped"]))


def fetch_rows(svc, body: dict, row_limit: int = 25000) -> list[dict]:
    """Fetch every GSC row; the API otherwise silently stops at ``rowLimit``.

    Attribution expands each observation by date and page, and the human-floor pull
    expands it again by query. Both can cross 25,000 rows even when the page-level totals
    look small. A truncated pull would understate named-query coverage and make withheld
    demand look larger than it is.
    """
    rows: list[dict] = []
    start_row = 0
    while True:
        request = dict(body)
        request["rowLimit"] = row_limit
        request["startRow"] = start_row
        batch = svc.searchanalytics().query(siteUrl=gr.SITE, body=request).execute().get(
            "rows", []
        )
        rows.extend(batch)
        if len(batch) < row_limit:
            return rows
        start_row += len(batch)


def daily_by_page(svc, start: str, end: str) -> dict[str, dict[str, dict]]:
    """{url: {date: {clicks, impressions, position}}} — complete, page dimension."""
    body = {"startDate": start, "endDate": end, "dimensions": ["date", "page"]}
    rows = fetch_rows(svc, body)
    out: dict[str, dict[str, dict]] = {}
    for r in rows:
        date, url = r["keys"]
        out.setdefault(url, {})[date] = {
            "clicks": r["clicks"], "impressions": r["impressions"],
            "position": r["position"]}
    return out


def daily_queries_by_page(svc, start: str, end: str) -> dict[str, dict[str, dict[str, dict]]]:
    """Return named-query totals and the visible human subset, both by page and date.

    ``named`` is still incomplete because GSC withholds low-volume queries. ``human`` is a
    floor inside that incomplete set after brand, blob and machine-family removal. Keeping
    both lets the report state the exact floor-to-ceiling interval instead of repeating a
    stale sitewide coverage approximation.
    """
    body = {"startDate": start, "endDate": end,
            "dimensions": ["date", "page", "query"]}
    rows = fetch_rows(svc, body)
    as_query = [{"keys": [r["keys"][2]], "clicks": r["clicks"],
                 "impressions": r["impressions"], "position": r["position"],
                 "date": r["keys"][0], "page": r["keys"][1]} for r in rows]
    human = gr.partition_queries(as_query)["human"]
    named_out: dict[str, dict[str, dict]] = {}
    for r in as_query:
        b = named_out.setdefault(r["page"], {}).setdefault(r["date"], {
            "clicks": 0.0, "impressions": 0.0})
        b["clicks"] += r["clicks"]
        b["impressions"] += r["impressions"]
    human_out: dict[str, dict[str, dict]] = {}
    for r in human:
        b = human_out.setdefault(r["page"], {}).setdefault(r["date"], {
            "clicks": 0.0, "impressions": 0.0})
        b["clicks"] += r["clicks"]
        b["impressions"] += r["impressions"]
    return {"named": named_out, "human": human_out}


def first_day(series: dict[str, dict], start: dt.date, field: str) -> int | None:
    """Days from start to the first date where `field` is positive."""
    hits = sorted(d for d, v in series.items() if v.get(field, 0) > 0)
    if not hits:
        return None
    return (dt.date.fromisoformat(hits[0]) - start).days


def trajectory(series: dict[str, dict]) -> list[dict]:
    """Impression-weighted position per calendar week since publish."""
    weeks: dict[str, dict] = {}
    for date, v in series.items():
        d = dt.date.fromisoformat(date)
        key = d.isocalendar()
        label = f"{key[0]}-W{key[1]:02d}"
        b = weeks.setdefault(label, {"impressions": 0.0, "weighted": 0.0, "clicks": 0.0})
        b["impressions"] += v["impressions"]
        b["clicks"] += v.get("clicks", 0)
        b["weighted"] += v.get("position", 0) * v["impressions"]
    return [{"week": k,
             "impressions": int(b["impressions"]), "clicks": int(b["clicks"]),
             "position": round(b["weighted"] / b["impressions"], 1) if b["impressions"] else None}
            for k, b in sorted(weeks.items())]


def describe(days: int | None, observable: int) -> str:
    """One of three states, never a bare zero."""
    if observable < 0:
        return "no data yet"
    if days is None:
        return f"not yet, {observable}d"
    return f"{days}d"


def build(svc, track_from: dt.date, today: dt.date) -> dict:
    latest = today - dt.timedelta(days=gr.GSC_LAG_DAYS)
    pages = tracked_pages(track_from)
    if not pages:
        return {"generated": today.isoformat(), "latest_data": latest.isoformat(),
                "track_from": track_from.isoformat(), "pages": [], "comparison": None}

    window_start = min([dt.date.fromisoformat(p["shipped"]) for p in pages]
                       + [track_from - dt.timedelta(days=35)])
    window_start = min(window_start, latest)
    all_daily = daily_by_page(svc, window_start.isoformat(), latest.isoformat())
    query_daily = daily_queries_by_page(svc, window_start.isoformat(), latest.isoformat())
    named_daily = query_daily["named"]
    human_daily = query_daily["human"]

    for p in pages:
        start = dt.date.fromisoformat(p["shipped"])
        observable = (latest - start).days
        # /blog/<slug>/ is the pre-migration path and still carries most traffic, so a
        # page's history lives under both prefixes. Merge them or every article looks new.
        series: dict[str, dict] = {}
        nseries: dict[str, dict] = {}
        hseries: dict[str, dict] = {}
        for prefix in ("/articles/", "/blog/") if p["kind"] == "article" else ("",):
            url = (f"{BASE}{prefix}{p['slug']}/" if prefix else p["url"])
            for src, dst in ((all_daily.get(url, {}), series),
                             (named_daily.get(url, {}), nseries),
                             (human_daily.get(url, {}), hseries)):
                for date, v in src.items():
                    b = dst.setdefault(date, {"clicks": 0.0, "impressions": 0.0,
                                              "position": v.get("position", 0)})
                    b["clicks"] += v.get("clicks", 0)
                    b["impressions"] += v["impressions"]
        p["observable_days"] = observable
        p["impressions"] = int(sum(v["impressions"] for v in series.values()))
        p["clicks"] = int(sum(v["clicks"] for v in series.values()))
        p["named_query_impressions"] = int(
            sum(v["impressions"] for v in nseries.values())
        )
        p["human_impressions"] = int(sum(v["impressions"] for v in hseries.values()))
        p["human_clicks"] = int(sum(v["clicks"] for v in hseries.values()))
        p["withheld_impressions"] = max(
            p["impressions"] - p["named_query_impressions"], 0
        )
        p["human_impressions_upper"] = (
            p["human_impressions"] + p["withheld_impressions"]
        )
        p["query_coverage_pct"] = (
            round(100 * p["named_query_impressions"] / p["impressions"], 1)
            if p["impressions"] else None
        )
        p["days_to_first_impression"] = first_day(series, start, "impressions")
        p["days_to_first_human_impression"] = first_day(hseries, start, "impressions")
        p["days_to_first_human_click"] = first_day(hseries, start, "clicks")
        p["trajectory"] = trajectory(series)
        # A URL can earn impressions before its current source file existed: the AI cluster
        # was recovered from 404, so those files are recent while the URLs have ranked for
        # months. Negative days are that, not a fast start, and they disqualify the page
        # from a days-to-first comparison.
        p["recovered_url"] = (p["days_to_first_impression"] is not None
                              and p["days_to_first_impression"] < 0)

    # The bet is about newly shipped pages. Pre-existing pages and recovered URLs carry
    # history that has nothing to do with how fast a new publish reaches search.
    def eligible(kind):
        return [p for p in pages if p["kind"] == kind and p["basis"] == "new"
                and not p["recovered_url"]]

    comparison = {}
    for kind in ("tool", "article"):
        elig = eligible(kind)
        obs = [p for p in elig if p["observable_days"] >= 0]
        got = [p["days_to_first_impression"] for p in obs
               if p["days_to_first_impression"] is not None]
        comparison[kind] = {
            "tracked": sum(1 for p in pages if p["kind"] == kind),
            "eligible": len(elig),
            "observable": len(obs),
            "reached_impression": len(got),
            "median_days": (sorted(got)[len(got) // 2] if got else None),
            "impressions": sum(p["impressions"] for p in elig),
            "human_impressions": sum(p["human_impressions"] for p in elig),
            "human_impressions_upper": sum(p["human_impressions_upper"] for p in elig),
            "withheld_impressions": sum(p["withheld_impressions"] for p in elig),
            "clicks": sum(p["clicks"] for p in elig),
            "excluded_pre_existing": sum(1 for p in pages if p["kind"] == kind
                                         and p["basis"] == "pre-existing"),
            "excluded_recovered": sum(1 for p in pages if p["kind"] == kind
                                      and p["recovered_url"]),
        }
    # The like-for-like comparison above will be unanswerable for weeks. Meanwhile some
    # pages already have months of history, and excluding them throws away the only
    # evidence about tools that exists today - /linter/ has been live since March.
    aged = {}
    for kind in ("tool", "article"):
        rows = [p for p in pages if p["kind"] == kind
                and p["observable_days"] >= AGED_DAYS and not p["recovered_url"]]
        got = [p["days_to_first_impression"] for p in rows
               if p["days_to_first_impression"] is not None]
        impressions = sorted(p["impressions"] for p in rows)
        aged[kind] = {
            "pages": len(rows),
            "reached_impression": len(got),
            "median_days_to_first": sorted(got)[len(got) // 2] if got else None,
            "median_impressions": impressions[len(impressions) // 2] if impressions else None,
            "total_impressions": sum(impressions),
            "total_human_impressions": sum(p["human_impressions"] for p in rows),
            "total_human_impressions_upper": sum(
                p["human_impressions_upper"] for p in rows
            ),
            "withheld_impressions": sum(p["withheld_impressions"] for p in rows),
            "with_any_human_impression": sum(1 for p in rows if p["human_impressions"] > 0),
            "examples": [{"title": p["title"], "days": p["observable_days"],
                          "first": p["days_to_first_impression"],
                          "impressions": p["impressions"],
                          "human": p["human_impressions"],
                          "human_upper": p["human_impressions_upper"],
                          "withheld": p["withheld_impressions"]}
                         for p in sorted(rows, key=lambda x: -x["impressions"])[:4]],
        }
    page_impressions = sum(p["impressions"] for p in pages)
    named_query_impressions = sum(p["named_query_impressions"] for p in pages)
    human_floor = sum(p["human_impressions"] for p in pages)
    withheld = sum(p["withheld_impressions"] for p in pages)
    coverage = {
        "page_impressions": page_impressions,
        "named_query_impressions": named_query_impressions,
        "pct": (round(100 * named_query_impressions / page_impressions, 1)
                if page_impressions else None),
        "human_floor": human_floor,
        "human_upper": human_floor + withheld,
        "withheld_impressions": withheld,
    }
    return {"generated": today.isoformat(), "latest_data": latest.isoformat(),
            "track_from": track_from.isoformat(), "pages": pages,
            "comparison": comparison, "aged": aged, "aged_days": AGED_DAYS,
            "coverage": coverage}


def render(d: dict) -> str:
    L = [f"\n## {d['generated']} — attribution since {d['track_from']}\n"]
    L.append(f"Search Console data through {d['latest_data']} "
             f"({gr.GSC_LAG_DAYS}-day lag). Days are counted from each page's own ship "
             f"date, or from its last substantial rewrite where there was one.\n")
    L.append("`no data yet` means the page is younger than the lag, so silence proves "
             "nothing. `not yet, Nd` means N observable days with no impression, which "
             "**is** a measurement. Neither is written as a zero, because a zero would "
             "read as \"it happened immediately\".\n")

    if not d["pages"]:
        L.append("Nothing tracked in this window.")
        return "\n".join(L) + "\n"

    cov = d["coverage"]
    pct = f" ({cov['pct']}%)" if cov["pct"] is not None else ""
    L.append(
        f"Across tracked pages, named-query rows expose "
        f"**{cov['named_query_impressions']} of {cov['page_impressions']} impressions"
        f"{pct}**; **{cov['withheld_impressions']} are withheld**. The visible named-human "
        f"count is a floor of {cov['human_floor']}; its defensible interval is "
        f"**{cov['human_floor']}–{cov['human_upper']}**, where the ceiling assumes every "
        f"withheld impression was human. That ceiling is an error bound, not an estimate.\n"
    )

    def table(rows, heading, note=None):
        L.append(f"\n### {heading}\n")
        if note:
            L.append(note + "\n")
        if not rows:
            L.append("None.")
            return
        L.append("| Page | Cluster | Shipped | Obs. days | 1st impr | "
                 "1st named-human impr | 1st named-human click | Impr | "
                 "Named-human floor | Withheld | Human interval |")
        L.append("|---|---|---|---:|---|---|---|---:|---:|---:|---:|")
        for p in rows:
            obs = p["observable_days"]
            cluster = gr.CLUSTER_BY_SLUG.get(p["cluster"] or "", "—")
            first = ("pre-dates ship" if p["recovered_url"]
                     else describe(p["days_to_first_impression"], obs))
            L.append(
                f"| {p['title'][:44]} | {cluster} | {p['shipped']}"
                f"{' *(rewritten)*' if p['rewritten'] else ''} | "
                f"{obs if obs >= 0 else '—'} | {first} | "
                f"{describe(p['days_to_first_human_impression'], obs)} | "
                f"{describe(p['days_to_first_human_click'], obs)} | "
                f"{p['impressions']} | {p['human_impressions']} | "
                f"{p['withheld_impressions']} | "
                f"{p['human_impressions']}–{p['human_impressions_upper']} |")

    table([p for p in d["pages"] if p["kind"] == "tool"], "Tools",
          "Every tool, whatever its age, because the calendar weighting rests on them.")
    table([p for p in d["pages"] if p["kind"] == "article" and p["basis"] == "new"],
          "Articles shipped since tracking began",
          "These are the like-for-like comparison against the tools.")

    # The voice sweep rewrote sixty long-lived articles in one commit. Listing them all
    # buries the twelve rows that matter, so they are summarised and the biggest shown.
    pre = [p for p in d["pages"] if p["kind"] == "article" and p["basis"] == "pre-existing"]
    if pre:
        rewritten = [p for p in pre if p["rewritten"]]
        recovered = [p for p in pre if p["recovered_url"]]
        L.append(f"\n### Pre-existing articles, rewritten but not newly shipped\n")
        L.append(f"{len(pre)} article(s) shipped before {d['track_from']} and are excluded "
                 f"from the comparison: {len(rewritten)} were substantially rewritten in "
                 f"this window and {len(recovered)} carry impressions predating their "
                 f"current source file, because the AI cluster was recovered from 404 and "
                 f"its URLs ranked long before the files were restored. Days-to-first-"
                 f"impression is meaningless for both. The ten largest by impressions:\n")
        L.append("| Page | Cluster | Impr | Named-human floor | Withheld | "
                 "Human interval | 1st impr vs ship |")
        L.append("|---|---|---:|---:|---:|---:|---|")
        for p in sorted(pre, key=lambda x: -x["impressions"])[:10]:
            cluster = gr.CLUSTER_BY_SLUG.get(p["cluster"] or "", "—")
            note = "pre-dates ship" if p["recovered_url"] else (
                f"{p['days_to_first_impression']}d"
                if p["days_to_first_impression"] is not None else "no impression")
            L.append(f"| {p['title'][:44]} | {cluster} | {p['impressions']} | "
                     f"{p['human_impressions']} | {p['withheld_impressions']} | "
                     f"{p['human_impressions']}–{p['human_impressions_upper']} | "
                     f"{note} |")

    ag, agd = d["aged"], d["aged_days"]
    L.append(f"\n### What the pages with real age already show\n")
    L.append(f"Only pages observable for {agd}+ days. The like-for-like comparison below "
             f"will stay unanswerable for weeks, but this evidence exists now and it is "
             f"the only evidence about tools there is.\n")
    L.append("| | Pages | Reached an impression | Median days to first | "
             "Median impr | Total impr | Named-human interval | "
             "Pages with a named-human impr |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for kind, label in (("tool", "Tools"), ("article", "Articles")):
        k = ag[kind]
        L.append(f"| {label} | {k['pages']} | {k['reached_impression']} | "
                 f"{k['median_days_to_first'] if k['median_days_to_first'] is not None else 'n/a'} | "
                 f"{k['median_impressions'] if k['median_impressions'] is not None else 'n/a'} | "
                 f"{k['total_impressions']} | {k['total_human_impressions']}–"
                 f"{k['total_human_impressions_upper']} | "
                 f"{k['with_any_human_impression']} |")
    if ag["tool"]["examples"]:
        L.append("\nAged tools individually:\n")
        for e in ag["tool"]["examples"]:
            first = f"{e['first']}d to first impression" if e["first"] is not None else "no impression yet"
            L.append(f"- `{e['title']}` — {e['days']}d live, {first}, "
                     f"{e['impressions']} impressions, named-human interval "
                     f"{e['human']}–{e['human_upper']} ({e['withheld']} withheld)")
    L.append(f"\n{d['aged_verdict']}\n")

    c = d["comparison"]
    L.append("\n### The bet: do tools reach search sooner than articles?\n")
    L.append("Newly shipped pages only. A pre-existing page carries history that says "
             "nothing about how fast a new publish reaches search, and a recovered URL "
             "carries impressions older than its own source file.\n")
    L.append("| | Tracked | Eligible | Observable | Reached an impression | Median days | "
             "Impressions | Named-human interval | Clicks |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for kind, label in (("tool", "Tools"), ("article", "Articles")):
        k = c[kind]
        L.append(f"| {label} | {k['tracked']} | {k['eligible']} | {k['observable']} | "
                 f"{k['reached_impression']} | "
                 f"{k['median_days'] if k['median_days'] is not None else 'n/a'} | "
                 f"{k['impressions']} | {k['human_impressions']}–"
                 f"{k['human_impressions_upper']} | {k['clicks']} |")
    excl = ", ".join(
        f"{label} {c[kind]['excluded_pre_existing']} pre-existing / "
        f"{c[kind]['excluded_recovered']} recovered"
        for kind, label in (("tool", "tools"), ("article", "articles")))
    L.append(f"\nExcluded from the comparison: {excl}.")

    L.append(f"\n{d['verdict']}\n")
    L.append("**What this cannot test.** The original tools bet rested on keyword research "
             "claiming no build-a-tool keyword carried an AI Overview; live SERP reads "
             "later falsified that premise and tool building stopped at five. **Search "
             "Console has no AI Overview dimension**, so this instrument cannot reproduce "
             "either external SERP claim. "
             "The measurable consequence is impression-to-click conversion at comparable "
             "positions, which needs named human clicks; the visible floor is empty. "
             "Withheld queries prevent that floor from proving no human demand.")
    return "\n".join(L) + "\n"


def verdict(d: dict) -> str:
    c = d["comparison"]
    if not c:
        return "No pages tracked yet, so there is nothing to compare."
    t, a = c["tool"], c["article"]
    if t["observable"] == 0 and a["observable"] == 0:
        return ("**Not answerable yet.** Nothing tracked has been observable for even one "
                "day, so neither side has had a chance to earn an impression.")
    if t["reached_impression"] == 0 and a["reached_impression"] == 0:
        withheld = t.get("withheld_impressions", 0) + a.get("withheld_impressions", 0)
        return (f"**Not answerable yet, and that is now a measurement rather than a wait.** "
                f"{t['observable']} tool(s) and {a['observable']} article(s) have been "
                f"observable and neither side has earned a page-level impression. No lever is "
                f"working yet; the question of which works better cannot be opened until "
                f"one of them does. Across these eligible pages, {withheld} impressions are "
                f"withheld from named-query rows; that bound matters once page impressions "
                f"exist, but it cannot turn page-level silence into demand.")
    if t["median_days"] is None and a["median_days"] is not None:
        return (f"**Articles are ahead, on a sample too small to conclude from.** "
                f"{a['reached_impression']} of {a['observable']} observable new articles "
                f"reached an impression, median {a['median_days']}d, against none of "
                f"{t['observable']} observable tools. That is evidence the tools bet has "
                f"not paid yet, not evidence it is wrong: most of the {t['tracked']} tools "
                f"shipped within days of this report and cannot have earned anything.")
    if a["median_days"] is None and t["median_days"] is not None:
        return (f"**Tools are ahead.** {t['reached_impression']} of {t['observable']} "
                f"observable tools reached an impression, median {t['median_days']}d, "
                f"against none of {a['observable']} new articles. On {t['eligible']} "
                f"eligible tools this is directional only.")
    faster = "Tools" if t["median_days"] < a["median_days"] else "Articles"
    return (f"**{faster} reach search sooner.** Tools median "
            f"{t['median_days']}d over {t['reached_impression']} page(s); articles median "
            f"{a['median_days']}d over {a['reached_impression']}. With samples this size "
            f"({t['tracked']} tools, {a['tracked']} articles) this is directional and not "
            f"a trend — do not reweight sixty calendar rows on it.")


def aged_verdict(d: dict) -> str:
    """What the pages with real age say about the tools bet, today."""
    t, a = d["aged"]["tool"], d["aged"]["article"]
    agd = d["aged_days"]
    if t["pages"] == 0:
        return (f"**No tool has been live {agd} days, so there is no aged evidence about "
                f"tools yet.** {a['pages']} article(s) qualify. Nothing here supports or "
                f"undermines the bet.")
    if a["pages"] == 0:
        return (f"**{t['pages']} tool(s) have {agd}+ days of history but no article does, "
                f"so there is nothing to compare them against.**")

    verdict = [f"**The aged evidence does not support the tools bet, and it is the only "
               f"evidence there is.**"]
    if t["median_days_to_first"] is not None and a["median_days_to_first"] is not None:
        gap = t["median_days_to_first"] - a["median_days_to_first"]
        # A few days apart on a handful of pages is not a difference. Calling it one is how
        # a 2-day gap on a sample of one becomes "tools are faster".
        if abs(gap) <= INDISTINGUISHABLE_DAYS or t["pages"] < 3:
            relation = (f"indistinguishable from articles — median "
                        f"{t['median_days_to_first']}d against "
                        f"{a['median_days_to_first']}d, which on {t['pages']} tool(s) is "
                        f"not a difference")
        else:
            relation = (f"{'slower than' if gap > 0 else 'faster than'} articles — median "
                        f"{t['median_days_to_first']}d against "
                        f"{a['median_days_to_first']}d")
        verdict.append(f"Time to a first impression is {relation}.")
    t_upper = t.get("total_human_impressions_upper", t["total_human_impressions"])
    a_upper = a.get("total_human_impressions_upper", a["total_human_impressions"])
    verdict.append(
        f"On page-level volume the gap is not close: {t['pages']} aged tool(s) hold "
        f"{t['total_impressions']} impressions, against {a['total_impressions']} across "
        f"{a['pages']} aged article(s). Named-human impressions are floors, not totals: "
        f"tools {t['total_human_impressions']}–{t_upper}, articles "
        f"{a['total_human_impressions']}–{a_upper}, where each ceiling assigns every "
        f"withheld impression to a human. {t['with_any_human_impression']} of the tools "
        f"expose a named-human impression, against {a['with_any_human_impression']} of the "
        f"articles; withheld queries prevent this from proving the remainder had no human "
        f"demand.")
    verdict.append(
        f"Two caveats that matter before anyone reweights the calendar. The sample is "
        f"{t['pages']} tool(s), which is not a basis for a decision on sixty rows. And the "
        f"aged tool is `/linter/`, a documentation linter that predates the AI-search "
        f"cluster — the four tools the bet actually rests on are days old. This is a "
        f"reason to wait for those four rather than a reason to abandon the bet, and it is "
        f"equally not a reason to add more tool rows before they report.")
    return " ".join(verdict)


def upsert_dated_report(existing: str, report: str, generated: str) -> str:
    """Keep exactly one authoritative attribution observation per generated date.

    The daily job, a manual verification, and a retry can all run on the same day. Those
    pulls are revisions of one lagged observation, not independent samples. Replace the
    first same-day section and remove any later duplicates while preserving every other
    date and all nested headings.
    """
    matches = list(DATED_SECTION.finditer(existing))
    targets = [
        (match.start(), matches[index + 1].start()
         if index + 1 < len(matches) else len(existing))
        for index, match in enumerate(matches)
        if match.group("date") == generated
    ]
    clean_report = report.strip() + "\n"
    if not targets:
        return existing.rstrip() + "\n\n" + clean_report

    updated = existing
    first_start = targets[0][0]
    for start, end in reversed(targets):
        updated = updated[:start] + (clean_report if start == first_start else "") + updated[end:]
    return updated.rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    ap.add_argument("--track-from", default=TRACK_FROM.isoformat())
    ap.add_argument("--credential")
    args = ap.parse_args()

    svc = gr.search_console(args.credential)
    if svc is None:
        print("Search Console UNAVAILABLE (missing credential or google-api-python-client). "
              "Nothing written — an attribution table of zeros would read as failure to earn.")
        return 2

    data = build(svc, dt.date.fromisoformat(args.track_from), dt.date.today())
    data["verdict"] = verdict(data)
    data["aged_verdict"] = (aged_verdict(data) if data.get("aged")
                             else "No pages tracked yet, so there is no aged comparison.")
    report = render(data)
    print(report)

    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(data, indent=1, default=str),
                                          encoding="utf-8")
    if args.dry_run:
        return 0

    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text(
            "# Attribution\n\n"
            "Maintained by `tools/gsc_attribution.py`, one authoritative section per day. "
            "Every page shipped or substantially\n"
            "rewritten recently, and every tool, measured from its own publish date rather\n"
            "than sitewide — which is the only way to see which lever works while the\n"
            "sitewide numbers are zero.\n\n"
            "`no data yet` means younger than the Search Console lag. `not yet, Nd` means N\n"
            "observable days and still nothing, which is a real measurement. Neither is\n"
            "written as a zero. Named-human figures are floors. Every dated section gives\n"
            "their exact query-coverage denominator and a floor-to-ceiling interval for\n"
            "withheld impressions; the ceiling is an error bound, not an estimate.\n",
            encoding="utf-8")
    LOG.write_text(
        upsert_dated_report(LOG.read_text(encoding="utf-8"), report,
                            data["generated"]),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
