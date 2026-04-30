# Content Plan: AI Agents Hub and Spoke (SEO-Optimized)

**Last updated:** 2026-04-28
**Goal:** 75 net-new articles across 9 topic clusters. Daily publishing starting now.

---

## Strategy

The hub-and-spoke model treats AI Agents as the central hub. Every spoke is a sub-topic that links back to the hub and to sibling spokes. Internal links flow naturally: an article about memory tiers links to context window management. An article about agent errors links to observability tooling. The model distributes link equity from high-traffic hub articles to deeper spoke content.

Each article targets one primary keyword and two secondary keywords. Secondary keywords are always drawn from the same cluster or adjacent clusters. This creates topical authority signals that Google rewards.

Articles are written first-person, conversational, and specific. No padding. Real examples from running code, reading papers, or deploying systems. The voice is a senior engineer who has actually done the thing, talking to another engineer who wants to know if it works and how to implement it.

---

## Cluster 1: AI Agents Hub

The authoritative center. Every AI agents article links here or to a related hub article.

| # | Status | Slug | Title | Primary Keyword | Notes |
|---|--------|------|-------|-----------------|-------|
| 1 | **existing** | state-of-ai-agent-memory-2026 | State of AI Agent Memory in 2026 | ai agent memory | Hub pillar |
| 2 | **existing** | production-ai-agent-errors | Production AI Agent Errors I Keep Seeing | production ai agents | Hub pillar |
| 3 | **existing** | agent-harnesses | Agent Harnesses: What Holds an AI Agent Together | ai agent architecture | Hub pillar |
| 4 | **existing** | agentic-cli-benchmarks | Agentic CLI Benchmarks: Claude Code vs Gemini CLI | agentic cli benchmarks | Hub pillar |
| 5 | written: 2026-04-21 | the-taxonomy-of-ai-agents | A Taxonomy of AI Agents That Actually Explains What You Are Building | types of ai agents | Core hub article |
| 6 | written: 2026-04-22 | why-ai-agents-keep-failing-in-production | Why AI Agents Keep Failing in Production and What the Field Is Doing About It | ai agent failures production | Links to production-ai-agent-errors |
| 7 | written: 2026-04-23 | agent-loop-anatomy | The Anatomy of an Agent Loop: Perceive, Think, Act, Remember | agent loop architecture | Links to agent-harnesses |
| 8 | written: 2026-04-26 | agent-vs-ai-assistant | When to Build an Agent and When to Build a Smarter Assistant | agent vs assistant | Hub intro for new readers |
| 9 | written: 2026-04-26 | the-agent-design-space | The Agent Design Space: A Map of What Engineers Are Actually Building | ai agent design patterns | Survey article, links to most spokes |
| 10 | written: 2026-04-27 | multi-agent-vs-single-agent-tradeoffs | Multi-Agent vs Single-Agent Systems: The Real Trade-offs | multi-agent systems | Links to production-ai-agent-errors (error propagation) |

---

## Cluster 2: Agent Memory (9 spokes from hub)

**Existing (8):** state-of-ai-agent-memory-2026, how-memory-works-in-claude-code, how-memory-works-in-deerflow, how-memory-works-in-hyperagents, memory-hierarchy-in-ai-systems, short-term-memory-for-ai-agents, memory-for-voice-ai-agents, ai-memory-management-for-llms, context-windows-vs-memory

**Gap topics (11):**

