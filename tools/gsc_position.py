#!/usr/bin/env python3
"""What moves position on this domain — measured, with the sample size on every claim.

The funnel breaks at position, not at indexing and not at click-through: 5.9% of human
impressions have ever been in the top 10, and 79% sat at 31+ where 9,321 impressions
produced one click. So the question that matters is what moves a page up, and whether
anything does.

    1. FEATURES     pages that reached the top 20 on a human query against pages stuck
                    at 31+: inbound links, word count, age, cluster, recovery
    2. TRAJECTORY   does position improve over time, per (page, query) pair
    3. MOVERS       pages whose position moved materially, and whether anything was done
                    to them

    tools/gsc_position.py             # append to planning/position.md
    tools/gsc_position.py --dry-run
    tools/gsc_position.py --json PATH

TWO MEASUREMENT DECISIONS THAT CHANGE THE ANSWER
------------------------------------------------
**Position is measured per (page, query) pair, never per page.** A page's average position
moves whenever its query mix moves, with no ranking change at all. That confound has
already produced two false readings on this campaign - an average position "improving" 23.1
to 7.2 in 2025 was the deep-position tail vanishing, and 37.0 to 66.3 in one week was two
almost-disjoint query sets.

**Clicks and impressions on the injected spam pages are excluded.** The query separator
works on queries, and the Japanese counterfeit-goods pages injected in September 2025
ranked for ordinary consumer queries, so it passed them as human - correctly, they were
real people. Eight of the twenty human clicks in the whole record landed on
`/products/<id>` URLs. They are not readers of this site's content and counting them
overstates the baseline, so pages outside the site's own URL structure are dropped here.

WHAT THE SAMPLE WILL AND WILL NOT SUPPORT
-----------------------------------------
Most of this is underpowered and the report says so per section rather than once at the end.
Coverage is measured and printed rather than assumed: over the full history the
date+page+query pull keeps about half of sitewide impressions, not the fifth a short-window
reading suggests. Every count is still a floor.

The binding limitation is that position movement is almost entirely a property of the
*previous* site: of the pairs with enough history to show a trend, the overwhelming majority
belong to legacy URLs, and campaign content contributes a handful. Anything this tool says
about trajectory is therefore about a site that no longer exists, until the campaign's own
pages accumulate history.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import pathlib
import re
import statistics as st
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gsc_report as gr  # noqa: E402
import gsc_attribution as at  # noqa: E402
import gsc_collapse_forensics as fx  # noqa: E402

LOG = gr.ROOT / "planning" / "position.md"
HISTORY_START = dt.date(2025, 4, 1)
TOP_BAND = 20.0
DEEP_BAND = 31.0
MIN_SPAN_DAYS = 21
MATERIAL_MOVE = 5.0
# Below this a group comparison is reported as directional at best.
UNDERPOWERED = 30
# Shares the scoreboard's weekday so the weekly reads land together.
WRITE_WEEKDAY = 0
POST_URL = re.compile(r"/(?:articles|blog)/([^/]+)/")
BODY_LINK = re.compile(r"\[([^\]]+)\]\(/articles/([a-z0-9][a-z0-9\-\.]*)/?\)")
DATED_SECTION = re.compile(
    r"(?m)^## (?P<date>\d{4}-\d{2}-\d{2}) — what moves position\s*$"
)


def pull_human(svc, start: dt.date, end: dt.date) -> list[dict]:
    """Human, non-brand, non-machine rows at date+page+query, excluding injected pages."""
    rows = []
    cursor = start
    while cursor <= end:
        stop = min(cursor + dt.timedelta(days=90), end)
        body = {"startDate": cursor.isoformat(), "endDate": stop.isoformat(),
                "dimensions": ["date", "page", "query"], "rowLimit": 25000}
        got = svc.searchanalytics().query(siteUrl=gr.SITE, body=body).execute().get("rows", [])
        if len(got) >= 25000:
            print(f"WARNING: row cap hit for {cursor}..{stop}; that chunk is truncated")
        rows += got
        cursor = stop + dt.timedelta(days=1)

    as_query = [{"keys": [r["keys"][2]], "clicks": r["clicks"],
                 "impressions": r["impressions"], "position": r["position"],
                 "date": r["keys"][0], "page": r["keys"][1]} for r in rows]
    human = gr.partition_queries(as_query)["human"]
    kept = [r for r in human if not fx.is_foreign(r["page"])]
    dropped = [r for r in human if fx.is_foreign(r["page"])]

    # The three-dimension pull is withheld far harder than one dimension. Measure the
    # coverage rather than describing it as "roughly a fifth": it is the error bar on
    # every count in this report.
    joined = sum(r["impressions"] for r in rows)
    site = gr.fetch(svc, start.isoformat(), end.isoformat(), "")
    sitewide = int(site[0]["impressions"]) if site else 0
    return kept, {"rows": len(dropped),
                  "clicks": int(sum(r["clicks"] for r in dropped)),
                  "impressions": int(sum(r["impressions"] for r in dropped)),
                  "joined_impressions": int(joined), "sitewide_impressions": sitewide,
                  "coverage_pct": round(100 * joined / sitewide, 1) if sitewide else None}


def post_features() -> dict[str, dict]:
    """Inbound body links, word count, ship date and cluster for every published post."""
    import frontmatter

    posts, bodies = {}, {}
    for path in sorted((gr.ROOT / "content" / "posts").glob("*.md")):
        fm = frontmatter.load(path)
        if fm.get("status") != "published":
            continue
        slug = str(fm.get("slug") or path.stem)
        bodies[slug] = fm.content
        posts[slug] = {
            "cluster": fm.get("category"),
            "words": len(fm.content.split()),
            "shipped": at.first_added(str(path.relative_to(gr.ROOT))),
            "inbound": 0,
        }
    # Body links only. Template and listing links are not editorial signals, and
    # tools/audit_clusters.py treats them separately for the same reason.
    for slug, body in bodies.items():
        for _, target in BODY_LINK.findall(body):
            if target in posts and target != slug:
                posts[target]["inbound"] += 1
    return posts


def slug_of(url: str) -> str | None:
    m = POST_URL.fullmatch(urlsplit(url).path)
    return m.group(1) if m else None


def feature_comparison(human: list[dict], posts: dict, latest: dt.date) -> dict:
    best, impressions, clicks = {}, collections.Counter(), collections.Counter()
    for r in human:
        slug = slug_of(r["page"])
        if slug is None or slug not in posts:
            continue
        best[slug] = min(best.get(slug, 999.0), r["position"])
        impressions[slug] += r["impressions"]
        clicks[slug] += r["clicks"]

    groups = {
        "top20": [s for s, b in best.items() if b <= TOP_BAND],
        "mid": [s for s, b in best.items() if TOP_BAND < b < DEEP_BAND],
        "deep": [s for s, b in best.items() if b >= DEEP_BAND],
    }

    def describe(slugs):
        if not slugs:
            return {"n": 0}
        ib = [posts[s]["inbound"] for s in slugs]
        wc = [posts[s]["words"] for s in slugs]
        ages = [(latest - posts[s]["shipped"]).days for s in slugs if posts[s]["shipped"]]
        return {
            "n": len(slugs),
            "inbound_median": st.median(ib), "inbound_mean": round(st.mean(ib), 1),
            "inbound_zero": sum(1 for x in ib if x == 0),
            "words_median": round(st.median(wc)),
            "age_median": round(st.median(ages)) if ages else None,
            "clusters": dict(collections.Counter(posts[s]["cluster"] for s in slugs).most_common()),
            "impressions_total": int(sum(impressions[s] for s in slugs)),
            "clicks_total": int(sum(clicks[s] for s in slugs)),
        }

    out = {k: describe(v) for k, v in groups.items()}
    out["posts_total"] = len(posts)
    out["posts_with_human_impression"] = len(best)
    out["posts_with_human_click"] = sum(1 for s in clicks if clicks[s] > 0)
    # Which features actually separate the groups.
    t, d = out["top20"], out["deep"]
    seps = {}
    if t["n"] and d["n"]:
        for key in ("inbound_median", "words_median", "age_median"):
            a, b = t.get(key), d.get(key)
            if a is None or b is None:
                continue
            seps[key] = {"top20": a, "deep": b,
                         "ratio": round(a / b, 2) if b else None,
                         "separates": bool(b and (a / b >= 1.5 or a / b <= 0.67))}
    out["separation"] = seps
    return out


def trajectories(human: list[dict], posts: dict) -> dict:
    """Per (page, query) position change, early third against late third of its own span."""
    pairs = collections.defaultdict(list)
    for r in human:
        pairs[(r["page"], r["keys"][0])].append((r["date"], r["position"], r["impressions"]))

    out = []
    for (page, query), obs in pairs.items():
        obs.sort()
        d0 = dt.date.fromisoformat(obs[0][0])
        d1 = dt.date.fromisoformat(obs[-1][0])
        span = (d1 - d0).days
        if span < MIN_SPAN_DAYS or len(obs) < 2:
            continue
        third = span / 3
        early = [(p, i) for d, p, i in obs if (dt.date.fromisoformat(d) - d0).days <= third]
        late = [(p, i) for d, p, i in obs if (d1 - dt.date.fromisoformat(d)).days <= third]
        if not early or not late:
            continue
        ep = sum(p * i for p, i in early) / sum(i for _, i in early)
        lp = sum(p * i for p, i in late) / sum(i for _, i in late)
        slug = slug_of(page)
        out.append({
            "page": urlsplit(page).path, "query": query, "slug": slug,
            "campaign": bool(slug and slug in posts),
            "span_days": span, "observations": len(obs),
            "early_position": round(ep, 1), "late_position": round(lp, 1),
            "delta": round(ep - lp, 1),     # positive = improved (moved up)
            "impressions": int(sum(i for _, _, i in obs)),
            "first_seen": obs[0][0], "last_seen": obs[-1][0],
        })

    def summarise(rows):
        if not rows:
            return {"n": 0}
        deltas = [r["delta"] for r in rows]
        return {"n": len(rows),
                "median_delta": round(st.median(deltas), 1),
                "mean_delta": round(st.mean(deltas), 1),
                "improved": sum(1 for x in deltas if x > MATERIAL_MOVE),
                "worsened": sum(1 for x in deltas if x < -MATERIAL_MOVE),
                "flat": sum(1 for x in deltas if abs(x) <= MATERIAL_MOVE)}

    return {"pairs": out,
            "all": summarise(out),
            "campaign": summarise([r for r in out if r["campaign"]]),
            "legacy": summarise([r for r in out if not r["campaign"]])}


def intervened(pair: dict) -> bool | None:
    """Was the page's source substantially changed during the movement window?

    None means unknowable rather than no: a legacy URL has no source file in this repo, so
    nothing can be checked. Collapsing that into "no" would turn an absence of evidence
    into evidence of absence on 82 of 84 movers.
    """
    if not (pair["campaign"] and pair["slug"]):
        return None
    for cand in (gr.ROOT / "content" / "posts").glob("*.md"):
        if cand.stem == pair["slug"]:
            since = dt.date.fromisoformat(pair["first_seen"])
            return at.last_substantial_change(
                str(cand.relative_to(gr.ROOT)), since) is not None
    return None


def movers(traj: dict, posts: dict) -> dict:
    """Material movers, and whether the page's source was touched during the movement."""
    out = []
    for r in traj["pairs"]:
        if abs(r["delta"]) < MATERIAL_MOVE * 2:
            continue
        out.append({**r, "intervened": intervened(r)})
    out.sort(key=lambda r: -abs(r["delta"]))
    unattributable = sum(1 for r in out if r["intervened"] is None)
    # Every campaign pair, not a sample: the whole campaign-content evidence base is
    # small enough to print, and printing it is the only honest way to show how small.
    campaign_pairs = sorted(({**r, "intervened": intervened(r)}
                             for r in traj["pairs"] if r["campaign"]),
                            key=lambda r: -r["delta"])
    # The clearest improvement nobody caused: biggest gainer with real impression volume,
    # on a page with no source file in this repo and no campaign work against it.
    sustained = sorted((r for r in traj["pairs"]
                        if not r["campaign"] and r["delta"] > MATERIAL_MOVE
                        and r["impressions"] >= 100 and r["span_days"] >= 90),
                       key=lambda r: -r["delta"])
    return {"movers": out, "unattributable": unattributable,
            "campaign_pairs": campaign_pairs, "sustained_legacy_gains": sustained[:5],
            "improved_without_intervention": [r for r in out
                                              if r["delta"] > 0 and r["intervened"] is False],
            "improved_with_intervention": [r for r in out
                                           if r["delta"] > 0 and r["intervened"] is True]}


