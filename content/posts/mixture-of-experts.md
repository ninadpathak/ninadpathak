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

A model that owns 36.2M parameters and uses 13.6M of them for each token is a mixture of experts. A mixture of experts (MoE) model splits each layer's feed-forward network into many smaller networks called experts, and a router sends every token through only a few of them.

Mixture of experts is older than the transformer, which dates from 2017. The method comes from a 1991 paper, [Adaptive Mixtures of Local Experts](https://en.wikipedia.org/wiki/Mixture_of_experts), and in 2017 [Shazeer and colleagues](https://arxiv.org/abs/1701.06538) changed the router so that it picks only a few experts per input, which means an expert that isn't picked costs no compute at all.

Mixture of experts is how DeepSeek-V3 computes with 37B parameters per token while owning 671B. The catch is in the hardware: the GPUs do the work of a 37B model on each token, and their memory still has to hold all 671B parameters.

That split between compute and memory is the part of [AI engineering](/articles/ai-engineering/) this page covers, with a 16-expert layer you can run to see why it happens.

## What is a mixture of experts model?

A mixture of experts model is a neural network that holds many expert sub-networks per layer and runs only a few of them for each token. A dense model runs every parameter for every token.

Model vendors publish both numbers, the total parameter count and the count used per token. Divide the second by the first and you get the share of the model that runs for each token, which is 5.5% for the largest model in this table:

| Model | Total parameters | Used per token | Source |
|---|---|---|---|
| Mixtral 8x7B | 46.7B | 12.9B | [Mistral, December 2023](https://mistral.ai/news/mixtral-of-experts) |
| DeepSeek-V2 | 236B | 21B | [DeepSeek, May 2024](https://arxiv.org/abs/2405.04434) |
| DeepSeek-V3 | 671B | 37B | [DeepSeek, December 2024](https://arxiv.org/abs/2412.19437) |

Mistral's announcement states the claim plainly, saying Mixtral "processes input and generates output at the same speed and for the same cost as a 12.9B model".

Mistral's sentence is a claim about speed and compute cost. It says nothing about memory, and the 33.8B parameters that a token doesn't use still have to be loaded for the model to run.

## How does MoE routing work?

A router scores every expert for the current token, keeps the top few, and mixes their outputs by score. The script below builds one MoE layer in NumPy, with 16 experts and 2 experts chosen per token:

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

The router in this script has random weights, so the output shows how routing works and not which experts a trained router would prefer. The first two lines of output are the same arithmetic as the table above: the layer has 525,312 parameters, and one token used 66,560 of them, or 12.7%.

DeepSeek's 671B model routes tokens the same way with more experts. Its [technical report](https://arxiv.org/html/2412.19437v2) describes each MoE layer as 1 shared expert that always runs plus 256 routed experts, with 8 of the routed ones activated per token.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/mixture-of-experts/moe-routing.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/mixture-of-experts/moe-routing.narrow.svg" width="288" height="664"><img class="np-has-narrow" src="/static/images/diagrams/mixture-of-experts/moe-routing.svg" width="720" height="256" alt="Each token passes through a router that activates 8 of the 256 routed experts in a DeepSeek-V3 layer. The other 248 stay idle for that token." loading="lazy" decoding="async"></picture></a>
  <figcaption>Compute follows the 8 active experts. All 256 stay loaded, because the next token may be routed to different ones.</figcaption>
</figure>

## Why does an MoE model still need all its memory?

An MoE model needs all its memory because the router chooses experts one token at a time, and the choice for a token isn't known until that token arrives. The last four lines of the script's output show the effect: 1 token needed 2 of the 16 experts, 16 tokens needed 13, and 64 tokens needed all 16.

So the memory an MoE model needs is its total parameter count multiplied by the bits stored per parameter. DeepSeek's 671B parameters come to about 1.34 TB for the weights alone at 16 bits each, and about 671 GB at 8 bits.

People do run very large MoE models on desktop machines, and they do it by shrinking each weight, not by loading fewer experts. On November 8 a project called [llama-modchip](https://github.com/synchopate/llama-modchip) reached the Hacker News front page with a README reporting a 284B DeepSeek model in a 57.99 GiB file, and resident memory a little above that.

Divide 57.99 GiB by 284B parameters, which is my arithmetic and not the README's, and each parameter gets about 1.75 bits, where an uncompressed weight uses 16. Going by the file size, the memory came down by storing each weight in fewer bits, and the [first thing the thread asked](https://news.ycombinator.com/item?id=50412500) was at which quantization, and what the output looks like.

My page on [LLM inference optimization](/articles/llm-inference-optimization/) has a second example from an NVIDIA tutorial. The model in that tutorial has 753B parameters and activates 40B per token, and its whole checkpoint still sits in GPU memory.

## How do MoE models keep every expert in use?

MoE models keep every expert in use by balancing the load during training, because an untrained router tends to send nearly all tokens to a few experts. DeepSeek's report calls the failure "routing collapse" and says the usual fix, an extra loss term that punishes uneven load, hurts model quality when it's set too high.

DeepSeek's fix is one bias number per expert, added to that expert's routing score. An expert that has been receiving too many tokens gets its bias lowered, and an expert that has been idle gets its bias raised.

The JAX project from the top of this page measured what the bias does on its 36.2M-parameter model. At step 2000 of training, expert load ran from 5.7% to 6.9% with the bias, where an even split is 6.25%, and from 0.09% to 18.6% without it.

Validation loss was 3.921 with the bias and 3.923 without it, so balancing the experts cost nothing in quality on that run. The result comes from one training run on 207 books, so I'd read it as a demonstration of how the bias works and not as proof that it works at DeepSeek's size.

## What does MoE save, in DeepSeek's own numbers?

DeepSeek-V2's paper compares the MoE model with the company's earlier dense 67B model. It reports 42.5% lower training cost, a KV cache 93.3% smaller and 5.76 times the maximum generation throughput.

I wouldn't credit all of those gains to mixture of experts. The same abstract assigns the KV cache saving to a change in the attention layers called Multi-head Latent Attention, so the throughput figure is the result of both changes together.

Mixture of experts is one of several ways to make each token cheaper. [Speculative decoding](/articles/speculative-decoding/) is another, and it keeps the model dense while a small, fast predictor drafts tokens for the large model to check.

## When does the architecture matter to you?

The architecture matters when you're the one paying for GPU memory. When you call an MoE model through an API, you pay per token and the provider holds the weights, so I'd evaluate the model the way I'd evaluate any other, by running it on my own task.

When you host the model yourself, you buy memory for the total parameter count, which is 671B for DeepSeek's model and not 37B. The compute saving then shows up as more tokens per second from those same GPUs.

## FAQ

**Is an MoE model with 37B active parameters the same as a 37B dense model?**

The two models do roughly the same amount of compute per token. They differ in how much they can store, because the MoE model picks a different set of experts for each token out of its full 671B parameters.

**Can I run DeepSeek-V3 locally?**

Only on a machine that can hold all 671B parameters. That's about 671 GB at 8 bits per weight before any cache, and a smaller footprint means quantizing further.

**What is routing collapse?**

Routing collapse is when the router sends nearly all tokens to a few experts and the rest go unused. DeepSeek counters it with a per-expert bias on the routing score.

**Do all layers in an MoE model use experts?**

No. Experts replace only the feed-forward part of a layer, and DeepSeek's report keeps an ordinary feed-forward network in the first few layers.

**Who came up with mixture of experts?**

The method dates to a 1991 paper by Jacobs and colleagues. The sparse version used in language models follows a 2017 paper by Shazeer and colleagues.
