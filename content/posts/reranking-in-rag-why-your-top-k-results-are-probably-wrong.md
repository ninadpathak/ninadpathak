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
title: 'Reranking in Rag: Why Your Top-k Results Are Probably Wrong'
---

Vector databases are powerful tools for building retrieval-augmented generation systems. I have seen many engineering teams assume that dropping text into an embedding model and performing a cosine similarity search is the entire retrieval job. You retrieve the top five results. You inject them into your prompt. You expect the language model to synthesize a perfect answer.

That architecture almost always breaks down in production. I consistently notice accuracy issues when systems rely solely on single-stage dense retrieval. The top-k results from a vector database are often semantically related to the query but entirely irrelevant to the user's actual question.

I want to explain exactly why this happens and how you can fix it. The solution requires adding a reranking stage to your retrieval pipeline. You will need to understand the structural limitations of bi-encoder models and the computational tradeoffs of cross-encoder architectures.

## The structural limitation of dense embeddings

Every document you store in a vector database passes through an embedding model. I discussed the geometry of these spaces in [Embedding models: the geometry of meaning across OpenAI, Cohere, and open-source](/blog/embedding-models-compared/). The model compresses the entire semantic meaning of a chunk of text into a single array of floating-point numbers.

<div class="visual-wrapper">
  <div class="visual-title">Bi-Encoder Architecture</div>
  <div class="visual-container">
    <iframe src="/static/visuals/bi-encoder-arch.html" title="Bi-Encoder isolated embedding architecture" loading="lazy"></iframe>
  </div>
</div>

The query undergoes the exact same process. The database then calculates the distance between the query vector and the document vectors.

A fundamental problem exists here. The embedding model evaluates the query and the document in total isolation. The model never sees the query and the document together. We call this a bi-encoder architecture. The model generates a vector for the query. The model generates vectors for the documents. The database compares the vectors.

Such an approach is extremely fast. You can pre-compute all document embeddings. You only need to embed the query at runtime. The distance calculation is computationally cheap.

Speed comes at the cost of deep reasoning. The model compresses everything into one fixed-size representation. Nuanced relationships between specific words in the query and specific words in the document get lost during that compression.

You ask a question about "how to configure a timeout for the postgres connection pool." The database might return a document about "how to configure a timeout for the redis connection pool." Both documents share massive semantic overlap. They both talk about configuring timeouts for connection pools. The embedding model plots them very close together in vector space.

The language model receives the redis document. The language model generates a hallucinated answer or states it cannot find the information. Your retrieval system failed because semantic similarity does not equal relevance.

## Enter the cross-encoder

I implement cross-encoders to solve this precise issue. A cross-encoder is a different type of machine learning model. It does not produce standalone embeddings.

A cross-encoder takes two pieces of text simultaneously. You feed it the query and a single document as a single input. The model processes them together through its attention layers.

Every token in the query can attend to every token in the document. The model can identify exact keyword matches. The model can understand complex logical connections between the two texts. The model outputs a single number. That number represents a highly accurate relevance score.

<div class="visual-wrapper">
  <div class="visual-title">Cross-Encoder Architecture</div>
  <div class="visual-container">
    <iframe src="/static/visuals/cross-encoder-arch.html" title="Cross-Encoder joint attention architecture" loading="lazy"></iframe>
  </div>
</div>

You cannot use a cross-encoder for your initial search. I will explain why. Running a cross-encoder requires passing the query and the document through a transformer model at runtime. Doing that for a million documents would take hours or days for a single search.

We must combine both approaches. I build two-stage retrieval systems. The bi-encoder handles the initial wide net. The cross-encoder handles the final precision sorting.

## Designing a two-stage retrieval pipeline

The architecture looks like a funnel. You start with your massive corpus of documents.

Stage one uses your standard vector database. You take the user's query and embed it using a fast bi-encoder. You run a vector search. You do not ask for the top five results. You ask for a much larger number. I typically retrieve the top one hundred or two hundred chunks from the database.

Those one hundred chunks contain the correct answer somewhere inside them. The order of those one hundred chunks is likely wrong. The correct answer might sit at position forty-seven because the bi-encoder missed a subtle keyword connection.

Stage two applies the cross-encoder. You take the original query. You pair it with each of the one hundred chunks retrieved in stage one. You send those one hundred pairs to your reranker model.

<div class="visual-wrapper">
  <div class="visual-title">Bi-Encoder vs Cross-Encoder Sorting</div>
  <div class="visual-container">
    <iframe src="/static/visuals/reranking-pipeline.html" title="Two Stage Reranking Pipeline Animation" loading="lazy"></iframe>
  </div>
</div>

The reranker scores each pair. You sort the one hundred chunks based on these new scores.

