---
title: "The Agent Design Space: A Map of What Engineers Are Actually Building"
date: 2026-04-26
slug: "the-agent-design-space"
description: "After surveying production agents across industries, the design space clusters into patterns. Here is what I found."
tags: [ai, agents, architecture]
status: published
---

Three weeks of reading production architecture posts, scraping GitHub for agent implementations, and talking to engineers who run agents at scale taught me one thing the taxonomy diagrams miss: I wanted to know what engineers are actually building, not what the boxes say they should build.

What I found is messier than the taxonomies suggest. Production agents do not map cleanly into types. They cluster around the constraints that decide everything else: how often the agent runs, what it can break when it gets something wrong, and how much a human can audit after the fact.

## The patterns that show up in production

**Retrieval-augmented single-loop agents** are the most common. A user sends a request, the agent retrieves relevant context, reasons about it, calls a tool or two, and returns an answer. Plenty of RAG applications look exactly like this once someone wraps them in an agent harness. Because the loop runs once, the failure modes stay limited to bad retrieval and bad tool selection. Teams reach for this shape when the task is bounded and a wrong answer costs little, say a docs-search assistant that surfaces the wrong paragraph and the user just re-asks.

I covered the memory and retrieval foundations for this pattern in my posts on [state-of-ai-agent-memory-2026](/blog/state-of-ai-agent-memory-2026/) and [hybrid-search-bm25-vector-search](/blog/hybrid-search-bm25-vector-search/). Retrieval itself is rarely where the trouble lives. What bites you is retrieval failing silently, the vector search returning three plausible-but-wrong chunks, and the agent confidently building an answer on top of them.

**Multi-turn conversational agents** are the second major cluster. Holding state across a single conversation session is what sets them apart. They are retrieval-augmented underneath, plus a memory layer that tracks the conversation history and lets the agent reference earlier turns. Customer support bots and coding assistants dominate this category, and the [short-term-memory-for-ai-agents](/blog/short-term-memory-for-ai-agents/) post covers the mechanisms used in practice.

Context pollution is the failure I see most in this cluster. Every turn appends to the conversation context, and without active compression or windowing, the agent ends up reasoning over a bloated context stuffed with stale earlier turns. I have watched it happen in production: a customer support agent kept citing a refund the user had already received, because the resolved ticket from three turns back was still sitting in its context window, and it answered the next question as if nothing had been settled.

**Workflow orchestration agents** execute a defined sequence of steps, where each step might itself be an agent or a plain old program. With the workflow laid out upfront, the agent handles routing, error recovery, and conditional branching. Production is where the [plan-and-execute pattern](/blog/agent-loop-anatomy/) shows up most often in this shape: document processing pipelines, code review automation, and data transformation jobs.

Error handling here looks nothing like the single-loop case. A workflow agent that dies on step four of seven has to either checkpoint state or restart from a known good position, otherwise it re-runs steps one through three and you get duplicate side effects, like a payment fired twice. I wrote about [circuit breakers](/blog/production-ai-agent-errors/) as a pattern for stopping cascade failures in these systems. A circuit breaker barely earns its keep in a simple single-loop agent, yet it becomes load-bearing once you have a chain of steps that can drag each other down.

**Supervisor-delegation agents** split a task across several specialized agents, with a supervisor running the orchestration. The supervisor decides which sub-agent owns which part of the work, aggregates results, and resolves conflicts when two agents return contradictory answers. Of everything I saw in production, this was the most architecturally complex pattern.

The [supervisor-agent pattern](/blog/multi-agent-vs-single-agent-tradeoffs/) post goes into where this works and where it breaks. One failure deserves naming outright: supervisors rack up hidden coordination costs that teams routinely underestimate. Every sub-agent call adds latency and one more thing that can break, the way adding people to a meeting adds nothing to the output but multiplies the time spent getting everyone aligned. Parallelize those sub-agent calls and you hit the same challenges I covered in [parallel versus sequential tool calls](/blog/agent-loop-anatomy/). The speedups are real, and so is the new class of failures you just signed up for.

**Persistent-goal agents** run continuously, carry state across days or weeks, and chip away at goals that need many steps spread over many sessions. Of all the patterns, these look least like software and most like automated employees. Bug triage agents that watch an issue tracker, research synthesis agents that build up a report over a week, and monitoring agents all live here.

