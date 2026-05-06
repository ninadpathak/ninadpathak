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

Inference is where LLM projects die. The model works in testing. In production, latency climbs, throughput craters, and your GPU budget evaporates. The gap between a proof-of-concept and a serving system that doesn't embarrass you in production is wide — and it gets wider as usage grows.

I've spent time working with inference stacks across vLLM, TensorRT-LLM, and SGLang. The techniques that actually matter fall into four categories: batching, memory management, quantization, and attention kernels. Here's how they work and where they break.

## Batching: The First Lever

The naive approach runs one request at a time. Your GPU sits idle while waiting for the next prompt. Batching solves this by packing multiple requests together — but how you batch matters enormously.

**Static batching** groups requests at the start of inference. It has a fatal flaw: you wait for the slowest request in the batch to finish before processing the next one. A single long completion blocks everything.

**Continuous batching** (also called iteration-level scheduling) addresses this. Requests enter and leave the batch dynamically, at each token generation step. New requests can slot in when earlier ones complete. This is what vLLM uses by default, and it's the reason vLLM typically delivers 10-20x higher throughput than naive batching for real-world request distributions.

The tradeoff is memory. Continuous batching requires pre-allocating enough memory for the maximum batch size you want to support. If you set `max_num_seqs=256` but your workload never actually uses that many concurrent sequences, you're wasting VRAM that could go toward a larger context window or more model weights.

## KV Cache Management

Every token your model generates needs to remember all previous tokens in the sequence. Storing these in GPU memory is the KV cache — and for long contexts, it becomes the dominant memory consumer.

The raw math: a 70B model with a 128K context window at full precision needs roughly 64GB just for the KV cache on a single sequence. Run 16 concurrent sequences and you've consumed 1TB. This is why context length and throughput are in direct tension.

**PagedAttention** (vLLM's approach) manages the KV cache like virtual memory — non-contiguous physical blocks mapped to logical sequence positions. This eliminates fragmentation and allows near-perfect memory utilization. In practice, PagedAttention typically lets you serve 2-4x more concurrent sequences than naively managed KV caches with the same memory budget.

**KV cache eviction** becomes critical once memory is full. LRU is the default, but it ignores the fact that some keys are accessed far more frequently than others. Recent work on "importance-based" eviction ( evicting tokens the model attended less to ) shows modest improvements, but the gains are small enough that most systems stick with LRU simplicity. I looked at this in more detail when examining [KV cache eviction accuracy](/articles/kv-cache-eviction-accuracy).

## Quantization: Trading Precision for Throughput

Quantization reduces the numerical precision of weights and activations — typically from 16-bit or 32-bit floats to 8-bit or 4-bit integers. The goal is to fit more model parameters in the same VRAM, enabling larger batch sizes or smaller hardware.

**FP8 quantization** (8-bit floating point) is now well-supported in both Ampere and Hopper architectures. For most models, FP8 delivers near-identical output quality to BF16 with a 40-50% memory reduction. The speedup is real but modest — you still need to dequantize to compute, so the memory bandwidth savings are the primary benefit.

**INT8 quantization** using quantization-aware training or post-training calibration is more aggressive. For language tasks, it typically degrades quality by 1-3% on standard benchmarks, which is acceptable for many production use cases. For code generation, the degradation hits harder — I've seen 5-8% drops on HumanEval with naive INT8 approaches.

**GPTQ and AWQ** are the two dominant post-training quantization methods. GPTQ is slower to apply but produces slightly better quality at 4-bit. AWQ is faster and preserves more quality at 4-bit for most tasks, which is why SGLang has defaulted to AWQ for its 4-bit quantization path.

The rule I follow: use FP8 if your hardware supports it and you need zero quality compromise. Use INT8 if memory is the bottleneck and you can tolerate small quality losses. Use 4-bit only when you're severely memory-constrained and the quality tradeoff is acceptable for your use case.

## Attention Kernels: Flash Attention and Beyond

The standard attention implementation materializes the full attention matrix — O(n²) memory for sequence length n. For a 4,096 token context, that's 16M values. For 128K, it's 16B.

**Flash Attention** computes attention in tiles that fit in GPU SRAM, streaming through HBM with minimal memory usage. It achieves O(n) memory instead of O(n²) and is typically 2-4x faster for longer sequences. This is now a baseline expectation — any inference stack without Flash Attention is leaving significant performance on the table.

**Flash Attention 2** improved the tile sizes for A100 and H100 architectures, delivering another 10-20% speedup over FA1 for many workloads. Flash Attention 3 (available on H100s with FP8 support) pushes this further with overlapping compute and memory operations.

**PagedAttention** I already mentioned in the KV cache context, but it's worth noting it combines with Flash Attention — vLLM uses PA by default with FA2 as its attention kernel.

## What I Actually Reach For

When I'm optimizing a new inference deployment, I work in this order:

1. **Enable continuous batching** if not already on — this is the single biggest win for most workloads.
2. **Flash Attention 2** — upgrade from standard attention if not already present.
3. **FP8 quantization** — if VRAM is tight, apply it first and check quality before going to INT8.
4. **PagedAttention** — if running long contexts or high concurrency, this is essential.
5. **INT8 or 4-bit** — only if the above still don't get you enough headroom.

Speculative decoding is worth adding once the baseline is fast enough. As I wrote in my [speculative decoding breakdown](/articles/speculative-decoding-explained), it delivers 2-3x token throughput gains for the right workload, but it requires two models and adds implementation complexity that matters when you're still chasing the fundamentals.

The common mistake is jumping to the advanced stuff — setting up speculative decoding on a system that hasn't enabled continuous batching yet. The fundamentals deliver more than the sophisticated techniques do.

## The Hardware Angle

No software optimization compensates for wrong hardware choices. The inference stack matters, but so does whether you're on the right GPU.

For batch inference with long sequences, H100s with NVLink matter — the high bandwidth between GPUs allows tensor parallelism to scale efficiently. A100s work well at smaller scales. RTX 4090s are excellent for single-GPU development and small-scale serving but lack the VRAM for large models at long context lengths.

If you're on consumer hardware with limited VRAM, quantization becomes your primary lever rather than an optimization on top of already-sufficient memory.
