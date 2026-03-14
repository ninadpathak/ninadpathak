---
title: "Time to First Token (TTFT): The Metric That Determines AI Snappiness"
date: 2026-03-08
description: "Users do not care about total throughput. They care about how fast the first word appears. Here is the engineering guide to measuring and optimizing Time to First Token (TTFT) in production."
tags: [ai, llm, infrastructure]
status: published
---

Interactive AI applications live or die by perceived latency. A model might generate 100 tokens per second. Such speed is irrelevant if the user waits five seconds for the stream to start. Time to First Token (TTFT) is the metric that determines if your application feels "alive" or broken.

Understanding the components of TTFT is vital for performance engineering. It is not a single number. It is the result of a complex pipeline involving networking and queueing and model prefill.

<div style="margin: 3rem 0; background: transparent; border: 1px solid var(--border); overflow: hidden;">
  <iframe src="/static/visuals/ttft-breakdown.html" style="width: 100%; height: 400px; border: none;" scrolling="no"></iframe>
</div>

## What TTFT actually measures

TTFT measures the interval between a user sending a request and receiving the first generated token. This is different from "tokens per second," which measures the generation speed once the stream has started.

Prefilling the prompt is the primary driver of TTFT. The model must process all input tokens to build the initial KV cache. Such computation is a "one-time tax" paid at the start of every request. Longer prompts lead directly to higher TTFT.

## TTFT is not the same as throughput

High throughput is important for batch tasks like document parsing. Interactive chat requires low TTFT. You can often trade one for the other.

<div style="margin: 3rem 0; background: transparent; border: 1px solid var(--border); overflow: hidden;">
  <iframe src="/static/visuals/ttft-vs-throughput.html" style="width: 100%; height: 450px; border: none;" scrolling="no"></iframe>
</div>

Optimizing for throughput usually involves increasing batch sizes. Such a strategy allows the GPU to work more efficiently but increases the wait time for individual requests. Optimizing for TTFT requires smaller batches or dedicated compute resources to ensure immediate processing.

## Model size is the first real lever

The size of the model determines the baseline TTFT. A 7B parameter model will always generate the first token faster than a 400B model on identical hardware. This is because the smaller model requires fewer memory loads to process the input.

Choosing a smaller "distilled" model is the most effective way to drop TTFT if your reasoning requirements allow it. Many teams use a small model for the initial response and a larger model for background tasks. Such an architecture provides immediate feedback to the user without sacrificing depth.

## A practical order for optimization

Follow this hierarchy when tasked with reducing latency in production.

<div style="margin: 3rem 0; background: transparent; border: 1px solid var(--border); overflow: hidden;">
  <iframe src="/static/visuals/ttft-hierarchy.html" style="width: 100%; height: 400px; border: none;" scrolling="no"></iframe>
</div>

**Model Selection.** Start by choosing the smallest model that meets your quality bar. This is the "low-hanging fruit" of latency work.

**Prompt Caching.** Use caching to eliminate the prefill tax for static context. This can drop TTFT by 80% for repeated prefixes.

**Speculative Decoding.** Use a draft model to speed up the verification step. Such a technique improves snappiness by predicting multiple tokens in parallel.

**Quantization.** Reduce the precision of model weights to speed up memory loads. Moving from FP16 to INT8 or FP8 provides a meaningful boost with minimal accuracy loss.

## How to measure without fooling yourself

Do not rely on averages. Latency is defined by the "tail." Measure your p95 and p99 TTFT to understand what your unluckiest users are experiencing.

Track TTFT alongside prompt length. A p95 of 500ms is great for a 1k token prompt. Such a number is impossible for a 100k token prompt without caching. Successful engineers build dashboards that normalize latency metrics by context volume.

Perception is reality in AI engineering. You win when the first token appears before the user has finished their thought. Focus on TTFT to build applications that feel like magic.
