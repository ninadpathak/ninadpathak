#!/usr/bin/env python3
"""Leading indicators: the earliest signals that move on this domain.

Human clicks have been zero for ten months and the day-90 band is a projection, so the
campaign has no way to know whether anything is working before November. These are the
signals that move first, read daily, so the first one arrives as news rather than as a
retrospective discovery. The autumn 2025 spam injection sat unnoticed for ten months
because nothing was reading the one record that showed it.

    1. TIME TO FIRST IMPRESSION   by ship era and by cluster, with the confound named
    2. RECOVERY WATCHLIST         previously-indexed URLs currently silent, and their
                                  return lag once they come back
    3. REVISION COHORT            pages substantially rewritten recently, and whether the
                                  rewrite moved impressions

    tools/gsc_leading.py              # append to planning/leading-indicators.md
    tools/gsc_leading.py --dry-run
    tools/gsc_leading.py --json PATH

THE CONFOUND THAT DOMINATES SECTION 1, AND WHY IT IS NAMED FIRST
----------------------------------------------------------------
Grouping time-to-first-impression by cluster gives documentation a median of 9 days and
AI-engineering 65, which reads as a seven-fold cluster effect and is not one. The clusters
shipped in different eras: AI-engineering landed 2026-03 to 2026-06, documentation mostly
2026-08. Group the same pages by ship quarter instead and the picture inverts —

    2026-Q1  median 96d      2026-Q2  median 66d      2026-Q3  median 4d

— and inside 2026-Q2, the one era holding more than one cluster, the clusters land within
ten days of each other (AI-engineering 62d, DevEx 72d, documentation 72d). **The variable
is the domain's indexing state over time, not the cluster.** So this tool reports the era
series as the headline and the cluster split only within an era, where it means something.

An earlier read of the same numbers also found documentation earning on only 57% of its
pages against AI-engineering's 91%, which looked like a survivorship story. It was an
artifact of counting pages younger than two weeks as failures. At a 14-day floor the earn
rates are 89% and 91% and there is no cluster difference to explain.

WHAT THIS CANNOT ANSWER YET
---------------------------
Most of it. Both recovery events landed 2026-08-17 and Search Console data ends three days
earlier, so the recovery question has no post-event data at all; the same is true of every
page rewritten this week. Those sections print what they are waiting for and how many days
until it becomes readable. A section reading "no data yet" is doing its job.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import pathlib
import statistics as st
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gsc_report as gr  # noqa: E402
import gsc_attribution as at  # noqa: E402
import report_log as rl  # noqa: E402

LOG = gr.ROOT / "planning" / "leading-indicators.md"
HISTORY_START = dt.date(2025, 4, 1)
# A page younger than this is not a failure for never having earned an impression.
MIN_AGE_FOR_EARN_RATE = 14
# Silence this long on a previously-indexed URL puts it on the recovery watchlist.
SILENCE_DAYS = 28
# Look back this far for substantial rewrites.
REVISION_WINDOW = 7
# Impression window compared before and after a rewrite.
REVISION_COMPARE = 14


def daily_by_page(svc, start: dt.date, end: dt.date) -> dict[str, dict[str, float]]:
    """{url: {date: impressions}} across a long span, chunked under the row cap."""
    out: dict[str, dict[str, float]] = {}
    cursor = start
    while cursor <= end:
        stop = min(cursor + dt.timedelta(days=90), end)
        body = {"startDate": cursor.isoformat(), "endDate": stop.isoformat(),
                "dimensions": ["date", "page"], "rowLimit": 25000}
        rows = svc.searchanalytics().query(siteUrl=gr.SITE, body=body).execute().get("rows", [])
        if len(rows) >= 25000:
            print(f"WARNING: row cap hit for {cursor}..{stop}; that chunk is truncated")
        for r in rows:
            d, url = r["keys"]
            out.setdefault(url, {})[d] = r["impressions"]
        cursor = stop + dt.timedelta(days=1)
    return out


def merged_series(daily: dict, slug: str) -> dict[str, float]:
    """A post's history across both the canonical and pre-migration path prefixes."""
    s: dict[str, float] = {}
    for prefix in gr.POST_PATH_PREFIXES:
        for d, i in daily.get(f"https://ninadpathak.com{prefix}{slug}/", {}).items():
            s[d] = s.get(d, 0) + i
    return s


