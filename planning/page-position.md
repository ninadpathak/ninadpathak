# Page position, point in time

Appended by `tools/gsc_page_position.py`. Every other Search Console tool here is
differential, so a page holding a steady position is invisible to all of them —
and absence from a movement report was once read as absence of a position, which
sent a merge in the wrong direction.

Four states, never collapsed: `measured`, `no-human-queries`, `withheld`
(has impressions, queries not named — a position exists and cannot be seen), and
`never-impressed`, which is the only one meaning no position. A position is never
printed without the query count it is averaged over.

## 2026-08-17 — page position, point in time

Window 2026-05-17 to 2026-08-14 (90d), ending 3 days back because Search Console lags. Human queries only: brand, machine fan-out and injected spam pages excluded.

**Query counts and human impressions are FLOORS, not counts.** Search Console withholds low-volume queries — the page+query pull sees 1142 of 6480 page-dimension impressions (17.6%), so a page ranks for more queries than are named here. Sitewide impressions and clicks come from the page dimension and are complete.

| State | Meaning |
|---|---|
| `measured` | human queries named; position reported with its query count |
| `no-human-queries` | has impressions, but every named query is brand, machine or spam |
| `withheld` | has impressions; Search Console names none of the queries. **A position exists and cannot be seen** |
| `never-impressed` | no impressions at all. **The only state that means no position** |

90 published pages: **35** `measured`, **0** `no-human-queries`, **35** `withheld`, **20** `never-impressed`.

### Pages with a measured human position

| Page | Cluster | Position (queries) | Human impr | Impr | Clicks | Top query |
|---|---|---|---:|---:|---:|---|
| llm-context-windows-explained | ai-engineering | 5.0 (n=1) | 1 | 5 | 0 | long context windows |
| state-of-open-source-memory-2026 | ai-engineering | 8.5 (n=1) | 2 | 35 | 0 | ai memory systems research 2026 |
| structured-outputs-llms-json-mode-functi | ai-engineering | 9.0 (n=1) | 1 | 32 | 0 | openai structured outputs json mod |
| shared-vs-isolated-memory-multi-agent | ai-engineering | 9.2 (n=2) | 6 | 120 | 2 | how does shared versus isolated me |
| agent-loop-anatomy | ai-engineering | 10.0 (n=1) | 1 | 12 | 0 | perceive think act |
| hybrid-search-bm25-vector-search | ai-engineering | 10.0 (n=1) | 1 | 79 | 0 | hybrid retrieval combining bm25 an |
| why-ai-agents-keep-failing-in-production | ai-engineering | 10.2 (n=1) | 4 | 4 | 0 | how do companies debug ai agents t |
| production-ai-agent-errors | ai-engineering | 10.5 (n=1) | 17 | 20 | 0 | how do you handle errors when ai a |
| fine-tuning-vs-rag-for-agent-memory | ai-engineering | 10.6 (n=3) | 23 | 87 | 2 | ai agent memory vs fine-tuning for |
| why-coding-agents-lose-their-memory | ai-engineering | 12.0 (n=1) | 1 | 24 | 0 | why do i have to keep re-explainin |
| how-stripes-technical-blog-became-a-comp | developer-experience | 13.9 (n=7) | 27 | 116 | 0 | stripe tech blog |
| state-of-ai-agent-memory-2026 | ai-engineering | 15.0 (n=1) | 2 | 73 | 0 | state of ai agent memory 2026 |
| how-to-write-a-technical-tutorial-that-a | technical-documentation | 17.5 (n=7) | 13 | 36 | 0 | technical tutorial |
| from-engineer-to-technical-writer-what-i | developer-experience | 20.7 (n=3) | 10 | 13 | 0 | engineer to technical writer |
| reranking-in-rag-why-your-top-k-results- | ai-engineering | 28.6 (n=3) | 5 | 39 | 0 | top k rag |
| multi-agent-vs-single-agent-tradeoffs | ai-engineering | 35.4 (n=7) | 35 | 80 | 0 | single agent vs multi agent |
| how-memory-works-in-claude-code | ai-engineering | 35.8 (n=11) | 14 | 138 | 0 | memory claude |
| ai-memory-management-for-llms | ai-engineering | 37.0 (n=1) | 1 | 48 | 0 | ai memory management for llms and  |
| how-anthropics-contextual-retrieval-chan | ai-engineering | 42.3 (n=2) | 3 | 2420 | 0 | contextual rag |
| time-to-first-token-ttft | ai-engineering | 47.4 (n=3) | 7 | 7 | 0 | ttft |
| agentic-workflow-playbook | ai-engineering | 56.0 (n=1) | 1 | 45 | 0 | agentic workflows from pr to merge |
| seo-for-technical-documentation | technical-documentation | 58.2 (n=2) | 6 | 10 | 0 | seo documentation |
| llm-inference-optimization | ai-engineering | 61.5 (n=8) | 63 | 79 | 0 | llm inference optimization |
| writing-release-notes-that-developers-tr | technical-documentation | 62.5 (n=2) | 2 | 27 | 0 | who writes release notes |
| memory-for-voice-ai-agents | ai-engineering | 65.2 (n=3) | 4 | 34 | 0 | voice ai context retention |
| asymmetric-retrieval-agent-memory | ai-engineering | 72.0 (n=1) | 1 | 12 | 0 | hybrid retrieval for agent memory |
| rag-evaluation-metrics-what-actually-mat | ai-engineering | 72.0 (n=10) | 34 | 40 | 0 | graph rag evaluation metrics |
| technical-documentation-template | technical-documentation | 75.1 (n=2) | 22 | 30 | 0 | code documentation template |
| best-llms-for-coding | ai-engineering | 76.0 (n=3) | 3 | 3 | 0 | llm coding |
| engineering-velocity-documentation | developer-experience | 76.7 (n=7) | 21 | 51 | 0 | engineering velocity |
| how-to-write-a-changelog-developers-actu | technical-documentation | 82.0 (n=1) | 1 | 5 | 0 | keep a changelog best practices |
| llm-token-budgets-cost-control | ai-engineering | 84.5 (n=2) | 2 | 5 | 0 | llm budget control |
| developer-onboarding-docs-what-works-wha | technical-documentation | 85.0 (n=1) | 1 | 40 | 0 | developer onboarding documentation |
| memory-hierarchy-in-ai-systems | ai-engineering | 87.0 (n=1) | 1 | 15 | 0 | inclusion property in memory hiera |
| types-of-technical-documentation | technical-documentation | 93.0 (n=2) | 2 | 4 | 0 | different types of documentation |

