---
title: "Time to first token: what TTFT measures and how to reduce it"
date: 2026-03-08
description: "TTFT is the latency metric that matters most for chat, copilots, and interactive AI apps. Here is what time to first token measures and how to reduce it without optimizing the wrong thing."
tags: [ai, llm, latency, inference]
status: published
---

If your assistant feels slow, users notice it before they care why. They are not thinking about throughput or model size. They are waiting for the first useful sign that the system is alive.

That delay has a name: **time to first token**, or **TTFT**.

It measures how long the system takes to start responding. A model can stream quickly once it gets going and still feel slow if it waits too long before the first token.

For interactive products, TTFT is usually the first latency metric I would fix. The main levers are smaller models, shorter prompts, cache reuse, better placement, and less queueing. Throughput work comes later.

## What TTFT actually measures

TTFT is the time between sending a request and receiving the first generated token back from the model.

That sounds neat because it collapses several steps into one number. The actual path is longer:

- the request travels from the client to the inference service
- the request may wait in a queue
- the system tokenizes and validates the prompt
- the model runs the **prefill** pass over the input
- the server schedules the first decode step
- the first token travels back to the client

The [OpenAI latency optimization guide](https://platform.openai.com/docs/guides/latency-optimization) treats latency as a mix of model choice, prompt size, and infrastructure behavior. That framing is the right one. TTFT is not one operation. It is a visible summary of several operations that happen before generation starts.

When the first token arrives late, the delay can come from network distance, queueing, prompt size, model size, cache misses, or server scheduling. The top-line number alone does not tell you which one is responsible.

## TTFT is not the same as throughput

These metrics get blurred together too often.

| Metric | What it measures | What it changes in the product |
| --- | --- | --- |
| **TTFT** | Delay before the first token appears | Whether the app feels responsive at the start |
| **Throughput** | Tokens generated per second after generation begins | How fast long answers stream |
| **Total latency** | Time until the entire response completes | End-to-end wait time |

A system can do well on throughput and still feel slow.

Suppose one path starts streaming in 350 milliseconds and emits 65 tokens per second. Another path starts in 2.1 seconds and emits 140 tokens per second. The second path wins on raw generation speed. The first path usually feels better in chat because the user sees output immediately.

That is the practical distinction. Once output is flowing, the interface has already crossed an important threshold. A long pause before that point creates more friction than a slightly slower stream after it.

## Why interactive apps should optimize TTFT first

Interactive products run on short loops. A user asks a question. A coding assistant suggests a fix. A support tool drafts a reply. An internal agent reports status. In each case, the model is part of a live workflow, not an offline batch job.

That changes the performance target.

For a batch summarization job, I care more about total runtime, cost, and tokens per second. For a streamed assistant, I care first about whether it starts quickly enough to keep the workflow moving.

TTFT usually matters most in products like these:

- chat assistants
- code copilots
- agent dashboards with live progress
- support tools that draft replies
- search products that stream synthesized answers
- internal AI tools used many times per hour

Throughput usually matters more in:

- offline summarization pipelines
- report generation jobs
- document processing queues
- evaluation runs
- asynchronous workloads where nobody watches the response stream live

The metric should match the workload. That sounds obvious, but a lot of latency work goes wrong right here.

## What sits inside TTFT

When I am debugging TTFT, I split it into stages.

| Stage | What happens | Common source of delay |
| --- | --- | --- |
| Network ingress | Request reaches the model service | Long physical distance, slow gateways |
| Queueing | Request waits for compute | Load spikes, oversubscribed GPUs |
| Prompt processing | Input is tokenized and prepared | Large prompts, tool-heavy contexts |
| Prefill | Model reads the input prompt | Large context windows, large models |
| First decode step | Model generates the first output token | Model compute cost, server scheduling |
| Network egress | First token reaches the client | Streaming path overhead |

This breakdown matters because each stage has different fixes. Prompt compression helps prefill. Regional placement helps network time. Warm capacity helps queueing. Speculative decoding helps when decode is the limiting factor.

Without that split, optimization turns into guesswork.

## Model size is usually the first real lever

The cleanest TTFT improvement is often model selection.

Before a model can emit anything, it has to read the prompt. Larger models generally make that first pass more expensive. Long prompts make the effect worse. A heavier model may still be the right choice for deep analysis, but that does not make it the right default for a short interactive turn.

I usually frame the decision with three questions:

- does this request need the strongest model available
- does it need that model on the first turn
- can a faster model handle the interaction and escalate only when necessary

That is a better starting point than treating model quality as one ranking.

The [OpenAI latency guide](https://platform.openai.com/docs/guides/latency-optimization) connects model choice directly to latency. That is not just an API concern. It is an architectural one. If every request routes to the biggest model by default, TTFT usually pays for it.

For interactive paths, I prefer a tiered setup:

| Request type | Better default |
| --- | --- |
| Short Q&A | Small or medium model with strong instruction following |
| Code suggestions | Fast coding model tuned for short turns |
| Agent planning | Mid-tier model, escalate when needed |
| Long analysis | Larger model where total quality matters more than start time |

A lot of TTFT work disappears once routing becomes sane.

## Prompt size is a TTFT tax

Prompt length is one of the easiest TTFT costs to introduce and one of the hardest to notice once it becomes normal.

Conversation history grows. Retrieval systems add more chunks. Tool descriptions expand. System prompts accumulate policy, style, product context, and fallback instructions. Each change looks minor in isolation. The model still has to read all of it before it can answer.

When I look at a slow interactive path, these are the first questions I ask:

- does the request need the full conversation history
- are retrieved chunks ranked tightly enough
- are tool descriptions longer than they need to be
- is the system prompt doing work that belongs elsewhere
- is stale context hanging around because nobody pruned it

Shorter prompts are not automatically better. If you remove the context that makes the answer correct, the product gets faster and worse. The goal is to stop rereading irrelevant material on every turn.

## Prompt caching changes the economics of repeated context

Once a prefix repeats across requests, caching becomes one of the strongest practical TTFT levers.

Both [Anthropic prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) and [OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching) are built around the same idea: if the stable part of the prompt has already been processed, the platform can reuse that work instead of paying the full prefill cost again.

On the self-hosted side, vLLM documents [automatic prefix caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html), which applies the same idea at the serving layer.

This matters most when you have:

- long stable system prompts
- repeated tool definitions
- shared policy text across requests
- similar multi-turn structures where only the tail changes

Caching rewards prompt discipline. If the stable instructions sit in a consistent prefix, the system can reuse them. If the prompt gets rebuilt differently every time, the opportunity disappears.

## Speculative decoding helps, but not with every TTFT problem

Speculative decoding works by having a smaller draft model predict candidate tokens and a larger model verify them. When the guesses line up, generation moves faster.

vLLM’s [speculative decoding documentation](https://docs.vllm.ai/en/latest/features/spec_decode.html) is a useful reference for how the serving path works.

The practical limit is simple. Speculative decoding helps when decode speed is the bottleneck. It does not fix queueing, long cross-region hops, or prompt-heavy prefill.

I would reach for it after answering two questions:

1. Is decode a meaningful part of the delay before the response feels usable?
2. Have I already reduced prompt and placement overhead?

If the answer to the second question is no, there are usually easier wins first.

## Placement still matters

TTFT is shaped by distance and contention.

If the user is in one region and the model runs in another, the request has to cross that distance twice before the first token appears. If the serving fleet is saturated, the request waits. If the system has to cold-start a worker or load weights under pressure, the user waits longer.

That is why placement and capacity planning belong in any serious TTFT discussion.

These checks are worth doing early:

- is the inference endpoint close to the users who need low latency
- is the traffic pattern creating queue spikes at peak time
- is autoscaling slow enough to expose cold paths
- is batching tuned for utilization at the expense of per-request responsiveness
- is a gateway or proxy adding work that the user does not benefit from

Many serving optimizations improve machine efficiency. That does not mean they improve the first moment of the product experience.

## Throughput optimizations and TTFT optimizations are different work

Some changes improve the time before the first token. Some improve generation after it starts. A few help both.

| Optimization | Helps TTFT | Helps throughput | Notes |
| --- | --- | --- | --- |
| Smaller model | Yes | Often | Best first check for interactive paths |
| Shorter prompts | Yes | Sometimes | Mainly reduces prefill cost |
| Prompt or prefix caching | Yes | Sometimes | Strong when prompts share a stable prefix |
| Regional placement | Yes | No | Cuts network delay and can reduce queueing |
| Warm capacity | Yes | No | Avoids queue spikes and cold starts |
| Speculative decoding | Sometimes | Yes | Best when decode is the constraint |
| Large dynamic batching | Often no | Yes | Can make TTFT worse |

For interactive systems, I start on the TTFT side of that table before I chase throughput.

## A practical order for TTFT work

When I need to reduce TTFT, I use this order:

1. **Measure TTFT separately from total latency.** A blended number hides too much.
2. **Check queueing and regional placement.** If the request is waiting before execution, model tweaks will not save it.
3. **Measure prompt size and prefill cost.** Large contexts explain more latency than teams expect.
4. **Test a smaller or faster model.** This can cut both prefill and decode cost.
5. **Introduce prompt or prefix caching where the prefix is stable.**
6. **Explore speculative decoding if decode still limits responsiveness.**

This order avoids a common mistake: reaching for a sophisticated serving trick before confirming that the prompt is twice as large as it should be.

## How to measure TTFT without fooling yourself

TTFT sounds easy to measure, but client-side timing and server-side timing get mixed together quickly.

A useful measurement setup records:

- request sent timestamp
- first byte received timestamp
- first token rendered timestamp in the client
- total response completion timestamp
- queue time if the serving system exposes it
- prompt token count and output token count
- model name and region

Those fields let you answer concrete questions. If TTFT rises with prompt size, prefill is likely involved. If TTFT spikes only during high concurrency, queueing is a better suspect. If server-side first byte is stable but client render time is erratic, the issue may sit in the streaming path or frontend.

For products with multiple model routes, I also want TTFT broken out by route. One slow path can disappear inside an average.

## Where teams usually waste time

One failure mode shows up again and again. The team sees latency complaints and optimizes the easiest number to benchmark. That is often output tokens per second. The chart improves. The app still feels slow because the painful part was the wait before the first visible response.

Prompt growth is another trap. Retrieval adds more context. Tools add more schemas. Product logic adds more instructions. Quality can improve for a while, but TTFT drifts upward until the product feels heavier than it should.

The third trap is sending every request through one model path. That keeps routing simple, but it forces very different workloads into the same latency budget.

These are architectural mistakes, not tuning details.

## What I would optimize for different workloads

| Workload | Primary metric | Secondary metric |
| --- | --- | --- |
| Chat assistant | TTFT | Total latency |
| Coding copilot | TTFT | Suggestion quality |
| Agent progress UI | TTFT | Reliability |
| Async document summarization | Throughput | Cost |
| Batch evaluation pipeline | Throughput | Total runtime |
| Long report generation | Total latency | Cost |

A single stack can serve all of these workloads, but it should not treat them the same way. If one latency strategy gets applied to all of them, one class of workload will get a worse tradeoff than it needs.

## The practical takeaway

For interactive systems, TTFT is usually the first metric to fix.

The checklist is short:

- choose a model that fits the interaction, not just the benchmark
- keep prompts smaller and more stable than they naturally become over time
- use caching when repeated prefixes make it worthwhile
- keep inference close to the user and avoid avoidable queueing
- treat speculative decoding as a targeted optimization, not a default answer

Once those pieces are in place, throughput work becomes more useful.

## Frequently asked questions

### What is a good TTFT for an LLM app?

There is no single threshold that fits every product. For interactive apps, lower is usually better. Once the delay pushes past about a second, the pause becomes much more noticeable. The acceptable number depends on the value of the answer and how often the user has to wait for it.

### Is TTFT the same as first byte latency?

They are close, but not always identical. First byte latency refers to when the first byte arrives from the server. TTFT refers to when the first generated token becomes available. Streaming and client rendering can make those differ slightly.

### Does prompt caching always reduce TTFT?

No. It helps when requests share a stable prefix that the system can reuse. If the prompt structure changes significantly each time, the cache hit rate may be too low to matter.

### Does speculative decoding always improve responsiveness?

No. It helps when decode speed is a meaningful bottleneck. If the delay is mostly queueing, network time, or prefill, the impact on TTFT will be limited.

### Should I optimize TTFT or total latency first?

For interactive apps, I would usually start with TTFT because it drives perceived responsiveness. For offline or asynchronous workloads, total latency and throughput are often more important.
