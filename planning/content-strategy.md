# Content Strategy: ninadpathak.com (v6.0 — Pillar Hubs + Hybrid Positioning)

> **v6.0 (2026-06-14):** Added a pillar/hub layer and a 7th cluster. See the
> "Pillar hubs" and "Hybrid positioning" sections at the bottom. v5.0 cluster map and
> rules below remain in force.



**Goal:** Rank for the technical AI/LLM and developer-content queries that DevTools and
B2B SaaS buyers (Heads of Content, DevRel leads, founders) search, and convert that
authority into inbound content engagements. Every post does double duty: it ranks, and
it is a writing sample that proves I can produce technical depth their engineers approve.

**Audience:** The Hacker News reader who ignores marketing and upvotes "I ran X on Y, here
is the profiler output." The buyer who needs a writer that already understands RAG,
agents, and inference, not one who needs it explained to them.

**Differentiator:** Programmer-turned-writer. Posts are anchored in code I wrote and
benchmarks I ran on real hardware (MacBook Air M2, 16GB). If an AI Overview can answer it
without a human running anything, it is not worth writing.

---

## Topical authority map (the six clusters)

SEO here is won by *cluster depth*, not one-off posts. The 61 live posts form six clusters.
Internal links run within each cluster (done as of the 2026-05 link pass) so crawlers and
readers see a connected authority hub, not scattered articles.

1. **AI Agent Memory** (deepest cluster, ~17 posts) — the flagship. ai-memory-management,
   the memory-hierarchy posts, how-memory-works-in-{claude-code,deerflow,hyperagents},
   short-term / episodic-semantic-working memory, rag-vs-memory, voice memory,
   memory-versioning, BEAM benchmark, state-of-agent-memory-2026.
2. **Agent Architecture** (~9 posts) — taxonomy, design space, loop anatomy, agent-vs-assistant,
   multi-agent tradeoffs, why-agents-fail, production errors, harnesses, MCP.
3. **RAG & Retrieval** (~9 posts) — rag-vs-fine-tuning, evaluation metrics, reranking,
   semantic caching, hybrid search, contextual retrieval, embeddings, structured outputs,
   WASM vector benchmarks.
4. **LLM Inference, Cost & Internals** (~10 posts) — context windows, token budgets, token
   counting, prompt caching, speculative decoding, TTFT, KV-cache eviction, MoE,
   best-LLMs-for-coding, lambda-calculus reasoning benchmark.
5. **Engineering Benchmarks** (the lab credibility) — agentic-CLI, uv, voice-AI latency,
   WASM vector, KV-cache. Original instrumented data, un-fabricatable, the strongest
   client-proof pieces.
6. **Technical Writing for DevTools** (~13 posts) — the meta cluster that directly targets
   the buyer: writing for engineers / AI products, shorter docs, onboarding docs, tutorials,
   changelogs, release notes, docs-lose-deals, Stripe moat, content-as-moat, trust hierarchy,
   velocity-and-docs, engineer-to-writer.

Clusters 1–5 prove I understand the domain. Cluster 6 sells the service. Cross-links
between 5 and 6 (benchmark posts linking to the writing posts and vice versa) are the
highest-value internal links for conversion.

---

## What changed in the 2026-05 cleanup (state of the corpus)

- **Deleted 4 off-brand posts** that sat in no cluster and diluted topical focus:
  iCloud Keychain escrow (Apple security), Spinel Ruby AOT compiler, python `model.predict()`
  (generic ML tutorial), and the HERMES.md Claude-billing post (unverifiable claim, reputational risk).
- **Fixed slugs:** the dated agent posts (taxonomy, why-failing, agent-loop, asymmetric,
  memory-versioning) had no explicit slug, so they built to ugly date-prefixed URLs while
  every internal link pointed at the clean slug. Added clean slugs to match. Going forward,
  every post gets an explicit keyword-rich `slug:` in frontmatter. No dates in URLs.
- **Fixed 96 broken internal links** (91 used a dead `/articles/` prefix, 5 used `/posts/`;
  canonical is `/blog/<slug>/`). Repointed 29 links that pointed at never-written posts to
  the closest existing post.
- **Internal linking:** every post now carries 2–3 contextual in-body links with keyword-rich
  anchor text, clustered by topic. The build also auto-generates a tag-based related-posts
  footer, so tags must stay aligned to the cluster.