| # | Status | Slug | Title | Primary Keyword | Internal Links |
|---|--------|------|-------|-----------------|----------------|
|| 11 | written: 2026-04-28 | asymmetric-retrieval-agent-memory | Why Agent Memory Retrieval Is Asymmetric and Why It Breaks Your RAG Pipeline | agent memory retrieval | Links to: state-of-ai-agent-memory-2026, hybrid-search-bm25-vector-search |
|| 11b | written: 2026-04-29 | the-memory-hierarchy-why-rag-is-not-enough | The Memory Hierarchy: Why RAG Alone Is Not Enough for Agent Memory | rag vs agent memory | Links to: state-of-ai-agent-memory-2026, asymmetric-retrieval-agent-memory, rag-vs-fine-tuning | **Added: 2026-04-23 — HN trend on RAG-to-agent-memory evolution** |
|| 12 | written: 2026-04-30 | memory-serialization-between-sessions | Memory Serialization: How Agents Persist State Across Sessions | agent memory persistence | Links to: how-memory-works-in-claude-code, memory-hierarchy-in-ai-systems, the-memory-hierarchy-why-rag-is-not-enough | **Priority: moved up — direct response to HN "why do agents refuse to save observations"** |
|| 13 | new | episodic-vs-semantic-vs-working-memory-agents | Episodic, Semantic, and Working Memory in AI Agents: A Practical Map | agent memory types | Links to: state-of-ai-agent-memory-2026, memory-hierarchy-in-ai-systems |
|| 14 | new | memory-versioning-and-audit-trails | Memory Versioning and Audit Trails for Regulated AI Agents | ai agent memory audit | Links to: state-of-ai-agent-memory-2026, production-ai-agent-errors |
|| 15 | new | contextual-compression-for-agent-memory | Contextual Compression for Agent Memory: What Stays and What Goes | agent memory compression | Links to: llm-context-windows-explained, memory-hierarchy-in-ai-systems |
|| 16 | new | agent-memory-for-customer-support | Building a Customer Support Agent with Persistent Memory: A Worked Example | customer support ai agent | Links to: memory-for-voice-ai-agents, state-of-ai-agent-memory-2026 |
|| 17 | new | memory-attribution-errors | Why Your Agent Remembers the Wrong Thing: Memory Attribution Failures | agent memory errors | Links to: production-ai-agent-errors, episodic-vs-semantic-vs-working-memory-agents |
|| 18 | new | shared-vs-isolated-memory-multi-agent | Shared Memory vs Isolated Memory in Multi-Agent Workflows | multi-agent memory architecture | Links to: multi-agent-vs-single-agent-tradeoffs, memory-hierarchy-in-ai-systems |
| 11c | **NEW** | knowledge-graphs-for-agent-memory-the-practical-answer | Knowledge Graphs for Agent Memory: When They Help and When RAG Is Enough | knowledge graph agent memory | Links to: state-of-ai-agent-memory-2026, memory-hierarchy-in-ai-systems, rag-vs-fine-tuning, memory-serialization-between-sessions | **Added: 2026-04-30 — HN demand from Ask HN posts on KG for agent memory; direct answer to questions being asked** |
| 19 | new | fine-tuning-vs-rag-for-agent-memory | Fine-Tuning vs RAG for Agent Memory: When Each Approach Makes Sense | agent memory fine-tuning rag | Links to: rag-vs-fine-tuning, state-of-ai-agent-memory-2026 |
| 19b | new | zero-search-vs-retrieval-memory-agents | Zero-Search Memory for AI Agents: A Practical Evaluation | zero-search memory AI agents | Links to: state-of-ai-agent-memory-2026, asymmetric-retrieval-agent-memory, context-windows-vs-memory |

---

## Cluster 3: Context Windows and Prompting (4 existing + 9 new)

**Existing:** context-windows-vs-memory, llm-context-windows-explained, llm-token-budgets-cost-control, prompt-caching-what-it-is-and-when-the-math-works

**Gap topics (9):**

| # | Status | Slug | Title | Primary Keyword | Internal Links |
|---|--------|------|-------|-----------------|----------------|
| 20 | new | context-window-management-strategies | Context Window Management Strategies That Actually Work | context window management | Links to: llm-context-windows-explained, kv-cache-eviction-accuracy |
| 21 | new | prompt-injection-in-agent-systems | Prompt Injection in Agent Systems: What It Looks Like and How to Contain It | prompt injection agents | Links to: production-ai-agent-errors, model-context-protocol-explained |
| 22 | new | system-prompt-optimization | System Prompt Optimization: What I Learned Benchmarking 12 Configurations | system prompt optimization | Links to: prompt-caching-what-it-is-and-when-the-math-works, llm-context-windows-explained |
| 23 | new | sliding-window-context-for-long-agents | Sliding Window Context for Long-Running Agents | sliding window context | Links to: context-windows-vs-memory, short-term-memory-for-ai-agents |
| 24 | new | context-misuse-versus-context-overload | Context Misuse vs Context Overload: Two Different Agent Failure Modes | agent context overload | Links to: production-ai-agent-errors, context-windows-vs-memory |
| 25 | new |如何评价-context-window-utilization | How to Measure Whether Your Agent Is Using Its Context Well | context window utilization metrics | Links to: llm-token-budgets-cost-control, rag-evaluation-metrics-what-actually-matters |
| 26 | new | Few-shot prompting for agents | Few-Shot Prompting for Agents: When It Helps and When It Hurts | few-shot prompting agents | Links to: system-prompt-optimization, prompt-caching-what-it-is-and-when-the-math-works |
| 27 | new | Chain-of-thought tradeoffs for agents | Chain-of-Thought Reasoning in Agents: The Real Token Cost | chain of thought agents | Links to: context-window-management-strategies, kv-cache-eviction-accuracy |
| 28 | new | context-resetting-side-effects | The Side Effects of Context Resetting in Long Agent Sessions | agent context resetting | Links to: sliding-window-context-for-long-agents, memory-serialization-between-sessions |

