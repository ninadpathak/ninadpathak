---
title: "Speculative decoding explained: how LLMs generate tokens faster without changing the output"
date: 2026-03-12
description: "Speculative decoding cuts LLM latency by 2-3x without changing output quality. Here's how the draft-verify loop works, why acceptance rate is the only number that matters, and when it actually hurts."
tags: [ai, llm, inference, performance]
status: published
---

If your model feels slow, the bottleneck is often not the math. It is the waiting. A large model spends a lot of inference time pulling weights from memory over and over just to emit one token at a time.

That is why speculative decoding matters. It is one of the few inference tricks that can make a model feel much faster without changing the output distribution. The basic move is simple: let a smaller draft model guess a few upcoming tokens, then ask the large target model to verify them in one pass instead of generating each token serially.

**The short answer:** speculative decoding uses a fast draft model to propose several next tokens, then verifies them with the target model in parallel. If the guesses are accepted, the system emits multiple tokens for roughly the cost of one target-model step. If they are rejected, it falls back cleanly. In the standard form, output quality is unchanged because the algorithm preserves the target model's sampling distribution.

## Why memory-boundedness makes this possible

A transformer forward pass is expensive because it has to read the model's weights from memory. That memory movement is often the real constraint, not the matrix multiplies themselves. Once the weights are available on chip, the GPU can do more work than a naive token-by-token decoding loop asks it to do.

Standard autoregressive decoding wastes that headroom. One forward pass gives you one token. Then the model does it again. And again. Each step reloads the same large set of weights.

Speculative decoding exploits that gap directly. If a draft model can guess `K` future tokens, the target model can check all of them in one pass. That spreads the expensive memory read across multiple candidate tokens instead of paying it once per token.

