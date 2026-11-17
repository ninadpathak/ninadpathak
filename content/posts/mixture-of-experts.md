---
category: ai-engineering
primary_query: mixture of experts
siblings:
- llm-inference-optimization
- speculative-decoding
date: 2026-03-13
description: A mixture of experts (MoE) model routes each token through a few of its
  expert networks. How routing works, with a runnable layer, and why DeepSeek-V3 computes
  with 37B parameters and still has to load 671B.
status: published
work_note: "Tutorials, explainers and comparisons for AI companies are my work as a freelance technical writer. I'm Ninad Pathak, and I build the example and run it before I draft, so your engineers review working code. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'How Mixture of Experts (MoE) Models Work'
slug: mixture-of-experts
---

On November 14 a Show HN put [DeepSeek-V3's architecture in 190 lines of JAX](https://github.com/Vaibhaav-Tiwari/deepseek-v3-jax), trained on a MacBook Air on public-domain detective fiction. Its README gives the model's size as 36.2M parameters, with 13.6M used per token.

Those two numbers are the whole idea. A mixture of experts (MoE) model splits each layer's feed-forward network into many smaller networks called experts, and a router sends every token through only a few of them.

The idea is older than the transformer. It comes from a 1991 paper, [Adaptive Mixtures of Local Experts](https://en.wikipedia.org/wiki/Mixture_of_experts), and in 2017 [Shazeer and colleagues](https://arxiv.org/abs/1701.06538) made the gate sparse, so an expert that isn't chosen costs no compute at all.

Mixture of experts is how DeepSeek-V3 computes with 37B parameters per token while owning 671B. It also sets the hardware bill in a way that surprises people, and that's the part of [AI engineering](/articles/ai-engineering/) this page is about: compute follows the active count, and memory follows the total.

## What is a mixture of experts model?

A mixture of experts model is a neural network that holds many expert sub-networks per layer and runs only a few of them for each token. A dense model runs every parameter for every token.

The vendors publish both counts, and the ratio between them is the saving in compute:

| Model | Total parameters | Used per token | Source |
|---|---|---|---|
| Mixtral 8x7B | 46.7B | 12.9B | [Mistral, December 2023](https://mistral.ai/news/mixtral-of-experts) |
| DeepSeek-V2 | 236B | 21B | [DeepSeek, May 2024](https://arxiv.org/abs/2405.04434) |
| DeepSeek-V3 | 671B | 37B | [DeepSeek, December 2024](https://arxiv.org/abs/2412.19437) |

Mistral's announcement states the claim plainly, saying Mixtral "processes input and generates output at the same speed and for the same cost as a 12.9B model". That sentence is about compute, and I'd keep it there, because nothing in it says the other 33.8B parameters can stay on disk.

## How does MoE routing work?

A router scores every expert for the current token, keeps the top few, and mixes their outputs by score. Here's one such layer in NumPy, with 16 experts and 2 chosen per token:

```python
"""One mixture-of-experts layer in NumPy: what a token computes with, and what must stay loaded."""
import numpy as np

rng = np.random.default_rng(0)
D, HIDDEN, EXPERTS, TOP_K = 64, 256, 16, 2

router = rng.normal(size=(D, EXPERTS))                    # one score per expert
w_in = rng.normal(size=(EXPERTS, D, HIDDEN)) * 0.05       # each expert is a small feed-forward network
w_out = rng.normal(size=(EXPERTS, HIDDEN, D)) * 0.05


def moe_layer(token):
    scores = token @ router
    chosen = np.argsort(scores)[-TOP_K:]                  # keep the top-k experts, skip the rest
    gates = np.exp(scores[chosen]) / np.exp(scores[chosen]).sum()
    out = sum(g * (np.maximum(token @ w_in[e], 0) @ w_out[e]) for g, e in zip(gates, chosen))
    return out, chosen


per_expert = w_in[0].size + w_out[0].size
total = router.size + EXPERTS * per_expert
active = router.size + TOP_K * per_expert
print(f"parameters in the layer:   {total:,}")
print(f"parameters one token uses: {active:,} ({active / total:.1%})")

tokens = rng.normal(size=(64, D))
seen = set()
for count, token in enumerate(tokens, start=1):
    _, chosen = moe_layer(token)
    seen.update(int(e) for e in chosen)
    if count in (1, 4, 16, 64):
        print(f"after {count:>2} tokens: {len(seen):>2} of {EXPERTS} experts have been needed")
```

Running `python moe_demo.py` with NumPy 2.0.2 printed:

```text
parameters in the layer:   525,312
parameters one token uses: 66,560 (12.7%)
after  1 tokens:  2 of 16 experts have been needed
after  4 tokens:  8 of 16 experts have been needed
after 16 tokens: 13 of 16 experts have been needed
after 64 tokens: 16 of 16 experts have been needed
```

The router here has random weights, so it shows the mechanism and says nothing about what a trained router learns. Even so, the first two lines are the arithmetic every MoE model card is built on: one token touched 12.7% of the layer.

DeepSeek-V3 does the same thing at a larger size. Its [technical report](https://arxiv.org/html/2412.19437v2) describes each MoE layer as 1 shared expert that always runs plus 256 routed experts, with 8 of the routed ones activated per token.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/mixture-of-experts/moe-routing.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/mixture-of-experts/moe-routing.narrow.svg" width="288" height="664"><img class="np-has-narrow" src="/static/images/diagrams/mixture-of-experts/moe-routing.svg" width="720" height="256" alt="Each token passes through a router that activates 8 of the 256 routed experts in a DeepSeek-V3 layer. The other 248 stay idle for that token." loading="lazy" decoding="async"></picture></a>
  <figcaption>Compute follows the 8 active experts. All 256 stay loaded, because the next token may be routed to different ones.</figcaption>
</figure>

## Why does an MoE model still need all its memory?

Every expert has to be loaded because the router picks per token, and nobody knows its pick until the token arrives. Look at the last four lines of that output: one token needed 2 experts, and 64 tokens needed all 16.

So the memory bill is plain multiplication on the total. DeepSeek's 671B parameters come to about 1.34 TB for the weights alone at 16 bits each, and about 671 GB at 8 bits.

People do run these models on small machines, though, and it's worth seeing how. On November 8 a project called [llama-modchip](https://github.com/synchopate/llama-modchip) reached the Hacker News front page with a README reporting a 284B DeepSeek model in a 57.99 GiB file, and resident memory a little above that.

Divide it out, which is my arithmetic and not the README's, and that's about 1.75 bits per parameter. Going by the file size, the memory came down by storing each weight in fewer bits, and the [first thing the thread asked](https://news.ycombinator.com/item?id=50412500) was at which quantization, and what the output looks like.

My page on [LLM inference optimization](/articles/llm-inference-optimization/) has the same trap in figures from an NVIDIA tutorial, a 753B model whose whole checkpoint sits in GPU memory while 40B run per token.

## How do MoE models keep every expert in use?

They balance the load during training, because a router left alone tends to favour a few experts. DeepSeek's report calls the failure "routing collapse" and says the usual fix, an extra loss term that punishes uneven load, hurts model quality when it's set too high.

DeepSeek's answer is a bias per expert that's added to the routing score. An expert that's been getting too many tokens has its bias lowered, and an idle one has it raised.

The JAX project measured this on its small model, which is why I opened with it. At step 2000, expert load ran from 5.7% to 6.9% with the bias, where an even split is 6.25%, and from 0.09% to 18.6% without it.

Validation loss was the same both ways, 3.921 against 3.923. That's one run of a 36.2M-parameter model on 207 books, so I'd take it as a clean picture of the mechanism and not as proof at DeepSeek's size.

## What does MoE save, in DeepSeek's own numbers?

DeepSeek-V2's paper compares the MoE model with the company's earlier dense 67B model. It reports 42.5% lower training cost, a KV cache 93.3% smaller and 5.76 times the maximum generation throughput.

I wouldn't credit all of that to the experts. The same abstract assigns the KV cache saving to a change in the attention layers called Multi-head Latent Attention, so the throughput figure is the result of both changes together.

Sparse routing isn't the only way to cut the cost of a token, either. [Speculative decoding](/articles/speculative-decoding/) keeps the model dense and has a cheap predictor draft tokens for it to check.

## When does the architecture matter to you?

It matters when you're the one buying the memory. Behind an API you pay per token and the provider carries the weights, so I'd judge an MoE model there like any other model, on your own task.

Self-hosting flips that. Size the hardware from the total parameter count, and expect the saving in compute to show up as more tokens per second from hardware you've already filled.

## FAQ

**Is an MoE model with 37B active parameters the same as a 37B dense model?**

In compute per token, roughly yes. For what it can store, no, because each token draws on a different set of experts out of the full 671B.

**Can I run DeepSeek-V3 locally?**

Only on a machine that can hold all 671B parameters. That's about 671 GB at 8 bits per weight before any cache, and a smaller footprint means quantizing further.

**What is routing collapse?**

Routing collapse is when the router sends nearly all tokens to a few experts and the rest go unused. DeepSeek counters it with a per-expert bias on the routing score.

**Do all layers in an MoE model use experts?**

No. Experts replace only the feed-forward part of a layer, and DeepSeek's report keeps an ordinary feed-forward network in the first few layers.

**Who came up with mixture of experts?**

The method dates to a 1991 paper by Jacobs and colleagues. The sparse version used in language models follows a 2017 paper by Shazeer and colleagues.