---

## Cluster 4: Architectures and Frameworks (2 existing + 8 new)

**Existing:** agent-harnesses, model-context-protocol-explained

**Gap topics (8):**

| # | Status | Slug | Title | Primary Keyword | Internal Links |
|---|--------|------|-------|-----------------|----------------|
| 29 | new | react-agents-when-to-use-them | ReAct Agents: When to Use Them and When a Simpler Loop Works | react agent architecture | Links to: agent-loop-anatomy, the-taxonomy-of-ai-agents |
| 30 | new | plan-and-execute-pattern | The Plan-and-Execute Pattern: Why It Exists and Where It Breaks | plan and execute agents | Links to: react-agents-when-to-use-them, agent-loop-anatomy |
| 31 | new | hybrid-reasoning-agents | Hybrid Reasoning Agents: Combining LLM Thinking with Symbolic Planning | hybrid reasoning agents | Links to: react-agents-when-to-use-them, chain-of-thought tradeoffs for agents |
| 32 | new | supervisor-agent-pattern | The Supervisor Agent Pattern in Production | supervisor agent pattern | Links to: multi-agent-vs-single-agent-tradeoffs, plan-and-execute-pattern |
| 33 | new |evaluating-agent-frameworks-2026 | Evaluating Agent Frameworks in 2026: A Practical Framework | ai agent frameworks comparison | Links to: agent-harnesses, state-of-ai-agent-memory-2026 |
| 34 | new | when-to-build-而不是-buy-agent-infra | When to Build and When to Buy Agent Infrastructure | build vs buy agent infrastructure | Links to: evaluating-agent-frameworks-2026, production-ai-agent-errors |
| 35 | new | event-driven-agent-architectures | Event-Driven Agent Architectures: Design and Trade-offs | event-driven ai agents | Links to: supervisor-agent-pattern, multi-agent-vs-single-agent-tradeoffs |
| 36 | new | declarative-versus-imperative-agent-definitions | Declarative vs Imperative Agent Definitions | declarative agent definitions | Links to: the-agent-design-space, evaluating-agent-frameworks-2026 |

---

## Cluster 5: Tool Use and MCP (2 existing + 8 new)

**Existing:** model-context-protocol-explained, (1 more - verify existing)

**Gap topics (8):**

| # | Status | Slug | Title | Primary Keyword | Internal Links |
|---|--------|------|-------|-----------------|----------------|
| 37 | new | tool-schema-design-for-reliability | Tool Schema Design for Agent Reliability | tool schema design | Links to: model-context-protocol-explained, production-ai-agent-errors |
| 38 | new | MCP-security-patterns | MCP Security Patterns: What to Lock Down Before Production | MCP security | Links to: model-context-protocol-explained, prompt-injection-in-agent-systems |
| 39 | new | multi-tool-coordination-in-agents | Multi-Tool Coordination: How Agents Sequence Tool Calls | multi-tool agent coordination | Links to: agent-loop-anatomy, tool-schema-design-for-reliability |
| 40 | new | strict-versus-flexible-tool-schemas | Strict vs Flexible Tool Schemas: The Trade-offs for Agent Reliability | tool schema strict vs flexible | Links to: tool-schema-design-for-reliability, MCP-security-patterns |
| 41 | new | tool-result-caching-in-agents | Tool Result Caching in Agent Systems | tool result caching agents | Links to: prompt-caching-what-it-is-and-when-the-math-works, multi-tool-coordination-in-agents |
| 42 | new | dynamic-tool-discovery-at-runtime | Dynamic Tool Discovery at Runtime in AI Agents | dynamic tool discovery | Links to: when-to-build-而不是-buy-agent-infra, evaluating-agent-frameworks-2026 |
| 43 | new | parallel-versus-sequential-tool-calls | Parallel vs Sequential Tool Calls: When Agents Should Multitask | parallel tool calls agents | Links to: multi-tool-coordination-in-agents, agent-loop-anatomy |
| 44 | new | tool-call-retry-and-error-recovery | Tool Call Retry and Error Recovery for Production Agents | tool call retry agents | Links to: production-ai-agent-errors, multi-tool-coordination-in-agents |

