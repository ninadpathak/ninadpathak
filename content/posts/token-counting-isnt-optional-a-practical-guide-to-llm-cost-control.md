---
date: 2026-03-22
description: I explain the mechanics of LLM tokenization, why JSON burns your API
  budget, and how to architect systems for strict token efficiency.
status: published
tags:
- llm
- infrastructure
- ai
title: 'Token Counting Isn''t Optional: a Practical Guide to Llm Cost Control'
---

Engineering teams keep treating LLM calls like traditional REST requests, where a `GET /users/42` costs the same whether the row is small or huge. LLM pricing works nothing like that. Every character you send and every character the model writes back moves the meter, so a chatty system prompt or a bloated retrieval payload quietly multiplies your bill on every single request. The first time I saw this bite, a teammate had appended the full conversation history to each turn of a support bot, and a fifty-message thread was paying to reprocess message one fifty separate times. Scaling an AI product without strict token budgeting is how you end up explaining a five-figure invoice to a finance team. I will walk through the mechanics of tokenization and show you how to architect systems that keep costs predictable.

## The Mechanics of Tokenization

Words do not map one-to-one with tokens. Large Language Models process text using algorithms like Byte Pair Encoding, which scans training data to find the most frequent character combinations and groups them into unique integers. A common word like "the" becomes one token, while something like "tokenization" might split into "token" and "ization". I have watched developers assume a thousand-word document equals exactly one thousand tokens, when the real count for standard English sits closer to thirteen hundred. Feed it minified code, stack traces, or a non-English language with its own script, and that ratio gets much worse because the model has fewer frequent patterns to lean on.

Whitespace counts too, which surprises people. On one production system I debugged, trailing spaces and the deeply nested tab indentation in a pile of exported HTML were eating roughly twenty percent of the prompt budget before a single real word arrived. The model reads each of those spaces as a discrete token that still has to pass through the attention mechanism, the same as any other token. Strip and normalize formatting from your data before it ever reaches a foundation model. A five-line `re.sub` to collapse runs of whitespace cut that document set down to size in an afternoon.

<div class="visual-wrapper">
  <div class="visual-title">Byte Pair Encoding Breakdown</div>
  <div class="visual-container">
    <iframe src="/static/visuals/token-byte-pair.html" title="Token Byte Pair Animation" loading="lazy"></iframe>
  </div>
</div>

## Input Costs Versus Output Costs

Generating tokens is computationally heavier than reading them. During the initial prefill phase the model reads your entire prompt in parallel, the way you can scan a whole page at a glance. Writing the response works more like dictation. The model computes probabilities for the first word, outputs it, appends it to the context, and recalculates everything to predict the second word, then the third, one at a time.

Providers charge up to five times more per output token than per input token because of this autoregressive bottleneck. My default is to optimize architectures for minimal output. Instruct the model to return only the requested fields and skip the conversational filler. Asking for a bare JSON object instead of one wrapped in "Sure, here is the data you asked for, formatted as requested:" can shave real money off a high-volume endpoint. On an extraction endpoint doing millions of calls a day, that one preamble sentence is twenty-odd tokens you pay for every time and parse out every time.

That asymmetry should also change how you design the task itself. A sentiment classifier that returns a single `positive` token is enormously cheaper than one that writes a paragraph explaining its choice, even though both read the same review. When I need the reasoning for debugging, I gate it behind a flag and turn it off in production once the prompt is stable. You can explore techniques like [Speculative Decoding](/blog/speculative-decoding-explained/) to see how inference engines try to speed up this sequential generation.

## The JSON Padding Trap

Reaching for JSON to structure data is a reflex for most of us, since that is what our APIs already speak. As context inside an LLM prompt, though, JSON carries a lot of dead weight. Every curly brace, every quotation mark, and every repeated key name like `"customer_id"` printed across two hundred records consumes tokens that teach the model nothing. Picture two hundred order rows where the strings `"customer_id"`, `"order_total"`, and `"status"` get re-typed on every line: the model has already learned the schema from the first row, yet you keep paying to spell it out. YAML drops the brackets and quotes in favor of plain indentation and a single key per line.

