# Cluster 3 consolidation audit

**Date:** 2026-08-17 · **Scope:** all 57 published `ai-engineering` posts

**Evidence:** `tools/url_inventory.py` (1,047 URLs), `tools/gsc_report.py`, `tools/audit_claims.py --count`, inbound and outbound link counts from the built output.

**Recommendation: consolidate 57 posts to 36.** 21 dispositions: 20 merges and 1 retirement.

**Corrected during batch 1.** `agent-memory-for-customer-support` was specified as a merge. Reading
the source showed its only surviving idea is a fabricated case study, so it retires with nothing
carried over. The count of 36 is unchanged; what changes is that one page contributes nothing to
its target. `tools/audit_claims.py` flagged none of the six invented figures, which is a scanner
blind spot for first-person metrics worth closing separately.

---

## What the numbers say before any judgement

| Measure | Value |
|---|---:|
| Published posts | 57 |
| Lifetime impressions, all 57 | 4,446 |
| **Lifetime clicks, all 57** | **6** |
| Posts with zero clicks ever | 53 of 57 |
| Posts with zero impressions ever | 5 |
| Share of all impressions held by one page | 54% (`how-anthropics-contextual-retrieval-changes-rag-architecture`) |
| Posts carrying unevidenced claims | 31 of 57 |

That single page holding 54% of the cluster's impressions is `how-anthropics-contextual-retrieval-changes-rag-architecture`, and its traffic is the 28-variant `anthropic contextual retrieval` fan-out already established as machine rather than human. **Strip it and the cluster is 2,026 impressions and 6 clicks across 56 posts.**

Four posts have ever produced a click: `shared-vs-isolated-memory-multi-agent` (2), `fine-tuning-vs-rag-for-agent-memory` (2), `prompt-caching-what-it-is-and-when-the-math-works` (1), `rag-vs-memory` (1).

---

## Why 36 and not 20

The click data would justify a far deeper cut. It should not be used that way, and this is the one place I am arguing against the evidence in front of me.

**The domain was spam-compromised and fully rebuilt inside twelve months.** Zero clicks on a page is not proof the page cannot earn. It is proof the cluster has not had a fair trial. Merging on demonstrated topic overlap is defensible on its own terms and survives whatever the domain does next. Retiring on click data from a rebuilt domain would be reading a broken instrument.

So every disposition below is **merge, not retire**, and each one is justified by overlap with a named sibling rather than by its traffic. Nothing in this audit is retired. Traffic is used only to choose which side of a merge survives.

---

## Dispositions

### Merge, 21 pages

Each row names the target and what survives from the source. The moat consolidation is the template: a consolidation that drops the only ideas worth keeping is a deletion wearing a redirect.

| Source | Impr | Claims | Target | What survives from the source |
|---|---:|---:|---|---|
| `state-of-open-source-memory-2026` | 35 | 0 | `state-of-ai-agent-memory-2026` | the open-source vendor landscape, which the owner covers only as commercial options |
| `beam-memory-benchmark` | 15 | 1 | `context-windows-vs-memory` | the measured long-context retrieval failure |
| `memory-hierarchy-in-ai-systems` | 15 | 1 | `ai-memory-management-for-llms` | the layered model, after it has absorbed the RAG-is-not-enough argument |
| `the-memory-hierarchy-why-rag-is-not-enough` | 13 | 0 | `ai-memory-management-for-llms` | the argument for why RAG alone fails as memory, which the hierarchy page states but does not argue |
| `asymmetric-retrieval-agent-memory` | 12 | 1 | `rag-vs-memory` | why agent-side retrieval is asymmetric, which is the mechanism behind the comparison |
| `how-memory-works-in-hyperagents` | 11 | 0 | `how-memory-works-in-deerflow` | the third framework as a comparison column |
| `contextual-compression-for-agent-memory` | 10 | 1 | `short-term-memory-for-ai-agents` | the compression decision when the window fills |
| `agentic-cli-benchmarks` | 10 | 0 | `best-llms-for-coding` | the CLI harness comparison as a section |
| `the-agent-design-space` | 8 | 2 | `the-taxonomy-of-ai-agents` | the design-space axes, which are the taxonomy stated as choices |
| `speculative-decoding-explained` | 7 | 1 | `llm-inference-optimization` | the draft-and-verify mechanism |
| `time-to-first-token-ttft` | 7 | 1 | `llm-inference-optimization` | TTFT as the metric the optimisations move |
| `memory-versioning-and-audit-trails` | 5 | 0 | `memory-serialization-between-sessions` | append-only history and the compliance case for it |
| `llm-context-windows-explained` | 5 | 0 | `context-windows-vs-memory` | lost-in-the-middle and why window size is not the fix |
| `memory-attribution-errors` | 4 | 2 | `ai-memory-management-for-llms` | attribution as a named failure class with its symptoms |
| `agent-vs-ai-assistant` | 4 | 0 | `the-taxonomy-of-ai-agents` | the outer boundary: who drives the loop |
| `why-ai-agents-keep-failing-in-production` | 4 | 1 | `production-ai-agent-errors` | the failure survey that frames the error patterns |
| `agent-memory-for-customer-support` | 0 | 1 | `state-of-ai-agent-memory-2026` | **CORRECTED 2026-08-17: nothing survives. RETIRE.** Its worked example is a fabricated case study (18 to 11 minutes, 61% to 74%, CSAT 3.8 to 4.3, "after 90 days of running this architecture"). Carrying it would import invented metrics. See the batch-1 spec. |
| `token-counting-isnt-optional-a-practical-guide-to-llm-cost-control` | 0 | 0 | `llm-token-budgets-cost-control` | tokenisation mechanics and why JSON is expensive |
| `rag-vs-fine-tuning` | 0 | 0 | `fine-tuning-vs-rag-for-agent-memory` | the general decision framework, which the memory page narrows |
| `mcp-server-setup-guide` | 0 | 0 | `model-context-protocol-explained` | the hands-on setup path |
| `coding-agent-setup-that-works` | 0 | 1 | `why-coding-agents-lose-their-memory` | the setup that prevents the loss |

