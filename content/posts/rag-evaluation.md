---
category: rag
primary_query: rag evaluation
siblings:
- rag-reranking
- contextual-retrieval
- vector-embeddings
date: 2026-04-16
description: RAG evaluation scores retrieval and the generated answer separately. What
  recall, precision, MRR, nDCG, faithfulness and response relevancy each measure, with
  a retrieval scorer you can run.
status: published
work_note: "I'm Ninad Pathak, and I freelance as a technical writer for AI companies. I build the example and run it before I draft a tutorial, so your engineers review working code. [Here's how we'd work together](/services/freelance-technical-writer-for-ai-companies/)."
title: 'RAG Evaluation Metrics and What Each One Measures'
updated: '2026-08-17'
slug: rag-evaluation
---

The method behind RAG evaluation was worked out on index cards. Cyril Cleverdon ran the [Cranfield experiments](https://en.wikipedia.org/wiki/Cranfield_experiments) at a college of aeronautics in England in the 1960s, comparing indexing systems by putting questions to a fixed collection of abstracts and checking whether relevant ones came back.

Neither phase of that work used a computer, and the setup hasn't changed much since. You still need a fixed set of questions and a human judgment of which documents answer each one.

RAG evaluation is the practice of scoring a retrieval-augmented generation pipeline in two parts: whether retrieval returned the right passages, and whether the generated answer sticks to them. The second part is the new one, and [Ragas](https://arxiv.org/abs/2309.15217) arrived in September 2023 with metrics for it that don't need a human-written reference answer.

Below are the RAG evaluation metrics for both halves of a [RAG](/articles/rag/) pipeline, with a retrieval scorer and the output it printed on a small labelled set.

## What are the main RAG evaluation metrics?

The main RAG evaluation metrics split into retrieval metrics, which compare a ranked list against labelled passages, and answer metrics, which need a model to judge the text:

| Metric | Stage | The question it answers | What it needs |
|---|---|---|---|
| Recall@k | Retrieval | Did the relevant passages make the top k? | Labelled relevant passages |
| Precision@k | Retrieval | How much of the top k is relevant? | Labelled relevant passages |
| MRR | Retrieval | How high is the first relevant passage? | Labelled relevant passages |
| nDCG@k | Retrieval | Are the relevant passages ranked near the top? | Labelled relevant passages |
| Faithfulness | Answer | Is each claim in the answer supported by the retrieved context? | A judge model |
| Response relevancy | Answer | Does the answer address the question that was asked? | A judge model and embeddings |

The names on the answer side move around. Ragas's [list of RAG metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) reads this way today, and a tutorial written against an older release may use other names:

- Context Precision
- Context Recall
- Context Entities Recall
- Noise Sensitivity
- Response Relevancy
- Faithfulness

## How do you measure retrieval quality?

You measure retrieval quality by running each test question through the retriever and comparing the ranked results with the passages a person marked as relevant. The script below does that for six questions over eight documents, with fastembed 0.7.4 and the `BAAI/bge-small-en-v1.5` embedding model:

```python
"""Score a small retriever with recall@k, precision@k, MRR and nDCG@k. No LLM involved."""
import math

import numpy as np
from fastembed import TextEmbedding

DOCS = {
    "d1": "Refunds are issued to the original payment method within 5 business days.",
    "d2": "To request a refund, open Billing, pick the invoice and choose Request refund.",
    "d3": "Annual plans can be refunded in full within 30 days of purchase.",
    "d4": "API keys are created under Settings, then Developer, then Keys.",
    "d5": "Rotate an API key by creating a new key and deleting the old one.",
    "d6": "The API allows 100 requests per minute for each key.",
    "d7": "A 429 response means the rate limit was hit. Wait and retry.",
    "d8": "Invoices are emailed on the first day of each month.",
}
# Each question with the documents a person marked as needed to answer it.
QUERIES = [
    ("How do I get my money back?", {"d1", "d2", "d3"}),
    ("How long does a refund take?", {"d1"}),
    ("Where do I make an API key?", {"d4"}),
    ("My key leaked, what now?", {"d5"}),
    ("Why am I getting 429 errors?", {"d6", "d7"}),
    ("When do I get billed?", {"d8"}),
]
K = 3

model = TextEmbedding("BAAI/bge-small-en-v1.5")
ids = list(DOCS)
doc_vecs = np.array(list(model.embed([DOCS[i] for i in ids])))


def retrieve(query):
    q = next(iter(model.embed([query])))
    scores = doc_vecs @ q / (np.linalg.norm(doc_vecs, axis=1) * np.linalg.norm(q))
    return [ids[i] for i in np.argsort(-scores)]


def ndcg(ranked, relevant, k):
    dcg = sum(1 / math.log2(rank + 1) for rank, doc in enumerate(ranked[:k], start=1) if doc in relevant)
    ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(len(relevant), k) + 1))
    return dcg / ideal


rows = []
print(f"{'query':<30} {'top ' + str(K):<12} recall@{K}  precision@{K}  RR    nDCG@{K}")
for query, relevant in QUERIES:
    ranked = retrieve(query)
    hits = [doc for doc in ranked[:K] if doc in relevant]
    recall = len(hits) / len(relevant)
    precision = len(hits) / K
    rr = 1 / next(rank for rank, doc in enumerate(ranked, start=1) if doc in relevant)
    score = ndcg(ranked, relevant, K)
    rows.append((recall, precision, rr, score))
    print(f"{query:<30} {' '.join(ranked[:K]):<12} {recall:<9.2f} {precision:<12.2f} {rr:<5.2f} {score:.2f}")
means = np.mean(rows, axis=0)
print(f"{'mean':<30} {'':<12} {means[0]:<9.2f} {means[1]:<12.2f} {means[2]:<5.2f} {means[3]:.2f}")
```

Running it printed:

```text
query                          top 3        recall@3  precision@3  RR    nDCG@3
How do I get my money back?    d2 d1 d3     1.00      1.00         1.00  1.00
How long does a refund take?   d1 d3 d2     1.00      0.33         1.00  1.00
Where do I make an API key?    d4 d5 d6     1.00      0.33         1.00  1.00
My key leaked, what now?       d5 d4 d6     1.00      0.33         1.00  1.00
Why am I getting 429 errors?   d7 d6 d4     1.00      0.67         1.00  1.00
When do I get billed?          d2 d8 d3     1.00      0.33         0.50  0.63
mean                                        1.00      0.50         0.92  0.94
```

The recall column reads 1.00 on every row, so by that metric this retriever is finished. It isn't, and the last row shows why: for "When do I get billed?" the refund instructions ranked first and the right document came second.

Only the rank-aware columns caught that. Reciprocal rank fell to 0.50 and nDCG to 0.63 on that question, which is the case for reading nDCG once you [add a reranking stage](/articles/rag-reranking/) and order is the thing you're tuning.

Now look at the precision column, because it's the one that misleads. A question with one relevant document can't score above 0.33 when k is 3, so the mean of 0.50 here says more about how many answers each question has than about the retriever.

That's also why I'd read the rows before the mean. The mean nDCG of 0.94 looks healthy, and the row under it is a billing question answered with refund steps.

If recall itself is low, the fix is upstream of everything on this page, in chunking or in the [embedding model](/articles/vector-embeddings/). [Contextual retrieval](/articles/contextual-retrieval/) is one such fix, and Anthropic reported its results as a drop in exactly this kind of top-k retrieval failure.

## How do you measure answer quality?

You measure answer quality with a judge model that checks the answer against the retrieved context and against the question. Ragas defines the two metrics that carry this, and both are scored between 0 and 1.

[Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) breaks the answer into claims and checks each against the context. The score is the number of supported claims divided by the total, and Ragas counts an answer as faithful "if all its claims can be supported by the retrieved context".

[Response relevancy](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/answer_relevance/) works backwards. The judge writes a few questions that the answer would fit, and the score is the average cosine similarity between those and the user's question.

Read that method again and you'll see what it can't catch. The docs say the metric works "without evaluating factual accuracy", so a wrong answer that stays on topic scores well, and I wouldn't report it without faithfulness beside it.

Ragas has retrieval-side metrics of its own too. Its [context recall](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/) splits a reference answer into claims and checks whether the retrieved context supports each, which means it needs a reference where faithfulness doesn't.

## Which metric should you fix first?

Fix retrieval recall first, because nothing downstream can use a passage that was never retrieved. After that I'd go in the order of the pipeline: precision and ranking, then faithfulness, then relevancy.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-evaluation/eval-order.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-evaluation/eval-order.narrow.svg" width="288" height="720"><img class="np-has-narrow" src="/static/images/diagrams/rag-evaluation/eval-order.svg" width="720" height="256" alt="Four RAG metrics in the order to fix them: context recall first, so the right chunks are retrieved; context precision second, so the context carries signal rather than noise; faithfulness third, so the answer sticks to the context; answer relevancy last, because it measures the whole system working together." loading="lazy" decoding="async"></picture></a>
  <figcaption>Each stage only means something once the one before it holds. Starting with answer relevancy hides upstream failures.</figcaption>
</figure>

The order matters for reading the scores as well as for fixing them. A low faithfulness score on a question where recall failed is a retrieval bug that happens to show up in the answer.

## How do you set a pass threshold?

Set it from your own labelled examples and from what a wrong answer costs you. I don't think a universal cutoff exists, and the precision column above is the reason: 0.33 was a perfect score on four of those six questions.

A threshold is also only as good as the test set under it. The questions are frozen on the day you write them and your users keep asking new ones, so I'd treat adding fresh production questions to the set as part of the evaluation work.

That worry is as old as the method. Wikipedia's account of Cranfield says the experiments were "the topic of continual debate for years", and the debate was over whether the test setup measured the right thing.

## FAQ

**Do I need ground-truth answers for RAG evaluation?**

For retrieval metrics you need labelled relevant passages. Faithfulness and response relevancy run without a reference answer, and Ragas's context recall requires one.

**What is a good faithfulness score?**

No single number applies everywhere. A score of 1.0 means every claim in the answer was supported by the retrieved context, and how far below that you can accept depends on what a wrong claim costs.

**How is context precision different from precision@k?**

Precision@k is the share of the top k results that are relevant. Ragas's context precision averages precision@k over the positions of the retrieved chunks, so it also rewards putting relevant chunks higher.

**Are BLEU and ROUGE useful for RAG?**

They score word overlap with a reference answer, so a correct answer in different words scores low. I'd use them only where the wording itself is what you're checking.

**Can I evaluate retrieval without calling an LLM?**

Yes. The script on this page computes recall, precision, reciprocal rank and nDCG from document ids alone.