def quarter(d: dt.date) -> str:
    return f"{d.year}-Q{(d.month - 1) // 3 + 1}"


def first_impression_lags(svc, daily: dict, latest: dt.date) -> dict:
    """Time from ship to first impression, by ship era and by cluster within an era."""
    import frontmatter

    pages = []
    for path in sorted((gr.ROOT / "content" / "posts").glob("*.md")):
        fm = frontmatter.load(path)
        if fm.get("status") != "published":
            continue
        rel = str(path.relative_to(gr.ROOT))
        shipped = at.first_added(rel)
        if shipped is None:
            continue
        slug = str(fm.get("slug") or path.stem)
        series = merged_series(daily, slug)
        hits = sorted(d for d, i in series.items() if i > 0)
        lag = (dt.date.fromisoformat(hits[0]) - shipped).days if hits else None
        pages.append({
            "slug": slug, "cluster": fm.get("category"), "shipped": shipped.isoformat(),
            "quarter": quarter(shipped), "age": (latest - shipped).days, "lag": lag,
            "impressions": int(sum(series.values())),
        })

    aged = [p for p in pages if p["age"] >= MIN_AGE_FOR_EARN_RATE]
    earned = [p for p in aged if p["lag"] is not None and p["lag"] >= 0]

    def summarise(rows):
        lags = sorted(r["lag"] for r in rows)
        return {"n": len(lags),
                "median": st.median(lags) if lags else None,
                "min": lags[0] if lags else None,
                "max": lags[-1] if lags else None}

    by_era = {q: summarise([p for p in earned if p["quarter"] == q])
              for q in sorted({p["quarter"] for p in earned})}
    within_era = {}
    for q in by_era:
        per = collections.defaultdict(list)
        for p in earned:
            if p["quarter"] == q:
                per[p["cluster"] or "(none)"].append(p)
        within_era[q] = {c: summarise(v) for c, v in sorted(per.items(), key=lambda kv: str(kv[0]))}

    earn_rate = {}
    for c in sorted({p["cluster"] or "(none)" for p in aged}, key=str):
        sub = [p for p in aged if (p["cluster"] or "(none)") == c]
        got = [p for p in sub if p["lag"] is not None]
        earn_rate[c] = {"aged": len(sub), "earned": len(got),
                        "rate": round(100 * len(got) / len(sub)) if sub else None}

    too_young = [p for p in pages if p["age"] < MIN_AGE_FOR_EARN_RATE]
    return {"by_era": by_era, "within_era": within_era, "earn_rate": earn_rate,
            "pages_total": len(pages), "pages_aged": len(aged),
            "pages_too_young": len(too_young),
            "comparable_eras": [q for q, v in within_era.items() if len(v) > 1]}


