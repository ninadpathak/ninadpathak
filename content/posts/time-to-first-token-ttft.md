---
title: "Time to first token: what TTFT measures and how to reduce it"
date: 2026-03-08
description: "TTFT is the latency metric that matters most for chat, copilots, and interactive AI apps. Here is what time to first token measures and how to reduce it without optimizing the wrong thing."
tags: [ai, llm, latency, inference]
status: published
---

In the early web, people obsessed over page load. That focus made sense because the first visible response shaped the whole interaction. LLM apps work the same way. In a chat UI or coding assistant, the moment that matters first is when the model starts answering.

That delay has a name: **time to first token**, or **TTFT**.

TTFT captures the start of the user experience, not the end of the computation. A model can stream quickly once it gets going and still feel slow if it waits too long before the first token.

For interactive products, TTFT is usually the latency metric to optimize first. The levers are straightforward: smaller models, shorter prompts, cache reuse, better placement, and less queueing. Throughput work comes later.

## What TTFT actually measures

TTFT is the time between sending a request and receiving the first generated token back from the model.

That definition is simple. The path underneath it is not.

Before the first token appears, several things have already happened:

- the request travels from the client to the API or inference server
- the request may sit in a queue waiting for compute
- the system tokenizes and validates the prompt
- the model runs the **prefill** pass over the input
- the server schedules the first decode step
- the first generated token comes back over the network

