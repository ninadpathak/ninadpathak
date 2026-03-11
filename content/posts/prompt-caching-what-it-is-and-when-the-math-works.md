---
title: "Prompt caching: what it is and when the math works in your favor"
date: 2026-03-07
description: "Prompt caching can cut latency and input cost, but only when your prompts share a stable prefix often enough to make cache reuse real. Here is how I think about it in production."
tags: [ai, llm, prompt-caching, inference]
status: published
---

Prompt caching sounds great in theory because the pitch is simple. Reuse the expensive part of the prompt, cut latency, lower cost, move on.

The catch is that it only works when the reusable part of the prompt is actually stable. If your app keeps rebuilding the top of the prompt, changing document order, or stuffing dynamic context too early, the savings disappear fast.

Here is the short version.

> Prompt caching reduces the cost of repeatedly processing the same prompt prefix. It works best when long instructions, tool definitions, examples, documents, or conversation history stay identical across requests. The math works when the reusable prefix is large, the requests recur within the cache lifetime, and the uncached tail is relatively small.

## What prompt caching actually does

A language model has to process the input prompt before it can generate output. That prefill work is expensive when the prompt is large. Prompt caching lets the system reuse that work when the beginning of the prompt is identical across requests.

OpenAI’s [prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) says this directly. Requests with the same prefix can be routed to a machine that already processed that prefix, making the request cheaper and faster than processing the prompt from scratch.

The same idea shows up elsewhere.

