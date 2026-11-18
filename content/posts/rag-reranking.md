---
category: rag
primary_query: reranking
siblings:
- vector-embeddings
- hybrid-search
- fine-tuning-vs-rag
bridges:
- slug: llm-context-windows
  reason: Every retrieved token costs latency and money.
date: 2026-03-21
description: 'Reranking in RAG, tested: a bi-encoder and two cross-encoders ranked the same candidates. What the reranker fixed, what it left wrong, and what 100 pairs cost.'
status: published
work_note: "I'm Ninad Pathak, a freelance technical writer. If your AI product's tutorials have fallen behind the product, I write them, and I run the product first. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Reranking in RAG: Why Your Top-K Results Are Probably Wrong'
slug: rag-reranking
updated: 2026-11-17
---

To find out what a reranker changes, I ranked four small sets of candidate passages with an embedding model and then with two cross-encoder rerankers. Neither reranker changed which passage came first, and in the two sets where the embedding model's first choice was wrong, both rerankers repeated the mistake.

Reranking in RAG is a second scoring pass: a retriever returns its top-k candidates, a reranking model reads the query together with each candidate, and the reordered best few go to the language model. The run supports adding that step on one condition, that its scores are checked against marked answers before anyone sets a threshold on them.

Reranking is the stage after retrieval in a [RAG pipeline](/articles/rag/).

## What is reranking in RAG?

Reranking is the stage between retrieval and generation where a slower, more careful model rescores the retriever's candidates against the query. The first stage has to be cheap enough to search the whole corpus, so it uses [embeddings](/articles/vector-embeddings/) computed for each text alone.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-reranking/bi-encoder.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-reranking/bi-encoder.narrow.svg" width="288" height="544"><img class="np-has-narrow" src="/static/images/diagrams/rag-reranking/bi-encoder.svg" width="720" height="600" alt="The query and the document each pass through the embedding model on their own, and each comes out as a single vector. The database compares the two vectors by distance, so the model never sees the query and the document together." loading="lazy" decoding="async"></picture></a>
  <figcaption>The model embeds the query and the document separately, so the score compares two vectors and never the two texts.</figcaption>
</figure>

That first-stage model is a bi-encoder, and its limit is in the figure: the query and the document are never read together. A sentence about error E-4047 scores 0.68 against a query for E-4048 in the run below, because closeness is all the vector records.

## How does a reranker work?

A reranker is usually a [cross-encoder](/glossary/cross-encoder-reranking/), a model that takes the query and one candidate as a single input and returns one relevance score. Every query token can attend to every document token, so the model can check a condition in the question against the text of the answer.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-reranking/cross-encoder.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-reranking/cross-encoder.narrow.svg" width="288" height="544"><img class="np-has-narrow" src="/static/images/diagrams/rag-reranking/cross-encoder.svg" width="720" height="600" alt="The query and one candidate document go into the cross-encoder as a single combined input, so every query token can attend to every document token. The model reads the pair side by side and outputs one relevance score." loading="lazy" decoding="async"></picture></a>
  <figcaption>A single model reads the query and the document together, which sharpens its score and makes it too slow for the whole corpus.</figcaption>
</figure>

The cost of reading pairs is that nothing can be computed ahead of time. Each query needs one model pass per candidate, which is why a reranker runs over a short list and never over the corpus.

Cohere's [Rerank documentation](https://docs.cohere.com/docs/rerank-overview) describes the same contract for its hosted model: a query and a list of documents go in, and the documents come back ordered by relevance with a score each.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-reranking/reranking-pipeline.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-reranking/reranking-pipeline.narrow.svg" width="288" height="720"><img class="np-has-narrow" src="/static/images/diagrams/rag-reranking/reranking-pipeline.svg" width="720" height="256" alt="Stage one embeds the query with a fast bi-encoder and pulls the top 100 chunks from the vector database, where the right chunk can sit far down the list. Stage two pairs the query with each of those chunks, scores the pairs with a cross-encoder, and promotes the right chunk to the top five." loading="lazy" decoding="async"></picture></a>
  <figcaption>Somewhere in the top 100 sits the correct answer, and the second stage rescores that list before the cut.</figcaption>
</figure>

## What does a reranker fix, and what does it leave?

The rerankers in my run widened the distance between right and wrong scores and left the top-ranked passage unchanged. I gave a small embedding model, a small cross-encoder and a larger one the same four candidates for each of four queries, with the answering document marked in advance.

