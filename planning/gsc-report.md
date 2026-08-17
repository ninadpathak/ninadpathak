# Search Console report

Appended by `tools/gsc_report.py`. Movement, decay, and striking distance,
per cluster. Search Console lags about three days, so every window ends three
days before its date, and every query-dimension figure is a floor rather than
a total because low-volume queries are withheld.

The machine keyword-salad fan-out is separated from human queries by the
heuristic documented in the tool's docstring. Families are collapsed and
reported, never silently dropped.

## 2026-08-17

Current window 2026-07-18 to 2026-08-14 (28d), against 2026-06-20 to 2026-07-17. Windows end 3 days back because Search Console lags.

**Sitewide** 11 clicks / 1573 impressions, avg pos 14.6 (prior 22 / 2775, pos 14.0).

Query dimension sees 314 impressions across 73 named queries — a **floor**, not a total: Search Console withholds low-volume queries.


### Cluster rollup

| # | Cluster | Pages | Clicks | Impressions | Avg pos |
|---:|---|---:|---:|---:|---:|
| 1 | Technical documentation & docs ops | 14 | 0 | 95 | 41.1 |
| 2 | Developer experience & DevRel | 4 | 1 | 32 | 13.9 |
| 3 | AI agents, memory, RAG, inference | 44 | 0 | 1191 | 11.5 |
| 4 | AI Overviews & AI-search citation | 1 | 0 | 2 | 18.0 |
| 5 | Reddit marketing | 0 | 0 | 0 | — |
| 6 | Forums & community building | 0 | 0 | 0 | — |
| 7 | Technical & community events | 0 | 0 | 0 | — |
| — | Pages in no cluster | 48 | 10 | 525 | 13.0 |

**Earning nothing:** cluster 5 (Reddit marketing), cluster 6 (Forums & community building), cluster 7 (Technical & community events).

**Post-path split:** 86 impressions on the canonical `/articles/` path against 1259 on the legacy `/blog/` path (94% legacy), plus 500 elsewhere. Both prefixes map to the same cluster here, since the slug identifies the post; a high legacy share means the migration is still unresolved.

### What moved


**Pages** — 29 moved more than 3 places.

| Page | Pos | Prior | Δpos | Clicks Δ | Impr Δ |
|---|---:|---:|---:|---:|---:|
| https://ninadpathak.com/blog/structured-outputs-llms-json-mode-functio | 45 | 23.8 | **-21.2** down | +0 | -18 |
| https://ninadpathak.com/ai-agent-architecture/ | 12.5 | 32.9 | **+20.4** up | +0 | -7 |
| https://ninadpathak.com/blog/how-memory-works-in-deerflow/ | 10 | 26.5 | **+16.5** up | +0 | -33 |
| https://ninadpathak.com/blog/memory-hierarchy-in-ai-systems/ | 18.2 | 34 | **+15.8** up | +0 | -5 |
| https://ninadpathak.com/portfolio/ | 4.5 | 20.1 | **+15.6** up | +0 | -43 |
| https://ninadpathak.com/blog/kv-cache-eviction-accuracy/ | 7.8 | 22.1 | **+14.3** up | +0 | -130 |
| https://ninadpathak.com/blog/engineering-velocity-documentation/ | 5 | 18.6 | **+13.6** up | +0 | -19 |
| https://ninadpathak.com/blog/mixture-of-experts-explained/ | 22 | 8.8 | **-13.2** down | +0 | -15 |
| https://ninadpathak.com/blog/llm-inference-optimization/ | 48 | 58.2 | **+10.2** up | +0 | -75 |
| https://ninadpathak.com/blog/short-term-memory-for-ai-agents/ | 17.7 | 27 | **+9.3** up | +0 | -14 |
| https://ninadpathak.com/blog/technical-writing-for-ai-products-the-new | 18.9 | 9.8 | **-9.0** down | +1 | +2 |
| https://ninadpathak.com/glossary/late-chunking/ | 38.4 | 29.6 | **-8.8** down | +0 | -3 |
| https://ninadpathak.com/blog/state-of-ai-agent-memory-2026/ | 10.3 | 18.6 | **+8.3** up | +0 | -23 |
| https://ninadpathak.com/glossary/agentic-router/ | 16.3 | 8.6 | **-7.8** down | +0 | -1 |
| https://ninadpathak.com/work/kiwisizing/ | 28.5 | 20.9 | **-7.6** down | -1 | +5 |
| https://ninadpathak.com/blog/embedding-models-compared/ | 31.3 | 24.1 | **-7.2** down | +0 | +1 |
| https://ninadpathak.com/work/delightchat/ | 27.4 | 20.2 | **-7.1** down | +0 | -2 |
| https://ninadpathak.com/blog/agentic-workflow-playbook/ | 14.4 | 7.5 | **-7.0** down | +0 | -26 |
| https://ninadpathak.com/blog/shared-vs-isolated-memory-multi-agent/ | 4.8 | 11.6 | **+6.8** up | +0 | -19 |
| https://ninadpathak.com/blog/how-stripes-technical-blog-became-a-compe | 13.2 | 6.8 | **-6.4** down | +0 | -52 |

