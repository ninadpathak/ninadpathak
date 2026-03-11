---
title: "Agent harnesses: the infrastructure layer your LLM agent actually needs"
date: 2026-03-10
description: "Every production AI agent needs a harness. Here's what one contains, why frameworks often aren't enough, and how to build the layer that actually determines reliability."
tags: [ai, agents, infrastructure, llm]
status: published
---

Picture a research agent that reads twenty web pages, cross-references the findings, and produces a structured report. Sounds straightforward until you watch it fail at step fourteen because a downstream API timed out, and you realize the whole run has to start from scratch. That failure is not a model failure. The LLM reasoned correctly every step of the way. What failed was the infrastructure holding it together.

That infrastructure has a name: the agent harness.

**What an agent harness is:** An agent harness is the runtime control layer between your application and the LLM. It accepts a task, manages the execution loop, provides the model with tools and context, handles tool call results, tracks state across steps, and surfaces results and errors back upstream. The model handles reasoning. The harness handles everything else.

## Why the raw LLM API breaks down for agentic tasks

A direct API call is stateless. You send a prompt, receive a completion, and the interaction ends. Agents need something more durable. They make decisions across many sequential steps, call external tools, accumulate context as they go, and need to recover gracefully from partial failures.

Consider that research agent again. Across a single task it might make thirty to fifty API calls, invoke a browser tool twenty times, and manage a context window that grows with every new observation. The API handles none of that coordination. Without something to manage it, that coordination code ends up scattered across your application layer: a custom execution loop here, some ad-hoc tool call parsing there, a retry handler someone bolted on after the first production incident.

That is still a harness. The question is whether it was designed intentionally or grew organically around a specific use case until it became impossible to test, extend, or hand off.

## The five components every harness contains

A well-designed harness is not one monolithic block of logic. It has five distinct components, each with a specific responsibility.

**Tool registry.** A catalog of available tools, each defined with a typed schema, a description the model can read, and an execution handler the harness calls when the model requests it. The harness intercepts tool call requests, routes them to the right handler, and returns results in the format the model expects. The non-obvious part: the tool registry is also where you enforce per-tool permissions and rate limits. A web browsing tool with uncapped request volume is an incident waiting to happen.

**Prompt assembler.** At inference time, the harness constructs the full context window from multiple sources: the system prompt, any cached instructions, retrieved documents, conversation history, current task state, and pending tool results. The order of those components matters. How much of each to include matters. The prompt assembler is where context engineering happens at runtime, dynamically, not once at design time and never revisited.

**Execution loop.** The core of any harness. Send the current context to the model. If the response contains a tool call, execute it, append the result, and send again. If the response is a final answer, surface it. Enforce the stop conditions: maximum iterations reached, context window full, explicit completion signal, unrecoverable error. The loop is simple to describe and surprisingly easy to get wrong at scale, especially when you need it to handle concurrent runs and partial failures without corrupting shared state.

**State manager.** Agents that span more than a few API calls need somewhere to store their working state: what subtasks are complete, what data has been gathered, what decisions have been made. Some harnesses keep all of this inside the context window, which works for short tasks and breaks for long ones. Others write to external storage after each step, enabling checkpoint-based recovery. That choice (in-context state versus external state) is the single biggest architectural decision in agent design, and the harness is where it gets made.

**Observer.** Structured logging of every step: what was in the prompt, what the model returned, which tool was called, what it returned, how long each step took. Without observability, debugging a failed run means staring at an opaque error and guessing. With it, you can replay any run, pinpoint exactly where reasoning went wrong, and build evaluation datasets from production traces. Observability is not a nice-to-have for production agents. It is load-bearing infrastructure.

## Framework options and where each one fits

The open-source ecosystem has matured enough that building a harness from scratch is no longer the default starting point. Several frameworks implement harness patterns with meaningful differences in philosophy and scope.

