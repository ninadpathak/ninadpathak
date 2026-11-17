---
category: ai-engineering
primary_query: llm context window
siblings:
- time-to-first-token
- llm-token-budgets
bridges:
- slug: contextual-retrieval
  reason: Retrieval is the alternative to a long prompt, and that page reduces its main failure.
- slug: short-term-agent-memory
  reason: Compaction shrinks a full window, and that page covers what a summary can lose.
date: 2026-03-14
description: 'An LLM context window is what a model can read at once. Why the middle gets ignored, what context rot is, what length costs, and how to fill a large window.'
status: published
work_note: "Building an AI product whose readers are engineers? I'm Ninad Pathak, a freelance technical writer, and I write tutorials and technical articles for companies like yours after running the product myself. [Hire me](/services/freelance-technical-writer-for-ai-companies/)."
title: "LLM Context Windows Explained"
slug: llm-context-windows
updated: 2026-11-17
---

An LLM context window is the span of text a model can read at once: the system prompt, the conversation so far, tool results and the reply it is writing. Anthropic's [documentation](https://platform.claude.com/docs/en/build-with-claude/context-windows) calls it the model's "working memory", and on current Claude models it runs to a million tokens.

DOS programs had a fixed budget to work in. [Wikipedia's entry](https://en.wikipedia.org/wiki/Conventional_memory) defines conventional memory as "the first 640 kilobytes of the memory on IBM PC or compatible systems", and years of software were written to fit under that line.

A million tokens sounds like the end of fitting under lines. But the Anthropic page that lists the million also says "more context isn't automatically better."

That sentence is the reason window size is a cost and quality decision in [LLM inference](/articles/ai-engineering/), and a larger number on a model card settles little.

## What counts toward the context window?

Everything the model can refer to while it generates, and that includes the response it's writing. So the reply spends the same budget as the prompt.

A conversation fills it turn by turn, since each request resends the turns before it. When a request would run past the limit on recent Claude models, generation stops with the reason `model_context_window_exceeded`, and older models reject the request up front.

## Why does the middle of a long context get ignored?

Because models recall the two ends of their input better than the middle. The finding has a name from the paper that reported it, [Lost in the Middle](https://arxiv.org/abs/2307.03172), submitted on July 6, 2023.

Its authors found that models did best when the relevant fact sat at the beginning or the end of the input, and noticeably worse when it sat in the middle. That held "even for explicitly long-context models."

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/llm-context-windows/lost-in-the-middle.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/llm-context-windows/lost-in-the-middle.narrow.svg" width="288" height="528"><img class="np-has-narrow" src="/static/images/diagrams/llm-context-windows/lost-in-the-middle.svg" width="720" height="544" alt="A long prompt split into its start, middle, and end. The model reliably recalls facts placed at the start, which frames the task, and at the end, which is the runway to the next token. Facts buried in the middle compete for whatever attention is left and often get skipped." loading="lazy" decoding="async"></picture></a>
  <figcaption>Recall follows a U shape across the context. Put the instruction and the data you care about at the two ends.</figcaption>
</figure>

The models in that paper date from 2023, and I don't assume the curve is as deep today. But the rule costs nothing to keep: put the instruction and the facts that matter at the start or the end of the prompt.

## What is context rot?

Context rot is the loss of accuracy as the input grows, wherever the important part sits. Chroma's [technical report](https://research.trychroma.com/context-rot) of July 14, 2025 tested 18 models and gave the effect its name.

The report starts from an assumption and then removes it: that a model handles its 10,000th token as reliably as its 100th. What it found is that models don't use their context evenly, and that they get less reliable as the input gets longer.

Now, Chroma sells a retrieval database, so it has a reason to find that stuffing the window fails. But Anthropic sells the tokens, and its own docs now say the same: "As token count grows, accuracy and recall degrade, a phenomenon known as context rot."

And the failure differs by model. On questions with distracting passages, the report found Claude models tending to abstain when unsure, and GPT models more often answering wrongly with confidence.

## What does a long context cost?

It costs money on every call and time before the first word. Input tokens are billed each time they are sent, and a chat that resends its history pays for the early turns again and again.

My [token budgets guide](/articles/llm-token-budgets/) runs the arithmetic on a 20-turn chat, where the last turn costs 3.6 times the first. And the wait grows too, since the model has to read the whole prompt before it answers, the phase that [time to first token](/articles/time-to-first-token/) measures.

## Should you use a long context or retrieval?

Use the window for material that has to be read together, and retrieval for material that has to be found. A contract and the question about it belong in one prompt, and a library of ten thousand documents doesn't.

Retrieval puts a few passages in front of the model, which keeps the input short. It can also miss the right passage, and [contextual retrieval](/articles/contextual-retrieval/) is one way to reduce that failure at indexing time.

Inside a long session the third option is to shrink what is already there. Compaction replaces old turns with a summary, and [short-term memory for agents](/articles/short-term-agent-memory/) covers what that can lose.

## How should you fill a large window?

Treat the size as a ceiling and fill it by choice. Anthropic's own page says that choosing what goes into the context matters as much as how much room there is.

- Send what the task needs, and leave out documents included in case they help.
- Place instructions and key facts at the start or the end.
- Count tokens before sending, so a request is refused by your code and not by the API.
- Measure answers at the lengths you will run, since a prompt that works at 2,000 tokens tells you little about 200,000.

Newer models help with the bookkeeping. Anthropic says several current ones keep track of how much window is left through a conversation, which lets a long task plan against that space.

## FAQ

**What is a context window in an LLM?**

It is the text the model can read at once, measured in tokens, including the prompt, the conversation history and the reply being generated.

**Is a bigger context window always better?**

No. A 2023 paper, a 2025 report and Anthropic's own documentation all say that accuracy falls as the input grows.

**What happens when the context window is full?**

The request fails or generation stops, depending on the model. Applications avoid it by counting tokens, trimming input, or compacting old turns into a summary.
