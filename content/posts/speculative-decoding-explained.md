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

A transformer step is expensive because the model has to pull a huge set of weights from memory. That data movement is often the bottleneck. The math is not always the slow part.

Normal decoding wastes a lot of that capacity. The model does one full pass to generate one token. Then it repeats the whole process for the next token.

Speculative decoding takes advantage of that. If a draft model guesses `K` future tokens, the target model can check them together. That means one expensive read can cover several tokens instead of just one.

Here is a simple way to picture it. Say the user asks for Python code to reverse a linked list. The draft model guesses the next four tokens are `def`, `reverse_list`, `(`, and `head`. Instead of making the large model generate those four tokens one by one, speculative decoding lets the large model check that whole chunk at once.

[Spec-Bench, the ACL 2024 benchmark](https://github.com/hemingkx/Spec-Bench) for evaluating speculative decoding methods, measured EAGLE achieving a 2.4x to 2.5x speedup over autoregressive decoding across model sizes, with a maximum of 3.0x on mathematical reasoning tasks with Vicuna-33B. The [original Google Research blog post on speculative decoding](https://research.google/blog/looking-back-at-speculative-decoding/) documented 2x to 3x improvements across translation and summarization tasks from the initial 2022 work.

[SCREENSHOT: Google Research blog post header at research.google/blog/looking-back-at-speculative-decoding/ showing the original post and any speedup figures]

## How the draft-verify loop works

The loop is easier to understand when you break it into three parts:

| Step | What happens | Why it matters |
|---|---|---|
| Draft | A smaller model proposes the next `K` tokens. | This is cheap because the draft model is small. |
| Verify | The target model evaluates the context plus those draft tokens in one pass. | This is where the latency savings come from. |
| Accept or reject | Matching tokens are kept. The first mismatch triggers resampling and the rest are discarded. | This preserves correctness while still getting speedup from accepted runs. |

The exact implementation can vary, but the pattern stays the same. A small model guesses ahead. The large model checks the guesses. Accepted tokens go straight into the output.

Using the same code example:

- The draft model guesses: `def reverse_list(head):`
- The target model checks that full stretch in one pass
- If all of it matches, those tokens are accepted immediately
- If the target model disagrees at `head`, the system keeps the accepted prefix and resumes from the first mismatch

That is the whole idea. Guess ahead, verify once, keep what matches.

The important part is that the standard version does not change the result. It is designed to sample from the same distribution as the target model on its own. The [comprehensive survey of speculative decoding techniques](https://arxiv.org/html/2401.07851v2) covers the formal proofs if you want the math.

## Acceptance rate: the only metric that matters for real-world speedup

Everything comes back to acceptance rate. If the draft model proposes four tokens and the target model accepts three, the setup looks good. If it accepts one, the benefit can disappear.

This is the number to watch because it tells you whether the draft model is helping or just adding work.

Go back to the linked-list example. If the model is generating boilerplate Python, the draft model will often guess right. Acceptance rate goes up. If the model is writing a more open-ended explanation of tradeoffs in distributed systems, the draft model is more likely to drift. Acceptance rate goes down.

Acceptance rate depends on two things:

- **Task predictability.** Code, structured outputs, and repetitive continuations tend to accept well. Open-ended generation usually accepts less.
- **Draft-target alignment.** The draft model needs to guess what the target model would have picked. If the two models behave differently, rejection goes up.

That is why benchmark numbers can mislead you. A setup that looks great on code or math can look average on open-ended generation. Measure acceptance rate on your own workload before you plan around any published speedup.

That is also why coding assistants are such a natural fit for speculative decoding. A lot of generated code has predictable local structure. Chat responses usually have more room to wander.

## The main variants worth knowing

You do not need every variant in your head. These are the ones worth recognizing:

| Variant | What it does | Tradeoff |
|---|---|---|
| External draft model | A separate small model makes the guesses. | Easy to understand, but you have another model to run. |
| Medusa | Extra heads on the target model predict future tokens. | Usually better matched, but needs model-side training work. |
| Speculative Streaming | The target model uses its own signals to guess ahead. | Cleaner serving setup, but gains vary. |
| Mirror Speculative Decoding | Lets draft and target models use different vocabularies. | Helpful when the two models come from different families. |

The [BentoML inference handbook's speculative decoding section](https://bentoml.com/llm/inference-optimization/speculative-decoding) and their [practical 3x speedup guide](https://www.bentoml.com/blog/3x-faster-llm-inference-with-speculative-decoding) are useful if you want the practical version. [Apple Machine Learning Research](https://machinelearning.apple.com/research/llm-inference) and [Mirror Speculative Decoding](https://machinelearning.apple.com/research/mirror) cover two important variants.

[SCREENSHOT: BentoML blog post at bentoml.com/blog/3x-faster-llm-inference-with-speculative-decoding showing the chart with draft model comparison]

## When speculative decoding helps and when it hurts

**It helps most when:**

- You are serving single requests or low-concurrency workloads. The draft-verify loop's gains are per-request latency improvements, which is what matters for interactive applications like chat and coding assistants.
- Your outputs are partly predictable. Structured outputs, code generation, and continuation tasks usually get higher acceptance rates.
- You are optimizing TTFT and inter-token latency. Speculative decoding cuts the number of target-model steps needed to produce a response. I wrote more about [why TTFT matters for interactive applications in my earlier post on time to first token](/blog/time-to-first-token-ttft/).

If your product is a coding assistant that spends its day generating imports, function signatures, and test scaffolding, this is exactly the kind of workload where speculative decoding can help.

**It hurts or does not help when:**

- You are running high-throughput batch inference. If the GPU is already busy serving many requests at once, the draft model can add overhead without giving you much back.
- Your acceptance rate is low. If the draft model keeps guessing wrong, the extra work can add latency instead of removing it. This shows up more often in creative writing, domain-heavy outputs, and multilingual text.
- You have tight memory constraints. Running a draft model next to a large target model takes more GPU memory. That can force smaller batch sizes and wipe out the gain.

If the same system switches from code generation to writing long product copy, the shape of the workload changes. The draft model misses more often, so the speedup can shrink fast.

## FAQ

**Does speculative decoding change the quality of outputs?**

No in the standard rejection-sampling approach. It is designed to preserve the exact output distribution of the target model. Some faster variants relax that guarantee, so check what your inference stack actually uses.

**How do I know if my use case has a high enough acceptance rate?**

Run it and measure. Most inference frameworks expose acceptance rate directly. As a rough rule, above 70% is promising. Below 50%, gains often get thin. Code and structured outputs usually do better than open-ended generation.

**What is the right draft model to use?**

Ideally, you want a purpose-built speculator trained to match the target model. A smaller model from the same family is a good second choice. A generic small model from a different family is usually the weakest option. Medusa is worth considering if you can afford the training work.

**How does speculative decoding interact with quantization?**

They can stack, but the gain changes. Quantization already reduces some of the memory pressure that makes speculative decoding useful, so the upside may shrink. It can still help, especially at low concurrency. The [2025 benchmark on test-time scaling](https://arxiv.org/abs/2509.04474) includes evaluation under different model configurations.

**Is speculative decoding worth implementing for a small team?**

It depends on where you run inference. If you call a hosted API, this is mostly the provider's problem. If you run your own stack with vLLM, TGI, or similar frameworks, it is worth testing for latency-sensitive workloads.