**Queries** — 0 moved more than 3 places.

None.

### What decayed

52 page(s) lost impressions or position, prior window at least 5 impressions. A decaying page wants a refresh, not a new article.

| Page | Impr | Prior | Δ | Pos | Δpos |
|---|---:|---:|---:|---:|---:|
| https://ninadpathak.com/blog/how-anthropics-contextual-retrieval-chang | 755 | 1305 | -550 | 8.3 | -0.0 |
| https://ninadpathak.com/blog/kv-cache-eviction-accuracy/ | 5 | 135 | -130 | 7.8 | +14.3 |
| https://ninadpathak.com/about/ | 66 | 147 | -81 | 8.7 | -3.2 |
| https://ninadpathak.com/blog/llm-inference-optimization/ | 2 | 77 | -75 | 48 | +10.2 |
| https://ninadpathak.com/blog/local-wasm-vector-benchmarks/ | 14 | 69 | -55 | 7.3 | +1.1 |
| https://ninadpathak.com/blog/how-stripes-technical-blog-became-a-compe | 18 | 70 | -52 | 13.2 | -6.4 |
| https://ninadpathak.com/portfolio/ | 33 | 76 | -43 | 4.5 | +15.6 |
| https://ninadpathak.com/blog/rag-evaluation-metrics-what-actually-matt | 0 | 40 | -40 | — | — |
| https://ninadpathak.com/blog/how-memory-works-in-deerflow/ | 1 | 34 | -33 | 10 | +16.5 |
| https://ninadpathak.com/blog/how-memory-works-in-claude-code/ | 0 | 27 | -27 | — | — |
| https://ninadpathak.com/blog/agentic-workflow-playbook/ | 9 | 35 | -26 | 14.4 | -7.0 |
| https://ninadpathak.com/blog/state-of-open-source-memory-2026/ | 0 | 23 | -23 | — | — |
| https://ninadpathak.com/blog/state-of-ai-agent-memory-2026/ | 25 | 48 | -23 | 10.3 | +8.3 |
| https://ninadpathak.com/blog/shared-vs-isolated-memory-multi-agent/ | 5 | 24 | -19 | 4.8 | +6.8 |
| https://ninadpathak.com/blog/engineering-velocity-documentation/ | 4 | 23 | -19 | 5 | +13.6 |
| https://ninadpathak.com/blog/structured-outputs-llms-json-mode-functio | 1 | 19 | -18 | 45 | -21.2 |
| https://ninadpathak.com/blog/voice-ai-latency-gemini-benchmark/ | 25 | 43 | -18 | 9.2 | +0.6 |
| https://ninadpathak.com/blog/fine-tuning-vs-rag-for-agent-memory/ | 35 | 52 | -17 | 12 | -2.2 |
| https://ninadpathak.com/blog/semantic-caching-rag-optimization/ | 10 | 26 | -16 | 20.1 | +2.4 |
| https://ninadpathak.com/blog/mixture-of-experts-explained/ | 2 | 17 | -15 | 22 | -13.2 |

### What is close

46 queries sit in positions 4–30 carrying 204 impressions. Separated out: 28 machine fan-out variants (149 impressions), 3 brand (4), 1 pasted blob (1), 9 below the 3-impression floor (9).


**Human queries in reach — 5.**

