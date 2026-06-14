---
title: "LLM Inference Optimization: What Actually Works in Production"
date: "2026-05-06"
slug: "llm-inference-optimization"
description: "A practical breakdown of the inference optimization techniques that move the needle — batching, quantization, caching, and attention kernels — with concrete numbers and the tradeoffs between them."
tags:
- ai
- llm
- infrastructure
status: published
---

Inference is where LLM projects die. The model works in testing. Push it to production and latency climbs, throughput craters, and your GPU budget evaporates. A demo that answers one question in 400ms can turn into a serving system that buckles at 50 concurrent users, and the problem only worsens as traffic grows.

Across vLLM, TensorRT-LLM, and SGLang, I've spent time tuning inference stacks until they hold up under load. The techniques that actually matter fall into four categories: batching, memory management, quantization, and attention kernels. Here's how they work and where they break.

<div class="visual-wrapper">
  <div class="visual-title">Inference Optimization Stack</div>
  <div class="visual-container">
    <iframe src="/static/visuals/inference-optimization-stack.html" title="LLM inference optimization stack: batching, flash attention, KV cache, quantization, and speculative decoding with speedup contributions" loading="lazy"></iframe>
  </div>
</div>

## Batching: The First Lever

Running one request at a time leaves your GPU mostly idle, waiting on the next prompt while thousands of cores do nothing. Batching fixes the idleness by packing multiple requests together, and how you batch matters enormously.

**Static batching** groups requests at the start of inference. It carries a fatal flaw: you wait for the slowest request in the batch to finish before processing the next one. Picture a single 2,000-token completion in a batch of mostly 50-token replies. Everyone else sits and waits for that one straggler to drain.

**Continuous batching** (also called iteration-level scheduling) addresses the straggler problem. Requests enter and leave the batch dynamically, at each token generation step, so a finished sequence frees its slot immediately and a queued request drops in. Think of it as a bus that picks up and drops off passengers at every stop rather than waiting for the whole bus to empty before the next group can board. Continuous batching is what vLLM uses by default, and it's the reason vLLM typically delivers 10-20x higher throughput than naive batching for real-world request distributions.

Memory is the tradeoff. Continuous batching requires pre-allocating enough memory for the maximum batch size you want to support. Set `max_num_seqs=256` on a workload that rarely sees more than 30 concurrent sequences, and you've reserved VRAM for 226 phantom requests, memory that could have gone toward a longer context window or more model weights.

## KV Cache Management

Every token your model generates needs to remember all previous tokens in the sequence. Storing those keys and values in GPU memory is the KV cache, and for long contexts it becomes the dominant memory consumer, often dwarfing the weights themselves.

Run the numbers and the pressure is obvious. A 70B model with a 128K context window at full precision needs roughly 64GB just for the KV cache on a single sequence. Sixteen concurrent sequences consume 1TB, which no single GPU holds. Context length and throughput pull against each other for exactly this reason: every extra token of context steals room you could have spent on another concurrent user.

