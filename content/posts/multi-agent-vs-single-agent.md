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
description: 'Multi-agent systems vs a single agent: what a second agent buys, what it costs, and the 2026 rule from Cognition that only one agent should write.'
slug: multi-agent-vs-single-agent
status: published
work_note: "Building an AI product whose readers are engineers? I'm Ninad Pathak, a freelance technical writer, and I write tutorials and technical articles for companies like yours after running the product myself. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Multi-Agent vs Single-Agent Systems: The Real Trade-offs'
updated: 2026-11-17
---

A multi-agent system is several model loops, each with its own context window and a narrower job, passing work between them. A single-agent system is one loop that does everything, and one loop is still the place to start.

Martin Fowler wrote [Monolith First](https://martinfowler.com/bliki/MonolithFirst.html) in June 2015 after watching teams adopt microservices, and what he'd noticed was that "Almost all the successful microservice stories have started with a monolith that got too big and was broken up".

So I'll take the question in that order for [AI agent architecture](/articles/ai-agents/): what a second agent buys, what it costs, and what Walden Yan of Cognition, who told everyone in 2025 not to build these, now says works.

## What does a second agent buy?

A second agent buys more context to think with, on work that splits cleanly. Anthropic's account of [its multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system), published on June 13, 2025, reports that a lead agent with subagents "outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval."

Why would more agents do better? The post's own answer is capacity: a separate analysis in it found that "token usage by itself explains 80% of the variance", and a system of agents spends more tokens because each one has a window to itself.

Now, the eval is internal and the models in it date from 2025, so I take from it that subagents help on research and wouldn't quote the 90.2% for today's models. The mechanism still applies, though: a subagent can read twenty pages and hand back a paragraph, which keeps the lead agent's window clear.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/multi-agent-vs-single-agent/agent-topology.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/multi-agent-vs-single-agent/agent-topology.narrow.svg" width="288" height="656"><img class="np-has-narrow" src="/static/images/diagrams/multi-agent-vs-single-agent/agent-topology.svg" width="720" height="488" alt="A single agent runs one loop with one trace. A multi-agent system puts a supervisor over three workers, each with its own memory and failure boundary, so they can run independent work in parallel, but every handoff between them is a message boundary where things can break in transit." loading="lazy" decoding="async"></picture></a>
  <figcaption>Parallel workers cut wall-clock time only when the work is independent, and every handoff adds a place to fail.</figcaption>
</figure>

## What does it cost?

It costs tokens first. Anthropic's post is upfront about the bill: "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats."

So a multi-agent run costs a little under four times a single-agent run of the same task. Anthropic's condition for paying that is that "the value of the task is high enough to pay for the increased performance."

Coordination is the second cost. The post says plainly where the design doesn't fit, "some domains that require all agents to share the same context or involve many dependencies between agents", and it names coding as one.

## Where do multi-agent systems break?

Multi-agent systems break at the handoff, where one agent acts on a guess about what another meant. Yan made the case in [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) on June 12, 2025, with a task to clone Flappy Bird split between two subagents.

The subagent given the background builds one that looks like Super Mario Bros., and the subagent given the bird builds one that moves nothing like the bird in Flappy Bird, so a final agent is left combining what Yan calls "these two miscommunications." His first rule comes from that: "Share context, and share full agent traces, not just individual messages".

But shared context isn't enough. Give both subagents the full task and they can still pick visual styles that clash, which is his second rule: "Actions carry implicit decisions, and conflicting decisions carry bad results".

## What does Yan say works now?

Yan says the systems that work are ones where only one agent writes. On April 22, 2026 he published a follow-up, [Multi-Agents: What's Actually Working](https://cognition.com/blog/multi-agents-working), which keeps the warning for parallel writers and describes "a narrower class of patterns" that held up: "setups where multiple agents contribute intelligence to a task while writes stay single-threaded."

| Pattern in the 2026 post | What the extra agent does | Who writes |
| --- | --- | --- |
| Clean-context reviewer | Reviews the coding agent's diff with no shared history | The coding agent |
| Smart friend | A larger model the working model can consult as a tool | The working model |
| Manager and children | Splits a large task, hands out pieces and reports back | Each child, on its own piece |

The clean-context reviewer reverses his own 2025 advice to share context, and he says so. For review, his team found "this technique to work best when the coding and review agents do not share any context beforehand."

And what about swarms of agents negotiating with each other? His answer is short: he thinks they are largely "a distraction."

The line between agents that read and the one agent that writes is Yan's, and he credits Anthropic with reaching it too. A footnote says the two 2025 posts, published a day apart, "came to similar conclusions about the first area of applicability being in readonly agents".

## What would I add to that?

I'd add a confirmation and two cautions. The confirmation comes from a second vendor: Anthropic's [post on its own code review](https://claude.dev/blog/solving-code-review-at-anthropic/) from October 15 describes the clean-context reviewer in production: before a pull request is opened, "a subagent reviews the diff with fresh context".

The first caution is that both sources sell what they describe. Cognition sells agents and Anthropic sells the tokens they run on, so both gain when a task uses several, and neither post prints a failed deployment.

The second caution is that "writes stay single-threaded" is only useful if somebody checks it. It's a rule you can take into a design review as one question: for each thing this system can change, which single agent is allowed to change it?

A manager that only decides which specialist gets a request is the smallest multi-agent design, an [agentic router](/glossary/agentic-router/). Claude Code's [subagents](/articles/claude-code-subagents/) sit one step up, working in their own windows and returning only a final report.

## When should you split a single agent?

Start with one agent, as Fowler's teams started with one service, and split once you can say which part of the work a second agent would own. Kadharmoideen Fadurudeen's [guide to multi-agent patterns](https://kadhar.dev/blog/multi-agent-systems-from-scratch), published in June and discussed on Hacker News on November 5, gives a test for staying put: "You can't yet say what each agent would own."

So before you add an agent, put four questions to the design.

- Can the subtasks run without seeing each other's results?
- Does each added agent only read and advise, with one agent doing the writing?
- Is the task worth several times the token bill?
- Can a person trace a wrong answer back to the agent that produced it?

If the subtasks need each other's results, the work belongs in one loop. If nobody can trace a wrong answer to its agent, the system needs logging before it needs more agents, since [agents fail](/articles/ai-agent-failures/) in ways that are hard to reconstruct even with one.

A split also changes memory. Several agents either share a store or keep their own, a choice [shared vs isolated memory](/articles/shared-vs-isolated-memory/) works through, and the ways to connect the agents are laid out in [agent design patterns](/articles/agent-design-space/).

How much an agent decides alone is a separate question, and my guide to the [types of AI agents](/articles/ai-agent-taxonomy/) covers it.

## FAQ

**What is a multi-agent system?**

A multi-agent system is one in which several AI agents, each with its own context and tools, pass work between them to complete a task.

**Are multi-agent systems better than a single agent?**

For broad research that splits into independent searches, Anthropic reported a large gain in 2025. For work that changes shared files, Cognition's 2026 advice is to keep one agent writing and use the others to review or advise.

**Why do multi-agent systems cost more?**

Each agent has its own context window to fill. Anthropic's 2025 figures put multi-agent systems at about 15 times the tokens of a chat, against about 4 times for a single agent.
