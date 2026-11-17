---
category: ai-engineering
primary_query: llm inference optimization
siblings:
- kv-cache-eviction
- time-to-first-token
- llm-structured-outputs
date: '2026-05-06'
description: 'LLM inference optimization in late 2026, covering which techniques are engine defaults, how to size the KV cache and where more throughput stops helping.'
slug: llm-inference-optimization
status: published
work_note: 'I''m a technical writer, and the measurements on this page come from the linked sources. [My portfolio](/portfolio/) shows the work I do for AI companies.'
title: 'LLM Inference Optimization: What Actually Works in Production'
updated: '2026-11-16'
---

At sixteen concurrent requests, two NVIDIA DGX Stations serving GLM-5.3 through vLLM produced 607.8 tokens per second, and at thirty-two they produced 385.0. Those figures come from [a tutorial NVIDIA published on November 13](https://developer.nvidia.com/blog/when-one-gpu-isnt-enough-serving-glm-5-3-across-two-nvidia-dgx-stations-with-vllm/), and the table they sit in is the best short lesson in inference optimization I've read this year.

LLM inference optimization is the work of serving more tokens per GPU at a latency users will accept, and that run shows where the work now sits. The run had prefix caching and an FP8 KV cache switched on, the batching and paging this page used to tell you to enable were already running, and doubling the load still made the whole system slower.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/llm-inference-optimization/inference-stack.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/llm-inference-optimization/inference-stack.narrow.svg" width="288" height="1040"><img class="np-has-narrow" src="/static/images/diagrams/llm-inference-optimization/inference-stack.svg" width="720" height="856" alt="The inference stack as layered slabs, top to bottom: serving engines (vLLM, TensorRT-LLM, SGLang); continuous batching, drawn as request lanes where a finished request frees its slot for a new one; Flash Attention, drawn as a score matrix streamed tile by tile into on-chip memory; quantization, drawn as one weight at 16, 8, and 4 bits; the paged KV cache, drawn as three sequences mapped onto scattered memory blocks; and the GPU with its memory stacks. Numbered squares mark four of the layers, top to bottom: batching, the attention kernel, FP8 quantization and the paged KV cache." loading="lazy" decoding="async"></picture></a>
  <figcaption>The serving stack, from engine to GPU. Batching and the paged KV cache come switched on in vLLM and SGLang, and precision is the layer left to choose.</figcaption>
</figure>

## Which LLM inference optimization techniques are on by default?

Continuous batching, the paged KV cache and prefix caching are on by default in vLLM and SGLang. Modelplane's [Open Field Guide to Inference Engineering](https://docs.modelplane.ai/guides/inference-guide), which reached Hacker News on November 10, covers the first pair in five words: "Check it, don't build it."

| Technique | What it does | What is left for you |
| --- | --- | --- |
| Continuous batching | Requests join and leave the batch at each token step, so a finished sequence frees its slot at once | Set the concurrency limit |
| Paged KV cache | [PagedAttention](/glossary/pagedattention/) hands out cache in small blocks, the way an operating system pages RAM | Size the cache |
| Prefix caching | Reuses the work done on a repeated prompt opening | Watch the hit rate |

The guide is long, and one of its maintainers [said on Hacker News](https://news.ycombinator.com/item?id=50453146) "We certainly used agents to help us put a draft together", so I use it as a reference for defaults and for one set of measurements. Upbound's engineers ran coding agents against a self-hosted model, and the guide reports that "About two-thirds of prompt tokens hit the prefix cache, because agents resend their transcript on every turn."

That figure is why the prefix cache hit rate belongs on a dashboard once your clients are agents.

The same team "found that vLLM and scheduling worked. The time went to TLS, identity, timeouts, storage, IAM and observability."

## How much memory does the KV cache need?

The KV cache needs 2 × layers × KV heads × head dimension × bytes per value for every token of every live sequence. For Meta's 70B Llama models in 16-bit precision that is 2 × 80 × 8 × 128 × 2 bytes, or 327,680 bytes per token, using the layer and head counts in [Meta's Llama paper](https://arxiv.org/abs/2407.21783).

A single 128,000-token sequence therefore takes about 42 GB of cache, and sixteen of them take about 671 GB. Context length and concurrency draw on the same memory, so every token of context you allow is a token another user can't have.

Mixture-of-experts models add a sizing trap. The GLM-5.3 build in NVIDIA's tutorial "has 753 billion parameters, with 40 billion activated per token", and the full 464 GB checkpoint still has to sit in GPU memory because any token can route to any expert.

The [KV cache eviction article](/articles/kv-cache-eviction/) covers which cached state goes when memory fills.

## Quantization: start at FP8 and measure

Use the lowest precision your GPU runs natively and your own evals accept, which on current NVIDIA hardware means FP8 first. FP8 has native tensor-core support on NVIDIA's [Hopper](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) and [Ada Lovelace](https://images.nvidia.com/aem-dam/Solutions/geforce/ada/nvidia-ada-gpu-architecture.pdf) architectures, and Ampere cards like the A100 have none.

On the newer cards the matrix multiplies run in FP8, so you get compute throughput as well as roughly half the weight storage of BF16. Weight-only 4-bit formats such as AWQ and GPTQ are a different trade: they free memory for the KV cache and speed up decode, and they leave prefill where it was.

Posts about quantization, including the earlier version of this one, like to quote a percentage of quality lost per step down. I've removed those numbers because the loss depends on the model and the task, and the only figure worth trusting comes from your own eval set.

## Where does more throughput stop helping?

More throughput stops helping at the concurrency where requests no longer meet your latency target. Throughput that still meets the target is called goodput, and it is the number to plan capacity with.

| Concurrent requests | Total throughput (tok/s) | Mean request latency (s) | Mean time to first token (ms) |
| --- | --- | --- | --- |
| 1 | 107.4 | 49.84 | 479.75 |
| 8 | 386.0 | 114.17 | 433.79 |
| 16 | 607.8 | 136.46 | 482.90 |
| 32 | 385.0 | 453.54 | 899.36 |

Total throughput in NVIDIA's table rises through sixteen requests, and each user pays for it, with per-user speed falling "from 115.3 tok/s at C1 to 13.0 tok/s at C32." Past the peak nobody gains anything.

The detail that settles it is in the reproduction notes. The launch script ships with `--max-num-seqs 16`, and NVIDIA had to relaunch the server with the cap raised to 32 to produce the last row, so the shipped configuration already stops at the peak.

That makes the concurrency cap the first setting to tune, and it makes a throughput benchmark quoted without latency the overrated number in this field. The [time to first token guide](/articles/time-to-first-token/) covers the latency side.

## The engine changes what the model outputs

The engine and its flags change output quality, and tool calls show it first. Ubicloud's Jesse Donkervliet and Junhao Li [reported on October 20](https://www.ubicloud.com/blog/fixing-tool-call-accuracy-in-vllm) that "when we served Kimi K2.6 with vLLM version 0.28, we got the expected tool call schema only 92% of the time."

Constrained decoding, which masks any token that would break the tool schema, took their score on the K2VV ToolCall benchmark to 100%. vLLM ships the feature behind a `--tool-strict-level` flag and leaves it off by default, because some models misbehave when forced.

On [Hacker News](https://news.ycombinator.com/item?id=50245479), Aurornis objected that the title oversells the work, since "really they just needed to configure it correctly." That objection makes the case for treating configuration as optimization, because one serving flag moved tool-call accuracy by eight points.

The same post describes "a bug in the interplay between constrained decoding and speculative decoding" that rejected valid speculative tokens and failed requests. Speed features and correctness features share one decode loop, so rerun your [structured output](/articles/llm-structured-outputs/) checks after every engine upgrade.

## What order should you apply inference optimizations in?

Start with what the engine already does and end with anything that needs a draft model.

1. **Check the defaults.** Confirm continuous batching, the paged KV cache and prefix caching are active in the engine version you pinned.
2. **Fit the weights with room for cache.** Pick FP8 where the hardware runs it natively, and budget the KV cache with the formula above.
3. **Find the goodput peak.** Sweep concurrency against your own prompts, as NVIDIA's table does, and cap requests at the last level that meets your latency target.
4. **Verify output quality.** Run tool-call and schema checks against the served model, with constrained decoding on where the model supports it.
5. **Add speculative decoding last.** It helps when single responses stream too slowly even at low load.

[Speculative decoding](/articles/speculative-decoding/) comes last because its failure doesn't show on the usual panels: "If acceptance collapses, every pass still pays for the guesses and the model slows while other panels look normal." It also differs from [test-time compute](/glossary/test-time-compute/), which spends extra inference work to improve an answer and makes no attempt to produce the same output in fewer steps.

## Does hardware change the order?

Hardware changes the order only when memory is short. On a consumer GPU a large model and a long context won't fit together, so quantization moves from step two to the first decision you make.

A model that outgrows one GPU has to be split, and NVIDIA's two-Station setup does it with tensor parallelism over RDMA. Plan that before deployment, because sharding is a launch configuration.
