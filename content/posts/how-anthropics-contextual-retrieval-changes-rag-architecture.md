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

What I like about that result is how clean the mechanism is. No new retrieval model. No weird ranking trick. No attempt to hide the failure behind a bigger context window. Anthropic changed the chunk before retrieval ever started.

That is the part I keep coming back to. Retrieval work usually piles up at query time, where teams swap embedding models, add rerankers, widen top-K, and keep pushing on the same end of the system. Anthropic pushed on the other end, before anyone runs a single query. I think that is why the idea matters.

## The chunk is usually the problem

A raw chunk carries less meaning than the document it came from. That sounds obvious, yet I still see people treat the chunk as if it were a clean unit of knowledge. It rarely is.

Take a sentence about revenue growth. Split it away from the filing and it loses the company and the quarter, so a query like "Acme Q3 revenue" no longer has an obvious thing to match against. A setup step loses the product surface it configures. A function body loses the file and module that tell me why it exists. A paragraph about retries loses the service boundary that makes it relevant, which means it reads the same whether it belongs to the payments worker or the email queue.

Retrieval quality drops right there, at the seam where the chunk got cut out.

Context decay is something I wrote about in [LLM Context Windows Explained](/blog/llm-context-windows-explained/), and the same idea shows up earlier in the pipeline. Small chunks improve recall because they are easier to match, and the same smallness strips away the frame that made the text identifiable in the first place.

That tradeoff sits in the middle of production RAG, and most teams pick a chunk size by feel and then live with whatever it costs them.

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

Claude then writes a short explanation of what the chunk is about given the full document, something like "This is from Acme's Q3 2024 10-Q, in the section on segment revenue." Anthropic says that explanation usually runs **50 to 100 tokens**. The explanation gets prepended to the raw chunk, and the enriched text goes into both the embedding model and the BM25 index.

Anthropic calls the two retrieval pieces **Contextual Embeddings** and **Contextual BM25**.

That is the whole trick.

Techniques like this are the ones I trust, because I can reason about them end to end. The indexed chunk becomes more legible. Semantic search gets more context. Lexical search gets more terms. A reranker, when I add one, starts from a stronger candidate pool. It works the way labeling a moving box does. The contents stay the same. Writing "kitchen, top shelf, fragile" on the side tells you what is inside without opening it.

## Contextual Retrieval fixes a real retrieval failure

Embedding search and BM25 fail in different ways.

Embeddings handle paraphrase well, and they struggle when a chunk needs document-level framing before the semantic representation becomes useful. BM25 handles exact terms well, and it struggles when the query and the text use different words for the same thing. Search "how do I rotate API keys" against a chunk that only says "call `refresh()` on the credential object" and BM25 has nothing to grab.

Contextual Retrieval helps both. The prepended explanation gives embeddings more signal and gives BM25 more exact vocabulary. A chunk about quarterly growth can now carry words like the company name, the quarter, the filing type, or the section purpose even when the original text never spelled any of them out.

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

I trust that breakdown more than a single aggregate number because it shows where the improvement comes from. Contextualization helps. Hybrid retrieval still helps on top of it. Reranking still helps on top of that. Anthropic did not publish a benchmark saying one clever chunking trick made the rest of the stack irrelevant, and that restraint is part of why I believe the rest of the numbers.

Anthropic also shares details that matter:

- the headline metric is **1 - recall@20**
- the appendix includes **@10** and **@5**
- **top-20 chunks** worked better than top-10 and top-5 in Anthropic's tests
- reranking started from **top 150** candidates and reduced them to **top 20**
- the datasets included **codebases, fiction, ArXiv papers, and science papers**

