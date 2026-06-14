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

Inference speed is the biggest hurdle I keep running into with interactive LLM applications. Watching a 70B model dribble out text one token at a time, while a user stares at a blinking cursor, feels slow in a way that no amount of clever UI hides. The first instinct I had, and the one I see most teams reach for, was to throw more GPUs at the problem. That instinct ignores the physics of how these models actually run, and it costs a fortune for a speedup that never quite arrives.

Large models are "memory-bound." When I generate a single token, the GPU spends most of its time waiting for the model's weights to travel from high-bandwidth memory into the compute units, the same memory wall that makes [KV cache eviction such a high-value optimization](/blog/kv-cache-eviction-accuracy/). The arithmetic of turning those weights into one token finishes almost instantly, then the cores sit idle waiting for the next batch of weights. Picture a chef with a tiny cutting board who has to walk to a pantry across the building for each ingredient. The chopping takes seconds. The walking takes minutes. Speculative decoding is how I put that idle compute to work without adding a single GPU.

The numbers make the imbalance concrete. A model serving a single request often pushes the GPU's compute units to a few percent utilization even as memory bandwidth pegs near its ceiling, the inverse of what you see during training. Training runs in big batches that keep every core busy, so the chip looks healthy on a dashboard. Single-stream inference starves those same cores. Adding a second GPU does nothing for one user's request, because the request was never waiting on math in the first place. It was waiting on the bus.

## The draft-verify loop in practice

Two models do the work. A small "draft" model guesses the next few tokens in rapid succession, and a large "target" model verifies all of those guesses in a single parallel step. The draft model is fast and frequently wrong, something like a 1B model running ahead. The target model is slow and authoritative, the 70B you actually want answering.

<div class="visual-wrapper">
  <div class="visual-title">SPECULATIVE DECODING</div>
  <div class="visual-container">
    <iframe src="/static/visuals/speculative-decoding.html" title="A small draft model proposes several tokens, the large target model verifies them in parallel, accepted tokens are kept and rejected ones discarded" loading="lazy"></iframe>
  </div>
</div>

The system works because checking is cheaper than generating. Verifying four or five proposed tokens costs the target model almost the same wall-clock time as producing one, since it loads its weights once and runs the candidates through together. When the draft model's guesses are correct, I have generated several tokens in the time budget of a single forward pass. When a guess is wrong, I throw away that token and everything after it, then resume from the last correct position. A useful way to think about it: the draft model writes a rough sentence in pencil, and the target model reads the whole sentence at once, accepting words until it hits one it would not have written, then taking over from there. Nothing wrong ever slips through, because the target model has the final say on every token.

That last point matters more than the speed. I worried the first time I enabled this that the small model would quietly degrade output quality, the way a cheaper autocomplete might. It cannot. The acceptance check guarantees the result is mathematically identical to what the target model would have produced on its own. The draft model only ever proposes. It never decides.

A walk through one round makes the savings tangible. Say the draft model proposes five tokens, then the target model runs all five candidates plus its own next prediction through a single forward pass. If the target agrees with the first three drafted tokens and disagrees on the fourth, I keep those three, take the target's own corrected token for the fourth position, and discard the fifth. That round produced four real tokens for the price of one slow forward pass and one cheap draft pass. The worst case, where the target rejects the very first drafted token, still produces one token, the same as ordinary decoding, so the floor on performance is plain old generation rather than a regression.

## Why this is "free" speedup

You are already paying for the memory bandwidth to drag the large model's weights across the bus on every step. A 1B draft model adds maybe a percent or two to that bill, because its weights are a fraction of the size and load in a sliver of the time. The verification rides on GPU compute cycles that were sitting idle anyway, the same cores that finished their real work and went quiet waiting for memory. So the speedup comes out of slack the hardware was already wasting, which is why I describe it as close to free.

How much you get back depends on the "acceptance rate," the share of drafted tokens the target model keeps. The rate climbs when the text is predictable. Boilerplate code, structured JSON, and the verbose scaffolding around an answer ("Sure, here is the function you asked for...") get drafted almost perfectly, and I have watched those sections fly. The rate drops on genuinely creative or high-entropy passages where even a good small model cannot anticipate the large one. A strong pairing lands a 2x to 3x speedup across a typical mix of requests. Even a modest acceptance rate trims the latency a user feels, and that improvement shows up directly in [time to first token, the metric that determines AI snappiness](/blog/time-to-first-token-ttft/).

Choosing the draft model is where I have spent the most tuning effort. Too small, and its guesses get rejected so often that the extra verification passes erase the gains, leaving me slower than plain decoding. Too large, and the draft step itself becomes the bottleneck, since now I am loading meaningful weights twice per round. The sweet spot I keep returning to is a model from the same family as the target, around a tenth to a twentieth of its size, because shared training data makes the small model think like the big one and pushes the acceptance rate up.

Speculative length is the second knob, and it interacts with acceptance rate in a way that bit me early. Drafting more tokens per round sounds like a pure win, since a long correct guess collapses many steps into one. The cost hides in the rejections. A draft of eight tokens that gets rejected at position two wasted the work of drafting six tokens that never shipped, and on a workload heavy with creative text that waste piles up fast. For chat traffic full of code and structured output, a longer draft pays off. For open-ended generation, a shorter draft of two or three tokens keeps the rejection penalty small. I tune this per deployment rather than trusting a default.

Batching changes the calculus too, which surprised me. The whole technique leans on idle compute, so as I pack more concurrent requests onto one GPU, those formerly idle cores get busy serving other users and the free lunch shrinks. Speculative decoding shines brightest on latency-sensitive, low-concurrency serving, the interactive chat session where one user waits on one stream. A high-throughput batch job that already saturates the GPU sees a smaller benefit, sometimes none, because there was no slack left to borrow.

## Implementation options

Standard speculative decoding needs a separate draft model, which means I run, serve, and version two checkpoints that have to stay compatible. Plenty of teams find that operational overhead annoying, so newer techniques fold the drafting straight into the large model. Medusa bolts a handful of extra prediction heads onto the target so it proposes several future tokens itself, and Lookahead decoding generates and verifies candidate n-grams from the model's own recent output. Both approaches kill the need to babysit two separate networks, at the cost of either fine-tuning the heads or accepting a lower acceptance rate than a well-matched draft model gives me.

Self-drafting suits one situation especially well. When I cannot find a good small sibling for my target model, or the deployment has no room for a second checkpoint in memory, Medusa-style heads let me get a respectable speedup from the one model I already loaded. For a model with a strong small relative on hand, a dedicated draft model still tends to win on raw acceptance rate.

Production inference engines have made all of this far easier than it was. vLLM and TensorRT-LLM both support speculative decoding natively now, so turning it on is closer to setting a config flag than wiring up a research prototype. It has quietly become a default optimization rather than an exotic one. Anyone hosting their own models and feeling the latency squeeze should enable it before reaching for a bigger GPU budget, measure the acceptance rate on real traffic, and tune the draft model from there. The speedup was sitting in the hardware the whole time, waiting for the weights to show up.