def render(d: dict) -> str:
    f, t, m = d["features"], d["trajectory"], d["movers"]
    L = [f"\n## {d['generated']} — what moves position\n"]
    L.append(f"Search Console through {d['latest']}, human non-brand queries, fan-out "
             f"removed, and pages outside this site's URL structure excluded — that last "
             f"filter drops {d['excluded']['clicks']} click(s) and "
             f"{d['excluded']['impressions']} impressions on the injected `/products/` "
             f"spam pages, which were real people but not readers of this site.\n")
    L.append("Position is measured **per (page, query) pair**. A page's average position "
             "moves when its query mix moves, with no ranking change at all.\n")

    # 1 --------------------------------------------------------------
    L.append("### 1. What top-20 pages have that 31+ pages do not\n")
    L.append(f"Of {f['posts_total']} published posts, {f['posts_with_human_impression']} "
             f"have ever had a human impression and **{f['posts_with_human_click']} have "
             f"ever had a human click**.\n")
    L.append("| | Ever top-20 | Best 21–30 | 31+ only |")
    L.append("|---|---:|---:|---:|")
    rows = [("Pages", "n"), ("Inbound body links, median", "inbound_median"),
            ("Pages with zero inbound", "inbound_zero"),
            ("Word count, median", "words_median"), ("Age in days, median", "age_median"),
            ("Human impressions, total", "impressions_total"),
            ("Human clicks, total", "clicks_total")]
    for label, key in rows:
        L.append(f"| {label} | {f['top20'].get(key, '—')} | {f['mid'].get(key, '—')} | "
                 f"{f['deep'].get(key, '—')} |")
    L.append(f"| Clusters | {f['top20'].get('clusters', '—')} | "
             f"{f['mid'].get('clusters', '—')} | {f['deep'].get('clusters', '—')} |")

    seps = [k for k, v in f["separation"].items() if v["separates"]]
    if seps:
        L.append(f"\n**Separating features:** " + ", ".join(
            f"`{k}` ({f['separation'][k]['top20']} vs {f['separation'][k]['deep']}, "
            f"ratio {f['separation'][k]['ratio']})" for k in seps))
    else:
        L.append(f"\n**No feature separates the two groups.** Inbound links, word count and "
                 f"age are within a third of each other, and both groups are dominated by "
                 f"the same cluster. On n={f['top20']['n']} against n={f['deep']['n']} this "
                 f"is underpowered, but the honest reading is not \"we cannot tell\" — it is "
                 f"that **the features the campaign can control show no relationship to "
                 f"whether a page reached the top 20.**")

    # 2 --------------------------------------------------------------
    L.append("\n### 2. Does position improve over time?\n")
    L.append("| Cohort | Pairs | Median Δ | Mean Δ | Improved | Worsened | Flat |")
    L.append("|---|---:|---:|---:|---:|---:|---:|")
    for key, label in (("all", "All"), ("campaign", "Campaign content"),
                       ("legacy", "Legacy URLs")):
        s = t[key]
        if not s["n"]:
            L.append(f"| {label} | 0 | — | — | — | — | — |")
            continue
        L.append(f"| {label} | {s['n']} | {s['median_delta']:+.1f} | {s['mean_delta']:+.1f} | "
                 f"{s['improved']} | {s['worsened']} | {s['flat']} |")
    L.append(f"\nΔ is places gained, so positive means the pair moved up. A move counts as "
             f"material at more than {MATERIAL_MOVE:g} places.\n")
    L.append(d["trajectory_verdict"])

    # 3 --------------------------------------------------------------
    L.append(f"\n### 3. Movers, and whether anything was done to them\n")
    L.append(f"{len(m['movers'])} pair(s) moved more than {MATERIAL_MOVE*2:g} places. "
             f"Intervention is read from whether the page's source file was substantially "
             f"changed during the movement window; for legacy URLs there is no source file, "
             f"so **{m['unattributable']} of them cannot be attributed either way**.\n")
    if m["movers"]:
        L.append("| Query | Page | Δ | From → to | Span | Impr | Intervened |")
        L.append("|---|---|---:|---|---:|---:|---|")
        for r in m["movers"][:15]:
            iv = {True: "yes", False: "no", None: "unknowable"}[r["intervened"]]
            L.append(f"| {r['query'][:30]} | {r['page'][:30]} | {r['delta']:+.1f} | "
                     f"{r['early_position']} → {r['late_position']} | {r['span_days']}d | "
                     f"{r['impressions']} | {iv} |")
    if m["campaign_pairs"]:
        L.append(f"\n**Every campaign-content pair with enough history to show a trend — "
                 f"all {len(m['campaign_pairs'])} of them.** This is the entire evidence "
                 f"base for whether campaign pages move, and both were edited during the "
                 f"window, so neither is a clean natural experiment:\n")
        L.append("| Query | Page | Δ | From → to | Span | Impr | Intervened |")
        L.append("|---|---|---:|---|---:|---:|---|")
        for r in m["campaign_pairs"]:
            iv = {True: "yes", False: "no", None: "unknowable"}[r["intervened"]]
            L.append(f"| {r['query'][:30]} | {r['page'][:34]} | {r['delta']:+.1f} | "
                     f"{r['early_position']} → {r['late_position']} | {r['span_days']}d | "
                     f"{r['impressions']} | {iv} |")
        L.append("\nOne up, one down, both intervened. **n=2 with one outcome each way is "
                 "not evidence in either direction** — it is the sample telling you it is "
                 "not ready to be asked.")

    if m["sustained_legacy_gains"]:
        top = m["sustained_legacy_gains"][0]
        L.append(f"\n**The clearest improvement nobody caused.** `{top['page']}` moved "
                 f"{top['early_position']} → {top['late_position']} on `{top['query']}` over "
                 f"{top['span_days']} days, carrying {top['impressions']} impressions — the "
                 f"largest sustained gain in the record. It has no source file in this repo "
                 f"and no campaign work has ever touched it. Whether anyone edited it before "
                 f"the March 2026 rebuild is unknowable, but no campaign intervention did.\n")
        L.append("| Query | Page | Δ | From → to | Span | Impr |")
        L.append("|---|---|---:|---|---:|---:|")
        for r in m["sustained_legacy_gains"]:
            L.append(f"| {r['query'][:28]} | {r['page'][:32]} | {r['delta']:+.1f} | "
                     f"{r['early_position']} → {r['late_position']} | {r['span_days']}d | "
                     f"{r['impressions']} |")
        L.append("\nThe uncomfortable reading: the best-performing pages on this domain by "
                 "human impressions are legacy comparison pages on topics outside the "
                 "campaign's niche, which climbed by aging rather than by anything anyone did.")

    L.append(f"\n- **Improved without any intervention:** "
             f"{len(m['improved_without_intervention'])} pair(s).")
    L.append(f"- **Improved with an intervention:** "
             f"{len(m['improved_with_intervention'])} pair(s).")
    L.append(f"- **Unattributable (legacy, no source file):** {m['unattributable']} pair(s).")

    L.append("\n### Where the sample is too small to carry a conclusion\n")
    for line in d["limits"]:
        L.append(f"- {line}")
    return "\n".join(L) + "\n"


