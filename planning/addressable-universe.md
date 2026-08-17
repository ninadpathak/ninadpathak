# Addressable search universe — full niche

**Date:** 2026-08-17 · **Agent:** `seo-analytics` · **Branch:** `seo/analytics`
**Supersedes:** the documentation-only figure of 68,870 searches/month across 350 keywords.

Recomputed across the seven clusters settled in `CHARTER.md` §2c-bis. Cluster 1 reuses the
banked pull and was not re-bought. Clusters 2–7 cost **7 paid Ahrefs calls, 25,540 units**
(budget was 8 calls). Raw JSON in `planning/research-cache/`, every call logged in
`CALL-LOG.md`.

---

## 1. Headline

| | Documentation only (prior) | Full niche (this pass) |
|---|---:|---:|
| Keywords | 350 | **1,129** |
| Volume/month | 68,870 | **336,180** |
| KD≤20 keywords | 248 | **818** |
| KD≤20 volume/month | 36,870 | **184,160** |

The universe is **4.9× larger** than the documentation-only denominator.

**It does not matter nearly as much as that multiple suggests.** Addressable volume was
never the binding constraint on day-90 traffic. Publishing throughput and ranking maturity
are. See §6 — the revised click band is *lower* than the prior one despite a 5× larger
universe, because the prior band was too optimistic about how fast new pages rank.

---

## 2. Volume per cluster

Universe defined as: US, `volume ≥ 30`, `KD ≤ 45`, off-niche terms removed (§3).

| # | Cluster | Keywords | Volume/mo | KD≤20 kws | KD≤20 vol/mo | KD≤20 share | AIO SERPs |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Technical documentation & docs ops | 322 | 63,730 | 220 | 31,730 | 50% | 111 |
| 2 | Developer experience & DevRel | 56 | 7,930 | 54 | 7,190 | 91% | 26 |
| 3 | AI agents, memory, RAG, inference | 347 | 150,140 | 217 | 60,650 | 40% | 226 |
| 4 | AI Overviews & AI-search citation | 58 | 23,880 | 42 | 11,890 | 50% | 40 |
| 5 | Reddit marketing | 78 | 33,360 | 70 | 28,970 | 87% | 38 |
| 6 | Forums & community building | 94 | 24,140 | 82 | 18,440 | 76% | 51 |
| 7 | Technical & community events | 174 | 33,000 | 133 | 25,290 | 77% | 64 |
| | **Total** | **1,129** | **336,180** | **818** | **184,160** | **55%** | **556** |

Notes that change how this table should be read:

- **Cluster 3 is the whole story on volume** — 45% of the universe. The charter's claim that
  the retired AI-engineering cluster is "10 to 50× documentation" is not supported at
  10–50×, but it is genuinely **2.4× documentation** and it is the largest single cluster.
- **Cluster 3 is also the hardest.** Only 40% of its volume is KD≤20, the lowest share of any
  cluster, and 65% of its keywords carry an AI Overview. High volume, high friction.
- **Clusters 2, 5, 6, 7 are the winnable ones** — 76–91% of their volume sits at KD≤20.
  Cluster 2 (DevEx/DevRel) is tiny at 7,930/mo but 91% winnable.
- **Clusters 5, 6 and 7 hit the 250-row API limit**, so their true volumes are larger than
  recorded. Treat those three as floors, not measurements.
- **49.2% of the whole universe shows an AI Overview.** That is the single most important
  number in this table and it is applied as a click haircut in §6.

---

## 3. Cleaning — what was removed and why

Ahrefs `terms` mode matches on token presence, not meaning. Several clusters returned large
volumes of a *different industry* that happens to share vocabulary. Counting those would
have inflated the universe. Rules are in `_clean.py`, dropped keywords in
`DERIVED-cleaning-audit.json`.

| # | Cluster | Raw kws | Raw vol | Kept | Clean vol | Removed |
|---:|---|---:|---:|---:|---:|---|
| 1 | Documentation | 350 | 68,870 | 322 | 63,730 | Nursing/medical charting, one junk term |
| 2 | DevEx/DevRel | 67 | 8,680 | 56 | 7,930 | Job/salary queries |
| 3 | AI agents/RAG | 364 | 165,390 | 347 | 150,140 | Design assets, scraped junk, dev-shop procurement |
| 4 | AI Overviews | 62 | 27,030 | 62 | 27,030 | — |
| 5 | Reddit | 250 | 54,060 | 78 | 33,360 | Consumer `<topic> subreddit` navigation |
| 6 | Community | 250 | 58,460 | 94 | 24,140 | HOA property management, community colleges |
| 7 | Events | 250 | 46,920 | 174 | 33,000 | Corporate party planning, university hackathons |

