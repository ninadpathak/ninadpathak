---
title: "Mixture of experts: how MoE models are cheap to run but expensive to host"
date: 2026-03-13
description: "DeepSeek V3 has 671B parameters but only activates 37B per token. Here's how mixture of experts works, why it cuts inference costs, and the catch nobody puts in the headline."
tags: [ai, llm, inference, architecture]
status: published
---

DeepSeek's API pricing was roughly a tenth of comparable Anthropic and OpenAI endpoints when it launched. Output quality competitive across most standard benchmarks. The obvious question was how.

The architecture-level answer is mixture of experts. But that answer comes with a nuance that most explainers drop before they finish the paragraph, so let's start there.

**Short answer:** Mixture of experts breaks the feedforward layers of a transformer into specialist subnetworks and routes each token through only a small subset of them. You get a model with much higher total parameter capacity than a dense model of the same inference cost, because most parameters are dormant on any given token. The catch is that you still need all of them loaded in GPU memory to run the model at all.

## How the numbers work out

A standard dense transformer runs every token through every parameter in every layer. 70B model, 70B parameters worth of compute per token. Linear scaling.

A MoE model keeps the attention layers the same but replaces each transformer block's single feedforward network with a collection of expert networks, typically 8 to 256 per layer. A small learned router assigns each token to the top-K experts, typically 2 to 8. The token goes through those experts only. Everything else sits idle.

DeepSeek V3 uses 256 routed experts per layer plus a handful of shared experts, and activates 8 routed experts per token. Total parameters: 671B. Active parameters per token: 37B. Cameron Wolfe's [technical breakdown of MoE LLMs](https://cameronrwolfe.substack.com/p/moe-llms) goes through the parameter math in detail. The [DeepSeekMoE paper](https://arxiv.org/abs/2401.06066) and [DeepSeek-V2 paper](https://arxiv.org/abs/2405.04434) are the primary sources for the specific architectural choices.

[SCREENSHOT: DeepSeek V3 HuggingFace model card at huggingface.co/deepseek-ai/DeepSeek-V3 showing the 671B total / 37B active parameter split]

The reason this matters for cost is the memory bandwidth bottleneck I wrote about in [my piece on speculative decoding](/blog/speculative-decoding-explained/). LLM inference is mostly waiting for weight reads from DRAM, not running matrix multiplications. GPUs finish the compute almost instantly then idle while weights transfer. If you're only activating 37B parameters per forward pass, you're doing 37B parameters worth of that weight loading, not 671B. A 671B MoE model running 37B active parameters per token is doing roughly the same math per token as a 37B dense model.

## The part that doesn't save you money

The router needs to know which experts to route each token to. That decision happens at inference time, based on the token itself. Until you run the router, you don't know which experts you'll need. So you need all of them loaded in GPU memory before you can process a single token.

Running DeepSeek V3 requires holding 671B parameters in VRAM. In FP8 quantization, that's over 1.3TB. In BF16, more. That's a multi-node GPU cluster problem. NVIDIA's [Blackwell MoE overview](https://blogs.nvidia.com/blog/mixture-of-experts-frontier-models/) cites 10x faster inference and 1/10 the token cost in the headline. The context for those numbers is that you need NVL72 hardware to run the model in the first place.