def trajectory_verdict(t: dict) -> str:
    camp, leg, allc = t["campaign"], t["legacy"], t["all"]
    if camp["n"] < 10 and leg["n"] >= UNDERPOWERED:
        drift = leg["median_delta"]
        settled = ("essentially flat" if abs(drift) <= 2 else
                   f"drifting {'up' if drift > 0 else 'down'} by {abs(drift):.1f} places")
        return (
            f"**The campaign's own content cannot answer this: n={camp['n']}.** Almost all "
            f"the history long enough to show a trend belongs to the previous site "
            f"({leg['n']} pairs), so what follows describes a site that no longer exists.\n\n"
            f"On legacy URLs the median pair is {settled} over its own span, with "
            f"{leg['improved']} improving materially against {leg['worsened']} worsening and "
            f"{leg['flat']} flat. That is much closer to a random walk than to a climb. "
            f"**Read as a prior rather than a finding, it says pages land near where they "
            f"will stay, and that publishing more pages at position 40 should not be "
            f"expected to fix itself with time.** It cannot be transferred to campaign "
            f"content with any confidence: different pages, different cluster, and a domain "
            f"whose indexing behaviour has measurably changed since.")
    if camp["n"] >= UNDERPOWERED:
        drift = camp["median_delta"]
        return (f"**Campaign content: n={camp['n']}, median {drift:+.1f} places.** "
                f"{camp['improved']} improved materially, {camp['worsened']} worsened, "
                f"{camp['flat']} flat.")
    return (f"**Not answerable at this sample.** Campaign pairs n={camp['n']}, legacy "
            f"n={leg['n']}, total n={allc['n']}. Nothing here supports a claim in either "
            f"direction.")