You now take the top five or ten chunks from that newly sorted list. You pass only those highly relevant chunks to your language model for the final generation step. I covered the dangers of passing too much context in [Your Context Window Has a Middle. Models Don't Read It.](/blog/llm-context-windows-explained/). Providing a small, highly accurate set of chunks is critical for generation quality.

## Evaluating the latency tradeoff

Adding a reranker introduces new latency to your pipeline. I always measure the impact of this additional compute step.

Retrieving one hundred vectors from a database takes milliseconds. Embedding the query takes perhaps fifty milliseconds. Your initial retrieval is very fast.

Running one hundred pairs through a cross-encoder takes time. You are performing heavy transformer inference at runtime. Calling an external API like Cohere's Rerank endpoint will add network latency plus inference time. That can easily add hundreds of milliseconds to your total response time.

<div class="visual-wrapper">
  <div class="visual-title">Latency Tradeoff Comparison</div>
  <div class="visual-container">
    <iframe src="/static/visuals/latency-tradeoff.html" title="Latency chart comparing vector search to reranking" loading="lazy"></iframe>
  </div>
</div>

You must balance accuracy against speed. I sometimes reduce the initial retrieval size to fifty chunks if latency becomes a critical bottleneck. You can also host a smaller, open-source reranker model on your own infrastructure to eliminate network round trips.

Models like `bge-reranker-base` or `cross-encoder/ms-marco-MiniLM-L-6-v2` run very efficiently on small GPUs or even modern CPUs. I frequently deploy these models directly alongside the application server.

You might wonder if the latency penalty is worth it. I consistently measure massive improvements in retrieval metrics after adding a reranker. Metrics like Mean Reciprocal Rank (MRR) or Normalized Discounted Cumulative Gain (NDCG) jump significantly. The user experience improves because the system stops providing confidently wrong answers based on loosely related documents.

## Dealing with keyword exactness

Vector search struggles with exact numbers, acronyms, and specific identifiers. I see this fail constantly in technical documentation search.

A user searches for error code `E-4048`. The embedding model might split that into several tokens. The resulting vector represents a vague concept of an error code. The search returns documents containing `E-4049` or `E-4047` because they look semantically identical to the bi-encoder.

The cross-encoder fixes this immediately. The cross-encoder sees `E-4048` in the query and looks for it specifically in the document. It understands that a one-character difference changes the relevance entirely.

<div class="visual-wrapper">
  <div class="visual-title">Evaluating Keyword Exactness</div>
  <div class="visual-container">
    <iframe src="/static/visuals/keyword-exactness.html" title="Comparison of vector similarity vs reranker score for exact keywords" loading="lazy"></iframe>
  </div>
</div>

You can also improve the first stage by using hybrid search. I often combine vector search with standard keyword search (BM25) to generate that initial list of one hundred candidates. The reranker then evaluates candidates from both sources. This ensures that exact keyword matches make it into the reranking pool even if the vector search missed them entirely.

## Comparing models and providers

The market provides excellent options for reranking. I have tested several approaches across different production workloads.

Cohere provides a fantastic commercial API. Their `rerank-english-v3.0` and `rerank-multilingual-v3.0` models offer exceptional accuracy out of the box. You send them your query and a list of texts. They return the sorted indices and scores. The integration takes minutes.

Open-source options require more infrastructure work but offer better unit economics at scale. The BAAI general embedding (BGE) family includes several powerful rerankers. I rely on `bge-reranker-large` for high-accuracy local deployments.

<div class="visual-wrapper">
  <div class="visual-title">Comparing Models and Providers</div>
  <div class="visual-container">
    <iframe src="/static/visuals/models-providers.html" title="Comparison between commercial API and open source rerankers" loading="lazy"></iframe>
  </div>
</div>

You can also use a standard language model as a reranker. You pass the query and the document into a prompt and ask the model to output a score from one to ten. I generally avoid this approach. Generative models are slow. Parsing their output is fragile. Dedicated cross-encoders are smaller, faster, and trained specifically for the scoring task.

## Why you cannot skip the reranker

I hear arguments that newer, larger embedding models solve the relevance problem natively. Some teams believe that moving from a 384-dimensional vector to a 3072-dimensional vector eliminates the need for a second stage.

My experience shows that dimensionality does not solve the fundamental architecture flaw. A bi-encoder still compresses two texts independently. You can give it more dimensions. You are still asking it to predict a relationship without looking at the two items together.

<div class="visual-wrapper">
  <div class="visual-title">The Problem with Dimension Scaling</div>
  <div class="visual-container">
    <iframe src="/static/visuals/dimension-scaling.html" title="Scaling vector dimensions does not solve isolated evaluation" loading="lazy"></iframe>
  </div>
</div>

I also hear arguments that massive context windows solve the problem. You might think you can just pass all one hundred retrieved chunks directly to the language model. You let the language model sort it out. I analyzed this approach when comparing [Fine-Tuning vs RAG](/blog/rag-vs-fine-tuning/). Stuffing the context window increases your inference costs linearly. It also increases latency dramatically. Time to first token degrades when you send eighty thousand tokens on every request.

The language model will also lose track of information buried in that massive context. Providing five highly relevant chunks always yields better generation than providing one hundred marginally related chunks.

## Implementing the architecture

You should map out your current retrieval pipeline. I recommend logging the initial retrieved chunks and their vector distance scores. You will quickly notice that the document you actually want often sits below the top five results.

You can add a reranker with very few lines of code. Frameworks provide native wrappers for this. I prefer writing the integration manually to control the exact number of candidates passed between stages.

You take the output of your vector database client. You format it into a list of strings. You pass that list and the query to your reranker. You slice the top results from the response. You pass those to your prompt builder.

<div class="visual-wrapper">
  <div class="visual-title">Two-Stage Implementation Flow</div>
  <div class="visual-container">
    <iframe src="/static/visuals/implementation-flow.html" title="Code level pipeline steps for reranking" loading="lazy"></iframe>
  </div>
</div>

The impact on system reliability is profound. The language model receives crisp, relevant context. Hallucinations drop. The system feels much more intelligent to the end user.

You cannot build a production RAG system relying solely on cosine similarity. The math of vector spaces provides a great filtering mechanism. The math of vector spaces provides a terrible ranking mechanism. I always build with a two-stage pipeline to ensure the right information actually reaches the generation step.