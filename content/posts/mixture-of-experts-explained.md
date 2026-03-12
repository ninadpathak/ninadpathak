---
title: "Mixture of experts: how MoE models are cheap to run but expensive to host"
date: 2026-03-13
description: "DeepSeek V3 has 671B parameters but only activates 37B per token. Here's how mixture of experts works, why it cuts inference costs, and the catch nobody puts in the headline."
tags: [ai, llm, inference, architecture]
status: published
---

DeepSeek V3 has 671 billion parameters. When you send it a token, it uses 37 billion of them. The other 634 billion sit in memory doing nothing for that particular token. This sounds wasteful. It is actually the point.

This architecture is called mixture of experts, and it's the reason DeepSeek's API is priced at roughly a tenth of what Anthropic and OpenAI charge for comparable output quality. Understanding why requires understanding the specific bottleneck that MoE is designed to exploit, because the cost advantage is real but the tradeoffs are a little different than most explainers admit.

Here's where things get slightly counterintuitive, so stick with me for a minute.

## What MoE actually is

A standard dense transformer runs every token through every parameter on every forward pass. If you have a 70B parameter model, every single one of those 70B parameters participates in producing every single token. This is the brute-force approach to language modeling, and it works well, but it's expensive because the compute scales with total parameter count.

A mixture of experts model breaks the feedforward layers of the transformer into a collection of "expert" subnetworks. For each token, a small routing network, called the gating network or router, decides which experts to activate. Typically it picks the top-K experts out of N total. DeepSeek V3 uses 256 experts per layer and activates 8 of them per token. The token flows through only the activated experts, the rest are skipped.

