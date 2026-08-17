# Day-90 band derivations

Appended by `tools/gsc_band.py`, one dated section per re-derivation. The band
has been restated three times because premises under it changed, so each entry
records the inputs that moved and why. **Never compare a band figure against a
number quoted before its own date.**

All figures are human non-brand clicks per month, the same quantity the weekly
scoreboard measures. An earlier derivation mixed in sitewide clicks including
brand, which made the band and its own yardstick different quantities.

## 2026-08-17 — day-90 band re-derived

**Prior: 306–1,176 human non-brand clicks/month, central 741, on 71 rows and a tools-led plan.**

**Re-derived on 60 rows: 149–1,525, central 413. The central estimate moves -44% — DOWN.**

That band holds the AI Overview haircut at one value, which is what the prior derivation did, so the two are comparable. Letting the haircut move across its own now-untrustworthy range widens the outer bounds to **128–1,687**, and that widening is the real news.

Re-derived because the premise changed, not because the old arithmetic was wrong. Do not compare a number from this section against a band quoted before today.

### Why it moved

| Input | Was | Now | Effect |
|---|---|---|---|
| Rows remaining | 71 | 60 | mature-equivalents 22.0 → 18.6 — **down** |
| Protected tool subset | assumed to exist | **does not** — 3 of 6 live build-a-tool SERPs carry an AI Overview | **down** |
| AI Overview haircut | point estimate ×0.828 from tool feature flags | range ×0.912 to ×0.708, flags verified wrong on 3 of 4 rows in both directions | **wider, not just lower** |
| Tool rows' click contribution | counted | zero by design — tools are measured on referring domains now | **down** |
| Legacy term | 15–40 clicks/month, **sitewide including brand** | 0 — the measured human non-brand rate | **down, and now in the right units** |
| Cluster mix | spread across 7 | cluster 3 at 55% of rows | **up** — its KD≤20 keywords are larger |

### The arithmetic

Rows allocated: cluster 1 = 11, cluster 2 = 3, cluster 3 = 33, cluster 4 = 5, cluster 5 = 8.

Central scenario, which assumes the calendar hits the *second*-best slice of each cluster's pool rather than the very best — perfect selection is what the high scenario models:

| Cluster | Rows | KD≤20 pool | Slice taken | Head vol | Mean/row | Short by |
|---:|---:|---:|---|---:|---:|---:|
| 1 | 11 | 220 | 12-22 | 3612 | 328 | 0 |
| 2 | 3 | 54 | 4-6 | 495 | 165 | 0 |
| 3 | 33 | 217 | 34-66 | 11972 | 363 | 0 |
| 4 | 5 | 42 | 6-10 | 2280 | 456 | 0 |
| 5 | 8 | 285 | 9-16 | 4289 | 536 | 0 |

Head volume 22,648/mo across 60 rows, ×2.5 tail = **944/mo addressable per row**. 60 rows over 90 days buys **18.6 mature-equivalent pages** at maturities 0.55/0.3/0.08.

| Scenario | Selection | Vol/row | Top-3 CTR | AIO share | AIO loss | Multiplier | Raw | After AIO | + legacy | **Total** |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| low | 3rd slice | 510 | 8% | 65% | 45% | ×0.708 | 180 | 128 | 0 | **128** |
| mid | 2nd slice | 944 | 12% | 50% | 35% | ×0.825 | 500 | 413 | 0 | **413** |
| high | best slice | 2616 | 16% | 35% | 25% | ×0.912 | 1849 | 1687 | 0 | **1687** |

### How much the answer depends on a decision nobody has written down

The live queue is on the Hermes box and not readable from here, so the cluster-3 share of the sixty rows is a parameter. Central scenario at each:

| Cluster 3 share of rows | Central band |
|---|---:|
| 40% | 435 |
| 55% | 413 |
| 70% | 366 |

### The band moves down, and it should now carry its uncertainty on its face

**Down.** The central estimate goes 741 → **413**, -44%, and the floor 306 → **149**, with 90 days to 2026-11-15. Every input that moved except the cluster mix moved it down, and the mix cannot lift it far because cluster 3's larger keywords are also its harder and most AI-Overview-exposed ones.

**But a three-point band is now false precision, and I would not report one.** The spread between the low and high scenarios is 10.2x on the same calendar, and it is worth being precise about where that width comes from, because it points at different remedies:

- **All 10.2x of it is selection quality and CTR.** The comparable band holds the haircut fixed, so its entire width is those two axes, and neither has been demonstrated on this site. The measured top-3 CTR is 4.1%, well under the 8–16% the scenarios assume, and human clicks have been zero for ten months. This is the dominant uncertainty.
- **The AI Overview haircut adds a further 1.29x on top**, taking the outer bounds to 128–1,687. It is the input that became *untrustworthy* — flags wrong on three of four rows in both directions, seven SERPs read live — but it was never the widest term. Correcting it moved the central estimate; it did not create the range.

So reading more SERPs live is worth doing and will **not** narrow this materially. What narrows it is shipping pages and measuring what they actually reach, which `tools/gsc_attribution.py` now records per page from its publish date.

**What I would report instead of a band.** Two numbers with different standing, never averaged:

- **MEASURED, and the only one that decides anything: 0 human non-brand clicks per month.** Zero for ten consecutive months. Every projection here is an argument about when this stops being zero, and none of them is evidence that it will.
- **RANGE, ESTIMATE: 149–1,525 human non-brand clicks/month by day 90**, central 413, on the stated inputs. Quote the range or the central with the range attached — never the central alone.

Against the 10,000/month target: the re-derived ceiling of 1525 is 7x short. The target was already unreachable at 1,176; it is further out now, and nothing in this re-derivation changes the conclusion that it cannot be reached by publishing inside 90 days.