```python
"""Rank the same four candidates with a bi-encoder and two cross-encoders."""
import time
import numpy as np
from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder

# Each case: query, the number of the document that answers it, four candidates.
cases = [
    ("what does error E-4048 mean", 2, [
        "E-4047: the upload was rejected because the file is larger than the plan allows.",
        "E-4048: the API key is valid but lacks the scope this endpoint requires.",
        "E-4049: the request was throttled because the account passed its hourly limit.",
        "Error codes in the E-4000 range are returned by the gateway before a request reaches a service.",
    ]),
    ("can I get a refund after 30 days", 1, [
        "Refunds are available within 30 days of purchase. After 30 days we offer account credit only.",
        "Shipping takes 3 to 5 business days, and orders over 30 dollars ship free.",
        "Our refund policy covers annual plans. Monthly plans can be cancelled at any time.",
        "To request a refund, open Billing and choose Request refund next to the invoice.",
    ]),
    ("which python versions does the sdk not support", 2, [
        "The SDK supports Python 3.9 through 3.13.",
        "Python 3.8 and earlier are not supported and will fail at import.",
        "The SDK is tested on Linux, macOS and Windows with every supported Python version.",
        "Install the SDK with pip install acme-sdk.",
    ]),
    ("how do I rotate an API key without downtime", 2, [
        "API keys can be created and deleted on the Keys page of the dashboard.",
        "Create a second key, deploy it everywhere the first is used, then delete the first key. Both keys work during the overlap.",
        "Rotating keys regularly limits the damage from a leaked credential.",
        "Downtime during deployments usually comes from connections that are not drained before a restart.",
    ]),
]

bi = TextEmbedding("BAAI/bge-small-en-v1.5")
small = TextCrossEncoder("Xenova/ms-marco-MiniLM-L-6-v2")
base = TextCrossEncoder("BAAI/bge-reranker-base")


def line(label, scores, answer):
    order = [int(i) + 1 for i in np.argsort(-scores)]
    verdict = "right" if order[0] == answer else "wrong"
    print(f"  {label:<18}", " ".join(f"{v:7.2f}" for v in scores), " order", order, verdict)


for query, answer, docs in cases:
    q = np.array(list(bi.embed([query])))[0]
    d = np.array(list(bi.embed(docs)))
    print(f"{query}  (answer: document {answer})")
    line("bi-encoder cosine", d @ q, answer)
    line("MiniLM-L-6 score", np.array(list(small.rerank(query, docs))), answer)
    line("bge-base score", np.array(list(base.rerank(query, docs))), answer)

query, _, docs = cases[0]
hundred = (docs * 25)[:100]
print()
print(f"timing input: 100 passages averaging {sum(len(p.split()) for p in hundred) / 100:.0f} words")
for label, run in (
    ("bi-encoder, embed 1 query", lambda: list(bi.embed([query]))),
    ("MiniLM-L-6, score 100 pairs", lambda: list(small.rerank(query, hundred))),
    ("bge-base, score 100 pairs", lambda: list(base.rerank(query, hundred))),
):
    start = time.perf_counter()
    run()
    print(f"{label}: {(time.perf_counter() - start) * 1000:.0f} ms")
```

The script needs `pip install fastembed numpy`, and fastembed loads a quantized ONNX build of the embedding model. I ran `python3 rerank_demo.py` on an Apple M2 laptop CPU.

```text
what does error E-4048 mean  (answer: document 2)
  bi-encoder cosine     0.68    0.76    0.63    0.62  order [2, 1, 3, 4] right
  MiniLM-L-6 score      2.96    3.31    3.18   -1.18  order [2, 3, 1, 4] right
  bge-base score       -0.41    1.79   -3.09   -7.61  order [2, 1, 3, 4] right
can I get a refund after 30 days  (answer: document 1)
  bi-encoder cosine     0.87    0.64    0.71    0.69  order [1, 3, 4, 2] right
  MiniLM-L-6 score      8.10  -10.08   -4.20   -5.43  order [1, 3, 4, 2] right
  bge-base score        6.44   -7.18   -4.59   -4.07  order [1, 4, 3, 2] right
which python versions does the sdk not support  (answer: document 2)
  bi-encoder cosine     0.86    0.80    0.73    0.68  order [1, 2, 3, 4] wrong
  MiniLM-L-6 score      6.91    4.13    6.50   -7.26  order [1, 3, 2, 4] wrong
  bge-base score        2.42    0.37    0.47   -0.65  order [1, 3, 2, 4] wrong
how do I rotate an API key without downtime  (answer: document 2)
  bi-encoder cosine     0.72    0.68    0.63    0.57  order [1, 2, 3, 4] wrong
  MiniLM-L-6 score     -2.57   -8.30   -6.32   -6.24  order [1, 4, 3, 2] wrong
  bge-base score       -2.91   -5.08   -5.21   -4.35  order [1, 4, 2, 3] wrong

timing input: 100 passages averaging 14 words
bi-encoder, embed 1 query: 8 ms
MiniLM-L-6, score 100 pairs: 232 ms
bge-base, score 100 pairs: 1792 ms
```

