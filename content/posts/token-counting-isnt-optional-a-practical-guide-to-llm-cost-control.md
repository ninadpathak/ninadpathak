---
title: "Token Counting Isn't Optional: A Practical Guide to LLM Cost Control"
description: "I explain the mechanics of LLM tokenization, why JSON burns your API budget, and how to architect systems for strict token efficiency."
date: 2026-03-22
tags: [llm, infrastructure, ai]
status: published
---

I often see engineering teams treat LLM calls like traditional REST API requests. Traditional APIs have fixed costs per request regardless of the payload size. LLM API costs are entirely dynamic and scale directly with every character you send and receive. You cannot scale an AI product without strict token budgeting. I will explain the mechanics of tokenization and show you how to architect systems that keep costs predictable.

## The Mechanics of Tokenization

Words do not map one-to-one with tokens. Large Language Models process text using algorithms like Byte Pair Encoding. The algorithm scans the training data to find the most frequent character combinations and groups them into unique integers. I have watched developers assume that a thousand-word document equals exactly one thousand tokens. The reality is closer to thirteen hundred tokens for standard English text. The ratio becomes significantly worse when you process code logs or non-English languages.

Whitespace is also tokenized. I have debugged production systems where excessive trailing spaces and redundant tab indentations consumed twenty percent of the total prompt budget. The model reads those spaces as discrete tokens that must be processed through the attention mechanism. You must actively sanitize and strip formatting from your data before passing it to any foundation model.

<div class="visual-wrapper">
  <div class="visual-title">Byte Pair Encoding Breakdown</div>
  <div class="visual-container">
    <iframe src="/static/visuals/token-byte-pair.html" title="Token Byte Pair Animation" loading="lazy"></iframe>
  </div>
</div>

## Input Costs Versus Output Costs

Generating tokens is computationally heavier than reading them. The model reads your entire prompt in parallel during the initial prefill phase. Generating the response happens sequentially. The model must compute the probabilities for the first word, output it, append it to the context, and then recalculate everything to predict the second word.

Providers charge up to five times more for output tokens due to this autoregressive bottleneck. I always optimize my architectures for minimal output generation. You should aggressively instruct the model to be concise and return only the requested data points without conversational filler. You can explore techniques like [Speculative Decoding](/blog/speculative-decoding-explained/) to understand how inference engines attempt to speed up this sequential generation process.

## The JSON Padding Trap

Developers naturally reach for JSON when structuring data for APIs. JSON introduces massive token bloat when used as context inside an LLM prompt. Every curly brace, quotation mark, and repetitive key name consumes a token. I ran experiments comparing JSON representations to YAML for few-shot examples. YAML strips away the syntax heavy brackets and quotes in favor of simple indentation.

I measured a forty percent reduction in input tokens simply by parsing database records into YAML before passing them to the model. The model understands the hierarchical structure perfectly well without the strict JSON syntax. You should reserve JSON strictly for the final output where you need deterministic parsing back into your application layer.

<div class="visual-wrapper">
  <div class="visual-title">Syntax Token Bloat: JSON vs YAML</div>
  <div class="visual-container">
    <iframe src="/static/visuals/json-vs-yaml-tokens.html" title="JSON vs YAML Token Weight Animation" loading="lazy"></iframe>
  </div>
</div>

## Semantic Caching

Sending the exact same prompt to an LLM twice represents a failure in system design. I recommend intercepting user queries before they ever reach the expensive frontier model. You can embed the incoming natural language query into a vector using a fast local embedding model. You then compare that vector against a database of previously answered queries.

When the similarity score crosses a high confidence threshold, you immediately return the cached string. The architecture bypasses the LLM entirely and drops the marginal cost of that query to zero. I rely heavily on semantic caching for customer support chatbots where users ask identical questions using slightly different phrasing.

<div class="visual-wrapper">
  <div class="visual-title">Semantic Cache Query Routing</div>
  <div class="visual-container">
    <iframe src="/static/visuals/semantic-cache-routing.html" title="Semantic Cache Routing Animation" loading="lazy"></iframe>
  </div>
</div>

## Architectural Routing and Small Models

Routing every user query to a massive seventy-billion parameter model burns cash unnecessarily. I build intelligent routing layers that classify the complexity of a prompt at the edge. Simple summarization tasks or basic classification requests are routed to an eight-billion parameter model. Complex coding questions or deep reasoning tasks are forwarded to the expensive frontier model.

The routing logic itself can be handled by a fast embedding classifier or a very cheap language model. You preserve your budget for the tasks that actually require advanced reasoning capabilities. The system becomes significantly faster on average because the smaller models have much lower latency.

## Managing the Expanding Context Window

Foundation models now advertise context windows capable of holding millions of tokens. Developers often stuff entire repositories or massive document dumps into the prompt simply because the API allows it. I have seen cloud bills spike by thousands of dollars overnight from sloppy retrieval pipelines returning too many irrelevant chunks.

The solution requires strict filtering before the prompt is assembled. You must evaluate the relevance of every single chunk. I highly recommend implementing a cross-encoder to score and filter your vector search results, a technique I cover extensively in my post on [Reranking in RAG](/blog/reranking-in-rag-why-your-top-k-results-are-probably-wrong/). You should also look into [Prompt Caching](/blog/prompt-caching-what-it-is-and-when-the-math-works/) to offset the costs when you are forced to send massive system instructions repeatedly.

## Strict Budgeting

Token counting is a core engineering discipline for modern AI applications. I treat token limits with the exact same rigor as database query optimization or memory management. You must measure the token weight of your prompt templates in your continuous integration pipelines. You should actively monitor the output length of your model responses in production. The survival of your application depends entirely on your ability to control these dynamic costs.
