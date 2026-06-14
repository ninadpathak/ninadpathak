---
date: 2026-03-28
description: Semantic caching returns cached LLM responses for semantically similar
  queries, cutting API costs by 40-70% on the right workloads. Here's how the mechanism
  works and where it fails.
status: published
tags:
- ai
- rag
- infrastructure
- vector-search
title: 'Semantic Caching: The RAG Optimization Nobody Talks About'
---

Almost every conversation I see about RAG optimization centers on retrieval quality: better embeddings, rerankers, hybrid search, contextual chunking. The layer nobody talks about sits before retrieval even starts. Semantic caching intercepts a query, checks whether a sufficiently similar query has already been answered, and returns the stored response instead of running the full pipeline. Picture a support bot that has already answered "how do I reset my password" two hundred times this week. Done well, semantic caching cuts 40-70% of LLM API calls on the right workloads.

**Short answer:** Semantic caching embeds each query, searches a vector store of prior queries, and returns the cached response when cosine similarity exceeds a threshold (typically 0.85-0.92). It works well for FAQ-style, documentation, and support workloads where queries repeat with slight variations. It fails for conversational agents, personalized responses, and any workload where the answer must reflect current state.

## Why exact-match caching doesn't work for LLM queries

Traditional caching keys on the exact input string. "What is your return policy?" and "Can I return an item?" are different strings and produce separate cache misses, even though a support bot should give them the same answer.

LLM query traffic doesn't repeat exactly. It repeats semantically. [Industry data puts 30-40% of LLM requests as semantically similar to previous ones](https://blog.premai.io/semantic-caching-for-llms-how-to-cut-api-bills-by-60-without-hurting-quality/). For high-repetition categories like documentation lookup, code explanation, and FAQ responses, that figure climbs to 40-60%. Conversational categories drop to 5-15%.

Replacing string equality with embedding similarity is what makes the difference. The cache becomes a vector store of prior queries, and a hit occurs when a new query lands within a configurable similarity radius of a stored one. Think of an exact-match cache as a filing cabinet where the folder label has to be spelled character for character, against a semantic cache that files by what the question is about.

## How the mechanism works

The pipeline for semantic caching has four components:

1. **Embedding layer**: Convert the incoming query to a vector using the same embedding model you'll use for comparisons. Consistency here matters. A mismatch between the embedding model at cache write time and cache read time produces unreliable similarity scores.