### Keep but repoint, 1 page

- **`embedding-models-compared`** (120 impressions). titled "Vector Embeddings: a Guide to the Geometry of Meaning" but ranks and earns on embedding-model comparison. Retitle and retarget to the comparison query it already serves.

### Keep as is, 35 pages

Each owns a reader job no sibling owns. Sorted by lifetime impressions.

| Page | Impr | In | Out | Claims | Why it survives |
|---|---:|---:|---:|---:|---|
| `how-anthropics-contextual-retrieval-changes-rag-architecture` | 2420 | 7 | 3 | 0 | Only page on the mechanism. Its impressions are fan-out, but the page itself is sound. |
| `kv-cache-eviction-accuracy` | 144 | 6 | 2 | 0 | Original benchmark with published data. Unrepeatable by a competitor. |
| `how-memory-works-in-claude-code` | 138 | 3 | 4 | 1 | Highest-demand vendor teardown of the three. |
| `shared-vs-isolated-memory-multi-agent` | 120 | 1 | 5 | 0 | One of four pages that has ever earned a click. |
| `prompt-caching-what-it-is-and-when-the-math-works` | 111 | 10 | 3 | 1 | Earned a click. Distinct cost mechanism. |
| `fine-tuning-vs-rag-for-agent-memory` | 87 | 1 | 6 | 1 | Earned clicks, and absorbs the general decision page. |
| `local-wasm-vector-benchmarks` | 86 | 1 | 3 | 2 | Original benchmark on named hardware. |
| `multi-agent-vs-single-agent-tradeoffs` | 80 | 7 | 5 | 0 | Owns the one-or-many decision. |
| `hybrid-search-bm25-vector-search` | 79 | 5 | 2 | 1 | Owns BM25 plus dense retrieval and the fusion mechanism. |
| `llm-inference-optimization` | 79 | 1 | 3 | 1 | Becomes the inference owner after absorbing two mechanisms. |
| `rag-vs-memory` | 74 | 2 | 9 | 0 | Earned a click. Owns the boundary, absorbs the asymmetry mechanism. |
| `state-of-ai-agent-memory-2026` | 73 | 15 | 8 | 2 | Most-linked page in the cluster at 15 inbound. The de-facto hub. |
| `voice-ai-latency-gemini-benchmark` | 71 | 1 | 3 | 3 | Original latency benchmark. |
| `episodic-vs-semantic-vs-working-memory-agents` | 65 | 6 | 4 | 2 | Owns the memory-type taxonomy. |
| `ai-memory-management-for-llms` | 48 | 8 | 8 | 1 | Largest page in the cluster and becomes the memory owner. |
| `how-memory-works-in-deerflow` | 46 | 1 | 3 | 0 | Second vendor teardown, absorbs the third. |
| `semantic-caching-rag-optimization` | 46 | 1 | 2 | 0 | Distinct optimisation nobody else covers here. |
| `short-term-memory-for-ai-agents` | 46 | 10 | 8 | 1 | Owns working memory, absorbs compression. |
| `agentic-workflow-playbook` | 45 | 1 | 5 | 1 | Owns the repeatable workflow. |
| `rag-evaluation-metrics-what-actually-matters` | 40 | 6 | 3 | 1 | Owns RAG evaluation. |
| `reranking-in-rag-why-your-top-k-results-are-probably-wrong` | 39 | 7 | 3 | 1 | Owns reranking. |
| `memory-for-voice-ai-agents` | 34 | 1 | 8 | 1 | Real-time constraint no other memory page carries. |
| `structured-outputs-llms-json-mode-function-calling` | 32 | 10 | 2 | 0 | 10 inbound. Owns schema-constrained output. |
| `why-coding-agents-lose-their-memory` | 24 | 1 | 7 | 1 | Owns the coding-agent case, absorbs setup. |
| `lambda-calculus-ai-reasoning-benchmark` | 22 | 1 | 4 | 1 | Original reasoning benchmark. |
| `production-ai-agent-errors` | 20 | 17 | 3 | 0 | 17 inbound, the most-linked page in the cluster. Absorbs the failure survey. |
| `the-taxonomy-of-ai-agents` | 19 | 5 | 11 | 2 | Becomes the architecture owner after absorbing two overlapping pages. |
| `mixture-of-experts-explained` | 19 | 1 | 1 | 0 | Distinct architecture topic. |
| `memory-serialization-between-sessions` | 18 | 6 | 3 | 0 | Owns persistence, absorbs versioning. |
| `agent-loop-anatomy` | 12 | 9 | 7 | 0 | Owns the loop. 9 inbound. |
| `agent-harnesses` | 10 | 14 | 3 | 0 | 14 inbound. Owns the harness layer. |
| `llm-token-budgets-cost-control` | 5 | 4 | 3 | 0 | Owns cost control, absorbs tokenisation mechanics. |
| `model-context-protocol-explained` | 4 | 5 | 3 | 0 | Owns MCP, absorbs the setup guide. |
| `best-llms-for-coding` | 3 | 2 | 4 | 2 | Owns model choice for coding, absorbs the CLI benchmark. |
| `context-windows-vs-memory` | 2 | 13 | 5 | 1 | 13 inbound, 3,427 words. Absorbs two pages on long-context failure. |

