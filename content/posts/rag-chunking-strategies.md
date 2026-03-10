---
title: "RAG Chunking Strategies: What the Research Actually Shows"
date: 2026-03-14
description: "Chunk size and strategy affect RAG accuracy more than model choice in most systems. Here's what the research shows about fixed-size, semantic, and contextual approaches."
tags: [ai, rag, llm, infrastructure]
status: published
---

Every RAG tutorial starts with chunking and spends two paragraphs on it. Chunk your documents, embed them, retrieve them. The parameters passed as defaults. The chunk size of 512, the overlap of 50, the strategy of split-on-newlines. Then the tutorial moves on to the parts that feel more interesting.

Chunking is where most RAG systems are quietly broken.

The retrieval quality ceiling for any RAG system is set by chunking quality. A great embedding model retrieving bad chunks will consistently underperform a mediocre model retrieving good ones. The [LlamaIndex benchmarks from 2024](https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex-6207e5d3fec5) showed retrieval precision varying by over 30 percentage points across chunking strategies on the same corpus. That's not a marginal difference. That's the difference between a system that works and one that doesn't.

Here's what I understand about the main approaches and what each trades away.

## Fixed-size chunking: the default that causes most problems

Fixed-size chunking splits text at token or character boundaries, typically with some overlap. LangChain's `RecursiveCharacterTextSplitter` with chunk_size=1000 and chunk_overlap=200 is probably the most common RAG configuration deployed in production today.

The problem is mechanical. Text has semantic units. A sentence, a paragraph, a section. Fixed-size splitting ignores all of them. A chunk boundary can land in the middle of a code example, between a function definition and its parameters, or cutting off an explanation at the point it becomes useful.

The overlap parameter exists to patch this. Repeating 200 characters at the boundary gives adjacent chunks some shared context. It helps. It doesn't solve the underlying issue. You're still encoding fragments that may not make sense independently.

Where fixed-size chunking makes sense: high-volume ingestion pipelines where speed matters, corpora with highly uniform structure (rows of tabular data, for instance), or early-stage prototypes where you want to move fast and tune later. Understand what you're trading when you choose it.

## Recursive text splitting: better boundary detection, same core problem

LangChain's recursive character splitter improves on pure fixed-size chunking by attempting to split at semantic boundaries in order: paragraph breaks first, then sentence breaks, then word breaks, then characters. It degrades gracefully as chunk targets force smaller splits.

For most natural language documents, this produces meaningfully better chunks than naive fixed-size splitting. Paragraphs stay together when they fit. The overlap still patches rough edges.

It doesn't solve the core problem: the splitter has no understanding of content. A 400-token paragraph that covers two distinct topics will stay in a single chunk. Two tightly related sentences on opposite sides of a paragraph break will end up in different chunks. The splitting logic is syntactic, not semantic.

For general-purpose RAG over mixed document types, recursive splitting with tuned parameters is a reasonable default. The parameters that actually matter: chunk size relative to your embedding model's context window, and overlap as a fraction of chunk size (20-25% is a reasonable target, not a fixed number).

## Semantic chunking: embedding-based boundary detection

Semantic chunking uses embedding similarity to find topic boundaries. The approach: embed each sentence (or small paragraph), compute similarity between adjacent embeddings, and split where similarity drops sharply. A sudden shift in embedding space indicates a topic transition.

Greg Kamradt's [chunking experiments](https://github.com/FullStackRetrieval-com/RetrievalAugmentedGeneration/blob/main/LearnRAG/5_Levels_Of_Text_Splitting.ipynb) formalized this and showed it produces chunks with more coherent content than fixed-size or recursive approaches on narrative and technical documents. Each chunk is semantically unified because the splits happen where topics actually change.

The cost is latency. Every sentence needs to be embedded during ingestion, which is slower and more expensive than character counting. For a 100-page technical document, this is manageable. For a corpus of millions of documents, it's a bottleneck that changes the economics.

