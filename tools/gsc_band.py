#!/usr/bin/env python3
"""Re-derive the day-90 click band from its inputs, and say how much to trust it.

The band has been restated twice by hand — 700-2,400, then 350-1,350, then 306-1,176 —
each time because a premise under it changed rather than because the arithmetic was wrong.
It is a tool now so the next restatement is reproducible and the old premise is visible
next to the new number.

    tools/gsc_band.py                 # re-derive, append to planning/band.md
    tools/gsc_band.py --dry-run
    tools/gsc_band.py --rows 60 --c3-share 0.55

WHAT CHANGED UNDER IT THIS TIME (2026-08-17)
--------------------------------------------
The 306-1,176 band was computed when the plan was tools-led, and three of its inputs are
no longer what it assumed:

  1. **The protected tool subset does not exist.** The band's AI Overview haircut was
     built on keyword-tool feature flags. Live SERP reads found three of six readable
     build-a-tool keywords carry an AI Overview, the flagship `ai overviews checker`
     reproducibly so, and the flags disagreed with the live SERP on three of four rows in
     BOTH directions. The haircut input is therefore not just wrong, it is unreliable with
     no known sign.
  2. **Tools no longer contribute clicks by design.** They are measured on referring
     domains and the articles they enable, not sessions, so tool rows contribute zero to a
     click band.
  3. **The row count and the mix changed.** Sixty rows remain, not seventy-one, weighted
     toward cluster 3.

And one input was in the wrong units all along, which is corrected here: the band's legacy
term added 15-40 clicks/month, but those were sitewide clicks including brand. The band is
compared against **human non-brand** clicks in the weekly scoreboard, and the measured
human non-brand rate is zero. A band and the number it is judged against have to be the
same quantity.

HOW THE LABELS WORK
-------------------
    MEASURED  first-party and complete
    FLOOR     query-dimension derived; the truth is higher by an unknown amount
    ESTIMATE  bounded in neither direction
    RANGE     no valid point estimate exists; the spread is the answer
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import statistics as st
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gsc_report as gr  # noqa: E402

LOG = gr.ROOT / "planning" / "band.md"
UNIVERSE = gr.ROOT / "planning" / "research-cache" / "DERIVED-full-universe.json"
SWEEP = gr.ROOT / "planning" / "research-cache" / "DERIVED-contamination-sweep.json"

PRIOR_BAND = (306, 1176)
PRIOR_ROWS = 71
TARGET_MONTHLY = 10_000
DAY_90 = dt.date(2026, 11, 15)
ROWS_REMAINING = 60
TAIL_MULT = 2.5

# Cohort maturity at day 90: a page published on day 89 ranks for nothing on day 90.
COHORT_MATURITY = (0.55, 0.30, 0.08)

# DR 26. P(reaching each band within ~90 days) for a KD<=20 target.
P_TOP3, P_4_10, P_11_20 = 0.15, 0.30, 0.25
# Top-3 CTR. The site's own measured figure is 4.1% but sits on legacy off-niche queries.
CTR_TOP3 = (0.08, 0.12, 0.16)

# AI Overview haircut, now a RANGE rather than a point. The flags that produced the old
# 49.2%/35% point estimate were verified wrong on three of four rows in both directions,
# and only seven SERPs have been read live. Share of SERPs carrying an AIO, and the click
# loss on those SERPs.
AIO_SHARE = (0.35, 0.50, 0.65)
AIO_LOSS = (0.25, 0.35, 0.45)

# Measured, GSC: human non-brand clicks over the trailing 28 days, and for ten months.
LEGACY_HUMAN_CLICKS = 0

# Cluster 4 rows produce articles now; the five tools are built and contribute no clicks.
TOOL_ROWS = 0


def universe_kd20() -> dict[int, list[int]]:
    """Per-cluster KD<=20 keyword volumes, descending, scaled to the post-sweep total.

    The sweep recorded per-cluster totals but not which keywords it removed, so each
    cluster's curve is scaled by its own after/before volume ratio. Clusters 1 and 3 lost
    1.0% and 0.2%, so the approximation is tight exactly where the calendar now sits;
    the merged distribution cluster lost 38% and its curve is correspondingly optimistic.
    """
    rows = json.load(open(UNIVERSE))
    sweep = json.load(open(SWEEP))["per_cluster"]
    scale = {int(k): (v["after_volume"] / v["before_volume"] if v["before_volume"] else 1.0)
             for k, v in sweep.items()}
    # The Distribution merge folded clusters 5, 6 and 7 into 5.
    remap = {6: 5, 7: 5}
    per: dict[int, list[int]] = {}
    for r in rows:
        kd = r.get("difficulty")
        if kd is None or kd > 20:
            continue
        c = remap.get(r["cluster"], r["cluster"])
        vol = (r.get("volume") or 0) * scale.get(r["cluster"], 1.0)
        per.setdefault(c, []).append(vol)
    return {c: sorted(v, reverse=True) for c, v in per.items()}


def allocate(rows: int, c3_share: float) -> dict[int, int]:
    """Rows per cluster. Cluster 3 takes c3_share; the rest keep their prior proportions.

    The live queue is on the Hermes box and not readable here, so the mix is a parameter
    rather than a measurement. That is deliberate - it also shows how much the band depends
    on a decision nobody has written down yet.
    """
    c3 = round(rows * c3_share)
    rest = rows - c3
    # Prior weighting among the non-cluster-3 rows: documentation dominant, then
    # distribution, then AI-search articles, then DevEx.
    weights = {1: 0.45, 5: 0.28, 4: 0.17, 2: 0.10}
    alloc = {3: c3}
    assigned = 0
    for c, w in weights.items():
        n = round(rest * w)
        alloc[c] = n
        assigned += n
    # Push any rounding remainder into documentation, the largest non-c3 bucket.
    alloc[1] += rest - assigned
    return {c: n for c, n in alloc.items() if n > 0}


def mature_equivalents(rows: int, maturity=COHORT_MATURITY) -> float:
    """Rows spread evenly across three 30-day cohorts, weighted by ranking maturity."""
    per = rows / len(maturity)
    return sum(per * m for m in maturity)


def per_page_volume(kd20: dict[int, list[int]], alloc: dict[int, int],
                    selection_rank: int) -> dict:
    """Head volume the allocated rows can address, at a given selection quality.

    `selection_rank` is the slice of each cluster's ranked KD<=20 pool the campaign is
    assumed to hit: 0 takes the very best N keywords, 1 takes ranks N..2N, 2 takes 2N..3N.

    Taking rank 0 unconditionally is the trap. It assumes the calendar lands on the single
    best thirty-three keywords in a pool of two hundred, which is perfect selection, and it
    is what made a first run of this tool report the band moving UP when every premise
    under it had worsened. The prior derivation varied selection quality across its
    scenarios for exactly this reason; keeping that axis is what makes the two comparable.
    """
    total_head, detail = 0.0, {}
    for c, n in sorted(alloc.items()):
        pool = kd20.get(c, [])
        start = n * selection_rank
        taken = pool[start:start + n]
        head = sum(taken)
        detail[c] = {"rows": n, "pool": len(pool), "head_volume": round(head),
                     "mean_per_row": round(head / n) if n else 0,
                     "slice": f"{start + 1}-{start + n}",
                     "short_by": max(0, n - len(taken))}
        total_head += head
    return {"head_volume": round(total_head), "per_cluster": detail}


def band(kd20: dict[int, list[int]], rows: int, c3_share: float) -> dict:
    alloc = allocate(rows, c3_share)
    mature = mature_equivalents(rows)
    click_rows = rows - TOOL_ROWS   # tools contribute no clicks by design now

    out = {"allocation": alloc, "mature_equivalents": round(mature, 1), "scenarios": {},
           "comparable": {}}
    # Each scenario varies selection quality, CTR and the AIO haircut together, because a
    # campaign that picks well also tends to match intent well. Varying only one axis and
    # pinning the others at their best is how a model flatters itself.
    for name, rank, ctr, share, loss in (
            ("low", 2, CTR_TOP3[0], AIO_SHARE[2], AIO_LOSS[2]),
            ("mid", 1, CTR_TOP3[1], AIO_SHARE[1], AIO_LOSS[1]),
            ("high", 0, CTR_TOP3[2], AIO_SHARE[0], AIO_LOSS[0])):
        vol = per_page_volume(kd20, alloc, rank)
        per_row = (vol["head_volume"] / click_rows * TAIL_MULT) if click_rows else 0
        ctr_blend = P_TOP3 * ctr + P_4_10 * (ctr / 4) + P_11_20 * (ctr / 20)
        raw = per_row * ctr_blend * mature
        haircut = 1 - share * loss
        out["scenarios"][name] = {
            "selection_rank": rank, "volume": vol,
            "head_volume": vol["head_volume"], "addressable_per_row": round(per_row),
            "ctr_top3": ctr, "aio_share": share, "aio_loss": loss,
            "aio_multiplier": round(haircut, 3),
            "campaign_raw": round(raw),
            "campaign_after_aio": round(raw * haircut),
            "legacy": LEGACY_HUMAN_CLICKS,
            "total": round(raw * haircut) + LEGACY_HUMAN_CLICKS,
        }
        # The prior derivation varied selection and CTR together and held the AIO haircut
        # at one value. Reproducing that here is the only way the two bands are comparable;
        # compounding all three axes at their extremes gives a mathematically correct range
        # that is far too wide to decide anything with.
        central_haircut = 1 - AIO_SHARE[1] * AIO_LOSS[1]
        out["comparable"][name] = round(raw * central_haircut) + LEGACY_HUMAN_CLICKS
    return out


def build(rows: int, c3_share: float, today: dt.date) -> dict:
    kd20 = universe_kd20()
    primary = band(kd20, rows, c3_share)
    sensitivity = {f"{int(s*100)}%": band(kd20, rows, s)["comparable"]["mid"]
                   for s in (0.40, 0.55, 0.70)}
    outer_lo = primary["scenarios"]["low"]["total"]
    outer_hi = primary["scenarios"]["high"]["total"]
    comp = primary["comparable"]
    lo, mid, hi = comp["low"], comp["mid"], comp["high"]
    prior_central = round(sum(PRIOR_BAND) / 2)
    # Direction is judged on the central estimate, not on whether the ranges overlap. Two
    # ranges can overlap while the central estimate halves, and the central is what anyone
    # actually plans against.
    change = (mid - prior_central) / prior_central
    return {
        "generated": today.isoformat(),
        "days_to_day_90": (DAY_90 - today).days,
        "rows": rows, "c3_share": c3_share,
        "prior_band": PRIOR_BAND, "prior_rows": PRIOR_ROWS,
        "prior_central": prior_central,
        "primary": primary,
        "sensitivity_to_mix": sensitivity,
        "new_band": (lo, hi), "new_central": mid,
        "outer_bounds": (outer_lo, outer_hi),
        "central_change_pct": round(100 * change),
        # Decompose the band's width. The AIO term is the one that became untrustworthy,
        # but selection quality and CTR are what actually make the range wide, and saying
        # otherwise would point at the wrong fix.
        "width_selection_ctr": (primary["scenarios"]["high"]["campaign_raw"]
                                / primary["scenarios"]["low"]["campaign_raw"]
                                if primary["scenarios"]["low"]["campaign_raw"] else 0),
        "width_aio": (primary["scenarios"]["high"]["aio_multiplier"]
                      / primary["scenarios"]["low"]["aio_multiplier"]),
        "direction": ("down" if change <= -0.10 else
                      "up" if change >= 0.10 else "broadly unchanged"),
    }


def render(d: dict) -> str:
    p = d["primary"]
    lo, hi = d["new_band"]
    plo, phi = d["prior_band"]
    L = [f"\n## {d['generated']} — day-90 band re-derived\n"]
    olo, ohi = d["outer_bounds"]
    L.append(f"**Prior: {plo}–{phi:,} human non-brand clicks/month, central "
             f"{d['prior_central']}, on {d['prior_rows']} rows and a tools-led plan.**\n")
    L.append(f"**Re-derived on {d['rows']} rows: {lo}–{hi:,}, central {d['new_central']}. "
             f"The central estimate moves {d['central_change_pct']:+d}% — "
             f"{d['direction'].upper()}.**\n")
    L.append(f"That band holds the AI Overview haircut at one value, which is what the prior "
             f"derivation did, so the two are comparable. Letting the haircut move across "
             f"its own now-untrustworthy range widens the outer bounds to **{olo}–{ohi:,}**, "
             f"and that widening is the real news.\n")
    L.append("Re-derived because the premise changed, not because the old arithmetic was "
             "wrong. Do not compare a number from this section against a band quoted "
             "before today.\n")

    L.append("### Why it moved\n")
    L.append("| Input | Was | Now | Effect |")
    L.append("|---|---|---|---|")
    L.append(f"| Rows remaining | {d['prior_rows']} | {d['rows']} | "
             f"mature-equivalents {mature_equivalents(d['prior_rows']):.1f} → "
             f"{p['mature_equivalents']} — **down** |")
    L.append("| Protected tool subset | assumed to exist | **does not** — 3 of 6 live "
             "build-a-tool SERPs carry an AI Overview | **down** |")
    L.append("| AI Overview haircut | point estimate ×0.828 from tool feature flags | "
             f"range ×{p['scenarios']['high']['aio_multiplier']} to "
             f"×{p['scenarios']['low']['aio_multiplier']}, flags verified wrong on 3 of 4 "
             "rows in both directions | **wider, not just lower** |")
    L.append("| Tool rows' click contribution | counted | zero by design — tools are "
             "measured on referring domains now | **down** |")
    L.append(f"| Legacy term | 15–40 clicks/month, **sitewide including brand** | "
             f"{LEGACY_HUMAN_CLICKS} — the measured human non-brand rate | **down, and "
             f"now in the right units** |")
    L.append(f"| Cluster mix | spread across 7 | cluster 3 at "
             f"{int(d['c3_share']*100)}% of rows | **up** — its KD≤20 keywords are larger |")

    L.append("\n### The arithmetic\n")
    L.append(f"Rows allocated: " + ", ".join(
        f"cluster {c} = {n}" for c, n in sorted(p["allocation"].items())) + ".\n")
    midv = p["scenarios"]["mid"]
    L.append("Central scenario, which assumes the calendar hits the *second*-best slice of "
             "each cluster's pool rather than the very best — perfect selection is what the "
             "high scenario models:\n")
    L.append("| Cluster | Rows | KD≤20 pool | Slice taken | Head vol | Mean/row | Short by |")
    L.append("|---:|---:|---:|---|---:|---:|---:|")
    for c, v in sorted(midv["volume"]["per_cluster"].items()):
        L.append(f"| {c} | {v['rows']} | {v['pool']} | {v['slice']} | {v['head_volume']} | "
                 f"{v['mean_per_row']} | {v['short_by']} |")
    L.append(f"\nHead volume {midv['head_volume']:,}/mo across {d['rows']} rows, "
             f"×{TAIL_MULT} tail = **{midv['addressable_per_row']}/mo addressable per row**. "
             f"{d['rows']} rows over 90 days buys **{p['mature_equivalents']} "
             f"mature-equivalent pages** at maturities "
             f"{'/'.join(str(m) for m in COHORT_MATURITY)}.\n")
    L.append("| Scenario | Selection | Vol/row | Top-3 CTR | AIO share | AIO loss | "
             "Multiplier | Raw | After AIO | + legacy | **Total** |")
    L.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for name in ("low", "mid", "high"):
        sc = p["scenarios"][name]
        label = {0: "best slice", 1: "2nd slice", 2: "3rd slice"}[sc["selection_rank"]]
        L.append(f"| {name} | {label} | {sc['addressable_per_row']} | "
                 f"{100*sc['ctr_top3']:.0f}% | {100*sc['aio_share']:.0f}% | "
                 f"{100*sc['aio_loss']:.0f}% | ×{sc['aio_multiplier']} | "
                 f"{sc['campaign_raw']} | {sc['campaign_after_aio']} | {sc['legacy']} | "
                 f"**{sc['total']}** |")

    L.append("\n### How much the answer depends on a decision nobody has written down\n")
    L.append("The live queue is on the Hermes box and not readable from here, so the "
             "cluster-3 share of the sixty rows is a parameter. Central scenario at each:\n")
    L.append("| Cluster 3 share of rows | Central band |")
    L.append("|---|---:|")
    for k, v in d["sensitivity_to_mix"].items():
        L.append(f"| {k} | {v} |")

    L.append(f"\n### {d['verdict_heading']}\n")
    L.append(d["verdict"])
    return "\n".join(L) + "\n"


def verdict(d: dict) -> tuple[str, str]:
    lo, hi = d["new_band"]
    plo, phi = d["prior_band"]
    spread = hi / lo if lo else float("inf")
    direction = d["direction"]
    # The direction is read off the arithmetic, never asserted. A first run of this tool
    # printed the word "Down" above a band that had gone up, because the prose was written
    # before the numbers were.
    word = {"down": "**Down.**", "up": "**Up, against expectation.**",
            "overlapping": "**Overlapping the old band rather than clearly moving.**"}[direction]
    heading = {
        "down": "The band moves down, and it should now carry its uncertainty on its face",
        "up": "The band moves up, which was not the expectation — read why before using it",
        "overlapping": "The band overlaps the old one; the spread is the finding",
    }[direction]
    if direction == "down":
        why = ("Every input that moved except the cluster mix moved it down, and the mix "
               "cannot lift it far because cluster 3's larger keywords are also its harder "
               "and most AI-Overview-exposed ones.")
    elif direction == "up":
        why = ("The expectation was down and the arithmetic disagrees, so the reason matters "
               "more than the number. Weighting toward cluster 3 raises addressable volume "
               "per row — its KD≤20 keywords are roughly twice the size of cluster 1's — and "
               "that outweighs the smaller row count, the zeroed legacy term and the wider "
               "haircut. Treat this as a statement about cluster 3's keyword sizes, not as "
               "good news: the floor still rests on a CTR this site has never achieved and "
               "on a click rate that has been zero for ten months.")
    else:
        why = ("The inputs moved in both directions and roughly cancelled, which is why the "
               "spread rather than the midpoint is the honest output.")
    olo, ohi = d["outer_bounds"]
    body = (
        f"{word} The central estimate goes {d['prior_central']} → **{d['new_central']}**, "
        f"{d['central_change_pct']:+d}%, and the floor {plo} → **{lo}**, with "
        f"{d['days_to_day_90']} days to {DAY_90.isoformat()}. {why}\n\n"
        f"**But a three-point band is now false precision, and I would not report one.** "
        f"The spread between the low and high scenarios is {spread:.1f}x on the same "
        f"calendar, and it is worth being precise about where that width comes from, "
        f"because it points at different remedies:\n\n"
        f"- **All {spread:.1f}x of it is selection quality and CTR.** The comparable band "
        f"holds the haircut fixed, so its entire width is those two axes, and neither has "
        f"been demonstrated on this site. The measured top-3 CTR is "
        f"4.1%, well under the 8–16% the scenarios assume, and human clicks have been zero "
        f"for ten months. This is the dominant uncertainty.\n"
        f"- **The AI Overview haircut adds a further {d['width_aio']:.2f}x on top**, taking "
        f"the outer bounds to {olo}–{ohi:,}. It is the input that became *untrustworthy* — flags "
        f"wrong on three of four rows in both directions, seven SERPs read live — but it "
        f"was never the widest term. Correcting it moved the central estimate; it did not "
        f"create the range.\n\n"
        f"So reading more SERPs live is worth doing and will **not** narrow this materially. "
        f"What narrows it is shipping pages and measuring what they actually reach, which "
        f"`tools/gsc_attribution.py` now records per page from its publish date.\n\n"
        f"**What I would report instead of a band.** Two numbers with different standing, "
        f"never averaged:\n\n"
        f"- **MEASURED, and the only one that decides anything: 0 human non-brand clicks "
        f"per month.** Zero for ten consecutive months. Every projection here is an "
        f"argument about when this stops being zero, and none of them is evidence that it "
        f"will.\n"
        f"- **RANGE, ESTIMATE: {lo}–{hi:,} human non-brand clicks/month by day 90**, "
        f"central {d['new_central']}, on the stated inputs. Quote the range or the central "
        f"with the range attached — never the central alone.\n\n"
        f"Against the {TARGET_MONTHLY:,}/month target: the re-derived ceiling of {hi} is "
        f"{TARGET_MONTHLY/hi:.0f}x short. The target was already unreachable at "
        f"{phi:,}; it is further out now, and nothing in this re-derivation changes the "
        f"conclusion that it cannot be reached by publishing inside 90 days.")
    return heading, body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", type=int, default=ROWS_REMAINING)
    ap.add_argument("--c3-share", type=float, default=0.55)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    if not UNIVERSE.exists() or not SWEEP.exists():
        print(f"Cannot re-derive: missing {UNIVERSE.name} or {SWEEP.name}. "
              "The band depends on the keyword universe and the contamination sweep; "
              "without them there is no derivation, and a number would be invented.")
        return 2

    data = build(args.rows, args.c3_share, dt.date.today())
    data["verdict_heading"], data["verdict"] = verdict(data)
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
            "# Day-90 band derivations\n\n"
            "Appended by `tools/gsc_band.py`, one dated section per re-derivation. The band\n"
            "has been restated three times because premises under it changed, so each entry\n"
            "records the inputs that moved and why. **Never compare a band figure against a\n"
            "number quoted before its own date.**\n\n"
            "All figures are human non-brand clicks per month, the same quantity the weekly\n"
            "scoreboard measures. An earlier derivation mixed in sitewide clicks including\n"
            "brand, which made the band and its own yardstick different quantities.\n",
            encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
