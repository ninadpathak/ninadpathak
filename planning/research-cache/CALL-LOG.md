# Paid API Call Log

Every paid call made for the 90-day strategy. Plan: `planning/2026-q3-fetch-plan.md`.
Cap: 25 paid calls. Free calls (Ahrefs `doc`, `subscription-info`,
`management-brand-radar-reports`, Semrush discovery, WebSearch, WebFetch) are not counted
and not listed.

| # | UTC timestamp | Tool | Query summary | Rows | Units | Cache file |
|---:|---|---|---|---:|---:|---|
| 1 | 2026-08-17T11:28:31Z | ahrefs keywords-explorer-matching-terms | seeds: technical documentation, software documentation, product documentation, documentation template, documentation example; us; terms mode; vol>=30, KD<=45 | 250 | 11000 | A1-matching-terms-core-documentation.json |
| 2 | 2026-08-17T11:29:31Z | ahrefs keywords-explorer-matching-terms | seeds: api documentation, api reference, openapi, developer portal, sdk documentation; us; terms mode; vol>=30, KD<=45 | 250 | 11000 | A2-matching-terms-api-documentation.json |
| 3 | 2026-08-17T11:30:12Z | ahrefs keywords-explorer-matching-terms | seeds: docs as code, documentation workflow, documentation automation, documentation maintenance, documentation tools; us; terms mode; vol>=30, KD<=45 | 54 | 2376 | A3-matching-terms-docs-operations.json |
| 4 | 2026-08-17T11:31:40Z | ahrefs keywords-explorer-matching-terms | seeds: llms txt, ai documentation, documentation chatbot, semantic chunking, ai search optimization; us; terms mode; vol>=20, KD<=50 | 22 | 968 | A4-matching-terms-ai-ready-docs.json |
| 5 | 2026-08-17T11:32:20Z | ahrefs keywords-explorer-matching-terms | seed: llms.txt; us; PHRASE mode; no volume floor | 60 | 2640 | A5-matching-terms-llmstxt-phrase.json |
| - | 2026-08-17T11:33:05Z | ahrefs brand-radar-ai-responses | chatgpt,perplexity + google_ai_overviews, question filter on documentation terms | FAILED | 0 | none — "Missing addon: Brand Radar". Not available on this subscription. No units consumed. |
| 6 | 2026-08-17T11:33:40Z | ahrefs keywords-explorer-matching-terms | seeds: technical documentation, api documentation, developer documentation, documentation site; us; QUESTIONS mode; vol>=20, KD<=50 | 10 | 330 | A6-matching-terms-questions-documentation.json |
| 7 | 2026-08-17T11:35:10Z | ahrefs keywords-explorer-overview | 17 exact terms targeted by the 17 published posts; us | 14 | 462 | A7-overview-published-post-terms.json |
| 8 | 2026-08-17T11:36:00Z | ahrefs keywords-explorer-related-terms | technical documentation, docs as code, api documentation; us; view_for=top_10; vol>=50, KD<=40 | 60 | 1980 | A8-related-terms-adjacent.json |

## Phase 2 — full-niche universe recompute (2026-08-17, `seo-analytics`)

Charter 2c-bis widened the niche from documentation-only to seven clusters. Cluster 1 was
reused from the banked pull above and **not re-bought**. Clusters 2–7 needed new data.

Calls made through `_fetch.py`, which hits the same Ahrefs API v3 endpoint the MCP server
wraps, with the same credential, and writes raw JSON straight to this directory. Same unit
cost; it just avoids routing ~700 KB of keyword rows through an agent context.

All are `keywords-explorer/matching-terms`, `terms` mode, country `us`,
`where volume>=30 AND difficulty<=45`, `order_by volume:desc`, `limit 250`,
`select keyword,volume,difficulty,cpc,traffic_potential,parent_topic,intents,serp_features`.