On the refund query the embedding model gave the answer 0.87 and the wrong passages as much as 0.71. Both rerankers gave the answer a high positive score and every wrong passage a negative one.

A spread that wide is tempting to cut on, and the other rows say why a fixed cut is unsafe. When the reranker is right its scores separate cleanly, and when it is wrong they separate as cleanly around the wrong passage.

Asked which Python versions the SDK does not support, every model preferred the sentence listing the versions it does support, and asked how to rotate a key without downtime, every model preferred a sentence that mentions keys over the passage that gives the procedure.

On the key-rotation query the small reranker gave the right passage its lowest score of the four, so a threshold at zero drops the answer along with everything else. A set of sixteen passages can't measure how often that happens, and it is enough to show that a reranker can share the retriever's blind spots.

## Do rerankers handle exact identifiers better?

The larger reranker, bge-reranker-base, did, by a wide margin, and the small MiniLM model barely did. For the query about E-4048, bge-reranker-base scored the right document 1.79 and the two neighbouring codes below zero, while MiniLM scored both neighbours within 0.35 of the right one.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-reranking/keyword-exactness.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-reranking/keyword-exactness.narrow.svg" width="288" height="688"><img class="np-has-narrow" src="/static/images/diagrams/rag-reranking/keyword-exactness.svg" width="720" height="376" alt="A query for error code E-4048 goes to vector search, which returns both E-4048 and the near-identical E-4049 as close matches. A cross-encoder then reads the query and each document together: it rejects the document about E-4049 and keeps the document about E-4048." loading="lazy" decoding="async"></picture></a>
  <figcaption>The textbook case for exact identifiers. The run on this page had the bi-encoder put E-4048 first already, and the larger cross-encoder is what pushed E-4049 well below it.</figcaption>
</figure>

The embedding model had already ranked E-4048 first in this set. The dependable fix for identifiers is still to add a keyword retriever to the first stage, as [hybrid search](/articles/hybrid-search/) does, so the exact string is guaranteed a place in the candidate list.

## How large should top-k be before reranking?

Retrieve many more candidates than you intend to keep, because a reranker can only promote what the first stage returned. The measured example I trust here is Kapa's [Company Knowledge Bench](https://www.kapa.ai/blog/company-knowledge-bench) from October 2, 2026, which reports that "Retrieving 100 candidates and reranking them down to 15 lifts that to 0.50, for a third of a second more", up from 0.41 for plain hybrid search.

That gain mixes two changes. The plain row returned its top 15 directly, so the reranked row benefits from a pool nearly seven times deeper as well as from the reranker, and Kapa sells retrieval, which its post discloses.

My run can't speak to depth at all, since each query had four candidates. Its failures suggest a check to make before settling on a number: log the cases where the right chunk was retrieved and still ranked low after reranking, since a deeper pool won't help those.

## What does reranking cost in latency?

Reranking costs one model pass per candidate, so latency grows with both the candidate count and the size of the model. The run above scored 100 pairs in 232 ms with the small cross-encoder and 1,792 ms with the larger one, against 8 ms to embed the query.

The run's passages average 14 words, far shorter than a real chunk, so both figures are a floor.

A repeated question doesn't have to pay that cost twice, and [semantic caching](/articles/semantic-caching/) covers the cache that sits in front of retrieval.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-reranking/latency-tradeoff.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-reranking/latency-tradeoff.narrow.svg" width="288" height="616"><img class="np-has-narrow" src="/static/images/diagrams/rag-reranking/latency-tradeoff.svg" width="720" height="288" alt="A reranked request in four steps. Embedding the query and retrieving a hundred vectors each take milliseconds, so the first stage is fast. Reranking a hundred pairs with a cross-encoder adds from hundreds of milliseconds to more than a second, depending on the model, before the answer starts streaming." loading="lazy" decoding="async"></picture></a>
  <figcaption>Retrieval is fast, and the cross-encoder is where the time goes.</figcaption>