| Query | Impr | Clicks | Pos | Stopword ratio |
|---|---:|---:|---:|---:|
| ai agent memory vs fine-tuning for domain-specific knowledge retention | 15 | 0 | 6.7 | 0.22 |
| how do you handle errors when ai agents make mistakes in production? | 11 | 0 | 10.6 | 0.5 |
| roman hresko | 8 | 0 | 22.4 | 0.0 |
| how do companies debug ai agents that fail in production? | 4 | 0 | 10.2 | 0.4 |
| technical tutorial | 3 | 0 | 10 | 0.0 |

Stopword ratio is printed as a weak corroborating signal only. It excludes nothing — terse human queries score zero.

**Machine fan-out families — 1.** Collapsed, not dropped. A real topic with many close human variants would cluster here too, so read this list rather than trusting the split blindly.

| Variants | Shared core | Impr | Clicks | Avg pos | Example |
|---:|---|---:|---:|---:|---|
| 28 | `anthropic contextual retrieval` | 149 | 0 | 8.7 | anthropic contextual retrieval bm25 embeddings reran |

## 2026-08-17

Current window 2026-07-18 to 2026-08-14 (28d), against 2026-06-20 to 2026-07-17. Windows end 3 days back because Search Console lags.

**Sitewide** 11 clicks / 1573 impressions, avg pos 14.6 (prior 22 / 2775, pos 14.0).

Query dimension sees 314 impressions across 73 named queries — a **floor**, not a total: Search Console withholds low-volume queries.


### Cluster rollup

| # | Cluster | Pages | Clicks | Impressions | Avg pos |
|---:|---|---:|---:|---:|---:|
| 1 | Technical documentation & docs ops | 14 | 0 | 95 | 41.1 |
| 2 | Developer experience & DevRel | 4 | 1 | 32 | 13.9 |
| 3 | AI agents, memory, RAG, inference | 44 | 0 | 1191 | 11.5 |
| 4 | AI Overviews & AI-search citation | 1 | 0 | 2 | 18.0 |
| 5 | Reddit marketing | 0 | 0 | 0 | — |
| 6 | Forums & community building | 0 | 0 | 0 | — |
| 7 | Technical & community events | 0 | 0 | 0 | — |
| — | homepage | 1 | 9 | 133 | 8.1 |
| — | /work/ (case studies) | 5 | 0 | 77 | 15.6 |
| — | /about/ (bio) | 1 | 0 | 66 | 8.7 |
| — | /glossary/ (25 terms, republished 2026-08-17) | 13 | 0 | 63 | 35.2 |
| — | /contact/ | 1 | 0 | 36 | 7.2 |
| — | /portfolio/ | 1 | 0 | 33 | 4.5 |
| — | /projects/ | 1 | 0 | 26 | 6.2 |
| — | /static/ (assets, should not rank) | 15 | 0 | 21 | 34.9 |
| — | /topics/ | 1 | 0 | 18 | 7.3 |
| — | /blog/ | 3 | 0 | 17 | 5.1 |
| — | /terms/ | 1 | 0 | 16 | 4.6 |
| — | /articles/ | 1 | 1 | 10 | 4.6 |
| — | /ai-workflows/ | 1 | 0 | 3 | 22.7 |
| — | /technical-writing/ | 1 | 0 | 3 | 7.7 |
| — | /ai-agent-architecture/ | 1 | 0 | 2 | 12.5 |
| — | /ai-agent-memory/ | 1 | 0 | 1 | 10.0 |

**Earning nothing:** cluster 5 (Reddit marketing), cluster 6 (Forums & community building), cluster 7 (Technical & community events).

**Post-path split:** 86 impressions on the canonical `/articles/` path against 1259 on the legacy `/blog/` path (94% legacy), plus 500 elsewhere. Both prefixes map to the same cluster here, since the slug identifies the post; a high legacy share means the migration is still unresolved.

### What moved


**Pages** — 29 moved more than 3 places.

