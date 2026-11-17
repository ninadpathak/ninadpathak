---
category: ai-engineering
date: 2026-03-15
description: 'Vector embeddings explained with a model run on five texts: what an embedding is, why similarity scores mislead, how many dimensions to keep and what binary embeddings cost.'
status: published
work_note: 'At Mem0 I hired writers capable of understanding vector embeddings, and I handled the technical reviews. This guide to embeddings is my own, written for this site, and [the Mem0 case study](/portfolio/) is in my portfolio.'
title: 'Vector Embeddings: A Guide to the Geometry of Meaning in AI'
updated: 2026-11-17
slug: vector-embeddings
---

On October 22 someone posted [a semantic search over about 6.3 million museum artworks](https://lastmuseum.com/) to Hacker News, and an early reply came from a user whose search for "soviet" had "matched cylinder seal 3500bc". Vector embeddings are the numbers behind a search like that: a model turns each text or image into a point in a space with hundreds or thousands of dimensions, and the search returns whatever points sit nearest the query.

[The thread](https://news.ycombinator.com/item?id=50194522) teaches the geometry better than the king-and-queen diagram does, because each complaint in it is a property of the space. A commenter reported that the site "Completely failed if you search by Artist name", and another searched "holofernes" and got paintings "not-of-but-aesthetically-similar-to Judith beheading Holofernes".

A third user praised the results for Art Deco, and the same geometry accounts for that too.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/vector-embeddings/meaning-space.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/vector-embeddings/meaning-space.narrow.svg" width="288" height="544"><img class="np-has-narrow" src="/static/images/diagrams/vector-embeddings/meaning-space.svg" width="720" height="392" alt="Two texts that both use the word bank go through the same embedding model. Text about bank fees lands among financial concepts, and text about a river bank lands among geographic ones, so a strong model keeps the two senses apart in vector space." loading="lazy" decoding="async"></picture></a>
  <figcaption>A strong model keeps "bank" the institution and "bank" the riverside in different neighbourhoods.</figcaption>
</figure>

## What are vector embeddings?

A vector embedding is a fixed-length list of numbers that a model assigns to a piece of content so that distance between two lists tracks similarity of meaning. Any list of numbers is a vector, and an embedding is a vector produced by a model trained to make those distances useful.

The word covers four kinds of output, and they fail in different ways.

| Type | What is stored | Good at | Weak at |
| --- | --- | --- | --- |
| Dense | One vector per text, a few hundred to a few thousand floats | Paraphrase and topic | Telling near-identical names and codes apart |
| Sparse | One weight per vocabulary term, nearly all zero | Exact terms | Wording the document doesn't share |
| Multi-vector | One vector per token | Phrase-level matching | Storage |
| Binary | One bit per dimension of a dense vector | Memory and speed | Fine ranking |

Multi-vector retrieval comes from [the ColBERT paper](https://arxiv.org/abs/2004.12832) of April 2020, which calls the idea "a late interaction architecture that independently encodes the query and the document". The rest of this page is about dense embeddings and the binary form derived from them, and [hybrid search](/articles/hybrid-search/) covers pairing dense with sparse.

## How are vector embeddings created?

An embedding model reads the whole text, produces one vector per token, and pools those into a single vector of fixed length. To show what comes out, I embedded six short documents and a handful of queries with [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5), a small MIT-licensed model that runs on a laptop CPU.

```python
"""Embed six short texts with a small open model and compare float and binary search."""
import numpy as np
from fastembed import TextEmbedding

docs = [
    "Overdraft fees are charged when a withdrawal takes your bank account below zero.",
    "The river bank eroded after the spring flood and took the footpath with it.",
    "Error ORA-00942: table or view does not exist.",
    "Error ORA-00932: inconsistent datatypes.",
    "The query failed because the table it referenced was missing.",
    "Judith Beheading Holofernes, oil on canvas, Artemisia Gentileschi.",
]
queries = [
    "why was I charged for a negative balance?",
    "ORA-00942",
    "holofernes",
]

model = TextEmbedding("BAAI/bge-small-en-v1.5")
d = np.array(list(model.embed(docs)))
q = np.array(list(model.embed(queries)))
print("dimensions:", d.shape[1], "| vector length:", round(float(np.linalg.norm(d[0])), 3))

print("\ncosine similarity, rows are queries, columns are documents 1 to 6")
sims = q @ d.T
for text, row in zip(queries, sims):
    print(" ".join(f"{v:5.2f}" for v in row), " best:", int(row.argmax()) + 1, "|", text)

print("\nsame search on sign bits (matching bits out of", d.shape[1], ")")
db, qb = d > 0, q > 0
for text, row in zip(queries, qb):
    match = (db == row).sum(axis=1)
    print(" ".join(f"{v:5d}" for v in match), " best:", int(match.argmax()) + 1, "|", text)

print("\nbytes per vector: float32", d.shape[1] * 4, "| binary", d.shape[1] // 8)
```

The script needs `pip install fastembed numpy`, and `python3 embed_demo.py` printed this.

```text
dimensions: 384 | vector length: 1.0

cosine similarity, rows are queries, columns are documents 1 to 6
 0.73  0.45  0.51  0.53  0.57  0.37  best: 1 | why was I charged for a negative balance?
 0.48  0.37  0.75  0.70  0.57  0.46  best: 3 | ORA-00942
 0.43  0.39  0.46  0.45  0.50  0.62  best: 6 | holofernes

same search on sign bits (matching bits out of 384 )
  265   217   229   230   247   194  best: 1 | why was I charged for a negative balance?
  214   204   280   259   228   211  best: 3 | ORA-00942
  211   215   213   220   233   232  best: 5 | holofernes

bytes per vector: float32 1536 | binary 48
```

The first query shares no keyword with the overdraft sentence and still scores 0.73 against it, which is the behaviour people mean by semantic search. The second row shows the weakness: the query is the exact code in the ORA-00942 document, and the ORA-00932 document, a different Oracle error, scores 0.70 against the right answer's 0.75.

A dense model sees two strings that look alike and places them together, which is the wrong instinct for identifiers. The same row ranks the unrelated error above the sentence that describes the fault in plain words.

The run also offers one reading of the artist-name complaint. A name can only pull a document toward a query if the name was part of what got embedded, and one comment in the thread asks the question that decides it: "whether the embeddings come off the images or the catalog text", which the site's About page doesn't answer.

Query and document are embedded separately here, which is what makes the model a [bi-encoder](/glossary/bi-encoder/). The documents can be embedded once and stored, and only the query is embedded at search time.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/vector-embeddings/chunk-embed.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/vector-embeddings/chunk-embed.narrow.svg" width="288" height="720"><img class="np-has-narrow" src="/static/images/diagrams/vector-embeddings/chunk-embed.svg" width="720" height="400" alt="A document is split into chunks, and the embedding model turns each chunk into a vector, which is stored in a vector database with its original text and metadata. A user query is embedded by the same model and searched against the database for its nearest neighbors." loading="lazy" decoding="async"></picture></a>
  <figcaption>Chunks and queries go through the same model, so they land in the same space.</figcaption>
</figure>

## How is similarity measured between two embeddings?

Similarity is the cosine of the angle between the two vectors, which runs from 1 for the same direction to -1 for opposite ones. When vectors have length 1, as the 384-dimension vectors above do, the cosine is the dot product.

OpenAI's [embeddings guide](https://developers.openai.com/api/docs/guides/embeddings) says the same of its models: "OpenAI embeddings are normalized to length 1", so "Cosine similarity and Euclidean distance will result in the identical rankings".

<div class="visual-wrapper">
  <div class="visual-title">Vector Distance and Cosine Similarity</div>
  <div class="visual-container visual-container--fallback">
    <div class="visual-fallback"><img class="visual-fallback-light" src="/static/visuals/cosine-similarity.fallback-light.svg" alt="" loading="lazy"><img class="visual-fallback-dark" src="/static/visuals/cosine-similarity.fallback-dark.svg" alt="" loading="lazy"></div>
    <iframe src="/static/visuals/cosine-similarity.html" title="Interactive cosine similarity: rotate the query vector and read the cosine of its angle to the document" loading="lazy"></iframe>
  </div>
</div>

## Why can't you read a similarity score on its own?

A similarity score means nothing until you know the scores unrelated texts get from the same model, and that floor is high. The run above scored the bank-charge question as low as 0.37 and as high as 0.57 against the five wrong documents, so a rule such as "keep anything over 0.5" would have kept both Oracle errors as answers to it.

The floor is far above what the dimension count predicts. Random directions in a high-dimensional space are almost exactly perpendicular, which a few lines of numpy confirm.

```python
"""Cosine similarity between random directions in 3, 384 and 1,536 dimensions."""
import numpy as np

rng = np.random.default_rng(0)
for dim in (3, 384, 1536):
    x = rng.standard_normal((2000, dim))
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    sims = (x @ x.T)[np.triu_indices(2000, k=1)]
    print(f"{dim:>5} dims: mean {sims.mean():+.3f}  std {sims.std():.3f}  "
          f"largest of {sims.size:,} pairs {sims.max():.3f}")
```

Running `python3 shell_demo.py` printed this.

```text
    3 dims: mean +0.000  std 0.577  largest of 1,999,000 pairs 1.000
  384 dims: mean -0.000  std 0.051  largest of 1,999,000 pairs 0.266
 1536 dims: mean +0.000  std 0.026  largest of 1,999,000 pairs 0.126
```

Among two million pairs of random 384-dimension directions, the closest reached 0.266. The model scored a question about bank charges against an Oracle error at 0.51, so its vectors occupy a narrow part of the space and every score has to be read against that crowding.

An earlier version of this page said a score of 0.7 in 1,536 dimensions "might be noise". Chance alone topped out at 0.126 in two million pairs at that size, and the noise that matters is the model's own floor, which you find by scoring pairs you know are unrelated.

That floor is also the best explanation I have for the cylinder seal. Nearest-neighbour search always returns something, and when nothing in the index is close to a query the top result is whichever item the floor happens to favour.

## Why do queries and documents sit in different parts of the space?

A question and the passage that answers it are different kinds of text, so their embeddings form two populations. Apple's machine learning group built a retrieval method on that observation and [wrote it up on November 5, 2026](https://machinelearning.apple.com/research/faster-retrieval).

The post says that in RAG, queries "arise from short user-generated questions" and the stored keys "represent long, informative, and curated pieces of text, making keys and queries substantially different."

Their KeyNet is a small network trained on sample queries for one fixed database, and it moves each query toward where its answer is likely to be before a standard index searches. On about 2.6 million Natural Questions passages, "reaching 99% recall takes up to ~8× less time with the largest model (0.23 ms vs 1.8 ms for the raw query)".

The cost is in the setup. The network is trained "once, offline, for a fixed database of keys", and the post claims tolerance only of "mild distribution shift in the query patterns".

Embedding vendors handle the same asymmetry with a flag. Cohere's [embeddings documentation](https://docs.cohere.com/docs/embeddings) says "the search query should be embedded by setting input_type="search_query"", and stored passages take `search_document`.

## How many dimensions should an embedding have?

Start with the model's default and shorten only after measuring retrieval on your own queries. OpenAI's guide gives the defaults: "the length of the embedding vector is 1536 for text-embedding-3-small or 3072 for text-embedding-3-large."

Shortening works on models trained for it. The method is [Matryoshka Representation Learning](/glossary/matryoshka-representation-learning/), from [a paper submitted in May 2022](https://arxiv.org/abs/2205.13147) that "encodes information at different granularities and allows a single embedding to adapt to the computational constraints of downstream tasks."

<div class="visual-wrapper">
    <div class="visual-title">Matryoshka: keep the head of the vector</div>
    <div class="visual-container visual-container--tall visual-container--fallback">
        <div class="visual-fallback"><img class="visual-fallback-light" src="/static/visuals/matryoshka-truncation.fallback-light.svg" alt="" loading="lazy"><img class="visual-fallback-dark" src="/static/visuals/matryoshka-truncation.fallback-dark.svg" alt="" loading="lazy"></div>
        <iframe src="/static/visuals/matryoshka-truncation.html" title="Interactive Matryoshka truncation: choose how many leading dimensions to keep" loading="lazy"></iframe>
    </div>
</div>

OpenAI exposes it as a `dimensions` parameter and reports that "a text-embedding-3-large embedding can be shortened to a size of 256 while still outperforming an unshortened text-embedding-ada-002 embedding with a size of 1536." Cohere's embed-v5.0-pro accepts output sizes of 256 up to 2048.

The bge-small model in my run has 384 dimensions, and its model card describes no such training. Cutting its vectors to the first 128 values would discard information the model never arranged to keep at the front.

## What is a binary vector embedding?

A binary vector embedding keeps one bit per dimension, the sign of each float, and compares vectors by counting matching bits. Each vector in the run above shrank from 1,536 bytes to 48, a 32-fold saving.

The same run shows the price. The first two queries kept their best match, and "holofernes" lost it by a single bit, 233 against 232, to a sentence about a missing database table.

That result is why binary search is used as a first pass. Retrieve a generous candidate set on bits, then rescore those candidates with the full vectors, the same two-stage shape as [reranking](/articles/rag-reranking/).

Cohere's API returns compressed forms directly, and its documentation lists `float`, `int8`, `uint8`, `binary` and `ubinary` as embedding types. The same page warns that "because Cohere packages bits as bytes under the hood, the actual length of the vector changes", so 1,024 bits arrive as 128 bytes.

The int8 form is scalar quantization, one byte per dimension, a 4-fold saving. [Product quantization](/glossary/product-quantization/) goes a different way and replaces groups of dimensions with codebook entries.

## Which vector embedding models should you compare?

Compare one hosted default, one model with flexible dimensions and one you can run yourself, on queries with known answers from your own data. The figures below are the vendors' own, read on November 17, 2026.

| Model | Dimensions | Notes from the vendor's page |
| --- | --- | --- |
| OpenAI text-embedding-3-small | 1536, can be shortened | 62.3% on MTEB in OpenAI's table |
| OpenAI text-embedding-3-large | 3072, can be shortened | 64.6% on MTEB in OpenAI's table |
| Cohere embed-v5.0-pro | 256 to 2048 | "support for over 100 languages", binary and int8 output |
| BAAI/bge-small-en-v1.5 | 384 | MIT license, the model run above |

A public leaderboard score won't settle the choice. My six-document run is no benchmark either, and what it shows is the method: embed queries and documents with each candidate, then read the scores of the wrong documents as carefully as the right ones.

## Is there a universal geometry of embeddings?

There is evidence that different models arrange meaning in similar shapes. [A paper from May 2025](https://arxiv.org/abs/2505.12540) by Rishi Jha and colleagues describes "the first method for translating text embeddings from one vector space to another without any paired data, encoders, or predefined sets of matches."

The practical consequence is about security. The authors write that "An adversary with access only to embedding vectors can extract sensitive information about the underlying documents", so a vector store deserves the same access controls as the text it was built from.