---

## Cluster 6: Multi-Agent Orchestration (4 existing + 8 new)

**Existing:** production-ai-agent-errors (partial), state-of-ai-agent-memory-2026 (partial), short-term-memory-for-ai-agents, memory-for-voice-ai-agents

**Gap topics (8):**

| # | Status | Slug | Title | Primary Keyword | Internal Links |
|---|--------|------|-------|-----------------|----------------|
| 45 | new | supervisor-versus-hierarchical-multi-agent | Supervisor vs Hierarchical Multi-Agent: Choosing the Right Architecture | multi-agent hierarchy | Links to: supervisor-agent-pattern, multi-agent-vs-single-agent-tradeoffs |
| 46 | new | message-passing-in-multi-agent-systems | Message Passing in Multi-Agent Systems: Patterns and Pitfalls | message passing multi-agent | Links to: event-driven-agent-architectures, shared-vs-isolated-memory-multi-agent |
| 47 | new | shared-state-versus-message-passing | Shared State vs Message Passing in Multi-Agent Workflows | shared state vs message passing | Links to: message-passing-in-multi-agent-systems, shared-vs-isolated-memory-multi-agent |
| 48 | new | agent-messenger-architectures | Messenger Architectures for AI Agents: A Practical Survey | messenger architecture ai agents | Links to: message-passing-in-multi-agent-systems, event-driven-agent-architectures |
| 49 | new | context-pollution-in-multi-agent-loops | Context Pollution in Multi-Agent Loops: How It Happens and How to Stop It | multi-agent context pollution | Links to: production-ai-agent-errors, shared-vs-isolated-memory-multi-agent |
| 50 | new | agent-coordination-costs | The Hidden Coordination Costs of Multi-Agent Systems | multi-agent coordination costs | Links to: multi-agent-vs-single-agent-tradeoffs, llm-token-budgets-cost-control |
| 51 | new | role-assignment-in-agent-teams | Role Assignment in Agent Teams: Static vs Dynamic | agent role assignment | Links to: supervisor-versus-hierarchical-multi-agent, messenger-architectures |
| 52 | new | consensus-and-voting-in-agent-systems | Consensus and Voting Patterns in Agent Ensembles | agent consensus voting | Links to: role-assignment-in-agent-teams, message-passing-in-multi-agent-systems |

---

## Cluster 7: Production, Reliability, and Observability (2 existing + 9 new)

**Existing:** production-ai-agent-errors, agentic-cli-benchmarks

**Gap topics (9):**

| # | Status | Slug | Title | Primary Keyword | Internal Links |
|---|--------|------|-------|-----------------|----------------|
| 53 | new | agent-latency-optimization | Agent Latency Optimization: From Prompt to Action | ai agent latency optimization | Links to: time-to-first-token-ttft, production-ai-agent-errors |
| 54 | new | ai-agent-cost-analysis-per-call | AI Agent Cost Analysis: Breaking Down Cost Per Agentic Call | ai agent cost optimization | Links to: llm-token-budgets-cost-control, agent-latency-optimization |
| 55 | new | agent-observability-stack | The Observability Stack for AI Agents in Production | ai agent observability | Links to: production-ai-agent-errors, agent-latency-optimization |
| 56 | new | agent-circuit-breakers | Circuit Breakers for AI Agents: Preventing Cascade Failures | agent circuit breaker pattern | Links to: production-ai-agent-errors, agent-observability-stack |
| 57 | new | agent-rate-limiting | Rate Limiting Strategies for AI Agent APIs | ai agent rate limiting | Links to: llm-token-budgets-cost-control, production-ai-agent-errors |
| 58 | new | agent-timeout-strategies | Timeout Strategies for AI Agents: A Practical Guide | agent timeout strategies | Links to: production-ai-agent-errors, agent-circuit-breakers |
| 59 | new | agent-degraded-modes | Designing Degraded Modes for AI Agents | agent degraded mode design | Links to: agent-circuit-breakers, agent-observability-stack |
| 60 | new | agent-sla-targets | Setting SLA Targets for AI Agents: What Is Realistic | ai agent SLA | Links to: agent-latency-optimization, agent-timeout-strategies |
| 61 | new | agent-canary-deployments | Canary Deployments for AI Agent Updates | ai agent canary deployments | Links to: agent-degraded-modes, agent-circuit-breakers |

