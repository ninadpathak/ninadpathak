---
category: rag
primary_query: semantic caching
siblings:
- contextual-retrieval
- rag-reranking
bridges:
- slug: llm-token-budgets
  reason: Provider-side prompt caching is a different mechanism, and that page works out what it saves.
date: 2026-03-28
description: 'Semantic caching returns a stored LLM answer when a new question is close enough to an old one. How it works, a threshold test on a real embedding model, and when to skip it.'
status: published
work_note: "Tutorials, explainers and comparisons for AI companies are my work as a freelance technical writer. I'm Ninad Pathak, and I build the example and run it before I draft, so your engineers review working code. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Semantic Caching for LLM and RAG Applications'
slug: semantic-caching
updated: 2026-11-17
---

Semantic caching stores the answer an LLM gave to a question and returns it again when a new question means the same thing. A semantic cache decides that two questions mean the same thing by comparing their embeddings, so "How do I reset my password?" can match "I forgot my password, how can I change it?" although the wording differs.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/semantic-caching/semantic-cache.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/semantic-caching/semantic-cache.narrow.svg" width="288" height="664"><img class="np-has-narrow" src="/static/images/diagrams/semantic-caching/semantic-cache.svg" width="720" height="384" alt="An incoming query is embedded and compared with cached queries by similarity. Above the threshold it is a hit and the cached response returns. Below it is a miss, and the full pipeline and model run." loading="lazy" decoding="async"></picture></a>
  <figcaption>A hit returns the stored answer and skips retrieval and generation. A miss runs the pipeline and stores the result for next time.</figcaption>
</figure>

An HTTP cache has a simpler job, because it matches requests exactly. [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html), from June 2022, builds the cache key from the request method and the target URI, and notes that many caches in common use key on the URI alone.

A question typed by a person has no URI to use as a key. People phrase the same request in many different ways, so a cache in front of a [RAG pipeline](/articles/rag/) has to judge how close two questions are, and a wrong judgment returns the wrong answer.

## What is semantic caching?

Semantic caching is a lookup that runs before retrieval and generation and matches questions by meaning. The [glossary entry](/glossary/semantic-caching/) has the short definition, and the mechanism has four steps.

1. Embed the incoming question with an embedding model.
2. Search the stored questions for the nearest one.
3. Compare the similarity score with a threshold.
4. On a hit, return the stored answer, and on a miss, run the full pipeline and store the result.

So a cache hit costs one embedding call and one vector search. A hit skips retrieval, reranking and the model call.

## How much can a semantic cache save?