There's also a calibration problem. The similarity threshold for splits is a hyperparameter with no obvious correct value. Set it too high and you split aggressively, producing many small chunks with poor context. Set it too low and you produce large, heterogeneous chunks. The right value depends on corpus characteristics. It needs tuning per domain.

For corpora with natural topical structure (technical documentation, long-form articles, research papers), semantic chunking produces noticeably better retrieval at the cost of more complex ingestion. Worth the investment for high-value corpora where retrieval precision matters.

## Parent-child chunking: the architecture I find most interesting

Parent-child chunking (also called small-to-big retrieval or hierarchical chunking) addresses a real tension in RAG: embedding quality and retrieval precision improve with smaller chunks, but generated responses improve with more context.

The implementation: split your document at two granularities. Small "child" chunks (64-128 tokens) for embedding and retrieval. Larger "parent" chunks (512-2048 tokens) for context. When a child chunk is retrieved as relevant, you serve the parent chunk to the LLM.

The retrieval step benefits from the specificity of small chunks. A 100-token passage about a specific API parameter will be retrieved precisely when someone asks about that parameter. A 1000-token parent chunk containing that passage gives the LLM enough surrounding context to generate a useful answer.

LlamaIndex implements this as their `ParentDocumentRetriever`. LangChain has equivalent functionality. The indexing complexity is higher: you maintain two chunk sizes and a mapping between them. For most systems, the retrieval quality improvement justifies it.

## Contextual retrieval: Anthropic's approach to the lost context problem

Late 2024, Anthropic published their [contextual retrieval approach](https://www.anthropic.com/news/contextual-retrieval). The core insight: chunks lose context when separated from their source document. A chunk that says "The quarterly revenue was $2.3B, up 15% year-over-year" is useless without knowing which company, which quarter.

Their solution: before embedding each chunk, prepend a brief AI-generated summary explaining where the chunk sits in the document. Something like: "This chunk is from the Q3 2025 earnings report for Acme Corp. It discusses revenue performance." The chunk is then embedded with this context included.

Anthropic's benchmarks showed a 49% reduction in retrieval failures compared to standard chunking, and a 67% reduction when combined with BM25 hybrid search. Those numbers are from their own evaluation, on their own test cases. Independent reproduction varies. The approach is sound regardless of the exact improvement.

The cost is real: you need an LLM call per chunk to generate the contextual prefix. For a corpus of 100,000 chunks, that's 100,000 API calls at ingestion time. Anthropic's prompt caching reduces this cost significantly when the document structure is reused, but it changes the economics of ingestion substantially.

For high-stakes RAG applications where retrieval quality directly affects outcomes (customer support, legal research, medical information), the cost is worth it. For general knowledge bases and internal wikis, the standard approaches are usually sufficient.

## The parameters that actually matter

Chunk size interacts with everything. The embedding model's effective context window sets the upper bound. Models like OpenAI's text-embedding-3-small perform well up to about 512 tokens per chunk. Above that, the embedding starts averaging over too much content and precision drops. Below about 64 tokens, you lose too much context. The 128-512 token range is the empirically validated sweet spot for most embedding models.

Overlap should be proportional. Fixed overlap values (like 200 characters) don't scale across different chunk sizes. Aim for 10-20% of chunk size.

Metadata matters as much as content. Source document, section headers, page numbers, document type. When you retrieve a chunk, that metadata can be used for filtering and can be passed to the LLM alongside the chunk content. Most systems underuse metadata.

## What I actually recommend for new RAG systems

Start with recursive text splitting at 512 tokens with 10% overlap. Measure retrieval precision against a held-out evaluation set with 20-50 representative queries. Know your baseline.

Switch to parent-child if you find that retrieved chunks are precise but response quality is suffering from lack of context. Switch to semantic chunking if you have long documents with clear topic shifts and retrieval precision is the bottleneck. Add contextual retrieval only if you've established that chunk-level context loss is your primary failure mode, and only if the ingestion cost is acceptable.

The evaluation step is non-negotiable. Chunking intuitions built on toy datasets don't transfer. The only way to know what's working is to measure it on your actual corpus with your actual queries.
