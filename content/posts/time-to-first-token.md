---
category: ai-engineering
primary_query: time to first token
siblings:
- kv-cache-eviction
- speculative-decoding
- llm-inference-optimization
date: 2026-03-08
description: 'Time to first token (TTFT) explained: what it measures, why reasoning models need time to first answer token, and how TTFT behaves under load.'
status: published
work_note: 'I''m a technical writer, and what I offer on time to first token is an explanation of what the number measures and where the wait comes from. For the developer content I''ve published, see [my portfolio](/portfolio/).'
title: 'Time to First Token (TTFT): The Metric That Determines AI Snappiness'
slug: time-to-first-token
updated: 2026-11-17
---

Web developers have measured the wait for a response with one number for years. Time to First Byte, in [web.dev's definition](https://web.dev/articles/ttfb), "measures the time between starting navigating to a page and when the first byte of a response begins to arrive", and a slow one means the server is the problem.

Time to first token (TTFT) is the same measurement for a language model: the time from sending a request to receiving the first token back. The parallel breaks in one place, because a web server's first byte is the start of the page and a reasoning model's first token can be thinking the user never sees.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/time-to-first-token/ttft-chain.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/time-to-first-token/ttft-chain.narrow.svg" width="288" height="704"><img class="np-has-narrow" src="/static/images/diagrams/time-to-first-token/ttft-chain.svg" width="720" height="288" alt="The latency chain to the first token: the request crosses the network, waits in the queue, and the model prefills the prompt; together those make up time to first token. After the first token, generation streams the rest at the model's throughput." loading="lazy" decoding="async"></picture></a>
  <figcaption>Prefill cost scales with prompt length: a 200-token question returns far faster than the same request with 40k tokens of retrieved documents in front of it.</figcaption>
</figure>

## What does time to first token measure?

TTFT measures everything that happens before the model starts to answer: the network trip, the wait in the queue and the pass that reads the prompt. Modelplane's [inference field guide](https://docs.modelplane.ai/guides/inference-guide) from November 10 defines it in six words, "Queueing plus prefill", and describes it as "how long the user waits before anything appears".

Prefill is the part the prompt controls. The guide says prefill "Reads the whole input in parallel, including the system prompt and tool definitions as well as the conversation history", so a longer prompt means a later first token.

## Why is TTFT misleading for reasoning models?

A reasoning model starts emitting tokens long before it starts answering, and the usual TTFT counts the first of them. Artificial Analysis now publishes two numbers for that reason, and its [methodology page](https://artificialanalysis.ai/methodology) says of time to first token that "For reasoning models which return reasoning tokens, this will be the first reasoning token."

Its second metric, time to first answer token, "includes the time spent reasoning", which lets it compare the wait for an answer across models that reason and models that don't.

The difference is large at the top of the leaderboard. On November 17 the site's page for [Claude Fable 5.2](https://artificialanalysis.ai/models/claude-fable-5-2) ranked the model first of 81 on its intelligence index and listed "Time to first answer token 208.11s".

A title like this page's, calling TTFT the metric that decides whether an application feels fast, is true for models that answer straight away. For a reasoning model the number to watch is the one Modelplane's guide names: "Measure the first token the user sees."

## How does TTFT behave under load?

It can stay flat while the service gets much slower, which makes it a poor overload alarm. NVIDIA's [two-station GLM-5.3 tutorial](https://developer.nvidia.com/blog/when-one-gpu-isnt-enough-serving-glm-5-3-across-two-nvidia-dgx-stations-with-vllm/) from November 13 reports both numbers at four concurrency levels.

| Concurrent requests | Mean TTFT, ms | Mean request latency, s |
| --- | --- | --- |
| 1 | 479.75 | 49.84 |
| 8 | 433.79 | 114.17 |
| 16 | 482.90 | 136.46 |
| 32 | 899.36 | 453.54 |

Between one request and sixteen the first token arrives in under half a second every time, and the full response goes from 50 seconds to 136. NVIDIA adds a note under the table that "TTFT measures time to the first token, which may be reasoning".

## Is TTFT the same as throughput?

No. TTFT is set by queueing and prefill, and throughput is set by decoding, and the two have different limits.

Modelplane's guide puts prefill on the compute side and decode on memory bandwidth, and draws the consequence: "Because the phases have opposite bottlenecks, a technique that speeds one often does little for the other. That is why benchmarks report TTFT and tokens per second separately."

[Speculative decoding](/articles/speculative-decoding/) is an example of the second kind, since it raises tokens per second and leaves the first token where it was. The [KV-cache article](/articles/kv-cache-eviction/) covers the memory that decoding reads.

## What lowers time to first token?

A shorter prompt, a cached prompt prefix and a shorter queue all lower it. Each maps to one part of the definition.

- **Shorter prompt.** Prefill reads the whole input, so retrieved documents and tool definitions that aren't needed cost time before the first token.
- **Prefix caching.** The guide describes it as a way to "Reuse the work already done on repeated prompt openings", and says it is on by default in vLLM and SGLang.
- **Less queueing.** A request that waits behind others adds that wait to its TTFT, which is the jump at 32 concurrent requests in NVIDIA's table.

The wider set of serving choices is in the [LLM inference optimization guide](/articles/llm-inference-optimization/).

## How should you measure TTFT?

Measure it at the client, to the first token the user can see, and report percentiles. A server-side number leaves out the network, and a mean hides what Modelplane's guide warns about: "Users feel the tail, not the average".

Record time to first answer token beside it for any model that reasons. I report no measurements of my own on this page, and its numbers come from the sources linked above.