| Page | Pos | Prior | Δpos | Clicks Δ | Impr Δ |
|---|---:|---:|---:|---:|---:|
| https://ninadpathak.com/blog/structured-outputs-llms-json-mode-functio | 45 | 23.8 | **-21.2** down | +0 | -18 |
| https://ninadpathak.com/ai-agent-architecture/ | 12.5 | 32.9 | **+20.4** up | +0 | -7 |
| https://ninadpathak.com/blog/how-memory-works-in-deerflow/ | 10 | 26.5 | **+16.5** up | +0 | -33 |
| https://ninadpathak.com/blog/memory-hierarchy-in-ai-systems/ | 18.2 | 34 | **+15.8** up | +0 | -5 |
| https://ninadpathak.com/portfolio/ | 4.5 | 20.1 | **+15.6** up | +0 | -43 |
| https://ninadpathak.com/blog/kv-cache-eviction-accuracy/ | 7.8 | 22.1 | **+14.3** up | +0 | -130 |
| https://ninadpathak.com/blog/engineering-velocity-documentation/ | 5 | 18.6 | **+13.6** up | +0 | -19 |
| https://ninadpathak.com/blog/mixture-of-experts-explained/ | 22 | 8.8 | **-13.2** down | +0 | -15 |
| https://ninadpathak.com/blog/llm-inference-optimization/ | 48 | 58.2 | **+10.2** up | +0 | -75 |
| https://ninadpathak.com/blog/short-term-memory-for-ai-agents/ | 17.7 | 27 | **+9.3** up | +0 | -14 |
| https://ninadpathak.com/blog/technical-writing-for-ai-products-the-new | 18.9 | 9.8 | **-9.0** down | +1 | +2 |
| https://ninadpathak.com/glossary/late-chunking/ | 38.4 | 29.6 | **-8.8** down | +0 | -3 |
| https://ninadpathak.com/blog/state-of-ai-agent-memory-2026/ | 10.3 | 18.6 | **+8.3** up | +0 | -23 |
| https://ninadpathak.com/glossary/agentic-router/ | 16.3 | 8.6 | **-7.8** down | +0 | -1 |
| https://ninadpathak.com/work/kiwisizing/ | 28.5 | 20.9 | **-7.6** down | -1 | +5 |
| https://ninadpathak.com/blog/embedding-models-compared/ | 31.3 | 24.1 | **-7.2** down | +0 | +1 |
| https://ninadpathak.com/work/delightchat/ | 27.4 | 20.2 | **-7.1** down | +0 | -2 |
| https://ninadpathak.com/blog/agentic-workflow-playbook/ | 14.4 | 7.5 | **-7.0** down | +0 | -26 |
| https://ninadpathak.com/blog/shared-vs-isolated-memory-multi-agent/ | 4.8 | 11.6 | **+6.8** up | +0 | -19 |
| https://ninadpathak.com/blog/how-stripes-technical-blog-became-a-compe | 13.2 | 6.8 | **-6.4** down | +0 | -52 |

**Queries** — 0 moved more than 3 places.

None.

### What decayed

52 page(s) lost impressions or position, prior window at least 5 impressions. A decaying page wants a refresh, not a new article.

| Page | Impr | Prior | Δ | Pos | Δpos |
|---|---:|---:|---:|---:|---:|
| https://ninadpathak.com/blog/how-anthropics-contextual-retrieval-chang | 755 | 1305 | -550 | 8.3 | -0.0 |
| https://ninadpathak.com/blog/kv-cache-eviction-accuracy/ | 5 | 135 | -130 | 7.8 | +14.3 |
| https://ninadpathak.com/about/ | 66 | 147 | -81 | 8.7 | -3.2 |
| https://ninadpathak.com/blog/llm-inference-optimization/ | 2 | 77 | -75 | 48 | +10.2 |
| https://ninadpathak.com/blog/local-wasm-vector-benchmarks/ | 14 | 69 | -55 | 7.3 | +1.1 |
| https://ninadpathak.com/blog/how-stripes-technical-blog-became-a-compe | 18 | 70 | -52 | 13.2 | -6.4 |
| https://ninadpathak.com/portfolio/ | 33 | 76 | -43 | 4.5 | +15.6 |
| https://ninadpathak.com/blog/rag-evaluation-metrics-what-actually-matt | 0 | 40 | -40 | — | — |
| https://ninadpathak.com/blog/how-memory-works-in-deerflow/ | 1 | 34 | -33 | 10 | +16.5 |
| https://ninadpathak.com/blog/how-memory-works-in-claude-code/ | 0 | 27 | -27 | — | — |
| https://ninadpathak.com/blog/agentic-workflow-playbook/ | 9 | 35 | -26 | 14.4 | -7.0 |
| https://ninadpathak.com/blog/state-of-open-source-memory-2026/ | 0 | 23 | -23 | — | — |
| https://ninadpathak.com/blog/state-of-ai-agent-memory-2026/ | 25 | 48 | -23 | 10.3 | +8.3 |
| https://ninadpathak.com/blog/shared-vs-isolated-memory-multi-agent/ | 5 | 24 | -19 | 4.8 | +6.8 |
| https://ninadpathak.com/blog/engineering-velocity-documentation/ | 4 | 23 | -19 | 5 | +13.6 |
| https://ninadpathak.com/blog/structured-outputs-llms-json-mode-functio | 1 | 19 | -18 | 45 | -21.2 |
| https://ninadpathak.com/blog/voice-ai-latency-gemini-benchmark/ | 25 | 43 | -18 | 9.2 | +0.6 |
| https://ninadpathak.com/blog/fine-tuning-vs-rag-for-agent-memory/ | 35 | 52 | -17 | 12 | -2.2 |
| https://ninadpathak.com/blog/semantic-caching-rag-optimization/ | 10 | 26 | -16 | 20.1 | +2.4 |
| https://ninadpathak.com/blog/mixture-of-experts-explained/ | 2 | 17 | -15 | 22 | -13.2 |

