---
category: ai-engineering
date: 2026-04-13
description: 'PGlite vs SQLite-vec for vector search in the browser: how the two engines differ, and what to measure on your own data before you pick one.'
status: published
work_note: '[Ninad Pathak](/portfolio/)''s developer content for browser tools covers
  the initial download as well as the first query, helping readers evaluate startup
  costs before adopting a database.'
title: 'PGlite vs SQLite-vec: Vector Search in the Browser'
updated: '2026-08-17'
slug: browser-vector-search
---

[PGlite](https://pglite.dev/docs/) runs Postgres in the browser through WebAssembly, and its separately packaged [pgvector extension](https://pglite.dev/extensions/) adds vector columns and indexes. [SQLite-vec](https://github.com/asg017/sqlite-vec) is a pre-v1 SQLite extension that stores full-precision and quantized vectors in `vec0` tables, and it runs in the browser through WebAssembly too.

**Short answer:** Choose PGlite when you need Postgres features next to your vectors. Choose SQLite-vec when a SQLite runtime fits, and time both on your own vectors in your target browser, because this article doesn't measure which is faster.

## The architectural shift to the browser

Local-first software requires moving the database to the user's device. For years, that meant trading away the advanced retrieval capabilities of backend systems like pgvector or Pinecone.

The arrival of high-performance WebAssembly (WASM) builds for PGlite and SQLite-vec has erased that trade-off.

Local retrieval can remove a network round trip from an interactive search path.

Moving retrieval into the browser removes the first half of that latency chain entirely, and the box starts keeping up with the typist.

<div class="visual-wrapper">
  <div class="visual-title">Local-first WASM lifecycle: the loading sequence</div>
  <div class="visual-container">
    <iframe src="/static/visuals/wasm-vdb-sequence.html" title="WASM VDB Sequence" loading="lazy"></iframe>
  </div>
</div>

Implementing vector search in WASM means juggling three distinct environments: the main thread, the Web Worker, and the WASM memory heap. PGlite runs a full Postgres instance inside that heap.

SQLite-vec acts as a highly optimized C extension bolted onto the SQLite engine, closer to a single sharp tool than a whole workshop.

## What a reproducible comparison should measure

No benchmark artifact accompanies this article, so it does not report measured results. A reproducible comparison should report bundle size, index-build time, query latency distributions, memory use, and recall.


SQLite-vec loads as an extension, while PGlite starts a Postgres runtime inside the WebAssembly sandbox. That architectural difference affects startup work and feature coverage.

## PGlite and the power of HNSW

PGlite brings the industry-standard `pgvector` implementation to the edge. Its primary advantage is the **HNSW (Hierarchical Navigable Small World)** index.

[HNSW](/glossary/hierarchical-navigable-small-world-hnsw/) is a graph-based index for approximate nearest-neighbor search, using graph navigation instead of comparing the query with every stored vector.

<div class="visual-wrapper">
  <div class="visual-title">Search complexity: flat vs indexing</div>
  <div class="visual-container">
    <iframe src="/static/visuals/wasm-vdb-indexing.html" title="WASM VDB Complexity" loading="lazy"></iframe>
  </div>
</div>


The graph works like the express layers of a subway map: instead of stopping at every station, a query hops along sparse long-distance edges first, then drops down to local stops only near the answer.


## SQLite-vec and the speed of quantization

In its stable release, v0.1.9 from 2026-03-31, SQLite-vec answers a KNN query with what [its docs](https://github.com/asg017/sqlite-vec/blob/main/site/features/knn.md) call a brute-force scan, and it speeds that scan up with vector quantization. The [v0.1.10 alpha releases](https://github.com/asg017/sqlite-vec/releases) add ANN indexes, rescore and DiskANN, with IVF marked experimental and not enabled, so an indexed SQLite-vec is still pre-release.

Quantization shaves the precision off each dimension to save memory and speed up the arithmetic.

<div class="visual-wrapper">
  <div class="visual-title">Binary quantization: mapping and reduction</div>
  <div class="visual-container">
    <iframe src="/static/visuals/wasm-vdb-binary.html" title="WASM VDB Binary Quantization" loading="lazy"></iframe>
  </div>
</div>

Binary quantization is the most aggressive form of this optimization. Each 32-bit floating point dimension collapses to a single bit based on whether the value is positive or negative, like throwing away the exact GPS coordinates and keeping only which side of the street something sits on.

That collapse buys a 32x reduction in memory footprint and lets the CPU swap expensive floating-point dot products for XOR-based Hamming distance, which counts mismatched bits in a single cheap instruction.

## The precision tax: accuracy vs speed

Nothing in AI engineering comes free. Quantization buys speed and pays for it with a recall penalty, so the results drift slightly away from the true nearest neighbors.

A query that should surface the two most relevant support docs might return one of them plus a near miss.


## Dimensionality and the scaling wall

As vector dimensionality climbs, each vector comparison costs more on both engines. Standard open-source models like `all-MiniLM` use 384 dimensions.

OpenAI's [`text-embedding-3-large`](https://developers.openai.com/api/docs/models/text-embedding-3-large) uses 3072 dimensions by default, a jump rooted in [how embedding models trade dimensionality for information density](/articles/vector-embeddings/).

A flat scan does proportionally more arithmetic as vector dimension grows. Benchmark the crossover against the target browser, vector count, and recall requirement.

HNSW can compare fewer candidate vectors, but wider vectors still make each comparison cost more. [pgvector's HNSW index](https://github.com/pgvector/pgvector#hnsw) takes `vector` columns up to 2,000 dimensions and `halfvec` up to 4,000, so for 3072 dimensions I'd use a half-precision index or reduce the dimensions, then measure latency and recall.

## Memory constraints in the WASM heap

Browser and WebAssembly memory limits constrain how large an in-memory vector index can grow, and those limits vary by runtime.

HNSW indexes store graph edges on top of the vectors, so a flat quantized table can use less memory. Measure heap use in the target browser instead of assuming a universal footprint.

## Economic outcomes of edge retrieval

Moving retrieval to the client can reduce per-query backend compute, but it shifts compute and memory cost to the user's device.

Your retrieval compute budget quietly migrates off the AWS bill and onto the user's electricity bill.

## Choosing the right architecture

Picking between these two engines comes down to your application's data model and scale.

<div class="visual-wrapper">
  <div class="visual-title">Architectural decision matrix</div>
  <div class="visual-container">
    <iframe src="/static/visuals/wasm-vdb-comparison.html" title="WASM VDB Summary" loading="lazy"></iframe>
  </div>
</div>

PGlite is the correct choice for applications that need a real relational database. If your search results must be joined with complex metadata, filtered via JSONB, or [combined with BM25 full-text search in a hybrid retrieval setup](/articles/hybrid-search/), or synced with a backend Postgres instance, the PGlite bundle size is a small price to pay.

A local documentation assistant with a bounded corpus can fit SQLite-vec's simpler deployment model.

## The future of edge retrieval

As models become practical on more local hardware, retrieval can move into the same client-side application.

Shipping either PGlite or SQLite-vec pulls the biggest friction point out of the user's loop. Seasoned practitioners already know the fastest request is the one that never leaves the machine.

Local-first vector databases have graduated from a nice optimization to the new baseline for responsive, private, and scalable AI software.

## FAQ

**Can I run PGlite and SQLite-vec in the same application?** Yes, nothing stops one page from loading both. One design runs SQLite-vec for a fast, low-precision "first pass" search, then hands the candidates to PGlite for a high-precision "refinement" pass.

A two-stage design can show approximate candidates first and rerank them with a higher-precision index before settling the result set.


**Do these databases work in mobile browsers?** Both projects document a browser build through WebAssembly, and neither project's docs that I checked list tested mobile browsers. Test on the iOS Safari and Android Chrome versions you support, and measure heap use there, because this article has no mobile measurements.

**What is the "lost in the middle" problem for local RAG?** That one is a [context window limitation rather than a database limitation](/articles/llm-context-windows/). Even with flawless retrieval, packing too much context into a small local model degrades its reasoning, since the relevant passage gets buried among the filler.

Choose top-K from retrieval and answer-quality evals for the local model rather than copying a cloud pipeline's setting.
