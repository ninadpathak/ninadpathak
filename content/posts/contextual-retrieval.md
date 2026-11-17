---
category: rag
primary_query: contextual retrieval
siblings:
- hybrid-search
- rag-reranking
bridges:
- slug: llm-context-windows
  reason: Every retrieved token costs latency and money.
date: 2026-03-26
description: 'Contextual Retrieval (contextual RAG) prepends a model-written note to each chunk before indexing. What Anthropic measured, what it costs, and where it still fits.'
status: published
work_note: "I write developer documentation and technical articles for AI and developer-tool companies. I'm Ninad Pathak, and I work by one rule, which is to run the product before I write about it. [Work with me](/services/)."
title: How Anthropic's Contextual Retrieval Changes RAG Architecture
updated: '2026-11-17'
slug: contextual-retrieval
video: contextual-retrieval
---

Anthropic took a chunk like `"The company's revenue grew by 3% over the previous quarter."`, asked Claude to explain that chunk using the full document, and prepended the explanation before indexing it. That step is Contextual Retrieval, often searched for as contextual RAG, and in [the writeup Anthropic published on September 19, 2024](https://www.anthropic.com/engineering/contextual-retrieval) it cut top-20 retrieval failure by **49%** once contextual embeddings were paired with contextual BM25.

The mechanism changes the chunk before any query runs, where nearly all RAG tuning happens at query time. I still think that is the right end of the pipeline to push on, and coding agents have since changed my mind about which corpora it is for.

It works on the indexing stage of the [RAG pipeline](/articles/rag/).

## What is Contextual Retrieval?

Contextual Retrieval adds one step after chunking: a model reads the full document and a single chunk, writes a short note saying where the chunk sits, and that note is prepended to the chunk before it is embedded and before the BM25 index is built. Anthropic's post puts the note at "usually 50-100 tokens".

The step exists because a chunk is rarely a clean unit of knowledge. Cut the revenue sentence away from its filing and it loses the company and the quarter, so a query for "Acme third-quarter revenue" has nothing obvious to match.

The same thing happens to a setup step that loses the product it configures, and to a paragraph about retries that reads the same whether it belongs to the payments worker or the email queue. [Semantic chunking](/glossary/semantic-chunking/) moves the boundary to a change in meaning, and [late chunking](/glossary/late-chunking/) contextualizes tokens before pooling them, and neither writes the missing frame back in as text.

Both retrievers gain from the note. Embeddings get document-level framing, BM25 gets vocabulary the raw chunk never contained, and Anthropic names the two halves Contextual Embeddings and Contextual BM25.

That is why I read it as better input for [hybrid search](/articles/hybrid-search/) and never as a replacement for it. It is also the cleanest example I know of [context engineering](/glossary/context-engineering/) done at index time.

## What Anthropic's benchmark shows

Anthropic's result is a stack of separate reductions in retrieval failure, measured as 1 minus recall@20 and averaged across codebases, fiction, ArXiv papers and science papers.

| Setup | Top-20 retrieval failure | Reduction |
| --- | --- | --- |
| Standard embeddings and BM25 | 5.7% | Baseline |
| Contextual Embeddings | 3.7% | 35% |
| Contextual Embeddings and Contextual BM25 | 2.9% | 49% |
| Both, plus reranking from the top 150 down to the top 20 | 1.9% | 67% |

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/contextual-retrieval/retrieval-failure.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/contextual-retrieval/retrieval-failure.narrow.svg" width="288" height="432"><img class="np-has-narrow" src="/static/images/diagrams/contextual-retrieval/retrieval-failure.svg" width="720" height="472" alt="Reduction in top-20 retrieval failure, measured as 1 minus recall at 20, in Anthropic's contextual retrieval tests: 35% from contextual embeddings alone, 49% once contextual BM25 joins, and 67% once reranking joins too. Each tile is 5 percentage points." loading="lazy" decoding="async"></picture></a>
  <figcaption>From Anthropic's contextual retrieval writeup. Each layer still helps on top of the one before it; each tile is 5 points.</figcaption>
</figure>

The breakdown is worth more than the headline because it shows each layer still helping on top of the last. Anthropic did not claim that one chunking trick made the rest of the stack irrelevant, and the full per-domain numbers are in [Appendix II](https://assets.anthropic.com/m/1632cded0a125333/original/Contextual-Retrieval-Appendix-2.pdf).

The corpora are Anthropic's, and the averages use the embedding configuration that performed best in 2024, so a 49% measured there will not carry over cleanly to a support archive or an internal wiki.

## Prompt caching makes the cost bearable

Without [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), contextualizing every chunk resends the same full document once per chunk. Anthropic points to caching as the fix, describing it as "reducing latency by > 2x and costs by up to 90%".

The expense lands at ingestion, and query-time retrieval barely changes unless you add reranking. Every chunk still gets longer, which raises embedding cost, BM25 index size and storage, so the bill is worth paying where a retrieval miss hurts, such as a support bot citing the wrong refund policy.

Static prefixes should be reused, which is the same rule that governs [context windows](/articles/llm-context-windows/) at generation time.

## What changed since 2024: code left, prose stayed

The earlier version of this article called code the cleanest use case, on the reasoning that a helper named `format()` loses its identity faster than any paragraph. Coding agents answered that problem a different way, by not chunking at all.

Kapa's Matteo Bortoletto and Janis Fluri [wrote on October 26, 2026](https://www.kapa.ai/blog/retrieval-bottleneck) that "Models have become good enough at using grep that the semantic search path no longer helps coding agents in a meaningful way." Their explanation is that in code "identifiers are distinctive and spelled the same way everywhere", so a capable model can refine an exact pattern until it lands on the file.

I was wrong about code, or at least right only until coding agents learned to grep. The argument got stronger for the corpora the same post says grep can't handle, where documentation, tickets and forum threads describe one concept in several vocabularies.

That post also changes the order of checks before adopting the technique. Contextual Retrieval improves finding, and Kapa reports that finding is now half the problem: "Today, about half of the failed test cases are caused by search."

The other half fail after search, when the right chunk was retrieved and then cut. The last row of Anthropic's own table said as much in 2024, since reranking cut the remaining failures by about a third, and my [reranking guide](/articles/rag-reranking/) covers that stage.

## When to skip Contextual Retrieval

Skip it when the corpus is small, already self-describing or constantly changing. Anthropic sets the first threshold itself: under 200,000 tokens "you can just include the entire knowledge base in the prompt".

- Chunks that are already self-contained gain little.
- A corpus that changes daily pays the ingestion cost again and again.
- Metadata may already carry the frame, so check titles, section names, repo paths and version tags before reaching for a contextualizer.

The technique earns its cost when a chunk still reads as anonymous after the available metadata has been attached.

## How to roll it out

Keep the raw chunk, generate the contextualized one at ingestion, and index the contextualized text in both retrievers.

1. Keep the raw chunk and its metadata.
2. Generate contextualized chunks at ingestion time, with prompt caching on.
3. Index the contextualized text into embeddings and BM25.
4. Retrieve a wider candidate pool.
5. Add reranking when your evals show the loss is in selection.

Test generation with the raw chunk, the contextualized chunk, and the note as a header over the raw body. The best retrieval artifact is not always the best generation artifact, because the note is a model's paraphrase and the answer should quote the source.