### What is close

46 queries sit in positions 4–30 carrying 204 impressions. Separated out: 28 machine fan-out variants (149 impressions), 3 brand (4), 1 pasted blob (1), 9 below the 3-impression floor (9).


**Human queries in reach — 5.**

| Query | Impr | Clicks | Pos | Stopword ratio |
|---|---:|---:|---:|---:|
| ai agent memory vs fine-tuning for domain-specific knowledge retention | 15 | 0 | 6.7 | 0.22 |
| how do you handle errors when ai agents make mistakes in production? | 11 | 0 | 10.6 | 0.5 |
| roman hresko | 8 | 0 | 22.4 | 0.0 |
| how do companies debug ai agents that fail in production? | 4 | 0 | 10.2 | 0.4 |
| technical tutorial | 3 | 0 | 10 | 0.0 |

Stopword ratio is printed as a weak corroborating signal only. It excludes nothing — terse human queries score zero.

**Machine fan-out families — 1.** Collapsed, not dropped. A real topic with many close human variants would cluster here too, so read this list rather than trusting the split blindly.

| Variants | Shared core | Impr | Clicks | Avg pos | Example |
|---:|---|---:|---:|---:|---|
| 28 | `anthropic contextual retrieval` | 149 | 0 | 8.7 | anthropic contextual retrieval bm25 embeddings reran |

## 2026-08-17

Current window 2026-07-18 to 2026-08-14 (28d), against 2026-06-20 to 2026-07-17. Windows end 3 days back because Search Console lags.

**Sitewide** 11 clicks / 1573 impressions, avg pos 14.6 (prior 22 / 2775, pos 14.0).

Query dimension sees 314 impressions across 73 named queries — a **floor**, not a total: Search Console withholds low-volume queries.


### Cluster rollup

| # | Cluster | Pages | Clicks | Impressions | Avg pos |
|---:|---|---:|---:|---:|---:|
| 1 | Technical documentation & docs ops | 14 | 0 | 95 | 41.1 |
| 2 | Developer experience & DevRel | 4 | 1 | 32 | 13.9 |
| 3 | AI agents, memory, RAG, inference | 44 | 0 | 1191 | 11.5 |
| 4 | AI Overviews & AI-search citation | 1 | 0 | 2 | 18.0 |
| 5 | Distribution: Reddit, forums, communities, events | 0 | 0 | 0 | — |
| — | homepage | 1 | 9 | 133 | 8.1 |
| — | /work/ (case studies) | 5 | 0 | 77 | 15.6 |
| — | /about/ (bio) | 1 | 0 | 66 | 8.7 |
| — | /glossary/ (25 terms, republished 2026-08-17) | 13 | 0 | 63 | 35.2 |
| — | /contact/ | 1 | 0 | 36 | 7.2 |
| — | /portfolio/ | 1 | 0 | 33 | 4.5 |
| — | /projects/ | 1 | 0 | 26 | 6.2 |
| — | /static/ (assets, should not rank) | 15 | 0 | 21 | 34.9 |
| — | /topics/ | 1 | 0 | 18 | 7.3 |
| — | /blog/ | 3 | 0 | 17 | 5.1 |
| — | /terms/ | 1 | 0 | 16 | 4.6 |
| — | /articles/ | 1 | 1 | 10 | 4.6 |
| — | /ai-workflows/ | 1 | 0 | 3 | 22.7 |
| — | /technical-writing/ | 1 | 0 | 3 | 7.7 |
| — | /ai-agent-architecture/ | 1 | 0 | 2 | 12.5 |
| — | /ai-agent-memory/ | 1 | 0 | 1 | 10.0 |

