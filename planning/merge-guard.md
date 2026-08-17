# Pre-merge Search Console guard

Maintained by `tools/gsc_merge_guard.py`, one authoritative section per date. It tests whether planned merge sources and
targets share named first-party search demand, while preserving withheld demand as
unknown. It does not decide content equivalence.

## 2026-08-17 — pre-merge Search Console guard

Current window 2026-05-17 to 2026-08-14 (90d); history 2025-04-04 to 2026-08-14. Both end 3 days back.

**Named queries, human impressions and overlap counts are FLOORS.** Exact shared queries are positive evidence of overlap; no observed overlap is not evidence of distinct intent because Search Console withholds low-volume queries. Page impressions and clicks are complete.

- Current sitewide query coverage: 1142 of 6480 page-dimension impressions (17.6%).
- Current merge pages query coverage: 128 of 710 page-dimension impressions (18.0%).
- Historical sitewide query coverage: 17027 of 36523 page-dimension impressions (46.6%).
- Historical merge pages query coverage: 128 of 713 page-dimension impressions (18.0%).

**4** `no-source-demand-observed`, **1** `retire-no-demand-observed`, **6** `review-source-demand`, **10** `withheld-source-demand`.

| Source → target | Disposition | Execution | Current source | 90d position | Historical human queries | Exact shared | Verdict |
|---|---|---|---|---|---:|---:|---|
| `state-of-open-source-memory-2026` → `state-of-ai-agent-memory-2026` | merge | `pending` | `measured`; 35 impr | 9.9 (35 impr) | 1 | 0 | `review-source-demand` |
| `beam-memory-benchmark` → `context-windows-vs-memory` | merge | `pending` | `withheld`; 15 impr | 12.9 (15 impr) | 0 | 0 | `withheld-source-demand` |
| `memory-hierarchy-in-ai-systems` → `ai-memory-management-for-llms` | merge | `pending` | `measured`; 15 impr | 28.7 (15 impr) | 1 | 0 | `review-source-demand` |
| `the-memory-hierarchy-why-rag-is-not-enough` → `ai-memory-management-for-llms` | merge | `pending` | `withheld`; 13 impr | 8.2 (13 impr) | 0 | 0 | `withheld-source-demand` |
| `asymmetric-retrieval-agent-memory` → `rag-vs-memory` | merge | `pending` | `measured`; 12 impr | 18.3 (12 impr) | 1 | 0 | `review-source-demand` |
| `how-memory-works-in-hyperagents` → `how-memory-works-in-deerflow` | merge | `pending` | `withheld`; 11 impr | 11.2 (11 impr) | 0 | 0 | `withheld-source-demand` |
| `contextual-compression-for-agent-memory` → `short-term-memory-for-ai-agents` | merge | `pending` | `withheld`; 10 impr | 12.0 (10 impr) | 0 | 0 | `withheld-source-demand` |
| `agentic-cli-benchmarks` → `best-llms-for-coding` | merge | `pending` | `withheld`; 10 impr | 12.5 (10 impr) | 0 | 0 | `withheld-source-demand` |
| `the-agent-design-space` → `the-taxonomy-of-ai-agents` | merge | `pending` | `withheld`; 8 impr | 12.6 (8 impr) | 0 | 0 | `withheld-source-demand` |
| `speculative-decoding-explained` → `llm-inference-optimization` | merge | `pending` | `withheld`; 7 impr | 32.3 (7 impr) | 0 | 0 | `withheld-source-demand` |
| `time-to-first-token-ttft` → `llm-inference-optimization` | merge | `pending` | `measured`; 7 impr | 47.4 (7 impr) | 3 | 0 | `review-source-demand` |
| `memory-versioning-and-audit-trails` → `memory-serialization-between-sessions` | merge | `pending` | `withheld`; 5 impr | 3.4 (5 impr) | 0 | 0 | `withheld-source-demand` |
| `llm-context-windows-explained` → `context-windows-vs-memory` | merge | `pending` | `measured`; 5 impr | 14.8 (5 impr) | 1 | 0 | `review-source-demand` |
| `memory-attribution-errors` → `ai-memory-management-for-llms` | merge | `pending` | `withheld`; 4 impr | 6.5 (4 impr) | 0 | 0 | `withheld-source-demand` |
| `agent-vs-ai-assistant` → `the-taxonomy-of-ai-agents` | merge | `pending` | `withheld`; 4 impr | 6.5 (4 impr) | 0 | 0 | `withheld-source-demand` |
| `why-ai-agents-keep-failing-in-production` → `production-ai-agent-errors` | merge | `pending` | `measured`; 4 impr | 10.2 (4 impr) | 1 | 0 | `review-source-demand` |
| `agent-memory-for-customer-support` → `state-of-ai-agent-memory-2026` | retire | `pending` | `never-impressed`; 0 impr | — | 0 | 0 | `retire-no-demand-observed` |
| `token-counting-isnt-optional-a-practical-guide-to-llm-cost-control` → `llm-token-budgets-cost-control` | merge | `pending` | `never-impressed`; 0 impr | — | 0 | 0 | `no-source-demand-observed` |
| `rag-vs-fine-tuning` → `fine-tuning-vs-rag-for-agent-memory` | merge | `pending` | `never-impressed`; 0 impr | — | 0 | 0 | `no-source-demand-observed` |
| `mcp-server-setup-guide` → `model-context-protocol-explained` | merge | `pending` | `never-impressed`; 0 impr | — | 0 | 0 | `no-source-demand-observed` |
| `coding-agent-setup-that-works` → `why-coding-agents-lose-their-memory` | merge | `pending` | `never-impressed`; 0 impr | — | 0 | 0 | `no-source-demand-observed` |