| Framework | Best fit | Key tradeoff |
|---|---|---|
| LangGraph | Complex multi-agent topologies, graph-based workflows | Steeper learning curve than docs suggest |
| LlamaIndex agents | Teams already using LlamaIndex for retrieval | Less flexible for complex multi-agent patterns |
| Microsoft AutoGen | Inherently multi-agent problems with conversational agents | Overkill for single-agent systems |
| OpenAI Agents SDK | Teams wanting minimal abstraction close to raw API | Less batteries-included than LangGraph |
| Custom harness | Production systems with strict observability requirements | Higher upfront engineering cost |

LangGraph is the framework I reach for when the agent topology is genuinely complex: multiple agents with different roles, conditional routing between steps, or subgraphs that need to run in parallel. For something closer to a single focused agent, OpenAI's Agents SDK (which evolved from the earlier Swarm project) offers a lightweight starting point that stays close to the raw API and does not require fighting abstraction layers to understand what is happening.

The pattern I have seen most often in serious production systems is hybrid: a framework for early development and learning, then a custom harness for the critical agent path once the team understands what observability requirements actually look like in production. The framework abstractions that accelerate development in month one often become obstacles in month three, when you need step-level traces and the framework logs at a coarser granularity.

## Checkpointing: the part most harnesses get wrong

The hardest problem in harness design is not the execution loop. The hardest problem is state recovery.

Agents fail partway through tasks. The model hallucinates a tool call argument. A downstream API returns a 503. Context fills up at step eighteen of a twenty-five-step task. A network timeout drops the connection.

Without checkpointing, every one of those failures means restarting from the beginning. For a twenty-minute task costing a dollar in API fees, that is manageable. For a four-hour task costing fifteen dollars, it is not, and the cost compounds quickly when the failures are frequent enough to matter.

Checkpointing means writing the agent's full state to durable storage after each completed step. That state includes the message history, any external data gathered, decisions made, subtask completion status, and metadata like total token usage and elapsed time.

Three patterns work in practice:

**Step-level persistence.** Write state after each tool call completes. Maximum recovery granularity, higher storage overhead. Appropriate for long-running tasks with expensive tool calls.

**Phase-level persistence.** Write state at logical phase boundaries: after research completes, after analysis completes, before writing begins. Simpler to implement, coarser recovery points. Appropriate for tasks with clear phases that take roughly equal time.

**Idempotent tool design.** Build tools so calling them twice produces the same result as calling them once. Combined with step-level checkpointing, this eliminates an entire class of recovery errors: re-run from the last checkpoint, idempotent tools produce the same results, the agent continues from where it left off. Harder to implement, but the reliability improvement is substantial.

The harness owns the checkpointing logic. The model has no concept of checkpoints. The application layer should not have to manage them. Taking that responsibility into the harness as a core function is what separates a harness built for production from one built to get a demo working.

## Context management strategies for long-horizon tasks

The context window is a fixed resource. Long-running agents consume it. The harness needs a deliberate policy for what happens when it gets full, because "do nothing" is not a policy, it is a bug that surfaces at the worst possible moment.

Four approaches, in order of implementation complexity:

**Truncation.** Drop the earliest messages when context approaches capacity. Simple, predictable, and information-lossy. Acceptable when early messages are genuinely low-value.

**Summarization.** Before truncating, run a compression step that condenses earlier turns into a compact summary. Keep the summary, drop the raw messages. Better information preservation at the cost of additional latency and API spend at compression time.

**External memory with retrieval.** Keep the full message history in an external store. At each step, retrieve the most relevant past observations and inject them into context. The only approach that scales to truly long-horizon tasks, and the hardest to implement correctly.

**Task decomposition.** Avoid the problem by breaking large tasks into smaller subtasks, each fitting comfortably in context. Pass outputs between subtasks explicitly rather than relying on a shared context window. Requires more upfront task design, but produces the most reliable results for complex workflows.

