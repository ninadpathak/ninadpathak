---
title: "Hybrid Search: Combining BM25 and Vector Search for Better Retrieval"
date: 2026-03-29
description: "Hybrid search combines BM25 sparse retrieval with dense vector search. Here's how reciprocal rank fusion works, what it costs, and when the combination actually beats either method alone."
tags: [ai, rag, vector-search, infrastructure]
status: published
---

Dense vector search became the default for RAG systems quickly. Embeddings capture semantic meaning, handle paraphrase and synonym matching, and outperform keyword search on most standard retrieval benchmarks. The problem is that dense retrieval fails predictably on exact keyword queries: product codes, error messages, proper nouns, and technical identifiers that don't have semantic neighbors in embedding space. BM25 handles all of those well. Hybrid search runs both retrievers and fuses their results.

**Short answer:** Hybrid search runs BM25 and dense vector retrieval in parallel, then merges ranked results using reciprocal rank fusion (RRF) or a weighted linear combination. On BEIR benchmarks, hybrid search improves NDCG@10 by 18% over BM25 alone and produces consistent gains across domains. The tradeoff is higher retrieval infrastructure complexity and roughly 2x the compute per query.

## Why dense retrieval alone misses obvious queries

Dense vector search encodes queries and documents into a continuous embedding space and retrieves documents by geometric proximity. That works well for natural language queries where meaning is what matters. "What causes memory leaks in Go?" maps cleanly to documents about garbage collection, reference counting, and runtime profilers even without the exact words.

Exact-match queries break this. An error code like `ORA-00942` has no semantic neighborhood. A product SKU like `B08N5WRWNW` doesn't cluster with semantically related products in embedding space. A function name like `getStatefulPartitionedCall` appears once in a codebase and won't retrieve based on meaning because there's no meaning to encode beyond the string itself.

BM25 handles these cases directly. BM25 (Best Matching 25) is a probabilistic relevance model derived from TF-IDF that scores documents based on term frequency, inverse document frequency, and document length normalization. A query for `ORA-00942` scores documents containing that exact string very highly and ignores documents that are semantically related but don't contain the term.

The BEIR benchmark authors explicitly note that BM25 is a "strong generalizable baseline," with many dense single-vector embedding models trained on MS MARCO labels being outperformed by BM25 in out-of-domain settings. Dense retrieval generalizes well when your query distribution looks like your training distribution. When it doesn't, BM25 is often better.

## Reciprocal rank fusion: the merge algorithm that doesn't require score normalization

Running two retrievers is straightforward. Merging their ranked result lists is the hard part.

A naive linear combination of scores fails because BM25 scores and embedding similarity scores exist on completely different scales. A BM25 score of 8.5 and a cosine similarity of 0.87 mean nothing relative to each other without normalization. Min-max normalization addresses this but requires knowing the score distribution for each retriever on each query, which means you can't compute the final score until all candidates are returned.

