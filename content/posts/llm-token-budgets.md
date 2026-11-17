---
category: ai-engineering
primary_query: llm cost optimization
date: 2026-04-17
description: 'LLM token budgets from real figures: what a token costs, why input dominates a bill, why a chat costs more each turn, and where to cut first.'
status: published
work_note: 'I wrote this to make a token bill something you can predict before the invoice arrives. [My portfolio](/portfolio/) has the developer content I''ve published for AI companies.'
title: 'LLM token budgets: a practical guide to cost control'
slug: llm-token-budgets
updated: 2026-11-17
---

AWS's billing alarm is the cost control developers already know, and its [documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html) is exact about when it fires. The alarm "triggers only when the current billing exceeds the threshold" and "doesn't use projections based on your usage so far in the month."

An LLM token budget is the same control moved earlier: a limit on what one request or one period is allowed to spend, set before the spending happens. The alarm reports money that is already gone, and a token budget can refuse the request, because tokens can be counted before anything is sent.

Where such a budget has to look first shows in numbers two Amazon engineers [published on November 9](https://strandsagents.com/blog/amazon-saves-millions-replacing-sonnet-with-strands-decider/). Their ticket-labeling agent used 6,554 input tokens and 170 output tokens for each ticket on Claude Sonnet 4.6, which by my arithmetic put 89% of its model bill on input, the prompt that gets sent again on every call.

## What does a token cost?

A token costs whatever the model's price list says for its direction, and output is priced several times higher than input. Anthropic's [pricing page](https://platform.claude.com/docs/en/about-claude/pricing), read on November 17, 2026, lists these rates for Claude Sonnet 5.5 in USD per million tokens.

| Token type | Price per million tokens, USD |
| --- | --- |
| Input | 2.00 |
| Output | 10.00 |
| Cache write, five minutes | 2.50 |
| Cache read | 0.10 |

The count behind the price moves too. That page says of newer models that their tokenizer "produces approximately 30% more tokens for the same text", so a prompt measured on an old model is a low estimate on a new one.

## Where does the money go in one call?

For a call with a long standing prompt and a short answer, nearly all of it goes to input. Amazon's post describes the workload: "The agent ran with a long system prompt on every ticket, generating JSON and reasoning against a fixed set of labels."

The script below reproduces their cost per ticket from the token counts, then prices a second workload, a 20-turn chat.

```python
"""Two token budgets: one ticket-labeling call, and a 20-turn chat that replays its history."""

# 1. Amazon's published figures for labeling one ticket with Claude Sonnet 4.6.
IN_PRICE, OUT_PRICE = 3.00, 15.00            # USD per million tokens
in_tokens, out_tokens = 6_554, 170
in_cost = in_tokens * IN_PRICE / 1e6
out_cost = out_tokens * OUT_PRICE / 1e6
print(f"ticket: ${in_cost + out_cost:.4f} per call, {in_cost / (in_cost + out_cost):.0%} of it input")
print(f"        ${(in_cost + out_cost) * 1e6:,.0f} per million tickets")

# 2. A chat on Claude Sonnet 5.5 list prices: 2.00 in, 10.00 out, cache write 1.25x, cache read 0.05x.
IN, OUT, WRITE, READ = 2.00, 10.00, 2.50, 0.10
system, user, reply, turns = 1_500, 150, 250, 20

plain = cached = 0.0
history = 0
first = last = 0.0
for turn in range(1, turns + 1):
    prompt = system + history + user                      # everything sent this turn
    new = user if turn > 1 else system + user             # tokens the cache has not seen
    new += reply if turn > 1 else 0                       # last turn's reply is new to the cache too
    cost = prompt * IN / 1e6 + reply * OUT / 1e6
    plain += cost
    cached += (prompt - new) * READ / 1e6 + new * WRITE / 1e6 + reply * OUT / 1e6
    first = cost if turn == 1 else first
    last = cost
    history += user + reply

print(f"chat:   turn 1 sends {system + user:,} input tokens, turn {turns} sends {system + history - reply:,}")
print(f"        turn {turns} costs {last / first:.1f}x turn 1 without caching")
print(f"        20 turns: ${plain:.4f} without caching, ${cached:.4f} with it ({1 - cached / plain:.0%} less)")
```

```text
ticket: $0.0222 per call, 89% of it input
        $22,212 per million tickets
chat:   turn 1 sends 1,650 input tokens, turn 20 sends 9,250
        turn 20 costs 3.6x turn 1 without caching
        20 turns: $0.2680 without caching, $0.0831 with it (69% less)
```

The ticket cost in that output agrees with the post's own per-ticket figure. The post is published by the team that sells the replacement, a small decision model, and its headline is that the swap "performed just as well at 98% less cost".

I'm using only the Sonnet side of their table. The lesson in it holds whatever replaces the model: the replacement prompt was 2,009 tokens and the output was one token, so the saving came from sending and asking for less.

## Why does a chat cost more with every turn?

Each turn resends the system prompt and the whole conversation so far, so the input grows while the question stays the same size. The twentieth turn in the run above sends 9,250 input tokens against 1,650 for the first, and costs 3.6 times as much.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/llm-token-budgets/token-budget.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/llm-token-budgets/token-budget.narrow.svg" width="288" height="248"><img class="np-has-narrow" src="/static/images/diagrams/llm-token-budgets/token-budget.svg" width="720" height="280" alt="Six turns of a chat, each drawn as one request: the system prompt, the replayed history of every earlier turn, the new message, and the answer. Because history is replayed on every turn, each request is longer than the last." loading="lazy" decoding="async"></picture></a>
  <figcaption>A bot that replays its full history pays for the same tokens again on every message, so each turn costs more than the one before.</figcaption>
</figure>

Prompt caching is the direct answer, because the resent part is identical from one turn to the next. The same conversation cost 69% less in the run with the unchanged prefix read from cache, and Anthropic's page says "Caching saves money after a small number of cache reads".

The other answer is to stop resending everything. Compaction replaces old turns with a summary, as [short-term memory for agents](/articles/short-term-agent-memory/) describes, and the [context window guide](/articles/llm-context-windows/) covers how models use a long window.

## What should a token budget enforce?

A budget should enforce a hard stop, per request and per month. Simon Willison [argued on October 3](https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/) for the monthly kind as a default on every paid API: "after $X/month, cut this thing off and return errors".

His reason is the failure a warning can't prevent. "Soft caps, "after $X/month, send me a warning email", will not cut it."

A per-request budget is the same idea at a smaller scale. Cap the output with the API's maximum-tokens parameter, and reject a prompt over a set size before it is sent.

## Where should you cut first?

Cut in the order the run suggests, starting with what is sent on every call.

1. Shorten the standing prompt, since it is paid for on every request.
2. Cache the part of the prompt that doesn't change between requests.
3. Cap the output length, because output tokens carry the higher price.
4. Move work that can wait to a batch endpoint, which Anthropic prices "with a 50 percent discount on both input and output tokens".
5. Try a smaller model where the task is a fixed choice.

A smaller model is Amazon's result, and their own caveat belongs with it: "This worked because the task is a closed choice from a known catalog, the volume is high, and the latency of the old path mattered."
