---
title: "The Agentic Workflow Playbook: From Prompt to Shipped PR"
date: 2026-06-14
slug: "agentic-workflow-playbook"
description: "The repeatable five-stage process I run to take a task from vague intent to a pull request I trust, with an AI agent doing the heavy lifting and me stepping in to frame the work and read the diff before it merges."
tags: [ai, agents, developer-experience]
status: published
---

I do not turn an agent loose on a task and hope. I run a sequence, the same one every time, that turns a vague intent into a pull request I am willing to put my name on. The agent does the heavy lifting. I step in at the moments a mistake would actually cost something, like when the change touches a payment path, or the agent is about to edit a database migration that runs against production.

Almost all of the value in agentic work comes from the structure around the agent rather than the model. A strong model inside a sloppy process produces confident garbage. A modest model inside a tight process ships real work. The playbook below is the process I run, stage by stage, with the checkpoints where I step back in.

## The playbook in one sentence

Frame the task, scope it down, let the agent work against an instrumented loop, review the diff like I do not trust it, then land it. Five stages, two of them mine and one of them the agent's, with scoping and landing as the seams between. The art is knowing which stage owns which decision.

I think about the whole thing as a loop with a human at two of its phases. The agent runs its own perceive-think-act-remember cycle inside stage three, which I broke down in [the anatomy of an agent loop](/blog/agent-loop-anatomy/). My job is the outer loop around it, and that outer loop has barely changed across three generations of models.

<div class="visual-wrapper">
  <div class="visual-title">THE FIVE-STAGE AGENTIC WORKFLOW</div>
  <div class="visual-container">
    <iframe src="/static/visuals/agentic-workflow-pipeline.html" title="A five-stage horizontal pipeline from Frame to Land, with a pulse traveling through and human-checkpoint markers on the framing and review stages" loading="lazy"></iframe>
  </div>
</div>

## Stage 1: Frame the task before the agent sees it

The first stage has nothing to do with the agent. Framing is where I write down what done looks like, in plain terms, before a single token gets generated.

A good frame answers three questions. What is the change. How will I know it worked. What must not break. Ten minutes here saves an hour of watching an agent solve the wrong problem with great enthusiasm.

The failure I see most often is handing an agent a one-line request and expecting it to infer the constraints. "Add caching to the API" can mean six different things. The agent picks one, commits to it, and builds a whole structure around the wrong assumption. The cost of that wrong assumption compounds with every file it touches, because each later edit is consistent with the early mistake.

I write the frame as a short brief the agent reads first. Goal, acceptance check, hard constraints, and the files I expect to be involved. The brief is not the prompt. The brief is the contract, and I hold the agent to it during review.

## Stage 2: Scope the change to something reviewable

The second stage is mine too. Scoping is where I cut the task down to a change I can actually review in one sitting.

An agent will happily rewrite forty files in one pass. A forty-file diff is unreviewable, which means it is untrustable, which means it ships bugs. I scope the work so the diff stays in the range I can read carefully, usually a few hundred lines across a handful of files.

When a task is genuinely large, I split it into a sequence of scoped changes that each stand on their own. Each one gets its own frame, its own agent run, its own review. The sequence builds toward the big change through steps I can verify one at a time. A migration across a codebase becomes twelve small reviewable diffs rather than one giant unreadable one.

Scoping is also where I decide whether the task needs one agent or several. The honest answer is almost always one. I covered the real trade-offs in [multi-agent versus single-agent systems](/blog/multi-agent-vs-single-agent-tradeoffs/), and the short version is that coordination cost is real and most tasks do not need it.

## Stage 3: Let the agent work against an instrumented loop

Now the agent runs. The third stage belongs to the agent, and the only thing I control here is what I built before it started.

The agent reads the frame, reads the relevant files, and starts its loop. What matters is that I can see what it is doing. A run I cannot observe is a run I cannot trust. Structured logging of every tool call and its result is what lets me catch a wrong turn at step three instead of discovering it at step thirty.