---

## Execution constraints, all three learned expensively

**1. Nothing is retired, so no URL loses its destination.** 16 of the 21 merged sources still draw impressions. Every one redirects to a **genuinely equivalent page**, never to the `/articles/` listing, because seven hub redirects pointing at the bare listing were soft 404s.

One redirect chain was found and resolved before it shipped: `the-memory-hierarchy-why-rag-is-not-enough` pointed at `memory-hierarchy-in-ai-systems`, which is itself merging into `ai-memory-management-for-llms`. It now points directly at the final destination. **All 21 targets are terminal.**

**2. The retrofit is part of the merge, not a follow-up.** `tools/audit_clusters.py --strict` is a CI gate and a merge orphans whatever linked to the merged page. The merged sources carry 69 inbound links between them, so each merge commit repoints those links in the same change.

**3. `build.py` runs before the audit**, because the audit reads `output/`.

---

## Sequencing

Twenty-one merges is not one commit. Group them by target so each commit leaves the tree green:

| Batch | Merges | Target owner |
|---|---:|---|
| 1. Memory core | 6 | `ai-memory-management-for-llms`, `state-of-ai-agent-memory-2026` |
| 2. Memory satellites | 4 | `short-term-memory-for-ai-agents`, `rag-vs-memory`, `memory-serialization-between-sessions`, `how-memory-works-in-deerflow` |
| 3. Architecture | 3 | `the-taxonomy-of-ai-agents`, `production-ai-agent-errors` |
| 4. Inference and cost | 5 | `llm-inference-optimization`, `context-windows-vs-memory`, `llm-token-budgets-cost-control` |
| 5. Tooling | 3 | `model-context-protocol-explained`, `best-llms-for-coding`, `why-coding-agents-lose-their-memory` |

Batch 1 first: it carries the most inbound links and the most impressions, so it is where a mistake is most expensive and where the gates should be exercised earliest.

**The prose is Codex's.** This audit decides disposition, target, and what survives. It writes none of the merged text.

---

## What this does not fix

