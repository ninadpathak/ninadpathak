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
The campaign is weighting tools over articles because no build-a-tool keyword in the
niche research carried an AI Overview while all 15 top keywords did. **That is a claim
about other people's SERPs, from Ahrefs, and this tool cannot verify it.** Search Console
has no AI Overview dimension - there is no first-party way to see whether an AI Overview
appeared above one of our results, and Ahrefs is unavailable. Anything claiming otherwise
would be invented.

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

    tools/gsc_attribution.py              # append to planning/attribution.md
    tools/gsc_attribution.py --dry-run
    tools/gsc_attribution.py --track-from 2026-08-01
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
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


def daily_by_page(svc, start: str, end: str) -> dict[str, dict[str, dict]]:
    """{url: {date: {clicks, impressions, position}}} — complete, page dimension."""
    body = {"startDate": start, "endDate": end, "dimensions": ["date", "page"],
            "rowLimit": 25000}
    rows = svc.searchanalytics().query(siteUrl=gr.SITE, body=body).execute().get("rows", [])
    out: dict[str, dict[str, dict]] = {}
    for r in rows:
        date, url = r["keys"]
        out.setdefault(url, {})[date] = {
            "clicks": r["clicks"], "impressions": r["impressions"],
            "position": r["position"]}
    return out