**The banked cluster-1 data was not clean.** The prior pass's `DERIVED-clean-universe.json`
carried a body of *nursing documentation* keywords — `picc line documentation example`,
`unwitnessed fall documentation example`, `wound dressing documentation example`,
`perrla documentation example` and ~24 others — plus `test.com product documentation
features` at 3,000/mo, which is junk. Removing them takes documentation from 68,870 to
**63,730/mo**. The prior figure was overstated by 5,140/mo (7.5%).

Cluster 6 lost 59% of its raw volume, almost all of it HOA and property-management firms
(`vision community management`, `trestle community management`) and community colleges.
Cluster 5 lost 38%, almost all of it consumer subreddit navigation (`nfl subreddit`,
`anime subreddit`) rather than Reddit marketing.

Two judgment calls, recorded so they can be overturned:

1. **Vendor-procurement intent dropped** where Ninad sells nothing — AV production firms in
   cluster 7 (`virtual event production company`), AI dev shops in cluster 3
   (`ai agent development services`). He could rank for these; they convert to nothing.
2. **Market-research online communities (MROC) dropped** from cluster 6. It is a real
   discipline but a separate B2B industry from audience building.

---

## 4. Top 15 by volume × winnability

Winnability = P(reaching top 10 within ~90 days of publishing) for a **DR 26** site
(Ahrefs free endpoint, 2026-08-17 — the site is modest, not zero-authority as assumed).
KD≤10 → 0.65 · KD 11–20 → 0.45 · KD 21–30 → 0.24 · KD 31–45 → 0.10 · KD 46+ → 0.035.
Score = volume × winnability.

| # | Keyword | Cluster | Vol/mo | KD | Winnability | Score | Intent | AI Overview |
|---:|---|---:|---:|---:|---:|---:|---|:---:|
| 1 | reddit ads | 5 | 8,300 | 12 | 0.45 | 3,735 | informational, commercial, branded | **yes** |
| 2 | pinecone vector database | 3 | 4,400 | 8 | 0.65 | 2,860 | informational, commercial, branded | **yes** |
| 3 | subreddit | 5 | 4,700 | 14 | 0.45 | 2,115 | informational | **yes** |
| 4 | how to build an ai agent | 3 | 4,200 | 12 | 0.45 | 1,890 | informational | **yes** |
| 5 | what is a hackathon | 7 | 2,700 | 4 | 0.65 | 1,755 | informational | **yes** |
| 6 | technical documentation | 1 | 3,100 | 12 | 0.45 | 1,395 | informational | **yes** |
| 7 | community management | 6 | 2,600 | 13 | 0.45 | 1,170 | informational, commercial, local | **yes** |
| 8 | what is a vector database | 3 | 11,000 | 39 | 0.10 | 1,100 | informational | **yes** |
| 9 | agentic workflow | 3 | 2,200 | 20 | 0.45 | 990 | informational | **yes** |
| 10 | how to organize a community event | 7 | 1,400 | 3 | 0.65 | 910 | informational | **yes** |
| 11 | community event | 7 | 1,200 | 2 | 0.65 | 780 | informational, local | **yes** |
| 12 | what is an mcp server | 3 | 7,200 | 40 | 0.10 | 720 | informational | **yes** |
| 13 | qdrant vector database | 3 | 1,600 | 11 | 0.45 | 720 | informational, branded | **yes** |
| 14 | top answer engine optimization for ai solutions | 4 | 1,600 | 18 | 0.45 | 720 | informational, commercial | **yes** |
| 15 | chatgpt seo tool | 4 | 1,100 | 4 | 0.65 | 715 | commercial, branded | **yes** |

**All 15 carry an AI Overview.** There is no top-opportunity keyword in this niche where a
plain blue-link SERP is available. Any plan that assumes classic organic CTR on these terms
is wrong before it starts.

Cluster spread of the top 15: cluster 3 ×5, cluster 7 ×3, clusters 4 and 5 ×2 each,
clusters 1 and 6 ×1 each. Cluster 2 (DevEx/DevRel) places nothing — it is winnable but has
no head terms.

