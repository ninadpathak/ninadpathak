---
title: "LLM token budgets: a practical guide to cost control"
date: 2026-04-17
description: "Real numbers, real pricing, and concrete strategies for keeping your LLM spend predictable."
tags: [ai, cost, backend, llm]
status: published
---

Token costs are the new EC2 bills. I learned that the expensive way after burning $200 on GPT-4 over a single weekend, chasing a bug with a loop that re-sent the whole conversation on every retry. A production RAG pipeline serving 10,000 queries per day can quietly climb to $1,000 per month, and nobody notices until the invoice lands. For the first few years of the LLM era, most engineers I worked with treated inference spend as a black box. Input goes in, output comes out, invoice arrives at month end. That approach holds right up until traffic doubles or someone ships a chattier prompt.

What follows is how I make token costs visible, predictable, and controllable. No fluff. Real numbers.

## What a token actually costs

Tokens are not bytes. English text averages about 4 characters per token. A sentence like "The pipeline failed at step three" is roughly 7 tokens. A typical email runs 75 to 100 tokens. The model sees everything as tokens, and you pay per token, every time the model reads or writes one.

As of Q2 2026, here is the current pricing landscape, rounded to three significant figures. Numbers shift frequently, sometimes mid-quarter, so I check the API pricing pages before architecting around a specific rate. Always.

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| GPT-5.4 Standard | $2.50 | $15 |
| GPT-5.4 Mini | $0.75 | $4.50 |
| GPT-5.4 Nano | $0.20 | $1.25 |
| GPT-5.4 Pro | $30 | $180 |
| GPT-5.2 | $1.75 | $14 |
| GPT-5.1 | $1.25 | $10 |
| Claude Opus 4.7 | $5 | $25 |
| Claude Sonnet 4.6 | $3 | $15 |
| Claude Haiku 4.5 | $1 | $5 |
| Gemini 3.1 Pro (<=200K ctx) | $2 | $12 |
| Gemini 3.1 Pro (>200K ctx) | $4 | $18 |

A 1,000-token input with a 500-token output on GPT-5.4 Nano costs $0.00026. That sounds like a rounding error until you multiply it by 50,000 requests per day, which lands at $13 per day, or $390 per month. Context compounds too, and [bigger context windows are not always better for cost or accuracy](/blog/llm-context-windows-explained/). A chatbot that grows its system prompt and replays the full history on every turn pays for those same tokens again on each message, so a 20-message conversation can cost twenty times what the first reply did.

<div class="visual-wrapper">
  <div class="visual-title">TOKEN BUDGET</div>
  <div class="visual-container">
    <iframe src="/static/visuals/token-budget.html" title="A single request budget split into system prompt, history, retrieved context, and output, with a per-request cost readout" loading="lazy"></iframe>
  </div>
</div>

## Counting tokens before you spend them

Counting how many tokens a request will consume before you send it is [the most basic cost control technique there is](/blog/token-counting-isnt-optional-a-practical-guide-to-llm-cost-control/). Every major SDK ships a token counting utility for exactly this.

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

Fast and entirely offline, the tiktoken library needs no API call to do its job. I wire it into request pipelines to reject or queue anything that would blow past a budget threshold, like a user pasting a 40-page PDF into a chat box and expecting a free summary. Wiring it in takes about five minutes and spares you the end-of-month surprise.

## Building a token budget system

Raw token counting is table stakes. A real budget system needs three components working together: a budget allocation per time window, a running tally, and a circuit breaker that trips when limits are hit. Think of it like the fuel gauge, odometer, and engine cutoff on a rental scooter, where the cutoff is what stops you from running the tank dry without realizing it.

Here is a lightweight implementation I have run in production:

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

def llm_with_budget(prompt: str, model: str = "gpt-5.4") -> str:
    estimated = estimate_tokens(prompt)

    if not budget.consume(estimated):
        wait = budget.wait_time(estimated)
        time.sleep(wait)

    response = call_model(model, prompt)
    return response
```

Spend rate stays bounded even when traffic spikes without warning, say a launch post hitting the front page of a forum and sending 10x the usual load at your endpoint. I have watched a budget cap like this keep a $2,000 weekend bill from ballooning into a $12,000 one.

## Prompt compression: the high-impact move

Sending fewer tokens is the single most effective cost reduction technique I know. Every token you strip from the input is a token you never pay for, and in a multi-turn chat you avoid paying for it on every subsequent turn too.

Three compression strategies earn their keep in practice.

**Truncation with semantic loss detection.** Rather than chopping context at a token limit and hoping the useful part survived, identify and keep the most relevant chunks. An embedding similarity search ranks chunks before inclusion, so a question about refund policy pulls the refund docs instead of whichever paragraph happened to come first.

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

**System prompt minimization.** System prompts accumulate like commented-out code nobody dares delete. A team I worked with started with a 200-token system prompt, and six months later it had grown to 1,500 tokens, half of it instructions like "be helpful" that the model already does and nobody could explain. Auditing system prompts quarterly catches this. I cut every instruction the model follows without being told, then re-test to confirm nothing regressed.

**LLM distillation for routing.** Send simple queries to cheap models and complex ones to premium models, and let an LLM make the call:

```python
def route_query(query: str) -> str:
    routing_prompt = f"""
    Classify this query as 'simple' or 'complex'.
    Simple: factual recall, short answers, well-defined tasks.
    Complex: multi-step reasoning, ambiguous requirements, creative tasks.

    Query: {query}
    """

    response = call_model("gpt-5.4-nano", routing_prompt)

    if "simple" in response.lower():
        return "gpt-5.4-nano"
    return "gpt-5.4"
