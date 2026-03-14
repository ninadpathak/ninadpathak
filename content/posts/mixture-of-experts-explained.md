---
title: "Mixture of experts: how MoE models are cheap to run but expensive to host"
date: 2026-03-13
description: "DeepSeek V3 has 671B parameters but only activates 37B per token. Here's how mixture of experts works, why it cuts inference costs, and the catch nobody puts in the headline."
tags: [ai, llm, inference, architecture]
status: published
---

DeepSeek's API launched at roughly a tenth the price of comparable Anthropic and OpenAI endpoints, with competitive benchmark results. The architecture answer is mixture of experts. But that answer only makes sense once you understand the part most explainers skip: MoE cuts compute costs but does not cut memory costs. You still need the full model loaded in VRAM before processing a single token.

**Short answer:** Mixture of experts replaces each transformer block's feedforward layer with a bank of specialist subnetworks and routes each token through only a small subset. Inference compute scales with active parameters, not total parameters. DeepSeek V3 activates 37B parameters per token out of 671B total, doing roughly the same math per token as a 37B dense model. The catch: all 671B parameters must be loaded into GPU memory before inference begins.

<div style="margin: 3rem 0; background: #090909; border: 1px solid var(--border); overflow: hidden;">
  <iframe src="/static/visuals/moe-viz.html" style="width: 100%; height: 500px; border: none;" scrolling="no"></iframe>
</div>

## How MoE cuts inference compute

A dense transformer runs every token through every parameter. A 70B model means 70B parameters worth of compute per token, every time.

A MoE model keeps attention layers unchanged but replaces each block's single feedforward network with a collection of expert networks, typically 8 to 256 per layer. A small learned router assigns each token to the top-K experts — usually 2 to 8. The token goes through only those experts. Everything else is skipped for that token.

DeepSeek V3 uses 256 routed experts per layer plus a few shared experts, activating 8 per token. Cameron Wolfe's [technical breakdown of MoE LLMs](https://cameronrwolfe.substack.com/p/moe-llms) goes through the parameter math in detail. The [DeepSeekMoE paper](https://arxiv.org/abs/2401.06066) and [DeepSeek-V2 paper](https://arxiv.org/abs/2405.04434) cover the specific architectural choices behind V3.

The reason this translates to cost savings is the memory bandwidth bottleneck I explained in [my piece on speculative decoding](/blog/speculative-decoding-explained/). LLM inference spends most of its time waiting for weight reads from DRAM, not running matrix multiplications. If you activate only 37B parameters per forward pass, you do only 37B parameters worth of that weight loading — not 671B worth. A 671B MoE model running 37B active parameters per token does roughly the same math per token as a 37B dense model.

## Dense vs MoE across the dimensions that matter

| | Dense 67B | MoE 671B (37B active) |
|---|---|---|
| Compute per token | ~67B params | ~37B params |
| Memory to run (BF16) | ~134GB | ~1.3TB |
| Training complexity | Standard | Significantly harder |
| Fine-tuning | Straightforward | Harder — routing disrupts expert specialization |
| API cost at provider scale | Higher | Lower |
| Self-hosting feasibility | 8x A100 | Multi-node cluster required |

The DeepSeek-V2 paper compared their MoE model directly against their 67B dense model: 5.76x improvement in maximum generation throughput, 42.5% lower training cost, 93.3% reduction in KV cache size. That throughput multiplier is what makes the economics work at API scale. When many concurrent requests share the same loaded weights, per-token cost drops considerably.

## The memory catch

The router decides which experts to send each token to based on the token itself, at inference time. Until the router runs, you do not know which experts you need. So all of them must be in GPU memory before processing begins.

Running DeepSeek V3 requires holding 671B parameters in VRAM. In FP8 quantization, that is over 1.3TB. In BF16, more. NVIDIA's [Blackwell MoE overview](https://blogs.nvidia.com/blog/mixture-of-experts-frontier-models/) cites 10x faster inference and 1/10 the token cost — those numbers are accurate, but they apply in the context of NVL72-class hardware.

When you call DeepSeek's API, you are benefiting from their hardware and from running at high enough throughput to amortize that footprint across many requests. Self-hosting means facing the same memory footprint as self-hosting a dense model of the same total size, with the compute advantage only materializing at high concurrent request volumes.