### Named source demand requiring preservation review


**`state-of-open-source-memory-2026` → `state-of-ai-agent-memory-2026` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| ai memory systems research 2026 | 2 | 8.5 |

**`memory-hierarchy-in-ai-systems` → `ai-memory-management-for-llms` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| inclusion property in memory hierarchy | 1 | 87.0 |

**`asymmetric-retrieval-agent-memory` → `rag-vs-memory` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| hybrid retrieval for agent memory | 1 | 72.0 |

**`time-to-first-token-ttft` → `llm-inference-optimization` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| ttft | 4 | 50.2 |
| time to first token | 2 | 31.5 |
| time to first token optimization | 1 | 68.0 |

**`llm-context-windows-explained` → `context-windows-vs-memory` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| long context windows | 1 | 5.0 |

**`why-ai-agents-keep-failing-in-production` → `production-ai-agent-errors` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| how do companies debug ai agents that fail in production? | 4 | 10.2 |

### What this guard can and cannot decide

- `shared-named-demand` supports overlap but does not prove two pages should merge.
- `review-source-demand` means the source owns visible demand not observed on the target; the carried prose must answer it before redirecting.
- `withheld-source-demand` means a position exists but the query is private. It is an unknown, never a zero.
- Exact strings undercount semantic overlap, and page averages move when query mix moves. This report does not infer either one.
- Content equivalence, redirect correctness and carried ideas remain separate gates.

## 2026-08-18 — pre-merge Search Console guard

Current window 2026-05-18 to 2026-08-15 (90d); history 2025-04-04 to 2026-08-15. Both end 3 days back.

**Named queries, human impressions and overlap counts are FLOORS.** Exact shared queries are positive evidence of overlap; no observed overlap is not evidence of distinct intent because Search Console withholds low-volume queries. Page impressions and clicks are complete.

- Current sitewide query coverage: 1156 of 6510 page-dimension impressions (17.8%).
- Current merge pages query coverage: 128 of 710 page-dimension impressions (18.0%).
- Historical sitewide query coverage: 17043 of 36567 page-dimension impressions (46.6%).
- Historical merge pages query coverage: 128 of 713 page-dimension impressions (18.0%).

**4** `no-source-demand-observed`, **1** `retire-no-demand-observed`, **6** `review-source-demand`, **10** `withheld-source-demand`.

