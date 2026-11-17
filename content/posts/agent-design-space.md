---
category: ai-agents
primary_query: ai agent design patterns
siblings:
- ai-agent-taxonomy
- multi-agent-vs-single-agent
- agent-loop-anatomy
date: 2026-04-26
description: 'AI agent design patterns from chaining to the autonomous agent, set beside a second list that adds the blackboard, and a grid for placing any pattern.'
slug: agent-design-space
status: published
work_note: "I'm Ninad Pathak, a freelance technical writer. If your AI product's tutorials have fallen behind the product, I write them, and I run the product first. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'AI Agent Design Patterns'
updated: 2026-11-17
---

AI agent design patterns are the named ways to arrange model calls, tools and control flow into a working system. The list people cite comes from Anthropic's [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) of December 19, 2024, which describes five workflows and the autonomous agent.

[Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns), the 1994 book by the authors known as the Gang of Four, described 23 patterns, and what lasted from it was the shared vocabulary.

The agent lists are thirty years younger and don't yet agree with each other. Choosing among them is the wiring decision in [AI agent architecture](/articles/ai-agents/), and it comes after deciding how much the agent does alone.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-design-space/design-space-map.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-design-space/design-space-map.narrow.svg" width="288" height="472"><img class="np-has-narrow" src="/static/images/diagrams/agent-design-space/design-space-map.svg" width="720" height="288" alt="Agent design patterns grouped by who directs the steps. Prompt chaining, routing and parallelization run on paths fixed in code. In orchestrator-workers and evaluator-optimizer a model decides part of the path. In the autonomous agent the model directs every step." loading="lazy" decoding="async"></picture></a>
  <figcaption>Anthropic's six patterns in my grouping, from paths fixed in code on the left to a model directing every step on the right.</figcaption>
</figure>

## What are the AI agent design patterns?

Anthropic's post names six.

| Pattern | What it does |
| --- | --- |
| Prompt chaining | Splits a task into steps, and each model call works on the output of the one before. |
| Routing | Classifies the input and sends it to a prompt built for that kind. |
| Parallelization | Runs several model calls at once and combines their outputs in code. |
| Orchestrator-workers | Has one model break the task down, hand the parts to worker models and merge what comes back. |
| Evaluator-optimizer | Has one model write an answer and another critique it, in a loop. |
| Autonomous agent | Lets the model direct its own process and choose its own tools. |

The post files the first five under workflows, where "LLMs and tools are orchestrated through predefined code paths", and keeps the word agent for the last. It carries a note that the tooling it describes has changed since 2024, and the pattern names have outlived the tooling.

## Do other lists agree?

Partly. Kadharmoideen Fadurudeen's [guide to multi-agent patterns](https://kadhar.dev/blog/multi-agent-systems-from-scratch), published in June and discussed on Hacker News in early November, has three: pipeline, orchestrator and blackboard.

The first two map onto prompt chaining and orchestrator-workers. The third has no row in Anthropic's table, and the guide sums it up as "There's no boss."

In a blackboard design the agents share a board: each reads what's there, adds what it knows and steps in when it has something to offer. Nothing in Anthropic's six shares state that way, since each of them passes work along a path.

So the lists differ in length and in what they count. I find two questions sort every pattern on both of them.

| | Steps share only what is passed along | Steps share a common store |
| --- | --- | --- |
| Code decides the next step | Chaining, routing, parallelization | A pipeline writing to shared state |
| A model decides the next step | Orchestrator-workers, evaluator-optimizer, autonomous agent | Blackboard |

The grid is mine and neither source draws it. Its use is that a new pattern name can be placed by asking who decides the next step and what the steps share.

## How do you choose a pattern?

Start from the top-left cell and move only when the task forces it. A path fixed in code can be tested step by step, and every move toward the model trades that for flexibility.

So when do you move? Anthropic's post says to reach for orchestrator-workers when you can't predict the subtasks in advance, and for evaluator-optimizer when you have "clear evaluation criteria".

That second condition is stricter than it sounds. The clearest criteria are ones a program can check, which is why my [lambda calculus exercise](/articles/lambda-calculus-ai/) grades answers with a script.

A pattern is a separate choice from a type. My guide to the [types of AI agents](/articles/ai-agent-taxonomy/) ranks systems by how much they decide alone, and [AI agent vs AI assistant](/articles/agent-vs-ai-assistant/) covers the line below which no loop is needed at all.

## Where do the patterns break?

At the joins. A chain fails when one step's output isn't what the next expects, and an orchestrator fails when a worker misreads its brief, the handoff problem described in [multi-agent vs single-agent systems](/articles/multi-agent-vs-single-agent/).

A loop adds a failure of its own, which is never knowing when to stop. The [anatomy of an agent loop](/articles/agent-loop-anatomy/) goes through one pass, and [error handling for agents](/articles/agent-error-handling/) covers what the code around the loop has to decide.

And shared state fails differently again. A pair of agents writing to one board can overwrite each other, and the board needs the rules any shared store needs.

## FAQ

**What are the main AI agent design patterns?**

Anthropic's 2024 list has prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer and the autonomous agent. Other lists add a shared-state pattern called the blackboard.

**What is the difference between a workflow and an agent pattern?**

A workflow has code fix the path between model calls. An agent pattern leaves the next step to the model.

**Which agent design pattern should I start with?**

The one that fixes as much as possible in code and still does the job, which is often a chain or a router.