The result is a model where total parameter count and active parameter count are very different numbers. [DeepSeek-V3](https://huggingface.co/deepseek-ai/DeepSeek-V3) has 671B total parameters with 37B active per token. Compared to a dense 37B model, it has similar compute cost per forward pass. But compared to a dense 671B model, it has dramatically more capacity, because all those dormant experts can store specialized knowledge that gets invoked when relevant.

[SCREENSHOT: DeepSeek V3 model card on HuggingFace showing the 671B total / 37B active parameter breakdown]

Cameron Wolfe's [deep dive on MoE LLMs](https://cameronrwolfe.substack.com/p/moe-llms) is the clearest technical walkthrough I've found if you want to go deeper on the architecture. The [DeepSeekMoE paper](https://arxiv.org/abs/2401.06066) and the [DeepSeek-V2 paper](https://arxiv.org/abs/2405.04434) are worth reading if you want the original implementation details.

## Why this cuts inference cost

Going back to the memory bandwidth argument I made in [my post on speculative decoding](/blog/speculative-decoding-explained/): LLM inference is memory-bound, not compute-bound. The bottleneck is loading model weights from DRAM, not running the matrix multiplications.

This is where MoE gets interesting. If you have a 671B parameter model but only activate 37B parameters per token, you're doing roughly 37B worth of compute per forward pass, not 671B worth. Your compute cost scales with active parameters, not total parameters. That's the source of the inference efficiency.

But, and this is the catch that almost never makes it into the explainer articles: you still have to load all 671B parameters into memory. The gating network needs all the expert weights accessible so it can route tokens to the right ones. You cannot load just the experts you expect to use, because you don't know which ones you'll need until the routing happens at inference time.

So MoE gives you: a smaller compute bill per token, but the same (or larger) memory bill as a dense model of equivalent total size. Running DeepSeek V3 requires enough GPU VRAM to hold 671B parameters, which is roughly 1.3TB in FP8, or more in higher precision. That is not a consumer GPU problem. That's a cluster problem.

NVIDIA put it plainly in their [Blackwell MoE overview](https://blogs.nvidia.com/blog/mixture-of-experts-frontier-models/): MoE runs 10x faster and at 1/10 the token cost on their hardware. What that framing leaves out is how much that hardware costs.

## The routing problem nobody talks about

Routing sounds simple: a small neural network looks at a token and picks the best experts for it. In practice, training a MoE model is significantly harder than training a dense model, and most of the difficulty is in routing.

The core problem is called expert collapse. Left to its own devices, the gating network will figure out that a few experts are generally good at most things and start routing almost everything to them, ignoring the other experts entirely. You end up paying the memory cost for 256 experts but only using 8. The whole point was to have specialized experts that accumulate domain-specific knowledge. Expert collapse defeats this.

The traditional fix is an auxiliary loss, a penalty term added during training that pushes the router toward routing tokens evenly across experts. This works, but [research from 2024 found](https://arxiv.org/abs/2408.15664) that large auxiliary losses introduce interference gradients that hurt model quality. You're trading routing diversity for training stability. DeepSeek's solution was to develop an auxiliary-loss-free load balancing strategy, where instead of penalizing uneven routing in the loss function, they apply a per-expert bias to routing scores and update those biases dynamically based on recent load. Maarten Grootendorst's [visual guide to MoE](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-mixture-of-experts) covers the routing mechanics well if you're trying to build intuition here.

This is genuinely hard engineering. The [Cerebras analysis of MoE routing strategies](https://www.cerebras.ai/blog/moe-guide-router) goes into how much the choice of routing algorithm affects final model quality, and the short version is: it matters a lot more than the architecture diagrams suggest.

## What DeepSeek's numbers actually show

The DeepSeek-V2 paper is worth reading for the raw efficiency numbers. Compared to DeepSeek 67B (a dense model), DeepSeek-V2 achieved:

- 42.5% lower training cost
- 93.3% reduction in KV cache
- 5.76x improvement in maximum generation throughput

The KV cache number is particularly interesting. Key-value cache is what allows transformers to avoid recomputing attention for every token on every forward pass during generation. In a large dense model, the KV cache grows proportionally with model size and context length. MoE models, by activating fewer parameters per token, generate smaller KV caches per layer, which means they can fit more concurrent requests into the same GPU memory.

This is why DeepSeek can offer API pricing at a fraction of the cost of comparable dense models. It's not just that the model is more efficient to run. It's that the reduced KV cache allows higher throughput per GPU, so the economics of serving it are fundamentally different.

## When MoE helps and when it doesn't

MoE is a good fit for inference at scale where you're serving many different types of requests. The theory is that different experts specialize in different domains, so a request about Python code routes to different experts than a request about medieval history. Whether this actually happens as cleanly as the theory suggests is debated, but the efficiency gains are real regardless.

MoE is a worse fit for fine-tuning. When you fine-tune a dense model, you're updating all the parameters toward your target domain. When you fine-tune a MoE model, you're also updating the routing decisions, which means fine-tuning can disrupt the expert specialization that the model developed during pretraining. There are approaches that address this, but it's non-trivial compared to fine-tuning a dense model.

MoE also doesn't help you if memory is your constraint rather than compute. If you can't fit the full parameter count in GPU VRAM, a 671B MoE model has the same problem as a 671B dense model. The compute efficiency advantage evaporates if you're spending it on model sharding overhead instead.

## The honest version

MoE is a real architectural advancement and the efficiency gains are not marketing. DeepSeek V3's training cost of 2.788 million H800 GPU hours for a model that competes with frontier models is genuinely impressive, and MoE is a significant reason why.

But the narrative that MoE models are just "cheaper and better" leaves out a few things. They're harder to train, harder to fine-tune, and require the same (or more) memory to serve despite doing less compute per token. The cost advantage shows up at inference throughput scale, not necessarily in your initial setup cost.

If you're evaluating MoE models for production use, the question is not just "how much does a token cost?" It's "how much does serving this model cost at my expected throughput, with my expected prompt lengths, on the hardware I have access to?" Those answers are different from the API pricing and worth working out before you commit to an architecture.

One more thing: the routing behavior of MoE models is still not fully understood. Researchers are still figuring out what individual experts actually specialize in and whether the specialization is as clean as the diagrams suggest. The [Hugging Face analysis of MoE load balancing](https://huggingface.co/blog/NormalUhr/moe-balance) goes into some of the pitfalls teams have discovered in production. It's worth reading before you decide these models are solved.

If you're writing about this kind of architectural nuance for a technical audience and you want someone who can do the research and get the details right, [my work page](/work) has examples of that kind of writing.

## Questions

**Is DeepSeek V3's 671B MoE model actually comparable to GPT-4 class models?**

On most benchmarks, yes. The SWE-bench scores and coding benchmarks put it in the same tier as frontier models. Whether that holds for your specific use case depends on what you're doing, but the quality argument is not just marketing.

**Can I run DeepSeek V3 locally?**

Technically yes, practically probably not. You need enough GPU VRAM to hold 671B parameters. In FP8, that's over 1TB. In BF16, it's closer to 1.3TB. That requires a serious multi-GPU cluster. Quantized versions bring this down substantially, but you're still talking 8+ high-end GPUs minimum.

**Why don't all models use MoE if it's more efficient?**

Training difficulty. MoE models require getting the routing right, which means solving the load balancing problem, which adds significant complexity to the training process. A dense model of the same active parameter count is simpler to train reliably. MoE pays off at scale when you have the engineering resources to get the training right.

**Does MoE improve reasoning quality or just efficiency?**

Primarily efficiency, though there's an argument that more total capacity (even if sparse) allows more specialized knowledge to accumulate. The evidence that MoE specifically improves reasoning over a dense model of the same active parameter count is mixed. What it clearly does is give you a better quality-per-compute-dollar ratio at scale.

**How do I choose between a MoE model and a dense model for my application?**

If you're calling a hosted API, use whichever model has the best quality for your task at your price point. The architecture is someone else's problem. If you're self-hosting, and you have memory constraints, a dense model of the size you can fit is usually simpler to serve. If you have memory headroom and want to maximize throughput, MoE is worth evaluating seriously.
