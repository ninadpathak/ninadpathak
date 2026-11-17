---
category: coding-agents
primary_query: agentic workflows
siblings:
- claude-md
- claude-code-subagents
- red-build-nobody-reads
bridges:
- slug: agent-loop-anatomy
  reason: The run stage of the workflow is one agent loop, and that page takes the loop apart.
- slug: agent-harnesses
  reason: The limits and the trace for a run live in the harness.
- slug: multi-agent-vs-single-agent
  reason: Scoping a task includes deciding whether it needs more than one agent.
date: 2026-06-14
description: 'An agentic workflow puts an AI agent inside a fixed process. Five stages from prompt to pull request, and the five questions Anthropic asks before a run goes unattended.'
slug: agentic-workflows
status: published
work_note: "Your engineers shouldn't have to fix a tutorial's code in review. I'm Ninad Pathak, a freelance technical writer for AI companies, and I build and run every example before I draft. [Work with me on yours](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Agentic Workflows From Prompt to Pull Request'
updated: 2026-11-17
---

An agentic workflow is a multi-step process that an AI agent plans and carries out with tools, deciding each next step from the last result. For coding work, the version I'd run puts the agent between two points a person controls: the statement of what done means, and the approval of the result.

On November 4 someone asked Hacker News [what everyone's agentic setup looks like](https://news.ycombinator.com/item?id=50366117), and several hundred people answered. The answers disagree on the model, the harness and whether to sandbox at all.

Where they agree is smaller and more useful. A top reply, from someone who had thrown out their custom skills, put it this way: "the biggest trick is just to tell it what complete looks like."

So this page is about the part that survives a change of tools, as it applies to [coding agents](/articles/coding-agents/).

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agentic-workflows/workflow-pipeline.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agentic-workflows/workflow-pipeline.narrow.svg" width="288" height="776"><img class="np-has-narrow" src="/static/images/diagrams/agentic-workflows/workflow-pipeline.svg" width="720" height="264" alt="Five stages left to right: frame the task, scope it down, let the agent run with its own checks, review the diff, and land it. Framing and review are the human's stages, marked with a person; the work stage is the agent's own loop." loading="lazy" decoding="async"></picture></a>
  <figcaption>A person owns framing and review, the agent owns the run, and scoping and landing join the two.</figcaption>
</figure>

## What is an agentic workflow?

It's the process around an agent run, as distinct from the run. The agent's own cycle of model call and tool call is [the agent loop](/articles/agent-loop-anatomy/), and a workflow is what you put before and after that loop.

For a coding task the workflow starts at a prompt and ends at a merged pull request. I split it into five stages, and a person owns the first and the fourth.

## What are the five stages?

Frame, scope, run, review and land. Anthropic's [best practices for Claude Code](https://code.claude.com/docs/en/best-practices) list five questions to ask before a run goes unattended, and the stages line up with them closely enough that I've set the two side by side.

| Stage | Who | What it settles | Anthropic's question |
| --- | --- | --- | --- |
| Frame | You | What done means | Does it know what done looks like? |
| Scope | You | Which files and how large a change | What's it allowed to touch? |
| Run | The agent | The work, with its own checks | Can it check its own work, and what stops it? |
| Review | You | Whether the diff does what the frame asked | Who signs off? |
| Land | The agent drafts, you approve | The commit and the pull request | Where does the result go? |

The same page ends its list by naming what stays with you: starting the run, deciding what done means this time, and approving the merge at the end. I'd pin that above any agent setup.

## How do you frame a task for an agent?

Write down what done looks like before the agent sees anything. A frame answers what the change is, how you'll know it worked and what must not break.

Say the request is "add caching to the API". That could mean an in-memory layer or HTTP cache headers, and an agent given only that line will pick one and build on it.

So the frame goes in a short brief: the goal, an acceptance check, the hard constraints and the files you expect to change. Anthropic's version of the acceptance check is a goal condition or a failing test the agent has to turn green.

Rules that hold for every task don't belong in the brief. They go in the instruction file the agent loads at the start of each session, which my [CLAUDE.md guide](/articles/claude-md/) covers.

## How big should one agent task be?

Small enough that you can read the whole diff in one sitting. An agent will change forty files if you let it, and a diff nobody can read is a diff nobody reviewed.

When the task is larger than that, split it into changes that each stand alone, each with its own frame and its own review. The sequence gets you to the large change through steps you can check.

Scoping is also where you decide how many agents the task needs, and the answer is nearly always one. The costs of a second agent are in [multi-agent vs single-agent systems](/articles/multi-agent-vs-single-agent/).

## What should an agent run leave behind?

A record you can read afterwards, and evidence for anything it claims. Anthropic's advice is to ask for the command the agent ran and its output, because a bare "all tests pass" tells you very little.

The limits belong in the same place as the record. A turn limit and a spending limit stop a run that isn't getting anywhere, and the [agent harness](/articles/agent-harnesses/) is the layer that enforces both.

And a side task doesn't have to fill the main context. A [Claude Code subagent](/articles/claude-code-subagents/) does its searching in its own window and hands back the answer.

## Why review the diff and not the summary?

Because the summary is what the agent believes it did, and the diff is what it did. The two differ in exactly the cases you care about.

I'd read for the changes nobody asked for: a config flag flipped, an error swallowed, an assertion deleted so a test goes green. Nothing flags them, and they pass every automated check the agent ran.

Anthropic's docs suggest one more reader, a review by a fresh subagent that never saw the conversation and so isn't swayed by the reasoning that produced the code. I think that's a good second pass and a poor substitute for yours.

All of this assumes someone still has attention to spend on review. [My essay on a build that is always red](/articles/red-build-nobody-reads/) looks at what happens when agents produce more signals than a team can read.

## How do you land the change?

Reuse the frame. The acceptance check you wrote in stage one becomes the pull request description, so the reviewer checks the change against a stated bar.

Let the agent draft the commit message and the description from the diff, then edit them against what the diff does. A person approves the merge, as with anything else you can't take back.

## FAQ

**What is an agentic workflow?**

It's a multi-step process that an AI agent plans and carries out with tools. The version on this page puts a person's statement of what done means before it and a person's approval after it.

**Do I need a stronger model for an agentic workflow?**

A stronger model finishes more in one pass. The frame and the review catch mistakes from any model, so they matter whichever one you run.

**How big should a single agent task be?**

Small enough that you can review the whole diff in one sitting. Split anything larger into changes that each stand alone.

**Should I use several agents for one feature?**

Nearly always no. A second agent adds coordination, and one agent with a clear frame and a reviewed diff is the simpler setup to trust.