---

## Cluster 8: RAG and Retrieval (6 existing + 8 new)

**Existing:** hybrid-search-bm25-vector-search, embedding-models-compared, rag-evaluation-metrics-what-actually-matters, rag-vs-fine-tuning, rag-vs-memory, reranking-in-rag-why-your-top-k-results-are-probably-wrong

**Gap topics (8):**

| # | Status | Slug | Title | Primary Keyword | Internal Links |
|---|--------|------|-------|-----------------|----------------|
| 62 | new | parent-document-retrieval-for-agents | Parent Document Retrieval for Agentic RAG | parent document retrieval | Links to: rag-evaluation-metrics-what-actually-matters, hybrid-search-bm25-vector-search |
| 63 | new | hybrid-rag-implementation-guide | Hybrid RAG Implementation: From BM25 to Reranking | hybrid rag implementation | Links to: hybrid-search-bm25-vector-search, reranking-in-rag-why-your-top-k-results-are-probably-wrong |
| 64 | new | contextual-retrieval-bm25-understanding | How Anthropic's Contextual Retrieval Changes RAG Architecture | contextual retrieval | Links to: how-anthropics-contextual-retrieval-changes-rag-architecture, hybrid-rag-implementation-guide |
| 65 | new | knowledge-graph-rag-complex-queries | Knowledge Graph RAG for Complex Relational Queries | knowledge graph rag | Links to: hybrid-rag-implementation-guide, rag-evaluation-metrics-what-actually-matters |
| 66 | new | semantic-chunking-for-agent-retrieval | Semantic Chunking vs Fixed-Size Chunking for Agentic Retrieval | semantic chunking agents | Links to: hybrid-rag-implementation-guide, parent-document-retrieval-for-agents |
| 67 | new | late-interaction-models-colbert-for-rag | Late Interaction Models (ColBERT) for RAG: A Practical Evaluation | colbert late interaction rag | Links to: reranking-in-rag-why-your-top-k-results-are-probably-wrong, embedding-models-compared |
| 68 | new | mmr-diversity-retrieval-for-agents | Maximal Marginal Relevance and Diversity Retrieval for Agents | diversity retrieval agents | Links to: semantic-chunking-for-agent-retrieval, late-interaction-models-colbert-for-rag |
| 69 | new | real-time-rag-updates-for-agents | Real-Time RAG Updates for Fast-Changing Data Sources | real-time rag agents | Links to: parent-document-retrieval-for-agents, hybrid-rag-implementation-guide |

---

## Cluster 9: LLM Internals and Inference (6 existing + 10 new)

**Existing:** kv-cache-eviction-accuracy, speculative-decoding-explained, mixture-of-experts-explained, structured-outputs-llms-json-mode-function-calling, prompt-caching-what-it-is-and-when-the-math-works, time-to-first-token-ttft

**Gap topics (10):**