### Has impressions, queries withheld — position exists, unseen — 35

These are the pages the old inference got wrong. They rank for something; Search Console simply will not say what.

| Page | Cluster | Impr | Clicks |
|---|---|---:|---:|
| kv-cache-eviction-accuracy | ai-engineering | 144 | 0 |
| embedding-models-compared | ai-engineering | 120 | 0 |
| local-wasm-vector-benchmarks | ai-engineering | 86 | 0 |
| rag-vs-memory | ai-engineering | 74 | 1 |
| voice-ai-latency-gemini-benchmark | ai-engineering | 71 | 0 |
| how-memory-works-in-deerflow | ai-engineering | 46 | 0 |
| semantic-caching-rag-optimization | ai-engineering | 46 | 0 |
| short-term-memory-for-ai-agents | ai-engineering | 46 | 0 |
| technical-writing-for-ai-products-the-new-ru | developer-experience | 20 | 1 |
| the-taxonomy-of-ai-agents | ai-engineering | 19 | 0 |
| lambda-calculus-ai-reasoning-benchmark | ai-engineering | 19 | 0 |
| mixture-of-experts-explained | ai-engineering | 19 | 0 |
| episodic-vs-semantic-vs-working-memory-agent | ai-engineering | 16 | 0 |
| beam-memory-benchmark | ai-engineering | 15 | 0 |
| memory-serialization-between-sessions | ai-engineering | 15 | 0 |
| the-memory-hierarchy-why-rag-is-not-enough | ai-engineering | 13 | 0 |
| how-memory-works-in-hyperagents | ai-engineering | 11 | 0 |
| contextual-compression-for-agent-memory | ai-engineering | 10 | 0 |
| agent-harnesses | ai-engineering | 10 | 0 |
| agentic-cli-benchmarks | ai-engineering | 10 | 0 |
| the-agent-design-space | ai-engineering | 8 | 0 |
| speculative-decoding-explained | ai-engineering | 7 | 0 |
| the-case-for-shorter-technical-documentation | technical-documentation | 7 | 0 |
| memory-versioning-and-audit-trails | ai-engineering | 5 | 0 |
| agent-vs-ai-assistant | ai-engineering | 4 | 0 |
| memory-attribution-errors | ai-engineering | 4 | 0 |
| model-context-protocol-explained | ai-engineering | 4 | 0 |
| technical-documentation-best-practices-teste | technical-documentation | 3 | 0 |
| technical-writing-for-engineers | developer-experience | 3 | 0 |
| context-windows-vs-memory | ai-engineering | 2 | 0 |
| how-to-organize-a-documentation-site | technical-documentation | 2 | 0 |
| internal-vs-external-documentation | technical-documentation | 2 | 0 |
| why-devtools-startups-lose-deals-over-bad-do | developer-experience | 2 | 0 |
| documentation-review-checklist-before-you-pu | technical-documentation | 1 | 0 |
| what-is-technical-documentation-and-what-sho | technical-documentation | 1 | 0 |

### Has impressions, but no human query behind them — 0

Ranking for brand, machine fan-out or an injected page is not ranking for a reader.

None.

### No impressions in the window — the only 'no position' state — 20

| Page | Cluster | Impr | Clicks |
|---|---|---:|---:|
| agent-memory-for-customer-support | ai-engineering | 0 | 0 |
| ai-crawlers-robots-txt-training-vs-citation | ai-search-optimization | 0 | 0 |
| api-documentation-best-practices-reference-g | technical-documentation | 0 | 0 |
| api-documentation-examples-what-the-best-dev | technical-documentation | 0 | 0 |
| api-documentation-template-the-pages-every-a | technical-documentation | 0 | 0 |
| api-documentation-tools-hands-on-comparison- | technical-documentation | 0 | 0 |
| coding-agent-setup-that-works | ai-engineering | 0 | 0 |
| developer-trust-hierarchy | developer-experience | 0 | 0 |
| documentation-accessibility-checklist | technical-documentation | 0 | 0 |
| documentation-style-guide-template | technical-documentation | 0 | 0 |
| how-to-document-multiple-product-versions | technical-documentation | 0 | 0 |
| how-to-write-task-based-documentation-headin | technical-documentation | 0 | 0 |
| llms-txt-examples-real-files-audited | ai-search-optimization | 0 | 0 |
| mcp-server-setup-guide | ai-engineering | 0 | 0 |
| prompt-caching-what-it-is-and-when-the-math- | ai-engineering | 0 | 0 |
| rag-vs-fine-tuning | ai-engineering | 0 | 0 |
| technical-writing-examples | technical-documentation | 0 | 0 |
| token-counting-isnt-optional-a-practical-gui | ai-engineering | 0 | 0 |
| what-a-documentation-homepage-must-help-user | technical-documentation | 0 | 0 |
| what-makes-a-page-extractable-by-answer-engi | ai-search-optimization | 0 | 0 |