**Earning nothing:** cluster 5 (Distribution: Reddit, forums, communities, events).

**Post-path split:** 86 impressions on the canonical `/articles/` path against 1259 on the legacy `/blog/` path (94% legacy), plus 500 elsewhere. Both prefixes map to the same cluster here, since the slug identifies the post; a high legacy share means the migration is still unresolved.

### What moved


**Pages** — 29 moved more than 3 places.

| Page | Pos | Prior | Δpos | Clicks Δ | Impr Δ |
|---|---:|---:|---:|---:|---:|
| https://ninadpathak.com/blog/structured-outputs-llms-json-mode-functio | 45 | 23.8 | **-21.2** down | +0 | -18 |
| https://ninadpathak.com/ai-agent-architecture/ | 12.5 | 32.9 | **+20.4** up | +0 | -7 |
| https://ninadpathak.com/blog/how-memory-works-in-deerflow/ | 10 | 26.5 | **+16.5** up | +0 | -33 |
| https://ninadpathak.com/blog/memory-hierarchy-in-ai-systems/ | 18.2 | 34 | **+15.8** up | +0 | -5 |
| https://ninadpathak.com/portfolio/ | 4.5 | 20.1 | **+15.6** up | +0 | -43 |
| https://ninadpathak.com/blog/kv-cache-eviction-accuracy/ | 7.8 | 22.1 | **+14.3** up | +0 | -130 |
| https://ninadpathak.com/blog/engineering-velocity-documentation/ | 5 | 18.6 | **+13.6** up | +0 | -19 |
| https://ninadpathak.com/blog/mixture-of-experts-explained/ | 22 | 8.8 | **-13.2** down | +0 | -15 |
| https://ninadpathak.com/blog/llm-inference-optimization/ | 48 | 58.2 | **+10.2** up | +0 | -75 |
| https://ninadpathak.com/blog/short-term-memory-for-ai-agents/ | 17.7 | 27 | **+9.3** up | +0 | -14 |
| https://ninadpathak.com/blog/technical-writing-for-ai-products-the-new | 18.9 | 9.8 | **-9.0** down | +1 | +2 |
| https://ninadpathak.com/glossary/late-chunking/ | 38.4 | 29.6 | **-8.8** down | +0 | -3 |
| https://ninadpathak.com/blog/state-of-ai-agent-memory-2026/ | 10.3 | 18.6 | **+8.3** up | +0 | -23 |
| https://ninadpathak.com/glossary/agentic-router/ | 16.3 | 8.6 | **-7.8** down | +0 | -1 |
| https://ninadpathak.com/work/kiwisizing/ | 28.5 | 20.9 | **-7.6** down | -1 | +5 |
| https://ninadpathak.com/blog/embedding-models-compared/ | 31.3 | 24.1 | **-7.2** down | +0 | +1 |
| https://ninadpathak.com/work/delightchat/ | 27.4 | 20.2 | **-7.1** down | +0 | -2 |
| https://ninadpathak.com/blog/agentic-workflow-playbook/ | 14.4 | 7.5 | **-7.0** down | +0 | -26 |
| https://ninadpathak.com/blog/shared-vs-isolated-memory-multi-agent/ | 4.8 | 11.6 | **+6.8** up | +0 | -19 |
| https://ninadpathak.com/blog/how-stripes-technical-blog-became-a-compe | 13.2 | 6.8 | **-6.4** down | +0 | -52 |

**Queries** — 0 moved more than 3 places.

None.

### What decayed

