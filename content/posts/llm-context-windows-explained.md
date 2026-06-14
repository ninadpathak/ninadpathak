---
date: 2026-03-14
description: Context windows are expanding to millions of tokens. Here is why the
  middle of your context still gets ignored, what long context actually costs, and
  how to build production systems that use these massive windows effectively.
status: published
tags:
- ai
- llm
- infrastructure
title: 'Llm Context Windows Explained: Why More Is Not Always Better'
---

Language models read and reason over a fixed span of text called the context window, and that span has grown from a few thousand tokens to several million in barely a year. On paper, you can now drop an entire codebase, or a shelf of books, into one prompt and ask a question across all of it.

Production behavior tells a messier story. Bigger windows bring new failure modes, and they rewrite the economics of every inference call. I have shipped enough features on top of these models to know that the trade-offs decide whether the system is reliable or merely impressive in a demo. A prompt that handles ten documents beautifully can quietly mangle the eleventh, and the bill for that capacity arrives whether or not the model actually used the room you paid for.

## Why the middle of your context gets ignored

Attention is not spread evenly across the prompt. Research has found a consistent U-shaped recall curve: models retrieve facts placed at the very start or the very end of the context far more reliably than anything buried between them. A detail dropped into the middle of a long prompt often gets quietly skipped, as if it were never sent.

<div class="visual-wrapper">
  <div class="visual-title">LOST IN THE MIDDLE</div>
  <div class="visual-container">
    <iframe src="/static/visuals/lost-in-the-middle.html" title="U-shaped recall curve: high accuracy at the start and end of the context, sagging in the middle" loading="lazy"></iframe>
  </div>
</div>

Why this happens comes down to how attention rations a finite budget across thousands of tokens. The opening tokens frame the task, the closing tokens are the immediate runway to the next predicted word, and everything in between competes for whatever focus is left. Think of it like skimming a long contract: you read the first clause carefully, you read the signature block at the bottom, and your eyes glaze over the dense paragraphs in section 14. When I build long prompts, I put the actual instruction and the data I care about at the two ends, never in the soft middle.

The practical sting is that the same fact can be retrievable or invisible depending only on where it sits. Move a critical constraint from the bottom of the prompt to position 40,000 of 80,000 and recall can drop sharply, even though the words are identical and the model is the same. Layout, not just content, becomes something I tune deliberately.

## Context rot: the volume problem

Fill the window and quality slides, a decay people now call context rot. Position is only half of it. The sheer total volume the model has to hold in its head matters just as much, and every extra token nudges up the odds of a reasoning slip somewhere in the chain.



Give a model a 2,000-token prompt with a strict formatting rule, say "return only valid JSON, no prose," and it tends to obey. Pad that same prompt out to 100,000 tokens of supporting documents and it starts wrapping the JSON in commentary or dropping a required field. The signal thins out as the noise around it grows. The engineers I trust keep their prompts as lean as the task allows, large window or not.

Rot rarely announces itself, which is what makes it dangerous in production. The model still returns a confident, fluent answer, so a casual eyeball test passes and the regression slips through. I have watched a summarization step quietly stop mentioning the last two of five attached documents once the combined input crossed a certain size, with no error and no warning, just an answer that looked complete and was not. The fix was never a bigger window. Trimming each document to its relevant section before assembling the prompt restored the behavior, because I was handing the model less to lose track of.

## What long context actually costs

Bigger windows carry a tax you pay in dollars and in milliseconds. Standard attention scales quadratically with length, so doubling the context roughly quadruples the compute, the way doubling the side of a square quadruples its area. That curve shows up directly as slower responses and a fatter bill on every request.

The cost has two faces, and they bite at different times. There is the steady drip of paying for input tokens on every call, which a chatty agent racks up fast when it resends a growing history each turn. Then there is latency, the seconds a user spends staring at a blank cursor while the model digests a stuffed prompt before producing a single word. A nightly batch job can shrug off both. A live coding assistant or a checkout helper cannot, and that constraint usually decides how much context I am willing to send at all.



[Prompt caching can mitigate some of these costs by reusing a static prefix](/blog/prompt-caching-what-it-is-and-when-the-math-works/), and it helps a lot when most of your prompt is boilerplate. Caching does not bend the underlying physics of attention, though, so the bottleneck stays. Every design decision becomes a weigh-in: more context against a slower reply. A chat assistant that has to feel instant simply cannot afford to load a full 128k window on each turn, because [a long prompt directly drives up time to first token](/blog/time-to-first-token-ttft/).

## Long context vs RAG vs hybrid

Before million-token windows existed, Retrieval-Augmented Generation (RAG) was the standard way to point a model at a large dataset. A few people now declare RAG obsolete, and that take falls apart the moment you operate at real scale. RAG still wins when the corpus dwarfs even the biggest window, like a support knowledge base of half a million articles that no context could hold, and it costs a fraction of streaming millions of tokens on every single query.

Long context earns its keep on the opposite shape of problem: tasks that demand reasoning over everything at once. Summarizing a 200-page contract, or spotting that two functions in different files contradict each other, needs the model to hold the whole thing in view rather than fetch fragments. Retrieval struggles here because the answer is not in any single chunk. It lives in the relationship between chunks, and a similarity search has no way to know that clause 3 quietly overrides clause 41 unless both happen to surface together. Hand the model the entire document and the contradiction is at least in reach.

What I reach for in production is a hybrid. RAG narrows a huge store down to the relevant neighborhood, then a medium-sized window hands the model enough of that neighborhood to answer accurately. Picture answering a question about a single tax form: retrieval pulls the handful of pages that mention it, and the long context then reads those pages together so the model can reconcile the instructions across them. That split keeps both precision and cost in a sane range, and it degrades gracefully when the corpus keeps growing, since you scale the retrieval index rather than the prompt.



## What works in production

Three habits have served me well when building on long-context models today.

**Boundaries matter.** Put the task definition and the data you actually want answered at the two ends of the prompt, and let the soft middle carry the supporting material you can afford to lose a little fidelity on.

**Measure recall.** Never assume the model sees everything you send. Run needle-in-a-haystack tests against your own data, for example planting a fake order ID deep in a batch of real records and checking whether the model can pull it back out. Whatever depth it starts failing at becomes your working context limit.

**Optimize through chunking.** Split data into labeled units even when the whole thing fits, with clear delimiters like `### CUSTOMER PROFILE` between sections. Structure gives the attention mechanism handholds, the same way headings let a reader find their place in a long document.

A million-token window is a genuinely powerful tool, and it retires none of the careful context engineering that came before it. Token space stays a scarce resource if you want dependable output, which is also the groundwork for [keeping your LLM spend predictable with token budgets](/blog/llm-token-budgets-cost-control/).

## Questions

**Is million-token context useful for every app?**

No. A customer-facing chatbot or an autocomplete feature gains far more from a fast, precise reply than from the ability to swallow a million tokens it will mostly ignore.

**Does FlashAttention fix the quadratic cost?**

It makes the computation much faster and far easier on memory, which is why long contexts are practical at all. The underlying quadratic relationship still asserts itself at extreme scales, so the cost curve bends but never goes flat.

**Should I stop using vector databases?**

Vector databases are still the most efficient way to scale to billions of documents. They complement long-context models rather than competing with them.