Entries 8 and 12 (`what is a vector database` 11,000/mo, `what is an mcp server` 7,200/mo)
score on raw size despite KD 39–40. They are the two biggest prizes in the niche and the
two least likely to be won at DR 26 inside 90 days. Treat them as year-one targets.

---

## 5. Tool-led and calculation-led SERPs

Tools are the campaign's priority lever, and `linter.css` makes a new interactive tool
close to free (per standing order 4). **106 keywords, 20,550 searches/month** carry a
tool-shaped job; 90 of them are KD≤20.

### 5a. Build-an-actual-tool subset — 9 keywords, 1,940/mo

These want software, not an article. This is the buildable list.

| Keyword | Cluster | Vol/mo | KD | Job | AIO |
|---|---:|---:|---:|---|:---:|
| ai overviews checker | 4 | 700 | 0 | checker | no |
| llms.txt generator | 1 | 300 | n/a | generator | no |
| ai documentation generator | 1 | 250 | 37 | generator | no |
| openapi client generator | 1 | 150 | 35 | generator | no |
| openapi documentation generator | 1 | 150 | 23 | generator | no |
| llms.txt checker | 1 | 150 | n/a | checker | no |
| audit documentation software | 1 | 100 | 12 | audit | no |
| llms.txt validator | 1 | 100 | n/a | validator | no |
| audit documentation example | 1 | 40 | 0 | audit | no |

Three observations:

- **`ai overviews checker` — 700/mo at KD 0, no AI Overview on the SERP.** That is the
  single cleanest opportunity found anywhere in this analysis. Zero difficulty, meaningful
  volume, no AIO eating the click, and it is a tool Ninad is well placed to build.
- **The llms.txt tool family (generator + checker + validator, 550/mo combined) is
  half-built already** — an llms.txt generator exists at `templates/llms_txt_generator.html`.
  Splitting it into three addressable pages is plumbing, not new engineering.
- **Not one of these nine SERPs shows an AI Overview.** Tool queries are structurally
  protected from the thing suppressing clicks everywhere else in this niche. That is the
  strongest argument in this document for weighting the campaign toward tools.

### 5b. Tool-and-template listicle subset — 97 keywords, 18,610/mo

These want a comparison page or a downloadable, not software. Cluster 1 dominates with 83
of the 97. Highest volume: `ai search optimization tools` (1,900, KD 45),
`generative engine optimization tools` (1,300, KD 38), `chatgpt seo tool` (1,100, KD 4),
`generative engine optimization tool` (900, KD 39), `answer engine optimization tools`
(800, KD 26), `process documentation template` (600, KD 3),
`technical documentation template` (500, KD 0), `project documentation template` (450, KD 3).

The template sub-family in cluster 1 (44 keywords) is uniformly low-KD and is the most
mechanically winnable block in the entire universe. Only 2 keywords across the whole
universe are calculation-led, so there is no case for building a calculator.

---

## 6. Revised day-90 click band

**Prior band: 700–2,400 visits/month by 2026-11-15, documentation only, against a
10,000 target.**

### Revised: 350–1,350 clicks/month, central estimate ~710

Full arithmetic below. The band is *lower* than the prior one despite a 4.9× larger
universe, because volume was never the constraint.

**Step 1 — how many pages actually mature by day 90.** The queue holds 71 `Planned` rows
through 2026-11-15. A page published on day 89 ranks for nothing on day 90.

| Cohort | Pages | Age at day 90 | Maturity | Mature-equivalents |
|---|---:|---|---:|---:|
| published day 1–30 | 24 | 60–90d | 0.55 | 13.2 |
| published day 31–60 | 24 | 30–60d | 0.30 | 7.2 |
| published day 61–90 | 23 | 0–30d | 0.08 | 1.8 |
| | **71** | | | **22.2** |

**Publishing 71 pages in 90 days buys 22.2 mature pages of ranking by day 90.** This is the
binding constraint on the whole campaign, and it is unaffected by how large the niche is.

**Step 2 — volume per page.** Each page owns one head keyword plus the long tail it picks
up; tail multiplier 2.5×. Selection quality is the biggest single lever, so it is varied
across scenarios rather than assumed:

| Scenario | Selection | Head vol/page | ×2.5 tail = addressable |
|---|---|---:|---:|
| Low | mean of best 400 KD≤20 | 382 | 955 |
| Mid | mean of best 250 KD≤20 | 523 | 1,306 |
| High | mean of best 150 KD≤20 | 740 | 1,851 |

