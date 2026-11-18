---
category: ai-engineering
primary_query: structured outputs
siblings:
- llm-inference-optimization
- speculative-decoding
bridges:
- slug: agent-loop-anatomy
  reason: A tool call is the action payload inside an agent loop, whose control flow that page describes.
date: 2026-03-27
description: 'JSON mode, structured outputs and function calling promise different things. What each guarantees, what is left to your code, and what changes on self-hosted models.'
status: published
work_note: "I write tutorials and technical articles for AI companies, and I run the product before I write a line. I'm Ninad Pathak, a freelance technical writer, and [we can work together](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Structured Outputs with LLMs: JSON Mode, Function Calling, and When to Use
  Each'
slug: llm-structured-outputs
updated: 2026-11-17
---

Structured outputs constrain a model's completed output to a JSON Schema you supply, JSON mode only promises that the output parses as JSON, and function calling lets the model decide whether to call a tool and with what arguments. OpenAI's [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs) describes the first as "the evolution of JSON mode" and says "We recommend always using Structured Outputs instead of JSON mode when possible."

The guarantee is narrower than the name suggests, and the same guide spells out the limits in two sentences.

"Structured Outputs constrains completed, non-refusal model output to your supplied JSON Schema. Your application still needs to handle refusals, incomplete responses, and API errors, and validate any business rules that the schema does not express."

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/llm-structured-outputs/output-mechanisms.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/llm-structured-outputs/output-mechanisms.narrow.svg" width="288" height="488"><img class="np-has-narrow" src="/static/images/diagrams/llm-structured-outputs/output-mechanisms.svg" width="720" height="528" alt="The same extraction prompt sent through three mechanisms. JSON mode guarantees only syntactically valid JSON, so a field can come back with the wrong type. Function calling lets the model decide whether to call a tool at all. Structured outputs constrain decoding to the schema, so every completed response matches it." loading="lazy" decoding="async"></picture></a>
  <figcaption>JSON mode guarantees valid JSON and nothing about your schema. Structured outputs enforce the schema on every completed response.</figcaption>
</figure>

Structured outputs are the part of [LLM inference](/articles/ai-engineering/) that an application developer sets directly, through a schema.

## JSON mode vs structured outputs vs function calling

The mechanisms differ in what they promise and in what they leave for your code. See the [glossary entry on JSON mode and structured outputs](/glossary/json-mode-vs-structured-outputs/) for the short definitions.

| Mechanism | Promises | Leaves to you |
| --- | --- | --- |
| JSON mode | Output that parses as JSON | Field names, types, missing fields, and everything structured outputs leave to you |
| Structured outputs | Completed, non-refusal output that follows your schema | Refusals, incomplete responses, API errors, business rules |
| Function calling | A decision about whether to call a tool, plus arguments | Running the tool, parsing the arguments, deciding what happens next |

OpenAI keeps JSON mode for older models, noting that "Older models like gpt-4-turbo and earlier may use JSON mode instead." On anything newer, the choice is between a schema for the response and a schema for a tool's arguments.

## What do structured outputs guarantee?

Structured outputs guarantee that a response the model finishes, and does not refuse, matches the schema. OpenAI's Responses API takes the schema in `text.format`, and Chat Completions takes it in `response_format` with `type: "json_schema"` and `strict: true`.

A refusal comes back outside the schema. The Responses API returns it as a content item whose `type` is `"refusal"`, and for Chat Completions the guide's examples check `choice.message.refusal`, so code that validates only the parsed object will treat a refusal as an empty record.

A response cut off by a length limit is incomplete whatever the mode. The guide's Responses examples check `response.status` and `incomplete_details` before reading the result, and its Chat Completions examples check the finish reason.

Latency has one documented cost today, and the guide states it differently in its two tabs. The Responses API tab says without qualification that "the first request you make with any schema will have additional latency as our API processes the schema, but subsequent requests with the same schema will not have additional latency."

The Chat Completions tab opens the same note with "for fine tuned models" and adds "Other models do not have this limitation." Until the two agree, assume a first-request cost for any new schema.

The limit no provider can remove is the schema itself. Constrained decoding enforces the schema you wrote, so a `string` where you needed an `enum`, or a billing address captured where you wanted shipping, passes every check.