| # | UTC timestamp | Tool | Query summary | Rows | Units | Cache file |
|---:|---|---|---|---:|---:|---|
| 9 | 2026-08-17T12:54:57Z | ahrefs keywords-explorer-matching-terms | cluster 2 — seeds: developer experience, developer relations, developer marketing, developer advocate, devrel | 67 | 3318 | B1-devex-devrel.json |
| 10 | 2026-08-17T12:55:11Z | ahrefs keywords-explorer-matching-terms | cluster 3a — seeds: ai agent, agent memory, agentic workflow, ai agent framework, mcp server | 130 | 9038 | B2-ai-agents-memory.json |
| 11 | 2026-08-17T12:55:12Z | ahrefs keywords-explorer-matching-terms | cluster 3b — seeds: retrieval augmented generation, rag pipeline, llm inference, vector database, embeddings | 234 | 9038 | B3-rag-inference.json |
| 12 | 2026-08-17T12:55:14Z | ahrefs keywords-explorer-matching-terms | cluster 4 — seeds: ai overviews, generative engine optimization, answer engine optimization, chatgpt seo, ai search optimization | 62 | 0* | B4-ai-overviews-geo.json |
| 13 | 2026-08-17T12:55:24Z | ahrefs keywords-explorer-matching-terms | cluster 5 — seeds: reddit marketing, reddit ads, reddit seo, subreddit, reddit growth | 250 | 12470 | B5-reddit-marketing.json |
| 14 | 2026-08-17T12:55:25Z | ahrefs keywords-explorer-matching-terms | cluster 6 — seeds: online community, community building, community management, discord community, forum software | 250 | 11000 | B6-community-forums.json |
| 15 | 2026-08-17T12:55:26Z | ahrefs keywords-explorer-matching-terms | cluster 7 — seeds: developer conference, tech meetup, hackathon, community event, virtual event | 250 | 11000 | B7-events.json |

| — | 2026-08-17T13:58:31Z | ahrefs keywords-explorer-matching-terms | cluster 5+6+7 combined, 15 seeds, `limit=1000` — the uncapping re-pull | **FAILED** | 0 | none — HTTP 401 Unauthorized on the direct API, and MCP error -32600 "Access denied: MCP token is invalid". Persistent across retries on both transports. `~/.claude.json` was modified 2026-08-17T19:07 IST, ~21 min before the attempt, so the Ahrefs token appears to have been rotated or revoked. **No units consumed. Not a data-availability finding — do not treat these seeds as exhausted.** Retry this exact call once the credential is restored. |

\* The per-call `Units` column is a before/after read of the workspace meter, which is
eventually consistent and cannot be trusted at this call rate — call 12 reads 0 and the
column sums to 55,864, both wrong. **The authoritative figure is the session delta:
workspace usage went 36,604 → 62,144, so these 7 calls cost 25,540 units.**

- **Paid calls this phase: 7** (budget was 8; one unspent).
- Free calls used and not counted: `subscription-info-limits-and-usage`,
  `management-projects`, `management-brand-radar-reports`, `public-domain-rating-free`
  (returned DR 26 for ninadpathak.com), Google Search Console API.
- **Brand Radar remains unavailable** — confirmed again this phase. The management endpoint
  lists a report, which is misleading; the actual data endpoints return
  `Missing addon: Brand Radar`. No AI-citation data was bought or fabricated.
- Clusters 5, 6 and 7 returned exactly 250 rows, i.e. they hit the `limit`. Their true
  universes are larger than recorded. Treat those three cluster volumes as floors.

## Research phase closed

- **Paid calls used: 8 of the 25 cap.** 17 unspent.
- **Actual Ahrefs consumption: 17,050 units** (workspace 5,848 -> 22,898). Per-call
  estimates in the table above sum higher than the true meter because repeated columns
  across calls are not double-charged.
- **Semrush: 0 paid calls.** The two planned continuity calls (C1 `phrase_these`, C2
  `phrase_kdi`) were not made. Ahrefs returned enough volume and difficulty coverage that
  a second scale added no decision value, so the backlog CSV records `us-ahrefs` in its
  `Database` column and the original seven Semrush rows are left untouched at `us`.
- **Brand Radar: unavailable.** Every data source returns `Missing addon: Brand Radar`.
  The account holds a report but the API entitlement is not on this Standard plan. No
  units consumed. The AI-search half of the strategy is therefore built on the
  `serp_features` AI Overview flag (present on every keyword row pulled) plus free
  SERP and page reads, and the strategy says so explicitly rather than implying it had
  citation data.
- No call took `ninadpathak.com` or any Ninad property as an argument.

---

