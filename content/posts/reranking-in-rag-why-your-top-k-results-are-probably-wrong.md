---
date: 2026-03-21
description: Vector databases return results based on semantic similarity. I explain
  why that is rarely enough for production RAG and how a cross-encoder reranker fixes
  the problem.
status: published
tags:
- ai
- rag
- vector-search
- infrastructure
title: 'Reranking in RAG: Why Your Top-K Results Are Probably Wrong'
---

Vector databases are powerful tools for building retrieval-augmented generation systems. Plenty of engineering teams I have worked with assume that dropping text into an embedding model and running a cosine similarity search is the entire retrieval job. You retrieve the top five results. You inject them into your prompt. You expect the language model to synthesize a perfect answer.

That architecture almost always breaks down in production. Whenever a system relies solely on single-stage dense retrieval, I start seeing the same class of accuracy issue: the top-k results from a vector database come back semantically related to the query but entirely useless for the user's actual question. A search for a refund policy returns three pages about shipping policy, because both live in the same neighborhood of "customer policy" text.

Let me explain exactly why this happens and how you fix it. The repair is a reranking stage added to your retrieval pipeline. To use it well, you need to understand the structural limits of bi-encoder models and the compute tradeoffs of cross-encoder architectures.

## The structural limitation of dense embeddings

Every document you store in a vector database passes through an embedding model. I discussed the geometry of these spaces in [Embedding models: the geometry of meaning across OpenAI, Cohere, and open-source](/blog/embedding-models-compared/). The model compresses the entire semantic meaning of a chunk of text into a single array of floating-point numbers.

<div class="visual-wrapper">
  <div class="visual-title">Bi-Encoder Architecture</div>
  <div class="visual-container">
    <iframe src="/static/visuals/bi-encoder-arch.html" title="Bi-Encoder isolated embedding architecture" loading="lazy"></iframe>
  </div>
</div>

Your query undergoes the exact same process, and the database then calculates the distance between the query vector and the document vectors.

A fundamental problem hides in that setup. The embedding model evaluates the query and the document in total isolation, so it never sees the two together. We call this a bi-encoder architecture. The model generates a vector for the query, generates vectors for the documents, and the database compares the vectors after the fact.

Such an approach is extremely fast. You pre-compute every document embedding once, embed only the query at runtime, and the distance calculation costs almost nothing. Think of two people describing a movie to a third party in separate rooms: neither hears the other, and you are left guessing whether they watched the same film by comparing their notes. That is the bi-encoder. Two notes, compared, with nobody in the room who read both at once.

Speed buys that isolation at the cost of deep reasoning. The model compresses everything into one fixed-size representation, and the precise relationships between specific words in the query and specific words in the document get flattened out during that compression.

Picture a question like "how to configure a timeout for the postgres connection pool." The database might hand back a document about "how to configure a timeout for the redis connection pool." Both documents share massive overlap. They both talk about configuring timeouts for connection pools, so the embedding model plots them as near neighbors in vector space.

Your language model then receives the redis document and either hallucinates an answer or claims it cannot find the information. Retrieval failed because semantic similarity is not the same thing as relevance.

## Enter the cross-encoder

I reach for cross-encoders to solve this precise issue. A cross-encoder is a different type of machine learning model, and it does not produce standalone embeddings at all.

What it takes instead is two pieces of text simultaneously. You feed it the query and a single document as one combined input, and the model processes them together through its attention layers.

Every token in the query can attend to every token in the document. The model spots exact keyword matches, follows the logical connection between the two texts, and outputs a single number that represents a highly accurate relevance score. To extend the earlier picture: the cross-encoder is the one reviewer who sits down with both the question and the candidate answer in front of them and reads them side by side before scoring.

<div class="visual-wrapper">
  <div class="visual-title">Cross-Encoder Architecture</div>
  <div class="visual-container">
    <iframe src="/static/visuals/cross-encoder-arch.html" title="Cross-Encoder joint attention architecture" loading="lazy"></iframe>
  </div>
</div>

You cannot run a cross-encoder over your whole corpus for the initial search, and the reason is purely cost. Scoring a pair means pushing both texts through a transformer at query time. Do that for a million documents on a single user search and you are looking at hours, not milliseconds.