| Source → target | Disposition | Execution | Current source | 90d position | Historical human queries | Exact shared | Verdict |
|---|---|---|---|---|---:|---:|---|
| `state-of-open-source-memory-2026` → `state-of-ai-agent-memory-2026` | merge | `already-merged` | `measured`; 35 impr | 9.9 (35 impr) | 1 | 0 | `review-source-demand` |
| `beam-memory-benchmark` → `context-windows-vs-memory` | merge | `already-merged` | `withheld`; 15 impr | 12.9 (15 impr) | 0 | 0 | `withheld-source-demand` |
| `memory-hierarchy-in-ai-systems` → `ai-memory-management-for-llms` | merge | `already-merged` | `measured`; 15 impr | 28.7 (15 impr) | 1 | 0 | `review-source-demand` |
| `the-memory-hierarchy-why-rag-is-not-enough` → `ai-memory-management-for-llms` | merge | `already-merged` | `withheld`; 13 impr | 8.2 (13 impr) | 0 | 0 | `withheld-source-demand` |
| `asymmetric-retrieval-agent-memory` → `rag-vs-memory` | merge | `pending` | `measured`; 12 impr | 18.3 (12 impr) | 1 | 0 | `review-source-demand` |
| `how-memory-works-in-hyperagents` → `how-memory-works-in-deerflow` | merge | `pending` | `withheld`; 11 impr | 11.2 (11 impr) | 0 | 0 | `withheld-source-demand` |
| `contextual-compression-for-agent-memory` → `short-term-memory-for-ai-agents` | merge | `pending` | `withheld`; 10 impr | 12.0 (10 impr) | 0 | 0 | `withheld-source-demand` |
| `agentic-cli-benchmarks` → `best-llms-for-coding` | merge | `pending` | `withheld`; 10 impr | 12.5 (10 impr) | 0 | 0 | `withheld-source-demand` |
| `the-agent-design-space` → `the-taxonomy-of-ai-agents` | merge | `pending` | `withheld`; 8 impr | 12.6 (8 impr) | 0 | 0 | `withheld-source-demand` |
| `speculative-decoding-explained` → `llm-inference-optimization` | merge | `pending` | `withheld`; 7 impr | 32.3 (7 impr) | 0 | 0 | `withheld-source-demand` |
| `time-to-first-token-ttft` → `llm-inference-optimization` | merge | `pending` | `measured`; 7 impr | 47.4 (7 impr) | 3 | 0 | `review-source-demand` |
| `memory-versioning-and-audit-trails` → `memory-serialization-between-sessions` | merge | `pending` | `withheld`; 5 impr | 3.4 (5 impr) | 0 | 0 | `withheld-source-demand` |
| `llm-context-windows-explained` → `context-windows-vs-memory` | merge | `pending` | `measured`; 5 impr | 14.8 (5 impr) | 1 | 0 | `review-source-demand` |
| `memory-attribution-errors` → `ai-memory-management-for-llms` | merge | `already-merged` | `withheld`; 4 impr | 6.5 (4 impr) | 0 | 0 | `withheld-source-demand` |
| `agent-vs-ai-assistant` → `the-taxonomy-of-ai-agents` | merge | `pending` | `withheld`; 4 impr | 6.5 (4 impr) | 0 | 0 | `withheld-source-demand` |
| `why-ai-agents-keep-failing-in-production` → `production-ai-agent-errors` | merge | `pending` | `measured`; 4 impr | 10.2 (4 impr) | 1 | 0 | `review-source-demand` |
| `agent-memory-for-customer-support` → `state-of-ai-agent-memory-2026` | retire | `already-retired` | `never-impressed`; 0 impr | — | 0 | 0 | `retire-no-demand-observed` |
| `token-counting-isnt-optional-a-practical-guide-to-llm-cost-control` → `llm-token-budgets-cost-control` | merge | `pending` | `never-impressed`; 0 impr | — | 0 | 0 | `no-source-demand-observed` |
| `rag-vs-fine-tuning` → `fine-tuning-vs-rag-for-agent-memory` | merge | `already-merged` | `never-impressed`; 0 impr | — | 0 | 0 | `no-source-demand-observed` |
| `mcp-server-setup-guide` → `model-context-protocol-explained` | merge | `pending` | `never-impressed`; 0 impr | — | 0 | 0 | `no-source-demand-observed` |
| `coding-agent-setup-that-works` → `why-coding-agents-lose-their-memory` | merge | `pending` | `never-impressed`; 0 impr | — | 0 | 0 | `no-source-demand-observed` |

### Named source demand requiring preservation review


**`state-of-open-source-memory-2026` → `state-of-ai-agent-memory-2026` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| ai memory systems research 2026 | 2 | 8.5 |

**`memory-hierarchy-in-ai-systems` → `ai-memory-management-for-llms` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| inclusion property in memory hierarchy | 1 | 87.0 |

**`asymmetric-retrieval-agent-memory` → `rag-vs-memory` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| hybrid retrieval for agent memory | 1 | 72.0 |

**`time-to-first-token-ttft` → `llm-inference-optimization` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| ttft | 4 | 50.2 |
| time to first token | 2 | 31.5 |
| time to first token optimization | 1 | 68.0 |

**`llm-context-windows-explained` → `context-windows-vs-memory` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| long context windows | 1 | 5.0 |

**`why-ai-agents-keep-failing-in-production` → `production-ai-agent-errors` — `review-source-demand`**


| Source query not observed on target | Impr | Position |
|---|---:|---:|
| how do companies debug ai agents that fail in production? | 4 | 10.2 |

### What this guard can and cannot decide

- `shared-named-demand` supports overlap but does not prove two pages should merge.
- `review-source-demand` means the source owns visible demand not observed on the target; the carried prose must answer it before redirecting.
- `withheld-source-demand` means a position exists but the query is private. It is an unknown, never a zero.
- Exact strings undercount semantic overlap, and page averages move when query mix moves. This report does not infer either one.
- Content equivalence, redirect correctness and carried ideas remain separate gates.
