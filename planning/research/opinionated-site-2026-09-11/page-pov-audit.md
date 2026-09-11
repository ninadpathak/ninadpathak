# Complete public prose inventory and POV audit

Audit date: 2026-09-11. This register covers every currently published article and every generated prose template or instance found in the generator inputs. A disposition records review state; it is not semantic approval.

## Counts

- Published articles: 67 (41 EVIDENCE_REQUIRED, 24 PROVISIONAL_REVIEW, 0 REWRITE_BATCH, 2 PHASE_A_EDITED)
- Automated provenance sweep after zero-impression removal: 103 candidates across 41 of 67 articles
- Archived articles: 20 with zero recorded Google Search Console page impressions in 2026-06-11 through 2026-09-08; source and previous review dispositions preserved in `../zero-impression-cleanup-2026-09-11/`. This traffic disposition is not a judgment of content quality or proof of no rankings.
- Core/template surfaces: 15 register rows, including shared templates whose prose renders across pagination or tool instances
- Work detail pages: 5
- Glossary term pages: 23
- Category archives: 5 instances covered by one shared-template row and five distinct category arguments in `config.toml`
- Standalone tool pages: 5 instances covered by one bounded product-copy row
- Pillar YAML sources: 12; these feed links or metadata but do not render as independent HTML pages in the current build
- Legal pages: 2

## Disposition meanings

- `PHASE_A_EDITED`: changed in this phase; fixture checks may pass, but independent editorial review is still pending.
- `EVIDENCE_REQUIRED`: the automated sweep found first-person history, private incident, role, quote, price, measurement, or another provenance candidate. A human must classify each candidate.
- `REWRITE_BATCH`: no automated provenance blocker was found, but the page has a recorded structural or voice problem.
- `PROVISIONAL_REVIEW`: inventory is complete and no unresolved automated provenance candidate remains. This is not semantic approval.
- `REFERENCE_SCOPE` / `PRODUCT_SCOPE`: the surface has a reference or product job. These labels describe scope and approve nothing.
- `AUDIT_SOURCE`: source data can surface publicly but does not own an independent generated URL.

## Core and generated surfaces

| Surface | Path/source | Disposition | Audit |
| --- | --- | --- | --- |
| Core/template | `/` | PHASE_A_EDITED | Homepage preserves Ninad's heat with grammar-edited singular/plural agreement; independent editorial and current-render review remain pending. |
| Core/template | `/about/` | PHASE_A_EDITED | About carries the raw conviction before concrete adoption limits; independent editorial and current-render review remain pending. |
| Core/template | `/work/` | PHASE_A_EDITED | Work states that its outcome cards are published claims pending provenance review and makes no causal endorsement. |
| Core/template | `/portfolio/` | PHASE_A_EDITED | Portfolio asks readers to judge linked work; independent editorial and UI review remain pending. |
| Core/template | `/projects/` | PHASE_A_EDITED | Projects explains why Ninad builds inspectable checks; independent editorial and UI review remain pending. |
| Core/template | `/contact/` | PHASE_A_EDITED | Contact asks for product behavior, evidence, and the failed page; independent editorial and UI review remain pending. |
| Core/template | `/articles/` | PHASE_A_EDITED | Article listing frames the corpus as arguments and tests; pagination inherits this prose and awaits UI review. |
| Core/template | `/tools/` | PROVISIONAL_REVIEW | Tools argues for inspectable methods over unexplained scores; human evidence and UI review remain pending. |
| Core/template | `/glossary/` | PHASE_A_EDITED | Glossary index rejects circular definitions; independent editorial and UI review remain pending. |
| Core/template | `/404/` | REWRITE_BATCH | Functional error page; add voice only after core public claims pass review. |
| Core/template | `/terms/` | REFERENCE_SCOPE | Legal prose has a reference job; the label does not approve its claims. |
| Core/template | `/privacy/` | REFERENCE_SCOPE | Privacy prose has a reference job; the label does not approve its claims. |
| Core/template | `global footer` | PHASE_A_EDITED | Footer states tested examples, opinions, and human authorship; independent UI review remains pending. |
| Core/template | `five category archives` | PHASE_A_EDITED | Each archive carries a distinct argument; independent editorial and UI review remain pending. |
| Core/template | `five standalone tools` | PRODUCT_SCOPE | Each tool owns a testable job and method; evidence and UI-copy review remain pending. |