## Routing is where most of the training difficulty lives

Without an explicit mechanism to prevent it, the gating network converges on a few generalist experts and routes most tokens to them. This is expert collapse. If 240 of 256 experts never get used, you paid the memory cost for 256 and got the performance of 16.

The standard fix is an auxiliary loss term that penalizes uneven expert utilization during training. [2024 research](https://arxiv.org/abs/2408.15664) found that tuning this loss weight is a frustrating balancing act: too weak and you get collapse, too strong and the interference gradients hurt model quality. You trade one problem for another.

DeepSeek's approach in V3 removes the auxiliary loss entirely, replacing it with per-expert bias terms on routing scores, dynamically updated based on recent utilization. Overloaded experts get their bias nudged down, reducing selection probability in future batches. It is a feedback control loop rather than a penalty. The [Hugging Face post on MoE load balancing](https://huggingface.co/blog/NormalUhr/moe-balance) traces how balancing strategies have evolved. Cerebras's [router comparison](https://www.cerebras.ai/blog/moe-guide-router) makes the case that routing algorithm choice affects final model quality more than most people expect.

Expert specialization is also messier than the diagrams imply. Research teams have tried to interpret what individual experts learn. The results are distributed and noisy — not the clean "expert A handles Python, expert B handles French" story. Maarten Grootendorst's [visual guide to MoE](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-mixture-of-experts) is the most honest treatment I have seen at showing what routing actually looks like.

## When MoE is and is not the right choice

Fine-tuning is harder with MoE. Updating a dense model toward a target domain changes parameters uniformly. Updating a MoE model also shifts routing decisions, which can disrupt expert specialization built during pretraining. The mitigations exist but add complexity. If you need a domain-specific model and are not operating at massive scale, a dense base model is the simpler starting point.

Benchmark numbers for MoE models are usually measured on tasks that favor routing stability: coding, math, structured reasoning. These have predictable token distributions and consistent expert selection. Open-ended generation, multilingual tasks, and domain-specific workloads with unusual token distributions tend to see more variable performance because routing is less stable on out-of-distribution inputs.

If you are consuming MoE models through an API, the architecture mostly does not matter to you. You pay per token, the provider owns the infrastructure, and you should evaluate on your actual task. The architecture matters if you are self-hosting, deciding whether to fine-tune, or trying to understand why a model behaves inconsistently on edge cases.

Explaining these kinds of infrastructure tradeoffs clearly for developer audiences is a significant part of what I do for AI companies. [My work page](/work) has examples if that is relevant.

## Questions

**Is a MoE model with 37B active parameters as capable as a dense 37B model?**

Usually more capable. Active parameter count determines inference cost. Total parameter count determines how much specialized knowledge can be stored. A 671B MoE model activating 37B parameters per token has access to knowledge distributed across 671B parameters, even though any given token only touches 37B of them.

**Why doesn't every model use MoE?**

Training complexity. Getting load balancing right, preventing expert collapse, and validating that expert specialization developed correctly is substantially more work than training a dense model. At smaller scales, the complexity overhead is not worth the efficiency gains.

**Can I run DeepSeek V3 locally?**

Only with serious hardware. FP8 requires over 1.3TB of VRAM. Quantized versions (GPTQ, GGUF) reduce this, but you are still looking at a minimum of 8 high-end GPUs for reasonable throughput. More aggressive quantization degrades output quality on tasks that are sensitive to it.

**Does MoE improve reasoning or just efficiency?**

Primarily efficiency, though higher total capacity plausibly allows more domain-specific knowledge to accumulate in specialized experts. The evidence that MoE specifically improves reasoning over a dense model of the same active parameter count is mixed. What is consistent: better output quality per dollar of inference cost at provider scale.

**How does the KV cache reduction work?**

The key-value cache stores past attention states so the model does not recompute them on each generation step. In a dense model, KV cache scales with model width and context length. In MoE, only active experts contribute to the cache for any given token, so the per-token footprint is smaller. More requests fit in the same GPU memory simultaneously, directly improving throughput. The DeepSeek-V2 numbers: 93.3% reduction in KV cache size compared to their 67B dense model, which is the main driver of the 5.76x throughput improvement.
