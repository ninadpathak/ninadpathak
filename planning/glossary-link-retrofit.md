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

## Merge review

No glossary slugs were merged. The decision was made term by term, not from a preference for preserving the current count.

| Term | Decision | Boundary that justifies the decision |
|---|---|---|
| Context engineering | Keep | Owns assembly of instructions, evidence, state, and tool results for one model step. Prompt engineering and memory each cover only part of that boundary. |
| Agentic engineering | Keep | Owns the engineering discipline around model-controlled actions, state, permissions, recovery, and completion evidence. Tool calling is only one interface inside it. |
| Flow engineering | Keep | Owns host-controlled sequences of generated artifacts and independent checks. An agentic loop lets the model choose the route. |
| Test-time compute | Keep | Owns additional search, sampling, or verification work spent after a request arrives. Speculative decoding targets serving speed while preserving the target distribution. |
| Model Context Protocol | Keep | Owns the host-client-server protocol boundary for discovering resources and tools. Tool calling describes a model request inside or outside that protocol. |
| Semantic caching | Keep | Owns semantic response reuse and its eligibility and invalidation risks. Prompt caching reuses prefix computation, not an answer selected by meaning. |
| Matryoshka Representation Learning | Keep | Owns embeddings trained to support useful nested prefixes. Product quantization compresses subspaces after representation learning. |
| Cross-encoder reranking | Keep | Owns joint query-candidate scoring over a small retrieved set. A bi-encoder independently encodes a large reusable corpus. |
| Late chunking | Keep | Owns the order in which contextual encoding and chunk pooling occur. Semantic chunking chooses boundaries instead. |
| GraphRAG | Keep | Owns graph-derived retrieval for relationship and corpus-level questions. Ordinary RAG does not require entity resolution, edges, or community summaries. |
| Tool calling | Keep | Owns the request loop in which a model selects an operation and supplies arguments while the host executes it. MCP standardizes discovery and transport across a connection. |
| PagedAttention | Keep | Owns non-contiguous placement and mapping of retained KV-cache blocks. KV-cache eviction removes states rather than placing them. |
| KV-cache eviction | Keep | Owns the policy for discarding retained token states under memory pressure. Paging and quantization retain the logical state in different storage forms. |
| Semantic chunking | Keep | Owns boundary selection according to topical change. Late chunking changes when embeddings are produced for whichever boundaries were chosen. |
| Hypothetical Document Embeddings | Keep | Owns answer-like query transformation for zero-shot dense retrieval. It generates a search representation, not filters or evidence. |
| Self-querying retrieval | Keep | Owns translation of natural language into a semantic query plus typed metadata filters. HyDE generates an answer-like document rather than a filter expression. |
| Bi-encoder | Keep | Owns independent, reusable query and document encodings for first-stage retrieval. Cross-encoder reranking jointly reads each pair and cannot replace corpus-scale pre-encoding. |
| Product quantization | Keep | Owns codebook-based lossy vector compression. HNSW navigates a graph, and MRL trains prefixes to remain useful at several dimensions. |
| HNSW | Keep | Owns multilayer graph navigation for approximate nearest-neighbor search. It neither creates nor compresses the vectors it indexes. |
| ReAct prompting | Keep | Owns an adaptive action-observation trajectory in which new evidence changes the next step. Plan-and-Solve decomposes the task before execution. |
| Plan-and-Solve | Keep | Owns upfront decomposition intended to expose omitted dependent steps. ReAct is better when observations must continually change the route. |
| Speculative decoding | Keep | Owns draft-and-verify inference that preserves the target model distribution. Test-time compute spends extra work to improve or select an answer. |
| Agentic router | Keep | Owns selection among externally visible models, agents, tools, workflows, or human paths. A planner decomposes work after a path is selected. |
| JSON mode vs. structured outputs | Keep | Owns the application decision between syntax validity and schema adherence. It stays a comparison entry because separating the two into standalone terms would duplicate the same consumer contract and failure example. |
| DSPy | Keep | Owns declarative LLM programs optimized against examples and a metric. Flow engineering is the broader orchestration pattern and does not prescribe an optimizer. |