- **Visuals:** restored 11 purpose-built Three.js memory visuals that existed but were never
  embedded; repaired 2 corrupted CSS visuals (chunking, reranking-pipeline); added 6 new
  pure-CSS/SVG visuals (MoE routing, MCP architecture, hybrid-search RRF, RAG-vs-finetune
  decision, agent loop, structured-outputs comparison). 35 of 61 posts now carry a visual.

---

## Rules going forward

1. **Slugs:** explicit, keyword-rich, no date prefix. Set `slug:` in frontmatter on day one.
2. **Internal links:** 2–3 per post, in-body, keyword-rich anchor text, only to posts in the
   same or an adjacent cluster. Never link to a post that does not exist yet (see roadmap).
3. **Tags:** drive the related-posts footer. Use them to keep a post inside its cluster.
4. **Visuals:** prefer self-contained pure CSS/SVG (zero dependencies, always renders). Use
   Three.js only when 3D genuinely helps, and only the verified CDN pair
   (`three@0.128.0/build/three.min.js` + `three@0.128.0/examples/js/controls/OrbitControls.js`).
   Every visual ships the standard `:root` token block and dark-mode media query.
5. **Voice:** first person, no em dashes, no semicolons in prose, no banned sentence-starters
   (In/This/By/Finally/Most/Ever/If), no forbidden words (leverage/synergy/unlock/gap/distance).
   The linter enforces this. New posts pass before publish.
6. **Evidence:** benchmark posts cite real numbers from real runs, including a "what didn't work"
   section. No fabricated data, no fabricated bugs.

---

## Conversion path

Every post's related/footer and at least one in-body link should be reachable, within two
hops, from a Cluster 6 (technical-writing) post. The reader who lands on a deep RAG benchmark
from search should be one or two clicks from "why DevTools startups lose deals over bad docs"
and the contact CTA. That is how topical authority turns into leads.

---

## Pillar hubs (v6.0)

SEO and AI Overviews reward a clear topical hub for each head term. As of 2026-06-14 every
cluster has a pillar page that gathers its spokes into one curated reading path. Pillars live
at top-level slugs to maximize the head-term signal, with an index at `/topics/`.

| Pillar | URL | Cluster |
|--------|-----|---------|
| AI Agent Memory | `/ai-agent-memory/` | 1 |
| AI Agent Architecture | `/ai-agent-architecture/` | 2 |
| RAG & Retrieval | `/rag/` | 3 |
| LLM Inference & Cost | `/llm-inference/` | 4 |
| AI Workflows & Automation | `/ai-workflows/` | 7 (new) |
| Technical Writing for DevTools | `/technical-writing/` | 6 |

**How pillars work (mechanics):** source is `content/pillars/*.yaml` (intro markdown,
curated `sections` of post slugs, `faqs`, `bridges`). The build resolves slugs to live posts
and warns on any unknown slug, so a pillar can never link to a post that does not exist. Each
pillar emits `CollectionPage` + `ItemList` + `BreadcrumbList` + `FAQPage` schema, and is
wired into the sitemap, `llms.txt` ("Topic Hubs"), and nav. Cluster 5 (Engineering
Benchmarks) is not a standalone pillar — its posts are folded into the relevant topic hubs as
credibility sections, since benchmarks support multiple topics.

**Pillar maintenance:** when a new post ships, add its slug to the right section of the
pillar YAML. Keep curated ordering (fundamentals → quality → production → benchmarks).

---

## Hybrid positioning (v6.0)

Decision (2026-06-14): pursue **both** the infra moat and a practitioner cluster. Clusters
1–5 prove I understand the internals. Cluster 7 (AI Workflows & Automation) targets the
stated brand — AI workflows, automation, speeding up work, agentic setups — for a
work-faster audience with higher commercial intent. The `/ai-workflows/` pillar bridges into
the infra hubs so the depth backs the advice, and into `/technical-writing/` so automation
readers reach the paid service.

Cluster 7 definition, audience, keyword targets, and 12 sequenced article briefs live in
`planning/ai-workflows-cluster.md`. Tier-1 anchors to write first: `coding-agent-setup-that-works`,
`agentic-workflow-playbook`, `mcp-server-setup-guide`.