Durability is everything for this pattern, which is why the [agent-loop-anatomy](/blog/agent-loop-anatomy/) matters most. Every component of that loop has to survive a restart. Drop state when the process recycles overnight and the perceive-think-act cycle wakes up with no idea what it was working toward. Serve stale data from the memory layer and the agent reasons forward from premises that stopped being true days ago, like an employee who comes back from vacation and acts on a plan that was cancelled while they were out.

<div class="visual-wrapper">
  <div class="visual-title">THE DESIGN SPACE MAP</div>
  <div class="visual-container">
    <iframe src="/static/visuals/agent-design-space-map.html" title="A 2D design-space map plotting the five production agent patterns by run frequency and blast radius" loading="lazy"></iframe>
  </div>
</div>

## What the production data shows

Across the implementations I surveyed, three things stood out.

**Most agents are simpler than the taxonomy suggests.** Useful as the five-type taxonomy I published last week is for classification, production agents rarely sit cleanly in one type. They are blends with a dominant pattern. The single most common agent I found is a retrieval-augmented single-loop agent with multi-turn conversational memory bolted on, a Type 2-3 hybrid that has no clean home in most taxonomies and yet shows up everywhere.

**The tool layer decides reliability more than the model does.** Teams with fragile agents almost always had a tool schema problem, not a model problem. The [tool schema design](/blog/structured-outputs-llms-json-mode-function-calling/) post covers this in depth, and the short version is that agents fall over when the tool interface is underspecified, when one tool returns errors as a 500 and another returns them as a cheerful 200 with an error string in the body, and when the agent has no defined way to retry a failed call.

**Observability is the biggest blind spot.** Right behind tool schema problems, the second most common production failure was teams having no way to see what their agent was doing mid-execution. A minimum viable observability layer earns its place fast here. Basic logging was common in the teams I surveyed, but structured tracing of agent decisions was not, neither was the ability to replay a specific decision path or attribute cost to a single agentic action.

## Where agents are not being built

Clear blind spots showed up in the survey too, areas where the demand exists but production-grade implementations stay rare.

**Cross-agent state synchronization** is the piece nobody has nailed. When several agents need to share state in real time, teams reach for shared databases or message queues, yet no established pattern exists for doing it without bolting the agents tightly together. The post on [message passing between agents](/blog/multi-agent-vs-single-agent-tradeoffs/) covers what does exist, and most of it still demands a pile of custom plumbing.

**Agent regression testing** barely exists. Agents get tested the way teams test ordinary software: unit tests for functions, integration tests for APIs. An agent that sails through every unit test can still blow up in production the moment it meets an input shape it never saw in CI, such as a user pasting a 40-page PDF into a chat that the test suite only ever fed one-line questions. The post on [agent and RAG evaluation frameworks](/blog/rag-evaluation-metrics-what-actually-matters/) covers the eval frameworks that come closest to closing this.

**Structured output reliability** from agents is still unsolved. Agents that must emit structured JSON or hit specific action schemas fail at higher rates than agents that just produce freeform text. The cause is rarely raw model capability and almost always prompt and schema design, which I dug into in [structured-outputs-llms-json-mode-function-calling](/blog/structured-outputs-llms-json-mode-function-calling/).

## The design space is not a menu

After all this surveying, the point I keep coming back to is that the design space is not a menu where you pick the most impressive pattern. These patterns exist because the constraints that produce them are real.

A reactive information agent is not a watered-down persistent-goal agent. It is the correct architecture for a bounded task where failure is cheap and nothing needs to persist between runs. Picking a simpler pattern is not the mistake. Picking a simpler pattern and then stretching it past its intended scope is, like turning a single-loop docs assistant into something you expect to track a multi-day migration on its own.

Sketching a new agent system, I start with the [three questions in the taxonomy post](/blog/the-taxonomy-of-ai-agents/). Does it need to act or just generate? Does it need to persist state? Does the task complexity genuinely call for multiple agents? Those three questions narrow the design space faster than any framework diagram.

The [agent-harnesses](/blog/agent-harnesses/) post covers the runtime layer that sits beneath whatever pattern you choose. Whatever architecture you land on, the harness is where reliability gets built or lost.
