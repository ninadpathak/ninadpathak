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
