---
title: "LLM token budgets: a practical guide to cost control"
date: 2026-04-17
description: "Real numbers, real pricing, and concrete strategies for keeping your LLM spend predictable."
tags: [ai, cost, backend, llm]
status: published
---

Token costs are the new EC2 bills. For the first few years of the LLM era, engineers treated inference spend as a black box. Input goes in, output comes out, invoice arrives at the end of the month. That approach works until it doesn't. A single weekend of heavy debugging with GPT-4 can run $200. A production RAG pipeline that gets 10,000 queries per day can hit $1,000 per month without anyone noticing until the bill lands.

This guide is about making token costs visible, predictable, and controllable. No fluff. Real numbers.

## What a token actually costs

Tokens are not bytes. English text averages about 4 characters per token. A sentence like "The pipeline failed at step three" is roughly 7 tokens. A typical email is 75-100 tokens. The model sees everything as tokens, and you pay per token.

Here is the current pricing landscape as of Q2 2026, rounded to three significant figures:

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| GPT-4.5 | $75 | $150 |
| GPT-4o | $2.50 | $10 |
| GPT-4o-mini | $0.15 | $0.60 |
| Claude 3.5 Sonnet | $3 | $15 |
| Claude 3.5 Haiku | $0.80 | $4 |
| Gemini 2.5 Flash | $0.15 | $0.60 |
| Gemini 2.5 Pro | $1.25 | $5 |

Numbers shift frequently. Always check the current API pricing pages before architecting around a specific rate.

A 1,000-token input with a 500-token output on GPT-4.5 costs $0.112. That sounds small until you multiply it by 50,000 requests per day. Then it is $5,600 per day, or $168,000 per month. Context compounds.

## Counting tokens before you spend them

The most basic cost control technique is knowing how many tokens a request will consume before you send it. Every major SDK provides a token counting utility.

```python
from anthropic import Anthropic

client = Anthropic()

# Count tokens without making a request
message = client.messages.count_tokens(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="You are a code reviewer.",
    messages=[
        {"role": "user", "content": "Explain the difference between a mutex and a semaphore."}
    ]
)

print(f"Token count: {message}")
```

OpenAI provides the same capability:

```python
import tiktoken

encoding = tiktoken.get_encoding("claude")
tokens = encoding.encode("Explain the difference between a mutex and a semaphore.")
print(f"Token count: {len(tokens)}")
```

The tiktoken library is fast and works without making an API call. Use it in your request pipeline to reject or queue requests that would exceed a budget threshold.

## Building a token budget system

Raw token counting is table stakes. A real budget system needs three components: a budget allocation per time window, a running tally, and a circuit breaker when limits are hit.

Here is a lightweight implementation:

```python
import time
from dataclasses import dataclass
from threading import Lock

@dataclass
class TokenBudget:
    max_tokens_per_minute: int
    window_seconds: int = 60

    def __post_init__(self):
        self.used_tokens = 0
        self.window_start = time.time()
        self.lock = Lock()

    def consume(self, token_count: int) -> bool:
        """Returns True if the tokens can be consumed, False if budget is exceeded."""
        with self.lock:
            now = time.time()
            if now - self.window_start >= self.window_seconds:
                self.used_tokens = 0
                self.window_start = now

            if self.used_tokens + token_count > self.max_tokens_per_minute:
                return False

            self.used_tokens += token_count
            return True

    def wait_time(self, token_count: int) -> float:
        """Seconds to wait until enough budget is available."""
        elapsed = time.time() - self.window_start
        return max(0, self.window_seconds - elapsed)
```

Apply it to your LLM calls:

```python
budget = TokenBudget(max_tokens_per_minute=500_000)

def llm_with_budget(prompt: str, model: str = "gpt-4o") -> str:
    estimated = estimate_tokens(prompt)

    if not budget.consume(estimated):
        wait = budget.wait_time(estimated)
        time.sleep(wait)

    response = call_model(model, prompt)
    return response
```

This keeps your spend rate bounded even if traffic spikes unexpectedly.

## Prompt compression: the high-leverage move

The single most effective cost reduction technique is sending fewer tokens. Every token you remove from the input is a token you do not pay for twice (input + output context).

Three compression strategies work well in practice.

**Truncation with semantic loss detection.** Rather than blindly truncating context at a token limit, identify and preserve the most relevant chunks. Use an embedding similarity search to rank chunks before inclusion.

```python
def compress_context(chunks: list[str], query: str, max_tokens: int) -> list[str]:
    from anthropic import Anthropic
    client = Anthropic()

    # Score each chunk against the query
    scored = []
    for chunk in chunks:
        similarity = compute_embedding_similarity(query, chunk)
        scored.append((similarity, chunk))

    scored.sort(reverse=True)

    selected = []
    total_tokens = 0
    for _, chunk in scored:
        chunk_tokens = count_tokens(chunk)
        if total_tokens + chunk_tokens > max_tokens:
            break
        selected.append(chunk)
        total_tokens += chunk_tokens

    return selected
```