What a semantic cache saves depends on how often your users ask the same thing, and the published figures come from traffic that repeats a lot. A paper from November 2024, [GPT Semantic Cache](https://arxiv.org/abs/2411.05276) by Sajal Regmi and Chetan Phakami Pun, reports that its cache "reduces API calls by up to 68.8% across various query categories".

The same abstract reports that over 97% of its hits were correct ones. Both figures come from the authors' own tests on query categories they chose, and I'd treat them as an upper limit for a support-style FAQ.

A multi-turn conversation, where every message depends on the message before it, repeats far less often than an FAQ. So measure the repeat rate in your own logs before you build anything.

## How do you choose a similarity threshold?

Choose a threshold by starting high and lowering it while you check for hits that return the wrong answer. Redis's [guide to semantic cache tuning](https://redis.io/blog/10-techniques-for-semantic-cache-optimization/) suggests 0.88 cosine similarity as a starting point for an FAQ cache, then moving down gradually.

The difficulty is that one threshold has to separate questions that mean the same thing from questions that only look alike. The script below scores a handful of new questions against a small cache with an open embedding model, at several thresholds.

```python
"""Score new questions against a small cache of answered ones, at three thresholds."""
import numpy as np
from fastembed import TextEmbedding

MODEL = "BAAI/bge-small-en-v1.5"
CACHED = [
    "How do I reset my password?",
    "How do I cancel my subscription?",
    "What is your return policy?",
]
NEW = [
    ("I forgot my password, how can I change it?", "How do I reset my password?"),
    ("Can I send an item back?", "What is your return policy?"),
    ("How do I cancel my last order?", None),
    ("When does my plan renew?", None),
]
THRESHOLDS = [0.80, 0.88, 0.92]

model = TextEmbedding(MODEL)


def embed(texts):
    vectors = np.array(list(model.embed(texts)))
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


cache = embed(CACHED)
print(f"model: {MODEL}")
print(f"{'new question':<44}{'nearest cached question':<34}{'cosine':<8}" + "".join(f"{t:<7}" for t in THRESHOLDS))
for question, right_answer in NEW:
    scores = cache @ embed([question])[0]
    best = int(scores.argmax())
    cells = []
    for t in THRESHOLDS:
        if scores[best] < t:
            cells.append("miss")
        elif CACHED[best] == right_answer:
            cells.append("hit")
        else:
            cells.append("WRONG")
    print(f"{question:<44}{CACHED[best]:<34}{scores[best]:<8.3f}" + "".join(f"{c:<7}" for c in cells))
```

Run on November 17, it printed this.

```text
model: BAAI/bge-small-en-v1.5
new question                                nearest cached question           cosine  0.8    0.88   0.92
I forgot my password, how can I change it?  How do I reset my password?       0.914   hit    hit    miss
Can I send an item back?                    What is your return policy?       0.761   miss   miss   miss
How do I cancel my last order?              How do I cancel my subscription?  0.807   WRONG  miss   miss
When does my plan renew?                    What is your return policy?       0.644   miss   miss   miss
```

"Can I send an item back?" should hit the cached return policy answer, and it scores 0.761. "How do I cancel my last order?" should miss, because the cached entry is about cancelling a subscription, and it scores 0.807.

So the question that should miss scored higher than the question that should hit. Any threshold low enough to serve the return question also serves the cancel-order question, and at a threshold of 0.80 the cache tells a customer how to cancel a subscription when they asked about an order.

A few test questions and one small embedding model prove nothing about your traffic. The output does show why a threshold needs testing against labelled pairs from your own domain, including pairs that look alike and need different answers.

## What makes a cached answer wrong later?

A cached answer becomes wrong when something it depended on changes, such as the source document. A semantic cache stores each entry under a question, so nothing in the entry says which document its answer came from, and a changed document gives you no list of entries to delete.

The usual causes are a changed source document, a changed system prompt and a changed model. The fix I'd reach for first is to store a version with each entry, made of the document version and the prompt version, and to treat a mismatch as a miss.

A time limit on each entry covers the changes that version numbers miss, such as an edit to a document nobody versioned. And changing the embedding model means rebuilding the cache, since scores from one model can't be compared with vectors from another.

## When should you skip semantic caching?

Skip semantic caching when two people who type the same words need different answers. "When does my plan renew?" is identical text for every customer, so a cache keyed on meaning alone will serve one customer's date to another.

Skip semantic caching for the steps inside an agent loop as well. A prompt that carries tool results and history is close to unique on every turn, so the lookup adds latency and seldom hits.

Skip it also for any answer that contains a live value, such as a price or a queue length. A cached price is wrong as soon as the real price changes.

## Where does a semantic cache sit in a RAG pipeline?

A semantic cache sits in front of every other stage of the pipeline. A hit skips the query embedding for retrieval, the search, the reranker and the model call, so a hit saves retrieval cost and latency as well as the model's bill.

Tuning a cache is separate work from improving retrieval. [Contextual retrieval](/articles/contextual-retrieval/) and [reranking](/articles/rag-reranking/) improve the answer a miss produces, and the cache decides how often a miss happens.

A semantic cache is also different from the prompt caching that model providers offer, where the provider charges less for the opening part of a prompt it has seen before and the model still runs. The [token budgets guide](/articles/llm-token-budgets/) works out what prompt caching saves.

## FAQ

**What is semantic caching?**

Semantic caching is a cache for LLM answers that matches on the meaning of the question. A new question that is similar enough to a stored one gets the stored answer without the model being called.

**What similarity threshold should I start with?**

Redis suggests 0.88 cosine similarity for an FAQ cache. Then test that threshold against pairs of questions from your own domain, including pairs that look alike and need different answers.

**How do I invalidate a semantic cache when the knowledge base changes?**

Store the source document's version with each entry and treat a mismatch as a miss. A time limit on entries catches the changes that versioning doesn't.
