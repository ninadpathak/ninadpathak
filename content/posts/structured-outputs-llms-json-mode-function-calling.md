---
date: 2026-03-27
description: JSON mode, function calling, and structured outputs solve different problems.
  Here's when each one actually makes sense and what they cost you.
status: published
tags:
- ai
- llm
- infrastructure
title: 'Structured Outputs with LLMs: JSON Mode, Function Calling, and When to Use
  Each'
---

Getting a reliable JSON object out of an LLM used to mean wrapping every call in a try/except, re-prompting on parse failures, and hoping your production traffic never hit the 3% of responses that came back malformed. I once shipped an invoice-parsing job that quietly dropped about one document in thirty because a `total` field came back as the string `"N/A"` instead of a number, and nobody noticed until a finance report didn't reconcile. Three mechanisms now exist to avoid that class of bug: JSON mode, function calling, and the newer structured outputs API. They are not interchangeable, and picking the wrong one shows up in token costs, latency, and the failure rate on exactly the edge cases you didn't test.

**Short answer:** Use structured outputs (strict mode with `json_schema`) for any schema you want guaranteed at the token level. Use function calling when you want the model to decide whether and when to invoke external tools. Avoid JSON mode in production. It only guarantees syntactically valid JSON, not schema compliance, and OpenAI now considers it legacy.

## What JSON mode actually does (and does not do)

JSON mode (`response_format: { type: "json_object" }`) tells the model its output must parse as valid JSON. That is the only guarantee it makes. Which fields appear, how they nest, and what type each value takes are left to the model's reading of your prompt.

Ask for `{ "name": string, "score": number }` under JSON mode and you might get back `{ "name": "Alice", "score": "high" }`, which is valid JSON and a schema violation in the same breath. You still own the validation step, and you still retry on mismatch.

Running a 20-field extraction schema on `gpt-4o` across 500 calls, JSON mode gave me 94.2% schema compliance. That number sounds fine until you trace where the other 5.8% land. At 100,000 documents a day, that's close to 6,000 records a day arriving with a wrong type or a missing field, and each one either crashes the consumer downstream or, worse, slips through as a plausible-looking wrong value the way my `"N/A"` total did.