| # | Status | Slug | Title | Primary Keyword | Internal Links |
|---|--------|------|-------|-----------------|----------------|
| 70 | new | attention-mechanisms-explained-for-engineers | Attention Mechanisms Explained for Engineers Who Need to Debug Them | attention mechanism explained | Links to: kv-cache-eviction-accuracy, mixture-of-experts-explained |
| 71 | new | kv-cache-compression-techniques | KV Cache Compression Techniques: A Practical Survey | kv cache compression | Links to: kv-cache-eviction-accuracy, context-window-management-strategies |
| 72 | new | quantization-for-agent-deployment | Quantization for Agent Deployment: INT8 vs INT4 vs NF4 | quantization for llm agents | Links to: kv-cache-eviction-accuracy, local-wasm-vector-benchmarks |
| 73 | new | batch-inference-for-agents | Batch Inference Optimization for High-Throughput Agents | batch inference agents | Links to: llm-token-budgets-cost-control, agent-latency-optimization |
| 74 | new | speculative-decoding-practical-implementation | Speculative Decoding: Practical Implementation and Real Bottlenecks | speculative decoding implementation | Links to: speculative-decoding-explained, time-to-first-token-ttft |
| 75 | new | flash-attention-memory-tradeoffs | Flash Attention: Memory and Performance Trade-offs on Real Hardware | flash attention memory | Links to: kv-cache-eviction-accuracy, kv-cache-compression-techniques |
| 76 | new | continuous-batching-for-agents | Continuous Batching for Agents: Latency vs Throughput Trade-offs | continuous batching agents | Links to: batch-inference-for-agents, speculative-decoding-practical-implementation |
| 77 | new | prefix-caching-explained | Prefix Caching Explained: What Stays Cached and Why It Breaks Sometimes | prefix caching llm | Links to: prompt-caching-what-it-is-and-when-the-math-works, kv-cache-compression-techniques |
| 78 | new | sparsity-in-mixture-of-agents | Sparsity in Mixture of Experts: What Activates and What Gets Skipped | mixture of experts sparsity | Links to: mixture-of-experts-explained, quantization-for-agent-deployment |
| 79 | new | streaming-versus-blocking-agent-responses | Streaming vs Blocking Agent Responses: A Latency Comparison | streaming agent responses | Links to: time-to-first-token-ttft, agent-latency-optimization |

---

## Cluster 10: Evaluation and Benchmarking (3 existing + 8 new)

**Existing:** agentic-cli-benchmarks, local-wasm-vector-benchmarks, beam-memory-benchmark

**Gap topics (8):**

| # | Status | Slug | Title | Primary Keyword | Internal Links |
|---|--------|------|-------|-----------------|----------------|
| 80 | new | agent-evals-that-actually-predict-production | Agent Evals That Actually Predict Production Behavior | agent evaluation framework | Links to: rag-evaluation-metrics-what-actually-matters, production-ai-agent-errors |
| 81 | new | benchmark-agent-memory-latency | Benchmarking Agent Memory: Latency and Accuracy Trade-offs | agent memory benchmark | Links to: beam-memory-benchmark, kv-cache-eviction-accuracy |
| 82 | new | harness-versus-organic-agent-testing | Harness Testing vs Organic Agent Testing: When Each Applies | agent testing methodologies | Links to: agent-evals-that-actually-predict-production, agent-harnesses |
| 83 | new | red-teaming-ai-agents | Red Teaming AI Agents: Prompt Injection, Context Overflow, and Memory Attacks | red teaming ai agents | Links to: prompt-injection-in-agent-systems, agent-evals-that-actually-predict-production |
| 84 | new | agent-success-rate-benchmarks | Agent Success Rate Benchmarks: Defining and Measuring What Success Looks Like | agent success rate metrics | Links to: agent-evals-that-actually-predict-production, agentic-cli-benchmarks |
| 85 | new | human-in-the-loop-evaluation | Human-in-the-Loop Evaluation for AI Agents | human in the loop agent eval | Links to: agent-evals-that-actually-predict-production, agent-observability-stack |
| 86 | new | regression-testing-for-agent-updates | Regression Testing for Agent Behavior After Model Updates | agent regression testing | Links to: agent-canary-deployments, agent-evals-that-actually-predict-production |
| 92 | new | why-agent-benchmarks-lie | Why Agent Benchmarks Lie: What Trustworthy Evaluation Actually Looks Like | ai agent benchmark reliability | Links to: agent-evals-that-actually-predict-production, production-ai-agent-errors | **Added: 2026-04-28 — HN trend on benchmark exploitation; response to Berkeley RDI article** |

---

## Cluster 11: DevTools and AI (partial overlap with existing + 5 new)

**Existing:** uv-package-manager-benchmark, how-to-write-a-changelog-developers-actually-read, how-to-write-a-technical-tutorial-that-actually-teaches, technical-writing-for-engineers, technical-writing-for-ai-products-the-new-rules, developer-onboarding-docs-what-works-what-doesnt, why-devtools-startups-lose-deals-over-bad-docs, the-case-for-shorter-technical-documentation, writing-release-notes-that-developers-trust, developer-trust-hierarchy

**Gap topics (5):**

