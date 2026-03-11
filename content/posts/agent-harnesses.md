---
title: "Agent harnesses: the infrastructure layer your LLM agent actually needs"
date: 2026-03-22
description: "Every production AI agent needs a harness. Here's what one contains, why frameworks often aren't enough, and how to build the layer that actually determines reliability."
tags: [ai, agents, infrastructure, llm]
status: published
---

An agent without a harness is a prompt with ambitions. The LLM handles reasoning. The harness handles everything else: tool registration, state persistence, error recovery, prompt assembly, rate limiting, and the thousand other things that determine whether a multi-step agent actually completes its task or quietly fails at step four.

I've watched teams build the same harness from scratch three times before deciding to use a framework, and I've watched other teams adopt frameworks they didn't understand and spend weeks fighting the abstraction. The choice matters. Understanding what a harness does before you choose how to build one is the prerequisite.

**What is an agent harness?** An agent harness is the runtime control layer that sits between your application and the LLM. It accepts a task, manages the agent's execution loop, provides the LLM with tools and context, handles tool call responses, tracks state across steps, and surfaces results and errors back to your system. The LLM handles reasoning. The harness handles execution.

---

## Why the raw API isn't enough

A direct LLM API call is stateless. You send a prompt, get a completion, done. Agents need more. They make decisions across multiple steps, call external tools, accumulate context, and need to recover from partial failures.

Consider a research agent that reads ten web pages, synthesizes findings, and writes a report. Across that task it might make 30 to 50 API calls, call a browser tool twenty times, and manage a context window that grows with each observation. None of that is handled by the API itself.

Without a harness, the code that manages all this lives in your application layer. You write an execution loop. You handle tool call parsing. You append tool results to the message history. You catch API rate limit errors and retry. You truncate context when it gets too long. You log what happened for debugging.

That's a harness. You've built one. The question is whether it's the one you'd design intentionally or the one that grew organically around your specific use case and is now hard to test, extend, or hand off.

---

## What a harness actually contains

A well-designed harness has five components.

**Tool registry.** A catalog of available tools with their schemas, descriptions, and execution handlers. The harness exposes this catalog to the LLM as function definitions and intercepts tool call requests, routes them to the right handler, and returns results in the format the LLM expects. The non-obvious part: the tool registry is also where you enforce permissions and rate limits per tool. A web browsing tool that can make unlimited requests is an incident waiting to happen.

**Prompt assembler.** At inference time, the harness constructs the full context window from multiple sources: the system prompt, any cached instructions, retrieved documents, conversation history, current task state, and pending tool results. The order matters. How much to include matters. The prompt assembler is where context engineering happens at runtime, not at design time.

**Execution loop.** The core of any agent harness. Send the current context to the LLM. If the response contains a tool call, execute it, append the result, and send again. If the response is a final answer, surface it. Handle the stop conditions: max iterations reached, context window full, explicit done signal, or unrecoverable error. The loop is simple to describe and surprisingly easy to get wrong under load.

**State manager.** Agents that run longer than a single API call need somewhere to put their working state. What subtasks are complete? What information has been gathered? What decisions have been made? Some harnesses keep state in the context window, which works for short tasks but breaks for long ones. Others write to external storage at each step, enabling checkpoint-based recovery. The choice between in-context state and external state is the single biggest architectural decision in agent design.

**Observer.** Structured logging of every agent step: what was in the prompt, what the LLM returned, which tool was called, what it returned, how long each step took. Without this, debugging a failed agent run means staring at opaque error messages. With it, you can replay any run, pinpoint exactly where reasoning went wrong, and build evaluation datasets from production traces. Observability is not optional for anything running in production.

---

## Frameworks versus building your own

The frameworks worth knowing:

**LangChain's AgentExecutor and LangGraph.** AgentExecutor is the original framework harness, now showing its age for complex multi-agent workflows. LangGraph is the current recommendation for anything graph-based or requiring fine-grained control over agent topology. Mature ecosystem, extensive integrations, steeper learning curve than the docs suggest.

**LlamaIndex's agent framework.** Tightly integrated with LlamaIndex's retrieval primitives. If you're already using LlamaIndex for retrieval-augmented generation, the agent layer composes naturally. Less flexible than LangGraph for complex multi-agent topologies.

**Microsoft AutoGen.** Designed around multi-agent conversations where different agents with different roles collaborate on tasks. A good fit if your problem is inherently multi-agent. Overkill for single-agent systems.

**OpenAI's Agents SDK.** OpenAI's lightweight framework, open-sourced and updated from their earlier Swarm project. Minimal abstraction, close to raw API, good for teams that want to understand what's happening without fighting framework internals.

**Custom harnesses.** More common than people admit. Most teams I've talked to who are serious about production reliability end up with a custom harness for their core agent path, even if they started with a framework. The reason is almost always the observer component. Production observability requirements exceed what frameworks provide out of the box.

My take on the build-versus-buy question: use a framework to learn the pattern and move fast in the first month. Plan to own the harness layer for anything critical. The framework abstractions that feel helpful during development often become obstacles when you need to debug production failures at the step level.

---

## The checkpoint problem

The hardest part of building a harness is state recovery.

Agents fail partway through tasks. The LLM hallucinates a tool call argument. A downstream API returns a 503. Context fills up at step 18 of a 25-step task. A network timeout kills the connection.

Without checkpointing, all of those failures mean starting over. For a task that takes 20 minutes and costs $0.80 in API calls, that's manageable. For a task that takes four hours and costs $15, it isn't.

