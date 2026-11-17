---
category: rag
primary_query: hybrid search
siblings:
- vector-embeddings
- rag-reranking
date: 2026-03-29
description: 'Hybrid search fuses BM25 and vector retrieval. How it scores on a 2026 production benchmark, how reciprocal rank fusion works with runnable code, and what to add after it.'
status: published
work_note: "Your engineers shouldn't have to fix a tutorial's code in review. I'm Ninad Pathak, a freelance technical writer for AI companies, and I build and run every example before I draft. [Hire me to write yours](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Hybrid Search: Combining BM25 and Vector Search'
slug: hybrid-search
updated: 2026-11-17
---

Hybrid search runs a keyword retriever, usually BM25, and a dense vector retriever over the same corpus and fuses the two ranked lists into one. On the latest production benchmark I can find, that fused list is the lowest-scoring retriever in the table.

Within a [RAG pipeline](/articles/rag/) it is the retrieval stage, ahead of reranking.

Kapa's Finn Bauer [published the benchmark on October 2, 2026](https://www.kapa.ai/blog/company-knowledge-bench). It scores seven retrievers on "1,000 eval cases annotated from real production data", and plain hybrid search comes last.

## How does hybrid search score on a 2026 benchmark?

Plain hybrid search scores 0.41 on Kapa's Company Knowledge Bench, below every other retriever tested. The rows above it either draw a deeper pool from the same search and select from it, or replace the search with a model that greps.

| Retriever | Score | Time per query, where the post states it |
| --- | --- | --- |
| Hybrid search | 0.41 | |
| Hybrid search, 100 candidates reranked to 15 | 0.50 | "a third of a second more" |
| Query decomposition, hybrid search and a reranker | 0.56 | 1.8 seconds |
| Agent with grep, OpenAI's smaller Luna model | 0.54 | 13 to 17 seconds |
| Agent with grep, OpenAI's Sol model | 0.61 | 13 to 17 seconds |
| Kapa Default, a tuned fixed pipeline | 0.61 | 3.3 seconds |
| Kapa Deep, a tuned agentic retriever | 0.65 | about five seconds |

Kapa sells retrieval and says so: "A note on bias: retrieval is core to our product, and all seven retrievers were built by us". The fixed-pipeline rows don't depend on its product, and the post's advice from them is "If you change one thing in a basic RAG pipeline, add a reranker."

I read the 0.41 as the score for stopping too early. Hybrid search generates candidates, and the plain row returns its top 15 as they come.

The second row pulls 100 from the same search and reranks them to 15, and the third pools 50 for each of up to three sub-queries, so both gain from a deeper pool and from a step that chooses.

## Why fuse a keyword retriever with a vector retriever?

The two retrievers miss different documents, so their union contains more of what a query needs than either list.

Dense retrieval matches a question about memory leaks to a page on garbage collection that shares none of its words. Given an error code like `ORA-00942` it ranks the exact page first by a margin too thin to set a threshold on, 0.75 against 0.70 for a different Oracle code in [a run on the embeddings page](/articles/vector-embeddings/), and a keyword index matches the string outright.

The published evidence for the gain is older than a year, so read it with its dates. Microsoft's [Azure AI Search comparison](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167) from September 18, 2023 used the Ada-002 embedding model.

<!-- evidence-three: NDCG@3 is the metric Microsoft's Table 1 reports for its customer datasets -->
| Azure AI Search mode, 2023 | Customer datasets, NDCG@3 | BEIR, NDCG@10 | MIRACL, NDCG@10 |
| --- | --- | --- | --- |
| Keyword | 40.6 | 40.6 | 49.6 |
| Vector (Ada-002) | 43.8 | 45.0 | 58.3 |
| Hybrid | 48.4 | 48.4 | 58.8 |
| Hybrid and semantic ranker | 60.1 | 50.0 | 72.0 |

Elastic's [hybrid retrieval post](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid) from July 20, 2023 fused BM25 with Elastic's own learned sparse encoder, with no dense vectors involved. It reports that "Reciprocal Rank Fusion increases average NDCG@10 by 1.4% over Elastic Learned Sparse Encoder alone and 18% over BM25 alone."

Both posts predate the models in Kapa's table, and the shape of the result has held: fusion beats either retriever alone, and on Azure's customer datasets the reranker added more than fusion had.