| # | Status | Slug | Title | Primary Keyword | Internal Links |
|---|--------|------|-------|-----------------|----------------|
| 87 | new | ai-code-review-automation | AI Code Review Automation: What Works and What Produces Noise | ai code review automation | Links to: best-llms-for-coding, agent-evals-that-actually-predict-production |
| 88 | new | agentic-ci-cd-build-automation | Agentic CI/CD: Using AI Agents in Build and Deployment Pipelines | agentic ci cd | Links to: agentic-cli-benchmarks, agent-canary-deployments |
| 89 | new | debugging-agent-behaviors-in-production | Debugging Agent Behaviors in Production: Tools and Patterns | debugging ai agents production | Links to: agent-observability-stack, agent-latency-optimization |
| 90 | new | developer-handoff-in-ai-features | Developer Handoff Patterns When Shipping AI Features | ai feature developer handoff | Links to: technical-writing-for-ai-products-the-new-rules, agent-observability-stack |
| 91 | new | ai-assistants-in-legacy-codebase-migration | Using AI Assistants for Legacy Codebase Migration | ai legacy code migration | Links to: best-llms-for-coding, ai-code-review-automation |

---

## Writing Workflow

### Article structure

Every article follows this pattern. No exceptions.

**Frontmatter (required):**
```yaml
title: "Exact Article Title"
date: "YYYY-MM-DD"
description: "One sentence under 160 chars for SEO meta"
tags: ["tag1", "tag2"]
status: published
```

**Body:**
1. Opening hook: specific, first-person, no fluff. One paragraph that states the problem or observation.
2. Core explanation: what it is, how it works, when to use it. Specific numbers and examples.
3. Worked example or benchmark data if applicable.
4. Trade-offs and failure modes.
5. Practical recommendations.
6. Links to related articles placed naturally in context (not in a dedicated section).

### Internal linking rules

Links are woven into sentences naturally. Acceptable: "If you want to understand the memory hierarchy, I wrote about it in my post on [memory-hierarchy-in-ai-systems](/articles/memory-hierarchy-in-ai-systems)." Not acceptable: "As I wrote in my previous article about memory, which you can find here..."

Links per article: 7-10. All links must be contextually relevant.

### Voice rules (enforced)

- First person required throughout. "I", "I think", "I found", "I almost made this mistake."
- No em-dashes, semicolons, horizontal rules.
- No banned phrases from the writing-rules skill.
- Short sentences. One idea per sentence.
- Active voice.
- No sentence starts with: In, This, By, Finally, Most, Ever.
- Specific numbers over vague quantities.
- Real examples from code, benchmarks, or deployments.
- Controversial takes where warranted.

### File naming

`YYYY-MM-DD-slug.md` where slug is the kebab-case version of the title.

### Publishing pipeline

1. Write article in `content/posts/YYYY-MM-DD-slug.md`
2. Build: `cd ~/ninadpathak && python3 build.py`
3. Push: `git add . && git commit -m "Article: Title" && git push origin main`
4. Mark as written in this plan: change status from "new" to "written: YYYY-MM-DD"
5. Log in `planning/post-queue.md`

---

## Article Assignment Queue

The cron job picks the next unwritten article from this list in order. Priority goes to Cluster 1 hub articles first, then Cluster 2 (memory), then Cluster 3 (context windows), then outward spokes.

### Priority order for cron job

1. Cluster 1, Article 5: the-taxonomy-of-ai-agents
2. Cluster 1, Article 6: why-ai-agents-keep-failing-in-production
3. Cluster 1, Article 7: agent-loop-anatomy
4. Cluster 1, Article 8: agent-vs-ai-assistant
5. Cluster 1, Article 9: the-agent-design-space
6. Cluster 1, Article 10: multi-agent-vs-single-agent-tradeoffs
7. Cluster 2, Article 11: asymmetric-retrieval-agent-memory
8. Cluster 2, Article 12: memory-serialization-between-sessions
9. Cluster 2, Article 13: episodic-vs-semantic-vs-working-memory-agents
10. ...continuing through the list

---

## SEO Notes

- Each article targets a primary keyword from the title and secondary keywords from the cluster
- H2 headings should contain keywords where natural
- First paragraph should contain the primary keyword
- Internal links use the pattern `/articles/slug` for the static site
- Description field is the meta description (under 160 chars)
- Tags should include at least one cluster keyword

---

*Last article queued: 91 (ai-assistants-in-legacy-codebase-migration)*
*Existing articles as of 2026-04-21: 50*
*New articles to write: 41*