## Work pages

| Surface | Path/source | Disposition | Audit |
| --- | --- | --- | --- |
| Work detail | `/work/centus/` | EVIDENCE_REQUIRED | 50+ Developer Guides That Engineers Actually Use: metrics, roles, causality, and any retained quotations require provenance review before clearance. |
| Work detail | `/work/delightchat/` | EVIDENCE_REQUIRED | Zero to 50,000 Monthly Organic Visits: metrics, roles, causality, and any retained quotations require provenance review before clearance. |
| Work detail | `/work/kiwisizing/` | EVIDENCE_REQUIRED | 7,000 to 450,000 Monthly Visits, A 64x Traffic Multiplier: metrics, roles, causality, and any retained quotations require provenance review before clearance. |
| Work detail | `/work/linuxfordevices/` | EVIDENCE_REQUIRED | From 487 to 203,000 Monthly Visits, And $34K More MRR: metrics, roles, causality, and any retained quotations require provenance review before clearance. |
| Work detail | `/work/mem0/` | EVIDENCE_REQUIRED | Scaling Mem0 from 24k to 45k Monthly Visits in 60 Days: metrics, roles, causality, and any retained quotations require provenance review before clearance. |

## Glossary term pages

| Surface | Path/source | Disposition | Audit |
| --- | --- | --- | --- |
| Glossary term | `/glossary/context-engineering/` | REFERENCE_SCOPE | Context Engineering: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/agentic-engineering/` | REFERENCE_SCOPE | Agentic Engineering: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/flow-engineering/` | REFERENCE_SCOPE | Flow Engineering: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/test-time-compute/` | REFERENCE_SCOPE | Test-Time Compute (TTC): reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/model-context-protocol/` | REFERENCE_SCOPE | Model Context Protocol (MCP): reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/semantic-caching/` | REFERENCE_SCOPE | Semantic Caching: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/matryoshka-representation-learning/` | REFERENCE_SCOPE | Matryoshka Representation Learning (MRL): reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/cross-encoder-reranking/` | REFERENCE_SCOPE | Cross-Encoder Reranking: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/late-chunking/` | REFERENCE_SCOPE | Late Chunking: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/tool-calling/` | REFERENCE_SCOPE | Tool Calling: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/pagedattention/` | REFERENCE_SCOPE | PagedAttention: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/kv-cache-eviction/` | REFERENCE_SCOPE | KV Cache Eviction: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/semantic-chunking/` | REFERENCE_SCOPE | Semantic Chunking: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/hypothetical-document-embeddings-hyde/` | REFERENCE_SCOPE | Hypothetical Document Embeddings (HyDE): reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/self-querying-retrieval/` | REFERENCE_SCOPE | Self-Querying Retrieval: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/bi-encoder/` | REFERENCE_SCOPE | Bi-Encoder Architecture: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/product-quantization/` | REFERENCE_SCOPE | Product Quantization (PQ): reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/hierarchical-navigable-small-world-hnsw/` | REFERENCE_SCOPE | Hierarchical Navigable Small World (HNSW): reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/react-prompting/` | REFERENCE_SCOPE | ReAct Prompting: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/plan-and-solve-framework/` | REFERENCE_SCOPE | Plan-and-Solve Framework: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/speculative-decoding/` | REFERENCE_SCOPE | Speculative Decoding: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/agentic-router/` | REFERENCE_SCOPE | Agentic Router: reference job is definition and boundary; the label does not approve its claims. |
| Glossary term | `/glossary/json-mode-vs-structured-outputs/` | REFERENCE_SCOPE | JSON Mode vs. Structured Outputs: reference job is definition and boundary; the label does not approve its claims. |

## Published articles

The thesis text below is a candidate extracted from each page's actual opening, not a mechanical approval. The evidence sweep is intentionally over-inclusive; a human reviewer decides whether each candidate is earned, needs rewriting, or should be cut.

| Surface | Path/source | Disposition | Audit |
| --- | --- | --- | --- |
| Article | `2026-04-21-the-taxonomy-of-ai-agents.md` | EVIDENCE_REQUIRED | Thesis candidate: “Every few months someone publishes a new taxonomy of AI agents.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `2026-04-22-why-ai-agents-keep-failing-in-production.md` | EVIDENCE_REQUIRED | Thesis candidate: “Across two years of debugging production AI agents, I keep landing on the same handful of failures.” Automated sweep found 4 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `2026-04-23-agent-loop-anatomy.md` | EVIDENCE_REQUIRED | Thesis candidate: “When an agent starts misbehaving, the loop is the first useful boundary to inspect.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `2026-04-25-lambda-calculus-ai-reasoning-benchmark.md` | EVIDENCE_REQUIRED | Thesis candidate: “Lambda calculus exposes whether an AI system can preserve bindings through composition.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `2026-04-26-agent-vs-ai-assistant.md` | EVIDENCE_REQUIRED | Thesis candidate: “For the last year I have watched teams make the same architectural mistake twice.” Automated sweep found 3 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `2026-04-27-multi-agent-vs-single-agent-tradeoffs.md` | EVIDENCE_REQUIRED | Thesis candidate: “The first time I split a single agent into two, I thought I was solving a parallelism problem.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `2026-05-05-contextual-compression-for-agent-memory.md` | EVIDENCE_REQUIRED | Thesis candidate: “Around week three, the problem shows up.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `2026-05-05-memory-versioning-and-audit-trails.md` | EVIDENCE_REQUIRED | Thesis candidate: “An AI agent that hallucinates in a consumer app is annoying.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `agent-harnesses.md` | PROVISIONAL_REVIEW | Thesis candidate: “Agents look impressive in demos because the happy path is easy to show.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `agentic-cli-benchmarks.md` | PROVISIONAL_REVIEW | Thesis candidate: “Claude Code and Gemini CLI can both inspect a repository, edit files, and run verification commands.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `agentic-workflow-playbook.md` | EVIDENCE_REQUIRED | Thesis candidate: “I do not turn an agent loose on a task and hope.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `ai-memory-management-for-llms.md` | EVIDENCE_REQUIRED | Thesis candidate: “Having a context window does not mean an LLM has memory.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `best-llms-for-coding.md` | EVIDENCE_REQUIRED | Thesis candidate: “Evaluating models for software engineering stopped being about snippet generation a while ago.” Automated sweep found 3 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `code-documentation.md` | PROVISIONAL_REVIEW | Thesis candidate: “A codebase starts to become hard to change when the reason for a line lives in a handbook, while the handbook repeats signatures the source already knows.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `context-windows-vs-memory.md` | PROVISIONAL_REVIEW | Thesis candidate: “A model can accept a long prompt and still fail to use the fact that answers the question.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `developer-onboarding-docs-what-works-what-doesnt.md` | PROVISIONAL_REVIEW | Independent review accepted the Phase B rewrite. Thesis: onboarding documentation should end in a safe merged change rather than a finished reading list. Illustrative hosts, services, commands, and recovery blocks are labeled before use; the package-manager check now follows the selected `packageManager` value and cites Corepack's maintained source; no automated provenance candidate remains. |
| Article | `documentation-accessibility-checklist.md` | PROVISIONAL_REVIEW | Thesis candidate: “Accessibility testing matters for documentation because a page can look finished and still leave a reader unable to complete its task.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `documentation-review-checklist-before-you-publish.md` | PROVISIONAL_REVIEW | Independent review accepted the Phase B rewrite. Thesis: review should begin with product truth, then test the reader route, rendered artifact, and release state before polishing prose. Fictional claims, paths, roles, hosts, commands, and responses are labeled before use; repeated verdict scaffolding and duplicated tail checks were cut; the automated provenance scan is clear. |
| Article | `embedding-models-compared.md` | PROVISIONAL_REVIEW | Thesis candidate: “Every interaction with a modern language model begins with a conversion.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `engineering-velocity-documentation.md` | EVIDENCE_REQUIRED | Thesis candidate: “Of every investment I have watched move engineering velocity, technical documentation is the one most teams underrate.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `episodic-vs-semantic-vs-working-memory-agents.md` | PROVISIONAL_REVIEW | Thesis candidate: “An agent can forget what it just did even when its logs look normal, retrieval is fast, and the context window has room.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `fine-tuning-vs-rag-for-agent-memory.md` | PROVISIONAL_REVIEW | Thesis candidate: “Which approach wins depends on what problem you are actually solving.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `from-engineer-to-technical-writer-what-i-kept-and-what-i-left-behind.md` | EVIDENCE_REQUIRED | Thesis candidate: “Moving from engineering to technical writing did not feel like abandoning a technical career.” Automated sweep found 3 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `how-anthropics-contextual-retrieval-changes-rag-architecture.md` | PROVISIONAL_REVIEW | Thesis candidate: “Anthropic took a chunk like '"The company's revenue grew by 3% over the previous quarter."', asked Claude to explain that chunk using the full document, then prepended the explanation before indexing it.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `how-memory-works-in-claude-code.md` | EVIDENCE_REQUIRED | Thesis candidate: “Claude Code carries instructions across sessions through 'CLAUDE.md' files and auto memory.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `how-memory-works-in-deerflow.md` | EVIDENCE_REQUIRED | Thesis candidate: “Structured context passing is what I call the way DeerFlow organizes memory.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `how-memory-works-in-hyperagents.md` | EVIDENCE_REQUIRED | Thesis candidate: “HyperAgents Memory Architecture” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `how-stripes-technical-blog-became-a-competitive-moat.md` | EVIDENCE_REQUIRED | Thesis candidate: “Stripe built a strong technical blog by creating an acquisition surface, a trust layer, and a product education system.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `how-to-organize-a-documentation-site.md` | PROVISIONAL_REVIEW | Independent review accepted the Phase B rewrite. Thesis: organize documentation around reader routes rather than the org chart. Illustrative URLs, searches, prompts, roles, and migration trees are labeled before use; the global-navigation H3 now promises content routes, matching its examples; repeated verdict scaffolding and duplicated tail copy were cut; no automated provenance candidate remains. |
| Article | `how-to-write-a-changelog-developers-actually-read.md` | PROVISIONAL_REVIEW | Thesis candidate: “You are about to approve a dependency bump and someone asks, “Is this actually safe to ship?” The changelog says “improved pagination,” “updated authentication,” and “internal maintenance.”” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `how-to-write-a-technical-tutorial-that-actually-teaches.md` | PHASE_A_EDITED | Thesis: “The earlier worked example on this page imported 'verifyWebhook' from '@example/webhooks' and celebrated a successful event without supplying the dependency or a command to start the server.” Fixture and claim checks passed; the edit still awaits independent editorial review. |
| Article | `how-to-write-task-based-documentation-headings.md` | PROVISIONAL_REVIEW | Thesis candidate: “A heading should tell a scanning reader what the section contains.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `hybrid-search-bm25-vector-search.md` | EVIDENCE_REQUIRED | Thesis candidate: “Dense vector search became the default for RAG systems almost overnight.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `internal-vs-external-documentation.md` | PROVISIONAL_REVIEW | Thesis candidate: “Internal documentation helps your team operate the system.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `kv-cache-eviction-accuracy.md` | PROVISIONAL_REVIEW | Thesis candidate: “VRAM capacity dictates the boundary of what a Large Language Model (LLM) can actually do for you.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `llm-context-windows-explained.md` | EVIDENCE_REQUIRED | Thesis candidate: “Language models read and reason over a fixed span of text called the context window, and that span has grown from a few thousand tokens to several million in barely a year.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `llm-inference-optimization.md` | EVIDENCE_REQUIRED | Thesis candidate: “Inference is where LLM projects die.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `llm-token-budgets-cost-control.md` | EVIDENCE_REQUIRED | Thesis candidate: “Token costs are the new EC2 bills.” Automated sweep found 21 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `local-wasm-vector-benchmarks.md` | EVIDENCE_REQUIRED | Thesis candidate: “PGlite and SQLite-vec take different approaches to vector search in the browser.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `memory-for-voice-ai-agents.md` | EVIDENCE_REQUIRED | Thesis candidate: “Voice agents and text chatbots fail differently.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `memory-serialization-between-sessions.md` | PROVISIONAL_REVIEW | Thesis candidate: “An agent can handle every conversation in one process and still lose its state at the next restart.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `mixture-of-experts-explained.md` | EVIDENCE_REQUIRED | Thesis candidate: “DeepSeek's API launched at roughly a tenth the price of comparable Anthropic and OpenAI endpoints, with competitive benchmark results.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `model-context-protocol-explained.md` | EVIDENCE_REQUIRED | Thesis candidate: “Wiring an AI model up to external data has always been a messy engineering chore.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `production-ai-agent-errors.md` | EVIDENCE_REQUIRED | Thesis candidate: “Two years of running AI agents in production taught me that error handling separates a system that survives reality from one that falls over the moment something goes wrong.” Automated sweep found 4 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `rag-evaluation-metrics-what-actually-matters.md` | EVIDENCE_REQUIRED | Thesis candidate: “Building a RAG system is the part every tutorial covers.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `rag-vs-memory.md` | PROVISIONAL_REVIEW | Thesis candidate: “RAG and memory both put useful context in front of a model, but they govern different things.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `reranking-in-rag-why-your-top-k-results-are-probably-wrong.md` | EVIDENCE_REQUIRED | Thesis candidate: “Vector databases are powerful tools for building retrieval-augmented generation systems.” Automated sweep found 4 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `semantic-caching-rag-optimization.md` | EVIDENCE_REQUIRED | Thesis candidate: “Almost every conversation I see about RAG optimization centers on retrieval quality: better embeddings, rerankers, hybrid search, contextual chunking.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `seo-for-technical-documentation.md` | EVIDENCE_REQUIRED | Thesis candidate: “I built the audit for this guide around Cloudflare's live Workers CLI guide.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `shared-vs-isolated-memory-multi-agent.md` | PROVISIONAL_REVIEW | Thesis candidate: “Consider a three-stage document pipeline: one agent extracts fields, one validates them, and one writes the summary.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `short-term-memory-for-ai-agents.md` | EVIDENCE_REQUIRED | Thesis candidate: “Context windows are not memory, and that is the first thing engineers get wrong when building AI agents.” Automated sweep found 3 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `speculative-decoding-explained.md` | EVIDENCE_REQUIRED | Thesis candidate: “Inference speed is the biggest hurdle I keep running into with interactive LLM applications.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `state-of-ai-agent-memory-2026.md` | EVIDENCE_REQUIRED | Thesis candidate: “An agent can act on stale or contradictory state without realizing that its memory is wrong.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `structured-outputs-llms-json-mode-function-calling.md` | PROVISIONAL_REVIEW | Thesis candidate: “Getting a reliable JSON object out of an LLM used to mean wrapping every call in a try/except, re-prompting on parse failures, and hoping your production traffic never hit the 3% of responses that came back malformed.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `technical-documentation-best-practices-tested-real-developer-docs.md` | PROVISIONAL_REVIEW | Thesis candidate: “A documentation page can be accurate and still fail the moment a reader leaves the happy path.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `technical-documentation-template.md` | PHASE_A_EDITED | Thesis: “A documentation template can manufacture the appearance of order in seconds: a getting-started page, a reference section, a neat little slot for troubleshooting.” Fixture and claim checks passed; the edit still awaits independent editorial review. |
| Article | `technical-writing-for-ai-products-the-new-rules.md` | EVIDENCE_REQUIRED | Thesis candidate: “Technical writing for AI products has become a product design problem.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `technical-writing-for-engineers.md` | EVIDENCE_REQUIRED | Thesis candidate: “Documentation debt accumulates silently.” Automated sweep found 1 provenance candidate; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `the-agent-design-space.md` | EVIDENCE_REQUIRED | Thesis candidate: “Three weeks of reading production architecture posts, scraping GitHub for agent implementations, and talking to engineers who run agents at scale taught me one thing the taxonomy diagrams miss: I wanted to know what engineers are actually b” Automated sweep found 4 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `the-case-for-shorter-technical-documentation.md` | EVIDENCE_REQUIRED | Thesis candidate: “Technical documentation often suffers from information obesity.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `time-to-first-token-ttft.md` | EVIDENCE_REQUIRED | Thesis candidate: “Every interactive AI app I have shipped lives or dies by perceived latency.” Automated sweep found 5 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `types-of-technical-documentation.md` | PROVISIONAL_REVIEW | Thesis candidate: “Technical documentation is not one thing.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `voice-ai-latency-gemini-benchmark.md` | EVIDENCE_REQUIRED | Thesis candidate: “Voice latency is the sum of endpointing, transcription, model inference, speech synthesis, buffering, and transport.” Automated sweep found 3 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `what-is-technical-documentation-and-what-should-it-include.md` | PROVISIONAL_REVIEW | Thesis candidate: “Technical documentation is the material that helps someone understand, use, integrate with, or safely operate a system.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |
| Article | `why-coding-agents-lose-their-memory.md` | EVIDENCE_REQUIRED | Thesis candidate: “The first time I watched a coding agent forget a six-hour refactoring session, I assumed it was a bug.” Automated sweep found 3 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `why-devtools-startups-lose-deals-over-bad-docs.md` | EVIDENCE_REQUIRED | Thesis candidate: “DevTools startups lose deals over bad docs long before anyone writes "documentation" into a CRM field.” Automated sweep found 2 provenance candidates; a human must classify each KEEP, REWRITE, or CUT. |
| Article | `writing-release-notes-that-developers-trust.md` | PROVISIONAL_REVIEW | Thesis candidate: “It is late in the release cycle and someone wants to upgrade the SDK before the weekend.” Automated sweep found no provenance candidate; human evidence and editorial review remain pending. |

## Non-rendered pillar sources

| Surface | Path/source | Disposition | Audit |
| --- | --- | --- | --- |
| Pillar source | `content/pillars/ai-agent-architecture.yaml` | AUDIT_SOURCE | AI Agent Architecture: Patterns for Systems That Actually Ship: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/ai-agent-memory.yaml` | AUDIT_SOURCE | AI Agent Memory: A Practical Guide to Persistence, Recall, and Forgetting: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/ai-ready-documentation.yaml` | AUDIT_SOURCE | AI-Ready Documentation: Structure Content for Reliable Retrieval: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/ai-workflows.yaml` | AUDIT_SOURCE | AI Workflows and Automation: Getting Real Work Done with Coding Agents: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/api-documentation.yaml` | AUDIT_SOURCE | API Documentation: Reference, Guides, and Working Requests: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/docs-as-code.yaml` | AUDIT_SOURCE | Docs as Code: Git Workflows, Testing, and Maintenance: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/documentation-seo.yaml` | AUDIT_SOURCE | Documentation SEO: Make Developer Docs Discoverable: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/documentation.yaml` | AUDIT_SOURCE | Developer Documentation: Plan, Structure, Write, and Maintain It: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/llm-inference.yaml` | AUDIT_SOURCE | LLM Inference, Cost, and Internals: The Engineering Behind Fast, Cheap Models: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/rag.yaml` | AUDIT_SOURCE | RAG and Retrieval: Building Pipelines That Return the Right Context: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/technical-content.yaml` | AUDIT_SOURCE | Technical Content: Tutorials, Code Examples, and SEO Briefs: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |
| Pillar source | `content/pillars/technical-writing.yaml` | AUDIT_SOURCE | Technical Writing for DevTools: Content Engineers Actually Trust: not a standalone generated page; audit copy when it appears in feeds, links, or future hubs. |

## Omissions check

The structural inventory guard compares this register against `status: published` frontmatter and the explicit corpus sources. A missing or duplicate published article fails validation. It rejects canned opening phrases and near-duplicate openings, but it cannot approve meaning, evidence, or point of view.

Draft resources and nine non-published post files are outside the public corpus and remain untouched.
