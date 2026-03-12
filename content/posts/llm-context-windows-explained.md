---
title: "LLM context windows: what the number on the spec sheet actually means"
date: 2026-03-13
description: "A 1M token context window sounds impressive. Here's why the model often can't reliably use most of it, and what actually happens to your data inside a full context window."
tags: [ai, llm, inference, context]
status: published
---

A 1M token context window does not mean you get 1M tokens of reliable reasoning. It means the model will accept 1M tokens. Those are different things.

Here's what actually happens: model providers benchmark long-context performance by putting the relevant content at the beginning or end of a long context. That's where models perform best. They don't test middle-of-context retrieval, because middle-of-context retrieval is where things fall apart.

**Short answer:** LLMs attend unevenly across their context. Performance is strong at the start and end, weak in the middle, and gets worse as total context length grows. The spec sheet number is an input limit, not a performance guarantee.

## Your data doesn't get equal attention

This is the mechanical reason, and once you see it you can't unsee it.

During a transformer's forward pass, each token attends to every token before it in the sequence. A token at position 1 gets attended to by every single subsequent token through the entire model. A token at position 200,000 only matters to positions 200,001 onward. The attention signal that early tokens accumulate over the full sequence is categorically different from what middle tokens get.

Researchers at Stanford, Berkeley, and Samaya AI tested this systematically in 2023. They published [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172), where they varied the position of relevant documents across a fixed context and measured retrieval accuracy. Performance dropped by up to 40% for content in the middle of the context compared to content at the beginning. The pattern held across model sizes and families.

Flash attention doesn't help here. [Flash attention](https://arxiv.org/abs/2205.14135) is a compute optimization that tiles the attention calculation to fit in fast SRAM, which reduces memory use and speeds things up considerably. The attention weights that create this positional bias are unchanged. You get the same biased distribution, faster.

[SCREENSHOT: Figure from the "Lost in the Middle" paper showing retrieval accuracy by document position in context]

## More context also makes the model dumber

Here's where I lose some people, because they assume these are the same problem. They're not.

The positional degradation issue is about where in the context your content lives. This second issue is about how much total content you have, regardless of position.

A [2025 paper studying context length in isolation](https://arxiv.org/html/2510.05381v1) found that retrieval accuracy degrades as total context length increases, even when the relevant documents are placed correctly and retrieved without error. Adding more irrelevant content makes it harder for the model to isolate the signal, full stop.

[The Understanding AI writeup on context rot](https://www.understandingai.org/p/context-rot-the-emerging-challenge) calls this a noise problem: every additional irrelevant token competes with the content you actually care about. At 500k tokens, there's a lot of noise. The model has to look past all of it every time it generates a token.

The context window arms race has mostly answered the question "can we technically process this many tokens" without answering "does the model reason well across all of them." Anthropic, Google, and OpenAI have all shipped million-token windows. The underlying attention architecture hasn't changed.

## It also costs a lot

Attention is O(n²) in the naive implementation. Double the context, quadruple the compute. Flash attention reduces that in practice, but the relationship is still steep. A 200k token prompt costs substantially more to process than a 5k token prompt, on every single request.

The latency hit is the one you feel first. It shows up as time to first token, which I covered in more depth [in my post on TTFT](/blog/time-to-first-token-ttft/). A model that starts generating 8 seconds after you submit a 200k token prompt is behaving correctly. Whether 8 seconds works for your application is a different question, and for most interactive use cases the answer is no.

Then there's the bill. Most providers price input tokens similarly to output tokens. Loading 500,000 tokens per request means paying for 500,000 tokens per request. At scale, that adds up fast. I've seen teams build perfectly functional RAG systems and then decide to "simplify" by just dumping everything into context, not realizing they were trading a few hours of plumbing work for a 10x increase in API costs.

## What actually works

Think about context like you'd think about RAM. You don't load your entire database into RAM because you have enough RAM to hold it. You load what you need. Same logic applies to context.

If you know which documents are relevant to a query, put them at the top of the context. It's inelegant but the positional bias is real and consistent. Working with it beats pretending it doesn't exist.

For most production document Q&A, retrieval beats long context architecturally. Passing the model fewer tokens with higher signal density is better than passing it everything and hoping. The [tradeoffs between RAG and other approaches](/blog/rag-vs-fine-tuning/) are worth thinking through before you commit to an architecture, but RAG's fundamental advantage here is that it controls what the model actually sees.

[Introl's guide on long-context infrastructure](https://introl.com/blog/long-context-llm-infrastructure-million-token-windows-guide) goes into evaluation methodology in detail. [Together AI's writeup on long-context fine-tuning](https://www.together.ai/blog/long-context-fine-tuning-a-technical-deep-dive) is worth reading if you're building systems that genuinely need long context rather than systems that are reaching for it because it's available.

Long context is genuinely the right answer for some tasks: legal analysis across an entire contract, reasoning about how changes in one part of a codebase affect another, synthesizing a full research paper. These break when you chunk and retrieve because chunking destroys the relationships between parts. For "answer questions about our knowledge base," RAG wins.

## Questions

**What context length is actually usable?**

Rough heuristic: the first 20-30% and last 20-30% of a model's advertised context are the high-confidence zones. For a 128k model, that's roughly the first 25k and last 25k tokens. The middle 75k is where you're taking on risk. Run evals on your actual data rather than trusting benchmark numbers.

**Does putting relevant content at the start always help?**

Consistently yes. It's the cheapest single intervention for improving long-context retrieval quality. It feels wrong because it's not how you'd structure a document for a human reader, but you're not writing for a human reader.

**Is long context ever the right answer over RAG?**

Yes, when the task requires reasoning over relationships between documents rather than retrieving specific facts. When chunking would destroy the thing you're trying to understand. For fact retrieval from a knowledge base, RAG is almost always the better system.

**Does flash attention fix the positional bias?**

No. Flash attention changes how the computation runs, not what values come out of it. The same tokens still accumulate the same relative attention weight.

**If the model has a 1M token context window, why shouldn't I just use it?**

You can. Put your test questions where the answers live in the middle of the context and run evals. If it's working, great. If it's returning confident but wrong answers, you've found your practical limit, and it's almost certainly smaller than 1M tokens.

Writing about infrastructure tradeoffs like these for developer audiences is a significant part of what I do. If your team needs that kind of technical depth, [my work page](/work) has examples.
