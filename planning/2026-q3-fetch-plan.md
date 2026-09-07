# Q3 2026 Fetch Plan

> Historical branch artifact restored during consolidation on 2026-09-07. Figures and proposed actions describe the dated investigation below; use `campaign-90d.md` and current tools for active decisions.

**Written:** 2026-08-17
**Branch:** `seo/90day-strategy`
**Hard cap:** 25 paid calls. This plan commits 15 and holds 10 in reserve.
**Scope rule:** every call is about keywords, questions, or competitor pages in the
documentation niche. No call takes `ninadpathak.com` as an argument. No organic-traffic,
rank-tracking, backlink, or site-explorer call is made against any Ninad property.

## Decisions this research has to inform

The 90-day plan needs one new article every day plus scheduled remediation. That volume
only works if the target list is already researched, so the research has to answer five
questions and nothing else:

1. Which documentation and AI-ready-docs keywords have enough demand and low enough
   difficulty to be worth one of the 90 slots?
2. For each, is the term itself the target, or does its parent topic already own it?
   (A term whose parent topic is a broader page is a section, not an article.)
3. Which of those terms trigger an AI Overview, so the page has to be written for
   extraction as well as ranking?
4. What question-shaped and comparison-shaped queries do people actually put to AI
   assistants in this niche, and what pages get cited in the answers?
5. Which domains own AI citations here, so the competitive read is about real cited
   pages rather than assumed competitors?

A call that does not move one of those five does not get made.

## Niche seed vocabulary

Confirmed from the corpus, not assumed. All 17 published articles resolve to the
`technical-documentation` category; the `ai-memory` category has zero published posts.
Seeds are drawn from `documentation-authority-plan.md` keyword findings and the published
tag set (`documentation`, `technical-writing`, `developer-experience`, `documentation-seo`,
`docs-as-code`, `documentation-workflow`, `information-architecture`).

| Group | Seeds |
|---|---|
| Core documentation | technical documentation, software documentation, product documentation, documentation template, documentation example |
| API documentation | api documentation, api reference, openapi, developer portal, sdk documentation |
| Docs operations | docs as code, documentation workflow, documentation automation, documentation maintenance, documentation tools |
| AI-ready docs | llms.txt, ai documentation, documentation chatbot, docs rag, semantic chunking, ai search optimization |
| Developer experience | developer onboarding, developer experience, developer documentation |

## Paid call schedule

Cost model: Ahrefs charges 10 units per row for each of `volume`, `difficulty`,
`traffic_potential`, and `global_volume`. Selecting volume + difficulty +
traffic_potential is 30 units per row. The workspace has ~394,000 units remaining before
the 2026-09-07 reset, so unit cost is not the binding constraint. The 25-call cap is.

### Block A: keyword universe (Ahrefs Keywords Explorer, 7 calls)

| # | Tool | Query | Decision it informs |
|---:|---|---|---|
| A1 | `keywords-explorer-matching-terms` | seeds: core documentation group, `country=us`, `match_mode=terms`, `terms=all`, `where` volume >= 30, limit 400 | Q1, Q2, Q3. Produces the core-documentation cluster and its parent topics. |
| A2 | `keywords-explorer-matching-terms` | seeds: API documentation group, same filters | Q1, Q2, Q3. Month-2 cluster in the canonical plan; needs its own volume/KD spread. |
| A3 | `keywords-explorer-matching-terms` | seeds: docs operations group, same filters | Q1, Q2, Q3. Docs-as-code cluster sizing. |
| A4 | `keywords-explorer-matching-terms` | seeds: AI-ready docs group, same filters | Q1, Q2, Q3. The cluster with the least existing research and the highest strategic weight. |
| A5 | `keywords-explorer-matching-terms` | seeds: core + API documentation, `terms=questions`, limit 300 | Q3, Q4. Question-shaped demand feeds both FAQ blocks and the AI-search plan. |
| A6 | `keywords-explorer-matching-terms` | seeds: AI-ready docs + developer experience, `terms=questions`, limit 300 | Q3, Q4. Same, for the AI cluster. |
| A7 | `keywords-explorer-related-terms` | `keywords=technical documentation,api documentation,docs as code`, `view_for=all` | Q1. Catches adjacent topics the seed vocabulary would miss entirely. |

Every A-call selects: `keyword, volume, difficulty, cpc, traffic_potential, parent_topic,
intents, serp_features`. `serp_features` is the free column that answers Q3, so it is
never dropped.

### Block B: AI search (Ahrefs Brand Radar, 6 calls)

Brand Radar is queried in market mode using a `where` filter on `question`. No `brand`
argument, no `report_id`, so nothing is scoped to a Ninad property.

| # | Tool | Query | Decision it informs |
|---:|---|---|---|
| B1 | `brand-radar-ai-responses` | `where` question iphrase_match "technical documentation", `data_source=chatgpt,perplexity`, limit 60 | Q4. Real questions and the exact links each answer cited. |
| B2 | `brand-radar-ai-responses` | `where` question iphrase_match "api documentation", same sources, limit 60 | Q4. |
| B3 | `brand-radar-ai-responses` | `where` question iphrase_match "llms.txt", same sources, limit 60 | Q4. The AI-ready cluster's evidence base, currently assumed rather than measured. |
| B4 | `brand-radar-ai-responses` | `where` question iphrase_match "documentation tool", same sources, limit 60 | Q4. Comparison-shaped queries specifically. |
| B5 | `brand-radar-cited-domains` | `where` question iphrase_match "documentation", `data_source=chatgpt,perplexity,google_ai_overviews`, limit 60 | Q5. Who owns AI citations in this niche. |
| B6 | `brand-radar-cited-pages` | same filter as B5, limit 100 | Q5. Which exact pages get cited, so the citability analysis reads real pages. |

### Block C: Semrush continuity (2 calls)

`semrush-opportunity-backlog.csv` records Semrush US volume and KD. New rows sourced from
Ahrefs are not numerically comparable to the existing seven. Rather than mix scales
silently, the `Database` column records provenance as `us-ahrefs` or `us-semrush`, and two
Semrush calls re-anchor the highest-priority shortlist on the original scale.

| # | Tool | Query | Decision it informs |
|---:|---|---|---|
| C1 | `execute_report` / `phrase_these` | semicolon-batched shortlist of ~40 finalist keywords, `database=us` | Q1. Semrush-native volume for continuity with existing rows. |
| C2 | `execute_report` / `phrase_kdi` | same shortlist, `database=us` | Q1. Semrush-native KD for the same reason. |

### Reserve (10 calls, unspent unless a decision is actually blocked)

Held for: a second Brand Radar pass if B1-B4 return thin data for a cluster; a
`serp-overview` on a term where the free SERP read is ambiguous about who owns it; a
follow-up matching-terms pass on a cluster that turns out larger than expected. Any spend
past 25 stops and asks first.

## Free-source work done before and alongside the paid calls

WebSearch and WebFetch carry the competitor teardowns, the reads of actual ranking pages,
and the llms.txt file inspections. Those are exhausted first on every question that does
not strictly need metric data.

## Caching and logging

Every raw response is written to `planning/research-cache/` as JSON, named by call ID
(`A1-matching-terms-core-documentation.json`). Every call is appended to
`planning/research-cache/CALL-LOG.md` with a UTC timestamp, tool name, the exact query,
row count, and unit cost from the response envelope. Nothing is fetched twice; a cached
file is read instead.
