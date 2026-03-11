---
title: "Speculative decoding explained: how LLMs generate tokens faster without changing the output"
date: 2026-03-12
description: "Speculative decoding cuts LLM latency by 2-3x without changing output quality. Here's how the draft-verify loop works, why acceptance rate is the only number that matters, and when it actually hurts."
tags: [ai, llm, inference, performance]
status: published
---

Most explanations of speculative decoding describe it as "using a small model to help a large model go faster." That is accurate and mostly useless. It tells you what happens but not why it is possible — and the why is the part that lets you reason about when it works, when it does not, and which variant is worth using for your setup.

The real explanation starts with a fact about GPU hardware: modern GPUs can perform hundreds of trillions of floating-point operations per second, but their memory bandwidth — the rate at which they can read weights and activations from DRAM — is orders of magnitude slower. During autoregressive decoding, generating a single token requires a full forward pass through every layer of the model, reading all those weights from memory. The GPU finishes that computation almost instantly and then sits idle waiting for the next memory read. Speculative decoding is a technique for making better use of the compute that is already available while that memory transfer is happening.

**The short answer:** Speculative decoding uses a small, fast draft model to propose several candidate tokens ahead, then passes all of them to the large target model for parallel verification in a single forward pass. Because LLM inference is memory-bound rather than compute-bound, verifying four draft tokens costs approximately the same as generating one — the GPU was underutilized anyway. Accepted tokens are kept; rejected tokens are resampled. Output quality is mathematically identical to standard autoregressive decoding. Practical speedups range from 2x to 3x depending on acceptance rate.

## Why memory-boundedness makes this possible

A transformer forward pass reads a fixed amount of memory regardless of how many tokens it is evaluating in that pass. The bottleneck is loading the model weights, not running the matrix multiplications. Once the weights are in SRAM or cache, the GPU can verify a batch of candidate tokens for essentially the same cost as verifying one.

Standard autoregressive decoding wastes this. It runs one forward pass, produces one token, and then runs another forward pass for the next token. Each pass loads the full model weights again. The GPU's compute capacity is barely touched.

Speculative decoding exploits this inefficiency directly. By proposing K tokens in advance and verifying them all in one pass, you amortize the expensive memory reads across multiple output tokens. When the acceptance rate is high — when the draft model's guesses are usually right — you get K tokens out for roughly the cost of one pass instead of K passes.