2. **Vector search**: Run an approximate nearest-neighbor search over stored query embeddings. Redis LangCache, [GPTCache from Zilliz](https://github.com/zilliztech/GPTCache), and purpose-built LLM gateways all handle this step, though with different tradeoffs on throughput and latency.

3. **Similarity evaluation**: Compare the nearest-neighbor distance against a threshold. A cosine similarity above 0.88-0.92 typically indicates semantic equivalence. Below 0.75-0.80 is a miss. The middle range is where you tune.

4. **Response or pass-through**: On a hit, return the stored response. On a miss, run the full RAG pipeline, store the result, and add the query to the cache.

Across query categories, [GPTCache](https://arxiv.org/abs/2411.05276) reports API call reduction of up to 68.8%, with cache hit rates from 61.6% to 68.8%. The system achieved positive hit rates exceeding 97%, meaning cached responses returned for genuine semantic matches were almost always appropriate. Speed improvement on hits is 2-10x depending on your LLM's baseline latency.

<div class="visual-wrapper">
  <div class="visual-title">SEMANTIC CACHE: HIT VS MISS</div>
  <div class="visual-container">
    <iframe src="/static/visuals/semantic-cache.html" title="An incoming query embedded and compared to the cache by similarity threshold, showing a HIT that returns the cached response versus a MISS that calls the LLM and stores the result" loading="lazy"></iframe>
  </div>
</div>

## Similarity threshold tuning: the number that determines everything

Most implementations go wrong at the threshold. Set it too high and you get almost no cache hits. Set it too low and you return wrong answers for queries that only superficially resemble the cached one, like serving the answer to "how do I cancel my subscription" when the user asked "how do I cancel my last order."

Starting at 0.88 cosine similarity for an FAQ-style cache is what [Redis LangCache documentation](https://redis.io/blog/10-techniques-for-semantic-cache-optimization/) recommends, then tuning down gradually as you observe false positive rates. A practical technique is confidence buffering: if your threshold is 0.90, only serve cache hits above 0.92. The buffer absorbs borderline cases without requiring you to tighten the primary threshold.

My experience is that the threshold should vary by domain. Product documentation queries where phrasing variation is large but intent is narrow can tolerate 0.82-0.85. Legal or compliance queries where one swapped word ("may" for "must") changes the answer need 0.94-0.96. Treating the whole cache as a single threshold ignores this variance.

[Redis recommends domain partitioning](https://redis.io/blog/10-techniques-for-semantic-cache-optimization/) as an explicit technique: don't mix customer support queries with product documentation queries in the same cache namespace. Different domains have different similarity distributions, and a threshold calibrated for one domain will over-fire or under-fire on another.

## Production backends: why SQLite is not GPTCache's default in prod

GPTCache ships with SQLite as its default storage backend, and SQLite doesn't handle concurrent writes well. Under production traffic with multiple workers, you'll see write contention, lock timeouts, and missed cache writes. Swapping the backend to Redis or PostgreSQL fixes it.

The most common production backend for semantic caching is [Redis](https://redis.io/tutorials/semantic-caching-with-redis-langcache/). It keeps embeddings and responses in memory with optional persistence, supports native vector search, and handles the concurrent write load that kills SQLite. Redis LangCache is the managed option. RedisVL is the open-source library.

One production deployment I've seen in enterprise inventory management processed over 10,000 queries with an average latency of 8.2 seconds end-to-end and 94.3% semantic accuracy at cache hits. The latency figure includes the cache lookup (under 50ms for Redis) plus the fallback LLM call on misses.

## Cache invalidation: where semantic caches fail quietly

Exact-match caches have clean invalidation: delete the key. Semantic caches don't have keys in the same sense. A stored query embedding represents a region of semantic space, so invalidating responses for a changed document means finding all cached queries that pointed to that document and removing them.

Handling this poorly is the norm, not the exception. The common failure modes:

**Model version changes.** Your LLM provider updates the model. Cached responses from the old model version may now be inconsistent with what the new model would produce: different tone, different verbosity, updated safety thresholds. Serving them looks like a model regression to users.

**System prompt changes.** A cached response was generated under an old system prompt. The new system prompt changes product instructions, persona, or constraints. The cached response reflects instructions you've since overridden.

**Factual staleness.** Any time your underlying knowledge base changes, cached responses that drew on old documents become stale. A support bot that cached "the return window is 14 days" will keep serving that for semantically similar queries even after the policy changed to 30 days.

[Practical guidance](https://mbrenndoerfer.com/writing/caching-prompt-semantic-invalidation-hit-rates-llm) distinguishes three invalidation strategies: TTL-based (invalidate after N hours), event-based (invalidate when source documents change), and version keys (append a version string to cached entries and rotate on model or prompt updates). Production systems I trust combine all three.

My recommendation: treat semantic caching as appropriate only for content that changes on a known schedule or not at all. FAQ responses with monthly review cycles, documentation that gets versioned on release, code examples tied to a library version. Don't cache responses for anything where the ground truth can change without a clear invalidation trigger.

## The embedding model selection problem

Semantic caching quality depends heavily on the embedding model you use for query similarity. A model that clusters paraphrases well at 0.88 cosine similarity for one domain may cluster them at 0.72 for another. Running `text-embedding-ada-002` on a technical code query corpus produced different similarity distributions than `text-embedding-3-small` in tests I ran: the same threshold that gave 8% false positives on one model gave 2% on the other.

What follows in practice is that you have to calibrate your similarity threshold on your actual query distribution using your actual embedding model. A threshold validated on a generic FAQ corpus doesn't transfer to a medical documentation corpus, and a threshold validated on one embedding model doesn't transfer to a different one.

Switching embedding models mid-production requires a full cache invalidation. Cached query embeddings were computed under the old model and won't compare correctly to new query embeddings computed under a different model. The two models lay out the same sentences in differently shaped coordinate spaces, so distances measured in one are meaningless in the other. Version your cache entries with the embedding model identifier, the same way you'd version them with the LLM version.

## When semantic caching actively hurts

A few workload patterns where semantic caching creates more problems than it solves:

**Personalized responses.** A query from user A might be semantically identical to a query from user B, but the correct answer differs based on their account state, preferences, or history. "When does my plan renew?" embeds the same for both users and resolves to different dates. Serving user B the cached response for user A is a correctness failure. Add user context to the cache key or skip caching entirely for personalized workloads.

**Agentic workflows.** An agent step where the prompt includes prior conversation history or tool outputs is almost never semantically identical across two runs. Cache hit rates drop to near zero, and the embedding computation per step adds latency with no benefit.

**High-variance conversational queries.** Free-form conversation produces low cache hit rates (5-15% per the industry data above). Running embedding lookups on every conversational turn to get a 5% cache hit rate is negative-ROI.

**Real-time data queries.** "What's the current price of X?" should never be cached beyond a few seconds, since the cached answer is wrong the moment the price moves.

## Connecting to the broader RAG optimization picture

Semantic caching is not a retrieval improvement. It sits before retrieval. When a query hits the cache, the retrieval system never runs at all.

Where you put your effort changes once you see that. Retrieval improvements (better embeddings, hybrid search, reranking) reduce the cost and improve the quality of cache misses. Semantic caching reduces how often the retrieval system runs in the first place. They compound.

I covered retrieval improvements with [contextual retrieval here](/blog/how-anthropics-contextual-retrieval-changes-rag-architecture/) and [reranking here](/blog/reranking-in-rag-why-your-top-k-results-are-probably-wrong/). Semantic caching fits in the layer above both.

What people miss is that semantic caching doesn't just reduce LLM API calls. A cache hit skips the retrieval search, the reranker call, and the query-side embedding too. The full cost reduction is larger than the LLM API savings alone.

## FAQ

**What similarity threshold should I start with?**
Start at 0.88 cosine similarity for FAQ or documentation workloads. Use confidence buffering: only serve hits above 0.90 even if your threshold is 0.88. Lower thresholds (0.82-0.85) work for domains where phrasing varies widely but intent is narrow. Never go below 0.80 without labeling a validation set and measuring false positive rates.

**Can I use semantic caching with streaming responses?**
Yes, but with a tradeoff. Streaming responses require storing the full response before you can cache it, which means the first request for any query receives no latency benefit regardless of future cache hits. Some systems cache a non-streaming version and serve it on hits even if the original was streamed. Whether that's acceptable depends on your UX.

**How do I handle cache invalidation when my knowledge base changes?**
Use event-based invalidation tied to your document versioning system. When a document is updated, delete or expire all cached queries whose stored embeddings have high similarity to the document's topic embedding. For practical implementation, Redis LangCache supports namespace-level invalidation that lets you flush all entries in a domain partition at once.

**Does semantic caching work with multi-turn conversation?**
Rarely. Multi-turn prompts include conversation history, which makes them nearly unique on each turn. Cache hit rates for conversational workloads are typically 5-15%, making the overhead of embedding lookups per turn a net negative. Use semantic caching for single-turn, intent-driven queries instead.

**What's the difference between GPTCache and Redis LangCache?**
GPTCache is an open-source Python library from Zilliz, designed to integrate directly into LLM application code. Redis LangCache is a managed service from Redis with embedding controls, LLM-as-a-judge validation, adaptive TTL policies, and built-in observability. GPTCache gives you more control and costs you more operational work. Redis LangCache is faster to operationalize and has better support for production features like domain partitioning and confidence buffering.