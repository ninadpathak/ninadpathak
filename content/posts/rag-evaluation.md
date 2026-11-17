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

The method used to evaluate a RAG system today was worked out in the 1960s with index cards and no computer. Cyril Cleverdon ran the [Cranfield experiments](https://en.wikipedia.org/wiki/Cranfield_experiments) at a college of aeronautics in England, comparing indexing systems by putting questions to a fixed collection of abstracts and checking whether relevant ones came back.

A retrieval test in 2026 has the same two ingredients as Cleverdon's. You need a fixed set of questions, and you need a person's judgment of which documents answer each question.

RAG evaluation is the practice of scoring a retrieval-augmented generation pipeline in two parts: whether retrieval returned the right passages, and whether the generated answer says only what those passages support. Cleverdon had no generated answer to score, and [Ragas](https://arxiv.org/abs/2309.15217) arrived in September 2023 with metrics for the answer that don't need a human-written reference answer.

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

Ragas has renamed its metrics between releases, so check the current names before copying an import from a tutorial. The metric this page calls response relevancy has also been called answer relevancy, and Ragas's [list of RAG metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) reads this way today:

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

The recall column reads 1.00 on every row, which would suggest the retriever has nothing left to fix. The last row shows a real error that recall missed: for "When do I get billed?" the retriever ranked the refund instructions (`d2`) first and the invoice schedule (`d8`) second.

Recall counts whether `d8` appears anywhere in the retrieved results, so it scored that row as perfect. Reciprocal rank and nDCG both look at position, and they fell to 0.50 and 0.63 on the billing question.

Position is what a reranker changes, so nDCG is the metric to watch once you [add a reranking stage](/articles/rag-reranking/).

The precision column understates this retriever. A question with one relevant document can't score above 0.33 when k is 3, because the other two retrieved slots have to hold something.

So the mean precision of 0.50 largely reflects that four of the six questions have a single relevant document.

I'd read the per-question rows before I read the mean. The mean nDCG of 0.94 looks healthy, and it hides one question out of six where a customer asking about billing dates would be shown refund steps first.

If recall itself is low, no ranking change will help, because the right passage never reached the candidate list. The fix is in how documents are chunked or in the [embedding model](/articles/vector-embeddings/).

[Contextual retrieval](/articles/contextual-retrieval/) is one fix of that kind, and Anthropic reported its results as a drop in how often the right passage was missing from the top 20.

## How do you measure answer quality?

You measure answer quality with a judge model that checks the answer against the retrieved context and against the question. Ragas defines a metric for each of those checks, faithfulness and response relevancy, and both are scored between 0 and 1.

[Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) breaks the answer into claims and checks each against the context. The score is the number of supported claims divided by the total, and Ragas counts an answer as faithful "if all its claims can be supported by the retrieved context".

For [response relevancy](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/answer_relevance/), the judge model reads the answer and writes a few questions that the answer would fit, and the score is the average cosine similarity between those generated questions and the user's real question.

Response relevancy can't tell a correct answer from a wrong one. The docs say the metric works "without evaluating factual accuracy", so an answer that gives the wrong billing date still scores well as long as it's about billing dates, and I wouldn't report response relevancy without faithfulness beside it.

Ragas also has metrics for the retrieval step. Its [context recall](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/) splits a reference answer into claims and checks whether the retrieved context supports each, which means context recall needs a reference answer and faithfulness doesn't.

## Which metric should you fix first?

Fix retrieval recall first, because nothing downstream can use a passage that was never retrieved. After that I'd go in the order of the pipeline: precision and ranking, then faithfulness, then relevancy.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-evaluation/eval-order.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-evaluation/eval-order.narrow.svg" width="288" height="720"><img class="np-has-narrow" src="/static/images/diagrams/rag-evaluation/eval-order.svg" width="720" height="256" alt="Four RAG metrics in the order to fix them. Recall comes first, so the right passages are retrieved. Precision and ranking come second, so the context carries little noise. Faithfulness is third, so the answer sticks to the context, and response relevancy is last." loading="lazy" decoding="async"></picture></a>
  <figcaption>A faithfulness score means little until recall is high, because the answer can't stick to a passage that was never retrieved. Starting with response relevancy hides those retrieval failures.</figcaption>
</figure>

The same order tells you how to read a bad score. Suppose faithfulness is low on a question where recall also failed: the model made claims the context didn't support because the supporting passage was never retrieved, and the bug to fix is in retrieval.

When recall and ranking are good and the answer still contradicts the passages, the model's behavior is the problem. Changing a model's behavior is the subject of [RAG vs fine-tuning](/articles/fine-tuning-vs-rag/).

## How do you set a pass threshold?

Set a pass threshold from your own labelled examples and from what a wrong answer costs you. I don't think a universal cutoff such as "precision above 0.8" can exist, and the script's output shows why: 0.33 was the highest possible precision on four of its six questions.

A threshold only holds while the test questions match what users ask. The test questions are frozen on the day you write them and your users keep asking new ones, so I'd add fresh questions from production logs to the test set on a schedule.

Cleverdon's critics raised the same concern about his fixed test collection. Wikipedia's account of Cranfield says the experiments were "the topic of continual debate for years", and the debate was over whether the test setup measured the right thing.

## FAQ

**Do I need ground-truth answers for RAG evaluation?**

For retrieval metrics you need labelled relevant passages. Faithfulness and response relevancy run without a reference answer, and Ragas's context recall requires one.

**What is a good faithfulness score?**

No single faithfulness score counts as good for every application. A score of 1.0 means every claim in the answer was supported by the retrieved context, and how far below that you can accept depends on what a wrong claim costs.

**How is context precision different from precision@k?**

Precision@k is the share of the top k results that are relevant. Ragas's context precision takes precision@k at each rank that holds a relevant chunk and averages those values, so a relevant chunk at the top rank scores higher than the same chunk two ranks lower.

**Are BLEU and ROUGE useful for RAG?**

BLEU and ROUGE score how many words an answer shares with a reference answer, so a correct answer phrased differently scores low. I'd use them only where the exact wording is what you're checking, as in translation.

**Can I evaluate retrieval without calling an LLM?**

Yes. The script on this page computes recall, precision, reciprocal rank and nDCG from document ids alone.