**PagedAttention** (vLLM's approach) manages the KV cache the way an operating system manages RAM, mapping non-contiguous physical blocks to logical sequence positions instead of demanding one long contiguous slab per request. Fragmentation disappears, and memory utilization gets close to perfect. PagedAttention typically lets you serve 2-4x more concurrent sequences than naively managed KV caches on the same memory budget.

**KV cache eviction** becomes critical once memory is full. LRU is the default, though it ignores the fact that some keys get attended to far more often than others. Recent work on "importance-based" eviction (dropping tokens the model attended to least) shows modest improvements, but the gains stay small enough that most systems keep the simplicity of LRU. I dug into this when examining [KV cache eviction accuracy](/blog/kv-cache-eviction-accuracy/).

## Quantization: Trading Precision for Throughput

Quantization reduces the numerical precision of weights and activations (typically from 16-bit or 32-bit floats to 8-bit or 4-bit integers). Fitting more model parameters into the same VRAM is the goal, which buys you larger batch sizes or lets you run the same model on cheaper hardware.

**FP8 quantization** (8-bit floating point) is now well-supported in both Ampere and Hopper architectures. For most models, FP8 delivers near-identical output quality to BF16 with a 40-50% memory reduction. The speedup is real but modest, since you still dequantize before computing, so the saved memory bandwidth is the primary benefit, not raw arithmetic throughput.

**INT8 quantization** using quantization-aware training or post-training calibration pushes harder. For language tasks, it typically degrades quality by 1-3% on standard benchmarks, acceptable for many production use cases like summarization or chat. Code generation is where the degradation bites. I've seen 5-8% drops on HumanEval with naive INT8 approaches, the kind of regression that turns a working function into one with an off-by-one bug you only catch in review.

**GPTQ and AWQ** are the two dominant post-training quantization methods. GPTQ takes longer to apply and produces slightly better quality at 4-bit. AWQ runs faster and preserves more quality at 4-bit for most tasks, which is why SGLang has defaulted to AWQ for its 4-bit quantization path.

Here is the rule I follow. Reach for FP8 when your hardware supports it and you need zero quality compromise. Move to INT8 when memory is the bottleneck and you can tolerate small quality losses. Drop to 4-bit only when you're severely memory-constrained and the quality tradeoff is acceptable for the specific job in front of you.

## Attention Kernels: Flash Attention and Beyond

Standard attention materializes the full attention matrix: O(n²) memory for sequence length n. A 4,096 token context produces 16M values. Stretch that to 128K and you're at 16B values, which alone overflows the memory of most GPUs before the model has generated a single token.

**Flash Attention** computes attention in tiles that fit in GPU SRAM, streaming through HBM with minimal memory usage. The trick resembles reading a huge spreadsheet column by column instead of loading the entire sheet into memory at once: it processes the matrix in chunks small enough to keep on-chip, so it never has to write the full result back out. That gets you O(n) memory instead of O(n²) and runs typically 2-4x faster for longer sequences. Any inference stack without Flash Attention leaves real performance on the table, so it's now a baseline expectation.

**Flash Attention 2** improved the tile sizes for A100 and H100 architectures, delivering another 10-20% speedup over FA1 for many workloads. Flash Attention 3 (available on H100s with FP8 support) pushes this further with overlapping compute and memory operations.

**PagedAttention** I already mentioned in the KV cache context, but it's worth noting it combines with Flash Attention. vLLM uses PA by default with FA2 as its attention kernel.

## What I Actually Reach For

When I'm optimizing a new inference deployment, I work in this order:

1. **Enable continuous batching** if not already on: this is the single biggest win for most workloads.
2. **Flash Attention 2**: upgrade from standard attention if not already present.
3. **FP8 quantization**: if VRAM is tight, apply it first and check quality before going to INT8.
4. **PagedAttention**: if running long contexts or high concurrency, this is essential.
5. **INT8 or 4-bit**: only if the above still don't get you enough headroom.

Speculative decoding earns its place once the baseline is fast enough. As I wrote in my [speculative decoding breakdown](/blog/speculative-decoding-explained/), it delivers 2-3x token throughput gains for the right workload, though it requires running two models and adds implementation complexity you don't want to carry while the basics are still unsettled.

Jumping to the advanced stuff is the common mistake, like wiring up speculative decoding on a server that hasn't even enabled continuous batching yet. It's the equivalent of bolting on a turbocharger and leaving the handbrake engaged. The draft model adds weeks of work, and a single config flag for continuous batching would have moved throughput far more. The basics deliver more than the sophisticated techniques do.

## The Hardware Angle

No software optimization compensates for the wrong hardware choice. Your inference stack matters, and so does the GPU underneath it.

For batch inference with long sequences, H100s with NVLink earn their cost, because the high bandwidth between GPUs lets tensor parallelism scale efficiently across cards. A100s hold up well at smaller scales. RTX 4090s shine for single-GPU development and small-scale serving, yet a 70B model at 128K context simply won't fit in their 24GB.

Running on consumer hardware with limited VRAM flips the priority order: quantization becomes your first move rather than a refinement on top of already-sufficient memory. For workloads with repeated system prompts or shared prefixes, like a RAG app that prepends the same 3,000-token instruction block to every query, [prompt caching](/blog/prompt-caching-what-it-is-and-when-the-math-works/) is worth understanding as a complementary technique. It cuts the compute cost of re-encoding tokens that don't change between requests, and it compounds well with the batching and KV cache strategies above.
