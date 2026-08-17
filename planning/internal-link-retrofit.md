# Internal link retrofit plan

**Date:** 2026-08-17 · **Source:** `tools/audit_clusters.py` against the build at `9e39eea8`
**Charter:** 2e (linking), 2c-bis (cluster isolation)

88 published posts. **20 have no inbound link at all, 23% of the site.** Nine have fewer than
two outbound, five with none. Every URL below was taken from the freshly built
`output/sitemap.xml` and `output/llms.txt` after `python build.py`, per Charter 2e rule 1. None
came from memory.

Codex writes the sentences. This plan names the source, the reason, and the anchor concept only.

## How a source was chosen

Same cluster as the orphan, always. Within that, the page whose reader is at the exact moment
where the orphan is the next thing they need. A source is not "a related page", it is the page a
reader is already on when the orphan becomes useful.

**Four sources were picked to solve both problems at once.** They are themselves zero-outbound
pages, so one edit gives the orphan its inbound link and the source its missing outbound. Marked
**[dual]**.

## The 20 orphans

### ai-engineering (11)

| Orphan | Source page | Why a reader moves between them | Anchor concept |
|---|---|---|---|
| `lambda-calculus-ai-reasoning-benchmark` | `best-llms-for-coding` | A reader choosing a coding model is being sold leaderboard numbers. This is a reasoning test that separates models a leaderboard ranks identically. | a composition-level reasoning test, not a leaderboard |
| `agent-vs-ai-assistant` | `the-taxonomy-of-ai-agents` | The taxonomy classifies agents. Before any classification is useful the reader needs the outer boundary: which side of agent-versus-assistant they are on. | where the agent boundary actually falls |
| `contextual-compression-for-agent-memory` | `context-windows-vs-memory` | That page ends on "a window is not memory". The immediate next question is what to keep when the window fills. | deciding what survives when context runs out |
| `memory-versioning-and-audit-trails` | `memory-serialization-between-sessions` | Serialization gets state across a restart. Versioning is the next question: keeping the history rather than overwriting it. | keeping an auditable history instead of overwriting |
| `agent-memory-for-customer-support` | `state-of-ai-agent-memory-2026` | The state-of overview surveys the stack. A reader who has read the survey wants one workload where it plays out. | how the stack behaves in a support workload |
| `coding-agent-setup-that-works` **[dual]** | `agentic-cli-benchmarks` | The benchmark compares two coding CLIs. Setup is what decides the outcome before either tool writes a line, which the benchmark cannot show. | the setup that decides the result before the run |
| `fine-tuning-vs-rag-for-agent-memory` | `rag-vs-fine-tuning` | The general decision page is the obvious owner. The memory case changes the answer, so it must delegate rather than absorb. | how the same choice changes for agent memory |
| `llm-inference-optimization` | `time-to-first-token-ttft` | TTFT names the metric a user feels. This is the set of techniques that move it. | the optimizations that move first-token latency |
| `mcp-server-setup-guide` | `model-context-protocol-explained` | Classic explainer-to-implementation delegation. The explainer must hand off rather than grow a setup section. | connecting an agent to your own tools |
| `memory-attribution-errors` | `production-ai-agent-errors` | The production-errors page catalogues failure classes. Attribution is one class it names but does not work through. | memory attributed to the wrong session or user |
| `shared-vs-isolated-memory-multi-agent` | `multi-agent-vs-single-agent-tradeoffs` | Once a reader has chosen multiple agents, the next unavoidable decision is whether they share memory. | whether agents share one memory or hold their own |

### technical-documentation (5)

| Orphan | Source page | Why a reader moves between them | Anchor concept |
|---|---|---|---|
| `api-documentation-template-the-pages-every-api-needs` | `api-documentation-best-practices-reference-guides-and-working-requests` | The anchor assigns each page a job. The template is the outline that job list produces, so the anchor should delegate the inventory. | the outline an API docs project starts from |
| `api-documentation-tools-hands-on-comparison-small-teams` | `api-documentation-examples-what-the-best-developer-portals-get-right` | After studying what good portals do, the next question is which tool produces that. Deliberately not sourced from the best-practices anchor, which already carries the template link. | choosing the tool that produces that portal |
| `documentation-accessibility-checklist` **[dual]** | `how-to-organize-a-documentation-site` | Reorganising a drifted docs site is exactly when structural accessibility failures surface and get fixed cheaply. | the accessibility failures that block a release |
| `technical-writing-examples` **[dual]** | `how-to-write-a-technical-tutorial-that-actually-teaches` | A reader writing their first tutorial wants to see finished work in other formats before committing to one. | finished examples from working teams |
| `what-is-technical-documentation-and-what-should-it-include` | `technical-documentation-template` **[dual]** | Someone who downloaded the template needs to know the minimum set a documentation package must contain before filling placeholders. | what a documentation set must include |

### developer-experience (4)

Only eight posts exist in this cluster and four of them are orphans, so every remaining page
becomes a source. That is a structural weakness, not a linking accident: see the note below.

| Orphan | Source page | Why a reader moves between them | Anchor concept |
|---|---|---|---|
| `developer-trust-hierarchy` | `why-devtools-startups-lose-deals-over-bad-docs` | The deals page describes the symptom. The trust hierarchy is the mechanism underneath it: how engineers rank what they will believe. | how engineers rank what they trust |
| `engineering-velocity-documentation` | `technical-content-as-a-moat-the-long-game-for-developer-tools` | The moat argument is external and compounding. Velocity is the internal half of the same claim. | what documentation quality does to throughput |
| `from-engineer-to-technical-writer-what-i-kept-and-what-i-left-behind` | `technical-writing-for-engineers` | Its reader is an engineer being asked to write. The transition piece answers the question that page raises but does not address. | which engineering habits survive the move |
| `technical-writing-for-ai-products-the-new-rules` | `how-stripes-technical-blog-became-a-competitive-moat` | **Weakest pairing in this plan.** The Stripe piece argues docs, blog, and tooling reinforce each other as one product surface. AI products change what that surface contains. If Codex cannot make the connection the subject of a sentence, leave it and raise it. | what changes when the product is an AI system |

