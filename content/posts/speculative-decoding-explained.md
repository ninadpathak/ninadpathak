---
date: 2026-03-07
description: LLM inference is memory-bound, not compute-bound. Speculative decoding
  uses this fact to speed up generation by 2-3x using a smaller draft model to predict
  tokens for a larger one.
status: published
tags:
- ai
- llm
- infrastructure
title: 'Speculative Decoding: How to Speed up Llm Inference for Free'
---

Inference speed is the biggest hurdle for interactive LLM applications. Waiting for a large model to generate text token-by-token feels slow. Most developers assume they need more GPUs to fix this. Such a view ignores the fundamental physics of how these models run.

Large models are "memory-bound." The bottleneck is the time it takes to move weights from memory to the processor, the same memory wall that makes [KV cache eviction such a high-value optimization](/blog/kv-cache-eviction-accuracy/). The actual math of generating a token is relatively fast. Speculative decoding exploits this idle compute time to generate multiple tokens at once.

## The draft-verify loop in practice

Speculative decoding uses two models. A small "draft" model guesses the next few tokens. A large "target" model then verifies these guesses in a single parallel step. The small model is much faster and less accurate. The large model is slow but authoritative.

<div class="visual-wrapper">
  <div class="visual-title">SPECULATIVE DECODING</div>
  <div class="visual-container">
    <iframe src="/static/visuals/speculative-decoding.html" title="A small draft model proposes several tokens, the large target model verifies them in parallel, accepted tokens are kept and rejected ones discarded" loading="lazy"></iframe>
  </div>
</div>

Such a system works because the large model can check four or five tokens in almost the same time it takes to generate one. If the small model's guesses are correct, we have successfully generated multiple tokens in one step. If a guess is wrong, we simply discard it and continue from the last correct token.

## Why this is "free" speedup

You are already paying for the memory bandwidth to load the large model's weights. The draft model is so small that its resource requirements are negligible. You are using the spare compute cycles of your GPU to run the verification in parallel.

The effectiveness of this technique depends on the "acceptance rate." Such a metric measures how often the large model agrees with the small one. A high acceptance rate leads to a 2x or 3x speedup. Even a moderate acceptance rate provides a meaningful improvement in snappiness for the end user, which shows up directly in [time to first token, the metric that determines AI snappiness](/blog/time-to-first-token-ttft/).

## Implementation options

Standard speculative decoding requires a separate draft model. Newer techniques like Medusa or Lookahead decoding integrate the "drafting" capability directly into the large model itself. These methods eliminate the need to manage two separate neural networks.

Most high-performance inference engines like vLLM and TensorRT-LLM now support speculative decoding natively. It is becoming a standard optimization for production deployments. You should enable it if you are hosting your own models and need to improve user experience without increasing your hardware budget.