The instrumentation lives in the harness, not in the prompt. The harness enforces the iteration budget, the timeouts, and the retries, and it records the trace for me to read later. I wrote about what belongs in that layer in [agent harnesses](/blog/agent-harnesses/). A coding agent without a harness is a demo. A coding agent with one is a tool I can rely on.

I do not babysit every step. I let the agent run to a natural checkpoint, a passing test or a completed sub-change, and then I look. The point of the instrumentation is that I can read back the whole trace when something is off, rather than staring at the agent live and hoping to catch the moment it goes wrong.

## Stage 4: Review like you do not trust it

The fourth stage is the one people skip, and skipping it is why agentic work gets a bad name. Review is where I read the diff as if a stranger wrote it under deadline pressure.

I do not read the agent's summary of what it did. I read the diff. The summary is the agent telling me what it believes it did. The diff is what it actually did. The two diverge more often than the confident tone suggests.

My review checks the same things every time. Does the change match the acceptance check from stage one. Did it touch files outside the scope from stage two. Are there silent changes, a config flag flipped, an error swallowed, a test weakened so it passes. Agents are very good at making tests green, and not always by making the code correct.

The errors that survive to this stage tend to be the quiet ones. A dependency added that did not need to be. An edge case handled by deleting the assertion that caught it. A retry wrapped around a call that should have failed loudly. I keep a running list from [why AI agents keep failing in production](/blog/why-ai-agents-keep-failing-in-production/), and most of those failures are visible in the diff once I actually read it line by line.

## Stage 5: Land it

The last stage is the cheapest when the first four were done well. Landing is commit, push, and open the PR, with the frame from stage one becoming the PR description.

The frame doing double duty here is deliberate. The acceptance check I wrote before the agent started becomes the thing a reviewer verifies. The constraints become the things they know to watch. A PR that explains what done looks like is a PR that gets reviewed fast, because the reviewer is checking against a stated bar rather than guessing at intent.

I let the agent draft the commit message and the PR body from the diff, then I edit. The draft is usually eighty percent right and saves the part of the job I find tedious. The edit is where I make sure the description matches what the diff actually does, not what the agent hoped it did.

## Where the playbook saves me

The playbook is not overhead. It is the thing that makes the agent worth using at all.

The two stages I own, framing and review, are where my judgment lives. The stage the agent owns, the actual work, is where its speed lives. Scoping and landing are the seams that connect them. Skip framing and the agent solves the wrong problem. Skip review and the wrong solution ships. Keep all five and the agent becomes the fastest reliable contributor I work with.

I run this loop several times a day. The model gets better every few months and the playbook does not change, because the playbook is about where human judgment belongs rather than about which model is best this quarter. The shape of what people build keeps shifting, and I mapped a lot of that in [the agent design space](/blog/the-agent-design-space/), but the outer loop has stayed the same since the first week I trusted an agent with real work. Get the structure right and the model becomes a detail you swap out.

## FAQ

**What is an agentic workflow?**

An agentic workflow is a repeatable process where an AI agent does part of the work inside a structure you control. The agent runs its own loop on the task, and you step in where a mistake would cost something real, like a change to a billing flow or anything that runs against production, usually by framing the work up front and reading the diff before it merges.

**Do I need a powerful model to run this playbook?**

No. The playbook is built so a modest model still produces reliable output, because the structure catches its mistakes. A stronger model finishes more in one pass, and the framing and review stages still matter more than the model choice.

**How big should a single agent task be?**

Small enough that you can review the entire diff in one sitting, usually a few hundred lines across a handful of files. When the task is larger, split it into a sequence of scoped changes that each stand on their own and review each one.

**Why review the diff instead of the agent's summary?**

The summary is what the agent believes it did. The diff is what it actually did. Agents are good at making tests pass and writing confident summaries, and the quiet mistakes, a swallowed error or a weakened test, only show up when you read the diff.

**Should I use multiple agents for a single feature?**

Usually not. Coordination between agents adds latency and new failure modes, and most features ship faster with one well-instrumented agent. Reach for multiple agents only when the work splits into clearly separate roles that each need their own context and tools.