**System prompt minimization.** System prompts accumulate. A typical engineering team starts with a 200-token system prompt. Six months later it is 1,500 tokens and nobody remembers why half of it exists. Audit system prompts quarterly. Remove every instruction that the model follows without being told.

**LLM distillation for routing.** Route simple queries to cheap models. Route complex ones to premium models. The routing itself can be done by an LLM:

```python
def route_query(query: str) -> str:
    routing_prompt = f"""
    Classify this query as 'simple' or 'complex'.
    Simple: factual recall, short answers, well-defined tasks.
    Complex: multi-step reasoning, ambiguous requirements, creative tasks.

    Query: {query}
    """

    response = call_model("gpt-4o-mini", routing_prompt)

    if "simple" in response.lower():
        return "gpt-4o-mini"
    return "gpt-4o"
```

The cost of the routing call is negligible. The savings from sending 80% of queries to the $0.15/$0.60 model instead of the $2.50/$10 model are not.

## Caching: when the math works

Token costs are incurred on every new request. If your application handles repetitive or similar queries, response caching can eliminate a large fraction of your bill.

OpenAI, Anthropic, and Google all support some form of cached inference. You pass a set of tokens as a cache object and the model processes them at a deep discount, typically 90% off input token pricing.

```python
# Anthropic caching example
cache_key = compute_cache_key(user_id, conversation_topic)

if cached_context := redis.get(cache_key):
    # Cache hit: use cached tokens at reduced cost
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        cache_control=[{"type": "hit", "value": cached_context}],
        messages=[{"role": "user", "content": current_message}]
    )
else:
    # Cache miss: build context, store for next time
    context_tokens = build_context(user_id, conversation_topic)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": context_tokens},
            {"role": "user", "content": current_message}
        ]
    )
    redis.setex(cache_key, 3600, extract_tokens(response))
```

Cache hit rates above 40% are common in customer support bots, internal tooling, and any application with a finite set of recurring question patterns.

## Output token control

Input costs dominate for most applications. Output costs matter when your pipeline generates long responses. Code generation, document synthesis, and agentic reasoning all produce large outputs.

Hard-limit output tokens. Set max_tokens conservatively. A question that can be answered in 50 tokens should never be allowed to generate 500 tokens at $0.15 per 1M.

```python
def bounded_completion(prompt: str, max_output: int = 150) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_output,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

The model will truncate if the answer requires more tokens. That is preferable to an unbounded bill.

## Monitoring in production

Cost control without monitoring is guesswork. Set up per-model, per-endpoint spend tracking.

```python
import logging
from datetime import datetime

class SpendTracker:
    def __init__(self):
        self.logger = logging.getLogger("llm_spend")
        self.daily_spend = {}
        self.model_prices = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        }

    def record(self, model: str, input_tokens: int, output_tokens: int):
        prices = self.model_prices.get(model, {"input": 0, "output": 0})
        cost = (input_tokens / 1_000_000 * prices["input"] +
                output_tokens / 1_000_000 * prices["output"])

        today = datetime.utcnow().date().isoformat()
        self.daily_spend[today] = self.daily_spend.get(today, 0) + cost

        self.logger.info(
            f"model={model} input_tokens={input_tokens} "
            f"output_tokens={output_tokens} cost=${cost:.4f} "
            f"daily_total=${self.daily_spend[today]:.2f}"
        )
```

Route the logs to your metrics system. Alert when daily spend exceeds a threshold. Set weekly budget caps that trigger circuit breakers rather than surprise invoices.

## The multiplier problem

Most cost control advice focuses on individual request optimization. The harder problem is scale.

A pipeline that costs $0.001 per request seems cheap. Run it 5 million times per month and it is $5,000. Add a second pipeline at $0.002 per request and you are at $15,000. Three pipelines, 20 million requests, different models across teams, and nobody has the full picture.

The fix is centralized spend governance. Every LLM call in every service should route through a thin proxy that records token counts and cost. Aggregate by team, by product, by endpoint. Without this visibility, you are managing a budget by looking at your bank balance once a quarter.

Build the proxy. Instrument every call. Tag every request with a cost center. This is not glamorous work. It is the work that separates teams that get surprised by their invoice from teams that set budgets and hit them.

## Where to cut first

If you are starting from a position of no cost control, here is the priority order:

1. Enable token counting on every request. You cannot manage what you cannot measure.
2. Route simple queries to cheap models. A 60% routing ratio to GPT-4o-mini instead of GPT-4o saves 94% on input token costs.
3. Audit system prompts. Halve them first. Measure the difference.
4. Enable caching. Target 30%+ cache hit rate on high-volume endpoints.
5. Set hard output token limits. This alone can cut output costs by 20-40%.
6. Build a spend dashboard. Alert on anomalies before they compound.

The goal is not to use fewer models. It is to use the right model for each task at the right price. That requires visibility, discipline, and the willingness to measure what you spend.

Token budgets are not optional. They are the cost accounting layer that makes LLM applications sustainable.