The harness is the right place to implement whichever policy fits your task characteristics. Handling context management deterministically in the harness produces predictable behavior. Delegating it to the model with a prompt instruction like "summarize when context is full" produces inconsistent results.

## What to check before deploying an agent to production

Before any agent ships, a harness audit should cover the following ground.

**Tool registry:**
- All tools have typed schemas with input validation
- Tool calls are logged with inputs, outputs, and latency
- Tools have per-call timeout enforcement
- Tool errors return structured objects the model can reason about

**Execution loop:**
- Maximum iteration count is enforced and tested
- Context window usage is tracked at each step
- Loop exits cleanly on unrecoverable error with a structured error response
- Stop conditions are explicit, not inferred from output format

**State manager:**
- Task state is fully serializable
- Checkpoint write happens after each successful tool call
- Recovery from checkpoint is tested, not assumed to work

**Observer:**
- Every prompt is logged with timestamp and token count
- Every completion is logged with latency and finish reason
- Every tool call is logged with full inputs and outputs
- Traces are queryable by run ID

That last item matters more than it looks. Production incidents in agent systems are almost always diagnosed by replaying traces. Without a run ID that threads through every log entry for a given execution, trace replay is not possible and debugging collapses into guesswork.

## When you do not need a harness

Not every LLM application is an agent. A harness adds real complexity, and adding complexity to a system that does not need it is not good engineering.

Harness complexity is unnecessary when an application takes a single user input, calls the model once, and returns a response; when it calls the model a fixed number of times with a fixed sequence of prompts; or when it uses retrieval-augmented generation with a fixed retrieval step followed by a single synthesis step.

A harness is necessary when the model decides which tools to call and in what order; when tasks span more than a handful of API calls; when partial failures need recovery without a full restart; or when auditability of what the agent did and why is a requirement.

The rough line: if the model controls the flow, the harness is load-bearing infrastructure. If the application controls the flow and the model is a subroutine, the harness is overhead.

## The harness is not glamorous, and that is the point

The agent harness is not where interesting AI capability lives. The interesting capability is what the agent can do. The harness is what determines whether that capability is reliable enough to run in production, survive failures, and be debugged when something goes wrong.

Teams that treat the harness as scaffolding they will clean up later consistently spend more time on reliability than teams that design it deliberately from the start. The investment pays off not because a well-designed harness makes agents smarter, but because it makes failure modes predictable and recoverable.

An agent that fails cleanly, checkpoints its progress, and can be debugged through structured traces is worth far more than one that is technically more capable but opaque when it breaks. In production, predictable failure beats opaque success.

## Frequently asked questions

**What is the difference between a harness and a framework?**

A framework is a library that implements harness patterns. The harness is the concept. LangGraph, AutoGen, and OpenAI's Agents SDK are frameworks. You can build a harness without using any of them.

**Do harnesses add significant latency?**

The harness itself adds minimal latency. State writes add some overhead: typically under 50 milliseconds per step on local storage and 100 to 300 milliseconds on remote storage. The bigger latency driver is the execution loop when dozens of sequential LLM calls are in play.

**How do harnesses handle concurrent agents?**

Most framework harnesses are designed for single-agent execution. Multi-agent concurrency requires explicit design: shared state needs locking or conflict resolution, tool rate limits need to account for concurrent usage, and the observer needs to tag traces by agent identity. AutoGen and LangGraph both have patterns for this, but concurrent execution adds meaningful architectural complexity.

**When should checkpoints happen after every step versus after phases?**

Checkpoint after every step when any individual step is expensive: long-running API calls, database writes, or anything that takes more than ten to fifteen seconds. Checkpoint after phases when steps are fast but phases carry clear semantic meaning. The goal is the same in either case: minimize work lost on failure.

**What belongs in the observer log?**

Every prompt (or a hash of it when PII is a concern), every completion, every tool call with full inputs and outputs, every error with complete context, and total token usage per step. Production incidents in agent systems are almost always debugged by replaying traces, and you cannot replay what you did not capture.