</figure>

Those figures are one run on one laptop, and they moved between runs: an earlier run of the small model took 479 ms for the same 100 pairs. A GPU or a hosted API changes the absolute numbers, and the ratio between model sizes is the part to plan around.

The larger model was nearly eight times slower here and was also the only one that separated the error codes. That is the trade a team has to make with its own queries, and it is why the candidate count is worth tuning before the model is.

## Which reranking models should you try first?

Try one small open model, one larger open model and one hosted API, on queries with known answers from your own data. The table lists the two I ran and the hosted model named in Cohere's current documentation.

| Model | Where it runs | What I can say about it |
| --- | --- | --- |
| Xenova/ms-marco-MiniLM-L-6-v2 | Your own CPU, an 80 MB download | 232 ms per 100 short pairs in my run, weak on near-identical codes |
| BAAI/bge-reranker-base | Your own CPU or GPU, about 1 GB, MIT license | 1,792 ms per 100 short pairs in my run, clear separation on codes |
| Cohere rerank-v5.0-pro | Hosted API | Not run for this page |

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-reranking/models-providers.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-reranking/models-providers.narrow.svg" width="288" height="360"><img class="np-has-narrow" src="/static/images/diagrams/rag-reranking/models-providers.svg" width="720" height="424" alt="An application can send rerank requests two ways. The first path goes over the network to a hosted API such as Cohere Rerank, with no infrastructure to run but a network hop and a fee per request. The other goes to an open-source model such as bge-reranker-base running locally on the team's own GPU, with no network hop but a fixed infrastructure cost." loading="lazy" decoding="async"></picture></a>
  <figcaption>A hosted API trades a network hop and per-call fees for zero infrastructure, and a local model costs a GPU but no hop and no fee.</figcaption>
</figure>

A general-purpose language model can also do the choosing. The highest row of Kapa's table is an agentic retriever, in which a model selects what to read, and it takes "about five seconds" per query.

## Can a larger embedding model or a long context replace the reranker?

I don't think so, and the reason is in how each is built. A larger embedding still describes each text alone, so more dimensions add detail to both descriptions and still compare nothing.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-reranking/dimension-scaling.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-reranking/dimension-scaling.narrow.svg" width="288" height="552"><img class="np-has-narrow" src="/static/images/diagrams/rag-reranking/dimension-scaling.svg" width="720" height="288" alt="Moving from a 384-dimension embedding to a 3072-dimension embedding gives the bi-encoder eight times the dimensions, but it still compresses the query and the document separately, so the larger vector is still marked as failing to compare them together. The cross-encoder after it remains the step that reads both at once." loading="lazy" decoding="async"></picture></a>
  <figcaption>A vector with eight times the dimensions still describes each text alone, so the reranker stays.</figcaption>
</figure>

Passing all hundred candidates to the language model moves the selection problem into the prompt. The [context window guide](/articles/llm-context-windows/) covers what models do with long inputs, and the comparison of [fine-tuning and RAG](/articles/fine-tuning-vs-rag/) covers the cost side.

Neither argument is measured on this page. The run adds one thing to them: reranker scores spread far enough to cut on once they have been checked against [marked answers](/articles/rag-evaluation/), and a long prompt offers no cut at all.

## How do you add a reranker to an existing pipeline?

Insert it between the search call and the prompt builder: raise the retrieval count, score each candidate against the query and keep the top few. The script above is the whole mechanism, with a list of strings in and a list of scores out.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-reranking/implementation-flow.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-reranking/implementation-flow.narrow.svg" width="288" height="720"><img class="np-has-narrow" src="/static/images/diagrams/rag-reranking/implementation-flow.svg" width="720" height="256" alt="Four steps in order. The vector database returns one hundred candidates for the query. The query and each candidate's text go to the reranker as a list of pairs, which scores them. The top five results are sliced off the sorted list and handed to the prompt builder." loading="lazy" decoding="async"></picture></a>
  <figcaption>Search wide, rerank the hundred, keep the top five for the prompt.</figcaption>
</figure>

Before shipping, collect the queries your current pipeline answers badly and mark the passage that should have answered each. Run them through the reranker as I did above, and count the cases it corrects separately from the cases it merely rescores.

Set a score threshold only after that count, and only where the marked answers sit above it.
