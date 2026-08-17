# Weekly scoreboard

Maintained by `tools/gsc_scoreboard.py`, one authoritative section per date. The five
figures the campaign is judged on and nothing else — the other Search Console
tools answer everything wider.

Read the labels. **MEASURED** is a complete sitewide total. **FLOOR** comes
from the query dimension, which withholds low-volume queries, so the truth is
higher by an unknown amount. **ESTIMATE** is bounded in neither direction.
"Human" means non-brand and non-machine: brand is removed first, then pasted
blobs, then machine query fan-out. Where a number cannot be computed honestly
it says so — there are no placeholders here.

## 2026-08-17 — weekly scoreboard

This week 2026-08-08 to 2026-08-14, against last week 2026-08-01 to 2026-08-07. Windows end 3 days back because Search Console lags about that long.

Labels: **MEASURED** is a complete sitewide total. **FLOOR** comes from the query dimension, which withholds low-volume queries, so the real figure is higher by an unknown amount. **ESTIMATE** is bounded in neither direction. "Human" means non-brand and non-machine.

### 1. Human non-brand clicks — the number the campaign lives on

| | This week | Last week | Trailing 28d | Prior 28d |
|---|---:|---:|---:|---:|
| **Human clicks** (ESTIMATE) | **0** | 0 | 0 | 0 |
| Human impressions (ESTIMATE) | 31 | 15 | 97 | 146 |
| Human avg position | 66.3 | 37.0 | 39.4 | 52.5 |
| Brand clicks, for contrast (FLOOR) | 3 | 0 | 4 | 7 |
| Machine fan-out impressions removed (FLOOR) | 64 | 56 | 149 | 91 |

Week over week: **zero to zero.** No percentage is quoted because there is nothing to compare — this is a flat line at zero, not a decline.

The human average position moved 37.0 to 66.3, and that is **composition, not movement**: the two weeks share 0 queries out of 32 and 28 named. A different set of queries produces a different average. This site has already been misread once this way — an average position rising 23.1 to 7.2 in 2025 was the deep-position tail vanishing, not a gain.

Against the day-90 band of **149–1,525 human clicks/month** (central 413): the trailing 28 days produced **0**. That is below the floor, and not marginally: the floor assumes the campaign produces human clicks at all.

**The band was re-derived on 2026-08-17** and replaced 306–1,176. The premise under the old one was a tools-led calendar in a protected niche, and live SERP reads found the protected niche does not exist. Tools are now measured on referring domains rather than sessions, sixty rows remain rather than seventy-one, and the old legacy term added sitewide clicks including brand to a band judged on human non-brand clicks. The central estimate moved 741 → 413. **Do not compare this week's figure against a band quoted before 2026-08-17** — see `planning/band.md`.

### 2. Distance to 10,000/month

**Not computable as a multiple.** Human non-brand clicks over the trailing 28 days are zero, and a multiple of zero is not a number. Stated plainly rather than shown as infinity or a placeholder: the campaign has produced no human non-brand click in this window.

### 3. Top 20 human queries — what entered and what left

This week holds 9 human queries and last week 8, both under 20, so this is the complete list rather than a ranking. Nothing is being cut off.

- **Entered (9, 31 impressions):** `code documentation template` (19), `coding documentation template` (3), `technical tutorial` (3), `ans` (1), `different types of documentation` (1), `how to write tutorial` (1), `rag score` (1), `technical documentation` (1), `technical tutorials` (1)
- **Left (8, 15 impressions):** `seo documentation` (5), `how do you handle errors when ai agents make mistakes in production?` (4), `developer onboarding documentation` (1), `hybrid retrieval combining bm25 and dense embeddings improves performance beir benchmark` (1), `seo requirements document` (1), `stripe tech blog` (1), `uv resolution-markers` (1), `why do i have to keep re-explaining my codebase to my ai agent` (1)
- **Held (0):** none

71% of the queries on both sides carry one impression or fewer, so near-total turnover here is sampling noise rather than movement. Do not read `Held (0)` as a collapse.

| Human query this week | Impr | Clicks | Pos |
|---|---:|---:|---:|
| code documentation template | 19 | 0 | 74.5 |
| coding documentation template | 3 | 0 | 79.3 |
| technical tutorial | 3 | 0 | 10 |
| ans | 1 | 0 | 7 |
| different types of documentation | 1 | 0 | 90 |
| how to write tutorial | 1 | 0 | 42 |
| rag score | 1 | 0 | 100 |
| technical documentation | 1 | 0 | 96 |
| technical tutorials | 1 | 0 | 36 |

### 4. Human impressions per cluster

Joining the page and query dimensions costs coverage: 124 of 496 sitewide impressions survive the join (25.0%). **This is the hardest floor in the report** — treat a zero as "nothing named", not as proof of nothing.

| # | Cluster | Live surfaces | Human impr | Human clicks | Pages named |
|---:|---|---:|---:|---:|---:|
| 1 | Technical documentation & docs ops | 23 | 29 | 0 | 3 |
| 2 | Developer experience & DevRel | 7 | 0 | 0 | 0 |
| 3 | AI agents, memory, RAG, inference | 57 | 1 | 0 | 1 |
| 4 | AI Overviews & AI-search citation | 8 | 0 | 0 | 0 |
| 5 | Distribution: Reddit, forums, communities, events | 0 | 0 | 0 | 0 |
| — | Pages in no cluster | — | 1 | 0 | 1 |

**Shipped but earning nothing named:** cluster 2 (7 live surfaces), cluster 4 (8 live surfaces). Something has been tried here and has not landed yet.

**Nothing live yet:** cluster 5. A zero here means nothing has been published, not that it failed.

### 5. Does the trajectory reach 10,000/month by 2026-11-15?

No. Human non-brand clicks over the trailing 28 days are zero, so there is no rate to extrapolate and no multiple to quote: 10,000 from zero is not a multiple, it is a standing start with 90 days left. Reaching even the band's floor of 149/month requires a change in kind rather than degree, and reaching 10,000 is 6.6x beyond the band's own ceiling of 1,525, so the target was never reachable by publishing inside 90 days.