## Contamination sweep — 2026-08-17, agent `seo-currency`

**Paid calls: 0.** Nothing was bought for this pass.

| Instrument | Calls | Cost | Notes |
|---|---:|---|---|
| Ahrefs | 0 | — | Unusable. `Access denied: MCP token is invalid` on every endpoint, including the free `subscription-info-limits-and-usage`. Reproduced independently; it is the token, not a quota. Raised to Ninad. |
| Semrush | 0 | — | Available and tested working, but not needed. Volume figures were not in question; meaning was. |
| WebSearch SERP reads | 9 | free | The correct instrument for this job: the question is what a SERP shows, not what a volume number says. |
| Banked parent topics | — | free | Already in `DERIVED-full-universe.json` from the original paid pull. The primary tell, at no cost. |

SERP reads made, all 2026-08-17, all free, each recorded with its verdict in
`_contamination_sweep.py` under `DECISIONS`:

1. `community management` → REMOVE (entirely HOA/property)
2. `community management software` → KEEP (majority on-niche)
3. `community management services` → REMOVE (entirely HOA/property)
4. `online community engagement` → REMOVE (civic/public consultation)
5. `reddit seo` → KEEP (genuine Reddit-marketing practice)
6. `developer portal` → KEEP (genuine docs-ops concept)
7. `audit documentation example` → REMOVE (PCAOB/ISA 230 accounting)
8. `chatgpt seo` → KEEP (majority citation-optimisation sense)
9. `how to host a virtual event` → REMOVE (corporate webinar industry)
10. `subreddit` → REMOVE (consumer navigation; Reddit Help, Wikipedia, Dictionary.com)

Reads 5 and 6 each reversed a removal that the parent topic alone would have made
wrongly, which is the argument for keeping the SERP step rather than trusting the
parent-topic field on its own.

Outputs: `_contamination_sweep.py`, `DERIVED-contamination-sweep.json`,
`planning/research/CONTAMINATION-SWEEP-2026-08-17.md`.

Finding written up in `planning/cluster-intent-check-2026-08-17.md`.

## 2026-08-17 cluster 4 verification (Semrush; Ahrefs still returning "MCP token is invalid")

| # | Tool | Query | Database | Rows | Finding |
|---:|---|---|---|---:|---|
| S4 | phrase_organic | `code documentation` | us | 10 | Clean. IBM, GitHub, Heretto, Codacy. Dedicated pages for the term = parent topic owns itself. Used for row 20. |
| S5 | phrase_fullsearch | `developer conference` | us | 25 | Navigational brand traffic: WWDC 5,400, GDC 2,400, NVIDIA, Roblox, Esri. Cluster 7 contaminated. |
| S6 | phrase_fullsearch | `conference talk proposal` | us | 4 | **All variants 0/mo.** No how-to intent under cluster 7. |
| S7 | phrase_fullsearch | `call for papers` | us | 20 | 1,300 but academic navigation: NeurIPS, ICML, ICLR, upenn. Not writable. |
| S8 | phrase_fullsearch | `answer engine optimization` | us | 30 | Real and rising. AEO 4,400, what-is 480, aeo-vs-geo 210. |
| S9 | phrase_organic | `answer engine optimization` | us | 10 | Clean SERP: HubSpot, Coursera, Forbes, Ahrefs, CXL. Real AEO intent, hard competition. |
| S10 | phrase_kdi | 15 cluster-4 head terms | us | 15 | **KD 35-68 across the board.** AEO 52, GEO 68, chatgpt seo 61, llms.txt 49. None are KD<=20. |
| S11 | phrase_fullsearch | `ai overviews`, Nq>80 KD<25 | us | 30 | KD<=20 tail is rank-tracker SaaS intent plus `company overview` token matches. ~4 usable. |
| S12 | phrase_fullsearch | `llms.txt` | us | 30 | **Clean and strong.** llms.txt 3,600, generator 2,400, file 1,900, what-is 1,000, examples 480. |

**Correction to an earlier correction.** On 2026-08-17 I reported `llms.txt generator` at 300/mo
from Ahrefs and used it to argue the canonical plan's Month 5 anchor was built on a bad number.
Semrush puts it at **2,400**, which matches what the canonical plan said. The plan was right and my
correction was wrong. The llms.txt sub-cluster is the healthiest part of cluster 4.