Reciprocal Rank Fusion (RRF) avoids the normalization problem entirely. RRF scores each document by summing `1 / (k + rank)` across all result lists the document appears in, where `k=60` is a constant from [the original Cormack et al. SIGIR 2009 paper](https://opensearch.org/blog/introducing-reciprocal-rank-fusion-hybrid-search/). Rank position is all that matters; the underlying scores are discarded.

The formula means a document ranked first in one list and missing from the other scores `1/(60+1) = 0.0164`. A document ranked first in both lists scores `0.0164 + 0.0164 = 0.0328` and will almost always win. A document ranked 100th in both lists scores `0.0099 + 0.0099 = 0.0198` and stays near the bottom. Documents that appear in only one list score modestly and get natural deranking relative to documents that both retrievers agreed on.

The practical advantage of RRF: no tuning required for initial deployment. The `k=60` constant generalizes well across domains. You don't need labeled data to set weights. [Elasticsearch recommends RRF as the starting point](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid) precisely because of this robustness.

## Benchmark numbers: what the gains actually look like

[Elastic's benchmarks](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid) show RRF increasing average NDCG@10 by 1.4% over their Learned Sparse Encoder alone and 18% over BM25 alone across the BEIR benchmark suite.

[Azure AI Search benchmarks](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167) show hybrid retrieval plus semantic reranking consistently outperforming pure vector search even with OpenAI's `text-embedding-3-large` as the dense retriever. The combination of hybrid search and a cross-encoder reranker on top produces the strongest results.

On the WANDS furniture e-commerce benchmark, RRF added only +1.7% NDCG over dense-only. On domain-specific scientific literature benchmarks, the gains reach +24%. The size of the improvement correlates with how much exact-match terminology your corpus contains.

[Weaviate's search mode benchmarking](https://weaviate.io/blog/search-mode-benchmarking) compares pure keyword, pure vector, and hybrid across their own benchmarks and shows hybrid consistently at the top, though the margins vary.

## Implementation differences across the major systems

**Weaviate** has the most ergonomic hybrid search API. A single `hybrid()` call takes an `alpha` parameter: `alpha=0` means pure BM25, `alpha=1` means pure vector search, and `alpha=0.5` runs both with equal weighting using RRF. You don't need to manage separate retrieval calls or merge logic. Weaviate handles the BM25 index internally.

```python
results = collection.query.hybrid(
    query="memory leak debugging",
    alpha=0.5,
    limit=10
)
```

**Qdrant** takes a more explicit approach. You run sparse and dense retrievals separately and apply fusion in the query. Qdrant supports both RRF and its Distribution-Based Score Fusion (DBSF), which attempts to normalize scores before combining them. DBSF can outperform RRF when you have domain knowledge to calibrate it, but it requires more setup. Qdrant also supports SPLADE sparse vectors as a BM25 alternative for richer sparse representations.

**Elasticsearch** supports hybrid search through the `sub_searches` + `rank` API. [Elasticsearch's linear retriever](https://www.elastic.co/search-labs/blog/linear-retriever-hybrid-search) supports weighted linear combination as an alternative to RRF, which can outperform RRF once you have enough annotated queries to tune the weights. Their data suggests roughly 40 annotated queries is the threshold where tuned weights beat untuned RRF.

**Vespa** combines BM25 and neural retrieval natively in its ranking framework. Vespa's advantage is that the fusion happens at the ranking expression level, which gives you fine-grained control over how features from both retrievers interact. The tradeoff is Vespa's steeper learning curve compared to managed services.

## Score normalization vs RRF: when to switch

RRF's rank-only approach discards information. When one retriever is much more confident about a document than the other, RRF treats a rank-1 result the same whether the underlying score was 0.99 or 0.55. Score-based fusion preserves that signal.

Linear combination with min-max normalization can outperform RRF when the score distributions are stable and you have labeled data for weight tuning. [Elasticsearch's benchmarks](https://www.elastic.co/search-labs/blog/weighted-reciprocal-rank-fusion-rrf) found hybrid dismax with name boosting achieved a mean NDCG of 0.7497 versus RRF's 0.7068 on one e-commerce dataset, with the gap closing as document diversity increased.

My recommendation: start with RRF. It requires no labeled data, no score distribution assumptions, and no calibration. Move to weighted linear combination only when you have enough labeled queries to tune it properly and your benchmark results show it's worth the maintenance overhead.

## The alpha parameter and query type routing

Not every query should use the same alpha. A query like "what are the differences between TCP and UDP?" benefits from semantic retrieval (alpha closer to 1). A query like "ERROR_CODE_4291 stack trace" benefits from keyword retrieval (alpha closer to 0).

Some systems route queries to different alpha values based on query classification. A classifier labels queries as "keyword-style" or "semantic-style" and adjusts alpha accordingly. [LlamaIndex has a writeup on alpha tuning](https://medium.com/llamaindex-blog/llamaindex-enhancing-retrieval-performance-with-alpha-tuning-in-hybrid-search-in-rag-135d0c9b8a00) that shows the performance gains from per-query-type tuning versus a fixed alpha.

My opinion on this: query routing for alpha adds complexity that isn't worth it unless you're running production traffic at scale and have the labeled data to validate the classifier. For most teams, a fixed alpha of 0.5-0.7 gets you 90% of the hybrid search benefit.

## Reranking on top of hybrid search

Hybrid search improves recall. Reranking improves precision. The combination is stronger than either alone.

After hybrid retrieval returns a top-K candidate set (typically 20-100 documents), a cross-encoder reranker scores each document against the query independently. Cross-encoders are slower than bi-encoders but produce better relevance scores because they can attend to the interaction between query and document.

[Azure's benchmark data](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167) shows the hybrid + rerank combination consistently outperforming hybrid alone by a significant margin. I wrote about reranking mechanics in depth at [Reranking in RAG](/blog/reranking-in-rag-why-your-top-k-results-are-probably-wrong/).

The ordering matters. Always hybrid-retrieve a larger candidate set first, then rerank down to the final top-K you'll send to the LLM. Running a cross-encoder over your full corpus is too slow to be practical.

## The honest tradeoff

Hybrid search is not universally better than dense-only. On workloads where your queries are natural language and your documents are prose, well-trained dense embeddings often match or exceed hybrid search. The gains show up on mixed corpora: code, product names, technical identifiers mixed with prose documentation.

The infrastructure cost is real. You're running two indexes (BM25 and vector), two retrieval passes per query, and a merge operation. Latency roughly doubles versus single-retriever approaches before any reranking. For latency-sensitive applications, that matters.

I covered embedding model selection in [Embedding Models Compared](/blog/embedding-models-compared/), which is relevant here: the dense retriever quality has a floor effect on hybrid search. A weak dense retriever won't be salvaged by BM25. The combination amplifies both retrievers' strengths, not their weaknesses.

## FAQ

**Should I always use hybrid search for RAG?**
For general-purpose document retrieval over mixed corpora, yes. For narrow semantic workloads where your queries are always natural language and your documents are prose, a well-tuned dense-only retriever can match hybrid performance with half the infrastructure cost. Benchmark your specific corpus before committing to the added complexity.

**Is RRF always better than score normalization?**
RRF is better when you don't have labeled data for weight calibration. Score normalization with tuned weights can outperform RRF, but only with enough annotated queries to validate the tuning. Elasticsearch's data suggests 40+ annotated queries as the practical minimum. Below that, use RRF.

**What is SPLADE and when should I use it instead of BM25?**
SPLADE is a learned sparse model that produces sparse vector representations rather than BM25's explicit term statistics. SPLADE typically outperforms BM25 on semantic queries while retaining the exact-match properties of sparse retrieval. Use SPLADE if you want a stronger sparse component and are willing to run a model at query time. Use BM25 if you want zero ML inference cost on the sparse side.

**What alpha value should I start with in Weaviate?**
Start at 0.5 (balanced BM25 and vector) and evaluate on a representative query set. Move toward 1.0 (more vector) for semantic workloads, toward 0.0 (more BM25) for keyword-heavy workloads. Avoid spending time on fine-grained tuning until you've measured that it moves your benchmark metric meaningfully.

**Does hybrid search help with multi-lingual retrieval?**
Dense multilingual models handle translation-equivalent queries better than BM25. For multi-lingual corpora, the contribution of BM25 drops unless your queries and documents share the same language. In cross-lingual retrieval, a strong multilingual dense retriever with no BM25 typically outperforms hybrid.