Thirty-six posts in a cluster with 65% AI Overview saturation and 40% KD<=20 is still a large cluster in a hostile field. Consolidation makes it defensible, not competitive.

The 12 planned cluster-3 rows should still collapse to about 6, and the freed slots should stay empty. **Adding to a cluster this saturated is the move this audit exists to prevent.**

---

## Reconciled against the operational long-tail, 2026-08-17

The tool-first premise died the same day, and the twelve expansion rows repointed at cluster 4 on
that reasoning came back for re-decision. The evidence offered for redirecting them was cluster 3's
operational long-tail: the only two genuinely human queries this domain holds, `how do you handle
errors when ai agents make mistakes in production` at position 10.6, and `how do companies debug ai
agents that fail in production` at 10.2.

That looks like it contradicts this audit, which says cluster 3 is over-populated. It does not, and
the reconciliation is that **the two findings are about different shapes.** What is over-populated
is definitional and taxonomic: five chunking variants, two chatbot architectures, three overlapping
memory hierarchies. What is absent is operational: the question a working engineer types when
something is broken.

**Fewer, better, operational. But the honest row count that justifies is zero new rows, and here is
why.**

**Both queries already map to pages the plan holds.** `how do companies debug ai agents that fail in
production` is order 76, The Agent Observability Stack, whose stated reader outcome is "see what an
agent did, in enough detail to debug a bad run". `how do you handle errors when ai agents make
mistakes in production` is order 78, Circuit Breakers for AI Agents, "stop a failing agent loop
before it burns budget or corrupts state". Both were already in the keep set, and both are
demand-backed by the corpus rather than by a keyword tool.

**The queries also already rank.** Position 10.2 and 10.6 is page one to two on an existing page,
`production-ai-agent-errors`, which holds 17 inbound links and is the batch-3 merge target absorbing
`why-ai-agents-keep-failing-in-production`. Writing new pages for queries an existing page already
ranks for is cannibalization, which is the rule this campaign enforces everywhere else.

So the operational demand is served by **expanding a page that already ranks**, and that expansion
is the batch-3 merge rather than a new row. The merge brief carries the requirement: the merged page
answers those two questions directly, with question-shaped headings, in the operational register
rather than the definitional one.

### The caveats, carried into the rows rather than left in a covering note

Both go into the batch-3 merge brief and into orders 76 and 78:

- **Cluster 3's headline impressions are largely machine fan-out with zero clicks.** One page holds
  54% of the cluster's impressions and it is the `anthropic contextual retrieval` fan-out. Its
  apparent strength is inflated the same way everything else on this domain has been. Nothing in
  these rows may cite cluster-3 impressions as evidence of demand.
- **The two queries are conversational and operational, not head terms.** That is a different brief
  shape: a question typed when something is broken, answered in the first two sentences, not a
  definitional page with a taxonomy.

### What actually changed

| Action | Rows |
|---|---:|
| New cluster-3 rows added | **0** |
| Cluster-3 rows skipped, completing this audit's collapse | **6** (68, 69, 70, 71, 74, 75) |
| Cluster-3 planned rows remaining | **6** (63, 72, 73, 76, 77, 78) |
| Cluster-4 rows repointed | 1 retitle (50), 1 re-justification (36) |

Cluster 3 planned goes 12 to 6, exactly as this audit recommended. **The freed slots stay empty.**

### Two corrections to the premise I was given

**It was five rows, not twelve.** Of the twelve cancelled expansion slots, six were filled with
cluster-4 targets and six were skipped on the day for want of a verified seventh target. One of the
six filled was later skipped as a duplicate of a live article. So five rows carried the tools-lead
reasoning, not twelve, and the other seven are already empty.

**Four of those five survive the premise dying.** Orders 35, 38, 39 and 40 are cluster-4 *articles*
chosen on verified keyword volume and parent-topic checks, not on tool intent. Only order 36 was
justified by the dead premise, and it survives on a smaller and different justification: it gives a
live tool an inbound link, which is a structural fix that does not depend on the premise. Its brief
now says so and forbids claiming tool intent escapes AI Overviews.

**The free win was already in the queue.** Google's People-also-ask "Does LLMs.txt actually work?"
is order 50, previously titled "Does llms.txt Improve AI Visibility? A Controlled Documentation
Test". The PAA validates an existing row rather than adding one. Retitled to the question Google
actually surfaces.

**The six skipped expansion slots cannot be reused.** `Skipped` is terminal in the queue state
machine, with no transition out of it. They stay empty, which is the intended outcome.