- Anthropic’s [prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) describe caching across `tools`, `system`, and `messages` up to the block marked with `cache_control`.
- Google’s [Gemini context caching docs](https://ai.google.dev/gemini-api/docs/caching) split the feature into implicit and explicit caching.
- vLLM’s [automatic prefix caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/) exposes the same principle in self-hosted serving.

So the core idea is not vendor-specific. It is an inference optimization around shared prefixes.

## The important detail is prefix, not prompt

This is the part that decides whether caching helps.

OpenAI says cache hits are possible only for exact prefix matches. Anthropic says cache hits require 100 percent identical prompt segments up to the cached block. Gemini recommends placing large common content at the beginning of the prompt.

That means prompt caching does not care that two requests are conceptually similar. It cares that the reusable section is byte-for-byte or token-for-token identical in the right place.

That one detail changes how I design prompts.

| Prompt pattern | Cache-friendly | Why |
| --- | --- | --- |
| Long system prompt first, user tail last | Yes | Stable instructions sit in the prefix |
| Tool definitions repeated identically | Yes | Tools become reusable prefix material |
| Retrieved documents inserted in random order | No | Prefix changes even when content is similar |
| Dynamic timestamps near the top | No | Small variations break the shared prefix |
| Long conversation history reused across turns | Often | Shared history can be prefetched and reused |

This is why prompt caching is partly an application design problem, not just an API feature.

## The headline numbers are real, but conditional

OpenAI says prompt caching can reduce latency by up to 80 percent and input token costs by up to 90 percent. Those are strong numbers. They are also best-case numbers.

The conditions matter.

OpenAI’s guide says caching kicks in automatically for prompts that are 1024 tokens or longer. Anthropic’s docs describe a default 5-minute cache lifetime, with an optional 1-hour cache at additional cost. OpenAI’s in-memory retention generally lasts 5 to 10 minutes of inactivity, sometimes up to 1 hour, and some models support extended retention up to 24 hours.

So when I read `up to 80 percent`, I translate that into a more useful question:

**How much of my prompt is large, repeated, and reused within the cache window?**

That is the real variable.

## When the math actually works

I think about prompt caching as a ratio problem.

The bigger the reusable prefix, the more there is to save. The more often that prefix repeats within the cache lifetime, the more often the savings show up. The smaller the variable tail, the more the request benefits from reuse.

The math tends to work when most of these are true:

- the prompt has a long stable prefix
- the same prefix appears across many requests
- requests land close enough together to stay within the cache lifetime
- the uncached tail is small relative to the cached section
- the system is latency-sensitive enough that faster prefill matters

The math usually does **not** work when most of these are true:

- every request rewrites the top of the prompt
- the shared content is short
- requests are too sparse to keep caches warm
- most of the cost sits in output generation, not input prefill
- the application injects dynamic context before the stable instructions

That last one is more common than it should be.

## The best prompt caching workloads

The vendor docs line up on the kinds of workloads that benefit.

Anthropic calls out long conversations, coding assistants, document-heavy prompts, and agentic tool use. vLLM highlights long-document querying and multi-round conversations. Gemini points to repeated input tokens and explicit cached corpora.

Those cases share a structure.

### 1. Long system instructions

If your application repeats a large system prompt, style guide, policy block, or tool schema on every call, caching can remove a lot of redundant prefill work.

### 2. Code assistants and agent systems

These systems often resend a stable instruction set, tool definitions, and working context across many turns. Anthropic explicitly mentions coding assistants and agentic tool use here, and that makes sense. The stable prefix is usually large.

### 3. Document Q and A

If users keep asking questions about the same large document, caching becomes powerful. vLLM describes this case directly. Process the large document once, then reuse that prefix for follow-up questions.

### 4. Multi-turn conversations

When a conversation retains a large shared history, prefix reuse can cut both latency and cost. vLLM and Anthropic both call this out.

## The hidden reason caching fails

The feature usually fails for boring reasons.

The prompt is not actually stable.

That can happen in a lot of ways:

- documents are inserted in a different order
- JSON keys get serialized differently across calls
- timestamps or request IDs sit near the top of the prompt
- tools are included conditionally and shift the prefix
- user-specific context gets inserted before the stable instructions

Anthropic’s docs are particularly useful here because they spell out how easy it is to invalidate a cache. Changes to `tool_choice`, image presence, block locations, or even unstable key ordering in `tool_use` payloads can break reuse.

This is why I think prompt caching rewards disciplined prompt assembly more than clever prompting.

## OpenAI, Anthropic, Gemini, and vLLM do not behave exactly the same way

The underlying idea is the same. The details differ enough to matter.

| System | Important detail |
| --- | --- |
| OpenAI | Automatic for prompts 1024 tokens and longer, exact prefix matching, optional `prompt_cache_key`, overflow effects above roughly 15 requests per minute per prefix-key combination |
| Anthropic | Explicit `cache_control`, caching across `tools`, `system`, and `messages`, default 5-minute TTL, optional 1-hour TTL |
| Gemini | Implicit and explicit caching, TTL on explicit caches, cache-hit counts visible in usage metadata |
| vLLM | Prefix caching only reduces prefill, not decode, and works best when large prefixes repeat |

That difference matters because the application strategy should follow the platform behavior.

If I am working with Anthropic, I care more about explicit cache breakpoints and block ordering. If I am on OpenAI, I care more about exact prefix construction, prompt length thresholds, and whether `prompt_cache_key` will improve routing. If I am self-hosting with vLLM, I care about whether the workload is prefill-heavy enough to benefit at all.

## Prompt caching is not a throughput trick only

People often describe caching as a cost optimization. It is that. It is also a latency optimization.

OpenAI frames it as both. Anthropic explicitly says you will generally see improved time to first token for long documents. That is the more interesting effect for interactive products.

If the model no longer has to reprocess a long shared prefix, the first visible output can show up faster. That matters in chat, copilots, and document-heavy assistants.

I wrote separately about [why TTFT often matters more than throughput for interactive products](/blog/time-to-first-token-ttft/). Prompt caching fits directly into that argument because it attacks prefill cost, which is a major component of first-token latency.

## Caching does not fix everything

Prompt caching only helps with the reused part of the input. It does not change how long the model takes to generate new output.

vLLM’s docs state this cleanly. Automatic prefix caching reduces the processing time of the query, the prefilling phase, but does not reduce decoding time. That means the benefit shrinks when responses are very long or when most of the time is spent generating tokens.

This is the easiest mistake to make with the feature. A team sees large latency numbers, enables caching, then expects every request to feel faster. If the application spends most of its time in generation rather than prefill, the gains will be smaller.

That is why I separate workloads like this:

| Workload | Caching impact |
| --- | --- |
| Long shared prompt, short answer | High |
| Large document Q and A | High |
| Agent loop with repeated tool definitions | High |
| Short prompt, long generated report | Limited |
| Requests with highly dynamic prompt prefixes | Limited |

## A practical design checklist

If I wanted prompt caching to work in production, I would design for it explicitly.

1. **Move stable instructions to the front.**
2. **Keep dynamic user-specific data at the end.**
3. **Keep serialization stable.**
4. **Do not shuffle documents or tools without a reason.**
5. **Measure cache-hit tokens and latency, not just total tokens.**
6. **Check whether requests arrive frequently enough to keep the cache useful.**

OpenAI exposes cached-token details in usage. Gemini exposes cache-hit counts in usage metadata. Anthropic exposes cache read and cache creation token counts. If the platform gives you cache metrics and you are not logging them, you are flying blind.

## The best mental model

My mental model is simple.

Prompt caching is not a magic acceleration layer for prompts in general. It is a discount on repeated prefill work.

If the expensive part of your request sits in a stable prefix, caching can be one of the cleanest wins in the stack.

If your prompt assembly is chaotic, the feature will mostly sit there looking impressive in the docs.

## Frequently asked questions

### Does prompt caching change model output?

No. Anthropic’s docs say output generation is unaffected, and OpenAI describes caching as reuse of prompt processing rather than a change in the generated response. The model still computes the answer fresh.

### Does prompt caching help short prompts?

Usually not much. OpenAI says automatic caching applies to prompts of 1024 tokens or more. Even when a platform reports cached tokens for smaller requests, the savings are limited if the repeated prefix is tiny.

### Is prompt caching mainly about cost or latency?

Both. The strongest cost savings show up when large prefixes repeat. The strongest latency gains show up when prefill is a large part of the request, which is common in long-prompt interactive systems.

### Should I rely on caching instead of shortening prompts?

No. I would still simplify prompts where possible. Caching helps repeated work. It does not excuse unnecessary work.

### When should I use a longer cache TTL?

Anthropic’s docs give a practical answer. Use the default short cache when prompts recur frequently enough to refresh it. Reach for longer TTLs when requests are less frequent but still predictable enough that reuse will happen before the longer window expires.
