# Claim-candidate review: repaired-scanner delta

**Reviewed:** 2026-08-17  
**Detector change:** `643d2e7f`  
**Scope:** only candidates newly exposed by the repaired indirect-experience patterns

## Result

The old and repaired scanners report 81 and 92 candidates respectively on the integrated
90-post corpus: **11 new hits**. One is an earned present-tense judgment and needs no edit. The
other **10 are unsupported event or measurement claims**: three should leave the corpus through
already-planned cluster-3 dispositions, and seven need evidence-neutral rewrites on retained
pages.

This is a review specification, not publishable prose. It authorizes no redirect or status
change. Cluster-3 execution remains frozen behind `tools/gsc_merge_guard.py` and the preservation
requirements in `planning/cluster-3-batch-1-merge-spec.md`.

## KEEP: detector candidate, not an evidence defect

| Page | Passage | Decision | Why |
|---|---|---|---|
| `the-case-for-shorter-technical-documentation` | “I follow four minimalist principles in my work.” | **KEEP** | A present-tense statement of the author's own editorial rule. It asserts no client, past event, measurement, or outcome. |

## Remove through an already-planned disposition; do not repair in place

| Page | Newly visible passage | Decision and merge acceptance criterion |
|---|---|---|
| `agent-memory-for-customer-support` | “I spent three weeks building a customer support agent for a SaaS product…” | **CUT with the retiring page.** Do not transplant this alleged project into `state-of-ai-agent-memory-2026`. |
| `agent-memory-for-customer-support` | “Forcing that attribution reduced attribution errors by roughly 60% in my testing.” | **CUT with the retiring page.** There is no test artifact, denominator, fixture, or result record. Carry no figure. |
| `memory-attribution-errors` | “I spent three days chasing a bug where a customer support agent kept quoting a pricing policy…” | **CUT during its merge into `ai-memory-management-for-llms`.** Preserve attribution as a named failure class and its observable symptoms, as the merge spec requires; do not preserve the customer incident or duration. |

These cuts do not relax the first-party demand guard. In particular, batch 1 still has to keep
the layered-memory job in `ai-memory-management-for-llms` and the `ai memory systems research
2026` job in `state-of-ai-agent-memory-2026` before any source redirects.

## REWRITE on retained pages

Keep the useful technical point, but remove the asserted personal event, team sample, or
unreproduced measurement. A direct present-tense judgment is acceptable where identified below;
do not invent a study or citation to preserve first person.

| Page | Newly visible passage | Required repair |
|---|---|---|
| `the-taxonomy-of-ai-agents` | “I keep seeing teams treat schema design as an afterthought…” | State the schema-design failure mode directly. Do not claim repeated team observations or production incidents. |
| `multi-agent-vs-single-agent-tradeoffs` | “Context is the limit I kept hitting.” | State context accumulation as the single-agent trade-off. Do not imply a personal build history. |
| `why-coding-agents-lose-their-memory` | “What I see most often is an agent that has access to all three layers…” | Describe the layer-confusion failure directly. Do not claim a frequency or observed population. |
| `agent-vs-ai-assistant` | “I wrote about the production errors I keep seeing… the root cause in almost every case…” | Keep the concrete stop-condition/tool-retry explanation that follows, but remove the repeated-observation and “almost every case” claims. |
| `agentic-workflow-playbook` | “Handing an agent a one-line request… is the failure I see most often.” | Keep the author’s workflow rule and the ambiguity example; remove the unsupported frequency claim. |
| `memory-serialization-between-sessions` | “Re-processing a 500-message history added roughly 3 seconds… in my measurements, on a Claude Sonnet call…” | Remove the 500-message/3-second/model measurement unless a reproducible fixture, model/version, date, raw result, and runner are committed. Preserve only the qualitative latency-and-token trade-off otherwise. |
| `memory-serialization-between-sessions` | “10,000 requests per minute… msgpack or Protocol Buffers cut serialization overhead by 5x in my benchmarks.” | Remove the throughput scenario as personal evidence and the 5× result unless a benchmark artifact and environment are committed. Preserve the readable-JSON versus binary-format trade-off without a number. |

## Handoff gates

1. The writer changes only the seven retained-page passages above; it does not separately polish
   the three source passages scheduled to disappear.
2. No replacement introduces a client, duration, result, frequency, benchmark, or production
   event without an inspectable artifact.
3. Batch-1 carried prose contains neither customer-support anecdote nor the 60% figure, and
   retains the GSC-mandated search jobs in their final owners.
4. Run `tools/audit_claims.py --paths` on the changed retained pages, then the normal build,
   rule, cluster, stylesheet, structure, and test gates. Existing candidates outside this delta
   remain review work; a lower count is evidence of repair, not permission to ignore them.