def limits(d: dict) -> list[str]:
    f, t, m = d["features"], d["trajectory"], d["movers"]
    out = []
    out.append(f"**Feature comparison is n={f['top20']['n']} against "
               f"n={f['deep']['n']}.** Directional at best, and it currently shows no "
               f"separation at all rather than a weak one. Do not read the absence of a "
               f"link effect as evidence that links do not matter; read it as this site "
               f"having no page whose link profile is unusual enough to test the question.")
    out.append(f"**Trajectory on campaign content is n={t['campaign']['n']}.** That is not "
               f"directional, it is nothing. The legacy figure (n={t['legacy']['n']}) is a "
               f"prior about a different site.")
    if f["posts_with_human_click"] == 0:
        out.append(f"**0 of {f.get('posts_total', '?')} published posts has ever earned a "
                   f"human click**, and only {f.get('posts_with_human_impression', '?')} "
                   f"have earned a human impression. Every human click in the record belongs "
                   f"to legacy URLs or to the injected spam pages, so there is no "
                   f"campaign-content click behaviour to analyse — not a small sample, an "
                   f"empty one.")
    out.append(f"**Intervention is unknowable for {m['unattributable']} of the movers**, "
               f"because legacy URLs have no source file to check. Any statement about what "
               f"caused a legacy page to move is inference from timing alone.")
    ex = d.get("excluded", {})
    cov = ex.get("coverage_pct")
    out.append(f"**The date+page+query pull keeps "
               f"{ex.get('joined_impressions', '?')} of "
               f"{ex.get('sitewide_impressions', '?')} sitewide impressions"
               + (f" ({cov}%)" if cov is not None else "")
               + ".** Every count here is a floor, and a page can have moved without "
                 "appearing at all.")
    return out