When you call DeepSeek's API, you're benefiting from the fact that they have that hardware and are running the model at high enough throughput that many concurrent requests share the same loaded weights. The [DeepSeek-V2 paper](https://arxiv.org/abs/2405.04434) compared it against their 67B dense model and found 5.76x improvement in maximum generation throughput, 42.5% lower training cost, and 93.3% reduction in KV cache size. That throughput multiplier is why the economics work at API scale.

Self-hosting is a different story. You face the same memory footprint as self-hosting a dense model of the same total size, and the compute benefit only kicks in once you're running enough concurrent requests to keep GPU utilization high. Whether that breakeven point makes sense depends heavily on your traffic patterns.

## Routing is where the hard engineering lives

Here's where most explainers stop, which is a problem because this is where most of the training difficulty actually is.

Without an explicit mechanism to prevent it, the gating network converges on a few general-purpose experts and routes almost all tokens to them. This is called expert collapse. If 240 of your 256 experts never get used, you paid the memory cost for 256 experts and got the performance of 16. Great job, you've built an expensive dense model.

The traditional fix is an auxiliary loss term that penalizes uneven expert utilization during training. It works until it doesn't. [2024 research](https://arxiv.org/abs/2408.15664) found that tuning the auxiliary loss weight is a genuinely frustrating balancing act: too weak and you get collapse, too strong and the interference gradients hurt model quality. You're trading one problem for another.

DeepSeek's approach in V3 was to remove the auxiliary loss entirely and instead apply a per-expert bias term to routing scores, dynamically updated based on each expert's recent utilization. If an expert is getting too much traffic, its bias gets nudged down, reducing selection probability in future batches. It's a feedback control loop instead of a penalty. The [Hugging Face post on MoE load balancing](https://huggingface.co/blog/NormalUhr/moe-balance) tracks how the approach to load balancing has evolved and what teams discovered trying to productionize each version. Cerebras's [router comparison](https://www.cerebras.ai/blog/moe-guide-router) gets into how much routing algorithm choice affects final model quality, and the answer is more than you'd expect.

Expert specialization is also messier than the diagrams imply. Research teams have tried to interpret what individual experts learn. The results are distributed and noisy, not the clean "expert A handles Python, expert B handles French" story. Maarten Grootendorst's [visual guide to MoE](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-mixture-of-experts) is the best I've seen at making the routing mechanics intuitive without oversimplifying them.

## When to use MoE and when to not bother

Fine-tuning is genuinely harder. Fine-tuning a dense model updates all parameters toward your target domain. Fine-tuning a MoE model also changes routing decisions, which can destabilize the expert specialization the model built during pretraining. The approaches for handling this exist but add complexity. If you need a domain-specific model and you're not operating at massive scale, a dense base model is the simpler starting point.

For evaluation: benchmark numbers for MoE models are usually measured on tasks that favor routing stability. Coding, math, structured reasoning. These tasks have predictable token distributions and consistent expert selection. Open-ended generation, multilingual tasks, and domain-specific workloads with unusual token distributions tend to see more variable performance because the routing is less stable on out-of-distribution inputs.

If you're consuming MoE models through an API, most of this is academic. You're paying per token, the provider owns the infrastructure problem, and you should evaluate on your actual task. The architecture matters if you're self-hosting, deciding whether to fine-tune, or trying to understand why a model behaves inconsistently on edge cases.

Technical writing about infrastructure tradeoffs like this is a significant part of what I do for AI companies who need to explain architectural decisions to developer audiences. If that's relevant to your team, [my work page](/work) has examples.

## Questions

**Is a MoE model with 37B active parameters as good as a dense 37B model?**

Usually better, because MoE models have much more total capacity. Active parameter count determines inference cost. Total parameter count determines how much specialized knowledge can be stored across the expert bank. A 671B MoE model activating 37B parameters per token has access to knowledge distributed across 671B parameters, even though it only uses 37B of them at a time.

**Why doesn't everyone use MoE?**

Training complexity. Getting load balancing right, avoiding expert collapse, validating that expert specialization actually developed correctly is substantially more work than training a dense model. It pays off at scale when you have the engineering resources to get it right.

**Can I run DeepSeek V3 locally?**

Only with serious hardware. FP8 requires over 1.3TB of VRAM. GPTQ and GGUF quantizations bring this down, but you're still looking at a minimum of 8 high-end GPUs for reasonable throughput. Quantized versions run on less but with quality degradation that matters for some tasks.

**Does MoE improve reasoning or just efficiency?**

Primarily efficiency, though higher total capacity plausibly allows more domain-specific knowledge to accumulate in specialized experts. The evidence that MoE specifically improves reasoning over a dense model of the same active parameter count is mixed. What's consistently true is better output quality per dollar of inference cost at scale.

**How does the KV cache reduction work?**

The key-value cache stores past attention states so the model doesn't recompute them on every generation step. In a dense model, KV cache size scales with model width and context length. In a MoE model, only the active experts contribute to the KV cache for any given token, so the per-token footprint is smaller. Across many concurrent requests, that smaller cache means more requests fit in the same GPU memory simultaneously, which directly improves throughput. The DeepSeek-V2 numbers on this were striking: 93.3% reduction in KV cache size compared to their 67B dense model, which is the main driver of the 5.76x throughput improvement.
