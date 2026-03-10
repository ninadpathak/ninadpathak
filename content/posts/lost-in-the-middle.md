---
title: "Your Context Window Has a Middle. Models Don't Read It."
date: 2026-02-20
description: "The 'lost in the middle' problem is real, quantified, and not solved by bigger context windows. Here's what the research actually says about where LLMs pay attention."
tags: [ai, llm, rag, context-engineering]
status: published
---

There's a paper from 2023 that should have changed how everyone builds RAG systems. It didn't, really. Teams kept stuffing more documents into longer contexts, assuming bigger windows meant better results. The paper said otherwise, with numbers.

It's called ["Lost in the Middle: How Language Models Use Long Contexts"](https://arxiv.org/abs/2307.03172), by Nelson Liu, Kevin Lin, and others from Stanford. The finding: language models are significantly better at using information at the beginning or end of their context window than information in the middle. The performance curve across context position is U-shaped. Put your relevant document in the middle of a 20-document context and watch accuracy fall off a cliff.

Anyone who's read the attention mechanism papers won't be surprised, but seeing it quantified is different from understanding it theoretically.

## The numbers

The experiment was multi-document question answering. Given a question and 20 documents (one containing the answer, the rest distractors), models were tested with the answer-containing document placed at different positions.

With GPT-3.5-Turbo and 20 documents: when the relevant document was at position 20 (the end), accuracy was around 42%. When it was at positions 5 through 15 (the middle), accuracy dropped to around 25%. That's a 17 percentage point drop, from one placement decision.

Here's the part that should make you uncomfortable: adding more context hurt. GPT-3.5-Turbo's closed-book baseline (no retrieved documents at all) was 56.1% on the evaluation set. When the relevant document was in the middle of the context, the model with access to the answer performed *worse* than the model with no access at all. You gave it the information and it performed worse than if you hadn't.

Extended-context models, the ones specifically trained for longer inputs, showed nearly identical U-shaped curves. The window got bigger. The bias didn't go away.

## Why this happens

The paper doesn't provide a definitive mechanistic explanation, but the intuition is reasonable: models are trained on text where important information tends to appear at the start or end. Abstracts, introductions, conclusions, subject lines. The attention patterns that emerge from training reflect those distributions.

There's also a simpler story: at very long contexts, attending to positions in the middle is harder. The gradient signal during training is weaker for distant positions in some architectures. The recency bias (end of context) and primacy bias (start of context) are stable phenomena in human cognition too; it's not obvious that transformers trained on human text would be immune to them.

## What this means for how you build RAG

Naive RAG pipelines chunk documents, embed them, retrieve top-k by similarity, and concatenate everything into the prompt. The most relevant chunk lands somewhere in the middle of the context by default, ranked first in the retrieval list but buried after the system prompt.

A few things follow from the research:

**Put the highest-ranked result at the start of the retrieved context, not buried in the middle.** With 10 retrieved chunks, the one with the highest similarity score should be first (and possibly last, reordered). A one-line reordering that improves accuracy on nearly every setup.

**Don't retrieve more than you need.** The [Databricks long context RAG research](https://arxiv.org/abs/2411.03538) from late 2024 found that retrieval performance peaks around top 5-10 chunks and degrades with more. You're adding noise, not signal, and the noise lands in the middle of the context.

**Evaluate on your actual distribution.** The U-shaped curve varies by model and task. The only way to know how bad your specific setup is: create a held-out eval set, place your known-answer chunk at positions 1, 5, 10, 15, 20, measure accuracy at each. You'll probably see the curve. Then you'll know whether it's a problem worth fixing for your use case.

## Long context vs. RAG is the wrong frame

The conventional wisdom in mid-2024 was "context windows are getting so big that RAG will become unnecessary." Gemini 1.5 Pro at 1 million tokens. Claude with 200k. Just dump everything in.

The research doesn't support this. The SummHay benchmark tested whether models could summarize information from long contexts. Without a retrieval mechanism, GPT-4o and Claude 3 Opus scored below 20%, despite both having near-perfect performance on "needle in a haystack" tests (>99% recall). Finding a specific string in a long document is not the same as reasoning over distributed information in that document.

RAG isn't redundant because context windows got bigger. They solve different things. Long context handles cases where the information is known, bounded, and fits comfortably. RAG handles cases where you have more information than the context can hold, or where you need to pull from dynamic external sources.

The real question isn't "should I use RAG or long context?" It's "how do I fill my context window with the right information for this specific query?" Which is where context engineering comes in.

## Context engineering is a real discipline now

Andrej Karpathy [defined it](https://x.com/karpathy/status/1937902205765607626) as "the delicate art and science of filling the context window with just the right information for the next step." It sounds obvious when you read it. The practice is not obvious.

For a real agent or RAG system, what goes in the context at inference time is not static. It's assembled dynamically from: the system prompt, any cached instructions, retrieved documents ordered carefully, conversation history (summarized or truncated how?), tool outputs, current task state. Getting each of these right, in the right order, in the right amount, is engineering work.

Anthropic's [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) is partly a context engineering tool: when your system prompt is 50k tokens (a large codebase, a full policy document, detailed instructions), you pay to write it to cache once and then read it at 90% discount on subsequent calls. A 200k token context at standard Claude pricing costs around $3.00 per call. With cache hits, it drops to about $0.10. That's not a marginal savings.

The interesting design question is not "how big a context can I use" but "what is the minimum context that gives the right answer?" Smaller context is cheaper, faster, and, the research confirms, often more accurate.

## What I'm convinced of after reading this research

Position matters more than presence. Retrieving the right document is necessary but not sufficient. Where it lands in the context window determines whether the model actually uses it.

Optimal RAG parameters exist and are measurable. Five to ten chunks, ordered carefully, is roughly the sweet spot for most models and tasks. Going to 20 chunks adds noise. Going to 50 is almost certainly hurting you.

Long context and RAG are complementary, not competing. Use long context for bounded, stable information. Use RAG for dynamic retrieval from large corpora. Use both together for complex agents.

The models that score well on needle-in-a-haystack benchmarks are not solving the same problem as models reasoning over large documents. Needle-in-a-haystack is easy; it's string matching at scale. Synthesizing distributed information is hard, and longer contexts don't automatically make it easier.

None of this is exotic research. The "Lost in the Middle" paper is two years old. The practices that follow, reranking, result ordering, limiting retrieved chunks, are available in every RAG framework. The question is whether the teams building these systems actually know about the curve.

The ones getting RAG right do. The ones stuffing 50 chunks into a prompt and wondering why accuracy is mediocre probably don't.
