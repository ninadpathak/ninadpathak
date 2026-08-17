#!/usr/bin/env python3
"""Weekly scoreboard: the five numbers the campaign is actually judged on.

Four measurement tools already exist and between them they can answer almost anything.
This one deliberately answers almost nothing. It reports the figures that change a
decision and leaves everything else to the other tools, because a scoreboard nobody can
read in a minute is a scoreboard nobody reads.

    1. Human non-brand clicks, this week against last week and against the day-90 band.
    2. Distance to 10,000/month, as a multiple, on human non-brand clicks and nothing else.
    3. What entered and what left the top 20 human queries.
    4. Human impressions per cluster, so a cluster earning nothing is visible.
    5. One sentence on whether the trajectory reaches the target, with the arithmetic.

    tools/gsc_scoreboard.py              # append a dated section to planning/scoreboard.md
    tools/gsc_scoreboard.py --dry-run    # print, write nothing
    tools/gsc_scoreboard.py --json PATH

HOW TO READ THE LABELS
----------------------
Every number here carries one of three labels and they are not interchangeable:

  MEASURED  a sitewide total straight from Search Console. Complete.
  FLOOR     derived from the query dimension, which withholds low-volume queries. The
            real figure is higher by an unknown amount. Never a total.
  ESTIMATE  bounded in neither direction. The human figures are estimates: they undercount
            because the withheld tail is excluded, and overcount because machine query
            fan-out is only detected within the window being measured.

"Human" means non-brand and non-machine. Brand queries are removed first, then pasted
blobs, then machine query fan-out - permutation families with a shared core, which on this
site reached 57% of named impressions in one month. The separator lives in gsc_report.py
and its limits are documented there.

Where a number cannot be computed honestly it says so. There are no placeholders and no
zeros standing in for missing data.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gsc_report as gr  # noqa: E402

LOG = gr.ROOT / "planning" / "scoreboard.md"

# campaign-90d.md, fourth-cycle refresh: the band was cut from 350-1,350 after a sweep
# found the keyword universe 12.6% contaminated. Both ends are monthly human clicks.
BAND_LOW, BAND_HIGH = 306, 1176
TARGET_MONTHLY = 10_000
DAY_90 = dt.date(2026, 11, 15)
WEEK = 7
TOP_N = 20
# A month for rate purposes. The trailing-28d window is what every other tool uses.
DAYS_IN_MONTH = 28
# tools/daily.sh calls this every day with --weekly; it only writes on this weekday, so a
# weekly scoreboard does not silently become a daily log.
WRITE_WEEKDAY = 0
WRITE_WEEKDAY_NAME = "Monday"


def week_windows(today: dt.date) -> dict[str, tuple[str, str]]:
    """This week, last week, and the trailing/prior 28 days, all ending the same lag back."""
    end = today - dt.timedelta(days=gr.GSC_LAG_DAYS)
    this_start = end - dt.timedelta(days=WEEK - 1)
    last_end = this_start - dt.timedelta(days=1)
    last_start = last_end - dt.timedelta(days=WEEK - 1)
    m_start = end - dt.timedelta(days=DAYS_IN_MONTH - 1)
    pm_end = m_start - dt.timedelta(days=1)
    pm_start = pm_end - dt.timedelta(days=DAYS_IN_MONTH - 1)
    return {
        "this_week": (this_start.isoformat(), end.isoformat()),
        "last_week": (last_start.isoformat(), last_end.isoformat()),
        "trailing_28": (m_start.isoformat(), end.isoformat()),
        "prior_28": (pm_start.isoformat(), pm_end.isoformat()),
    }


def human_bucket(svc, window: tuple[str, str]) -> dict:
    """Human non-brand clicks and impressions for a window, plus the queries themselves."""
    rows = gr.fetch(svc, *window, "query")
    parts = gr.partition_queries(rows)
    summary = gr.summarise(parts["human"])
    summary["named_queries"] = len(rows)
    summary["named_impressions"] = int(sum(r["impressions"] for r in rows))
    summary["brand_clicks"] = int(sum(r["clicks"] for r in parts["brand"]))
    summary["machine_impressions"] = int(sum(r["impressions"] for r in parts["machine"]))
    summary["queries"] = sorted(
        ({"query": r["keys"][0], "impressions": int(r["impressions"]),
          "clicks": int(r["clicks"]), "position": round(r["position"], 1)}
         for r in parts["human"]), key=lambda q: -q["impressions"])
    return summary


def cluster_human_impressions(svc, window: tuple[str, str]) -> dict:
    """Human impressions per cluster, by joining the page and query dimensions.

    The page+query dimension pair is withheld far more aggressively than either dimension
    alone - about a quarter of sitewide impressions survive it on this site - so these are
    the hardest floor in the report. Coverage is returned alongside so the reader can see
    how thin the basis is rather than having to guess.
    """
    body = {"startDate": window[0], "endDate": window[1],
            "dimensions": ["page", "query"], "rowLimit": 25000}
    rows = svc.searchanalytics().query(siteUrl=gr.SITE, body=body).execute().get("rows", [])
    # partition_queries keys off keys[0], so present the query as the first dimension.
    as_query = [{"keys": [r["keys"][1]], "clicks": r["clicks"],
                 "impressions": r["impressions"], "position": r["position"],
                 "page": r["keys"][0]} for r in rows]
    parts = gr.partition_queries(as_query)

    slug_clusters = gr.load_slug_clusters()
    per: dict[str, dict] = {}
    for r in parts["human"]:
        category = gr.page_cluster(r["page"], slug_clusters) or "(no cluster)"
        b = per.setdefault(category, {"impressions": 0.0, "clicks": 0.0, "pages": set()})
        b["impressions"] += r["impressions"]
        b["clicks"] += r["clicks"]
        b["pages"].add(urlsplit(r["page"]).path)

    site = gr.fetch(svc, *window, "")
    site_impressions = int(site[0]["impressions"]) if site else 0
    joined = int(sum(r["impressions"] for r in rows))

    live = live_pages_per_cluster()
    out = []
    for num, slug, label in gr.CLUSTERS:
        b = per.get(slug)
        out.append({"cluster": num, "label": label,
                    "live_pages": live.get(slug, 0),
                    "impressions": int(b["impressions"]) if b else 0,
                    "clicks": int(b["clicks"]) if b else 0,
                    "pages": len(b["pages"]) if b else 0})
    b = per.get("(no cluster)")
    if b:
        out.append({"cluster": None, "label": "Pages in no cluster",
                    "impressions": int(b["impressions"]), "clicks": int(b["clicks"]),
                    "pages": len(b["pages"])})
    return {"clusters": out, "joined_impressions": joined,
            "site_impressions": site_impressions,
            "coverage_pct": (round(100 * joined / site_impressions, 1)
                             if site_impressions else None)}


def top_movement(this_queries: list[dict], last_queries: list[dict],
                 top_n: int = TOP_N) -> dict:
    """Which human queries entered and left the top N between the two weeks.

    Entries carry their impressions, because on a site this size the set turns over almost
    completely every week on single-impression rows. Bare names would read as dramatic
    churn when the whole movement is worth a handful of impressions.
    """
    this_top = this_queries[:top_n]
    last_top = last_queries[:top_n]
    this_names = {q["query"] for q in this_top}
    last_names = {q["query"] for q in last_top}

    entered = [q for q in this_top if q["query"] not in last_names]
    left = [q for q in last_top if q["query"] not in this_names]
    held = [q for q in this_top if q["query"] in last_names]
    return {
        "n": top_n,
        "this_count": len(this_top), "last_count": len(last_top),
        "entered": entered, "left": left, "held": held,
        "entered_impressions": sum(q["impressions"] for q in entered),
        "left_impressions": sum(q["impressions"] for q in left),
        # Below top_n the "top 20" is simply every human query there was, which is a list
        # and not a ranking. Say which it is.
        "is_a_ranking": len(this_top) >= top_n and len(last_top) >= top_n,
        # A set that turns over entirely on tiny rows is noise, not a signal.
        "single_impression_share": (
            round(sum(1 for q in this_top + last_top if q["impressions"] <= 1)
                  / len(this_top + last_top), 2) if (this_top or last_top) else None),
    }


def live_pages_per_cluster() -> dict[str, int]:
    """Surfaces actually live per cluster, so a zero can be read correctly.

    Zero named impressions on a cluster with no pages means nothing has been tried. Zero
    on a cluster with eight live surfaces means something has been tried and has not
    landed. Those are opposite situations and the impression count alone cannot tell them
    apart.
    """
    counts: dict[str, int] = {slug: 0 for _, slug, _ in gr.CLUSTERS}
    for category in gr.load_slug_clusters().values():
        if category in counts:
            counts[category] += 1
    for category in gr.TOOL_PATHS.values():
        if category in counts:
            counts[category] += 1
    return counts


def verdict(this_week: dict, trailing: dict, today: dt.date) -> dict:
    """Whether the trajectory reaches the target. Arithmetic, no hedging."""
    days_left = (DAY_90 - today).days
    monthly_rate = trailing["clicks"]      # trailing 28d ~ one month
    reaches_target = monthly_rate >= TARGET_MONTHLY
    reaches_band = monthly_rate >= BAND_LOW
    if monthly_rate == 0:
        multiple = None
        sentence = (
            f"No. Human non-brand clicks over the trailing {DAYS_IN_MONTH} days are zero, "
            f"so there is no rate to extrapolate and no multiple to quote: "
            f"{TARGET_MONTHLY:,} from zero is not a multiple, it is a standing start with "
            f"{days_left} days left. Reaching even the band's floor of {BAND_LOW}/month "
            f"requires a change in kind rather than degree, and reaching "
            f"{TARGET_MONTHLY:,} is {TARGET_MONTHLY / BAND_HIGH:.1f}x beyond the band's "
            f"own ceiling of {BAND_HIGH:,}, so the target was never reachable by publishing "
            f"inside 90 days.")
    else:
        multiple = round(TARGET_MONTHLY / monthly_rate, 1)
        verdict_word = "Yes" if reaches_target else "No"
        sentence = (
            f"{verdict_word}. Human non-brand clicks are {monthly_rate}/month on the "
            f"trailing {DAYS_IN_MONTH} days, which is {multiple}x short of "
            f"{TARGET_MONTHLY:,} and "
            f"{'inside' if reaches_band else 'below'} the {BAND_LOW}\u2013{BAND_HIGH:,} band, "
            f"with {days_left} days to {DAY_90.isoformat()}. Closing the gap needs "
            f"{TARGET_MONTHLY - monthly_rate:,} more clicks a month; the band's ceiling of "
            f"{BAND_HIGH:,} is itself {TARGET_MONTHLY / BAND_HIGH:.1f}x short of the target.")
    return {"days_to_day_90": days_left, "monthly_human_clicks": monthly_rate,
            "multiple_to_target": multiple, "reaches_target": reaches_target,
            "reaches_band_floor": reaches_band, "sentence": sentence}


def render(d: dict) -> str:
    w = d["windows"]
    tw, lw, tr, pr = d["this_week"], d["last_week"], d["trailing_28"], d["prior_28"]
    L: list[str] = []
    L.append(f"\n## {d['generated']} — weekly scoreboard\n")
    L.append(f"This week {w['this_week'][0]} to {w['this_week'][1]}, against last week "
             f"{w['last_week'][0]} to {w['last_week'][1]}. Windows end "
             f"{gr.GSC_LAG_DAYS} days back because Search Console lags about that long.\n")
    L.append("Labels: **MEASURED** is a complete sitewide total. **FLOOR** comes from the "
             "query dimension, which withholds low-volume queries, so the real figure is "
             "higher by an unknown amount. **ESTIMATE** is bounded in neither direction. "
             "\"Human\" means non-brand and non-machine.\n")

    # 1 -------------------------------------------------------------------
    L.append("### 1. Human non-brand clicks — the number the campaign lives on\n")
    L.append("| | This week | Last week | Trailing 28d | Prior 28d |")
    L.append("|---|---:|---:|---:|---:|")
    L.append(f"| **Human clicks** (ESTIMATE) | **{tw['clicks']}** | {lw['clicks']} | "
             f"{tr['clicks']} | {pr['clicks']} |")
    L.append(f"| Human impressions (ESTIMATE) | {tw['impressions']} | {lw['impressions']} | "
             f"{tr['impressions']} | {pr['impressions']} |")
    L.append(f"| Human avg position | {tw['position'] or '—'} | {lw['position'] or '—'} | "
             f"{tr['position'] or '—'} | {pr['position'] or '—'} |")
    L.append(f"| Brand clicks, for contrast (FLOOR) | {tw['brand_clicks']} | "
             f"{lw['brand_clicks']} | {tr['brand_clicks']} | {pr['brand_clicks']} |")
    L.append(f"| Machine fan-out impressions removed (FLOOR) | {tw['machine_impressions']} | "
             f"{lw['machine_impressions']} | {tr['machine_impressions']} | "
             f"{pr['machine_impressions']} |")

    change = d["week_change"]
    L.append(f"\n{change}\n")
    if d["position_is_composition"]:
        L.append(f"The human average position moved {lw['position']} to {tw['position']}, "
                 f"and that is **composition, not movement**: the two weeks share "
                 f"{len(d['movement']['held'])} queries out of "
                 f"{tw['named_queries']} and {lw['named_queries']} named. A different set "
                 f"of queries produces a different average. This site has already been "
                 f"misread once this way — an average position rising 23.1 to 7.2 in 2025 "
                 f"was the deep-position tail vanishing, not a gain.\n")
    L.append(f"Against the day-90 band of **{BAND_LOW}–{BAND_HIGH:,} human clicks/month**: "
             f"the trailing 28 days produced **{tr['clicks']}**. "
             f"{d['band_position']}\n")

    # 2 -------------------------------------------------------------------
    v = d["verdict"]
    L.append(f"### 2. Distance to {TARGET_MONTHLY:,}/month\n")
    if v["multiple_to_target"] is None:
        L.append(f"**Not computable as a multiple.** Human non-brand clicks over the "
                 f"trailing {DAYS_IN_MONTH} days are zero, and a multiple of zero is not "
                 f"a number. Stated plainly rather than shown as infinity or a "
                 f"placeholder: the campaign has produced no human non-brand click in "
                 f"this window.\n")
    else:
        L.append(f"**{v['multiple_to_target']}x away.** {v['monthly_human_clicks']} human "
                 f"non-brand clicks/month against a target of {TARGET_MONTHLY:,}.\n")

    # 3 -------------------------------------------------------------------
    m = d["movement"]
    L.append(f"### 3. Top {m['n']} human queries — what entered and what left\n")
    if not m["is_a_ranking"]:
        L.append(f"This week holds {m['this_count']} human queries and last week "
                 f"{m['last_count']}, both under {m['n']}, so this is the complete list "
                 f"rather than a ranking. Nothing is being cut off.\n")
    def named(rows):
        return (", ".join(f"`{q['query']}` ({q['impressions']})" for q in rows)
                if rows else "none")

    L.append(f"- **Entered ({len(m['entered'])}, {m['entered_impressions']} impressions):** "
             + named(m["entered"]))
    L.append(f"- **Left ({len(m['left'])}, {m['left_impressions']} impressions):** "
             + named(m["left"]))
    L.append(f"- **Held ({len(m['held'])}):** " + named(m["held"]))
    if m["single_impression_share"] is not None and m["single_impression_share"] >= 0.5:
        L.append(f"\n{100*m['single_impression_share']:.0f}% of the queries on both sides "
                 f"carry one impression or fewer, so near-total turnover here is sampling "
                 f"noise rather than movement. Do not read `Held (0)` as a collapse.")
    if tw["queries"]:
        L.append("\n| Human query this week | Impr | Clicks | Pos |")
        L.append("|---|---:|---:|---:|")
        for q in tw["queries"][:m["n"]]:
            L.append(f"| {q['query'][:58]} | {q['impressions']} | {q['clicks']} | "
                     f"{q['position']} |")
    else:
        L.append("\nNo human queries were named this week.")

    # 4 -------------------------------------------------------------------
    c = d["clusters"]
    L.append(f"\n### 4. Human impressions per cluster\n")
    cov = (f"{c['coverage_pct']}%" if c["coverage_pct"] is not None else "unknown")
    L.append(f"Joining the page and query dimensions costs coverage: {c['joined_impressions']} "
             f"of {c['site_impressions']} sitewide impressions survive the join "
             f"({cov}). **This is the hardest floor in the report** — treat a zero as "
             f"\"nothing named\", not as proof of nothing.\n")
    L.append("| # | Cluster | Live surfaces | Human impr | Human clicks | Pages named |")
    L.append("|---:|---|---:|---:|---:|---:|")
    for row in c["clusters"]:
        num = row["cluster"] if row["cluster"] is not None else "—"
        live = row.get("live_pages")
        L.append(f"| {num} | {row['label']} | {live if live is not None else '—'} | "
                 f"{row['impressions']} | {row['clicks']} | {row['pages']} |")
    tried = [r for r in c["clusters"] if r["cluster"] is not None
             and r["impressions"] == 0 and (r.get("live_pages") or 0) > 0]
    untried = [r for r in c["clusters"] if r["cluster"] is not None
               and r["impressions"] == 0 and not (r.get("live_pages") or 0)]
    if tried:
        L.append(f"\n**Shipped but earning nothing named:** " + ", ".join(
            f"cluster {r['cluster']} ({r['live_pages']} live surfaces)"
            for r in tried) + ". Something has been tried here and has not landed yet.")
    if untried:
        L.append(f"\n**Nothing live yet:** " + ", ".join(
            f"cluster {r['cluster']}" for r in untried)
            + ". A zero here means nothing has been published, not that it failed.")

    # 5 -------------------------------------------------------------------
    L.append(f"\n### 5. Does the trajectory reach {TARGET_MONTHLY:,}/month by "
             f"{DAY_90.isoformat()}?\n")
    L.append(v["sentence"])
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    ap.add_argument("--credential")
    ap.add_argument("--weekly", action="store_true",
                    help="write only on WRITE_WEEKDAY, so the daily job can call this "
                         "every run without turning a weekly scoreboard into a daily log")
    args = ap.parse_args()

    if args.weekly and dt.date.today().weekday() != WRITE_WEEKDAY:
        print(f"scoreboard: not {WRITE_WEEKDAY_NAME}, skipping (weekly cadence). "
              f"Run without --weekly for an on-demand read.")
        return 0

    svc = gr.search_console(args.credential)
    if svc is None:
        print("Search Console UNAVAILABLE (missing credential or google-api-python-client). "
              "No scoreboard written — a scoreboard of zeros would read as a collapse.")
        return 2

    today = dt.date.today()
    w = week_windows(today)
    this_week = human_bucket(svc, w["this_week"])
    last_week = human_bucket(svc, w["last_week"])
    trailing = human_bucket(svc, w["trailing_28"])
    prior = human_bucket(svc, w["prior_28"])

    # Week-over-week change, honest about a zero denominator.
    if last_week["clicks"] == 0 and this_week["clicks"] == 0:
        change = ("Week over week: **zero to zero.** No percentage is quoted because there "
                  "is nothing to compare — this is a flat line at zero, not a decline.")
    elif last_week["clicks"] == 0:
        change = (f"Week over week: **0 to {this_week['clicks']}.** No percentage is "
                  f"quoted because the previous week was zero and a change from zero has "
                  f"no multiple.")
    else:
        pct = 100 * (this_week["clicks"] - last_week["clicks"]) / last_week["clicks"]
        change = (f"Week over week: **{last_week['clicks']} to {this_week['clicks']}**, "
                  f"{pct:+.0f}%.")

    if trailing["clicks"] == 0:
        band_position = (f"That is below the floor, and not marginally: the floor assumes "
                         f"the campaign produces human clicks at all.")
    elif trailing["clicks"] < BAND_LOW:
        band_position = (f"That is below the band's floor by "
                         f"{BAND_LOW - trailing['clicks']} clicks/month.")
    elif trailing["clicks"] <= BAND_HIGH:
        band_position = "That is inside the band."
    else:
        band_position = (f"That is above the band's ceiling by "
                         f"{trailing['clicks'] - BAND_HIGH} clicks/month.")

    data = {
        "generated": today.isoformat(),
        "windows": w,
        "this_week": this_week, "last_week": last_week,
        "trailing_28": trailing, "prior_28": prior,
        "week_change": change,
        "band": {"low": BAND_LOW, "high": BAND_HIGH, "target": TARGET_MONTHLY},
        "band_position": band_position,
        "movement": top_movement(this_week["queries"], last_week["queries"]),
        "clusters": cluster_human_impressions(svc, w["this_week"]),
        "verdict": verdict(this_week, trailing, today),
    }
    # An average position over two almost-disjoint query sets is composition, not movement.
    held = len(data["movement"]["held"])
    data["position_is_composition"] = bool(
        this_week["position"] and last_week["position"]
        and held <= max(1, min(this_week["queries"] and len(this_week["queries"]) or 0,
                               last_week["queries"] and len(last_week["queries"]) or 0) // 3))

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
            "# Weekly scoreboard\n\n"
            "Appended by `tools/gsc_scoreboard.py`, one dated section per run. The five\n"
            "figures the campaign is judged on and nothing else — the other Search Console\n"
            "tools answer everything wider.\n\n"
            "Read the labels. **MEASURED** is a complete sitewide total. **FLOOR** comes\n"
            "from the query dimension, which withholds low-volume queries, so the truth is\n"
            "higher by an unknown amount. **ESTIMATE** is bounded in neither direction.\n"
            "\"Human\" means non-brand and non-machine: brand is removed first, then pasted\n"
            "blobs, then machine query fan-out. Where a number cannot be computed honestly\n"
            "it says so — there are no placeholders here.\n",
            encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
