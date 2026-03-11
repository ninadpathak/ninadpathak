---
title: "Speculative decoding explained: how LLMs generate tokens faster without changing the output"
date: 2026-03-12
description: "Speculative decoding cuts LLM latency by 2-3x without changing output quality. Here's how the draft-verify loop works, why acceptance rate is the only number that matters, and when it actually hurts."
tags: [ai, llm, inference, performance]
status: published
---

Your LLM is slow. Not because it can't do the math — modern GPUs are obscenely fast at matrix multiplication. The bottleneck is memory bandwidth. Every time the model generates a token, it reads its full set of weights from DRAM. That memory transfer is the slow part, not the computation.

Speculative decoding exploits a simple insight: if you're going to pay for one expensive memory read, you might as well verify several tokens during that pass instead of just one.

**Here's how it works:** A small, fast draft model proposes the next K tokens. The big target model verifies all of them in a single forward pass. Tokens where the two models agree get accepted and go straight into the output. The first disagreement triggers a resampling step and the rest are discarded. Rinse, repeat.

The output distribution is mathematically identical to running the target model on its own. No quality tradeoff. [Spec-Bench](https://github.com/hemingkx/Spec-Bench) measured 2.4-3x speedup on code and math tasks. [Google's original 2022 work](https://research.google/blog/looking-back-at-speculative-decoding/) showed similar numbers on translation and summarization.

[SCREENSHOT: Google Research blog post at research.google/blog/looking-back-at-speculative-decoding/ — grab the speedup chart]

## Why the memory-bound argument actually matters

This is the part most articles skip, and it's the part that lets you reason about everything else.

A GPU forward pass has two costs: loading the weights into fast memory, and doing the computation with them. For large models, loading the weights dominates. The compute happens fast. The GPU then sits idle waiting for the next weight transfer.

Standard autoregressive decoding runs one pass per token. Each pass loads the full model weights. For a 70B model, that is a lot of memory to move for a single token.

Speculative decoding doesn't change the cost of loading weights. But it does change how many tokens you get per load. If the draft model guesses `def`, `reverse_list`, `(`, `head` and the target model agrees with all four — you just got four tokens for the cost of one weight-loading cycle.

That is why the speedup is real and not a trick. You're not approximating anything. You're just using the GPU's compute capacity that was sitting idle anyway.

## The draft-verify loop in practice

| Step | What happens |
|---|---|
| Draft | Small model proposes K tokens autoregressively. Fast because the model is tiny. |
| Verify | Target model runs one forward pass over context + all K draft tokens simultaneously. |
| Accept or reject | Matching tokens are kept. First mismatch triggers resampling, rest are discarded. |

Concrete example. User asks for a Python function to reverse a linked list. Draft model guesses: `def reverse_list(head):`. Target model checks the whole thing in one pass. If it agrees — all five tokens are accepted immediately. If it disagrees at `head`, the system keeps `def reverse_list(` and resumes from there.

The [survey of speculative decoding techniques](https://arxiv.org/html/2401.07851v2) has the formal proofs if you want to verify the output equivalence mathematically.

## Acceptance rate is the only number that actually matters

Everything else — draft model choice, K value, variant selection — feeds into one metric: acceptance rate. What fraction of the draft model's proposed tokens does the target model accept?

High acceptance rate, good speedup. Low acceptance rate, you're burning compute on a draft model that keeps getting overruled.

Two things drive acceptance rate:

**Task predictability.** Code generation, structured outputs, boilerplate continuations — acceptance rates are high because the next tokens are often obvious. Open-ended generation, creative writing, multilingual text — the draft model drifts more. This is why coding assistants are the natural home for speculative decoding. A lot of what they generate is syntactically predictable.

**Draft-target distribution alignment.** The draft model needs to predict what the target model would have predicted, not just what a reasonable continuation looks like. A generic small model from a different training run may produce fine output but still get rejected constantly because its token distribution doesn't match the target's.

My rule of thumb: above 70% acceptance rate, you're doing well. Below 50%, speculative decoding may be adding overhead rather than removing it. Measure on your actual workload before planning infrastructure around any benchmark number. I've seen teams expect 3x and get 1.4x because they benchmarked on code and deployed on open-ended chat.

## The variants worth knowing

You don't need them all in your head. These are the ones that come up:

| Variant | What it does | Tradeoff |
|---|---|---|
| External draft model | Separate small model proposes tokens | Straightforward, but another model to serve |
| Medusa | Extra prediction heads on top of the target model itself | Better distribution alignment, needs training |
| Speculative Streaming | Target model uses its own attention signals to speculate | No separate model, gains vary by task |
| Mirror Speculative Decoding | Handles vocabulary mismatch between draft and target | Useful when pairing models from different families |

[Apple's Speculative Streaming paper](https://machinelearning.apple.com/research/llm-inference) and [Mirror Speculative Decoding](https://machinelearning.apple.com/research/mirror) are worth reading if you're evaluating the last two. The [BentoML 3x speedup guide](https://www.bentoml.com/blog/3x-faster-llm-inference-with-speculative-decoding) covers practical setup for the external draft model approach.

[SCREENSHOT: BentoML blog post at bentoml.com/blog/3x-faster-llm-inference-with-speculative-decoding — the draft model comparison chart]

## When to use it and when not to

**Use it when:**
- You're serving interactive, latency-sensitive workloads at low-to-medium concurrency. Chat, coding assistants, anything where a human is waiting on each response.
- Your outputs are predictable. Code, structured data, templated responses.
- You care about inter-token latency, not just throughput. Speculative decoding reduces sequential forward passes per response. For more on why that distinction matters, [my post on time to first token](/blog/time-to-first-token-ttft/) covers it.

**Skip it when:**
- You're running high-throughput batch inference. If the GPU is already fully utilized serving many requests, the draft model adds compute overhead without buying back anything. The memory-bound argument breaks down when you're already saturating the GPU.
- Your acceptance rate will be low. Creative generation, multilingual workloads, domain-specific models with unusual distributions.
- Memory is tight. Draft model plus target model on the same GPU means less room for KV cache, which can force smaller batch sizes and erase the gain.

## Questions

**Does speculative decoding change output quality?**

No, in the standard rejection-sampling approach. The algorithm is mathematically equivalent to sampling directly from the target model. Some faster variants relax that guarantee, so check what your inference stack actually implements.

**How do I pick a draft model?**

A purpose-built speculator trained to mimic the target model's distribution is best. A smaller model from the same family is a solid second choice. A generic small model from a different family is the weakest option — it'll have low acceptance rate unless the task is very predictable. Medusa is worth it if you can afford the training investment.

**Does it play nicely with quantization?**

Yes, but the gains can shrink. Quantization already reduces memory pressure, which is the same problem speculative decoding solves. They're not redundant, but the upside from adding speculative decoding on top of a quantized model is smaller than adding it to a full-precision model. The [2025 test-time scaling benchmark](https://arxiv.org/abs/2509.04474) includes numbers across configurations.

**Is it worth setting up if you're a small team?**

If you're calling a hosted API, this is the provider's problem. If you're running your own stack — vLLM, TGI, or similar — speculative decoding support is increasingly standard and worth enabling for latency-sensitive workloads. The [BentoML inference handbook](https://bentoml.com/llm/inference-optimization/speculative-decoding) is a good practical starting point.

**What's a realistic speedup to expect?**

2-3x on code and math tasks with a well-matched draft model and high concurrency. 1.3-1.8x on more open-ended workloads. Measure yours. Don't plan around someone else's benchmark.