Both approaches have to work together. I build two-stage retrieval systems where the bi-encoder casts the initial wide net and the cross-encoder does the final precision sorting on a much smaller set.

## Designing a two-stage retrieval pipeline

The architecture looks like a funnel that starts with your massive corpus of documents. Wide at the top, narrow at the bottom, and each stage trades breadth for precision.

Stage one runs on your standard vector database. You embed the user's query with a fast bi-encoder and run a vector search, but you do not ask for the top five results. You ask for a much larger number. I typically pull the top one hundred or two hundred chunks from the database.

Somewhere inside those one hundred chunks sits the correct answer. The order is the problem. The right chunk might be sitting at position forty-seven because the bi-encoder missed a subtle keyword connection that pushed three near-duplicates above it.

Stage two brings in the cross-encoder. You pair the original query with each of the one hundred chunks from stage one and send those one hundred pairs to your reranker model.

<div class="visual-wrapper">
  <div class="visual-title">Bi-Encoder vs Cross-Encoder Sorting</div>
  <div class="visual-container">
    <iframe src="/static/visuals/reranking-pipeline.html" title="Two Stage Reranking Pipeline Animation" loading="lazy"></iframe>
  </div>
</div>

The reranker scores each pair, and you re-sort the one hundred chunks by those new scores.