The background for all of it is the [BEIR benchmark paper](https://arxiv.org/abs/2104.08663) from April 2021, which compared single retrievers and tested no fusion. Its abstract says dense and learned-sparse models "often underperform other approaches" outside their training domain, which is the case against relying on one family.

## How does reciprocal rank fusion work?

Reciprocal rank fusion (RRF) scores each document by summing `1 / (k + rank)` over every list it appears in, and ignores the retrievers' own scores. That sidesteps the problem that a BM25 score of 8.5 and a cosine similarity of 0.87 share no scale.

The method and its constant come from [a SIGIR 2009 paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) by Cormack, Clarke and Büttcher, which says "k = 60 was fixed during a pilot investigation". The whole algorithm fits in a few lines of Python.

```python
def rrf(rankings, k=60):
    """Fuse ranked lists of document ids. Ranks start at 1, as in the 2009 paper."""
    scores = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


bm25 = ["ORA-00942 runbook", "grants guide", "schema FAQ", "tuning notes"]
dense = ["permissions overview", "grants guide", "ORA-00942 runbook", "roles tutorial"]

for doc, score in rrf([bm25, dense]):
    print(f"{score:.4f}  {doc}")

print()
print(f"first in one list only    {1 / 61:.4f}")
print(f"first in both lists       {2 / 61:.4f}")
print(f"rank 100 in both lists    {2 / 160:.4f}")
```

Running it with `python3 rrf.py` prints the fused order and the reference scores.

```text
0.0323  ORA-00942 runbook
0.0323  grants guide
0.0164  permissions overview
0.0159  schema FAQ
0.0156  tuning notes
0.0156  roles tutorial

first in one list only    0.0164
first in both lists       0.0328
rank 100 in both lists    0.0125
```

The two documents both retrievers returned finish well ahead of the one that topped a single list. A document at rank 100 in both lists scores 0.0125, below a document ranked first in only one, so agreement helps and deep agreement helps less.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/hybrid-search/rrf-fusion.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/hybrid-search/rrf-fusion.narrow.svg" width="288" height="536"><img class="np-has-narrow" src="/static/images/diagrams/hybrid-search/rrf-fusion.svg" width="720" height="392" alt="A BM25 keyword list and a vector list each rank the same documents differently. Reciprocal rank fusion discards their scores and adds 1/(60 + rank) from each list, so the document both retrievers rank highly rises to the top of the fused list." loading="lazy" decoding="async"></picture></a>
  <figcaption>Agreement between the two retrievers becomes the strongest signal, and the underlying scores are discarded.</figcaption>
</figure>

Engines disagree on the constant. Elasticsearch's [RRF retriever reference](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/rrf-retriever) says of `rank_constant` that it "Defaults to 60.", and Qdrant's [hybrid queries documentation](https://qdrant.tech/documentation/concepts/hybrid-queries/) counts ranks from zero and says "k is a constant (set to 2 by default)".

A small constant rewards the top of each list much more sharply, so the same two result lists can fuse into different orders on the two engines. Check the default before comparing results across them.

## Should you use RRF or score-based fusion?

Start with whatever your engine defaults to, and treat fusion tuning as a late step. RRF needs no labeled data, and score-based fusion keeps information RRF throws away, such as how far ahead the top result was.

Weaviate has moved to the second kind: its [hybrid search documentation](https://docs.weaviate.io/weaviate/search/hybrid) says "Relative Score Fusion is the default fusion method starting in v1.24." The same page defines the `alpha` weight that balances the two retrievers.

"An alpha of 1 is a pure vector search. An alpha of 0 is a pure keyword search."

Qdrant offers a score-based option called Distribution-Based Score Fusion, available from v1.11.0, which "keeps the raw scores from each query but normalizes their distributions before combining."

My opinion is that routing queries to different alpha values by query type is complexity few systems need. Kapa's table puts the larger win after fusion, and a wrong route sends an identifier query to the retriever least able to tell it from its neighbours.

## Do agents with grep make hybrid search unnecessary?

For code, largely yes, and for mixed company knowledge, no. The Kapa post notes that "Cursor recently stopped searching your code via embeddings in favor of relying only on grep and indexed search.", and its own grep agent with a strong model ties the tuned pipeline at 0.61.

The tie costs 13 to 17 seconds a query against 3.3, and a second Kapa post, [by Matteo Bortoletto and Janis Fluri on October 26](https://www.kapa.ai/blog/retrieval-bottleneck), measures what the grep agent hands back: "for grep, only about one in twenty-five of the chunks it returns is needed". Grep finds things and leaves every selection decision to the model reading the results.

Selection is also where fixed pipelines now lose. That post traced each needed chunk through a test pipeline and found "Of all the gold chunks search found, 34% were never shown to the agentic retriever."

A third of the right material was retrieved and then dropped. That is the same conclusion as the first table, reached from the other direction, and the [reranking guide](/articles/rag-reranking/) covers the step where it happens.

## What does hybrid search cost?

Hybrid search costs a second index, a second query per request and a fusion step. Elastic's 2023 post named the latency side of that, noting that query latency rose "as the two queries are performed sequentially in Elasticsearch" at the time.

Engines differ on whether the two queries run in sequence or in parallel, so measure your own. The choice of dense model is its own decision, covered on the embeddings page linked above.

## FAQ

**Should I always use hybrid search for RAG?** Use it as the candidate generator for mixed corpora that combine prose with code, product names and identifiers, and put a reranker after it. On Kapa's 2026 benchmark that pairing scored 0.50, up from 0.41.

**Is RRF always better than score normalization?** No. RRF is the safer start because it needs no labeled data, and engines disagree on the default: Elasticsearch's RRF retriever uses a rank constant of 60, and Weaviate has defaulted to Relative Score Fusion since v1.24.

**What alpha value should I start with in Weaviate?** Set it explicitly, because Weaviate's documentation says "If you do not set alpha, the effective weighting depends on your client." Start at 0.5, evaluate on a representative query set, and move toward 1 for paraphrase-heavy queries or toward 0 for identifier-heavy ones.
