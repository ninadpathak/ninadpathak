---
category: ai-agents
primary_query: ai agent design patterns
siblings:
- ai-agent-taxonomy
- multi-agent-vs-single-agent
- agent-loop-anatomy
date: 2026-04-26
description: "AI agent design patterns are the named ways to arrange model calls and tools. This page sets Anthropic's six beside a second list that adds the blackboard pattern, and gives a two-question grid for placing any pattern."
slug: agent-design-space
status: published
work_note: "I'm Ninad Pathak, a freelance technical writer. If your AI product's tutorials have fallen behind the product, I write them, and I run the product first. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'AI Agent Design Patterns'
updated: 2026-11-17
---

AI agent design patterns are the named ways to arrange model calls, tools and control flow into a working system. The list people cite comes from Anthropic's [Building effective agents](https://www.anthropic.com/research/building-effective-agents) of December 19, 2024, which describes five workflows and the autonomous agent.

[Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns), the 1994 book by the authors known as the Gang of Four, described 23 patterns, and what lasted from it was the vocabulary, since programmers still say singleton and observer without explaining either.

The lists of agent patterns are thirty years younger and don't yet agree with each other. Choosing a pattern decides how the model calls connect, and in [AI agent architecture](/articles/ai-agents/) that choice comes after deciding how much the agent does alone.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-design-space/design-space-map.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-design-space/design-space-map.narrow.svg" width="288" height="472"><img class="np-has-narrow" src="/static/images/diagrams/agent-design-space/design-space-map.svg" width="720" height="288" alt="Agent design patterns grouped by who directs the steps. Prompt chaining, routing and parallelization run on paths fixed in code. In orchestrator-workers and evaluator-optimizer a model decides part of the path. In the autonomous agent the model directs every step." loading="lazy" decoding="async"></picture></a>
  <figcaption>Anthropic's six patterns in my grouping, from paths fixed in code on the left to a model directing every step on the right.</figcaption>
</figure>

## What are the AI agent design patterns?

Anthropic's post names six patterns.

| Pattern | What it does |
| --- | --- |
| Prompt chaining | Splits a task into steps, and each model call works on the output of the one before. |
| Routing | Classifies the input and sends it to a prompt built for that kind. |
| Parallelization | Runs several model calls at once and combines their outputs in code. |
| Orchestrator-workers | Has one model break the task down, hand the parts to worker models and merge what comes back. |
| Evaluator-optimizer | Has one model write an answer and another critique it, in a loop. |
| Autonomous agent | Lets the model direct its own process and choose its own tools. |

The post files the first five under workflows, where "LLMs and tools are orchestrated through predefined code paths", and keeps the word agent for the last. The post carries a note that the tooling it describes has changed since 2024, and the pattern names have outlived that tooling.

## Do other lists agree?

Other lists agree in part. Kadharmoideen Fadurudeen's [guide to multi-agent patterns](https://kadhar.dev/blog/multi-agent-systems-from-scratch), published in June and discussed on Hacker News in early November, has three: pipeline, orchestrator and blackboard.

Pipeline maps onto prompt chaining, and orchestrator maps onto orchestrator-workers. The blackboard has no row in Anthropic's table, and the guide sums it up as "There's no boss."

In a blackboard design the agents share one store, the board, say a single JSON document: each agent reads the board, adds what it knows and acts when it has something to offer. None of Anthropic's six patterns shares state that way, since each passes work from one call to the next.

So the two lists differ in length, and only Fadurudeen's has a pattern built on shared state. I sort every pattern on both lists with two questions: does code or a model decide the next step, and do the steps share a common store?

| | Steps share only what is passed along | Steps share a common store |
| --- | --- | --- |
| Code decides the next step | Chaining, routing, parallelization | A pipeline writing to shared state |
| A model decides the next step | Orchestrator-workers, evaluator-optimizer, autonomous agent | Blackboard |

The grid is mine and neither source draws it. When a new pattern name turns up, I'd place it by asking the same two questions.

## How do you choose a pattern?

Start with chaining, routing or parallelization, where code decides each step, and move only when the task forces it. A path fixed in code can be tested one step at a time, and each decision you hand to the model gives up some of that testing in exchange for flexibility.

So when do you move? Anthropic's post says to reach for orchestrator-workers when you can't predict the subtasks in advance, and for evaluator-optimizer when you have "clear evaluation criteria".

The clearest evaluation criteria are ones a program can check, such as a test that passes or fails, which is why my [lambda calculus exercise](/articles/lambda-calculus-ai/) grades answers with a script.

Choosing a pattern is separate from choosing a type of agent. My guide to the [types of AI agents](/articles/ai-agent-taxonomy/) ranks systems by how much they decide alone, and [AI agent vs AI assistant](/articles/agent-vs-ai-assistant/) covers the cases where a person picks each next step and no loop is needed.

## Where do the patterns break?

The patterns break at the handoffs between calls. A chain fails when one step's output isn't what the next step expects, and an orchestrator fails when a worker misreads the task it was handed, the handoff problem described in [multi-agent vs single-agent systems](/articles/multi-agent-vs-single-agent/).

A loop adds a failure of its own, which is never knowing when to stop. The [anatomy of an agent loop](/articles/agent-loop-anatomy/) goes through one pass, and [error handling for agents](/articles/agent-error-handling/) covers how the code around the loop classifies a tool error and whether a failed call is safe to repeat.

Shared state fails when two agents write to one board and one overwrites the other. So the board needs what any shared store needs: a rule for who may write, and a version check on each write.

## FAQ

**What are the main AI agent design patterns?**

Anthropic's 2024 list has prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer and the autonomous agent. Other lists add a shared-state pattern called the blackboard.

**What is the difference between a workflow and an agent pattern?**

A workflow's code fixes the path between model calls. An agent pattern lets the model choose the next step.

**Which agent design pattern should I start with?**

Start with the pattern that fixes as much as possible in code and still does the job, which is often a chain or a router.
