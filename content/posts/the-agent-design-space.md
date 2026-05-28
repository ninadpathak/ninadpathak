---
title: "The Agent Design Space: A Map of What Engineers Are Actually Building"
date: 2026-04-26
slug: "the-agent-design-space"
description: "After surveying production agents across industries, the design space clusters into patterns. Here is what I found."
tags: [ai, agents, architecture]
status: published
---

I spent three weeks reading production architecture posts, scraping GitHub for agent implementations, and talking to engineers who run agents at scale. The goal was to go beyond the taxonomy diagrams and find out what engineers are actually building.

The answer is messier than the taxonomies suggest. Production agents do not map cleanly into types. They cluster into patterns based on the constraints that actually matter: how often the agent runs, what it can break, and how much a human can audit what it did.

## The patterns that show up in production

**Retrieval-augmented single-loop agents** are the most common. A user sends a request. The agent retrieves relevant context, reasons about it, calls a tool or two, and returns an answer. This is what most RAG applications look like when someone wraps them in an agent harness. The loop runs once. The failure modes are limited to bad retrieval and bad tool selection. Teams choose this when the task is bounded and the cost of a wrong answer is low.

I covered the memory and retrieval foundations for this pattern in my posts on [state-of-ai-agent-memory-2026](/blog/state-of-ai-agent-memory-2026/) and [hybrid-search-bm25-vector-search](/blog/hybrid-search-bm25-vector-search/). The retrieval piece is usually not the interesting part. The interesting part is what happens when retrieval fails silently and the agent proceeds on bad context.

**Multi-turn conversational agents** are the second major cluster. These agents maintain state across a single conversation session. They are retrieval-augmented but add a memory layer that tracks the conversation history and lets the agent reference earlier turns. Customer support bots and coding assistants dominate this category. The [short-term-memory-for-ai-agents](/blog/short-term-memory-for-ai-agents/) post covers the mechanisms used in practice.

The failure mode I see most in this cluster is context pollution. Each turn appends to the conversation context. Without active compression or windowing, the agent eventually operates on a bloated context that includes stale or irrelevant earlier turns. This is not a hypothetical failure. I have seen it in production where a customer support agent starts giving answers that reference resolved tickets from three turns ago.

**Workflow orchestration agents** are agents that execute a defined sequence of steps, where each step might itself be an agent or a traditional program. The workflow is defined upfront. The agent handles routing, error recovery, and conditional branching. This is where the [plan-and-execute pattern](/blog/agent-loop-anatomy/) shows up most often in production, usually in document processing pipelines, code review automation, and data transformation tasks.

The error patterns here are different from single-loop agents. A workflow agent that fails midway needs to either checkpoint state or restart from a known good position. I wrote about [circuit breakers](/blog/production-ai-agent-errors/) as a pattern for preventing cascade failures in these systems. The circuit breaker pattern is less relevant in simple single-loop agents and critical in workflow orchestration.

**Supervisor-delegation agents** split a task across multiple specialized agents, with a supervisor agent handling the orchestration. The supervisor decides which sub-agent handles which part of the task, aggregates results, and handles conflicts between agent outputs. This is the most architecturally complex pattern I found in production.

The [supervisor-agent pattern](/blog/multi-agent-vs-single-agent-tradeoffs/) post goes into where this works and where it breaks. The failure mode I want to name specifically: supervisor agents create hidden coordination costs that are easy to underestimate. Each sub-agent call adds latency and a potential failure point. When a supervisor decides to parallelize sub-agent calls, it faces the same challenges I covered in [parallel versus sequential tool calls](/blog/agent-loop-anatomy/). The parallelism gains are real but so are the failure modes.

**Persistent-goal agents** run continuously, maintain state across days or weeks, and work toward goals that require multiple steps across multiple sessions. These are the agents that look least like software and most like automated employees. Bug triage agents, research synthesis agents, and monitoring agents occupy this space.

This is where the [agent-loop-anatomy](/blog/agent-loop-anatomy/) matters most. A persistent-goal agent needs every component of that loop to be durable. If the perceive-think-act cycle drops state on restart, the agent loses track of its goal. If the memory layer serves stale data, the agent makes decisions on outdated premises.

<div class="visual-wrapper">
  <div class="visual-title">THE DESIGN SPACE MAP</div>
  <div class="visual-container">
    <iframe src="/static/visuals/agent-design-space-map.html" title="A 2D design-space map plotting the five production agent patterns by run frequency and blast radius" loading="lazy"></iframe>
  </div>
</div>

## What the production data shows

Looking across the implementations I surveyed, three things stood out.

**Most agents are simpler than the taxonomy suggests.** The five-type taxonomy I published last week is a useful classification frame, but production agents rarely sit cleanly in one type. They are combinations of types with a dominant pattern. The most common production agent is a retrieval-augmented single-loop agent with multi-turn conversational memory. That is a Type 2-3 hybrid that does not exist cleanly in most taxonomies but shows up constantly.

**The tool layer determines reliability more than the model.** Teams that built fragile agents almost always had a tool schema problem, not a model problem. The [tool schema design](/blog/structured-outputs-llms-json-mode-function-calling/) post covers this in detail, but the short version: agents fail when the tool interface is underspecified, when error responses from tools are inconsistent, and when the agent has no schema for retrying a failed tool call.

**Observability is the biggest blind spot.** The second most common production failure, after tool schema problems, was that teams had no way to understand what their agent was doing mid-execution. A minimum viable observability layer matters most here. Most teams I surveyed had basic logging but no structured tracing of agent decisions, no way to replay a specific agent decision path, and no cost attribution per agentic action.

## Where agents are not being built

The survey also showed clear blind spots. Areas where the demand exists but production-grade implementations are rare.

**Cross-agent state synchronization** is a missing piece. When multiple agents need to share state in real time, teams reach for shared databases or message queues, but there is no established pattern for doing this without creating tight coupling between agents. The post on [message passing between agents](/blog/multi-agent-vs-single-agent-tradeoffs/) covers the patterns that exist, but most of them require significant custom plumbing.

**Agent regression testing** is nearly nonexistent. Most teams test agents the same way they test traditional software: unit tests for functions, integration tests for APIs. But an agent that passes a unit test can still fail in production because it encountered a new type of input. The post on [agent and RAG evaluation frameworks](/blog/rag-evaluation-metrics-what-actually-matters/) covers the eval frameworks that come closest to solving this.

**Structured output reliability** from agents is still a hard problem. Agents that must produce structured JSON or execute specific action schemas fail at higher rates than agents that produce freeform text. This is not a model capability problem as much as a prompt and schema design problem, covered in [structured-outputs-llms-json-mode-function-calling](/blog/structured-outputs-llms-json-mode-function-calling/).

## The design space is not a menu

One thing I want to be clear about after this survey: the design space is not a menu where you pick the most impressive pattern. The patterns exist because the constraints that produce them are real.

A reactive information agent is not a lesser version of a persistent-goal agent. It is the right architecture for a bounded task where the cost of failure is low and the task does not need to persist state. The mistake is not choosing a simpler pattern. The mistake is choosing a simpler pattern and then trying to stretch it beyond its intended scope.

When I am sketching a new agent system, I start with the [three questions in the taxonomy post](/blog/the-taxonomy-of-ai-agents/). Does it need to act or just generate? Does it need to persist state? Does the task complexity require multiple agents? Those three questions will narrow the design space faster than any framework diagram.

The [agent-harnesses](/blog/agent-harnesses/) post covers the runtime layer that sits beneath whatever pattern you choose. Whatever architecture you land on, the harness is where reliability gets built or lost.