Parsing a batch of database records into YAML before sending them, I measured a forty percent cut in input tokens against the JSON version of the same data. The model reads the hierarchy from indentation just fine without the strict syntax. Reserve JSON for the final output, where you actually need deterministic parsing back into your application layer.

<div class="visual-wrapper">
  <div class="visual-title">Syntax Token Bloat: JSON vs YAML</div>
  <div class="visual-container">
    <iframe src="/static/visuals/json-vs-yaml-tokens.html" title="JSON vs YAML Token Weight Animation" loading="lazy"></iframe>
  </div>
</div>

## Semantic Caching

Paying the frontier model twice to answer the same question is a design failure, not a cost of doing business. My approach is to intercept user queries before they ever reach the expensive model. A fast local embedding model turns the incoming natural language query into a vector, which you then compare against a database of queries you have already answered.

Once the similarity score crosses a high-confidence threshold, you return the cached answer directly and the request never touches the LLM, so its marginal cost falls to zero. Think of it as the read-through cache sitting in front of a slow database, except the key is the meaning of the sentence rather than its exact bytes, so two differently worded questions hash to the same entry. Customer support chatbots are where I lean on this constantly, because "how do I reset my password" and "I forgot my login, what now" land on the same cached answer despite sharing almost no words.

<div class="visual-wrapper">
  <div class="visual-title">Semantic Cache Query Routing</div>
  <div class="visual-container">
    <iframe src="/static/visuals/semantic-cache-routing.html" title="Semantic Cache Routing Animation" loading="lazy"></iframe>
  </div>
</div>

## Architectural Routing and Small Models

Sending every user query to a massive seventy-billion parameter model burns cash you did not need to spend. I build a routing layer that classifies prompt complexity at the edge and picks the cheapest model that can do the job. A request to summarize a paragraph or tag a ticket as billing-related goes to an eight-billion parameter model, while a request to debug a race condition or reason through a multi-step plan gets forwarded to the frontier model.

Handling the routing decision itself costs a fraction of a cent when a fast embedding classifier or a very cheap language model makes the call. That preserves your budget for the tasks that genuinely need advanced reasoning. Average latency drops as a bonus, since the small models that field most of the traffic respond much faster than the large one.

Get the routing wrong in the cheap direction and the failure is loud and recoverable: the small model produces a weak answer, you detect it, and you escalate to the frontier model on retry. Send everything to the big model to play it safe and the failure is silent, showing up only as a bill nobody can explain at the end of the month. I would rather build the escalation path and tune the classifier than pay the premium on every request out of caution.

## Managing the Expanding Context Window

Foundation models now advertise context windows that hold millions of tokens, and developers treat that ceiling as an invitation. Stuffing an entire repository or a folder of PDFs into the prompt feels free because the API accepts it. One sloppy retrieval pipeline I reviewed was returning fifty chunks per query when three were relevant, and the cloud bill had climbed by thousands of dollars over a single weekend before anyone noticed.

Strict filtering before the prompt gets assembled is what fixes this. Score the relevance of every chunk and drop the ones that do not earn their place. A cross-encoder reranker does this well, scoring each retrieved chunk against the query directly, a technique I cover in my post on [Reranking in RAG](/blog/reranking-in-rag-why-your-top-k-results-are-probably-wrong/). Capping that pipeline at the top three reranked chunks took the bill on the system above back to sane numbers without measurably hurting answer quality. Look into [Prompt Caching](/blog/prompt-caching-what-it-is-and-when-the-math-works/) as well, so you can offset the cost when you genuinely have to resend a large system instruction on every call.

## Strict Budgeting

Token counting is a core engineering discipline for any serious AI application. I treat token limits with the same rigor I give database query plans or memory allocation. Measure the token weight of your prompt templates in continuous integration, so a careless edit that doubles a system prompt fails the build instead of surfacing on the invoice. A failing assertion that the system prompt stays under, say, eight hundred tokens has caught more than one well-meaning refactor for me. Monitor the output length of your responses in production with the same attention you give p99 latency. Whether your application survives contact with real traffic comes down to how well you control these dynamic costs.