---
title: "pgvector vs Dedicated Vector Databases: An Honest Comparison"
date: 2026-03-11
description: "pgvector is genuinely good. Dedicated vector databases exist for real reasons. Here's how to think through the tradeoff without the vendor hype."
tags: [ai, vector-search, pgvector, infrastructure, rag]
status: published
---

There's a recurring debate in AI infrastructure circles that generates more heat than light. On one side: "just use pgvector, you already have Postgres." On the other: "pgvector doesn't scale, use a real vector database." Both sides are mostly arguing past each other, and neither is right as a general principle.

The honest answer depends on what you're building, at what scale, with what query patterns. Here's an attempt at a grounded comparison.

## What pgvector actually is

[pgvector](https://github.com/pgvector/pgvector) is a Postgres extension, first released in 2021, that adds a vector data type and approximate nearest neighbor search to Postgres. You store embeddings as `vector(1536)` columns alongside your regular relational data. You create an index using either IVFFlat (inverted file flat) or HNSW (since pgvector 0.5.0). You query with `<->` for L2 distance, `<=>` for cosine, `<#>` for inner product.

The HNSW implementation in pgvector uses the same basic algorithm as dedicated databases -- hierarchical navigable small world graphs, the same parameters (m, ef_construction, ef at query time). The core algorithm isn't the differentiator.

What pgvector gives you is the rest of Postgres for free. Your vectors live in the same database as your relational data. You can do `JOIN` between vector search results and your users table. You get Postgres's ACID transactions, full-text search, JSONB columns, row-level security, and everything else in a single system. Backups, replication, point-in-time recovery -- the entire Postgres ecosystem applies.

## Why dedicated vector databases exist

The "just use pgvector" argument is compelling for small to medium deployments. Dedicated vector databases didn't emerge because pgvector is wrong in principle. They emerged because at large scale, vector search has specific performance and operational requirements that don't fit naturally into a general-purpose RDBMS.

**Memory architecture.** HNSW must live in RAM for performance -- the random-access traversal pattern is fatal on any storage medium with seek latency. Postgres manages memory via its shared buffer pool, which also needs to cache table data, index pages for other operations, and work through the OS page cache. A dedicated vector database can dedicate its entire memory footprint to the index. At 50 million vectors, the difference matters.

**Filtered search.** Filtered vector search -- "find me the 10 most similar vectors where `user_id = 42` and `status = active`" -- is genuinely hard. pgvector 0.7.0 introduced iterative index scans that help considerably, but the problem isn't fully solved at high filter selectivity. Qdrant built a custom query planner that estimates filter cardinality and decides whether to pre-filter (reduce the dataset before searching) or post-filter (search then filter). Weaviate has a similar approach with its filtered HNSW traversal. These are purpose-built solutions to a problem that Postgres wasn't designed around.

**Quantization and compression.** At scale, storing full-precision float32 vectors is expensive. INT8 scalar quantization reduces memory to 25%; binary quantization reduces it to 3% at the cost of some recall (recoverable with oversampling). Qdrant and Weaviate both have first-class quantization support. pgvector got half-precision (float16) storage in 0.7.0, which helps, but doesn't match the quantization options available in dedicated databases.

**Distributed deployment.** Postgres can be sharded horizontally, but it requires significant operational work. Purpose-built distributed vector search (Pinecone's pods, Qdrant's cluster mode, Weaviate's node sharding) is designed from the start to distribute across nodes. For datasets that don't fit on a single machine's RAM, the distributed options in dedicated databases are more mature.

## The numbers you should actually look at

Generic claims about "pgvector doesn't scale" or "pgvector is fast enough" don't tell you anything useful. The relevant questions are specific:

**At what vector count does pgvector start degrading?** For an in-memory HNSW index, pgvector performs comparably to dedicated databases up to roughly 1-5 million vectors, assuming you've tuned m and ef_construction appropriately. Above that, dedicated databases start showing advantages in query latency, particularly under concurrent load.

**What's the recall at your efSearch setting?** pgvector's HNSW implementation achieves comparable recall to Qdrant and Weaviate at equivalent efSearch values on standard benchmarks (ANN Benchmarks, the canonical evaluation source). The algorithm is the algorithm.

**What's your p99 latency under production load?** Benchmarks in isolation don't capture shared buffer pool contention, Postgres vacuum overhead, or checkpoint interference. If your database is handling a mix of OLTP and vector workloads, the vector queries compete for resources with everything else.

**What are your filter selectivity patterns?** Low selectivity filters (eliminating 1-5% of the dataset) are handled fine by pgvector's post-filter approach. High selectivity filters (returning 0.1% of the dataset) are where the dedicated query planners in Qdrant or Weaviate start pulling ahead.

## The case for pgvector

Fewer systems is a genuine advantage. Each additional database in your infrastructure is an operational liability: another thing to monitor, back up, secure, upgrade, and learn. The cognitive overhead of multi-database architecture compounds.

For applications under a few million vectors, pgvector with HNSW indexed correctly (m=16 or m=32, ef_construction=100+, efSearch tuned to your recall target) delivers performance that's good enough for the large majority of use cases. The marginal recall or latency improvement from switching to a dedicated database often doesn't justify the operational overhead and migration cost.

There's also the data locality argument. When your vectors live next to your metadata in Postgres, queries like "retrieve the 10 most semantically similar items to this one, ordered by creation date, filtered by subscription tier" are a single query. With a separate vector database, you do a vector search, get back IDs, then query Postgres for the metadata, then filter and sort in application code. That's three round trips and more application complexity.

[Supabase Vector](https://supabase.com/vector) and [Neon](https://neon.tech/) have made pgvector operationally simpler by hosting it as a managed service with sensible defaults. If you're already on managed Postgres and under ~5 million vectors, starting with pgvector and migrating if needed is a reasonable strategy.

## The case for dedicated databases

At scale -- 10 million+ vectors, high query volume, strict p95 latency requirements -- dedicated databases have real advantages that aren't just marketing.

Qdrant, written in Rust, has consistently strong benchmark numbers. The filtered search implementation is purpose-built. Memory-mapped storage lets it handle datasets larger than RAM with reasonable performance (slower than in-memory, but more graceful degradation than pgvector under memory pressure). The payload indexing system lets you filter on metadata without a separate database call.

Weaviate makes a different set of tradeoffs: HNSW filtered traversal, a GraphQL and gRPC API, module-based integration for generating embeddings. Better for teams that want a more opinionated system; more operational complexity for teams that want control.

Pinecone is the managed option for teams that don't want to run infrastructure. You pay a significant premium over self-hosted alternatives for serverless scaling and operational simplicity. The proprietary architecture means less visibility into what's happening under the hood.

[DiskANN-based](https://www.microsoft.com/en-us/research/publication/diskann-fast-accurate-billion-point-nearest-neighbor-search-on-a-single-node/) systems (used in Pinecone's serverless backend, among others) make sense at billion-vector scale by using SSDs instead of RAM as primary storage. The random-access problem with HNSW on disk is addressed with a graph layout optimized for SSD access patterns. For datasets that don't fit in RAM, this matters.

## A decision framework that's actually useful

Start with pgvector if:

- Your vector count is under 5 million
- Filtered search selectivity is low-to-moderate
- You're already on Postgres
- Your team's operational capacity is limited
- You need transactional consistency between vector and relational data

Consider a dedicated database if:

- You're approaching 10 million+ vectors
- High selectivity filtered search is a core requirement (returning <1% of the dataset)
- You have strict p95 latency requirements (under 10ms) under production load
- You need distributed deployment across nodes
- Your team can absorb the operational overhead of an additional system

A third path: avoid the debate entirely by starting with pgvector and setting up your application so the vector database interface is abstracted. When you need to migrate -- if the benchmarks tell you to -- you do it at the adapter layer without rewriting application code. This is how the teams that have done this successfully usually approach it.

## What the benchmarks say (and don't say)

The [ANN Benchmarks](http://ann-benchmarks.com/) site publishes recall vs. queries-per-second plots for dozens of algorithms and datasets. At equivalent recall targets, the gaps between pgvector's HNSW and dedicated database HNSW implementations are often small. The algorithm is the algorithm.

Where dedicated databases pull ahead is in concurrent load, filtered search, and memory-constrained environments. Those conditions don't show up in single-client benchmarks.

The benchmark that matters is the one you run on your data, with your query patterns, under your production load profile. That benchmark is harder to set up than running ANN Benchmarks, but it's the only one that tells you something actionable about your specific situation.

---

The framing of "pgvector vs. vector databases" implies a binary choice that doesn't reflect how good teams actually make infrastructure decisions. The real question is: what's the minimum system that reliably handles your current requirements, with a migration path if requirements change?

For most teams at most stages, that system starts with pgvector.