[Spec-Bench, the ACL 2024 benchmark](https://github.com/hemingkx/Spec-Bench) for evaluating speculative decoding methods, measured EAGLE achieving a 2.4x to 2.5x speedup over autoregressive decoding across model sizes, with a maximum of 3.0x on mathematical reasoning tasks with Vicuna-33B. The [original Google Research blog post on speculative decoding](https://research.google/blog/looking-back-at-speculative-decoding/) documented 2x to 3x improvements across translation and summarization tasks from the initial 2022 work.

[SCREENSHOT: Google Research blog post header — research.google/blog/looking-back-at-speculative-decoding/ — showing the original post and any speedup figures]

## How the draft-verify loop works

The mechanism has three steps that repeat for every batch of tokens:

**Draft phase:** A small, fast model — the speculator — runs autoregressively and generates K candidate tokens. This is fast because the draft model is small. Common choices are a 1B or 3B model paired with a 70B target, or a purpose-built speculator trained to match the target model's distribution.

**Verify phase:** The target model runs a single forward pass over the original context plus all K draft tokens simultaneously. It produces K+1 output distributions — one for each position.

**Accept or reject:** For each draft token, the algorithm compares the target model's distribution to the draft model's distribution at that position. Tokens where the distributions agree closely are accepted. The first rejected token triggers a resampling step, and everything after it is discarded.

The mathematical guarantee is that this process produces the exact same distribution of outputs as standard autoregressive sampling from the target model. No approximation, no quality tradeoff. The [comprehensive survey of speculative decoding techniques](https://arxiv.org/html/2401.07851v2) covers the formal proofs across rejection sampling variants if you want to verify this.

## Acceptance rate: the only metric that matters for real-world speedup

Everything reduces to acceptance rate. If the draft model proposes four tokens and the target model accepts three of them on average, you are doing roughly 3x better than autoregressive decoding. If it accepts one, you are barely ahead and may be behind when accounting for draft model overhead.

Acceptance rate depends on two things:

**Task predictability.** For text that follows predictable patterns — function names, boilerplate code, continuation of a phrase the model has seen many times — acceptance rates are high. For creative text, multilingual content, or outputs where the target distribution is highly diffuse, acceptance rates drop. This is why the speedup on mathematical reasoning tasks in Spec-Bench is higher than on translation: math has more predictable intermediate tokens.

**Draft-target distribution alignment.** The draft model needs to predict what the target model would predict, not just what a correct continuation looks like. A draft model trained on different data or with a different objective may produce reasonable text but still get rejected frequently by the target model. This is why speculator models trained specifically to imitate a target model's distribution tend to outperform general-purpose small models as drafters.

I've seen teams deploy speculative decoding in production expecting 3x speedup and getting 1.4x because their use case involved short prompts with long, open-ended responses where the draft model's acceptance rate was under 50%. The benchmark numbers are from tasks that favor high acceptance rates. Measure yours before planning infrastructure around an assumed speedup.

## The main variants worth knowing

**External draft model** is the original approach: a separate smaller model proposes tokens, the target model verifies. The [BentoML inference handbook's speculative decoding section](https://bentoml.com/llm/inference-optimization/speculative-decoding) and their [practical 3x speedup guide](https://www.bentoml.com/blog/3x-faster-llm-inference-with-speculative-decoding) are good references for implementation with real models.

**Medusa** adds multiple prediction heads directly on top of the target model instead of using a separate speculator. Each head predicts a token at a future position. The advantage is that the draft heads see the same representations as the target model, which tends to increase acceptance rate. The disadvantage is that you need to train those heads, which requires compute and the original model.

**Speculative Streaming**, published by [Apple Machine Learning Research](https://machinelearning.apple.com/research/llm-inference), eliminates the separate draft model entirely by using the target model's own attention patterns to speculate on future tokens within a single pass. Simpler to deploy; acceptance rates can be lower depending on the task.

**Apple's Mirror Speculative Decoding** tackles a different problem: how to use speculative decoding when the draft and target models have different vocabularies. Their [published approach](https://machinelearning.apple.com/research/mirror) achieves up to 2.8x speedup even without a vocabulary-matched speculator, which matters if you are pairing models from different families.

[SCREENSHOT: BentoML blog post showing speedup benchmarks — bentoml.com/blog/3x-faster-llm-inference-with-speculative-decoding — the chart with draft model comparison]

## When speculative decoding helps and when it hurts

**It helps most when:**

- You are serving single requests or low-concurrency workloads. The draft-verify loop's gains are per-request latency improvements, which is what matters for interactive applications like chat and coding assistants.
- Your outputs are partially predictable. Structured outputs, code generation, and continuation tasks have naturally high acceptance rates.
- You are optimizing TTFT and inter-token latency. Speculative decoding directly reduces the number of sequential forward passes needed to produce a response. I wrote more about [why TTFT matters for interactive applications in my earlier post on time to first token](/blog/time-to-first-token-ttft/) — speculative decoding is one of the few techniques that actually moves that number for a fixed model.

**It hurts or does not help when:**

- You are running high-throughput batch inference. When the GPU is already heavily utilized serving many concurrent requests, the draft model adds compute overhead without a corresponding benefit. The memory-bound argument only holds when the GPU has spare compute capacity.
- Your acceptance rate is low. If the draft model's distribution consistently diverges from the target — creative writing, domain-specific outputs, multilingual text — the overhead of running the draft model and doing rejection sampling adds latency instead of removing it.
- You have tight memory constraints. Running a draft model alongside a large target model doubles your GPU memory usage relative to running just the target. On setups where memory is already the constraint, this can force you to a smaller batch size and erase the gains.

## FAQ

**Does speculative decoding change the quality of outputs?**

No, and this is the most important property of the standard approach. The rejection sampling algorithm is designed to produce the exact same output distribution as the target model alone. From the caller's perspective, the output is indistinguishable from standard autoregressive sampling. Some variants — particularly those that use greedy acceptance rather than distribution-matching — do make approximations, so check which variant your inference stack is using if output quality matters to you.

**How do I know if my use case has a high enough acceptance rate?**

Run it and measure. Most inference frameworks that support speculative decoding expose acceptance rate as a metric. Target above 70% for meaningful speedup. Below 50%, you may be better off without it. The task type is a decent prior: code generation and structured outputs tend to be high; open-ended creative generation tends to be low.

**What is the right draft model to use?**

Ideally, a purpose-built speculator trained to match your target model's token distribution. The target model's own smaller variant from the same family is a reasonable second choice. A generic small model from a different family is the weakest option and often not worth the setup cost. Medusa heads are worth considering if you have the compute to train them on your specific target model.

**How does speculative decoding interact with quantization?**

They stack, but carefully. A quantized target model already reduces memory bandwidth requirements, which changes the memory-bound calculation. In practice, speculative decoding still provides meaningful speedup on quantized models, particularly at low concurrency. The [2025 benchmark on test-time scaling](https://arxiv.org/abs/2509.04474) includes evaluation of speculative decoding under different model configurations if you want numbers on this.

**Is speculative decoding worth implementing for a small team?**

It depends on whether you are running your own inference stack. If you are calling a hosted API, this is the provider's problem, not yours — and most major providers already use some form of speculative decoding or similar optimization internally. If you are running self-hosted inference with vLLM, TGI, or a similar framework, speculative decoding support is increasingly standard and worth enabling for latency-sensitive workloads.