## What is function calling for?

Function calling is for letting the model decide whether a tool is needed, which makes it a control mechanism and a poor fit for plain extraction. Asked "what's the weather in Paris?" with a `get_weather` tool available, the model returns [a tool call](/glossary/tool-calling/), and asked for a compliment it answers in text.

OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) lists a `strict` field on each function definition, "Whether to enforce strict mode for the function call", which applies schema enforcement to the arguments. The arguments still arrive as text: each call carries a name "and JSON-encoded arguments", so your code parses them unless an SDK helper does.

A tool call only names the action and its arguments. The [agent-loop anatomy](/articles/agent-loop-anatomy/) article covers the control flow that decides when an agent acts or retries.

## How do Anthropic and Google handle structured outputs?

Anthropic and Google both offer schema-constrained output, with different parameter names. Anthropic's [structured outputs documentation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) says they "guarantee schema-compliant responses through constrained decoding" and records the move out of beta: "The output_format parameter has moved to output_config.format, and beta headers are no longer required."

Google's [Gemini API update](https://developers.googleblog.com/new-gemini-api-updates-for-gemini-3/) of November 25, 2025 added a combination with its hosted tools: "You can now combine Gemini hosted tools, specifically Grounding with Google Search and URL context with structured outputs."

Parameter names in this area move, as Anthropic's did, so check each provider's page before copying an older example, including any older version of this one.

## What changes on self-hosted models?

On open-weight models the guarantee is a serving option you have to turn on and test. Ubicloud's Jesse Donkervliet and Junhao Li [reported on October 20, 2026](https://www.ubicloud.com/blog/fixing-tool-call-accuracy-in-vllm) that a model served on vLLM 0.28 produced the expected tool-call schema 92% of the time, and added "In other words, 2 out of every 25 attempted tool calls failed."

Constrained decoding in vLLM took their benchmark score to 100%, and their post says of the grammar engine that "this runtime enforcement adds negligible performance overhead." vLLM leaves the feature off by default because some models produce worse output when forced.

A commenter on the Hacker News thread, hansvm, [raised the point](https://news.ycombinator.com/item?id=50245187) every strict mode has to answer: "Schema-constrained decoding changes the distribution the LLM will output." The same comment wonders how a back-up-and-retry method would compare, and describes that method as also reaching full tool-call accuracy.

I think the worry is right about a different failure than the one Ubicloud fixed. A grammar guarantees the shape and can still push a model into a worse answer inside that shape, so the check after turning strict mode on is answer quality.

[Outlines](https://github.com/dottxt-ai/outlines) is the library route for local models, and its README claims "Guaranteed valid structure" across backends including vLLM. [Instructor](https://python.useinstructor.com/) covers validation and automatic retries for rules a schema can't express, such as a date that must fall after another date.

The serving side of constrained decoding, including how constrained and [speculative decoding](/articles/speculative-decoding/) interact, is in the [LLM inference optimization guide](/articles/llm-inference-optimization/).

## FAQ

**Does structured outputs mode cost more per API call?** The schema travels with every request, and OpenAI's guide documents extra latency on the first request with a new schema, for any model in its Responses API tab and for fine-tuned models in its Chat Completions tab. I could not find a current official figure for per-token overhead, so measure it on your own schema.

**Can I use function calling and structured outputs together?** Yes. OpenAI's function definitions take a `strict` field that enforces the schema on tool-call arguments, so the model still chooses whether to call the tool and the arguments it sends follow your schema.

**When should I use JSON mode at all in 2026?** Use JSON mode only when the model doesn't support structured outputs. OpenAI's guide recommends structured outputs "when possible" and reserves JSON mode for older models.

**What happens when the model refuses inside structured outputs?** The refusal comes back outside the schema. OpenAI's Responses API returns it as a content item of type `refusal`, and Chat Completions as `message.refusal`, so check for it before reading the parsed object.

**Does Anthropic's structured outputs work differently from OpenAI's?** The mechanism is the same, constrained decoding against a JSON Schema, and the parameters differ. Anthropic's current parameter is `output_config.format`, and its documentation says beta headers are no longer required.
