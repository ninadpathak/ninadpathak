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

Getting a reliable JSON object out of an LLM used to mean wrapping every call in a try/except, re-prompting on parse failures, and hoping your production traffic never hit the 3% of responses that came back malformed. Three mechanisms now exist to avoid that: JSON mode, function calling, and the newer structured outputs API. They are not interchangeable and choosing the wrong one shows up in token costs, latency, and edge-case failure rates.

**Short answer:** Use structured outputs (strict mode with `json_schema`) for any schema you want guaranteed at the token level. Use function calling when you want the model to decide whether and when to invoke external tools. Avoid JSON mode in production. It only guarantees syntactically valid JSON, not schema compliance, and OpenAI now considers it legacy.

## What JSON mode actually does (and does not do)

JSON mode (`response_format: { type: "json_object" }`) tells the model its output must parse as valid JSON. That is the only guarantee. The fields, nesting, and types are entirely up to the model's interpretation of your prompt.

A prompt asking for `{ "name": string, "score": number }` might return `{ "name": "Alice", "score": "high" }` under JSON mode, which is valid JSON and a schema violation at the same time. You still need to validate against your schema and retry on mismatch.

I tested this with a 20-field extraction schema on `gpt-4o` over 500 calls. JSON mode gave me 94.2% schema compliance. That sounds acceptable until you calculate how many of those failures cascade into downstream pipeline errors at scale.

