---
title: "A Taxonomy of AI Agents That Actually Explains What You Are Building"
date: 2026-04-21
slug: "the-taxonomy-of-ai-agents"
description: "Most AI agent taxonomies are either too academic or too vague to be useful. Here is the classification I use when I need to decide what kind of agent to build."
tags: [ai, agents, architecture]
status: published
---

Every few months someone publishes a new taxonomy of AI agents. The diagrams look clean, the categories feel comprehensive, and then you try to use one to decide whether your customer support bot should run a single-agent loop or a multi-agent hierarchy, and the taxonomy dissolves into hand-waving.

Having spent the last year building agents for production, reading the research papers that vendors cite selectively, and talking to teams whose agents either work reliably or fail in ways nobody can debug, I keep coming back to a simpler classification scheme. I sort agents by the **degree of autonomy**, the **task type**, and the **operational scope**.

Those three dimensions separate the agents that belong in your production pipeline from the ones that will page you at midnight because they mass-emailed your customer list.

## The three dimensions

**Autonomy** answers one question: how many decisions does this agent make without a human in the loop? A fully autonomous agent plans and executes a sequence of actions to reach a goal. A guided agent picks the next action from a fixed menu, the way a phone tree routes you to a department. A reactive agent responds to a single input with a single output. Cost and blast radius climb by roughly an order of magnitude at each step, because a reactive agent can only give a bad answer, and an autonomous one can give a bad answer and then act on it ten times.

Take an agent that retrieves and synthesizes information, and set it next to one that takes actions in external systems. That split is what **task type** captures. Information agents answer questions, summarize documents, and generate content. Action agents modify state: they book meetings, send emails, update records, or trigger a deployment. Production agents usually do both, and the ratio drives how much care the tool layer needs. A summarizer that occasionally calls one read-only search tool is a different animal from a sales agent that writes to your CRM.

Whether the agent handles a single session or carries state across many interactions is the question **operational scope** answers. A stateless agent treats every request as independent, like a calculator that forgets the previous sum. A stateful agent maintains memory of past interactions, within a conversation or across them. Why that distinction matters in practice is something I covered in my post on [state-of-ai-agent-memory-2026](/blog/state-of-ai-agent-memory-2026/).

<div class="visual-wrapper">
  <div class="visual-title">AGENT TYPES BY AUTONOMY</div>
  <div class="visual-container">
    <iframe src="/static/visuals/agent-taxonomy.html" title="The five agent types arranged as a ladder by degree of autonomy" loading="lazy"></iframe>
  </div>
</div>

## Type 1: Reactive information agents

These are the simplest agents. You send a prompt, the model generates a response, and the only autonomy involved is the model's internal reasoning about which words to produce next.

Plenty of chatbots and assistants you see in production today are reactive information agents. They hold no state between calls, and they reach for no tools unless the tool call rides inside that single request-response cycle. A docs Q&A box that answers from whatever you pasted into the prompt and nothing else is the canonical case. The [agentic-cli-benchmarks](/blog/agentic-cli-benchmarks/) I published last month tested two agents in this category.

Their failure mode is easy to spot: they hallucinate or produce generic filler when the answer was never in their training data, so a question about your internal pricing tiers gets you a confident, wrong number. Retrieval augmentation helps, and once you bolt it on you are halfway to a more complex architecture anyway.

## Type 2: Tool-using agents

One step up sits an agent that can call external tools during a single interaction. The model decides which tool to call based on the input, the tool returns results, and the model folds those results into its final response. Ask "what's the weather in Lisbon," it calls a weather lookup, and it answers with the number that came back instead of inventing one.

What makes or breaks this type is the tool schema. I keep seeing teams treat schema design as an afterthought, then wonder why tool calls fail in production. The schema is the agent's job description. Underspecify it and the agent makes poor tool choices, the way a contractor handed "fix the kitchen" might rewire an outlet you never asked about. Overspecify it with twenty near-identical tools and the agent second-guesses itself and calls the wrong one anyway. My post on [structured outputs and function-calling schemas](/blog/structured-outputs-llms-json-mode-function-calling/) digs into exactly this.

