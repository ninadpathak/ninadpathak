#!/usr/bin/env python3
"""Point-in-time position for a page, including a page that has not moved.

Every other Search Console tool here is differential: what moved, what decayed, what is
close, what changed since publish. A page holding a steady position appears in none of
them, and absence from a movement report was read as absence of a position. That inference
sent a merge in the wrong direction, and this tool exists so it cannot be made again.

    tools/gsc_page_position.py                          # every published page
    tools/gsc_page_position.py --page ai-memory-management-for-llms
    tools/gsc_page_position.py --window 90 --json out.json

FOUR STATES, NEVER COLLAPSED
----------------------------
Collapsing these is the failure this tool was built to prevent:

    measured          human queries are named, so a position exists and is reported with
                      the query count it is averaged over
    no-human-queries  the page has impressions, and every query behind them is brand,
                      machine fan-out, or on an injected spam page. It ranks for something,
                      but not for a person
    withheld          the page has impressions, and Search Console names none of the
                      queries behind them. A position exists and cannot be seen
    never-impressed   the page has no impressions at all in the window. Only this state
                      means "no position"

`withheld` and `never-impressed` look identical in any query-level report and mean opposite
things. Distinguishing them is the whole point.

TWO THINGS THIS TOOL REFUSES TO DO
----------------------------------
**It will not print an average position without the query count behind it.** A page's
average position moves whenever its query mix moves, with no ranking change at all, so a
bare position is not a fact about ranking. `position_cell` enforces that structurally: no
query count, no number.

**It will not report zeros when its inputs are missing.** Following the
tools/audit_clusters.py precedent, a missing credential, missing content directory or
missing build exits non-zero with a reason. A page reported at "no impressions" because
nothing was fetched is worse than no report.

Every count derived from the query dimension is a FLOOR and is labelled in the output, not
in a comment: Search Console withholds low-volume queries, so a page can rank for more
queries than are named here.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import pathlib
import re
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gsc_report as gr  # noqa: E402
import gsc_collapse_forensics as fx  # noqa: E402
import report_log as rl  # noqa: E402

LOG = gr.ROOT / "planning" / "page-position.md"
WINDOW_DAYS = 90
POSTS_DIR = gr.ROOT / "content" / "posts"
SITEMAP = gr.ROOT / "output" / "sitemap.xml"
# States, in the order they are decided.
MEASURED, NO_HUMAN, WITHHELD, NEVER = (
    "measured", "no-human-queries", "withheld", "never-impressed")


def position_cell(position: float | None, query_count: int) -> str:
    """A position is only printable with the query count it is averaged over.

    The confound this guards against has produced three false readings on this campaign:
    an average "improving" 23.1 to 7.2 was a vanishing tail, 37.0 to 66.3 in a week was two
    disjoint query sets, and a page absent from a movement table was read as unranked.
    """
    if position is None or query_count < 1:
        return "—"
    return f"{position:.1f} (n={query_count})"


def published_posts() -> dict[str, dict]:
    import frontmatter

    out = {}
    for path in sorted(POSTS_DIR.glob("*.md")):
        fm = frontmatter.load(path)
        if fm.get("status") != "published":
            continue
        slug = str(fm.get("slug") or path.stem)
        out[slug] = {"cluster": fm.get("category"),
                     "title": str(fm.get("title", slug))[:70]}
    return out


def live_paths() -> set[str]:
    return {urlsplit(m).path
            for m in re.findall(r"<loc>([^<]+)</loc>", SITEMAP.read_text())}


def collect(svc, start: str, end: str) -> tuple[dict, dict, dict]:
    """Page-dimension totals, and human page+query rows, plus what the spam filter dropped."""
    page_rows = gr.fetch(svc, start, end, "page")
    by_page = {}
    for r in page_rows:
        by_page[r["keys"][0]] = {"impressions": r["impressions"], "clicks": r["clicks"],
                                 "position": r["position"]}

    body = {"startDate": start, "endDate": end, "dimensions": ["page", "query"],
            "rowLimit": 25000}
    pq = svc.searchanalytics().query(siteUrl=gr.SITE, body=body).execute().get("rows", [])
    named_pages = {r["keys"][0] for r in pq}

    as_query = [{"keys": [r["keys"][1]], "clicks": r["clicks"],
                 "impressions": r["impressions"], "position": r["position"],
                 "page": r["keys"][0]} for r in pq]
    parts = gr.partition_queries(as_query)
    human = [r for r in parts["human"] if not fx.is_foreign(r["page"])]

    per_page = collections.defaultdict(list)
    for r in human:
        per_page[r["page"]].append(r)

    excluded = {
        "spam_rows": sum(1 for r in parts["human"] if fx.is_foreign(r["page"])),
        "brand_rows": len(parts["brand"]), "machine_rows": len(parts["machine"]),
        "named_page_count": len(named_pages),
        "pq_impressions": int(sum(r["impressions"] for r in pq)),
        "page_impressions": int(sum(v["impressions"] for v in by_page.values())),
    }
    return by_page, dict(per_page), {"named_pages": named_pages, **excluded}


def classify(slug: str, by_page: dict, human_by_page: dict, meta: dict) -> dict:
    """One page's state, position and query mix. See the four states in the docstring."""
    urls = [f"https://ninadpathak.com{prefix}{slug}/" for prefix in gr.POST_PATH_PREFIXES]

    impressions = clicks = 0.0
    for u in urls:
        if u in by_page:
            impressions += by_page[u]["impressions"]
            clicks += by_page[u]["clicks"]

    rows = [r for u in urls for r in human_by_page.get(u, [])]
    named_anywhere = any(u in meta["named_pages"] for u in urls)

    if rows:
        himpr = sum(r["impressions"] for r in rows)
        position = (sum(r["position"] * r["impressions"] for r in rows) / himpr
                    if himpr else None)
        queries = sorted(({"query": r["keys"][0], "impressions": int(r["impressions"]),
                           "clicks": int(r["clicks"]), "position": round(r["position"], 1)}
                          for r in rows), key=lambda q: -q["impressions"])
        state = MEASURED
    else:
        himpr, position, queries = 0, None, []
        if impressions <= 0:
            state = NEVER
        elif named_anywhere:
            state = NO_HUMAN
        else:
            state = WITHHELD

    return {
        "slug": slug, "state": state,
        "impressions": int(impressions), "clicks": int(clicks),
        "human_impressions": int(himpr),
        "human_clicks": int(sum(r["clicks"] for r in rows)),
        "position": round(position, 1) if position is not None else None,
        "query_count": len(queries), "queries": queries,
    }


