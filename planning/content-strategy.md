# Content Strategy: Ninad Pathak Portfolio (v4.0 - The Experiment Era)

**Hardware Baseline**: MacBook Air M2, 16GB Unified Memory.
**Core Objective**: Transition from "Technical Explainer" to "Engineering Laboratory." Every article must be anchored in code written, benchmarks run, and failures documented on local hardware. 
**Target Audience**: The Hacker News reader who ignores marketing but upvotes "I ran X on Y and here is the profiler output."

---

## The Strategic Pivot: Un-fabricatable Data

We are moving away from general advice. If a topic can be summarized by an AI Overview without a human running code, we are not writing it. We are building a "Competitive Moat" through **local instrumentation**.

### The Experiment Framework (Strict Requirements)
1.  **Repository-Linked**: Every article must reference a specific setup (Ollama, vLLM, local WASM DBs, or specific open-source benchmarks).
2.  **Hardware-Specific Findings**: Documenting how 16GB Unified Memory behaves under pressure (Swap usage, thermal throttling impacts on inference, memory pressure graphs).
3.  **The "Failure" Section**: Every post must include a section on what didn't work (e.g., "The model OOM'd at 4k context tokens").
4.  **Meaningful 2D/3D Data Visuals**: No more generic shapes. Visuals must be generated from the test result JSON/CSV files.

---

## The Next 20: Engineering Benchmarks & Implementation Post-mortems

### Hub 1: Local Inference & Memory Pressure
*   **The VRAM ceiling: running 1T parameter MoE models on a 16GB M2 Air**
    *   *Experiment*: Testing DeepSeek-V4 (quantized) and Mistral Large 3 local weights.
    *   *Metric*: Token/sec vs. Memory Pressure.
*   **Context engineering as RAM management: implementing KV cache eviction in TurboQuant**
    *   *Experiment*: Measuring accuracy decay as we aggressively prune the context window.
*   **The 800ms barrier: measuring local A2A (Audio-to-Audio) latency on Gemini 3.1 Flash Lite**
    *   *Experiment*: Building a real-time voice agent and profiling the latency chain.

### Hub 2: Edge Databases & Retrieval (RAG 3.0)
*   **100ms vector search in the browser: a head-to-head of PGLite vs SQLite-vec**
    *   *Experiment*: Indexing 100,000 vectors and measuring query time under concurrent load.
*   **Triples beat vectors: a production-grade post-mortem of GraphRAG vs Traditional RAG**
    *   *Experiment*: Testing "relationship-heavy" queries against a 10k document set.
*   **Local reranking: does a Cross-Encoder matter on 16GB?**
    *   *Experiment*: Comparing BGE-Reranker-v3 latency vs accuracy gains.

### Hub 3: Agentic Orchestration & Toolchains
*   **From 4 minutes to 12 seconds: a quantitative audit of uv and Mago toolchains**
    *   *Experiment*: Moving a 500-dependency project from Poetry to uv.
*   **Claude Code vs Cursor: a structural analysis of agentic file manipulation**
    *   *Experiment*: Forcing agents to refactor a legacy 10k LOC codebase and measuring success rate.
*   **Memory poisoning in shared contexts: measuring the hallucination rate of multi-agent loops**
    *   *Experiment*: Testing "Context Quarantine" vs Shared History in a 5-agent chain.

---

## Writing & Visual Rules (V4.0)

1.  **Title Case Titles / sentence case headings.**
2.  **Direct Answer**: "I reduced build times by 85% by switching to uv."
3.  **No Contrastive Parallelism**: Use factual evidence.
4.  **Visual Density**: 12+ visuals per post. Visuals MUST be data-driven (charts, sequence diagrams, profiler screenshots).
5.  **Verified Proof**: Use real screenshots of the terminal, profiler (Activity Monitor/Instruments), and benchmark outputs.