## 2026-08-17 intent check (Semrush, after Ahrefs token failure)

| # | UTC | Tool | Query | Rows | Note |
|---:|---|---|---|---:|---|
| - | 2026-08-17 | ahrefs keywords-explorer-matching-terms | reddit marketing seed set | FAILED | `Access denied: MCP token is invalid`. Ahrefs unavailable mid-session; fell back to Semrush per standing order 8. |
| S1 | 2026-08-17 | semrush phrase_related | "reddit marketing", us, Nq>100, Kd<35 | 25 | Head is account-buying and ad-platform navigation, not content intent. |
| S2 | 2026-08-17 | semrush phrase_fullsearch | "promote on reddit", us | 40 | Developer-relevant content intent totals ~100/mo. Row 20's target is 20/mo. |
| S3 | 2026-08-17 | semrush phrase_fullsearch | "developer community", us | 25 | Returns municipal housing and community development. Cluster 6 contaminated at the head. |

Finding written up in `planning/cluster-intent-check-2026-08-17.md`.

## 2026-08-17 cluster 4 verification (Semrush; Ahrefs still returning "MCP token is invalid")

| # | Tool | Query | Database | Rows | Finding |
|---:|---|---|---|---:|---|
| S4 | phrase_organic | `code documentation` | us | 10 | Clean. IBM, GitHub, Heretto, Codacy. Dedicated pages for the term = parent topic owns itself. Used for row 20. |
| S5 | phrase_fullsearch | `developer conference` | us | 25 | Navigational brand traffic: WWDC 5,400, GDC 2,400, NVIDIA, Roblox, Esri. Cluster 7 contaminated. |
| S6 | phrase_fullsearch | `conference talk proposal` | us | 4 | **All variants 0/mo.** No how-to intent under cluster 7. |
| S7 | phrase_fullsearch | `call for papers` | us | 20 | 1,300 but academic navigation: NeurIPS, ICML, ICLR, upenn. Not writable. |
| S8 | phrase_fullsearch | `answer engine optimization` | us | 30 | Real and rising. AEO 4,400, what-is 480, aeo-vs-geo 210. |
| S9 | phrase_organic | `answer engine optimization` | us | 10 | Clean SERP: HubSpot, Coursera, Forbes, Ahrefs, CXL. Real AEO intent, hard competition. |
| S10 | phrase_kdi | 15 cluster-4 head terms | us | 15 | **KD 35-68 across the board.** AEO 52, GEO 68, chatgpt seo 61, llms.txt 49. None are KD<=20. |
| S11 | phrase_fullsearch | `ai overviews`, Nq>80 KD<25 | us | 30 | KD<=20 tail is rank-tracker SaaS intent plus `company overview` token matches. ~4 usable. |
| S12 | phrase_fullsearch | `llms.txt` | us | 30 | **Clean and strong.** llms.txt 3,600, generator 2,400, file 1,900, what-is 1,000, examples 480. |

**Correction to an earlier correction.** On 2026-08-17 I reported `llms.txt generator` at 300/mo
from Ahrefs and used it to argue the canonical plan's Month 5 anchor was built on a bad number.
Semrush puts it at **2,400**, which matches what the canonical plan said. The plan was right and my
correction was wrong. The llms.txt sub-cluster is the healthiest part of cluster 4.

## 2026-08-17 fifth cycle — fortnight two verification (Semrush; Ahrefs still dead)

| # | Tool | Query | Rows | Finding |
|---:|---|---|---:|---|
| S13 | phrase_these | 12 docs-as-code sub-topics | 8 | Near-zero across the block: docs as code tools 20, documentation testing 20, documentation versioning 10, documentation migration 20, automated api documentation 30. Four returned nothing. |
| S14 | phrase_organic | `ai overview tracker` | 8 | Tool pages rank, including two FREE tools (Advanced Web Ranking, Seobility) plus one how-to post. Confirms the tool-first directive for this intent. |

**Adjacent finding, recorded for the tool directive rather than acted on as prose:**
`broken link checker` is **8,100/mo** and is tool intent, not article intent. The site already
ships five tools and this is the largest single tool-intent keyword found so far in the niche.
Row 41's brief explicitly declines to chase it with prose.