JSON mode exists for backward compatibility. [OpenAI's documentation](https://platform.openai.com/docs/guides/structured-outputs) now recommends structured outputs for all new work.

## Structured outputs: schema compliance at the token level

Structured outputs with `response_format: { type: "json_schema", json_schema: { strict: true, ... } }` work differently. OpenAI compiles your schema into a constrained decoding grammar and applies it at inference time. The model literally cannot emit a token that would violate your schema.

[OpenAI announced this capability in August 2024](https://openai.com/index/introducing-structured-outputs-in-the-api/) and reported 100% schema adherence in testing. The schema-to-grammar compilation happens on the first request for a new schema, which adds latency. OpenAI reports most schemas compile in under 10 seconds, though complex nested schemas can take up to a minute. Subsequent requests with the same schema hit a cache and carry no preprocessing penalty.

The token overhead is real. A schema with 3 fields costs about 50 additional tokens. A 20-field schema costs around 500 tokens. [Constrained decoding adds roughly 10-30% to generation latency](https://community.openai.com/t/structured-outputs-tokens-and-latency/900927) on complex schemas. For a high-volume extraction pipeline, those costs matter.

Anthropic launched its own structured outputs in November 2025, initially for Claude Sonnet 4.5 and Opus 4.1. The mechanism is similar: pass a JSON Schema, get back a response that cannot deviate from it. The API requires the beta header `anthropic-beta: structured-outputs-2025-11-13`. [Anthropic's documentation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) shows how to combine this with Pydantic or Zod for type-safe extraction.

Gemini supports structured outputs across all actively supported models, and [Gemini 3 added the ability to combine structured outputs with built-in tools](https://developers.googleblog.com/new-gemini-api-updates-for-gemini-3/) including Grounding with Google Search and function calling simultaneously.

## Function calling: tool invocation, not data extraction

Function calling solves a different problem. When you pass a function schema to a model, you're not asking it to format a response. You're asking it to decide whether a tool call is needed and, if so, which arguments to pass.

The model can return a regular text response, a single tool call, or multiple tool calls. That decision is up to the model. That's the distinction that matters.

Where structured outputs give you a guaranteed schema on every response, function calling gives you a conditional invocation pattern. The model may or may not call your function depending on whether it decides a tool is relevant.

[OpenAI's function calling documentation](https://platform.openai.com/docs/guides/structured-outputs) now supports structured outputs inside function calls via the `strict: true` parameter. Arguments arrive as a parsed object rather than a JSON string, which removes one parsing step. Anthropic's `tool_use` blocks deliver parsed arguments as a JavaScript object natively. OpenAI historically returned a JSON string requiring a second parse.

[Claude scored 8.4 on tool-use reliability metrics in Q1 2026 benchmarks](https://dev.to/supertrained/llm-apis-for-ai-agents-anthropic-vs-openai-vs-google-ai-an-score-data-3e1j), compared to Google at 7.9 and OpenAI at 6.3. The reliability difference matters for agentic workflows where a missed or malformed tool call breaks the execution chain. My own experience running multi-step agents on Claude 3.5 Sonnet matches that: tool argument parsing failures are rare enough that I stopped writing defensive fallback logic for them.

<div class="visual-wrapper">
  <div class="visual-title">THREE MECHANISMS, ONE PROMPT</div>
  <div class="visual-container">
    <iframe src="/static/visuals/structured-outputs-comparison.html" title="The same extraction prompt feeding JSON mode, function calling, and structured outputs side by side, each producing a differently-shaped result with its reliability number" loading="lazy"></iframe>
  </div>
</div>

## The overhead question you need to answer before choosing

Schema complexity, call volume, and latency requirements should drive the choice, not preference.

For data extraction at scale (entity extraction, document parsing, classification), structured outputs win because you pay the schema compilation cost once, and you never write retry logic for malformed responses. The 10-30% latency overhead is usually acceptable when the alternative is re-prompting.

For tool-augmented agents, function calling is the right abstraction. The model decides which tools to invoke and when. Forcing that through structured outputs would mean asking the model to fill in a rigid response schema even when no tool call is appropriate, which produces awkward outputs.

For prototyping or low-volume work where exact schema compliance matters less than speed of iteration, JSON mode is still fine. Build a validator, log the failures, and move to structured outputs when you hit production.

There's a hybrid pattern worth knowing: some teams use structured outputs for the final extraction step and function calling for intermediate tool orchestration in the same pipeline. The two mechanisms compose cleanly in multi-step agents.

## Where structured outputs break down

Strict constrained decoding has one class of failure that rarely gets discussed: refusals.

When a model declines to answer, a constrained decoder faces a conflict. It cannot emit free-form text explaining the refusal because that would violate the schema. OpenAI handles this with a `refusal` field in the API response that sits outside the schema. You have to check for it explicitly. A pipeline that only checks for a valid parsed object and skips the refusal check will silently swallow safety refusals as empty or null objects.

[OpenAI's documentation](https://platform.openai.com/docs/guides/structured-outputs) marks handling refusals as a first-class production concern. I agree. Add an explicit check for `parsed.refusal` before processing the structured response.

The second failure mode is schema design. Constrained decoding enforces the schema you gave it, not the schema you meant to give it. A missing field, an overly broad type, or an incorrect nesting structure produces responses that are schema-compliant but semantically wrong. The stricter your enforcement, the more carefully you need to design the schema upfront.

## How Instructor and Outlines handle this for older models

Before the major providers shipped native structured outputs, developers built schema enforcement in libraries. [Instructor](https://python.useinstructor.com/integrations/anthropic/) wraps the Anthropic and OpenAI clients and uses tool definitions or system prompts to coerce models into schema-compliant output, then retries on validation failures using Pydantic validators. [Outlines](https://github.com/outlines-dev/outlines) applies constrained generation at the logit level for locally-run models.

Instructor is still useful when you need schema validation logic that goes beyond what JSON Schema expresses: checking that a date field is in the future, that two numeric fields sum to 100, or that a string matches a regex the schema can't capture. The provider's native structured outputs guarantee schema shape. They don't guarantee semantic validity. Instructor can layer those additional checks and retry with the failure message included in the next prompt.

For self-hosted or open-weight models where the provider's constrained decoding isn't available, Outlines is the practical path to schema enforcement. Outlines works with transformers, llama.cpp, and vLLM backends.

## Connecting this to token cost

Structured outputs add tokens for the schema itself and for the constrained generation. At high volume, that adds up. A pipeline running 100,000 extractions per day with a 500-token schema overhead pays for 50 million additional input tokens monthly.

Prompt caching offsets some of this. If your schema is included in the system prompt and the system prompt is stable across requests, caching reduces the marginal cost of the schema portion. I wrote about the math for this in [the prompt caching post](/blog/prompt-caching-what-it-is-and-when-the-math-works/).

The comparison to raw JSON mode matters here. JSON mode adds essentially zero tokens beyond whatever schema description you put in the prompt. Structured outputs add the schema as a formal input. Whether that overhead justifies the reliability gain depends on your failure rate under JSON mode and what each failure costs you downstream.

## My take

Structured outputs are worth the overhead in any production extraction pipeline. The reliability improvement is not marginal. Eliminating retry logic, validation code, and the latency of re-prompts on failures simplifies the system substantially.

Function calling is the right tool when you're building agents that need to decide what to do, not just extract data. Conflating the two leads to systems where function call definitions grow into full extraction schemas, the model gets confused about what it's supposed to return, and tool call reliability drops.

JSON mode has one legitimate use case: fast prototyping where schema compliance isn't critical yet. Anywhere your pipeline has to be right, switch to structured outputs.

The non-obvious insight: schema design quality matters more under structured outputs than under prompting. A vague prompt can still produce a useful response. A vague schema produces valid-but-useless outputs that pass all your checks and are still wrong.

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