---
title: "LLM context windows: what the number on the spec sheet actually means"
date: 2026-03-13
description: "A 1M token context window sounds impressive. Here's why the model often can't reliably use most of it, and what actually happens to your data inside a full context window."
tags: [ai, llm, inference, context]
status: published
---

Someone is going to pitch you a model with a 1 million token context window. They'll say you can load your entire codebase, your full document library, your whole customer history into a single prompt and the model will reason across all of it. This sounds great. It is also, in practice, significantly less useful than advertised.

Here's where I lose you a little, and I want to warn you because this gets counterintuitive fast. The context window number tells you the maximum number of tokens a model can accept. It does not tell you how well the model uses tokens at different positions inside that window. Those are two different things, and the industry mostly talks about the first one.

**The short version:** LLMs perform best on information at the start and end of their context. Performance on information buried in the middle degrades, sometimes significantly. Longer contexts also cost more compute, add latency, and introduce what researchers are calling "context rot." The number on the spec sheet is a ceiling, not a promise.

## The lost in the middle problem is real and documented

In 2023, researchers at Stanford, UC Berkeley, and Samaya AI published ["Lost in the Middle: How Language Models Use Long Contexts"](https://arxiv.org/abs/2307.03172). The finding was uncomfortable: performance is highest when relevant information appears at the very beginning or very end of the input. Shove that same information into the middle of a long context and retrieval accuracy drops, sometimes by 40%.

This isn't a bug in a specific model. It's a structural consequence of how transformers work. Each token can only attend to tokens that came before it, which is called causal masking. Tokens at the start of a context get attended to by every subsequent token in the model. Token 500,000 sitting in the middle only gets attended to by token 500,001 onward. Earlier tokens accumulate more attention weight simply because they have more opportunities to be referenced. The middle gets comparatively starved.

[SCREENSHOT: Figure from the "Lost in the Middle" paper showing performance curve by document position]

I've seen this bite teams building document Q&A systems. They stuff 50 PDFs into a single context, get decent answers on the first few and the last few documents, and assume the whole thing is working. It isn't. The model is quietly ignoring a large chunk of what they fed it.

## Context rot: what happens as the window fills up

The "lost in the middle" problem is about position. Context rot is about volume. The [Understanding AI piece on context rot](https://www.understandingai.org/p/context-rot-the-emerging-challenge) describes what happens as context gets longer: performance doesn't just plateau, it actively degrades. More context creates more noise for the model to sort through. The relevant signal competes with an increasing amount of irrelevant tokens, and the model's ability to isolate what matters goes down.

There's a related finding from a 2025 paper [showing that context length alone hurts performance](https://arxiv.org/html/2510.05381v1) even under perfect retrieval conditions. Meaning: even if you retrieve exactly the right documents and put them in the context, adding more total context around them degrades the model's performance on questions about those documents. The context window is not a neutral container. Filling it has consequences.

My take on this, and it's a take I know isn't popular: the "big context window" arms race has mostly benefited marketing departments. For the use cases where you actually need long context, like processing a single long document, reasoning across a book-length piece of text, or analyzing a multi-hour transcript, long context windows are genuinely useful. But for the "dump everything in and let the model figure it out" use case, they mostly just let you build systems that feel like they're working when they're not.

## What context length actually costs you

Here's the part that gets left off the spec sheet.

Attention, the core mechanism of a transformer, is O(n²) in the naive implementation. Double your context length, and the attention computation quadruples. In practice, most modern models use [flash attention](https://arxiv.org/abs/2205.14135) and other approximations that bring this down, but long contexts still cost meaningfully more compute per request and take meaningfully longer to process.

The latency hit shows up as time to first token. If you've read [my earlier piece on TTFT](/blog/time-to-first-token-ttft/), you know TTFT is what makes an interactive application feel responsive. A 200k token prompt is going to have a noticeably longer TTFT than a 5k token prompt, regardless of how the model is optimized. You're paying for that context in wall clock time before you see the first word of response.

You're also paying for it in dollars. Most APIs price on input tokens. Loading 500k tokens into a single request is expensive even if the model handles it gracefully.

## What actually works in production

The teams I've seen get good results with long context tend to do a few specific things.

Put the most important content first and last. If you know which documents are most relevant to the query, don't bury them in the middle. This is inelegant and annoying and it works.

Use retrieval to limit context in the first place. RAG exists partly because we realized that stuffing everything into a context window was a bad idea. Retrieving the 10 most relevant chunks and passing those to the model beats passing all 500 chunks and hoping the model figures it out. [The tradeoffs in that decision are worth understanding](/blog/rag-vs-fine-tuning/) before you commit to either approach.

Evaluate on your actual data with your actual context sizes. The benchmarks that model providers use to measure long context performance are often designed to make their models look good. Run your own evals. Check whether the model is actually using information from the middle of your context or quietly ignoring it. [Introl's guide on long-context infrastructure](https://introl.com/blog/long-context-llm-infrastructure-million-token-windows-guide) covers some of the evaluation approaches worth running.

Treat context like memory, not like disk. The context window is not a place to dump everything and search later. It's a working memory. The more you put in it, the more the model has to hold in its head simultaneously, and the worse it does at any of it.

## The honest ceiling

Long context is genuinely useful and genuinely improving. The [Together AI work on long context fine-tuning](https://www.together.ai/blog/long-context-fine-tuning-a-technical-deep-dive) shows real progress on extending reliable context lengths. Models today handle 50k tokens more reliably than models from two years ago handled 8k tokens. The trajectory is real.

But the claim that you can load a million tokens and have the model reason uniformly well across all of it is not where the technology is right now. The spec sheet number is an upper bound on what the model accepts. What it reliably uses well is a much smaller number, and that number is task-dependent, position-dependent, and affected by how much total noise you're putting around your signal.

If someone is selling you a system design that depends on uniform performance across a 1M token context window, ask them to show you the evaluation. Ask where in the context the relevant information lives in their tests. The answer is usually the beginning.

## Questions

**Does putting relevant information at the start of the context always help?**

Consistently, yes. The "lost in the middle" research is robust across models. If you have control over what goes into your context and where, prioritize the most critical information at the top. This feels wrong because it's not how you'd organize a document for a human reader, but it matters for LLMs.

**Is 128k tokens enough for most use cases?**

For most practical applications, yes. A 128k context window fits roughly 250 pages of text, which covers the vast majority of single-document analysis tasks, long conversations, and medium-sized codebases. The cases where you need more than that are real but rarer than the marketing suggests.

**Does flash attention solve the lost in the middle problem?**

No. Flash attention is a compute optimization that makes the attention calculation more efficient. It doesn't change the underlying dynamics of how much attention different positions receive. The positional bias problem is about the model's learned behavior, not the computational implementation of attention.

**How do I know if my application is actually hitting this problem?**

Put your most critical information in the middle of your context window and test whether model answers quality changes. Most teams are surprised. If you're building something where context utilization matters, this is a 30-minute test worth running before you build a whole system around the assumption that context position doesn't matter.

**Should I use RAG or long context for document Q&A?**

For most production document Q&A, RAG. Not because long context doesn't work, but because RAG gives you control over what the model sees, makes it easier to cite sources, and doesn't charge you for tokens you don't need. Long context is better for tasks where the relationships between documents matter and where retrieval would break those relationships. Legal contract analysis across a long document is a good long context use case. "Answer questions about our knowledge base" is usually a RAG use case.
