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
description: 'An LLM context window is what a model can read at once. Why facts in the middle of a long prompt get ignored, what context rot is, what a long prompt costs, and how to choose what goes into a large window.'
status: published
work_note: "Building an AI product whose readers are engineers? I'm Ninad Pathak, a freelance technical writer, and I write tutorials and technical articles for companies like yours after running the product myself. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: "LLM Context Windows Explained"
slug: llm-context-windows
updated: 2026-11-17
---

An LLM context window is the span of text a model can read at once: the system prompt, the conversation so far, tool results and the reply it is writing. Anthropic's [documentation](https://platform.claude.com/docs/en/build-with-claude/context-windows) calls it the model's "working memory", and on current Claude models it runs to a million tokens.

DOS programs had a fixed amount of memory to work in. On an IBM PC that amount was the first 640 kilobytes, known as [conventional memory](https://en.wikipedia.org/wiki/Conventional_memory), and years of software were written to fit under that line.

A million tokens sounds like enough room that nobody has to fit under a limit again. But the Anthropic page that lists the million also says "more context isn't automatically better."

Anthropic's warning is why I treat window size as a cost and quality decision in [LLM inference](/articles/ai-engineering/). A model card that says 1M tokens tells you how much the model accepts, not how well it uses what you send.

## What counts toward the context window?

Everything the model can refer to while it generates counts toward the context window, including the response it's writing. So a 4,000-token reply uses 4,000 tokens of the same window as the prompt.

A conversation fills the window turn by turn, since each request resends all the turns before it. An input that exceeds the window on its own gets a 400 error on every Claude model.

On Claude 4.5 models and newer, a request whose input plus `max_tokens` would pass the limit is accepted. If generation then reaches the limit, it stops with the reason `model_context_window_exceeded`.

## Why does the middle of a long context get ignored?

The middle gets ignored because models recall the beginning and the end of their input better than the middle. The effect is named after the paper that reported it, [Lost in the Middle](https://arxiv.org/abs/2307.03172), submitted on July 6, 2023.

Its authors found that models did best when the relevant fact sat at the beginning or the end of the input, and noticeably worse when it sat in the middle. The drop in the middle appeared "even for explicitly long-context models."

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/llm-context-windows/lost-in-the-middle.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/llm-context-windows/lost-in-the-middle.narrow.svg" width="288" height="528"><img class="np-has-narrow" src="/static/images/diagrams/llm-context-windows/lost-in-the-middle.svg" width="720" height="544" alt="A long prompt split into its start, middle, and end. The model reliably recalls facts placed at the start, which frames the task, and at the end, which is the runway to the next token. Facts buried in the middle compete for whatever attention is left and often get skipped." loading="lazy" decoding="async"></picture></a>
  <figcaption>Recall follows a U shape across the context. Put the instruction and the data you care about at the two ends.</figcaption>
</figure>

The models in that paper date from 2023, and I don't assume current models lose as much in the middle. The paper's practical rule still costs nothing to follow: put the instruction and the facts that matter at the start or the end of the prompt.

## What is context rot?

Context rot is the loss of accuracy as the input grows, wherever the important part sits. Chroma's [technical report](https://www.trychroma.com/research/context-rot) of July 14, 2025 tested 18 models and made the term common.

The term context rot is a month older than Chroma's report. Simon Willison [credits a Hacker News comment](https://simonwillison.net/2025/Jun/18/context-rot/) with coining it in June 2025.

Chroma's report tests a common assumption, that a model handles its 10,000th token as reliably as its 100th. The report found that models don't use their context evenly, and that they get less reliable as the input gets longer.

Chroma sells a retrieval database, so it has a reason to find that stuffing the window fails. Anthropic has the opposite incentive, because it sells the tokens, and its docs now say the same thing: "As token count grows, accuracy and recall degrade, a phenomenon known as context rot."

The way a model fails on a long input also differs by vendor. On questions with distracting passages, the report found Claude models tending to abstain when unsure, and GPT models more often answering wrongly with confidence.

## What does a long context cost?

A long context costs money on every call and adds time before the first word of the reply. Input tokens are billed each time they are sent, and a chat that resends its history pays for the early turns again and again.

My [token budgets guide](/articles/llm-token-budgets/) runs the arithmetic on a 20-turn chat, where the last turn costs 3.6 times the first. The wait before the reply grows as well, since the model has to read the whole prompt before it answers, the phase that [time to first token](/articles/time-to-first-token/) measures.

## Should you use a long context or retrieval?

Use the window for material that has to be read together, and retrieval for material that has to be found. A contract and the question about it belong in one prompt, and a library of ten thousand documents doesn't.

Retrieval puts a few passages in front of the model, which keeps the input short. It can also miss the right passage, and [contextual retrieval](/articles/contextual-retrieval/) is one way to reduce that failure at indexing time.

Inside a long session there's a third option, which is to shrink the history that is already in the window. Compaction replaces old turns with a summary, and [short-term memory for agents](/articles/short-term-agent-memory/) covers what that can lose.

## How should you fill a large window?

Treat the window's size as an upper limit, and choose each thing you put into it. Anthropic's own page says that choosing what goes into the context matters as much as how much room there is.

- Send what the task needs, and leave out documents included in case they help.
- Place instructions and key facts at the start or the end.
- Count tokens before sending, so a request is refused by your code and not by the API.
- Measure answers at the lengths you will run, since a prompt that works at 2,000 tokens tells you little about 200,000.

Some models keep count of the window for you. Anthropic lists four, including Sonnet 5 and Haiku 4.5, that keep track of how much window is left through a conversation, and says its newer ones take an explicit task budget instead.

## FAQ

**What is a context window in an LLM?**

A context window is the text the model can read at once, measured in tokens, including the prompt, the conversation history and the reply being generated.

**Is a bigger context window always better?**

No. A 2023 paper, a 2025 report and Anthropic's own documentation all say that accuracy falls as the input grows.

**What happens when the context window is full?**

An input that is too long on its own is rejected, and on newer Claude models a reply that runs into the limit stops early with a stop reason. Applications avoid both by counting tokens and by trimming or compacting old turns.
