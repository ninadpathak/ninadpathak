#!/usr/bin/env python3
"""Derive deliverables from the cleaned universe: cluster table, top-15 by
volume x winnability, the tool-led / calculation-led set, and the day-90 click
band with its arithmetic exposed.

Deliberately does NOT use Ahrefs `traffic_potential`. That field reports the
traffic of the #1 ranking *page*, so navigational queries like "nfl streams
subreddit" score 481,000 because the #1 page is reddit.com. It measures the
incumbent, not the opportunity.
"""
import json
import os
import re
import statistics as st

CACHE = os.path.dirname(os.path.abspath(__file__))
U = json.load(open(os.path.join(CACHE, "DERIVED-full-universe.json")))

NAMES = {1: "Technical documentation & docs ops", 2: "Developer experience & DevRel",
         3: "AI agents, memory, RAG, inference", 4: "AI Overviews & AI-search citation",
         5: "Reddit marketing", 6: "Forums & community building",
         7: "Technical & community events"}

# --------------------------------------------------------------- winnability
# ninadpathak.com is DR 26 (Ahrefs free endpoint, 2026-08-17) - modest, not zero.
# P(reaching each position band within ~90 days of publish, well-executed page).
BANDS = [(10, {"top3": .30, "p4_10": .35, "p11_20": .20}),
         (20, {"top3": .15, "p4_10": .30, "p11_20": .25}),
         (30, {"top3": .06, "p4_10": .18, "p11_20": .25}),
         (45, {"top3": .02, "p4_10": .08, "p11_20": .18}),
         (100, {"top3": .005, "p4_10": .03, "p11_20": .10})]


def probs(kd):
    kd = 45 if kd is None else kd
    for cap, p in BANDS:
        if kd <= cap:
            return p
    return BANDS[-1][1]


def winnability(kd):
    p = probs(kd)
    return p["top3"] + p["p4_10"]


TOOL = re.compile(r"\b(checker|validator|generator|calculator|analyzer|converter|"
                  r"linter|scanner|tester|audit|template|tools?)\b", re.I)
CALC = re.compile(r"\b(calculator|roi|kpis?|metrics|budget|pricing|cost|statistics|"
                  r"benchmark|score)\b", re.I)

out = {}

# --------------------------------------------------------------- cluster table
clusters = []
for cid in sorted(NAMES):
    f = [r for r in U if r["cluster"] == cid]
    k20 = [r for r in f if r.get("difficulty") is not None and r["difficulty"] <= 20]
    clusters.append({
        "cluster": cid, "name": NAMES[cid], "kws": len(f),
        "volume": sum(r.get("volume") or 0 for r in f),
        "kd20_kws": len(k20), "kd20_vol": sum(r.get("volume") or 0 for r in k20),
        "aio": sum(1 for r in f if "ai_overview" in (r.get("serp_features") or [])),
    })
out["clusters"] = clusters

# --------------------------------------------------------------- top 15
scored = sorted(({
    "keyword": r["keyword"], "cluster": r["cluster"], "volume": r.get("volume") or 0,
    "kd": r.get("difficulty"), "winnability": round(winnability(r.get("difficulty")), 3),
    "score": round((r.get("volume") or 0) * winnability(r.get("difficulty"))),
    "intent": ",".join(k for k, v in (r.get("intents") or {}).items() if v) or "-",
    "aio": "ai_overview" in (r.get("serp_features") or []),
} for r in U), key=lambda x: -x["score"])
out["top15"] = scored[:15]

# --------------------------------------------------------------- tool-led
tools = sorted(({
    "keyword": r["keyword"], "cluster": r["cluster"], "volume": r.get("volume") or 0,
    "kd": r.get("difficulty"), "job": TOOL.search(r["keyword"]).group(1).lower(),
    "calc": bool(CALC.search(r["keyword"])),
    "aio": "ai_overview" in (r.get("serp_features") or []),
} for r in U if TOOL.search(r["keyword"])), key=lambda x: -x["volume"])
out["tools"] = tools

# --------------------------------------------------------------- click band
# Only the 71 NEW pages are modelled. The 15 pre-campaign pages are already live
# and measurably produce ~15 clicks/mo in total (GSC, date dimension, Jun-Aug
# 2026), so they enter as a measured legacy term rather than a modelled one.
PLANNED = 71
COHORTS = [("published day 1-30",  24, 0.55),   # age 60-90d at day 90
           ("published day 31-60", 24, 0.30),   # age 30-60d
           ("published day 61-90", 23, 0.08)]   # age 0-30d
MATURE_EQUIV = sum(n * m for _, n, m in COHORTS)

k20 = sorted([r for r in U if r.get("difficulty") is not None and r["difficulty"] <= 20],
             key=lambda r: -(r.get("volume") or 0))
