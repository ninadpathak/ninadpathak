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
title: 'Time to First Token (TTFT): What It Measures and What It Misses'
slug: time-to-first-token
updated: 2026-11-17
---

Time to first token (TTFT) is the time from sending a request to a language model to receiving the first token back. It is the number people quote for how fast an application feels, and it holds up as long as the first token is something the user can see.

Web performance has been through this with Time to First Byte. web.dev's [TTFB guide](https://web.dev/articles/ttfb), first published in October 2021, says the metric "precedes every other meaningful loading performance metric", and then tells readers how much weight to give it: "Because TTFB isn't a Core Web Vitals metric", a site doesn't have to hit the good threshold if the metrics that follow are healthy.

A first byte arrives before anything is painted. Reasoning models have put TTFT in that position, because their first token can be thinking that never reaches the screen.

TTFT and tokens per second are the two numbers that [LLM inference](/articles/ai-engineering/) is tuned against, and the first of them is the subject here.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/time-to-first-token/ttft-chain.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/time-to-first-token/ttft-chain.narrow.svg" width="288" height="704"><img class="np-has-narrow" src="/static/images/diagrams/time-to-first-token/ttft-chain.svg" width="720" height="288" alt="The latency chain to the first token: the request crosses the network, waits in the queue, and the model prefills the prompt; together those make up time to first token. After the first token, generation streams the rest at the model's throughput." loading="lazy" decoding="async"></picture></a>
  <figcaption>Time to first token covers the network trip, the queue and the pass that reads the prompt, and generation starts after it.</figcaption>
</figure>

## What does time to first token measure?

Measured at the client, TTFT is the network trip, the wait in the server's queue and the pass in which the model reads the prompt. That last phase is called prefill, and it grows with the length of the input.

Definitions differ on the network. Modelplane's [inference field guide](https://docs.modelplane.ai/guides/inference-guide), which gives its figures as of October 2026, defines TTFT from the server's side as "Queueing plus prefill", with no network term.

The web metric has the same split, since web.dev lists redirects, DNS lookup and connection setup among the phases TTFB adds up. A TTFT number is only comparable with another one measured from the same place.

## Why is TTFT misleading for reasoning models?

A reasoning model starts emitting tokens long before it starts answering, and the usual TTFT counts the first of them. Artificial Analysis publishes two numbers for that reason, and its [methodology page](https://artificialanalysis.ai/methodology) says of time to first token that "For reasoning models which return reasoning tokens, this will be the first reasoning token."

Its second metric, time to first answer token, "includes the time spent reasoning". On November 17 its page for [Claude Fable 5.2](https://artificialanalysis.ai/models/claude-fable-5-2) gave that figure at each of the model's effort settings.

| Effort setting | Time to first answer token, seconds |
| --- | --- |
| Low | 7.22 |
| Medium | 9.20 |
| High | 23.65 |
| Extra high | 48.22 |
| Max | 208.11 |

Those are Artificial Analysis's measurements on Anthropic's API, and this page adds none of its own. The spread is what I take from them: one model, and a wait that differs by a factor of about 29 depending on a parameter the caller sets.

So the wait before an answer is a product decision before it is a serving problem. A team that picks the highest setting has chosen a wait of minutes, and no change to the queue will bring it back.

## How does TTFT behave under load?

It can stay flat while the service gets much slower. NVIDIA's [two-station GLM-5.3 tutorial](https://developer.nvidia.com/blog/when-one-gpu-isnt-enough-serving-glm-5-3-across-two-nvidia-dgx-stations-with-vllm/) from November 13 reports TTFT and full request latency at four concurrency levels, and the last column is my division of one by the other.

| Concurrent requests | Mean TTFT, ms | Mean request latency, s | TTFT as a share of the wait |
| --- | --- | --- | --- |
| 1 | 479.75 | 49.84 | 0.96% |
| 8 | 433.79 | 114.17 | 0.38% |
| 16 | 482.90 | 136.46 | 0.35% |
| 32 | 899.36 | 453.54 | 0.20% |

Between one request and sixteen the first token arrives in under half a second every time, and the full response goes from 50 seconds to 136. An alert on TTFT would have stayed green through a near tripling of the wait.

NVIDIA adds a note under the table that "TTFT measures time to the first token, which may be reasoning". On this workload the first token was under one percent of what the user waited for, so I'd treat TTFT here as a health check on the queue and nothing more.

## Is TTFT the same as throughput?

No. TTFT is set by queueing and prefill, and throughput is set by decoding, the phase that produces tokens one after another.

The two respond to different fixes. [Speculative decoding](/articles/speculative-decoding/) raises tokens per second and leaves the first token where it was, and the cache that decoding reads from is the subject of the [KV-cache article](/articles/kv-cache-eviction/).

## What lowers time to first token?

A shorter prompt, a cached prompt prefix and a shorter queue all lower it. Each maps to one phase.

- **Shorter prompt.** Prefill reads the whole input, so retrieved documents and tool definitions that aren't needed cost time before the first token.
- **Prefix caching.** A prompt opening that repeats across requests can be read once and reused, and Modelplane's guide says the feature is on by default in vLLM and SGLang.
- **Less queueing.** A request that waits behind others adds that wait to its TTFT, which is the jump at 32 concurrent requests in NVIDIA's table.

The wider set of serving choices is in the [LLM inference optimization guide](/articles/llm-inference-optimization/).

## How should you measure TTFT?

Measure it at the client and report percentiles, since a mean hides the slow requests that users remember. For any model that reasons, record time to first answer token beside it.

Modelplane's guide has the rule in one line: "Measure the first token the user sees." The web's version of that rule is why TTFB sits outside the Core Web Vitals, and I expect TTFT to end up in the same supporting role.