## Nine posts with fewer than two outbound links

Four are already handled above as **[dual]** sources. The rest need outbound links added.

| Post | Out | Add links to | Why |
|---|---:|---|---|
| `agentic-cli-benchmarks` | 0 | `coding-agent-setup-that-works` **[dual]**, `best-llms-for-coding` | Setup explains the result the benchmark measures; model choice is the other variable. |
| `how-to-organize-a-documentation-site` | 0 | `documentation-accessibility-checklist` **[dual]**, `what-a-documentation-homepage-must-help-users-do` | Both are decisions taken during a reorganisation. |
| `how-to-write-a-technical-tutorial-that-actually-teaches` | 0 | `technical-writing-examples` **[dual]**, `types-of-technical-documentation` | Format choice and finished examples are what a first-time tutorial writer needs. |
| `developer-onboarding-docs-what-works-what-doesnt` | 0 | `what-is-technical-documentation-and-what-should-it-include`, `documentation-review-checklist-before-you-publish` | Onboarding docs are a subset of the minimum package, and they decay without a review gate. |
| `how-to-write-a-changelog-developers-actually-read` | 0 | `writing-release-notes-that-developers-trust`, `how-to-document-multiple-product-versions` | The changelog/release-notes boundary is already argued on both pages; versions are the third leg. |
| `memory-versioning-and-audit-trails` | 1 | `memory-serialization-between-sessions` | Reciprocates its own inbound retrofit above. |
| `mixture-of-experts-explained` | 1 | `llm-inference-optimization` | MoE is a serving-cost architecture; the optimization page is where that cost gets managed. |
| `structured-outputs-llms-json-mode-function-calling` | 1 | `agent-loop-anatomy` | Function calling is the act step of the loop. |
| `writing-release-notes-that-developers-trust` | 1 | `how-to-document-multiple-product-versions` | Release notes describe a version change; version routing is what the reader hits next. |

`developer-onboarding-docs-what-works-what-doesnt` sourcing `what-is-technical-documentation-and-what-should-it-include` makes that source a fifth
dual fix. Total: **20 orphans closed, 9 outbound deficits closed, 25 file edits.**

## Cross-cluster links: 6 of 22 fail the subject test

Charter 2c-bis permits a cross-cluster link only when the connection is the actual subject of the
sentence. Convenience, "a similar problem", and keyword proximity are never sufficient.

**These six should be removed.** Each name-drops a page from another cluster to decorate a claim
the sentence already made.

| From | To | The giveaway |
|---|---|---|
| `how-stripes-technical-blog-became-a-competitive-moat` | `agent-harnesses` | "I covered **a similar dynamic** in agent harnesses." The sentence is about trust in systems. Agent harnesses are not its subject. |
| `state-of-ai-agent-memory-2026` | `developer-onboarding-docs-what-works-what-doesnt` | "I wrote about **a similar fragmentation problem**… the pattern is the same." An analogy reaching from AI engineering into documentation. |
| `technical-content-as-a-moat-the-long-game-for-developer-tools` | `how-to-write-a-changelog-developers-actually-read` | "I made **a similar argument** from the reader side." Same construction, same failure. |
| `technical-content-as-a-moat-the-long-game-for-developer-tools` | `token-counting-isnt-optional-a-practical-guide-to-llm-cost-control` | "I prefer writing posts **such as**…" Self-citation as illustration of a preference. |
| `technical-content-as-a-moat-the-long-game-for-developer-tools` | `prompt-caching-what-it-is-and-when-the-math-works` | Same sentence as above, second link in the same list. |
| `technical-writing-for-ai-products-the-new-rules` | `agent-harnesses` | Buried inside a comma-list of examples, bare-keyword anchor. Fails the anchor rule as well as the cluster rule. |

`technical-content-as-a-moat-the-long-game-for-developer-tools` accounts for three of the six. It is the worst offender and should
be reviewed as a page, not just as three links.

**The other sixteen pass.** They share one shape: the sentence is *about* the linked work rather
than gesturing at it. "The frustration that produced my post on agent harnesses", "I covered the
schema side of that problem in", "stale guidance is one of the clearest signs of". The link is
the grammatical subject or object, not an aside.

Two pass structurally but carry a separate defect. `engineering-velocity-documentation` links to
`the-case-for-shorter-technical-documentation` and `developer-onboarding-docs-what-works-what-doesnt` inside sentences
built on "40-60%" and "60 seconds", figures the 2026-08-13 audit flagged as unsourced. The links
are fine. The statistics need a source or removal, which is a `voice-repair` item rather than a
linking one.

## What this does not fix

The developer-experience cluster has eight posts and four were orphans. A cluster that small
cannot generate its own inbound links, and cluster isolation means it cannot borrow them. The
retrofit closes the immediate gap, but the cluster needs more pages before its linking is
self-sustaining. The reweighted queue gives it only three of 71 rows, correctly, because it is
3.9% of winnable volume. That tension is real and should be decided rather than drifted into:
either DevEx earns more rows than its volume justifies so the cluster can support itself, or it
stays small and permanently depends on retrofits like this one.
