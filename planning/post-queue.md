# Daily Post Queue (v4.1 - Experiment & Benchmark Driven)

Posts are published one per day. Claude picks the next post, runs the experiment, writes the post-mortem, builds, and pushes.

## Queue (ordered)

20. **Beyond the chatbox: benchmarking Claude Code vs. Gemini CLI for autonomous repository refactoring**
    - Target: Apr 12, 2026
    - Visual: 2D success/fail rate comparison; Timeline of self-correction loops; Traces of file-system manipulation.
    - Primary Keyword: agentic CLI benchmarks
    - HN Hook: I gave two agentic CLIs the same legacy repo and a list of bugs. Here is the success-rate data and trace logs.

21. **100ms vector search in the browser: PGLite vs SQLite-vec head-to-head**
    - Target: Apr 13, 2026
    - Visual: 2D Bar chart of query latency over 100k vectors; Sequence diagram of WASM DB initialization.
    - Primary Keyword: local WASM vector database benchmarks
    - HN Hook: Moving RAG to the edge. I benchmarked the two fastest WASM relational-vector databases.

22. **From 4 minutes to 12 seconds: a quantitative audit of the uv package manager**
    - Target: Apr 14, 2026
    - Visual: 2D Stacked bar chart of cold vs warm build times; Screenshot of `uv lock` vs `poetry lock`.
    - Primary Keyword: uv vs poetry benchmark
    - HN Hook: I migrated a monolithic 500-dependency repo to uv. Here is exactly where the time was saved.

23. **Context engineering as heap management: measuring accuracy vs KV cache eviction**
    - Target: Apr 15, 2026
    - Visual: 3D Heatmap of "Attention Decay" as cache blocks are evicted; 2D line chart of RAG accuracy vs Pruning ratio.
    - Primary Keyword: KV cache eviction strategies
    - HN Hook: You don't need a 2M token window if you manage it like a garbage-collected heap.

24. **The 800ms barrier: profiling the latency chain of a real-time Gemini 3.1 voice agent**
    - Target: Apr 16, 2026
    - Visual: 2D Timeline of the A2A (Audio-to-Audio) request/response loop; Waterfall chart of network vs. inference latency.
    - Primary Keyword: real-time voice AI latency
    - HN Hook: I built a sub-second latency voice assistant. Here is the bottleneck analysis.

25. **Local reranking on M2: measuring the latency tax of Cross-Encoders**
    - Target: Apr 17, 2026
    - Visual: 2D Tradeoff chart (MRR vs Latency); Screenshot of Python profiler showing top-K processing time.
    - Primary Keyword: BGE-Reranker-v3 local performance
    - HN Hook: Everyone says reranking is "slow." I measured exactly how slow it is on unified memory.

26. **Triples beat vectors: a GraphRAG implementation post-mortem**
    - Target: Apr 18, 2026
    - Visual: 3D Interactive Knowledge Graph showing relationship traversal; 2D Accuracy comparison (GraphRAG vs Naive RAG).
    - Primary Keyword: GraphRAG vs vector search
    - HN Hook: Semantic search failed at complex relational queries. Here is how I implemented GraphRAG to fix it.

27. **Memory poisoning in multi-agent workflows: a quantified hallucination audit**
    - Target: Apr 19, 2026
    - Visual: 2D Confusion matrix of agent task crossovers; Sequence diagram of a 5-agent "Context Quarantine" loop.
    - Primary Keyword: multi-agent hallucination rates
    - HN Hook: I ran a 5-agent chain with and without context isolation. halllucination rates dropped by 45%.

28. **The intelligent compiler: profiling Mago linting speeds in enterprise PHP repos**
    - Target: Apr 20, 2026
    - Visual: 2D Comparison chart (Mago vs PHPStan vs Psalm); Waterfall chart of AST parsing time.
    - Primary Keyword: Mago PHP linter benchmark
    - HN Hook: Rust-native tooling is finally arriving for PHP. Here is the throughput analysis.

29. **The 16GB VRAM ceiling: profiling DeepSeek-V4 MoE inference on an M2 Air**
    - Target: Apr 21, 2026
    - Visual: 2D Line chart of tokens/sec vs. context size; Activity Monitor screenshot.
    - Primary Keyword: DeepSeek-V4 local benchmark
    - HN Hook: Can a 16GB Air handle a 1T parameter MoE? (Yes, with 4-bit quantization, and here is the profiler data).

30. **Think Anywhere: measuring the efficiency of learnable reasoning token placement**
    - Target: Apr 22, 2026
    - Visual: 2D Timeline of reasoning token activation during generation; 2D Tokens/sec vs Thinking Budget.
    - Primary Keyword: learnable reasoning tokens
    - HN Hook: Stop putting CoT at the start. I implemented dynamic thinking tokens and saved 20% on compute.

31. **A Taxonomy of AI Agents That Actually Explains What You Are Building**
    - Published: 2026-04-21
    - Slug: the-taxonomy-of-ai-agents
    - Cluster: AI Agents Hub (Cluster 1)

32. **Why AI Agents Keep Failing in Production and What the Field Is Doing About It**
    - Published: 2026-04-22
    - Slug: why-ai-agents-keep-failing-in-production
    - Cluster: AI Agents Hub (Cluster 1)

33. **When to Build an Agent and When to Build a Smarter Assistant**
    - Published: 2026-04-26
    - Slug: agent-vs-ai-assistant
    - Cluster: AI Agents Hub (Cluster 1)

34. **Multi-Agent vs Single-Agent Systems: The Real Trade-offs**
    - Published: 2026-04-27
    - Slug: multi-agent-vs-single-agent-tradeoffs
    - Cluster: AI Agents Hub (Cluster 1)

## 2026-04-28
- **Title**: Why Agent Memory Retrieval Is Asymmetric and Why It Breaks Your RAG Pipeline
- **Slug**: asymmetric-retrieval-agent-memory
- **Cluster**: Agent Memory (Cluster 2)

## Writing & Visual Rules (V4.0)

- **Word Count**: 3000+ words.
- **Tone**: Cynical, practitioner-first, Hacker News style.
- **Visuals**: 12+ per post. MUST be data-driven (charts, sequence diagrams, profiler screenshots).
- **Casing**: Title Case for titles. Sentence case for headings.
- **Proof**: Link to the benchmark script or repo for every article.

## Published (2026)

- 2026-04-29 | The Memory Hierarchy: Why RAG Alone Is Not Enough for Agent Memory | the-memory-hierarchy-why-rag-is-not-enough
2026-04-30 | Memory Serialization: How Agents Persist State Across Sessions | memory-serialization-between-sessions

92. **Episodic, Semantic, and Working Memory in AI Agents: A Practical Map**
    - Date: 2026-05-04
    - Slug: episodic-vs-semantic-vs-working-memory-agents
    - Primary Keyword: agent memory types
    - Status: published

2026-05-05 | Contextual Compression for Agent Memory: What Stays and What Goes | contextual-compression-for-agent-memory
2026-05-06 | Why Your Coding Agent Keeps Forgetting Everything: Memory Persistence in AI Coding Assistants | why-coding-agents-lose-their-memory