`traffic_potential` was deliberately **not** used. It reports the traffic of the #1 ranking
*page*, so `nfl streams subreddit` scores 481,000 because the #1 page is reddit.com. It
measures the incumbent, not the opportunity, and using it would have inflated the band by
an order of magnitude.

**Step 3 — position and CTR.** At DR 26 targeting KD≤20: P(top 3) = 0.15, P(4–10) = 0.30,
P(11–20) = 0.25. Top-3 CTR of 8% / 12% / 16% across the three scenarios.

The site's **own measured top-3 CTR is 4.1%** (GSC, 12 months, 98 impressions, 4 clicks).
That is far below normal and is the documented floor, but the sample is thin and sits on
legacy off-niche queries, so it is not used as the low scenario. It is a warning, not a
forecast — see §7.

**Step 4 — AI Overview haircut.** 49.2% of the universe shows an AIO; 35% click loss on
those SERPs. Net multiplier **0.828**.

**Step 5 — legacy.** Pre-campaign pages currently produce ~15 clicks/month (GSC, date
dimension, Jun–Aug 2026). Carried at 15 / 25 / 40.

| | Low | Mid | High |
|---|---:|---:|---:|
| Clicks per page at full maturity | 18.15 | 37.24 | 70.33 |
| day 1–30 cohort | 240 | 492 | 928 |
| day 31–60 cohort | 131 | 268 | 506 |
| day 61–90 cohort | 33 | 69 | 129 |
| Campaign raw | 404 | 828 | 1,564 |
| After AIO haircut (×0.828) | 334 | 685 | 1,295 |
| Plus legacy | +15 | +25 | +40 |
| **Site total, clicks/month** | **349** | **710** | **1,335** |

**Outer bounds**, for completeness: undirected keyword selection at the site's own measured
4.1% CTR floors at ~116/month. Perfect selection (best 71) at 20% CTR ceilings at
~2,623/month. Neither is a plausible operating assumption.

### Against the 10,000/month target

The central estimate is **~7% of target**; the high scenario reaches 13%, and even the
implausible outer ceiling of 2,623 reaches only 26%. **The 10,000 target is not reachable
by publishing inside 90 days, and no choice of niche changes that.**

The arithmetic of why: 10,000 clicks/month across 22.2 mature-equivalent pages requires 450
clicks/page/month. At a 12% top-3 CTR and P(top 3) = 0.15, that needs roughly 25,000
searches/month of addressable volume per page. The best 150 keywords in the entire
seven-cluster universe average 740. **The gap is 34×, and it is a throughput gap, not a
volume gap.** Reaching 10,000 requires either several years of compounding, or a channel
that is not organic search.

---

## 7. What the numbers say to do

Stated as findings, not recommendations to approve.

1. **Widening the niche was correct, but not for the reason given.** The charter expected
   volume relief. Volume was never the constraint. What the wider niche actually buys is
   *winnable* volume: clusters 2, 5, 6 and 7 are 76–91% KD≤20, against documentation's 50%
   and AI-engineering's 40%. The wider niche is easier, not bigger in any way that matters.
2. **Tools are the highest-value lever and the data now says so quantitatively.** Nine
   build-a-tool keywords, and **not one has an AI Overview**, against 49.2% across the
   universe. `ai overviews checker` at 700/mo and KD 0 is the cleanest single opportunity
   found. The llms.txt trio is 550/mo against a tool that already exists.
3. **The CTR problem outranks the content problem.** The site's measured 4.1% top-3 CTR is
   the difference between the low and high scenarios — a 3.8× swing on the same content.
   Fixing titles and descriptions on pages that already rank moves the band harder than any
   individual new article. This confirms CHARTER §4 with a number attached.
4. **Cluster 3 needs splitting by difficulty, not treated as one block.** Its 150,140/mo is
   real but 60% of it sits above KD 20. The two biggest prizes in the niche
   (`what is a vector database`, `what is an mcp server`, 18,200/mo combined) are KD 39–40
   and will not be won at DR 26 in 90 days.
5. **Cluster 2 should not get 1/7th of the calendar.** At 7,930/mo it is 2.4% of the universe
   and places nothing in the top 15. It is highly winnable but there is almost nothing there
   to win. Weight the calendar by volume × winnability, not evenly across seven clusters.
