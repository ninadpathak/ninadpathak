---
title: "A Taxonomy of AI Agents That Actually Explains What You Are Building"
date: 2026-04-21
slug: "the-taxonomy-of-ai-agents"
description: "Most AI agent taxonomies are either too academic or too vague to be useful. Here is the classification I use when I need to decide what kind of agent to build."
tags: [ai, agents, architecture]
status: published
---

Every few months someone publishes a new taxonomy of AI agents. The diagrams look clean. The categories feel comprehensive. Then you try to use one to decide whether your customer support bot should use a single-agent loop or a multi-agent hierarchy, and the taxonomy dissolves into hand-waving.

I have spent the last year building agents for production use cases, reading the research papers that vendors cite selectively, and talking to teams whose agents either work reliably or fail in ways that are hard to debug. What I keep coming back to is a simpler classification scheme: one based on the **degree of autonomy**, the **task type**, and the **operational scope**.

These three dimensions separate the agents that belong in your production pipeline from the ones that will generate expensive surprises.

## The three dimensions

**Autonomy** answers the question: how many decisions does this agent make without a human in the loop? A fully autonomous agent plans and executes a sequence of actions to reach a goal. A guided agent picks the next action from a fixed menu. A reactive agent responds to a single input with a single output. The difference in cost and risk between these three modes is an order of magnitude.

**Task type** separates agents that retrieve and synthesize information from agents that take actions in external systems. Information agents answer questions, summarize documents, and generate content. Action agents modify state: they book meetings, send emails, update records, or trigger deployments. Most production agents do both, but the ratio matters for how you design the tool layer.

**Operational scope** determines whether the agent handles a single session or persists state across multiple interactions. A stateless agent treats every request as independent. A stateful agent maintains memory of past interactions within a conversation or across conversations. I wrote about why this distinction matters in practice in my post on [state-of-ai-agent-memory-2026](/blog/state-of-ai-agent-memory-2026/).

<div class="visual-wrapper">
  <div class="visual-title">AGENT TYPES BY AUTONOMY</div>
  <div class="visual-container">
    <iframe src="/static/visuals/agent-taxonomy.html" title="The five agent types arranged as a ladder by degree of autonomy" loading="lazy"></iframe>
  </div>
</div>

## Type 1: Reactive information agents

These are the simplest agents. You send a prompt, the model generates a response. The only autonomy involved is the model's internal reasoning about which words to produce next.

Most chatbots and assistants you see in production today are reactive information agents. They do not maintain state between calls. They do not use tools unless the tool call is part of the single request-response cycle. The [agentic-cli-benchmarks](/blog/agentic-cli-benchmarks/) I published last month tested two agents in this category.

The failure mode for reactive agents is straightforward: they hallucinate or produce generic responses when the answer is not in their training data. Retrieval augmentation helps, but at that point you are halfway to a more complex architecture.

## Type 2: Tool-using agents

The next step up is an agent that can call external tools during a single interaction. The model decides which tool to call based on the input, the tool returns results, and the model incorporates those results into its final response.

The critical design element here is the tool schema. I keep seeing teams treat tool schema design as an afterthought, which is why tool calls fail in production. The schema defines what the agent can do. If it is underspecified, the agent makes poor tool choices. If it is overspecified, the agent second-guesses itself and calls the wrong tool anyway. I have a whole post on [structured outputs and function-calling schemas](/blog/structured-outputs-llms-json-mode-function-calling/) that goes into this.

The [model-context-protocol-explained](/blog/model-context-protocol-explained/) post covers how standardized tool schemas change the agent-to-tool interface. When your tool schemas are consistent, swapping tools or adding new ones stops being a fragile operation.

## Type 3: Loop agents

Loop agents go beyond single request-response. They run a planning or action loop that iterates until a stopping condition is met. The [agent-loop-anatomy](/blog/agent-loop-anatomy/) post breaks down what happens inside that loop: perceive, think, act, remember.

The most common implementation is a ReAct-style loop: the agent reasons about the current state, takes an action, observes the result, and repeats. This is where agents start being agents rather than sophisticated autocomplete.

The failure modes change here. A reactive agent produces a bad answer. A loop agent can produce a bad answer and then spend tokens pursuing that bad answer further. I documented the production errors I keep seeing in [production-ai-agent-errors](/blog/production-ai-agent-errors/), and tool-use failures in loop agents are a recurring theme in that data.

## Type 4: Multi-agent systems

The taxonomy gets interesting at the multi-agent level. Multiple agents coordinate, either through shared state or message passing, to handle tasks that are too complex for a single agent to handle reliably.

I compared the trade-offs of multi-agent versus single-agent architectures in [multi-agent versus single-agent architectures](/blog/multi-agent-vs-single-agent-tradeoffs/). The short version: multi-agent systems can handle more complex tasks, but they introduce coordination overhead and failure modes that are harder to debug.

The most common pattern I see in production is a supervisor agent that delegates sub-tasks to specialized agents. The supervisor-agent pattern covers where this works and where it breaks down.

## Type 5: Persistent-goal agents

The most autonomous category. These agents maintain a long-running goal and work toward it across multiple sessions, potentially over days or weeks. They checkpoint their state, resume after interruptions, and adapt their plan based on new information.

This is where the memory stack becomes critical, and where most teams underestimate the complexity. I covered the [memory-hierarchy-in-ai-systems](/blog/memory-hierarchy-in-ai-systems/) that underpins this in an earlier post. Without the right memory architecture, persistent-goal agents either forget what they were doing or carry stale state that corrupts future decisions.

## Why the taxonomy matters for your architecture decision

When someone asks me whether they should build an agent, I start by asking what they mean by agent. A Slack bot that responds to slash commands with LLM-generated text is a reactive information agent. It does not need a tool layer, a memory stack, or a loop architecture. Building all of that for a reactive use case is overengineering.

The mistakes flow both directions. Teams that build a reactive chatbot and call it an agent will hit a wall when they need it to take actions across sessions. Teams that overengineer a multi-agent supervisor architecture for a use case that fits in a single tool-using loop will spend months debugging coordination failures that did not need to exist.

The [agent-design-space](/blog/the-agent-design-space/) survey I published covers what engineers are actually building across these categories. The data shows that most production deployments cluster in Types 2 and 3, with Type 4 reserved for the more complex workflows.

## The taxonomy I actually use

When I am sketching out a new agent system, I ask three questions in order:

1. Does this agent need to take actions or just generate information? If it only generates text, a reactive or tool-using agent probably suffices.
2. Does this agent need to maintain state across multiple interactions? If yes, you are now in the memory design business.
3. Does the task complexity require multiple specialized agents working together? If yes, you are taking on multi-agent coordination costs that need to be justified by the task complexity.

These three questions will sort most agent designs into one of the five types. The taxonomy is not perfect, and there are hybrid cases that do not fit cleanly. But it is a more useful frame than the category sprawl you see in most vendor documentation.

If you want to go deeper on the architectural patterns that hold these agent types together, the [agent-harnesses](/blog/agent-harnesses/) post covers what actually ties an AI agent together in production.
