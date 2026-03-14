---
title: "Speculative Decoding: How to Speed Up LLM Inference for Free"
date: 2026-03-07
description: "LLM inference is memory-bound, not compute-bound. Speculative decoding uses this fact to speed up generation by 2-3x using a smaller draft model to predict tokens for a larger one."
tags: [ai, llm, infrastructure]
status: published
---

Inference speed is the biggest hurdle for interactive LLM applications. Waiting for a large model to generate text token-by-token feels slow. Most developers assume they need more GPUs to fix this. Such a view ignores the fundamental physics of how these models run.

Large models are "memory-bound." The bottleneck is the time it takes to move weights from memory to the processor. The actual math of generating a token is relatively fast. Speculative decoding exploits this idle compute time to generate multiple tokens at once.

## The draft-verify loop in practice

Speculative decoding uses two models. A small "draft" model guesses the next few tokens. A large "target" model then verifies these guesses in a single parallel step. The small model is much faster and less accurate. The large model is slow but authoritative.

<div style="margin: 3rem 0; background: transparent; border: 1px solid var(--border); overflow: hidden;">
  <iframe src="/static/visuals/speculative-decoding-viz.html" style="width: 100%; height: 500px; border: none;" scrolling="no"></iframe>
</div>

Such a system works because the large model can check four or five tokens in almost the same time it takes to generate one. If the small model's guesses are correct, we have successfully generated multiple tokens in one step. If a guess is wrong, we simply discard it and continue from the last correct token.

## Why this is "free" speedup

You are already paying for the memory bandwidth to load the large model's weights. The draft model is so small that its resource requirements are negligible. You are using the spare compute cycles of your GPU to run the verification in parallel.

The effectiveness of this technique depends on the "acceptance rate." Such a metric measures how often the large model agrees with the small one. A high acceptance rate leads to a 2x or 3x speedup. Even a moderate acceptance rate provides a meaningful improvement in snappiness for the end user.

## Implementation options

Standard speculative decoding requires a separate draft model. Newer techniques like Medusa or Lookahead decoding integrate the "drafting" capability directly into the large model itself. These methods eliminate the need to manage two separate neural networks.

Most high-performance inference engines like vLLM and TensorRT-LLM now support speculative decoding natively. It is becoming a standard optimization for production deployments. You should enable it if you are hosting your own models and need to improve user experience without increasing your hardware budget.