The full breakdown lives in [Appendix II](https://assets.anthropic.com/m/1632cded0a125333/original/Contextual-Retrieval-Appendix-2.pdf).

Strong evidence is how I read the result, and I would still run my own evals before betting an ingestion budget on it. Retrieval depends heavily on the corpus. Code, support tickets, legal docs, and a messy internal wiki all fail differently, and a 49% number measured on one will not carry over cleanly to another.

<div class="visual-wrapper">
  <div class="visual-title">CHUNK ENRICHMENT AND RETRIEVAL FAILURE REDUCTION</div>
  <div class="visual-container">
    <iframe src="/static/visuals/contextual-retrieval.html" title="A raw chunk versus a chunk with a prepended context blurb before embedding, and the 49% / 67% reduction in top-20 retrieval failure" loading="lazy"></iframe>
  </div>
</div>

## The interesting change happens before query time

The reason I keep dwelling on this technique is that it moves work upstream.

Almost every RAG conversation I sit in revolves around the live request path, which makes sense because query-time mistakes are the ones you can see in a trace. People talk about embeddings, rerankers, top-K, prompt assembly, and model choice because those components touch the final answer directly.

The index is what I care about, because bad candidate generation poisons everything downstream of it. A reranker cannot rescue a chunk that never made it into the candidate pool. The model cannot cite a paragraph it never saw. A flawless answerer sitting on top of a weak index still hands back weak answers, the same way a brilliant lawyer loses when the right document never made it into the case file.

Contextual Retrieval changes that part of the system. The chunk stops being a bare slice of source text and becomes an enriched retrieval artifact.

That changes the questions I ask:

- which corpora lose the most meaning during chunking?
- which metadata fields are missing often enough that I should recover them in the contextualizer?
- should the final model see the raw chunk, the contextualized chunk, or both?
- how much ingestion cost buys me a real lift in retrieval quality?

Those are indexing questions. I think that is the real contribution here.

## Prompt caching is what makes the idea practical

Without prompt caching, Contextual Retrieval would get expensive fast. Picture contextualizing a 100-page filing split into 400 chunks: the naive version resends all 100 pages 400 times, once per chunk, just to write 400 little blurbs.

The preprocessing job repeats the same pattern over and over:

- full document stays fixed
- target chunk changes

Anthropic points directly to [prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) as the practical answer, which tracks with how I already think about token costs. Static prefixes should be reused, and Anthropic applies that rule during ingestion rather than generation.

The same cost logic shows up in my piece on [Prompt Caching](/blog/prompt-caching-what-it-is-and-when-the-math-works/). Anthropic's docs say prompt caching can cut latency by **more than 2x** and reduce costs by **up to 90%** in the right setup. Those numbers matter here because the contextualization expense lands up front, at ingestion. Query-time retrieval barely moves unless I add reranking.

Discipline still applies to the ingestion cost. Every chunk gets longer. Embedding cost rises. BM25 index size rises. Storage rises. I would only pay that bill where a retrieval miss actually hurts, like a support bot citing the wrong refund policy or a code assistant pulling a deprecated function from the wrong service.

## Code looks like the cleanest use case

Anthropic includes codebases in the evaluation set, and code is where I think this idea looks strongest.

Code chunks lose identity faster than almost anything else. A helper named `format()` tells me very little on its own. A short logging block can look semantically identical to a dozen others across several services. A line that sets `max_retries = 3` might belong to the exact payment module I am hunting for, or to a background job that happens to use the same pattern, and the chunk alone gives me no way to tell.

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

Anthropic's codebase benchmark in the cookbook got my attention for that reason. Code retrieval punishes a vague chunk fast, because near-duplicate snippets are everywhere and the query rarely shares the snippet's exact wording.

## Small corpora do not need this much machinery

Anthropic makes one point I strongly agree with: corpora under **200,000 tokens** may not need RAG at all. I would often use long context there and skip the indexing complexity.

I would also skip Contextual Retrieval when:

- chunks are already self-contained
- the corpus changes constantly
- metadata already carries most of the missing frame
- ingestion cost matters more than small recall gains

Before I reach for a contextualizer, metadata is the first thing I check. A solid chunk schema with titles, section names, repo paths, service names, and version tags may already recover enough context on its own. Contextual Retrieval earns its keep when the raw chunk still reads as anonymous even after I have attached every field I have, which is exactly when a free-text blurb can say what no structured field captured.

## Reranking still matters

Reranking solves a different problem. Contextual Retrieval changes what I store, and reranking changes how I sort what I retrieved.

Both failure modes are ones I have watched happen. The first system retrieves the right answer somewhere in the top 100 and buries it under cleaner-looking weaker chunks, so the model never sees it inside a top-20 cut. A reranker rescues that one. The second system never surfaces the right chunk at all, because it lost too much identity when I split it out of the source document, and no amount of reordering fixes a candidate pool that does not contain the answer. Contextual Retrieval rescues that one.

Anthropic's results show the combination works well, which matches what I would expect. Better chunk representation and better ranking go after different parts of retrieval, so stacking them compounds instead of overlapping.

## How I would use it

Chunk identity carrying a lot of the retrieval burden is my signal to reach for Contextual Retrieval.

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

The best retrieval artifact is not always the best generation artifact. A chunk can retrieve beautifully and still carry a synthetic preface I would rather the answer model treat as a finding aid than as a quotable source, since the blurb is Claude's paraphrase and not the original text.

So much RAG work feels like tuning around a weak core, sanding rerankers and prompts to compensate for an index that lost the plot at chunking time. Contextual Retrieval improves the core itself. That is why I expect it to stick.