## 2026-08-17 sixth cycle — fortnight three verification (Semrush)

| # | Tool | Query | Rows | Finding |
|---:|---|---|---:|---|
| S15 | phrase_these | 10 fortnight-three targets | 7 | `developer onboarding checklist` 70 and `documentation automation` 170 are the only real ones. `readme best practices` 20, `developer community platform` 20, `how to build a developer community` 20. Three returned nothing at all. |

`online community management` shows 390 but is general community-management intent, not developer
community, and sits next to the HOA and property-management contamination already swept from
cluster 6. Not targeted.

---

## Tool SERP verification — 2026-08-17, agent `seo-currency`

**Paid calls: 1.**

| Instrument | Report | Lines | Cost | Notes |
|---|---|---:|---|---|
| Semrush | `phrase_these` | 7 | 10 units/line = **70 units** | Volume, KD and SERP-feature codes for the seven target tool keywords, as a cross-check on the live SERP reads. Found an 8x volume disagreement with Ahrefs on `llms.txt generator` (300 vs 2,400). |
| Live Google SERP reads | — | 7 | free | The primary instrument. Real browser session. |
| Search Console | — | 5 | free | Our positions, and the tool pages' full history. |
| Ahrefs | — | 0 | — | Still dead. `Access denied: MCP token is invalid`. |

Google served `/sorry/index` bot detection on the first attempt. **No attempt was made to
solve or bypass the CAPTCHA.** A plain query URL worked on retry and every read came from
that. Had it not, the question would have been reported as unanswerable.

Only Semrush code **52 = AI Overview** is authoritatively documented; codes 6, 7, 9, 14, 15,
20, 21 and 36 were left undecoded rather than guessed.

Output: `planning/research/TOOL-SERP-VERIFICATION-2026-08-17.md`.

---

## Volume arbitration and link baseline — 2026-08-17, agent `seo-currency`

**Paid calls: 0.** The Semrush figure under dispute was already bought on the earlier pass and
was not re-bought.

| Instrument | Result | Cost |
|---|---|---|
| Google Trends public endpoint | **HTTP 429.** The one free quantitative arbiter, closed. | free |
| Google autocomplete | Ordinal evidence: `generator` is the top modifier in the llms.txt family. | free |
| Search Console API | Zero `llms.txt` queries in the entire recorded history, so no first-party signal either way. | free |
| Search Console **Links report** | **Unreachable.** No links resource exists in the API — verified by enumerating the whole v1 service. The UI has it, but the signed-in browser account lacks access to the property. | free |
| GA4 Admin API | **HTTP 403, disabled on the credential's project.** | free |
| dev.to public API | 96 articles; 14 canonicalised here, 82 to pathak.ventures, 0 to any tool page. | free |
| LinkedIn | **HTTP 999** to automated fetches. | free |
| Ahrefs | Still dead. Not retried, per instruction. | — |

Outputs: `planning/research/LLMS-TXT-GENERATOR-VOLUME-2026-08-17.md`,
`tools/link_inventory.py`, `planning/link-inventory.json`, `tests/test_link_inventory.py`.

---

## Syndication audit — 2026-08-17, agent `seo-currency`

**Paid calls: 0.** Read-only: nothing posted to dev.to, cron untouched.

| Instrument | Use | Cost |
|---|---|---|
| dev.to public API | 96 articles, canonical targets, reactions, comments | free |
| Live fetch of a dev.to post | Link mechanics: canonical tag, rel attributes, followed vs nofollow | free |
| HTTP status checks on 14 canonical targets | Found 3 pointing at 404s, 2 at the homepage | free |
| WebSearch exact-phrase | Whether either copy ranks | free |
| Repo frontmatter | Cron pacing against publish dates | free |

Key mechanical finding: **dev.to applies no `rel=nofollow`.** External anchors carry
`noopener`, `noreferrer`, or no rel — none of which is nofollow. About four followed links per
post. Three of four carry `noreferrer`, so click-through referrals are structurally
unmeasurable in analytics.

Output: `planning/research/SYNDICATION-AUDIT-2026-08-17.md`, plus engagement and the
one-referring-domain ceiling now reported by `tools/link_inventory.py` on every run.
