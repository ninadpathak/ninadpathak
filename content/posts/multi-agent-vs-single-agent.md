---
category: ai-agents
primary_query: multi agent systems
siblings:
- ai-agent-taxonomy
- ai-agent-failures
- agent-design-space
bridges:
- slug: claude-code-subagents
  reason: Claude Code's subagents return only a final report, the read-only split this page recommends.
- slug: shared-vs-isolated-memory
  reason: Several agents either share a store or keep their own, which that page decides.
date: '2026-04-27'
description: 'Multi-agent systems vs a single agent: what a second agent buys, what it costs in tokens, where handoffs break, and a test for when to split.'
slug: multi-agent-vs-single-agent
status: published
work_note: 'For Firecrawl I wrote about agent harnesses and agent tools, the parts an agent needs whether there is one or five. Whether a job needs more than one is the question here, and [those pieces are in my portfolio](/portfolio/).'
title: 'Multi-Agent vs Single-Agent Systems: The Real Trade-offs'
updated: 2026-11-17
---

Martin Fowler wrote [Monolith First](https://martinfowler.com/bliki/MonolithFirst.html) in June 2015, after watching teams adopt microservices. His observation was that "Almost all the successful microservice stories have started with a monolith that got too big and was broken up", and that systems built as microservices from scratch tended to end in trouble.

Multi-agent systems raise Fowler's question for agent builders. A multi-agent system is several model loops, each with its own context window and a narrower job, passing work between them, and a single-agent system is one loop that does everything.

Services exchange requests with fixed fields. Agents hand each other prose, so a misunderstanding between two agents has no schema to fail against, and that is the weak point in any [AI agent architecture](/articles/ai-agents/) with more than one agent in it.

## What does a second agent buy?

More context to think with, on work that splits cleanly. Anthropic's account of [its multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), published on June 13, 2025, reports that a lead agent with subagents "outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval."

The post's own explanation is about capacity. A separate analysis of a browsing benchmark in the post found that "token usage by itself explains 80% of the variance", and a system of agents spends more tokens because each one has a window to itself.

The eval is internal and the models in it date from 2025. I read the number as showing direction, and the mechanism behind it still applies: a subagent can read twenty pages and hand back a paragraph, which keeps the lead agent's window clear.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/multi-agent-vs-single-agent/agent-topology.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/multi-agent-vs-single-agent/agent-topology.narrow.svg" width="288" height="656"><img class="np-has-narrow" src="/static/images/diagrams/multi-agent-vs-single-agent/agent-topology.svg" width="720" height="488" alt="A single agent runs one loop with one trace. A multi-agent system puts a supervisor over three workers, each with its own memory and failure boundary, so they can run independent work in parallel, but every handoff between them is a message boundary where things can break in transit." loading="lazy" decoding="async"></picture></a>
  <figcaption>Parallel workers cut wall-clock time only when the work is independent, and every handoff adds a place to fail.</figcaption>
</figure>

## What does it cost?

Tokens first. The same post says "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats."

By that arithmetic a multi-agent run costs a little under four times a single-agent run of the same task. Anthropic's condition for paying it is that "the value of the task is high enough to pay for the increased performance."

Coordination is the second cost, and the post is plain about where the design doesn't fit: "some domains that require all agents to share the same context or involve many dependencies between agents are not a good fit for multi-agent systems today." It names coding as an example.

## Where do multi-agent systems break?

At the handoff, where one agent acts on a guess about what another meant. Walden Yan of Cognition made the case in [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) on June 12, 2025, a day before Anthropic's post.

His example is a task to clone Flappy Bird, split between a subagent building the background and one building the bird. The first returns a background in the style of a different game, the second a bird that doesn't match, and a final agent is left to combine what he calls "these two miscommunications."

The rule he draws from it is "Actions carry implicit decisions, and conflicting decisions carry bad results". Each subagent made choices nobody wrote down, and the choices didn't agree.

His other rule is about what to pass along: "Share context, and share full agent traces, not just individual messages". A brief of two lines can't carry the decisions that led to it.

## Do the two posts disagree?

Less than their titles suggest. Anthropic's system splits a research question into searches that don't depend on each other, and Cognition's failure is two agents building parts of one artifact.

I think the line between them is whether the agents read or write. Agents that gather information in parallel can't contradict each other's work, and agents that each change the same thing can.

That matches the labels in my guide to the [types of AI agents](/articles/ai-agent-taxonomy/). Parallel readers are a safe first use of a second agent, and parallel writers need the shared context Yan asks for.

Claude Code's design follows the same line. A [subagent](/articles/claude-code-subagents/) there works in its own context window and returns only a final report, which suits a search and suits a joint edit badly.

## When should you split a single agent?

Start with one agent, as Fowler's teams started with one service, and split when you can name the seam. Kadharmoideen Fadurudeen's [guide to multi-agent patterns](https://kadhar.dev/blog/multi-agent-systems-from-scratch), published in June and discussed on Hacker News on November 5, gives a test for staying put: "You can't yet say what each agent would own."

The questions to put to a design are these.

- Can the subtasks run without seeing each other's results?
- Does each subagent only gather information, or does it change something?
- Is the task worth several times the token bill?
- Can a person trace a wrong answer back to the agent that produced it?

A no to the first question means the work belongs in one loop. A no to the last means the system needs logging before it needs more agents, since [agents fail](/articles/ai-agent-failures/) in ways that are hard to reconstruct even with one.

Memory is the last thing a split changes. Several agents either share a store or keep their own, and [shared vs isolated memory](/articles/shared-vs-isolated-memory/) covers that choice, with [agent design patterns](/articles/agent-design-space/) for the ways to wire them together.

## FAQ

**What is a multi-agent system?**

It is a system in which several AI agents, each with its own context and tools, pass work between them to complete a task.

**Are multi-agent systems better than a single agent?**

For broad research that splits into independent searches, Anthropic reported a large gain in 2025. For tasks where the parts depend on each other, a single agent avoids the handoff errors.

**Why do multi-agent systems cost more?**

Each agent has its own context window to fill. Anthropic's 2025 figures put multi-agent systems at about 15 times the tokens of a chat, against about 4 times for a single agent.