Checkpointing means writing the agent's full state to durable storage after each completed step. State includes the message history, any external data gathered, decisions made, subtask completion status, and metadata like total token usage and elapsed time.

Three checkpointing patterns I've seen work:

**Step-level persistence.** Write state after each tool call completes. Maximum recovery granularity, higher storage and write overhead. Right for long-running tasks with expensive tool calls.

**Phase-level persistence.** Write state at logical phase boundaries: after research is complete, after analysis is complete, before writing begins. Simpler to implement, coarser recovery points. Right for tasks with clear phases that take roughly equal time.

**Idempotent tool design.** Build tools so that calling them twice produces the same result as calling them once. Combined with step-level checkpointing, this means recovery always works: re-run from the last checkpoint, idempotent tools produce the same results, the agent continues from where it stopped. Harder to implement, but it eliminates an entire class of recovery errors.

The harness is where checkpointing logic lives. The LLM doesn't know about checkpoints. The application layer shouldn't have to manage them. The harness takes on that responsibility as a core function.

---

## Context management inside the harness

The context window is a fixed resource. Long-running agents consume it. The harness needs a policy for what to do when context gets full.

Four approaches, roughly in order of complexity:

**Truncate from the oldest end.** Drop the earliest messages when context is near capacity. Simple. Loses information. Acceptable for tasks where early messages are low-value.

**Summarize and compress.** Before truncating, run a summarization step that condenses earlier turns into a compact summary. Keep the summary, drop the raw messages. Better information preservation, adds latency and cost at compression time.

**External memory with retrieval.** Keep the full message history in an external store. At each step, retrieve the most relevant past observations and inject them into context. The hardest approach to implement correctly, but the only one that scales to truly long-horizon tasks.

**Task decomposition.** Avoid the problem by breaking large tasks into smaller subtasks, each of which fits comfortably in context. Pass outputs between subtasks explicitly rather than relying on a shared context window. Requires more upfront task design but produces the most reliable results.

The harness is the right place to implement whichever policy fits your task characteristics. Pushing this logic into the LLM's prompt ("summarize when context is full") produces inconsistent results. Handling it deterministically in the harness produces predictable behavior.

---

## A minimal harness checklist

Before deploying any agent to production, run through these requirements:

**Tool registry:**
- All tools have typed schemas with validation
- Tool calls are logged with inputs, outputs, and latency
- Tools have per-call timeout enforcement
- Tool errors return structured error objects the LLM can reason about

**Execution loop:**
- Maximum iteration count is enforced
- Context window usage is tracked at each step
- Loop exits cleanly on unrecoverable error with a structured error response
- Stop conditions are explicit, not inferred from LLM output format

**State manager:**
- Task state is serializable
- Checkpoint write happens after each successful tool call
- Recovery from checkpoint is tested, not assumed to work

**Observer:**
- Every prompt sent is logged with timestamp and token count
- Every LLM response is logged with latency and finish reason
- Every tool call is logged with full inputs and outputs
- Traces are queryable by run ID

---

## When you don't need a harness

Not every LLM application is an agent. A harness adds complexity. For applications that are single-turn or lightly interactive, that complexity is unnecessary overhead.

You probably don't need an agent harness if your application does one of the following:

- Takes a single user input, calls the LLM once, and returns a response
- Calls the LLM a fixed number of times with a fixed sequence of prompts
- Uses retrieval-augmented generation with a fixed retrieval step followed by a single synthesis step

You need a harness when your application does one of the following:

- Lets the LLM decide which tools to call and in what order
- Runs tasks that take more than a handful of LLM calls to complete
- Needs to recover from partial failures without restarting from scratch
- Requires auditability of what the agent did and why

The line is roughly: if the LLM controls the flow, you need a harness. If your code controls the flow and the LLM is a subroutine, you don't.

---

## Frequently asked questions

**What's the difference between an agent harness and an agent framework?**

A framework is a library or tool that provides harness functionality. The harness is the concept. LangGraph, AutoGen, and OpenAI's Agents SDK are frameworks that implement harness patterns. You can build a harness without using a framework.

**Do agent harnesses add significant latency?**

The harness itself adds minimal latency. State writes and checkpoint operations add some overhead, typically under 50 ms per step on local storage and 100 to 300 ms on remote storage. The bigger latency driver is the execution loop overhead when you're making dozens of LLM calls in sequence.

**How do harnesses handle concurrent agents?**

Most framework harnesses are designed for single-agent execution. Multi-agent concurrency requires explicit design: shared state needs locking or conflict resolution, tool rate limits need to account for concurrent usage, and the observer needs to tag traces by agent identity. AutoGen and LangGraph both have patterns for this, but concurrent agent execution adds meaningful complexity.

**What should I log in the observer?**

Log every prompt (or a hash of it if PII is a concern), every completion, every tool call with inputs and outputs, every error with full context, and total token usage per step. At minimum. Production incidents in agent systems are almost always debugged by replaying traces.

**When should I checkpoint after every step versus after phases?**

Checkpoint after every step if any individual step is expensive: long-running API calls, database writes, or anything that takes more than 10 to 15 seconds. Checkpoint after phases if steps are fast but phases have clear semantic meaning. The goal is always the same: minimize the amount of work lost on failure.

---

The harness is not the interesting part of an agent system. The interesting part is what the agent can do. The harness is the part that determines whether what the agent can do is reliable enough to matter in production. Getting it right upfront is much cheaper than rebuilding it around a system that's already deployed.
