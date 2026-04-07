# Content Brief: 100ms vector search in the browser — PGLite vs. SQLite-vec

**Topic**: Comparative performance benchmark of WASM-based vector databases
**Primary Keyword**: local WASM vector database benchmarks
**LSI Keywords**: PGLite vs SQLite-vec, browser vector search latency, pgvector WASM, sqlite-vec quantization, local-first RAG architecture, edge vector search.
**Target Audience**: AI Engineers, Local-First Developers, CTOs.
**Content Type**: Quantitative Comparison / Benchmarking.
**Word Count Target**: 3000+ words.

---

## Direct Answer for the Introduction
Sub-100ms vector search in the browser has moved from a research novelty to a production requirement for local-first AI applications. In my 2026 benchmark of 100,000 vectors, PGLite (pgvector) and SQLite-vec emerged as the dominant contenders with a clear architectural split: PGLite offers the full power of HNSW indexing and Postgres relational parity at the cost of a 3MB bundle, while SQLite-vec provides a lean 800KB footprint and superior quantized brute-force speed. For high-dimension vectors (3072+), PGLite's HNSW implementation is mandatory, but for standard 384-dimension models, SQLite-vec's binary quantization achieves <5ms latency, effectively turning the browser into a high-performance retrieval engine.

---

## The Benchmark Setup (Hardware: M2 Air 16GB)

### Dataset
- 100,000 vectors (Synthetic dataset)
- Dimensions: 384 (all-MiniLM-L6-v2) and 3072 (text-embedding-3-large)
- Data format: Float32 and Int8 (for quantization tests)

### Test Scenarios
1. **Load Time**: Bundle size + DB initialization time.
2. **Brute Force (Flat) Latency**: p50 and p99 query speed.
3. **Index-Based Latency**: HNSW (PGLite) vs. Quantized Scans (SQLite-vec).
4. **Memory Footprint**: Heap usage during concurrent searches.

---

## Planned Visuals (12+ assets)
1. **SVG Chart: p99 Latency vs Vector Count** (10k to 100k).
2. **SVG Table: 2026 Comparison Matrix** (Bundle Size, Features, Memory).
3. **3D Visual: HNSW Graph (PGLite)** vs **Quantized Flat List (SQLite-vec)**.
4. **2D Graph: Memory Pressure during Index Build**.
5. **SVG Sequence Diagram: Vector Search in a Web Worker**.
6. **Screenshot: Activity Monitor showing VRAM usage during search**.
7. **2D Chart: Latency vs. Dimensions** (384 vs 768 vs 1536 vs 3072).
8. **Screenshot: Chrome DevTools Profiler (Flame graph of a query)**.
9. **SVG Graphic: How Binary Quantization works**.
10. **Screenshot: Terminal output of the benchmark script**.
11. **2D Graph: Accuracy Loss vs. Quantization Level**.
12. **SVG Table: ROI of Edge RAG vs Cloud RAG (Latency/Cost)**.

---

## Strict Writing Constraints
- **Title Case Titles / sentence case headings.**
- **NO Emdashes (—)**. Use commas or periods.
- **NO Semicolons (;)**.
- **No Contrastive Parallelism**: Avoid "not X but Y."
- **Tone**: Cynical, practitioner-first, Hacker News style.
- **Hardware Proof**: Link to the WASM benchmark script used.