def render(d: dict) -> str:
    L = [f"\n## {d['generated']} — page position, point in time\n"]
    L.append(f"Window {d['window'][0]} to {d['window'][1]} ({d['window_days']}d), ending "
             f"{gr.GSC_LAG_DAYS} days back because Search Console lags. Human queries only: "
             f"brand, machine fan-out and injected spam pages excluded.\n")
    L.append(f"**Query counts and human impressions are FLOORS, not counts.** Search Console "
             f"withholds low-volume queries — the page+query pull sees "
             f"{d['coverage']['pq_impressions']} of "
             f"{d['coverage']['page_impressions']} page-dimension impressions "
             f"({d['coverage']['pct']}%), so a page ranks for more queries than are named "
             f"here. Sitewide impressions and clicks come from the page dimension and are "
             f"complete.\n")
    L.append("| State | Meaning |")
    L.append("|---|---|")
    L.append(f"| `{MEASURED}` | human queries named; position reported with its query count |")
    L.append(f"| `{NO_HUMAN}` | has impressions, but every named query is brand, machine or spam |")
    L.append(f"| `{WITHHELD}` | has impressions; Search Console names none of the queries. "
             f"**A position exists and cannot be seen** |")
    L.append(f"| `{NEVER}` | no impressions at all. **The only state that means no position** |")

    counts = collections.Counter(p["state"] for p in d["pages"])
    L.append(f"\n{len(d['pages'])} published pages: "
             + ", ".join(f"**{counts[s]}** `{s}`" for s in
                         (MEASURED, NO_HUMAN, WITHHELD, NEVER)) + ".\n")

    L.append("### Pages with a measured human position\n")
    L.append("| Page | Cluster | Position (queries) | Human impr | Impr | Clicks | Top query |")
    L.append("|---|---|---|---:|---:|---:|---|")
    measured = [p for p in d["pages"] if p["state"] == MEASURED]
    for p in sorted(measured, key=lambda x: (x["position"] or 999)):
        top = p["queries"][0]["query"][:34] if p["queries"] else "—"
        L.append(f"| {p['slug'][:40]} | {p['cluster']} | "
                 f"{position_cell(p['position'], p['query_count'])} | "
                 f"{p['human_impressions']} | {p['impressions']} | {p['clicks']} | {top} |")
    if not measured:
        L.append("| — | — | — | — | — | — | — |")

    for state, heading, note in (
            (WITHHELD, "Has impressions, queries withheld — position exists, unseen",
             "These are the pages the old inference got wrong. They rank for something; "
             "Search Console simply will not say what."),
            (NO_HUMAN, "Has impressions, but no human query behind them",
             "Ranking for brand, machine fan-out or an injected page is not ranking for a "
             "reader."),
            (NEVER, "No impressions in the window — the only 'no position' state", "")):
        rows = [p for p in d["pages"] if p["state"] == state]
        L.append(f"\n### {heading} — {len(rows)}\n")
        if note:
            L.append(note + "\n")
        if rows:
            L.append("| Page | Cluster | Impr | Clicks |")
            L.append("|---|---|---:|---:|")
            for p in sorted(rows, key=lambda x: -x["impressions"]):
                L.append(f"| {p['slug'][:44]} | {p['cluster']} | {p['impressions']} | "
                         f"{p['clicks']} |")
        else:
            L.append("None.")

    if d.get("focus"):
        L.append(f"\n### Requested pages in detail\n")
        for p in d["focus"]:
            L.append(f"\n**`{p['slug']}`** — state `{p['state']}`, position "
                     f"{position_cell(p['position'], p['query_count'])}, "
                     f"{p['human_impressions']} human impressions of {p['impressions']} "
                     f"total, {p['clicks']} clicks.\n")
            if p["queries"]:
                L.append("| Query | Impr | Clicks | Position |")
                L.append("|---|---:|---:|---:|")
                for q in p["queries"][:12]:
                    L.append(f"| {q['query'][:46]} | {q['impressions']} | {q['clicks']} | "
                             f"{q['position']} |")
                L.append(f"\nThe position above is averaged over these "
                         f"{p['query_count']} named queries and no others.")
            else:
                L.append("No named human queries, so no position can be attributed. That is "
                         "not the same as having no position.")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--page", action="append", default=[],
                    help="slug to report in detail; repeatable")
    ap.add_argument("--window", type=int, default=WINDOW_DAYS)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    ap.add_argument("--credential")
    args = ap.parse_args()

    # Refuse rather than report zeros. audit_clusters.py precedent.
    if not POSTS_DIR.exists():
        print(f"REFUSING: {POSTS_DIR} does not exist. Run from the repo root.")
        return 2
    if not SITEMAP.exists():
        print(f"REFUSING: {SITEMAP} does not exist. Run `python build.py` first — without a "
              f"build there is no live-page list, and every page would read as absent.")
        return 2
    svc = gr.search_console(args.credential)
    if svc is None:
        print("REFUSING: Search Console unavailable (missing credential or "
              "google-api-python-client). Reporting 'no impressions' for every page when "
              "nothing was fetched would be worse than reporting nothing.")
        return 2
    posts = published_posts()
    if not posts:
        print("REFUSING: no published posts found.")
        return 2

    end = dt.date.today() - dt.timedelta(days=gr.GSC_LAG_DAYS)
    start = end - dt.timedelta(days=args.window - 1)
    by_page, human_by_page, meta = collect(svc, start.isoformat(), end.isoformat())

    pages = [classify(slug, by_page, human_by_page, meta) for slug in posts]
    for p in pages:
        p["cluster"] = posts[p["slug"]]["cluster"]
        p["title"] = posts[p["slug"]]["title"]

    unknown = [s for s in args.page if s not in posts]
    if unknown:
        print(f"REFUSING: unknown slug(s) {unknown}. Not reporting a page that does not "
              f"exist as though it had no position.")
        return 2

    data = {
        "generated": dt.date.today().isoformat(),
        "window": (start.isoformat(), end.isoformat()), "window_days": args.window,
        "pages": pages,
        "focus": [p for p in pages if p["slug"] in args.page],
        "coverage": {
            "pq_impressions": meta["pq_impressions"],
            "page_impressions": meta["page_impressions"],
            "pct": (round(100 * meta["pq_impressions"] / meta["page_impressions"], 1)
                    if meta["page_impressions"] else None),
        },
        "excluded": {k: meta[k] for k in ("spam_rows", "brand_rows", "machine_rows")},
    }
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
            "# Page position, point in time\n\n"
            "Maintained by `tools/gsc_page_position.py`, one authoritative section per date. "
            "Every other Search Console tool here is\n"
            "differential, so a page holding a steady position is invisible to all of them —\n"
            "and absence from a movement report was once read as absence of a position, which\n"
            "sent a merge in the wrong direction.\n\n"
            "Four states, never collapsed: `measured`, `no-human-queries`, `withheld`\n"
            "(has impressions, queries not named — a position exists and cannot be seen), and\n"
            "`never-impressed`, which is the only one meaning no position. A position is never\n"
            "printed without the query count it is averaged over.\n",
            encoding="utf-8")
    LOG.write_text(
        rl.upsert_dated_report(LOG.read_text(encoding="utf-8"), report,
                               data["generated"]),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