[Spec-Bench, the ACL 2024 benchmark](https://github.com/hemingkx/Spec-Bench) for evaluating speculative decoding methods, measured EAGLE achieving a 2.4x to 2.5x speedup over autoregressive decoding across model sizes, with a maximum of 3.0x on mathematical reasoning tasks with Vicuna-33B. The [original Google Research blog post on speculative decoding](https://research.google/blog/looking-back-at-speculative-decoding/) documented 2x to 3x improvements across translation and summarization tasks from the initial 2022 work.

[SCREENSHOT: Google Research blog post header at research.google/blog/looking-back-at-speculative-decoding/ showing the original post and any speedup figures]

## How the draft-verify loop works

The loop is easier to understand when you break it into three parts:

| Step | What happens | Why it matters |
|---|---|---|
| Draft | A smaller model proposes the next `K` tokens. | This is cheap because the draft model is small. |
| Verify | The target model evaluates the context plus those draft tokens in one pass. | This is where the latency savings come from. |
| Accept or reject | Matching tokens are kept. The first mismatch triggers resampling and the rest are discarded. | This preserves correctness while still getting speedup from accepted runs. |

In practice, the details differ by implementation, but the shape stays the same. A cheap model guesses ahead. The expensive model checks the work. Accepted tokens move straight into the output stream.

The key property is accuracy. The standard rejection-sampling version produces the same output distribution as ordinary decoding from the target model. There is no built-in quality tradeoff in that version of the algorithm. The [comprehensive survey of speculative decoding techniques](https://arxiv.org/html/2401.07851v2) covers the formal proofs across rejection-sampling variants.

## Acceptance rate: the only metric that matters for real-world speedup

Everything comes back to acceptance rate. If the draft model proposes four tokens and the target model accepts three on average, the system looks great. If it accepts one, the gain can disappear once you count the draft model overhead.

This is the metric to watch because it captures whether the draft model is actually useful for your workload.

Acceptance rate depends on two things:

- **Task predictability.** Code, structured outputs, and repetitive continuations tend to accept well. Open-ended generation usually accepts less.
- **Draft-target alignment.** The draft model needs to guess what the target model would have said, not just something plausible. If those distributions drift apart, rejection goes up.

That is why benchmark numbers need context. A setup that looks great on code or math can look ordinary on looser generation tasks. Measure acceptance rate on your own traffic before treating any published speedup as your baseline.

## The main variants worth knowing

You do not need every variant in your head. These are the ones worth recognizing:

| Variant | What it does | Tradeoff |
|---|---|---|
| External draft model | Uses a separate smaller model as the speculator. | Simple conceptually, but adds another model to serve. |
| Medusa | Adds extra decoding heads on the target model. | Better alignment, but requires training changes. |
| Speculative Streaming | Uses the target model's own signals to speculate. | Simpler serving story, but gains depend on the task. |
| Mirror Speculative Decoding | Handles draft and target models with different vocabularies. | Useful when model families do not line up cleanly. |

The [BentoML inference handbook's speculative decoding section](https://bentoml.com/llm/inference-optimization/speculative-decoding) and their [practical 3x speedup guide](https://www.bentoml.com/blog/3x-faster-llm-inference-with-speculative-decoding) are good references for the external-draft setup. [Apple Machine Learning Research](https://machinelearning.apple.com/research/llm-inference) and [Mirror Speculative Decoding](https://machinelearning.apple.com/research/mirror) cover two important variants.

[SCREENSHOT: BentoML blog post at bentoml.com/blog/3x-faster-llm-inference-with-speculative-decoding showing the chart with draft model comparison]

## When speculative decoding helps and when it hurts

**It helps most when:**

- You are serving single requests or low-concurrency workloads. The draft-verify loop's gains are per-request latency improvements, which is what matters for interactive applications like chat and coding assistants.
- Your outputs are partially predictable. Structured outputs, code generation, and continuation tasks have naturally high acceptance rates.
- You are optimizing TTFT and inter-token latency. Speculative decoding reduces the number of sequential target-model steps needed to produce a response. I wrote more about [why TTFT matters for interactive applications in my earlier post on time to first token](/blog/time-to-first-token-ttft/).

**It hurts or does not help when:**

- You are running high-throughput batch inference. When the GPU is already heavily utilized serving many concurrent requests, the draft model adds compute overhead without a corresponding benefit. The memory-bound argument only holds when the GPU has spare compute capacity.
- Your acceptance rate is low. If the draft model's distribution consistently diverges from the target, as it often does in creative writing, domain-specific outputs, or multilingual text, the overhead of running the draft model and doing rejection sampling adds latency instead of removing it.
- You have tight memory constraints. Running a draft model alongside a large target model doubles your GPU memory usage relative to running just the target. On setups where memory is already the constraint, this can force you to a smaller batch size and erase the gains.

## FAQ

**Does speculative decoding change the quality of outputs?**

No in the standard rejection-sampling approach. It is designed to preserve the exact output distribution of the target model. Some faster approximations do relax that guarantee, so it is worth checking what your inference stack actually implements.

**How do I know if my use case has a high enough acceptance rate?**

Run it and measure. Most inference frameworks that support speculative decoding expose acceptance rate directly. As a rough rule, above 70% is promising. Below 50%, the gains often get thin. Code and structured outputs usually do better than open-ended generation.

**What is the right draft model to use?**

Ideally, a purpose-built speculator trained to match your target model's token distribution. The target model's own smaller variant from the same family is a reasonable second choice. A generic small model from a different family is the weakest option and often not worth the setup cost. Medusa heads are worth considering if you have the compute to train them on your specific target model.

**How does speculative decoding interact with quantization?**

They can stack, but the gain changes. Quantization already reduces the memory pressure that makes speculative decoding attractive, so the upside may shrink. It can still help, especially at low concurrency. The [2025 benchmark on test-time scaling](https://arxiv.org/abs/2509.04474) includes evaluation under different model configurations.

**Is speculative decoding worth implementing for a small team?**

It depends on where you run inference. If you call a hosted API, this is mostly the provider's concern. If you run your own stack with vLLM, TGI, or similar frameworks, it is worth testing for latency-sensitive workloads.
