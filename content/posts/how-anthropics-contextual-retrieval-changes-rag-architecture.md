---
date: 2026-03-26
description: Anthropic says Contextual Retrieval cut top-20 retrieval failure by 49%
  with contextual embeddings plus contextual BM25. I walk through the mechanism, the
  benchmark, and the part of the RAG pipeline it changes.
status: published
tags:
- ai
- rag
- infrastructure
- vector-search
title: How Anthropic's Contextual Retrieval Changes RAG Architecture
---

Anthropic took a chunk like `"The company's revenue grew by 3% over the previous quarter."`, asked Claude to explain that chunk using the full document, then prepended the explanation before indexing it. That one step cut top-20 retrieval failure by **49%** when Anthropic combined contextual embeddings with contextual BM25, according to [their writeup](https://www.anthropic.com/engineering/contextual-retrieval).

I like that result because the mechanism is clean. No new retrieval model. No weird ranking trick. No attempt to hide the failure behind a bigger context window. Anthropic changed the chunk before retrieval ever started.

That is the part I keep coming back to. Retrieval work usually piles up at query time. Teams swap embedding models, add rerankers, widen top-K, and keep pushing on the same end of the system. Anthropic pushed on the other end. I think that is why the idea matters.

## The chunk is usually the problem

A raw chunk carries less meaning than the document it came from. That sounds obvious. I still see people treat the chunk as if it were a clean unit of knowledge.

It rarely is.

A sentence about revenue growth loses the company and quarter once I split it away from the filing. A setup step loses the product surface it configures. A function body loses the file and module that tell me why it exists. A paragraph about retries loses the service boundary that makes it relevant.

Retrieval quality drops right there.

I wrote about context decay in [LLM Context Windows Explained](/blog/llm-context-windows-explained/). The same idea shows up earlier in the pipeline. Small chunks improve recall because they are easier to match. Small chunks also strip away the frame that made the text identifiable.

That tradeoff sits in the middle of production RAG.

## Anthropic's move is simple

The standard pipeline looks like this:

1. split the document
2. embed the chunk
3. store the chunk in a vector index
4. optionally store it in BM25
5. retrieve at query time
6. rerank or generate

Anthropic inserts one extra step after chunking.

Claude sees:

- the full document
- one chunk from that document

Claude then writes a short explanation of what the chunk is about in the context of the full document. Anthropic says that explanation is usually **50 to 100 tokens**. That explanation gets prepended to the raw chunk. The enriched text goes into the embedding model and the BM25 index.

Anthropic calls the two retrieval pieces **Contextual Embeddings** and **Contextual BM25**.

That is the whole trick.

I like techniques like this because they are easy to reason about. The indexed chunk becomes more legible. Semantic search gets more context. Lexical search gets more terms. A reranker, when I add one, starts from a stronger candidate pool.

## Contextual Retrieval fixes a real retrieval failure

Embedding search and BM25 fail in different ways.

Embeddings handle paraphrase well. They struggle when a chunk needs document-level framing before the semantic representation becomes useful. BM25 handles exact terms well. It struggles when the query and the text use different words for the same thing.

Contextual Retrieval helps both.

The prepended explanation gives embeddings more signal. It gives BM25 more exact vocabulary. A chunk about quarterly growth can now carry words like company name, quarter, filing type, or section purpose even when the original text did not contain them.

That is why I do not read this as a replacement for hybrid search. I read it as a way to give hybrid search better input.

My [reranking piece](/blog/reranking-in-rag-why-your-top-k-results-are-probably-wrong/) makes the case that vector similarity is a decent filter and a weak ranker. Contextual Retrieval fixes something earlier. It makes the filter more likely to surface the right chunk at all.

## The benchmark is three benchmark claims

Anthropic's headline number gets quoted a lot. The full result is more useful than the headline.

According to the [official post](https://www.anthropic.com/engineering/contextual-retrieval):

- Contextual Embeddings cut top-20 retrieval failure from **5.7%** to **3.7%**
- Contextual Embeddings plus Contextual BM25 cut it from **5.7%** to **2.9%**
- Adding reranking on top cut it from **5.7%** to **1.9%**

I read those as three separate claims:

- **35%** lower failure from contextual embeddings alone
- **49%** lower failure once contextual BM25 joins the stack
- **67%** lower failure once reranking joins too

I trust that breakdown more than a single aggregate number because it shows where the lift comes from. Contextualization helps. Hybrid retrieval still helps. Reranking still helps. Anthropic did not publish a benchmark saying one clever chunking trick made the rest of the stack irrelevant.

Anthropic also shares details that matter:

- the headline metric is **1 - recall@20**
- the appendix includes **@10** and **@5**
- **top-20 chunks** worked better than top-10 and top-5 in Anthropic's tests
- reranking started from **top 150** candidates and reduced them to **top 20**
- the datasets included **codebases, fiction, ArXiv papers, and science papers**

The full breakdown lives in [Appendix II](https://assets.anthropic.com/m/1632cded0a125333/original/Contextual-Retrieval-Appendix-2.pdf).

I trust the result as strong evidence. I would still run my own evals. Retrieval depends heavily on the corpus. Code, support content, legal docs, and internal knowledge bases all fail differently.

<div class="visual-wrapper">
  <div class="visual-title">CHUNK ENRICHMENT AND RETRIEVAL FAILURE REDUCTION</div>
  <div class="visual-container">
    <iframe src="/static/visuals/contextual-retrieval.html" title="A raw chunk versus a chunk with a prepended context blurb before embedding, and the 49% / 67% reduction in top-20 retrieval failure" loading="lazy"></iframe>
  </div>
</div>

## The interesting change happens before query time

The reason I keep dwelling on this technique is simple: it moves work upstream.

Most RAG conversations revolve around the live request path. That makes sense. Query-time mistakes are visible. People talk about embeddings, rerankers, top-K, prompt assembly, and model choice because those components touch the final answer directly.

I care about the index because bad candidate generation poisons everything after it.

A reranker cannot rescue a chunk that never made it into the candidate pool. The model cannot cite a paragraph it never saw. A perfect answerer on top of a weak index still gives weak answers.

Contextual Retrieval changes that part of the system. The chunk is no longer just a slice of source text. It becomes an enriched retrieval artifact.

That changes the questions I ask:

- which corpora lose the most meaning during chunking?
- which metadata fields are missing often enough that I should recover them in the contextualizer?
- should the final model see the raw chunk, the contextualized chunk, or both?
- how much ingestion cost buys me a real lift in retrieval quality?

Those are indexing questions. I think that is the real contribution here.

## Prompt caching is what makes the idea practical

Contextual Retrieval would get expensive fast without prompt caching.

The preprocessing job repeats the same pattern over and over:

- full document stays fixed
- target chunk changes

Anthropic points directly to [prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) as the practical answer. That tracks with how I think about token costs already. Static prefixes should be reused. Anthropic applies that rule during ingestion instead of generation.

I covered the same cost logic in [Prompt Caching](/blog/prompt-caching-what-it-is-and-when-the-math-works/). Anthropic's docs say prompt caching can cut latency by **more than 2x** and reduce costs by **up to 90%** in the right setup. Those numbers matter here because contextualization cost lands up front. Query-time retrieval does not change much unless I add reranking.

The ingestion cost still needs discipline. Every chunk gets longer. Embedding cost rises. BM25 index size rises. Storage rises. I would only pay that bill where retrieval misses are expensive enough to justify it.

## Code looks like the cleanest use case

Anthropic includes codebases in the evaluation set. I think code is where this idea looks strongest.

Code chunks lose identity quickly. A helper function name tells me very little on its own. A short logging block can look semantically close to similar code across several services. A line about retries might belong to the exact module I want or to another subsystem that happens to use the same pattern.

Contextualization puts some of that identity back:

- file role
- module purpose
- service boundary
- implementation intent

Technical docs show the same pattern.

- setup steps lose the product surface they configure
- examples lose the endpoint or SDK section they came from
- troubleshooting notes lose the error family they answer
- migration instructions lose the version boundary that makes them useful

Anthropic's codebase benchmark in the cookbook got my attention for that reason. Code retrieval punishes vague chunks quickly.

## Small corpora do not need this much machinery

Anthropic makes one point I strongly agree with: corpora under **200,000 tokens** may not need RAG at all. I would often use long context there and skip the indexing complexity.

I would also skip Contextual Retrieval when:

- chunks are already self-contained
- the corpus changes constantly
- metadata already carries most of the missing frame
- ingestion cost matters more than small recall gains

Metadata is the first thing I would check before adding a contextualizer. A solid chunk schema with titles, section names, repo paths, service names, and version tags may already recover enough context. Contextual Retrieval earns its keep when the raw chunk still feels anonymous after basic metadata work.

## Reranking still matters

Reranking solves a different problem.

Contextual Retrieval changes what I store. Reranking changes how I sort.

I have seen both failure modes.

One system retrieves the right answer somewhere in the top 100 and buries it under cleaner-looking but weaker chunks. A reranker helps there.

Another system never surfaces the right chunk at all because the original chunk lost too much identity when I split it out of the source document. Contextual Retrieval helps there.

Anthropic's results show the combination works well, which is exactly what I would expect. Better chunk representation and better ranking attack different parts of retrieval.

## How I would use it

I would reach for Contextual Retrieval when chunk identity carries a lot of the retrieval burden.

That usually means:

- codebases
- API docs
- legal or financial corpora
- product docs with repetitive local phrasing
- internal knowledge bases full of short, under-specified paragraphs

My rollout would stay simple:

1. keep the raw chunk and metadata
2. generate contextualized chunks at ingestion time
3. index the contextualized text into embeddings and BM25
4. retrieve a wider candidate pool
5. add reranking when evals justify it

I would also test generation three ways:

- raw chunk only
- contextualized chunk only
- contextualized header plus raw body

The best retrieval artifact is not always the best generation artifact. A chunk can retrieve beautifully and still carry a synthetic preface that I do not want the answer model to trust too much.

Plenty of RAG work feels like tuning around a weak core. I think Contextual Retrieval improves the core. That is why I expect it to stick.