```

The routing call itself costs almost nothing. Sending 80% of queries to the $0.20/$1.25 model instead of the $2.50/$15 one, though, is where the bill actually drops.

## Caching: when it pays off

Token costs land on every new request. For applications fielding repetitive or near-identical queries, response caching can wipe out a large fraction of the bill.

OpenAI, Anthropic, and Google all support some form of cached inference. You pass a set of tokens as a cache object, and the model processes them at a deep discount, typically 90% off input token pricing. The savings only materialize once the same prefix gets reused enough times to cover the small premium charged to write the cache, so I dig into [when prompt caching actually pays off](/blog/prompt-caching-what-it-is-and-when-the-math-works/) separately.

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

Hit rates above 40% are common in customer support bots, internal tooling, and any application with a finite set of recurring question patterns. On an internal dev-docs assistant where engineers kept asking the same "how do I deploy" and "where do logs go" questions, I have seen hit rates reach 60%.

## Output token control

Input costs dominate for most applications, yet output costs take over the moment your pipeline starts generating long responses. Code generation, document synthesis, and agentic reasoning loops all spill out large outputs.

Hard-limit output tokens and set max_tokens conservatively. A question answerable in 50 tokens should never be free to ramble for 500 at $0.15 per 1M. I learned this after a single debug session ran up $180 in output costs because nobody had set a max_tokens limit and the model kept "thinking out loud" on every retry.

```python
def bounded_completion(prompt: str, max_output: int = 150) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_output,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

A longer answer gets truncated when it overruns the limit, which beats an unbounded bill every time.

## Monitoring in production

Cost control without monitoring is guesswork. Set up per-model, per-endpoint spend tracking so you can see which service is the one quietly draining the budget.

```python
import logging
from datetime import datetime

class SpendTracker:
    def __init__(self):
        self.logger = logging.getLogger("llm_spend")
        self.daily_spend = {}
        self.model_prices = {
            "gpt-5.4": {"input": 2.50, "output": 15.00},
            "gpt-5.4-mini": {"input": 0.75, "output": 4.50},
            "claude-opus-4.7": {"input": 5.00, "output": 25.00},
            "claude-sonnet-4.6": {"input": 3.00, "output": 15.00},
            "gemini-3.1-pro": {"input": 2.00, "output": 12.00},
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

Route the logs to your metrics system, alert when daily spend crosses a threshold, and set weekly budget caps that trip circuit breakers instead of mailing you a surprise invoice.

## The multiplier problem

Most cost control advice fixates on optimizing a single request. Scale is the problem that actually hurts.

Run a pipeline that costs $0.001 per request 5 million times a month and you are at $5,000. A second pipeline at $0.002 per request pushes you to $15,000. Stack three pipelines, 20 million requests, and a different model behind each team, and suddenly nobody owns the full picture.

Centralized spend governance is the fix. Every LLM call in every service should route through a thin proxy that records token counts and cost, aggregated by team, by product, by endpoint. Skip that visibility and you are managing a budget the way you would manage groceries by glancing at your bank balance once a quarter.

Build the proxy, instrument every call, and tag every request with a cost center. None of it is glamorous. It is the work that separates teams blindsided by their invoice from teams that set budgets and hit them. I have yet to watch a team regret building it too early.

## Where to cut first

Starting from zero cost control, here is the priority order I would follow:

1. Enable token counting on every request. You cannot manage what you cannot measure.
2. Route simple queries to cheap models. A 60% routing ratio to GPT-5.4 Nano instead of GPT-5.4 saves 92% on input token costs.
3. Audit system prompts. Halve them first, then measure the difference.
4. Enable caching. Target 30%+ cache hit rate on high-volume endpoints.
5. Set hard output token limits. That single change can cut output costs by 20-40%.
6. Build a spend dashboard. Alert on anomalies before they compound.

The goal is not to use fewer models. It is to use the right model for each task at the right price, which takes visibility, discipline, and the willingness to measure what you spend.

Token budgets are not optional. They are the cost accounting layer that makes LLM applications sustainable.
