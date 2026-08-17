# Brief: Tool Schema Design for Reliable Tool Calls

**Slot:** 2026-10-09 | Order 72 | **Type:** NEW focused | **Cluster:** AI agents, memory,
RAG, inference | **Subcluster:** AI-ready documentation | **Experience: B**

## Why this row survives

This is a structural page, not a traffic forecast. Three existing articles independently tried to
link to this subject before it existed: `the-taxonomy-of-ai-agents`, `agent-loop-anatomy`, and
`the-agent-design-space`. Their links currently fall back to the structured-outputs article, whose
actual job is choosing an output mechanism rather than designing a reliable tool interface.

No search-volume or AI Overview claim is established for this row. Do not invent one in the run.

## Reader task

Design tool names, descriptions, parameters, constraints, and error contracts that let a model
select the intended operation and supply usable arguments without treating schema validity as
permission to execute.

## Owns

The interface-design decision: how one tool differs from its neighbours, how its schema narrows
valid inputs, how the host reports failures, and how a fixed evaluation set shows whether the
model calls it correctly.

## Must not repeat

- JSON mode versus structured outputs versus function calling. The live
  `/articles/structured-outputs-llms-json-mode-function-calling/` page owns that format choice.
- The general tool-calling loop and host responsibility. `/glossary/tool-calling/` owns the compact
  definition.
- MCP transport, discovery, or server setup. The two MCP articles own those jobs.
- A general catalogue of production-agent failures. `production-ai-agent-errors` owns that scope.

This page may link to each boundary when the reader needs it. It must not absorb their sections to
look more comprehensive.

## Evidence — Experience B

The article does not ship from schema advice alone. Run a controlled tool-calling comparison whose
result was not known when the fixtures were written.

1. Define one small, real tool set with at least one plausible selection collision, such as lookup
   by exact identifier versus search by free text. Keep execution harmless and local.
2. Prepare a weak schema and a corrected schema for the same operations. Change interface fields,
   not the underlying tool behaviour.
3. Freeze the prompt fixtures before any model calls. Cover exact identifiers, ambiguous natural
   language, invalid enum values, missing required arguments, and a request the host must refuse.
4. Use one named model snapshot and identical settings for both variants. Record the date and the
   raw proposed calls. The sample is an evaluation of that snapshot, not a universal model ranking.
5. Score four outcomes separately: correct tool selection, schema-valid arguments, semantically
   correct arguments, and host-policy refusal. A valid JSON object is not automatically a correct
   or authorised call.
6. Publish the fixtures, schemas, raw outputs with secrets removed, scorer, and rerun command. The
   artifact passes the information test only because the model outputs were unknown in advance.

**Feasibility gate:** confirm a real tool-calling model surface before drafting. A validator that
accepts fixtures authored in the same run carries zero information and does not satisfy Experience
B. If no authorised model surface is available, do not replace the experiment with simulated
calls. Transition the row to `Skipped` through `ninadpathak_queue_state.py` with that reason and
leave the slot empty.

## Claims the evidence does not support

- A percentage improvement for models other than the tested snapshot.
- “Production reliability” from one synthetic tool set.
- A claim that narrower schemas grant execution authority.
- A provider-wide rule inferred from one API's supported JSON Schema subset.

## Internal links, verified in the built sitemap

- `/articles/structured-outputs-llms-json-mode-function-calling/`
- `/articles/model-context-protocol-explained/`
- `/articles/agent-loop-anatomy/`
- `/glossary/tool-calling/`

## Inbound retrofit after publication

Replace the current structured-outputs stopgap only after the final canonical is live:

- `content/posts/2026-04-21-the-taxonomy-of-ai-agents.md`
- `content/posts/2026-04-23-agent-loop-anatomy.md`
- `content/posts/the-agent-design-space.md`

The retrofit belongs in the publish commit. Do not guess the future slug from this brief.