The [model-context-protocol-explained](/blog/model-context-protocol-explained/) post covers how standardized tool schemas change the agent-to-tool interface. When your tool schemas are consistent, swapping tools or adding new ones stops being a fragile operation.

## Type 3: Loop agents

Loop agents go past single request-response. They run a planning or action loop that iterates until a stopping condition is met. The [agent-loop-anatomy](/blog/agent-loop-anatomy/) post breaks down what happens inside that loop: perceive, think, act, remember.

Nearly every implementation I see is a ReAct-style loop: the agent reasons about the current state, takes an action, observes the result, and repeats. Watching an agent debug a failing test by reading the error, editing a line, rerunning, and reading the next error is the moment these stop being sophisticated autocomplete and start behaving like agents.

Failure modes get more expensive at this rung. A reactive agent produces a bad answer and stops. A loop agent can produce a bad answer and then burn fifty more iterations chasing it, like a GPS that missed a turn and keeps confidently recalculating you deeper into the wrong neighborhood. I documented the production errors I keep running into in [production-ai-agent-errors](/blog/production-ai-agent-errors/), where tool-use failures inside loop agents show up again and again.

## Type 4: Multi-agent systems

Things get interesting at the multi-agent level. Several agents coordinate, through shared state or message passing, to handle tasks too big for a single agent to handle reliably. A research agent gathers sources, a writer agent drafts from them, a critic agent flags weak claims, and a supervisor decides when the draft is done.

I compared the trade-offs of multi-agent against single-agent architectures in [multi-agent versus single-agent architectures](/blog/multi-agent-vs-single-agent-tradeoffs/). The short version: more agents buy you more task complexity at the price of coordination overhead and failure modes that are far harder to trace, since a wrong answer now has four places it could have originated.

A supervisor agent that delegates sub-tasks to specialized agents is the pattern I see most in production. The supervisor-agent setup covers where it works and where it breaks down.

## Type 5: Persistent-goal agents

The most autonomous category. These agents hold a long-running goal and work toward it across many sessions, sometimes over days or weeks. An agent assigned to "migrate this service off the deprecated payments API" might run for a week: opening pull requests, waiting on CI, and picking the work back up the next morning. They checkpoint their state, resume after interruptions, and adapt the plan as new information arrives.

Memory stops being optional here, and it is where most teams underestimate the complexity. The [memory-hierarchy-in-ai-systems](/blog/memory-hierarchy-in-ai-systems/) that underpins this got its own earlier post. Get the memory architecture wrong and persistent-goal agents either forget what they were doing or drag stale state forward that corrupts every later decision, like resuming a migration against a schema that changed two days ago.

## Why the taxonomy matters for your architecture decision

When someone asks me whether they should build an agent, I start by asking what they mean by agent. A Slack bot that answers slash commands with LLM-generated text is a reactive information agent. It needs no tool layer, no memory stack, no loop architecture. Building all of that for a reactive use case is overengineering, like pouring a foundation for a tool shed.

Mistakes run in both directions. Teams that ship a reactive chatbot and call it an agent hit a wall the day a stakeholder asks it to actually book the meeting it keeps describing. Teams that reach for a multi-agent supervisor architecture when the job fits in a single tool-using loop spend months debugging coordination failures that never needed to exist.

My [agent-design-space](/blog/the-agent-design-space/) survey covers what engineers are actually building across these categories. The data shows production deployments clustering in Types 2 and 3, with Type 4 held back for the genuinely complex workflows.

## The taxonomy I actually use

When I am sketching out a new agent system, I ask three questions in order:

1. Does this agent need to take actions or just generate information? When it only generates text, a reactive or tool-using agent probably suffices.
2. Does this agent need to maintain state across multiple interactions? A yes drops you straight into the memory design business.
3. Does the task complexity genuinely require multiple specialized agents working together? A yes means signing up for multi-agent coordination costs that the task had better justify.

Those three questions sort most agent designs into one of the five types. The taxonomy is not perfect, and hybrid cases refuse to sit cleanly in one box. As a working frame, though, it beats the category sprawl you find in most vendor documentation.

If you want to go deeper on the architectural patterns that hold these agent types together, the [agent-harnesses](/blog/agent-harnesses/) post covers what actually ties an AI agent together in production.
