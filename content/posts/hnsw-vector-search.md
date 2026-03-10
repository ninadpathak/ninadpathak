---
title: "HNSW: What's Actually Happening When You Do a Vector Search"
date: 2026-03-05
description: "Vector database users often treat HNSW as a black box. Here's the actual algorithm, the tradeoffs, and when you should care."
tags: [ai, vector-search, hnsw, infrastructure]
status: published
---

Treating vector search as a black box works fine, until it doesn't. You add embeddings to a vector DB, call a search function, get back results. Then at some point you need to tune recall, or you're running out of memory, or your queries are slow, and suddenly you're staring at parameters called `M`, `ef_construction`, and `efSearch` with no mental model for what they do.

Reading the [original HNSW paper](https://arxiv.org/abs/1603.09320) is actually worth your time. You won't implement it yourself. The algorithm's structure explains every tradeoff you'll encounter in production, and that's the useful part.

Here's what's happening.

## The problem HNSW is solving

Finding the nearest neighbor to a query vector in a dataset of a million 1536-dimensional floats is slow done naively. Brute force computes cosine similarity against every vector, returns the top k, and scales linearly with dataset size. At 10 million vectors, that's slow. At 100 million, it's unusable for anything interactive.

The standard computer science move is to trade exactness for speed. You find the *approximate* nearest neighbors. HNSW (Hierarchical Navigable Small World graphs) is the dominant approach right now across Qdrant, Weaviate, Chroma, FAISS, and other vector databases. The paper, by Malkov and Yashunin, was submitted to arXiv in 2016 and published in IEEE TPAMI in 2018. It won out over the competition because it achieves very high recall at very low latency, in a structure that's easy to reason about once you understand the layers.

## The layers

HNSW builds a multi-layer graph. At the bottom layer (layer 0), every vector in your dataset is a node. Each node has bidirectional connections to its M nearest neighbors. M is the single most important parameter you'll tune: it controls graph density, search recall, memory usage, and build time simultaneously.

At higher layers, only some nodes appear, with exponentially decreasing probability. The formula is roughly `exp(-level / mL)` where mL is derived from M. With M=32, you get about 97% of nodes at layer 0, about 3% at layer 1, about 0.09% at layer 2, and so on. It thins out fast.

The structure is intentionally similar to a skip list. The top layers let you take big jumps across the space; the bottom layer is where you do precise local search.

## How search works

You enter the graph at the top layer, at a pre-designated entry point. You greedily traverse: at each step, you move to whichever connected neighbor is nearest to your query. When no neighbor is closer than your current position, you've hit a local minimum on that layer. Drop to the next layer. Repeat.

Here's where I lose some people, so let me be direct about it: the greedy traversal on the top layers isn't finding the answer. It's finding a *starting point* for the detailed search at layer 0. The top layers are navigation; layer 0 is where the actual nearest neighbor candidates get identified.

At layer 0, you run the search with a larger candidate pool controlled by the `ef` (or `efSearch`) parameter. Higher ef means you explore more candidates before returning results. More exploration, better recall. More computation, higher latency. The tradeoff is direct and predictable, which is one reason people like HNSW.

On the SIFT1M benchmark, you can get roughly 80% recall at sub-millisecond query times, or ~100% recall at around 50ms. That's a 50x latency difference across the recall range. Where you land depends entirely on ef.

## The M parameter is doing more than you think

M controls the number of bidirectional connections per node. The memory cost of HNSW is dominated by M. The formula: for each vector, you pay the cost of the raw float data plus M × 4 bytes per connection.

For 1 million OpenAI text-embedding-3-small vectors (1536 dimensions, float32): that's ~6.1 GB of raw vector data. With M=32, add another ~128 MB for connection overhead. Fine. At 100 million vectors, the memory requirements become the constraint, not query performance.

During index construction, you use `ef_construction` to control how carefully neighbors are selected at build time. Higher ef_construction = better graph quality = slower build. One-time cost, but significant for large datasets. Weaviate defaults to efConstruction=100; Qdrant's "accurate" config uses ef_construct=100 with m=32. The gap between fast and accurate configurations isn't small on billion-scale data.

## The thing everyone learns the hard way about filtering

Standard HNSW has no native support for filtered search. Take a query like "find me the 10 most similar vectors where metadata.user_id = 42". Two options exist: pre-filter (reduce the dataset before searching) or post-filter (search the full index, then filter results).

Both are wrong in different ways. Pre-filtering can make the graph disconnected or too small to traverse efficiently. Post-filtering means you might ask for k=10 results and get back 3, because 7 of the top 10 got filtered out, and you have no visibility into whether better matches exist further down the list.

Qdrant solved this with a custom query planner that decides which approach to use based on cardinality estimates. It's one of the reasons Qdrant gets recommended specifically for filtered search workloads. The others either have the same problem or have built partial workarounds. For teams where filtered search is a core requirement, this matters.

## Why HNSW must live in RAM

The graph traversal is random-access by nature. Each step in the greedy search jumps to a neighbor, which could be anywhere in the vector space. On spinning disks, random I/O is fatal. On SSDs, it's still slow enough to destroy performance.

That's HNSW's fundamental scaling ceiling. You can hold roughly 100-500 million vectors in RAM depending on dimensionality and M, but beyond that you're either compromising recall or switching algorithms.

[DiskANN](https://www.microsoft.com/en-us/research/publication/diskann-fast-accurate-billion-point-nearest-neighbor-search-on-a-single-node/), out of Microsoft Research (NeurIPS 2019), solves this with a different graph structure (Vamana) designed for SSD access patterns. It indexed 1 billion vectors on a single workstation with 64GB RAM, hitting 5000+ QPS at 95%+ recall and under 3ms mean latency. Pinecone's serverless architecture uses something similar: vectors live in object storage (S3/GCS), organized into immutable files called "slabs", with caching layers to manage the latency.

Well below a billion vectors, none of this matters today. The architectural assumption that your index fits in RAM is still worth being aware of.

## For very high-dimensional embeddings, the hierarchy might not help

A 2024 paper found that for dimensions >= 96, a flat navigable small world graph (no layers, just layer 0) matches HNSW latency and recall while using 38% less memory. The intuition: at high dimensions, the layers don't help navigation as much, because the geometry of high-dimensional spaces makes "big jumps" less effective. You're not getting the skip-list benefit you pay for with extra memory.

Theoretical for most use cases right now, but worth watching. Modern embedding models produce 768, 1536, or higher-dimensional vectors. The hierarchy that makes HNSW work might matter less at the dimensions we're actually using.

## Google's ScaNN takes a different approach

[ScaNN](https://arxiv.org/abs/1908.10396) (ICML 2020) doesn't use HNSW at all. It uses anisotropic vector quantization: quantizing vectors in a way that penalizes errors in the direction parallel to the query more than errors in orthogonal directions. The idea is that parallel errors affect the dot product more than orthogonal ones, so your quantization should be query-aware.

Google claimed 2x performance over other libraries on ann-benchmarks.com at the time. The [ann-benchmarks site](http://ann-benchmarks.com/) is the canonical reference: automated benchmarks on glove-100, sift-128, nytimes-256 and others, with recall vs. queries-per-second plots for 38 algorithms. When evaluating which index to use for a specific dataset and dimensionality, that's where to start.

## The parameters you'll actually tune

Here's what the research says matters:

**M:** Set higher for better recall, lower for lower memory and faster builds. Weaviate and Qdrant both default to M=16 or M=32. For most use cases, M=16 is fine. M=32 when recall is critical and you have the memory.

**ef_construction:** A build-time investment. Higher ef_construction affects only graph quality, leaving memory and query time unchanged. Teams indexing infrequently and querying constantly should set this high (200+). Qdrant's accurate config uses 100; doubling that won't break anything but will slow your index build.

**efSearch (or ef at query time):** The dial you turn when you need more recall without rebuilding the index. Start low, measure recall against a held-out dataset, increase until you hit your recall target. The latency cost is linear with ef. When recall is already fine, leave it alone.

**Quantization:** Under memory pressure, INT8 scalar quantization (4x compression, modest accuracy loss) or binary quantization (32x compression, ~74% raw recall) are worth evaluating. With oversampling on binary quantization, you can recover most of the recall loss. Weaviate's [binary quantization docs](https://weaviate.io/blog/binary-quantization) have the actual numbers.

---

HNSW is an approximate algorithm, every parameter is a tradeoff surface, and the tradeoffs are predictable once you understand the structure. M controls memory and density. ef controls query-time recall and speed. ef_construction controls build-time graph quality. The rest is implementation details.

Performance issues with a vector DB almost always resolve at the parameter level before requiring architecture changes.