6. **Re-pull clusters 5, 6 and 7 before relying on their totals.** All three hit the 250-row
   limit; the recorded volumes are floors. One paid call remains in this phase's budget.

---

## 8. Provenance

| Item | Source | Cost |
|---|---|---|
| Cluster 1 keywords | banked `DERIVED-clean-universe.json`, re-cleaned here | 0 (reused) |
| Clusters 2–7 keywords | 7 × `keywords-explorer-matching-terms` | 25,540 units |
| Domain Rating (26) | `public-domain-rating-free` | free |
| CTR by position, legacy clicks | Google Search Console API, first-party | free |
| AI-citation data | **not available** — Brand Radar returns `Missing addon` | — |

Files: `_fetch.py` (paid pulls) · `_clean.py` (cleaning rules) · `_analyze.py` (this
analysis) · `B1`–`B7` raw JSON · `DERIVED-full-universe.json` (1,129 cleaned, deduped,
cluster-assigned) · `DERIVED-cleaning-audit.json` (every dropped keyword) ·
`DERIVED-analysis.json` (all derived figures). Re-run: `python3 _clean.py && python3 _analyze.py`.

**No AI-search citation data exists in this analysis.** Brand Radar is not entitled on this
Standard plan — confirmed twice. AI-search exposure here is inferred solely from the
`serp_features` AI Overview flag, which says a SERP *has* an AI Overview, not whether
ninadpathak.com is cited in it. Anything claiming citation share would be fabricated.

---

## Appendix A — the cluster 5/6/7 cap, 2026-08-17

Appended, not merged into the tables above, so the correction keeps a history.

### The re-pull did not happen: the Ahrefs credential died

The uncapping call (clusters 5, 6 and 7, 15 seeds combined, `limit=1000`) **failed on
authentication**. HTTP 401 on the direct API and MCP error -32600 `Access denied: MCP
token is invalid`, persistent across retries on both transports. `~/.claude.json` was
modified at 19:07 IST, about 21 minutes before the attempt, so the token looks rotated
or revoked. No units were consumed and the call is logged as failed in `CALL-LOG.md`.

**This is not a data-availability finding.** The seeds are not exhausted. Someone with a
working credential should re-run that one call.

### The cap does not change the day-90 band, and this is provable without the re-pull

The band stands at **350–1,350 clicks/month, central ~710.** The cap cannot move it, for
a structural reason rather than an estimate.

All three capped pulls used `order_by volume:desc` with `limit 250`. Truncation therefore
removed only the **lowest**-volume keywords in each cluster. Every keyword the cap hid has
volume at most equal to the 250th row's:

| Cluster | Rows | Highest vol | Lowest returned vol = ceiling on anything missing |
|---:|---:|---:|---:|
| 5 Reddit marketing | 250 | 8,300 | **40/mo** |
| 6 Forums & community | 250 | 2,700 | **80/mo** |
| 7 Technical & community events | 250 | 2,700 | **90/mo** |

The band's per-page volume comes from the best 150 / 250 / 400 keywords of the KD≤20 pool.
Those sets have cut-offs of 250, 150 and **100/mo** respectively. The highest volume any
missing keyword can have is **90/mo** — below even the most permissive scenario's 100/mo
cut-off.

**No keyword the cap removed can enter any target set the band is built on.** The inputs
(740 / 523 / 382 head volume per page) are unchanged, so the band is unchanged.

### What the cap does understate

The cluster **totals** in §2, which are sums over the whole cluster rather than its best
keywords. Those three remain floors:

| Cluster | Recorded (floor) | What the re-pull would correct |
|---:|---:|---|
| 5 Reddit marketing | 33,360/mo | Upward, by keywords ≤40/mo each |
| 6 Forums & community | 24,140/mo | Upward, by keywords ≤80/mo each |
| 7 Technical & community events | 33,000/mo | Upward, by keywords ≤90/mo each |

So the honest position: the all-cluster total of **336,180/mo is a floor**, and the three
distribution clusters are the part of it most understated. The calendar was reweighted
toward these clusters — 32 of 71 rows, 45% of the schedule — and that reweighting is
**not** invalidated, because it rested on their KD≤20 winnability share (76–91%), which
the cap does not touch either: the withheld keywords are low-volume long tail, which skews
*easier*, not harder.

The one decision this cap could still affect is total-addressable sizing, not scheduling
and not the band. Re-run the call when the credential is back and correct §2 here.