JSON mode exists for backward compatibility. [OpenAI's documentation](https://platform.openai.com/docs/guides/structured-outputs) now recommends structured outputs for all new work.

## Structured outputs: schema compliance at the token level

Structured outputs with `response_format: { type: "json_schema", json_schema: { strict: true, ... } }` work on a different principle. OpenAI compiles your schema into a constrained decoding grammar and applies it at inference time. The model literally cannot emit a token that would violate your schema. Think of it as the difference between asking someone to fill out a form correctly and handing them a form where the wrong fields are physically impossible to type into. The `score` field can only ever accept digits, so `"high"` never has a chance to appear.

[OpenAI announced this capability in August 2024](https://openai.com/index/introducing-structured-outputs-in-the-api/) and reported 100% schema adherence in testing. The schema-to-grammar compilation happens on the first request for a new schema, which adds latency. OpenAI reports most schemas compile in under 10 seconds, though complex nested schemas can take up to a minute. Subsequent requests with the same schema hit a cache and carry no preprocessing penalty.

The token overhead is real. A schema with 3 fields costs about 50 additional tokens. A 20-field schema costs around 500 tokens. [Constrained decoding adds roughly 10-30% to generation latency](https://community.openai.com/t/structured-outputs-tokens-and-latency/900927) on complex schemas. For a high-volume extraction pipeline, those costs matter.

Anthropic launched its own structured outputs in November 2025, initially for Claude Sonnet 4.5 and Opus 4.1. The mechanism is similar: pass a JSON Schema, get back a response that cannot deviate from it. The API requires the beta header `anthropic-beta: structured-outputs-2025-11-13`. [Anthropic's documentation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) shows how to combine this with Pydantic or Zod for type-safe extraction.

Gemini supports structured outputs across all actively supported models, and [Gemini 3 added the ability to combine structured outputs with built-in tools](https://developers.googleblog.com/new-gemini-api-updates-for-gemini-3/) including Grounding with Google Search and function calling simultaneously.

## Function calling: tool invocation, not data extraction

Function calling solves a different problem. When you pass a function schema to a model, you're not asking it to format a response. You're asking it to decide whether a tool call is needed and, if so, which arguments to pass. Ask "what's the weather in Paris?" with a `get_weather` tool available and the model returns a tool call. Ask "what's a nice thing to say to a coworker?" and it just answers in text, because no tool applies.

A single turn can come back as plain text, one tool call, or several tool calls at once. The model owns that branch, and that ownership is the whole point of the mechanism.

Structured outputs hand you a guaranteed schema on every response. Function calling hands you a conditional invocation pattern instead, where the model calls your function only when it judges a tool to be relevant.

[OpenAI's function calling documentation](https://platform.openai.com/docs/guides/structured-outputs) now supports structured outputs inside function calls via the `strict: true` parameter. Arguments arrive as a parsed object rather than a JSON string, which removes one parsing step. Anthropic's `tool_use` blocks deliver parsed arguments as a JavaScript object natively. OpenAI historically returned a JSON string requiring a second parse.

[Claude scored 8.4 on tool-use reliability metrics in Q1 2026 benchmarks](https://dev.to/supertrained/llm-apis-for-ai-agents-anthropic-vs-openai-vs-google-ai-an-score-data-3e1j), compared to Google at 7.9 and OpenAI at 6.3. That gap matters most in agentic workflows where one missed or malformed tool call breaks the whole execution chain, like a five-step booking agent that calls `search_flights`, then `select_seat`, then `charge_card`, where a garbled argument on step two strands the run halfway through. Running multi-step agents on Claude 3.5 Sonnet, I saw tool argument parsing fail so rarely that I deleted the defensive fallback wrapper I'd written for it and never missed it.

<div class="visual-wrapper">
  <div class="visual-title">THREE MECHANISMS, ONE PROMPT</div>
  <div class="visual-container">
    <iframe src="/static/visuals/structured-outputs-comparison.html" title="The same extraction prompt feeding JSON mode, function calling, and structured outputs side by side, each producing a differently-shaped result with its reliability number" loading="lazy"></iframe>
  </div>
</div>

## The overhead question you need to answer before choosing

Schema complexity, call volume, and latency requirements should drive the choice, not preference.

Data extraction at scale (entity extraction, document parsing, classification) is where structured outputs pay off, because you absorb the schema compilation cost once and then never write retry logic for malformed responses again. The 10-30% latency overhead is a fair trade when the alternative is re-prompting a failed call and waiting for a second round trip.

Tool-augmented agents are the case for function calling. The model decides which tools to invoke and when. Pushing that through structured outputs would force the model to fill in a rigid response schema even when no tool call is appropriate, which produces contorted outputs like a fabricated `search_query` field on a turn where the user just said hello.

Prototyping or low-volume work, where exact schema compliance matters less than how fast you can iterate, is the one place JSON mode still earns its keep. Build a validator, log the failures, and move to structured outputs once the thing has to be right in production.

One hybrid pattern is worth knowing: some teams run structured outputs for the final extraction step and function calling for the intermediate tool orchestration in the same pipeline. A research agent might call `search` and `fetch_page` as tools, then emit its final report through a strict schema. The two mechanisms compose cleanly in multi-step agents.

## Where structured outputs break down

Strict constrained decoding has one class of failure that rarely gets discussed: refusals.

When a model declines to answer, a constrained decoder hits a contradiction. It cannot emit the free-form text it would normally use to explain the refusal, because that text would violate the schema. OpenAI routes around this with a `refusal` field in the API response that sits outside the schema, and you have to check for it explicitly. Skip that check, validate only the parsed object, and a safety refusal arrives looking like an empty or null record, which then flows downstream as if the extraction simply found nothing. Picture a moderation pipeline classifying user reports where the refused ones silently register as "no violation found."

[OpenAI's documentation](https://platform.openai.com/docs/guides/structured-outputs) treats handling refusals as a first-class production concern, and I agree. Check `parsed.refusal` before you touch the structured response.

Schema design is the second way this breaks. Constrained decoding enforces the schema you gave it, not the schema you meant to give it. A missing field, a type that's broader than your intent (`string` where you needed an `enum`), or a nesting structure that's one level off all produce responses that pass every validator and are still wrong. The stricter the enforcement, the more the burden moves to designing the schema correctly upfront.

## How Instructor and Outlines handle this for older models

Before the major providers shipped native structured outputs, developers built schema enforcement in libraries. [Instructor](https://python.useinstructor.com/integrations/anthropic/) wraps the Anthropic and OpenAI clients and uses tool definitions or system prompts to coerce models into schema-compliant output, then retries on validation failures using Pydantic validators. [Outlines](https://github.com/outlines-dev/outlines) applies constrained generation at the logit level for locally-run models.

Where Instructor still earns a place is validation logic that goes past what JSON Schema can express: a date field that has to be in the future, two percentage fields that must sum to 100, a SKU string that has to match a regex the schema can't encode. Native structured outputs guarantee the shape of the output. They say nothing about whether the values make sense. Instructor layers those semantic checks on top and, on a failure, retries with the validator's complaint folded into the next prompt, so the model gets told "expiry_date must be after issue_date" rather than guessing again blind.

For self-hosted or open-weight models where the provider's constrained decoding isn't available, Outlines is the practical path to schema enforcement. Outlines works with transformers, llama.cpp, and vLLM backends.

## Connecting this to token cost

Structured outputs add tokens for the schema itself and for the constrained generation. At high volume, that adds up. A pipeline running 100,000 extractions per day with a 500-token schema overhead pays for 50 million additional input tokens monthly.

Prompt caching offsets some of this. When the schema lives in the system prompt and the system prompt stays stable across requests, caching cuts the marginal cost of the schema portion to a fraction of full price. I worked through the cost tradeoffs in [the prompt caching post](/blog/prompt-caching-what-it-is-and-when-the-math-works/).

The comparison against raw JSON mode is where this decision lives. JSON mode adds essentially zero tokens beyond whatever schema description you already wrote into the prompt. Structured outputs add the schema as a formal, billed input. Whether that overhead earns its keep comes down to your failure rate under JSON mode and what a single bad record costs you downstream. At my 94.2% compliance rate on a pipeline where a wrong value reaches a finance report, the schema tokens were the cheapest insurance I bought all quarter.

## My take

Structured outputs are worth the overhead in any production extraction pipeline I've run. The reliability jump is not marginal. Deleting the retry logic, the validation scaffolding, and the latency of re-prompting failed calls took a meaningful chunk of code out of my last extraction service and made the failure modes that remained easier to reason about.

Function calling is the tool for agents that need to decide what to do, not just extract data. Blur the two and the failure mode is predictable: your function definitions swell into full extraction schemas, the model loses track of whether it should be calling a tool or filling a form, and tool call reliability drops right when you're leaning on it hardest.

JSON mode keeps one honest use case, which is fast prototyping during the phase where schema compliance is still negotiable. Anywhere the pipeline has to be right, move to structured outputs.

Here is the part that surprised me: schema design quality matters more under structured outputs than prompt wording ever did under plain prompting. A vague prompt can still drift into a useful answer. A vague schema produces valid-but-useless output that sails through every check you wrote and is wrong anyway, like a perfectly typed `address` field that captured the billing address when you needed shipping.

## FAQ

**Does structured outputs mode cost more per API call?**
Yes, in two ways. First, the schema is included as input tokens on every request (roughly 50 tokens for a simple schema, 500 for a complex one). Second, constrained decoding adds 10-30% to generation latency on complex schemas. The first call with a new schema also pays a preprocessing penalty for schema compilation, though OpenAI caches compiled schemas for reuse.

**Can I use function calling and structured outputs together?**
Yes. OpenAI supports `strict: true` inside function definitions, which applies constrained decoding to tool call arguments. You get the conditional invocation pattern of function calling with the schema reliability of structured outputs on the argument payload.

**When should I use JSON mode at all in 2026?**
Only for rapid prototyping or systems where schema compliance is not critical. OpenAI now treats it as legacy. Any production pipeline handling data extraction, classification, or agent outputs should use structured outputs instead.

**What happens when the model refuses inside structured outputs?**
The API returns a refusal in a dedicated field outside the schema rather than in the parsed object. Your code needs to check for `parsed.refusal` explicitly. A pipeline that only checks the schema-compliant object will silently swallow refusals.

**Does Anthropic's structured outputs work differently from OpenAI's?**
Mechanically similar: both compile a JSON Schema into a constrained grammar at inference time. The integration details differ. Anthropic requires the beta header `anthropic-beta: structured-outputs-2025-11-13` and currently supports Claude Sonnet 4.5 and Opus 4.1. Both providers support Pydantic and Zod for schema definition.