TAIL_MULT = 2.5   # head term plus the long tail one good page picks up

# Scenarios vary keyword SELECTION as well as CTR - selection is the bigger lever
# and the prior band varied neither.
# Anchors chosen from the sensitivity grid. A directed campaign with briefs picks
# from roughly the best 150-400 of the KD<=20 pool once topic distinctness and
# cluster balance are respected - not the best 71 (assumes perfect selection) and
# not the median (assumes none).
SEL = {
    "low":  ("mean of best 400 KD<=20", st.mean([r["volume"] for r in k20[:400]])),
    "mid":  ("mean of best 250 KD<=20", st.mean([r["volume"] for r in k20[:250]])),
    "high": ("mean of best 150 KD<=20", st.mean([r["volume"] for r in k20[:150]])),
}
# Top-3 CTR. The site's own measured 4.1% is the documented floor but sits on
# legacy off-niche queries; 20% is a clean-SERP ceiling rarely reached when 49%
# of these SERPs carry an AI Overview.
CTR = {"low":  {"top3": .08, "p4_10": .020, "p11_20": .004},
       "mid":  {"top3": .12, "p4_10": .030, "p11_20": .006},
       "high": {"top3": .16, "p4_10": .040, "p11_20": .008}}
LEGACY = {"low": 15, "mid": 25, "high": 40}
AIO_SHARE = sum(1 for r in U if "ai_overview" in (r.get("serp_features") or [])) / len(U)
AIO_HAIRCUT = 0.35

P = probs(20)
band = {}
for label in ("low", "mid", "high"):
    seln, headvol = SEL[label]
    page_vol = headvol * TAIL_MULT
    ctr = CTR[label]
    per_page_full = page_vol * (P["top3"] * ctr["top3"]
                                + P["p4_10"] * ctr["p4_10"]
                                + P["p11_20"] * ctr["p11_20"])
    detail, total = [], 0.0
    for cname, n, mat in COHORTS:
        sub = per_page_full * mat * n
        detail.append({"cohort": cname, "pages": n, "maturity": mat,
                       "subtotal": round(sub)})
        total += sub
    after_aio = total * (1 - AIO_SHARE * AIO_HAIRCUT)
    band[label] = {"selection": seln, "head_vol_per_page": round(headvol),
                   "page_vol": round(page_vol), "per_page_full": round(per_page_full, 2),
                   "detail": detail, "campaign_raw": round(total),
                   "campaign_after_aio": round(after_aio), "legacy": LEGACY[label],
                   "site_total": round(after_aio + LEGACY[label])}

out["band"] = {
    "dr": 26, "new_pages": PLANNED, "mature_equiv": round(MATURE_EQUIV, 1),
    "tail_mult": TAIL_MULT, "aio_share": round(AIO_SHARE, 3),
    "aio_haircut": AIO_HAIRCUT, "probs_kd20": P, "ctr": CTR, "selection": SEL,
    "cohorts": COHORTS, "legacy": LEGACY, "result": band,
}
json.dump(out, open(os.path.join(CACHE, "DERIVED-analysis.json"), "w"), indent=1)

# --------------------------------------------------------------- print
print(f"{PLANNED} new pages -> {MATURE_EQUIV:.1f} mature-equivalents by day 90 "
      f"| AIO share {AIO_SHARE:.1%}")
print("\nTOP 15 by volume x winnability")
for i, t in enumerate(out["top15"], 1):
    print(f"{i:>2}. {t['keyword'][:44]:44} c{t['cluster']} v={t['volume']:>5} "
          f"KD={str(t['kd']):>4} w={t['winnability']} score={t['score']:>4} "
          f"aio={'Y' if t['aio'] else 'n'}")
print(f"\nTOOL-LED: {len(tools)} kws, {sum(t['volume'] for t in tools)} vol/mo "
      f"({sum(1 for t in tools if t['calc'])} calculation-led)")
print("\nCLICK BAND")
for label in ("low", "mid", "high"):
    b = band[label]
    print(f"  [{label:4}] {b['selection']:24} head={b['head_vol_per_page']:>4}/mo "
          f"x{TAIL_MULT}={b['page_vol']:>4}  c/page@full={b['per_page_full']:>6}")
    print(f"         subtotals {[d['subtotal'] for d in b['detail']]} "
          f"raw={b['campaign_raw']} afterAIO={b['campaign_after_aio']} "
          f"+legacy {b['legacy']} => {b['site_total']}/mo")
print(f"\nBAND: {band['low']['site_total']} - {band['high']['site_total']} clicks/mo "
      f"(mid {band['mid']['site_total']}) at 2026-11-15")