52 page(s) lost impressions or position, prior window at least 5 impressions. A decaying page wants a refresh, not a new article.

| Page | Impr | Prior | Δ | Pos | Δpos |
|---|---:|---:|---:|---:|---:|
| https://ninadpathak.com/blog/how-anthropics-contextual-retrieval-chang | 755 | 1305 | -550 | 8.3 | -0.0 |
| https://ninadpathak.com/blog/kv-cache-eviction-accuracy/ | 5 | 135 | -130 | 7.8 | +14.3 |
| https://ninadpathak.com/about/ | 66 | 147 | -81 | 8.7 | -3.2 |
| https://ninadpathak.com/blog/llm-inference-optimization/ | 2 | 77 | -75 | 48 | +10.2 |
| https://ninadpathak.com/blog/local-wasm-vector-benchmarks/ | 14 | 69 | -55 | 7.3 | +1.1 |
| https://ninadpathak.com/blog/how-stripes-technical-blog-became-a-compe | 18 | 70 | -52 | 13.2 | -6.4 |
| https://ninadpathak.com/portfolio/ | 33 | 76 | -43 | 4.5 | +15.6 |
| https://ninadpathak.com/blog/rag-evaluation-metrics-what-actually-matt | 0 | 40 | -40 | — | — |
| https://ninadpathak.com/blog/how-memory-works-in-deerflow/ | 1 | 34 | -33 | 10 | +16.5 |
| https://ninadpathak.com/blog/how-memory-works-in-claude-code/ | 0 | 27 | -27 | — | — |
| https://ninadpathak.com/blog/agentic-workflow-playbook/ | 9 | 35 | -26 | 14.4 | -7.0 |
| https://ninadpathak.com/blog/state-of-open-source-memory-2026/ | 0 | 23 | -23 | — | — |
| https://ninadpathak.com/blog/state-of-ai-agent-memory-2026/ | 25 | 48 | -23 | 10.3 | +8.3 |
| https://ninadpathak.com/blog/shared-vs-isolated-memory-multi-agent/ | 5 | 24 | -19 | 4.8 | +6.8 |
| https://ninadpathak.com/blog/engineering-velocity-documentation/ | 4 | 23 | -19 | 5 | +13.6 |
| https://ninadpathak.com/blog/structured-outputs-llms-json-mode-functio | 1 | 19 | -18 | 45 | -21.2 |
| https://ninadpathak.com/blog/voice-ai-latency-gemini-benchmark/ | 25 | 43 | -18 | 9.2 | +0.6 |
| https://ninadpathak.com/blog/fine-tuning-vs-rag-for-agent-memory/ | 35 | 52 | -17 | 12 | -2.2 |
| https://ninadpathak.com/blog/semantic-caching-rag-optimization/ | 10 | 26 | -16 | 20.1 | +2.4 |
| https://ninadpathak.com/blog/mixture-of-experts-explained/ | 2 | 17 | -15 | 22 | -13.2 |

### What is close

46 queries sit in positions 4–30 carrying 204 impressions. Separated out: 28 machine fan-out variants (149 impressions), 3 brand (4), 1 pasted blob (1), 9 below the 3-impression floor (9).


**Human queries in reach — 5.**

| Query | Impr | Clicks | Pos | Stopword ratio |
|---|---:|---:|---:|---:|
| ai agent memory vs fine-tuning for domain-specific knowledge retention | 15 | 0 | 6.7 | 0.22 |
| how do you handle errors when ai agents make mistakes in production? | 11 | 0 | 10.6 | 0.5 |
| roman hresko | 8 | 0 | 22.4 | 0.0 |
| how do companies debug ai agents that fail in production? | 4 | 0 | 10.2 | 0.4 |
| technical tutorial | 3 | 0 | 10 | 0.0 |

Stopword ratio is printed as a weak corroborating signal only. It excludes nothing — terse human queries score zero.

**Machine fan-out families — 1.** Collapsed, not dropped. A real topic with many close human variants would cluster here too, so read this list rather than trusting the split blindly.

| Variants | Shared core | Impr | Clicks | Avg pos | Example |
|---:|---|---:|---:|---:|---|
| 28 | `anthropic contextual retrieval` | 149 | 0 | 8.7 | anthropic contextual retrieval bm25 embeddings reran |