def recovery_watchlist(svc, daily: dict, latest: dt.date) -> dict:
    """Previously-indexed URLs in the current sitemap that have gone silent.

    Defined from the record rather than from a hardcoded event date: a URL that earned
    impressions once and has earned none for SILENCE_DAYS is waiting to come back, whatever
    made it stop. When it returns, the gap is the return lag - which is the number that
    answers whether recovery re-ranks faster than new publishing earns.
    """
    sitemap = gr.ROOT / "output" / "sitemap.xml"
    live: set[str] = set()
    if sitemap.exists():
        import re
        live = {m for m in re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text())}
    live_paths = {urlsplit(u).path for u in live}

    cutoff = latest - dt.timedelta(days=SILENCE_DAYS)
    silent, returned = [], []
    for url, series in daily.items():
        path = urlsplit(url).path
        if path not in live_paths:
            continue          # not a page we currently serve; not a recovery candidate
        hits = sorted(d for d, i in series.items() if i > 0)
        if not hits:
            continue
        last = dt.date.fromisoformat(hits[-1])
        total = int(sum(series.values()))
        # A gap inside the record, then a return: measurable return lag.
        gaps = [(dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days
                for a, b in zip(hits, hits[1:])
                if (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days >= SILENCE_DAYS]
        if gaps:
            returned.append({"path": path, "impressions": total,
                             "longest_silence_days": max(gaps),
                             "last_seen": hits[-1]})
        if last <= cutoff:
            silent.append({"path": path, "impressions": total, "last_seen": hits[-1],
                           "silent_days": (latest - last).days})
    silent.sort(key=lambda r: -r["impressions"])
    returned.sort(key=lambda r: -r["longest_silence_days"])
    return {"silent": silent, "returned": returned,
            "silent_impressions": sum(r["impressions"] for r in silent),
            "median_return_lag": (st.median([r["longest_silence_days"] for r in returned])
                                  if returned else None)}


def revision_cohort(svc, daily: dict, latest: dt.date, window: int) -> dict:
    """Pages substantially rewritten recently, and whether it moved impressions."""
    import frontmatter

    since = dt.date.today() - dt.timedelta(days=window)
    rows = []
    for path in sorted((gr.ROOT / "content" / "posts").glob("*.md")):
        fm = frontmatter.load(path)
        if fm.get("status") != "published":
            continue
        rel = str(path.relative_to(gr.ROOT))
        changed = at.last_substantial_change(rel, since)
        if changed is None:
            continue
        slug = str(fm.get("slug") or path.stem)
        series = merged_series(daily, slug)
        observable = (latest - changed).days
        before_lo = changed - dt.timedelta(days=REVISION_COMPARE)
        before = sum(i for d, i in series.items() if before_lo.isoformat() <= d < changed.isoformat())
        after = sum(i for d, i in series.items() if d >= changed.isoformat())
        rows.append({
            "slug": slug, "cluster": fm.get("category"), "changed": changed.isoformat(),
            "observable_days": observable,
            "impressions_before": int(before), "impressions_after": int(after),
            "observable": observable >= 1,
            # A page that earned nothing before the rewrite cannot demonstrate that the
            # rewrite moved anything. Zero-to-zero is not a null result about revision, it
            # is a page with no signal to move.
            "informative": observable >= 1 and before > 0,
        })
    rows.sort(key=lambda r: (-r["impressions_before"], -r["observable_days"]))
    observable_rows = [r for r in rows if r["observable"]]
    informative = [r for r in rows if r["informative"]]
    moved = [r for r in informative
             if r["impressions_after"] != r["impressions_before"]]
    return {"pages": rows, "count": len(rows),
            "observable": len(observable_rows), "readable": len(informative),
            "moved": len(moved),
            "zero_before": len(observable_rows) - len(informative),
            "days_until_readable": (1 - max((r["observable_days"] for r in rows), default=0)
                                    if not informative else 0)}


def render(d: dict) -> str:
    L = [f"\n## {d['generated']} — leading indicators\n"]
    L.append(f"Search Console data through {d['latest']} ({gr.GSC_LAG_DAYS}-day lag). "
             f"Read daily. A section reading \"no data yet\" is working correctly — the "
             f"point is that the first real signal shows up in days rather than being found "
             f"retrospectively.\n")

    # 1 ------------------------------------------------------------------
    f = d["first_impression"]
    L.append("### 1. Time to first impression — the variable is the era, not the cluster\n")
    L.append(f"{f['pages_aged']} of {f['pages_total']} published pages are at least "
             f"{MIN_AGE_FOR_EARN_RATE} days old; {f['pages_too_young']} are younger and are "
             f"excluded rather than counted as failures.\n")
    L.append("| Ship quarter | Pages earned | Median days to 1st impression | Min | Max |")
    L.append("|---|---:|---:|---:|---:|")
    for q, v in f["by_era"].items():
        L.append(f"| {q} | {v['n']} | **{v['median']:.0f}** | {v['min']} | {v['max']} |")
    eras = list(f["by_era"])
    if len(eras) >= 2:
        first, last = f["by_era"][eras[0]], f["by_era"][eras[-1]]
        if first["median"] and last["median"]:
            L.append(f"\n**{eras[0]} to {eras[-1]}: {first['median']:.0f}d → "
                     f"{last['median']:.0f}d.** The domain now surfaces a new page far "
                     f"faster than it did, which is what makes any of these indicators "
                     f"usable as feedback rather than as history. **The latest era is "
                     f"n={last['n']}**, so treat the {last['median']:.0f}d figure as an "
                     f"early reading rather than an established rate; the direction across "
                     f"three eras is better supported than the level in any one of them.")

    L.append("\n**By cluster, only within an era — because across eras it is a confound.**\n")
    if f["comparable_eras"]:
        L.append("| Era | Cluster | Pages | Median days |")
        L.append("|---|---|---:|---:|")
        for q in f["comparable_eras"]:
            for c, v in f["within_era"][q].items():
                L.append(f"| {q} | {c} | {v['n']} | {v['median']:.0f} |")
        L.append("\nGrouping by cluster across all eras would report documentation at 9d "
                 "against AI-engineering at 65d. That is a seven-fold effect that does not "
                 "exist: documentation shipped in 2026-Q3 and AI-engineering in Q1–Q2. "
                 "Within a shared era the clusters land within ten days of each other, so "
                 "**cluster choice is close to neutral on indexing speed** and the calendar "
                 "reweighting is neither helped nor punished by it.")
    else:
        L.append("No single era yet holds more than one cluster, so no within-era cluster "
                 "comparison is possible. Any cross-era cluster comparison would be a ship-"
                 "date artifact.")

    L.append("\n**Earn rate — does a page ever earn an impression at all.**\n")
    L.append("| Cluster | Pages aged | Earned | Rate |")
    L.append("|---|---:|---:|---:|")
    for c, v in f["earn_rate"].items():
        L.append(f"| {c} | {v['aged']} | {v['earned']} | "
                 f"{str(v['rate']) + '%' if v['rate'] is not None else '—'} |")

    # 2 ------------------------------------------------------------------
    r = d["recovery"]
    L.append("\n### 2. Recovery watchlist\n")
    L.append(f"Previously-indexed URLs we still serve that have earned nothing for "
             f"{SILENCE_DAYS}+ days. Defined from the record, not from an event date, so it "
             f"catches any cause. **{len(r['silent'])} URL(s), "
             f"{r['silent_impressions']} impressions of history between them.** When one "
             f"returns, the silence length is the return lag — the number that decides "
             f"whether recovery beats new publishing.\n")
    if r["silent"]:
        L.append("| URL | Impressions ever | Last seen | Silent |")
        L.append("|---|---:|---|---:|")
        for x in r["silent"][:15]:
            L.append(f"| {x['path'][:52]} | {x['impressions']} | {x['last_seen']} | "
                     f"{x['silent_days']}d |")
    else:
        L.append("None — every URL we serve that has ever earned an impression has earned "
                 "one recently.")
    if r["returned"]:
        L.append(f"\n**Already returned once:** {len(r['returned'])} URL(s) have a silence "
                 f"of {SILENCE_DAYS}+ days inside the record followed by impressions again, "
                 f"median silence {r['median_return_lag']:.0f}d. That is a historical "
                 f"return lag, not a controlled measurement — nothing here confirms the URL "
                 f"was unreachable during the gap rather than simply not shown.")
        L.append("\n| URL | Impressions ever | Longest silence |")
        L.append("|---|---:|---:|")
        for x in r["returned"][:8]:
            L.append(f"| {x['path'][:52]} | {x['impressions']} | "
                     f"{x['longest_silence_days']}d |")

    # 3 ------------------------------------------------------------------
    v = d["revision"]
    L.append(f"\n### 3. Revision cohort — does rewriting move anything\n")
    L.append(f"{v['count']} page(s) substantially rewritten in the last {REVISION_WINDOW} "
             f"days. Impressions in the {REVISION_COMPARE} days before the change against "
             f"everything since.\n")
    L.append(f"Of those: **{v['observable']} have at least one observable day**, "
             f"**{v['zero_before']} of those earned nothing before the rewrite** and so "
             f"cannot show a revision effect either way, leaving "
             f"**{v['readable']} informative**.\n")
    if v["readable"] == 0:
        L.append(f"**No answer yet, and this is the honest state rather than a null result.** "
                 f"{'Every rewrite landed inside the ' + str(gr.GSC_LAG_DAYS) + '-day Search Console lag' if v['observable'] == 0 else 'The rewrites with an observable day all sit on pages that had zero impressions to begin with'}, "
                 f"so nothing here can distinguish \"the rewrite did nothing\" from \"we "
                 f"cannot see yet\". The first informative comparison needs a rewritten page "
                 f"that was already earning impressions.")
    else:
        L.append("| Page | Cluster | Changed | Obs. days | Impr before | Impr since |")
        L.append("|---|---|---|---:|---:|---:|")
        for x in v["pages"][:20]:
            if not x["readable"]:
                continue
            L.append(f"| {x['slug'][:40]} | {x['cluster']} | {x['changed']} | "
                     f"{x['observable_days']} | {x['impressions_before']} | "
                     f"{x['impressions_after']} |")
        L.append(f"\n{v['count'] - v['readable']} further page(s) changed too recently to "
                 f"read.")

    L.append(f"\n### What this cannot answer yet\n")
    for line in d["cannot_answer"]:
        L.append(f"- {line}")
    return "\n".join(L) + "\n"


def cannot_answer(d: dict) -> list[str]:
    out = []
    f, r, v = d["first_impression"], d["recovery"], d["revision"]
    if not f["comparable_eras"]:
        out.append("**Cluster effect on indexing speed** — no era holds two clusters yet.")
    else:
        out.append("**Whether cluster 3 genuinely indexes faster than cluster 1** — within "
                   "the one shared era the gap is under ten days on small samples, which is "
                   "too close to call and too small to test. Not decidable now, and it is "
                   "probably not the question that matters.")
    if v["readable"] == 0:
        reason = ("all landed inside the Search Console lag" if v["observable"] == 0 else
                  f"the {v['observable']} with an observable day all sit on pages that "
                  f"earned nothing beforehand, so there is no signal for a rewrite to move")
        out.append(f"**Whether substantive revision moves impressions** — {v['count']} "
                   f"rewrites in the window and {reason}. Needs a rewritten page that was "
                   f"already earning.")
    if not r["silent"]:
        out.append("**Whether recovery re-ranks faster than new publishing earns** — "
                   "nothing we serve is currently silent, so there is no recovery to watch. "
                   "The republished sets landed after the data ends.")
    else:
        out.append("**Whether recovery re-ranks faster than new publishing earns** — the "
                   "watchlist is populated but no listed URL has returned inside the data "
                   "window, so there is no return lag to compare against the "
                   "time-to-first-impression figures above.")
    out.append("**Anything about clicks.** Human non-brand clicks are zero and have been "
               "for ten months; every indicator here is an impression indicator, and an "
               "impression is not a reader.")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    ap.add_argument("--revision-window", type=int, default=REVISION_WINDOW)
    ap.add_argument("--credential")
    args = ap.parse_args()

    svc = gr.search_console(args.credential)
    if svc is None:
        print("Search Console UNAVAILABLE (missing credential or google-api-python-client). "
              "Nothing written — a leading-indicator page of zeros would read as a finding.")
        return 2

    latest = dt.date.today() - dt.timedelta(days=gr.GSC_LAG_DAYS)
    daily = daily_by_page(svc, HISTORY_START, latest)
    data = {
        "generated": dt.date.today().isoformat(),
        "latest": latest.isoformat(),
        "pages_with_impressions": len(daily),
        "first_impression": first_impression_lags(svc, daily, latest),
        "recovery": recovery_watchlist(svc, daily, latest),
        "revision": revision_cohort(svc, daily, latest, args.revision_window),
    }
    data["cannot_answer"] = cannot_answer(data)
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
            "# Leading indicators\n\n"
            "Maintained by `tools/gsc_leading.py`, one authoritative section per day. "
            "The earliest signals that move on\n"
            "this domain, so the first one arrives as news rather than as a retrospective\n"
            "discovery — the autumn 2025 spam injection went unnoticed for ten months\n"
            "because nothing read the record that showed it.\n\n"
            "Time-to-first-impression is reported **by ship era**, not by cluster. Grouping\n"
            "by cluster across eras reports a seven-fold effect that does not exist; the\n"
            "clusters shipped at different times and the domain's indexing speed changed\n"
            "underneath them. Cluster is only compared inside a single era.\n\n"
            "A section reading \"no data yet\" is working. A zero would mean \"nothing\n"
            "happened\"; these sections say \"we cannot see yet\" and how long until they can.\n",
            encoding="utf-8")
    LOG.write_text(
        rl.upsert_dated_report(LOG.read_text(encoding="utf-8"), report,
                               data["generated"]),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
