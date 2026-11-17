---
category: ai-engineering
primary_query: kv cache
siblings:
- llm-inference-optimization
- time-to-first-token
- llm-context-windows
date: 2026-04-15
description: The KV cache stores each token's keys and values so a model doesn't recompute
  them. How to size it from a model config, what eviction policies keep when it fills,
  and why Cloudflare's September incident makes it a security boundary.
status: published
work_note: "I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. I write developer documentation, tutorials and technical articles, and I run the product before I write about it. [See how I work](/services/freelance-technical-writer-for-ai-companies/) and tell me what you're shipping."
title: 'What the KV Cache Is and What Happens When It Fills Up'
updated: '2026-08-17'
slug: kv-cache-eviction
---

On October 26 Cloudflare published [a report](https://blog.cloudflare.com/kv-cache-exposure-remediation/) on a bug in which 155 responses from a model on Workers AI contained text from other customers' requests. The leaked text came from the KV cache, a block of GPU memory that the model reads while it generates.

The KV cache is the memory where a language model keeps the key and value vectors it has computed for every token so far. The cache exists so that generating the next token doesn't require recomputing every earlier token, and the cache grows by a fixed amount with each token in the context.

Cloudflare calls the bug a memory-safety bug, and it reminded me of [Heartbleed](https://en.wikipedia.org/wiki/Heartbleed), the OpenSSL bug disclosed in April 2014. A server with the Heartbleed bug read past the end of a buffer and sent back whatever was in memory there, and in Cloudflare's bug a model read cache pages that still held another customer's prompt.

So this page treats the KV cache the way you'd treat any block of memory: how many bytes it takes, what gets removed when it's full, and which request is allowed to read it. The page belongs with the other model-serving topics under [AI engineering](/articles/ai-engineering/).

## What is the KV cache?

The KV cache is a per-sequence store of the keys and values that each attention layer computed for earlier tokens. When the model generates token 1,001, it computes keys and values for that one token and reads the other 1,000 from the cache.

The price of skipping that recomputation is memory, and the memory grows with the length of the conversation. The [H2O paper](https://arxiv.org/abs/2306.14048) describes the cache as state held in GPU memory besides the model's weights, "scaling linearly with the sequence length and batch size".

Linear growth means a conversation twice as long needs twice the cache. A provider that offers a larger [context window](/articles/llm-context-windows/) therefore has to set aside more GPU memory per conversation, on top of charging for the tokens.

## How big is the KV cache?

The KV cache holds two vectors per token, a key and a value, for every KV head in every layer, so you can calculate its size from a model's config file. The script below does it for [Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/main/config.json), using the numbers in its published config:

```python
"""Size the KV cache of a model from its config. Numbers are for Qwen2.5-7B-Instruct."""
config = {"num_hidden_layers": 28, "num_attention_heads": 28, "num_key_value_heads": 4, "hidden_size": 3584}
BYTES_PER_VALUE = 2          # bfloat16, the dtype in the same config
head_dim = config["hidden_size"] // config["num_attention_heads"]


def kv_bytes(tokens, kv_heads):
    # one key vector and one value vector per token, per KV head, per layer
    return 2 * config["num_hidden_layers"] * kv_heads * head_dim * BYTES_PER_VALUE * tokens


per_token = kv_bytes(1, config["num_key_value_heads"])
print(f"head dimension: {head_dim}")
print(f"KV cache per token: {per_token:,} bytes")
for tokens in (4_096, 32_768, 131_072):
    grouped = kv_bytes(tokens, config["num_key_value_heads"]) / 2**30
    ungrouped = kv_bytes(tokens, config["num_attention_heads"]) / 2**30
    print(f"{tokens:>7,} tokens: {grouped:5.2f} GiB per sequence ({ungrouped:5.2f} GiB if every head kept its own keys and values)")
```

Running `python kv_size.py` printed:

```text
head dimension: 128
KV cache per token: 57,344 bytes
  4,096 tokens:  0.22 GiB per sequence ( 1.53 GiB if every head kept its own keys and values)
 32,768 tokens:  1.75 GiB per sequence (12.25 GiB if every head kept its own keys and values)
131,072 tokens:  7.00 GiB per sequence (49.00 GiB if every head kept its own keys and values)
```

A single conversation that fills the 131,072-token context needs 7 GiB of cache, in addition to the memory for the model's weights. A server running eight conversations of that length at once needs 56 GiB of cache.

The figure in brackets is what the same model would need if each of its 28 attention heads stored its own keys and values. The config sets `num_key_value_heads` to 4, so each group of 7 attention heads shares one set of keys and values, and the cache is a seventh of the size it would otherwise be.

The script counts only the key and value tensors. A serving engine such as vLLM adds its own bookkeeping on top, so I'd treat 7 GiB as the minimum for that conversation and not as the exact figure.

## What happens when the KV cache fills up?

When the KV cache is full, the model has to drop the keys and values of some tokens before it can add new ones. The research on [KV cache eviction](/glossary/kv-cache-eviction/) is about which tokens to drop, and each policy protects a different set of tokens:

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/kv-cache-eviction/eviction-policies.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/kv-cache-eviction/eviction-policies.narrow.svg" width="288" height="1000"><img class="np-has-narrow" src="/static/images/diagrams/kv-cache-eviction/eviction-policies.svg" width="720" height="544" alt="When the KV cache fills, StreamingLLM keeps the attention sinks, the first few tokens, plus the latest tokens, and evicts everything in between. H2O keeps the heavy hitters, the tokens with the highest accumulated attention, wherever they sit, and evicts the low scorers." loading="lazy" decoding="async"></picture></a>
  <figcaption>StreamingLLM keeps the first tokens and the recent ones and forgets the middle. H2O keeps the tokens with the highest attention scores.</figcaption>
</figure>

Dropping the oldest tokens is the obvious policy, and the [StreamingLLM paper](https://arxiv.org/abs/2309.17453) shows it fails once the text is longer than the cache. Its authors traced the failure to the first few tokens, which collect strong attention "even if they are not semantically important", and they named those tokens attention sinks.

StreamingLLM's policy keeps the attention sinks and the recent tokens and drops the rest. The paper reports stable language modeling at up to 4 million tokens with that policy, and the model can no longer attend to anything from the middle of the text.

H2O keeps the tokens that have received the highest attention scores so far, wherever they sit in the text. The policy rests on the observation that a small share of tokens accounts for the bulk of the attention score, and its eviction policy retains a balance of those heavy hitters and recent tokens.

[SnapKV](https://arxiv.org/abs/2404.14469) chooses which tokens to keep once, before generation starts. SnapKV looks at which earlier positions the last part of the prompt attends to and keeps those positions, and its authors report an 8.2x gain in memory efficiency on 16K-token inputs with comparable accuracy on 16 long-sequence datasets.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/kv-cache-eviction/attention-map.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/kv-cache-eviction/attention-map.narrow.svg" width="288" height="424"><img class="np-has-narrow" src="/static/images/diagrams/kv-cache-eviction/attention-map.svg" width="720" height="424" alt="An illustrative causal attention map, not measured data. Each row is a query and each column a key. The first column is the attention sink, the band along the diagonal is the immediate local context, and a few columns run the full height as heavy hitters that later tokens keep attending to." loading="lazy" decoding="async"></picture></a>
  <figcaption>An illustration of the pattern, not observed attention data. Drop a heavy hitter and generation can destabilize.</figcaption>
</figure>

Each of those results was measured by the paper's own authors on their own models and tasks, so I wouldn't compare 4 million tokens with 8.2x. An evicted token can't be attended to for the rest of the generation, so the test I'd run is whether my own task needs a token the policy dropped.

## Do serving engines evict tokens for you?

I found no H2O-style or SnapKV-style eviction setting in vLLM's docs. What vLLM documents is reuse of the cache: its [automatic prefix caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/) lets a new request skip computing a prefix it shares with an earlier one by reusing that prefix's KV cache.

Prefix caching is the KV cache saving you work across requests. A long system prompt is computed once and its keys and values serve every request that starts with it, which is how prefix caching shortens [time to first token](/articles/time-to-first-token/).

A voice agent is where [that saving is heard](/articles/voice-agent-latency/), because the caller is waiting in silence for the first word.

So the KV cache decisions you make when serving a model are about size and sharing, not about eviction papers. You decide how many tokens the cache pool holds and which requests may reuse another request's cached prefix, and the page on [LLM inference optimization](/articles/llm-inference-optimization/) covers both settings.

## Why is the KV cache a security boundary?

The KV cache is a security boundary because it holds other customers' prompts in a form the model can read directly. Cloudflare's incident report shows what happens when that boundary fails, and the failure started with a cache pool that was too small.

The model was deployed with a 1,048,576-token context window, and the cache pool on the prefill GPUs had room for 681,280 tokens.

The inference engine, SGLang, marked a prompt longer than 681,280 tokens as rejected. A bug in SGLang then let generation go ahead anyway, and the model attended over cache pages that still held earlier customers' requests.

Cloudflare's report classifies the failure in one line: "This bug belongs to a class of KV cache memory-safety bugs". The two fixes match that description, because Cloudflare made the pool about twice the size of the context window and patched SGLang so that a rejected prompt returns an error to the client.

The lesson I take from the report is to size the cache pool for the context window you advertise. Cloudflare advertised 1,048,576 tokens and provisioned 681,280, and every prompt between those two numbers depended on an error path that Cloudflare had assumed worked.

## FAQ

**What does KV stand for in KV cache?**

KV stands for key and value. A key and a value are the two vectors each attention layer computes per token, and later tokens read them instead of recomputing them.

**Is the KV cache the same as prompt caching?**

Prompt caching is built on the KV cache. A provider that caches a prompt prefix is keeping that prefix's keys and values so the next request can reuse them.

**Does the KV cache grow with batch size?**

Yes. Each sequence in a batch has its own cache, so memory grows with both the length of each sequence and the number of them.

**What is an attention sink?**

An attention sink is one of the first few tokens of a sequence, which attract strong attention regardless of what the tokens say. StreamingLLM found that keeping them is what stops a sliding window from failing.

**Can evicting tokens from the KV cache change the answer?**

Yes. An evicted token can't be attended to again, so anything the answer needed from it is lost.
