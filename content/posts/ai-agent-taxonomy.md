---
category: ai-agents
primary_query: types of ai agents
siblings:
- model-context-protocol
- agent-loop-anatomy
- agent-error-handling
bridges:
- slug: agent-memory-2026
  reason: Remembering is a step in the agent loop, and the memory hub covers it in full.
- slug: claude-vs-gemini-cli
  reason: A coding agent is the agent a developer uses daily.
- slug: llm-structured-outputs
  reason: Each turn of the agent loop spends tokens and latency.
- slug: ai-memory-management
  reason: Remembering is a step in the agent loop, and the memory hub covers it in full.
date: 2026-04-21
description: 'Types of AI agents sorted by how much each decides without a person, from reactive to persistent-goal, set against the textbook classes and Anthropic''s split.'
slug: ai-agent-taxonomy
status: published
work_note: 'I group agents on this page by how much they decide alone, because that decides which tools and memory a task needs. For the agent guides I''ve written for Firecrawl, see [my portfolio](/portfolio/).'
title: 'Types of AI Agents: Five Types by Autonomy and Scope'
video: ai-agent-taxonomy
updated: 2026-11-17
---

Tesla sells a feature called Full Self-Driving, and [Wikipedia's article on self-driving cars](https://en.wikipedia.org/wiki/Self-driving_car), as it read on November 17, files it as a "Level 2 (hands/on, eyes/on)" system. Waymo's robotaxis sit two levels higher, because the SAE levels rank a system by how much of the driving a human still has to do and say nothing about how clever the software is.

Types of AI agents sort the same way. The question that separates them is how much an agent decides and does before a person looks, and by that measure there are five types, set out in the table below.

The parallel breaks in one place. A car's level is fixed when the feature ships, and an agent's type is set by configuration, so one model can answer a single question in one deployment and work unattended for a week in another.

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

The textbook answer to the same question is a different five. Wikipedia's [article on intelligent agents](https://en.wikipedia.org/wiki/Intelligent_agent) gives the source: "Russell & Norvig (2003) group agents into five classes based on their degree of perceived intelligence and capability".

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

Both lines fall in the same place, between the tool-using type and the loop, and I agree that it is the largest step on the ladder.

I keep the two rungs below it because the word is used well below that line. United Airlines, quoted in the next section, bans "personal AI agents or assistants" as one group.

I also think one line is too few for a build decision. Anthropic's post treats several agents under an orchestrator as a workflow pattern, and it has no rung for an agent that keeps a goal across sessions, though each of those adds a failure the single loop doesn't have.

## Reading and acting are separate risks

On November 11 United Airlines said it was banning AI agents from booking flights for travellers, as [CBS News reported](https://www.cbsnews.com/news/united-airlines-bans-ai-agents-booking-flights/). The airline's statement names what it objects to: "actions taken by these tools may result in unintended purchases, account changes, or use of MileagePlus miles."

Everything in that sentence is a write. An agent that compares fares and an agent that buys the ticket can be the same type on the ladder, and only the second can spend the customer's money.

The same report cuts against a clean split. It quotes an aviation analyst saying "Flight searches cost airlines money", so a read-only agent still costs the system it reads from, and the [Hacker News thread](https://news.ycombinator.com/item?id=50458900) on the ban ran to more than 700 comments.

So each type carries a second label, read-only or acting. A third label says whether the agent keeps state between requests, and [context windows vs memory](/articles/context-windows-vs-memory/) explains what that state is.

## What each type adds

Each rung keeps the failures of the rungs below it and adds one of its own.

### Type 1: reactive

A prompt goes in and a reply comes out, with nothing kept between calls. The only thing that can go wrong is the answer, which makes this the type to choose whenever it does the job.

### Type 2: tool-using

The model picks a tool and fills in its arguments, the tool runs, and the model writes its reply from the result. The tool definitions decide what the model can choose from, and [structured outputs](/articles/llm-structured-outputs/) are how the arguments are kept to a schema.

A shared format for those definitions is what the [Model Context Protocol](/articles/model-context-protocol/) provides.

### Type 3: loop

The agent acts, reads the result and decides again, until it judges the goal met or hits a limit. Anthropic's post puts the cost in one sentence: "The autonomous nature of agents means higher costs, and the potential for compounding errors."

The [anatomy of an agent loop](/articles/agent-loop-anatomy/) walks through one pass, and [error handling for agents](/articles/agent-error-handling/) covers what to do when a step inside it fails.

### Type 4: multi-agent

Several agents share one task, passing messages or working from shared state. Coordination becomes a cost of its own, and the comparison of [multi-agent and single-agent systems](/articles/multi-agent-vs-single-agent/) is about when that cost pays for itself.

### Type 5: persistent-goal

The agent holds a goal across sessions, saves its progress and resumes after an interruption. It depends on memory more than any other type, since a resumed run acts on whatever the last run wrote down, and [AI memory management](/articles/ai-memory-management/) describes the layers that state sits in.

## Which type does a task need?

Choose the lowest type that does the job. Anthropic's post gives the same advice for the whole field: "we recommend finding the simplest solution possible, and only increasing complexity when needed."

The questions below place a task on the ladder.

1. Does it need information the model doesn't have, or an action in another system? If so it is at least type 2, and the acting label applies when a tool writes.
2. Can the number of steps be fixed in advance? If it can't, the task needs a loop.
3. Does the work outlast one session? If it does, the agent needs stored state and belongs at type 5.

Type 4 has no question of its own, because a second agent is a way to carry out a task and never a requirement of one. Add it when a single loop has been tried and measured.

The ladder sorts agents by how much they decide alone. How to wire a chosen type is the subject of [AI agent design patterns](/articles/agent-design-space/), where an [AI agent stops and an AI assistant begins](/articles/agent-vs-ai-assistant/) has a page of its own, and [agent harnesses](/articles/agent-harnesses/) covers the code around the model.

## FAQ

**What are the main types of AI agents?**

The textbook answer is Russell and Norvig's five classes, from simple reflex agents to learning agents. For agents built on language models a more practical list sorts by autonomy: reactive, tool-using, loop, multi-agent and persistent-goal.

**Is a chatbot an AI agent?**

By Simon Willison's definition it isn't, since it runs no tools in a loop. I count it as type 1 because the word is applied to such products anyway.

**What is the difference between a workflow and an agent?**

In Anthropic's terms a workflow follows code paths written in advance, and an agent directs its own steps. The split matters for testing, since a fixed path can be checked step by step.