def daily_human_by_page(svc, start: str, end: str) -> dict[str, dict[str, dict]]:
    """Same shape, but only human queries. A hard floor: the three-dimension pull keeps
    about a fifth of sitewide impressions, so a page can genuinely earn human impressions
    that never appear here."""
    body = {"startDate": start, "endDate": end,
            "dimensions": ["date", "page", "query"], "rowLimit": 25000}
    rows = svc.searchanalytics().query(siteUrl=gr.SITE, body=body).execute().get("rows", [])
    as_query = [{"keys": [r["keys"][2]], "clicks": r["clicks"],
                 "impressions": r["impressions"], "position": r["position"],
                 "date": r["keys"][0], "page": r["keys"][1]} for r in rows]
    human = gr.partition_queries(as_query)["human"]
    out: dict[str, dict[str, dict]] = {}
    for r in human:
        b = out.setdefault(r["page"], {}).setdefault(r["date"], {
            "clicks": 0.0, "impressions": 0.0})
        b["clicks"] += r["clicks"]
        b["impressions"] += r["impressions"]
    return out


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
    human_daily = daily_human_by_page(svc, window_start.isoformat(), latest.isoformat())

    for p in pages:
        start = dt.date.fromisoformat(p["shipped"])
        observable = (latest - start).days
        # /blog/<slug>/ is the pre-migration path and still carries most traffic, so a
        # page's history lives under both prefixes. Merge them or every article looks new.
        series: dict[str, dict] = {}
        hseries: dict[str, dict] = {}
        for prefix in ("/articles/", "/blog/") if p["kind"] == "article" else ("",):
            url = (f"{BASE}{prefix}{p['slug']}/" if prefix else p["url"])
            for src, dst in ((all_daily.get(url, {}), series),
                             (human_daily.get(url, {}), hseries)):
                for date, v in src.items():
                    b = dst.setdefault(date, {"clicks": 0.0, "impressions": 0.0,
                                              "position": v.get("position", 0)})
                    b["clicks"] += v.get("clicks", 0)
                    b["impressions"] += v["impressions"]
        p["observable_days"] = observable
        p["impressions"] = int(sum(v["impressions"] for v in series.values()))
        p["clicks"] = int(sum(v["clicks"] for v in series.values()))
        p["human_impressions"] = int(sum(v["impressions"] for v in hseries.values()))
        p["human_clicks"] = int(sum(v["clicks"] for v in hseries.values()))
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
            "with_any_human_impression": sum(1 for p in rows if p["human_impressions"] > 0),
            "examples": [{"title": p["title"], "days": p["observable_days"],
                          "first": p["days_to_first_impression"],
                          "impressions": p["impressions"],
                          "human": p["human_impressions"]}
                         for p in sorted(rows, key=lambda x: -x["impressions"])[:4]],
        }
    return {"generated": today.isoformat(), "latest_data": latest.isoformat(),
            "track_from": track_from.isoformat(), "pages": pages,
            "comparison": comparison, "aged": aged, "aged_days": AGED_DAYS}


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

    def table(rows, heading, note=None):
        L.append(f"\n### {heading}\n")
        if note:
            L.append(note + "\n")
        if not rows:
            L.append("None.")
            return
        L.append("| Page | Cluster | Shipped | Obs. days | 1st impr | 1st human impr | "
                 "1st human click | Impr | Human impr |")
        L.append("|---|---|---|---:|---|---|---|---:|---:|")
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
                f"{p['impressions']} | {p['human_impressions']} |")

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
        L.append("| Page | Cluster | Impr | Human impr | 1st impr vs ship |")
        L.append("|---|---|---:|---:|---|")
        for p in sorted(pre, key=lambda x: -x["impressions"])[:10]:
            cluster = gr.CLUSTER_BY_SLUG.get(p["cluster"] or "", "—")
            note = "pre-dates ship" if p["recovered_url"] else (
                f"{p['days_to_first_impression']}d"
                if p["days_to_first_impression"] is not None else "no impression")
            L.append(f"| {p['title'][:44]} | {cluster} | {p['impressions']} | "
                     f"{p['human_impressions']} | {note} |")

    ag, agd = d["aged"], d["aged_days"]
    L.append(f"\n### What the pages with real age already show\n")
    L.append(f"Only pages observable for {agd}+ days. The like-for-like comparison below "
             f"will stay unanswerable for weeks, but this evidence exists now and it is "
             f"the only evidence about tools there is.\n")
    L.append("| | Pages | Reached an impression | Median days to first | "
             "Median impr | Total impr | Total human impr | Pages with any human impr |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for kind, label in (("tool", "Tools"), ("article", "Articles")):
        k = ag[kind]
        L.append(f"| {label} | {k['pages']} | {k['reached_impression']} | "
                 f"{k['median_days_to_first'] if k['median_days_to_first'] is not None else 'n/a'} | "
                 f"{k['median_impressions'] if k['median_impressions'] is not None else 'n/a'} | "
                 f"{k['total_impressions']} | {k['total_human_impressions']} | "
                 f"{k['with_any_human_impression']} |")
    if ag["tool"]["examples"]:
        L.append("\nAged tools individually:\n")
        for e in ag["tool"]["examples"]:
            first = f"{e['first']}d to first impression" if e["first"] is not None else "no impression yet"
            L.append(f"- `{e['title']}` — {e['days']}d live, {first}, "
                     f"{e['impressions']} impressions, {e['human']} human")
    L.append(f"\n{d['aged_verdict']}\n")

    c = d["comparison"]
    L.append("\n### The bet: do tools reach search sooner than articles?\n")
    L.append("Newly shipped pages only. A pre-existing page carries history that says "
             "nothing about how fast a new publish reaches search, and a recovered URL "
             "carries impressions older than its own source file.\n")
    L.append("| | Tracked | Eligible | Observable | Reached an impression | Median days | "
             "Impressions | Human impr | Clicks |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for kind, label in (("tool", "Tools"), ("article", "Articles")):
        k = c[kind]
        L.append(f"| {label} | {k['tracked']} | {k['eligible']} | {k['observable']} | "
                 f"{k['reached_impression']} | "
                 f"{k['median_days'] if k['median_days'] is not None else 'n/a'} | "
                 f"{k['impressions']} | {k['human_impressions']} | {k['clicks']} |")
    excl = ", ".join(
        f"{label} {c[kind]['excluded_pre_existing']} pre-existing / "
        f"{c[kind]['excluded_recovered']} recovered"
        for kind, label in (("tool", "tools"), ("article", "articles")))
    L.append(f"\nExcluded from the comparison: {excl}.")

    L.append(f"\n{d['verdict']}\n")
    L.append("**What this cannot test.** The tools bet rests on no build-a-tool keyword "
             "carrying an AI Overview while all 15 top niche keywords do. That is a claim "
             "about other people's SERPs, taken from Ahrefs. **Search Console has no AI "
             "Overview dimension**, so there is no first-party way to confirm an AI "
             "Overview appeared above one of our own results, and Ahrefs is unavailable. "
             "The measurable consequence is impression-to-click conversion at comparable "
             "positions, which needs clicks; the site has none, so that column is empty "
             "rather than filled with zeros.")
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
        return (f"**Not answerable yet, and that is now a measurement rather than a wait.** "
                f"{t['observable']} tool(s) and {a['observable']} article(s) have been "
                f"observable and neither side has earned a single impression. No lever is "
                f"working yet; the question of which works better cannot be opened until "
                f"one of them does.")
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
    verdict.append(
        f"On volume the gap is not close: {t['pages']} aged tool(s) hold "
        f"{t['total_impressions']} impressions and {t['total_human_impressions']} human, "
        f"against {a['total_impressions']} and {a['total_human_impressions']} across "
        f"{a['pages']} aged article(s). {t['with_any_human_impression']} of the tools have "
        f"earned a single human impression, against {a['with_any_human_impression']} of "
        f"the articles.")
    verdict.append(
        f"Two caveats that matter before anyone reweights the calendar. The sample is "
        f"{t['pages']} tool(s), which is not a basis for a decision on sixty rows. And the "
        f"aged tool is `/linter/`, a documentation linter that predates the AI-search "
        f"cluster — the four tools the bet actually rests on are days old. This is a "
        f"reason to wait for those four rather than a reason to abandon the bet, and it is "
        f"equally not a reason to add more tool rows before they report.")
    return " ".join(verdict)


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
    data["aged_verdict"] = aged_verdict(data)
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
            "Appended by `tools/gsc_attribution.py`. Every page shipped or substantially\n"
            "rewritten recently, and every tool, measured from its own publish date rather\n"
            "than sitewide — which is the only way to see which lever works while the\n"
            "sitewide numbers are zero.\n\n"
            "`no data yet` means younger than the Search Console lag. `not yet, Nd` means N\n"
            "observable days and still nothing, which is a real measurement. Neither is\n"
            "written as a zero. Human figures come from the three-dimension pull and are a\n"
            "hard floor: it keeps about a fifth of sitewide impressions.\n",
            encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