The [OpenAI latency optimization guide](https://platform.openai.com/docs/guides/latency-optimization) discusses latency as a combination of model choice, prompt size, and infrastructure behavior. That framing is useful because TTFT is not one operation. It is the visible result of several operations that happen before generation starts streaming.

This is why TTFT tuning gets messy. If the first token is late, the bottleneck could be network distance, queueing, prompt length, model size, cache misses, or server scheduling. Looking at the final number alone does not tell you which part is responsible.

## TTFT is not the same as throughput

Latency metrics get lumped together too often, so it helps to separate them.

| Metric | What it measures | What it changes in the product |
| --- | --- | --- |
| **TTFT** | Delay before the first token appears | Whether the app feels responsive at the start |
| **Throughput** | Tokens generated per second after generation begins | How fast long answers stream |
| **Total latency** | Time until the entire response completes | End-to-end wait time |

A system can do well on throughput and still feel slow.

Suppose one path starts streaming in 350 milliseconds and emits 65 tokens per second. Another path starts in 2.1 seconds and emits 140 tokens per second. The second path wins on raw generation speed, but the first one usually feels better in a chat product because the user sees life immediately.

That distinction is central to interactive systems. Once output is already flowing, the interface has crossed an important threshold. The user knows the system is working. A long pause before that point creates uncertainty, even if the remaining tokens arrive quickly.

## Why TTFT matters more for interactive apps

Interactive apps are built around short loops.

A user asks a question. A coding assistant suggests a fix. A support tool rewrites a reply. An internal agent returns a short status update. In each case, the product is part of a live workflow. The system is not producing a report that someone checks later. It is participating in a decision the person is making right now.

That changes the performance target.

For a batch summarization job, I would care about total runtime, cost, and tokens per second. For a streamed assistant, I care first about whether it starts quickly enough to stay out of the user’s way. If that first response drags, the interaction feels heavier than it should.

TTFT tends to matter most in products like these:

- chat assistants
- code copilots
- agent dashboards with live progress
- support tools that generate suggested replies
- search products that stream synthesized answers
- internal AI tools used many times per hour

Throughput tends to matter more in these cases:

- offline summarization pipelines
- report generation jobs
- document processing queues
- evaluation runs
- large asynchronous workloads where nobody watches the output stream live

This is not just a measurement problem. It is a product problem. The right metric depends on the shape of the workload.

## What sits inside TTFT

If I am debugging TTFT, I break it into stages. That is the only useful way to reason about it.

| Stage | What happens | Common source of delay |
| --- | --- | --- |
| Network ingress | Request reaches the model service | Long physical distance, slow gateways |
| Queueing | Request waits for compute | Load spikes, oversubscribed GPUs |
| Prompt processing | Input is tokenized and prepared | Large prompts, tool-heavy contexts |
| Prefill | Model reads the input prompt | Large context windows, large models |
| First decode step | Model generates the first output token | Model compute cost, server scheduling |
| Network egress | First token reaches the client | Streaming path overhead |

That table is useful because different interventions map to different stages.

Prompt compression helps prefill. Regional placement helps network time. Warm capacity helps queueing. Speculative decoding helps decode-heavy workloads. If those boundaries stay blurry, optimization turns into trial and error.

## Model size is often the first real lever

The cleanest TTFT improvement is often model selection.

Before a model can emit anything, it has to read the prompt. Larger models generally make that first pass more expensive. Long prompts amplify the effect. This means that a heavier model can be entirely reasonable for deep analysis and still be the wrong default for a fast interactive turn.

I would frame the decision like this:

- does this request need the strongest model available
- does it need that model on the first turn
- can a faster model handle the interaction and escalate only when necessary

That is a better starting point than treating model quality as a single ranking.

The [OpenAI latency guide](https://platform.openai.com/docs/guides/latency-optimization) makes an explicit connection between model choice and latency. That is not just an API concern. It is an architectural concern. If every request gets routed to the biggest model by default, TTFT usually pays the price.

For interactive paths, I prefer a tiered setup:

| Request type | Better default |
| --- | --- |
| Short Q&A | Small or medium model with strong instruction following |
| Code suggestions | Fast coding model tuned for short turns |
| Agent planning | Mid-tier model, escalate when needed |
| Long analysis | Larger model where total quality matters more than start time |

A lot of TTFT work disappears once routing becomes sensible.

## Prompt size is a TTFT tax

Prompt length is one of the easiest TTFT costs to introduce and one of the hardest to notice once it becomes normal.

Conversation history grows. Retrieval systems add more chunks. Tool descriptions expand. System prompts accumulate safety rules, style rules, product context, and fallback instructions. Each individual addition feels small. The prefill bill does not care how the prompt got large.

The model still has to read the whole thing before it says anything useful.

When I look at a slow interactive path, I usually ask these questions first:

- does the request need the full conversation history
- are retrieved chunks ranked tightly enough
- are tool descriptions longer than they need to be
- is the system prompt doing work that belongs elsewhere
- is stale context hanging around because nobody pruned it

This is where TTFT and response quality need judgment. Shorter prompts are not automatically better if they remove the information that makes the answer correct. The goal is not to starve the model. The goal is to stop making it reread irrelevant material on every turn.

## Prompt caching changes the economics of repeated context

Once a prefix repeats across requests, caching becomes one of the strongest practical TTFT levers.

Both [Anthropic prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) and [OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching) are built around a simple idea: if the stable part of the prompt has already been processed, the platform can reuse that work instead of charging the full prefill cost again.

On the self-hosted side, vLLM documents [automatic prefix caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html), which applies the same logic at the serving layer.

This matters a lot in products with:

- long stable system prompts
- repeated tool definitions
- shared policy text across requests
- similar multi-turn structures where only the tail changes

A good way to think about caching is that it rewards prompt discipline. If the stable instructions sit in a consistent prefix, the system can reuse them. If the prompt gets rebuilt differently every time, the opportunity disappears.

That means caching is not just an inference feature. It is also a prompt construction problem.

## Speculative decoding helps, but only for the right bottleneck

Speculative decoding gets attention because it sounds clever, and it is. A smaller draft model predicts candidate tokens. The larger model verifies them. When those predictions line up well, generation moves faster.

vLLM’s [speculative decoding documentation](https://docs.vllm.ai/en/latest/features/spec_decode.html) is a useful reference for the serving mechanics.

The important practical point is narrower.

Speculative decoding helps when decode speed is the issue. It is not a universal TTFT fix. If the first token is late because the request sat in a queue, crossed regions, or spent too long in prefill, speculative decoding will not address the main cause.

I would reach for it after answering two questions:

1. Is decode actually a meaningful part of the time before the response feels usable?
2. Have I already reduced prompt and placement overhead?

If the answer to the second question is no, there are usually easier wins available first.

## Placement matters because physics still matters

Some latency discussions become too abstract. TTFT is still shaped by distance and contention.

If the user is in one region and the model runs in another, the request has to cross that distance twice before the first token appears. If the serving fleet is busy, the request waits. If the system cold-starts a worker or loads weights under pressure, the user waits longer.

That is why placement and capacity planning belong in any serious TTFT discussion.

These checks are usually worth doing early:

- is the inference endpoint close to the users who need low latency
- is the traffic pattern causing queue spikes at peak time
- is autoscaling slow enough to expose cold paths
- is batching tuned for utilization at the expense of per-request responsiveness
- is a gateway or proxy adding work that the user does not benefit from

The reason teams get tripped up here is simple. Many serving optimizations improve machine efficiency. That does not guarantee they improve the start of the user experience. A more efficient cluster can still produce a slower-feeling product if single-request latency gets sacrificed in the process.

## Throughput optimizations and TTFT optimizations are different work

This is where engineers often lose clarity.

Some changes help throughput after generation has started. Some changes improve the time before the first token. A few help both. Many do not.

| Optimization | Helps TTFT | Helps throughput | Notes |
| --- | --- | --- | --- |
| Smaller model | Yes | Often | Best first check for interactive paths |
| Shorter prompts | Yes | Sometimes | Mainly reduces prefill cost |
| Prompt or prefix caching | Yes | Sometimes | Strong when prompts share a stable prefix |
| Regional placement | Yes | No | Cuts network delay and can reduce queueing |
| Warm capacity | Yes | No | Avoids queue spikes and cold starts |
| Speculative decoding | Sometimes | Yes | Best when decode is the constraint |
| Large dynamic batching | Often no | Yes | Can make TTFT worse |

That table is the heart of the article. If the system is interactive, I would start on the left side before I chase the right side.

## A practical order for TTFT work

When I need to reduce TTFT, I use an order that keeps the diagnosis honest.

1. **Measure TTFT separately from total latency.** A blended number hides too much.
2. **Look at queueing and regional placement.** If the request is waiting before execution, model tweaks will not save it.
3. **Measure prompt size and prefill cost.** Large contexts often explain more than teams expect.
4. **Test a smaller or faster model.** This can remove both prefill and decode cost.
5. **Introduce prompt or prefix caching where the prefix is stable.**
6. **Explore speculative decoding if decode still limits responsiveness.**

That order avoids a common failure mode. It is easy to reach for a sophisticated serving trick before confirming that the prompt is twice as large as it needs to be.

## How to measure TTFT without fooling yourself

Measuring TTFT sounds straightforward, but it is easy to mix client behavior and server behavior together.

A clean measurement setup should record:

- request sent timestamp
- first byte received timestamp
- first token rendered timestamp in the client
- total response completion timestamp
- queue time if the serving system exposes it
- prompt token count and output token count
- model name and region

Those fields let you answer practical questions instead of guessing.

If TTFT rises with prompt size, prefill is likely involved. If TTFT jumps only during high concurrency, queueing is the better suspect. If server-side first byte is stable but client render time is erratic, the issue may sit in the streaming path or frontend.

For products with multiple model routes, I also want TTFT broken out by route. One slow path can disappear inside an average.

## Where teams usually waste time

The pattern is not mysterious.

A team sees latency complaints. They optimize the thing that is easiest to benchmark. That often means output tokens per second. The chart improves. The app still feels slow because the user spends most of the painful interval waiting for the first visible response.

Another common mistake is treating prompt growth as free. Retrieval adds more context, then tools add more schemas, then product logic adds more instructions. Quality may improve for a while, but TTFT drifts upward until the system feels heavier than the value it returns.

The third mistake is pushing all traffic through one model path. That keeps routing simple, but it often collapses very different workloads into the same latency budget.

These are architecture choices, not minor implementation details.

## What I would optimize for different workloads

The right target depends on what the user is actually doing.

| Workload | Primary metric | Secondary metric |
| --- | --- | --- |
| Chat assistant | TTFT | Total latency |
| Coding copilot | TTFT | Suggestion quality |
| Agent progress UI | TTFT | Reliability |
| Async document summarization | Throughput | Cost |
| Batch evaluation pipeline | Throughput | Total runtime |
| Long report generation | Total latency | Cost |

A single stack can serve all of these workloads, but it should not treat them the same way. If the architecture forces one latency strategy across all of them, one class of workload will get a worse tradeoff than it needs.

## The practical takeaway

TTFT is the metric that tells you how quickly an LLM product starts responding. In interactive systems, that start matters a lot because it shapes the feel of the whole interaction.

If I had to compress the decision into a short checklist, it would be this:

- choose a model that fits the interaction, not just the benchmark
- keep prompts smaller and more stable than they naturally become over time
- use caching when repeated prefixes make it worthwhile
- keep inference close to the user and avoid avoidable queueing
- treat speculative decoding as a targeted optimization, not a default answer

Once those pieces are in place, throughput work becomes more meaningful. Before that, it is easy to build a system that looks efficient in a benchmark and still feels delayed in the product.

## Frequently asked questions

### What is a good TTFT for an LLM app?

There is no single threshold that fits every product. For interactive apps, lower is almost always better. Once the delay pushes past about a second, the pause becomes much more noticeable. The acceptable number depends on how much value the answer delivers and how often the user waits for it.

### Is TTFT the same as first byte latency?

They are close, but they are not always identical. First byte latency refers to when the first byte arrives from the server. TTFT refers to when the first generated token becomes available. In practice, streaming and client rendering can make those differ slightly.

### Does prompt caching always reduce TTFT?

No. It helps when requests share a stable prefix that the system can reuse. If the prompt structure changes significantly each time, the cache hit rate may be too low to matter.

### Does speculative decoding always improve responsiveness?

No. It is useful when decode speed is a meaningful bottleneck. If the delay is mostly queueing, network time, or prefill, the impact on TTFT will be limited.

### Should I optimize TTFT or total latency first?

For interactive apps, I would usually start with TTFT because it drives perceived responsiveness. For offline or asynchronous workloads, total latency and throughput are often more important.
