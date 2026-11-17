---
category: ai-agents
primary_query: types of ai agents
siblings:
- model-context-protocol
- agent-loop-anatomy
- agent-error-handling
bridges:
- slug: context-windows-vs-memory
  reason: The stateful label on an agent type depends on what counts as kept state, which that page defines.
- slug: llm-structured-outputs
  reason: Structured outputs keep the arguments of a tool call to a schema.
- slug: ai-memory-management
  reason: Remembering is a step in the agent loop, and the memory hub covers it in full.
date: 2026-04-21
description: 'Types of AI agents sorted by how much each decides without a person, from reactive to persistent-goal, set against the textbook classes and Anthropic''s split.'
slug: ai-agent-taxonomy
status: published
work_note: "I'm Ninad Pathak. AI companies hire me as a freelance technical writer for setup tutorials, concept explainers and comparisons, and I run each product before I write about it. [See the work and get in touch](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Types of AI Agents: Five Types by Autonomy and Scope'
updated: 2026-11-17
---

Tesla sells a feature called Full Self-Driving, and [Wikipedia's article on self-driving cars](https://en.wikipedia.org/wiki/Self-driving_car), as it read on November 17, files it as a "Level 2 (hands/on, eyes/on)" system. Waymo's robotaxis sit two levels higher, because the SAE levels, published in 2014, rank a system by how much of the driving a human still has to do and say nothing about how clever the software is.

Types of AI agents can be ranked by how much an agent decides and does before a person looks. The first two are reactive and tool-using agents, and above them come loop agents and multi-agent systems, with persistent-goal agents at the top.

A car's level changes rarely, though the article records Mercedes withdrawing its Level 3 feature in January 2026. An agent's type is a configuration, so one model can answer a single question in one deployment and work unattended for a week in another.

That makes the type a decision in [AI agent architecture](/articles/ai-agents/), made per deployment, and the table sets out what each one decides alone.

| Type | What it decides alone | Labelled example | Failure it adds |
| --- | --- | --- | --- |
| 1. Reactive | The words of one reply | A docs question box that answers from the text pasted into its prompt | A wrong answer |
| 2. Tool-using | Which tool to call, and with what arguments, inside one request | A weather question answered with a lookup | A wrong call |
| 3. Loop | How many steps to take and when to stop | A coding agent that reruns a failing test until it passes | Errors that build on each other |
| 4. Multi-agent | How to split the work between agents | An orchestrator handing subtasks to workers | A fault with several possible origins |
| 5. Persistent-goal | What to do next across sessions and days | A service migration picked up again each morning | Decisions made on stale state |

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/ai-agent-taxonomy/agent-taxonomy.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/ai-agent-taxonomy/agent-taxonomy.narrow.svg" width="288" height="752"><img class="np-has-narrow" src="/static/images/diagrams/ai-agent-taxonomy/agent-taxonomy.svg" width="720" height="808" alt="A ladder of agent types by rising autonomy, from reactive at the bottom through tool-using, loop and multi-agent to persistent-goal at the top." loading="lazy" decoding="async"></picture></a>
  <figcaption>Each step up decides more without a person, and adds a failure the step below cannot have.</figcaption>
</figure>

## The textbook list answers a different question

Textbooks give a different five. Wikipedia's [article on intelligent agents](https://en.wikipedia.org/wiki/Intelligent_agent) gives the source: "Russell & Norvig (2003) group agents into five classes based on their degree of perceived intelligence and capability".

- Simple reflex agents
- Model-based reflex agents
- Goal-based agents
- Utility-based agents
- Learning agents

That list sorts agents by how they choose an action internally. An agent built on a language model leaves the choosing to the model at every rung, so I find the textbook classes of little use for deciding what to build.

A support chatbot and a coding agent can run on one model and differ only in what they are permitted to do. The five types on this page sort by that permission.

## Where Anthropic and Simon Willison draw the line

Anthropic's [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), published on December 19, 2024, splits the field in two. Workflows are "systems where LLMs and tools are orchestrated through predefined code paths", and agents are "systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks."

Simon Willison [settled on a definition](https://simonwillison.net/2025/Sep/18/agents/) on September 18, 2025: "An LLM agent runs tools in a loop to achieve a goal." Under his wording types 1 and 2 are no agents at all, and the word begins at the loop.

Willison's line falls between my tool-using type and the loop. Anthropic's cuts across the ladder, since it asks who directs the steps: the post files an orchestrator with workers under workflows, so a multi-agent system can sit on either side of it.

I agree with both that handing the loop to the model is the largest step. I keep the two rungs below it because the word is used well below that line, and United Airlines' ban covers "personal AI agents or assistants" as one group.

I also think one line is too few for a build decision. Neither definition has a rung for several agents sharing a task or for an agent that keeps a goal across sessions, and each of those adds a failure the single loop doesn't have.

## Reading and acting are separate risks

On November 11 United Airlines said it was banning AI agents from booking flights for travellers, as [CBS News reported](https://www.cbsnews.com/news/united-airlines-bans-ai-agents-booking-flights/). The airline's statement names what it objects to: "actions taken by these tools may result in unintended purchases, account changes, or use of MileagePlus miles."

Everything in that sentence is a write. An agent that compares fares and an agent that buys the ticket can be the same type on the ladder, and only the second can spend the customer's money.

The report also cuts against a clean split. It quotes an aviation analyst saying "Flight searches cost airlines money", so a read-only agent still costs the system it reads from, and the [Hacker News thread](https://news.ycombinator.com/item?id=50458900) on the ban ran to more than 700 comments.

So each type carries a second label, read-only or acting.

A third label, whether the agent keeps state between requests, applies below type 5 as well, since a tool-using assistant can remember a user's preferences without holding a goal. [Context windows vs memory](/articles/context-windows-vs-memory/) explains what that state is.

## What each type adds

Each rung keeps the failures of the rungs below it and adds one of its own.

### Type 1: reactive

A prompt goes in and a reply comes out, with nothing kept between calls. The only thing that can go wrong is the answer, which makes this the type to choose whenever it does the job.

### Type 2: tool-using

The model picks a tool and fills in its arguments, the tool runs, and the model writes its reply from the result. The tool definitions decide what the model can choose from, and [structured outputs](/articles/llm-structured-outputs/) are how the arguments are kept to a schema.

A shared format for those definitions is what the [Model Context Protocol](/articles/model-context-protocol/) provides, and the [MCP server tutorial](/articles/mcp-server-tutorial/) builds a two-tool server on it.

### Type 3: loop

The agent acts, reads the result and decides again, until it judges the goal met or hits a limit. Anthropic's post puts the cost in one sentence: "The autonomous nature of agents means higher costs, and the potential for compounding errors."

The [anatomy of an agent loop](/articles/agent-loop-anatomy/) walks through one pass, and [error handling for agents](/articles/agent-error-handling/) covers what to do when a step inside it fails.

### Type 4: multi-agent

Several agents share one task, passing messages or working from shared state. Coordination becomes a cost of its own, and the comparison of [multi-agent and single-agent systems](/articles/multi-agent-vs-single-agent/) is about when that cost pays for itself.

### Type 5: persistent-goal

The agent holds a goal across sessions, saves its progress and resumes after an interruption. It depends on memory more than any other type, since a resumed run acts on whatever the last run wrote down, and [AI memory management](/articles/ai-memory-management/) describes the layers that state sits in.

## Which type does a task need?

Choose the lowest type that does the job. Anthropic's post gives the same advice for the whole field: "we recommend finding the simplest solution possible, and only increasing complexity when needed."

1. Does it need information the model doesn't have, or an action in another system? If so it is at least type 2, and the acting label applies when a tool writes.
2. Can the number of steps be fixed in advance? If it can't, the task needs a loop.
3. Does the work outlast one session? If it does, the agent needs stored state and belongs at type 5.

Type 4 has no question of its own, because a second agent is a way to carry out a task and never a requirement of one. Add it when a single loop has been tried and measured.

The ladder sorts agents by how much they decide alone. How to wire a chosen type is the subject of [AI agent design patterns](/articles/agent-design-space/).

Where an agent ends and an assistant begins is argued in [AI agent vs AI assistant](/articles/agent-vs-ai-assistant/), and the code around the model is described in [agent harnesses](/articles/agent-harnesses/).

## FAQ

**What are the main types of AI agents?**

The textbook answer is Russell and Norvig's five classes, from simple reflex agents to learning agents. For agents built on language models a more practical list sorts by autonomy: reactive, tool-using, loop, multi-agent and persistent-goal.

**Is a chatbot an AI agent?**

By Simon Willison's definition it isn't, since it runs no tools in a loop. I count it as type 1 because the word is applied to such products anyway.

**What is the difference between a workflow and an agent?**

In Anthropic's terms a workflow follows code paths written in advance, and an agent directs its own steps. The split matters for testing, since a fixed path can be checked step by step.