From that newly sorted list you take only the top five or ten chunks and pass them to your language model for the final generation step. The dangers of passing too much context I covered in [Your Context Window Has a Middle. Models Don't Read It.](/blog/llm-context-windows-explained/). Handing the model a small, highly accurate set of chunks is what carries generation quality.

## Evaluating the latency tradeoff

Adding a reranker introduces new latency to your pipeline, and I always measure the cost of this extra compute step before shipping it.

Retrieving one hundred vectors from a database takes milliseconds. Embedding the query takes perhaps fifty milliseconds. Your initial retrieval is very fast.

The cross-encoder is where the clock starts ticking. Running one hundred pairs through it is heavy transformer inference at runtime, and calling an external API like Cohere's Rerank endpoint adds network latency on top of inference time. That single step can easily push hundreds of milliseconds onto your total response, the kind of pause a user feels as a beat of hesitation before the answer starts streaming.

<div class="visual-wrapper">
  <div class="visual-title">Latency Tradeoff Comparison</div>
  <div class="visual-container">
    <iframe src="/static/visuals/latency-tradeoff.html" title="Latency chart comparing vector search to reranking" loading="lazy"></iframe>
  </div>
</div>

Accuracy and speed have to be balanced against each other. When latency becomes a hard bottleneck, say a chat interface where anything over a second feels broken, I cut the initial retrieval size from one hundred down to fifty chunks. Hosting a smaller open-source reranker on your own infrastructure also kills the network round trip entirely.

Models like `bge-reranker-base` or `cross-encoder/ms-marco-MiniLM-L-6-v2` run efficiently on small GPUs or even modern CPUs, which is why I frequently deploy them directly alongside the application server rather than behind a separate service.

Whether the latency penalty earns its keep is the obvious question. Every time I add a reranker, the retrieval metrics climb in a way I can see in the numbers. Mean Reciprocal Rank (MRR) and Normalized Discounted Cumulative Gain (NDCG) both jump. More to the point, the system stops handing users confident answers built on documents that were only loosely related to what they asked.

## Dealing with keyword exactness

Exact numbers, acronyms, and specific identifiers are where vector search quietly falls apart, and I watch it fail constantly in technical documentation search.

Take a user searching for error code `E-4048`. The embedding model might split that string into several tokens, and the resulting vector represents a vague concept of "an error code" rather than that exact one. The search then returns documents about `E-4049` or `E-4047`, because to the bi-encoder they look semantically identical.

A cross-encoder fixes this on contact. Seeing `E-4048` in the query, it goes looking for that exact string in the document and treats a one-character difference as the relevance-killer it actually is.

<div class="visual-wrapper">
  <div class="visual-title">Evaluating Keyword Exactness</div>
  <div class="visual-container">
    <iframe src="/static/visuals/keyword-exactness.html" title="Comparison of vector similarity vs reranker score for exact keywords" loading="lazy"></iframe>
  </div>
</div>

Improving the first stage with hybrid search helps here too. I often combine vector search with standard keyword search (BM25) to build that initial list of one hundred candidates, and the reranker then evaluates candidates from both sources. Pulling from both lists guarantees that exact keyword matches reach the reranking pool even when vector search missed them entirely.

## Comparing models and providers

The market offers excellent options for reranking, and I have tested several across different production workloads.

Cohere ships a strong commercial API. Their `rerank-english-v3.0` and `rerank-multilingual-v3.0` models give you good accuracy out of the box. You send a query and a list of texts, they return the sorted indices and scores, and the integration is done in an afternoon.

Open-source options ask for more infrastructure work and pay you back with better unit economics at scale. The BAAI general embedding (BGE) family includes several capable rerankers, and I lean on `bge-reranker-large` for high-accuracy local deployments where I want to avoid per-call API fees.

<div class="visual-wrapper">
  <div class="visual-title">Comparing Models and Providers</div>
  <div class="visual-container">
    <iframe src="/static/visuals/models-providers.html" title="Comparison between commercial API and open source rerankers" loading="lazy"></iframe>
  </div>
</div>

A standard language model can also act as a reranker. You drop the query and the document into a prompt and ask the model to output a score from one to ten. I generally avoid this. Generative models are slow, parsing a number out of free-form text is fragile (one stray sentence of preamble and your regex breaks), and dedicated cross-encoders are smaller, faster, and trained for exactly this scoring task.

## Why you cannot skip the reranker

A recurring argument I hear is that newer, larger embedding models solve relevance natively. Teams point at the jump from a 384-dimensional vector to a 3072-dimensional vector and conclude the second stage is now optional.

Dimensionality does not touch the architecture flaw, though, and I have watched teams learn this the expensive way. A bi-encoder still compresses two texts independently. Give it eight times the dimensions and you are still asking it to guess a relationship without ever looking at the two items together. A bigger photograph of two rooms does not let you hear a conversation that never happened.

<div class="visual-wrapper">
  <div class="visual-title">The Problem with Dimension Scaling</div>
  <div class="visual-container">
    <iframe src="/static/visuals/dimension-scaling.html" title="Scaling vector dimensions does not solve isolated evaluation" loading="lazy"></iframe>
  </div>
</div>

The other argument I hear leans on massive context windows. The pitch is that you can pass all one hundred retrieved chunks straight to the language model and let it sort them out. I dug into that approach when comparing [Fine-Tuning vs RAG](/blog/rag-vs-fine-tuning/). Stuffing the context window grows your inference cost linearly and drags latency along with it. Time to first token degrades noticeably once you are sending eighty thousand tokens on every request, the difference between an answer that appears instantly and one the user waits on.

Buried information also slips past the model in that much context. Five highly relevant chunks consistently produce better generation than one hundred marginally related ones, because the model is not forced to hunt for the signal you already could have isolated.

## Implementing the architecture

Start by mapping out your current retrieval pipeline. Log the initial retrieved chunks alongside their vector distance scores, and run a handful of real user queries through it. You will quickly catch the document you actually wanted sitting at position eight or twelve, below the five chunks you were shipping to the model.

Adding a reranker costs you very few lines of code. Frameworks ship native wrappers for it, though I prefer writing the integration by hand so I control the exact number of candidates passed between stages.

The flow itself is short. You take the output of your vector database client, format it into a list of strings, and pass that list plus the query to your reranker. You slice the top results off the response and hand them to your prompt builder.

<div class="visual-wrapper">
  <div class="visual-title">Two-Stage Implementation Flow</div>
  <div class="visual-container">
    <iframe src="/static/visuals/implementation-flow.html" title="Code level pipeline steps for reranking" loading="lazy"></iframe>
  </div>
</div>

The effect on reliability runs deep. With crisp, relevant context in front of it, the language model hallucinates less and the whole system reads as noticeably sharper to the person on the other end.

Cosine similarity alone will not carry a production RAG system. Vector distance is a great mechanism for filtering a million documents down to a hundred candidates, and a poor mechanism for ranking those hundred in the order a human would. Two stages, every time, so the right information actually reaches the generation step.