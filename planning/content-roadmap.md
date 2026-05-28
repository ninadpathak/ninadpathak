# Content Roadmap — Demand-Driven Next Posts

These are not guesses. Every post below was *already linked to* from existing posts before
the 2026-05 link cleanup, which means the content was written as if these existed. I
repointed those links to the closest current post as a stopgap. When each post below ships,
upgrade the stopgap link to point at the real post (noted per item).

Priority = how many existing posts wanted it + cluster depth value.

## Cluster 2 — Agent Architecture (highest demand)

| Post | Slug | Wanted by | Stopgap currently points to |
|------|------|-----------|------------------------------|
| Tool Schema Design for Reliable Tool Calls | `tool-schema-design-for-reliability` | taxonomy, agent-loop-anatomy, agent-design-space | structured-outputs-llms-json-mode-function-calling |
| The Supervisor-Agent Pattern | `supervisor-agent-pattern` | taxonomy, agent-design-space | multi-agent-vs-single-agent-tradeoffs |
| Circuit Breakers for AI Agents | `agent-circuit-breakers` | why-agents-fail, agent-design-space | production-ai-agent-errors |
| The Agent Observability Stack | `agent-observability-stack` | why-agents-fail, agent-design-space | (unwrapped / production-ai-agent-errors) |
| Prompt Injection in Agent Systems | `prompt-injection-in-agent-systems` | why-agents-fail | (unwrapped to plain text) |
| Message Passing in Multi-Agent Systems | `message-passing-in-multi-agent-systems` | agent-design-space | multi-agent-vs-single-agent-tradeoffs |
| Parallel vs Sequential Tool Calls | `parallel-versus-sequential-tool-calls` | agent-design-space | agent-loop-anatomy |
| The Plan-and-Execute Pattern | `plan-and-execute-pattern` | agent-design-space | agent-loop-anatomy |
| Agent Evals That Actually Predict Production | `agent-evals-that-actually-predict-production` | agent-design-space | rag-evaluation-metrics-what-actually-matters |

## Cluster 3 — RAG & Retrieval

| Post | Slug | Wanted by | Stopgap currently points to |
|------|------|-----------|------------------------------|
| Vector Database Comparison: Pinecone vs Weaviate vs pgvector | `vector-databases-comparison` | rag-vs-memory | local-wasm-vector-benchmarks |
| Building RAG Pipelines with LangChain and Pinecone | `rag-pipelines-langchain-pinecone` | rag-vs-memory | how-anthropics-contextual-retrieval-changes-rag-architecture |
| Function Calling vs RAG: When to Use Each | `function-calling-vs-rag` | rag-vs-memory | structured-outputs-llms-json-mode-function-calling |
| Evaluating LLM Applications: A Practical Guide | `evaluating-llm-applications` | rag-vs-memory | rag-evaluation-metrics-what-actually-matters |
| RAG Optimization Techniques | `rag-optimization-techniques` | beam-memory-benchmark | semantic-caching-rag-optimization |

## Cluster 4 — Inference

| Post | Slug | Wanted by | Stopgap currently points to |
|------|------|-----------|------------------------------|
| Scaling LLM Inference Without GPUs | `scaling-llm-inference-without-gpus` | beam-memory-benchmark | speculative-decoding-explained |

---

## Visuals backlog (posts still without a visual)

26 posts still lack a visual. Highest-value to add next (visual-friendly + high search):
asymmetric-retrieval-agent-memory, the-memory-hierarchy-why-rag-is-not-enough,
episodic-vs-semantic-vs-working-memory-agents, the-taxonomy-of-ai-agents,
multi-agent-vs-single-agent-tradeoffs, semantic-caching-rag-optimization,
how-anthropics-contextual-retrieval, llm-context-windows-explained, prompt-caching,
time-to-first-token-ttft. Prefer pure CSS/SVG, same token block, same embed wrapper.

## Quality backlog (pre-existing, not introduced by the cleanup)

~30 older posts contain em dashes and/or forbidden words (leverage, gap, distance) that the
house linter flags. These predate the cleanup. A precision pass to bring them to house style
is worthwhile but should be done carefully to preserve first-person voice and meaning.
