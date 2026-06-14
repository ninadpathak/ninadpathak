---
date: 2026-03-13
description: Prompt caching can reduce LLM costs by up to 90% and cut latency by half.
  Here is the engineering guide to how it works, why prefix matching matters, and
  how to calculate your ROI.
status: published
tags:
- ai
- llm
- infrastructure
title: 'Prompt Caching: What It Is and When the Math Works'
---

Inference cost is what stops most LLM applications from scaling cheaply. Every standard API call makes the model re-read your entire prompt from scratch, which is pure waste when most of that prompt is the same on every request. I run an agent whose system block and tool definitions add up to roughly 12,000 tokens that never change, and without caching I was paying to process those 12,000 tokens on every single turn.

Prompt caching fixes that by persisting the intermediate state of the model's computation so you can reuse the work it already did. Whether you actually save money comes down to one mechanism: prefix matching. Get that wrong and caching does nothing for you in production.

## What prompt caching actually does

Caching stores the [Key-Value (KV) cache of a prompt prefix](/blog/kv-cache-eviction-accuracy/) in memory or on disk. That KV cache is the model's compressed summary of every token it has read so far, a bit like a chef who has already chopped and measured all the standing ingredients and only needs to add today's special order. When a new prompt shares an identical prefix with a cached one, the model skips the prefill phase entirely and goes straight to generating new tokens, which is why caching is one of the strongest tools for [cutting time to first token](/blog/time-to-first-token-ttft/).

<div class="visual-wrapper">
  <div class="visual-title">PROMPT CACHING</div>
  <div class="visual-container">
    <iframe src="/static/visuals/prompt-caching.html" title="First call writes the cache for a static prefix, later calls hit it and skip prefill, dropping cost up to 90 percent and latency about 50 percent" loading="lazy"></iframe>
  </div>
</div>

Systems with long system instructions or large retrieved datasets benefit the most. You pay the full prefill price once, and every request after that pays only for the unique tokens you appended at the end. For a RAG pipeline that prepends the same 40-page policy document to every question, or an agent that resends its full instruction set each turn, that shift in economics is the difference between a feature that ships and one that gets cut for being too expensive.

## The detail that trips everyone up: prefix, not prompt

A common wrong assumption is that caching works like a key-value store keyed on the whole prompt, so any two requests that differ at all get separate entries. What actually happens is finer-grained than that. The cache matches on the prefix. Given a prompt made of a system block, a knowledge block, and a user query, you get a cache hit as long as those first two blocks are byte-for-byte identical, even though the query at the end changes every time.

Change anything near the start of the prompt and you invalidate the entire cache for that request, because the prefix the model would match against no longer exists. Think of it like a book index that points at page numbers: insert one paragraph on page 2 and every page reference after it is wrong. That sensitivity forces a specific ordering on you, from most static to most dynamic. System instructions go first, background data follows, and the user's unique query sits dead last. The first time I shipped caching I interpolated the current timestamp into the system prompt header and watched my hit rate sit at zero for a day before I found it.

## When caching actually pays for itself

Caching is not free. Providers usually charge a write premium to store the cache (Anthropic, for example, bills cache writes at roughly 1.25 times the normal input rate) or require a minimum prefix length before anything caches at all. You also need enough traffic to keep the cached prefix warm in the provider's memory, since these entries expire after a few minutes of disuse and a cold cache earns you nothing.

Working out the return comes down to two numbers: your cache hit rate and the ratio of static tokens to dynamic ones, both of which slot neatly into a broader [practical approach to LLM cost control](/blog/llm-token-budgets-cost-control/). A chatbot with a 10,000-token static prefix and a 100-token user query saves a fortune even at low volume, because 99 percent of every request is the same bytes served at a tenth of the price. Run a workflow where the prefix changes on every call, though, and you save nothing and may end up paying the write premium on cache entries that nobody ever reads back.

## Provider differences

OpenAI, Anthropic, and Gemini each implement caching with different rules. A few cache automatically based on common prefixes they detect across your traffic, and others make you explicitly flag which blocks should be cached.

The most flexible implementation I have worked with is Anthropic's. You place "cache breakpoints" at specific points in the prompt (up to four of them per request), which hands you direct control over exactly what stays in memory and where the cached span ends. OpenAI leans the other way, caching automatically with no markers to manage, which is less work to set up and gives you less to tune when you are trying to squeeze a cost number down.

## A practical design checklist

Three rules cover most of what I check before shipping a cached prompt.

**Order matters.** Push every dynamic value (timestamps, request IDs, the user's question) to the very end, behind everything stable.

**Standardize prefixes.** Watch for the silent invalidators that change your bytes without you noticing, like a stray trailing newline or a JSON object serialized with unsorted keys, since either one quietly resets your hit rate.

**Monitor hit rates.** Read the cache-read token count off your responses in production. When it sits at zero across requests that should share a prefix, you have a silent invalidator to hunt down, and that number is the only thing that tells you your assembly logic is actually working.

Done well, prompt caching is the cheapest way I know to scale an LLM application without watching cost climb in lockstep with traffic. It rewards teams that treat prompt assembly as an infrastructure problem with bytes that must line up, rather than as a string you paste together and hope for the best.