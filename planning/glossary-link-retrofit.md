# Glossary inbound-link retrofit

Prepared 2026-08-17. These are the article passages that should link back to the expanded glossary definitions. The anchor belongs in the existing explanatory sentence named below, not in a related-reading block.

| Glossary entry | Existing article slug to retrofit | Sentence or anchor concept |
|---|---|---|
| Context engineering | `how-anthropics-contextual-retrieval-changes-rag-architecture.md` | The first passage that distinguishes contextual retrieval from prompt construction should link “context engineering.” |
| Agentic engineering | `the-agent-design-space.md` | The opening definition of the engineering discipline should link “agentic engineering.” |
| Flow engineering | `agentic-workflow-playbook.md` | The passage that explains staged generation, checking, and revision should link “flow engineering.” |
| Test-time compute | `llm-inference-optimization.md` | The comparison between inference-time quality work and serving optimizations should link “test-time compute.” |
| Model Context Protocol | `model-context-protocol-explained.md` | The first self-contained protocol definition should link “Model Context Protocol.” |
| Semantic caching | `semantic-caching-rag-optimization.md` | The first explanation of similarity-based response reuse should link “semantic caching.” |
| Matryoshka Representation Learning | `embedding-models-compared.md` | The discussion of useful embedding prefixes or dimension truncation should link the full term. |
| Cross-encoder reranking | `reranking-in-rag-why-your-top-k-results-are-probably-wrong.md` | The sentence that contrasts joint query-document scoring with independent embeddings should link “cross-encoder reranking.” |
| Late chunking | `how-anthropics-contextual-retrieval-changes-rag-architecture.md` | The comparison with other index-time context methods should link “late chunking.” |
| GraphRAG | `rag-evaluation-metrics-what-actually-matters.md` | The passage about evaluating relationship or corpus-level retrieval should link “GraphRAG.” |
| Tool calling | `structured-outputs-llms-json-mode-function-calling.md` | The sentence where a model returns arguments for a host-executed operation should link “tool calling.” |
| PagedAttention | `llm-inference-optimization.md` | The KV-cache memory-layout passage should link “PagedAttention.” |
| KV-cache eviction | `kv-cache-eviction-accuracy.md` | The first definition of removing retained token state should link “KV-cache eviction.” |
| Semantic chunking | `how-anthropics-contextual-retrieval-changes-rag-architecture.md` | The boundary-selection comparison should link “semantic chunking.” |
| Hypothetical Document Embeddings | `hybrid-search-bm25-vector-search.md` | The query-expansion passage should link “Hypothetical Document Embeddings.” |
| Self-querying retrieval | `hybrid-search-bm25-vector-search.md` | The passage separating semantic retrieval from metadata filters should link “self-querying retrieval.” |
| Bi-encoder | `embedding-models-compared.md` | The explanation of independently encoded query and document vectors should link “bi-encoder.” |
| Product quantization | `embedding-models-compared.md` | The vector compression passage should link “product quantization.” |
| HNSW | `local-wasm-vector-benchmarks.md` | The graph-index explanation should link “HNSW,” without using the article as benchmark proof. |
| ReAct prompting | `agent-loop-anatomy.md` | The action-observation loop comparison should link “ReAct prompting.” |
| Plan-and-Solve | `agentic-workflow-playbook.md` | The passage about producing a plan before execution should link “Plan-and-Solve.” |
| Speculative decoding | `speculative-decoding-explained.md` | The first draft-and-verify mechanism description should link “speculative decoding.” |
| Agentic router | `multi-agent-vs-single-agent-tradeoffs.md` | The passage about choosing among specialized execution paths should link “agentic router.” |
| JSON mode vs. structured outputs | `structured-outputs-llms-json-mode-function-calling.md` | The first contrast between syntax validity and schema adherence should link the glossary comparison. |
| DSPy | `rag-evaluation-metrics-what-actually-matters.md` | The passage about optimizing an LLM program against a metric should link “DSPy.” |

No glossary slugs were merged. Each entry has a distinct technical boundary, operational decision, or failure mode, so merging would make at least one definition less precise.