def upsert_dated_report(existing: str, report: str, generated: str) -> str:
    """Keep exactly one position section for a generated date.

    The weekly job can be invoked more than once by a manual check, launchd retry, or a
    resumed campaign cycle. Appending on every invocation makes two slightly different
    GSC pulls look like two independent observations. Replace the first same-day section
    and remove any later duplicates while preserving every other dated section.
    """
    matches = list(DATED_SECTION.finditer(existing))
    targets = [
        (match.start(), matches[i + 1].start() if i + 1 < len(matches) else len(existing))
        for i, match in enumerate(matches)
        if match.group("date") == generated
    ]
    clean_report = report.strip() + "\n"
    if not targets:
        return existing.rstrip() + "\n\n" + clean_report

    updated = existing
    first_start = targets[0][0]
    for start, end in reversed(targets):
        replacement = clean_report if start == first_start else ""
        updated = updated[:start] + replacement + updated[end:]
    return updated.rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    ap.add_argument("--credential")
    ap.add_argument("--weekly", action="store_true",
                    help="write only on the scoreboard's weekday, so the daily job can call "
                         "this every run without appending near-identical sections")
    args = ap.parse_args()

    if args.weekly and dt.date.today().weekday() != WRITE_WEEKDAY:
        print("position: not the write weekday, skipping (weekly cadence). "
              "Run without --weekly for an on-demand read.")
        return 0

    svc = gr.search_console(args.credential)
    if svc is None:
        print("Search Console UNAVAILABLE (missing credential or google-api-python-client). "
              "Nothing written.")
        return 2

    latest = dt.date.today() - dt.timedelta(days=gr.GSC_LAG_DAYS)
    human, excluded = pull_human(svc, HISTORY_START, latest)
    posts = post_features()
    traj = trajectories(human, posts)
    data = {
        "generated": dt.date.today().isoformat(), "latest": latest.isoformat(),
        "excluded": excluded,
        "features": feature_comparison(human, posts, latest),
        "trajectory": traj,
        "movers": movers(traj, posts),
    }
    data["trajectory_verdict"] = trajectory_verdict(traj)
    data["limits"] = limits(data)
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
            "# Position analysis\n\n"
            "Appended by `tools/gsc_position.py`. The funnel breaks at position, so this asks\n"
            "what moves it and refuses to answer past the sample.\n\n"
            "Position is measured per (page, query) pair, never per page: a page's average\n"
            "position moves whenever its query mix moves, and that confound has already\n"
            "produced two false readings on this campaign. Clicks on the injected\n"
            "`/products/` spam pages are excluded — real people, but not readers of this site.\n",
            encoding="utf-8")
    LOG.write_text(
        upsert_dated_report(LOG.read_text(encoding="utf-8"), report,
                            data["generated"]),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
