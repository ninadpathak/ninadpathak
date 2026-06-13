---
title: "How I Set Up a Coding Agent That Actually Finishes the Task"
date: 2026-06-13
slug: "coding-agent-setup-that-works"
description: "A coding agent succeeds or fails before it writes a line. Here is the setup I use, the rules file, repository context, tools, permissions, and guardrails, that turns a capable model into an agent I trust with real work."
tags: [ai, agents, devtools, developer-experience]
status: published
---

A coding agent fails or succeeds before it writes a line. The difference is the setup, the context I hand it and the limits I put around it. I have watched the same model produce careful, correct work in one repository and confident nonsense in another. The model was identical. The setup was not.

Almost every complaint I hear about coding agents traces back to setup. The agent forgot a convention nobody told it. It edited a file it should never have touched. It ran for twenty minutes and lost the thread halfway through. None of those are model problems. All of them are things I fix before the agent starts.

## The setup is a context problem, not a model problem

The model is the part I control least and worry about least. I pick a capable one and move on. I wrote about how I choose in [the best LLMs for coding](/blog/best-llms-for-coding/), and the headline is that the right model depends on the job, with a fast cheap one for small edits and a stronger one for architecture and large refactors.

Everything else about the setup is context. A coding agent is a reasoning engine pointed at a codebase it has never seen. My job is to hand it the same context a new senior engineer would need on day one, in a form it can read every time it starts a task. Get that right and a mid-tier model behaves like a careful colleague. Get it wrong and the best model on the market still guesses.

<div class="visual-wrapper">
  <div class="visual-title">WHAT A CODING AGENT READS BEFORE IT ACTS</div>
  <div class="visual-container">
    <iframe src="/static/visuals/coding-agent-context-stack.html" title="A stack of context layers a coding agent reads in order: rules file, repository map, the task brief, available tools, and guardrails, with each layer highlighting in turn" loading="lazy"></iframe>
  </div>
</div>

## The rules file: what the agent should always know

The single most useful piece of setup is a rules file the agent reads on every run. Tools like Claude Code load a project file at startup and treat it as standing instructions. I covered the mechanics of that in [how memory works in Claude Code](/blog/how-memory-works-in-claude-code/). The file is where I put the conventions the agent cannot infer from the code fast enough to be useful.

What goes in it: the commands to build and test, the conventions the team actually follows, the directories that are off limits, and the patterns I want copied. What stays out of it: anything the agent can read straight from the code itself. A bloated rules file is as bad as an empty one, because the agent spends attention parsing it on every single run.

I keep mine short and specific. Run the tests with this command. Never edit files in this folder. Match the error-handling style in this module. Concrete instructions the agent can act on, not principles it has to interpret. Vague guidance like "write clean code" does nothing, because the agent already believes it is doing that.

## Repository context: helping the agent find its way

A large codebase is mostly noise to a fresh agent. The skill is pointing it at the signal. I do not expect the agent to read the whole repository, and I do not want it to, because every irrelevant file it reads is tokens spent and attention diluted.

The frame I write for each task names the files I expect to be involved. That gives the agent a starting point instead of a search. When the work touches an area I know well, I name the two or three files that matter and let the agent expand from there. When it touches an area I do not know, I let it explore first and report back what it found before it changes anything.

The agent's first move on any non-trivial task should be reading, not writing. I want it to build a picture of the relevant code before it edits, the same way I would. A coding agent that starts editing in the first thirty seconds is an agent that has not understood the problem yet.

## Tools and permissions: what the agent is allowed to touch

A coding agent without tools is a chat window. The tools are what let it read files, run commands, and edit code. The permissions are what keep those tools from doing damage.

I scope permissions tightly. The agent can read the repository, run the test suite, and edit code inside the project. It cannot touch anything outside the working directory, and anything that reaches the network or a production system needs my explicit approval. The default posture is that the agent acts freely inside a sandbox and asks before stepping outside it.

Tool design earns its keep here. A tool with a clear schema and good validation catches a bad argument before it runs. A vague tool invites the agent to call it wrong. I treat tool schemas as part of the setup, not an afterthought, and I went deep on what makes them reliable in [structured outputs and function calling](/blog/structured-outputs-llms-json-mode-function-calling/).

## Guardrails: making failure cheap

The goal of guardrails is not to stop the agent from ever being wrong. The goal is to make being wrong cheap to catch and easy to undo.

Version control is the first guardrail. The agent works on a branch, never on the main line, so every change is reversible with one command. A run that goes sideways costs me a branch deletion, not a recovery.

The test suite is the second. An agent that can run the tests gets a fast signal about whether its change broke something. I want that loop tight, because a slow test suite turns a self-correcting agent into one that ships untested guesses. Running the tests after every meaningful change is the difference between an agent that converges on correct and one that drifts.

Observability is the third. I keep a structured log of every command the agent ran and every file it changed, which is the same instrumentation I argued for in [agent harnesses](/blog/agent-harnesses/). When the result is wrong, the log tells me where the agent went off course, so I can fix the setup rather than blame the model.

## Keeping context alive across a long task

The hardest part of a long task is that the agent forgets. A context window has fixed capacity, and a task that runs for twenty minutes generates more history than the window holds. The agent drops the early context to make room, and the early context is often where the constraints lived.

I keep tasks scoped small partly for this reason. A change I can review in one sitting is also a change short enough that the agent never runs out of room. When a task genuinely has to run long, I lean on the agent writing its progress to a file it can re-read, so its working state survives the window filling up. I broke down why this happens and the patterns that fix it in [why coding agents keep forgetting everything](/blog/why-coding-agents-lose-their-memory/).

The signal that an agent has lost context is unmistakable once you know it. It re-solves a problem it already solved. It contradicts a decision it made ten minutes ago. It asks for information it was given at the start. Every one of those is the window having evicted something that mattered.

## The setup I actually run

My working setup is four things. A short rules file with the build and test commands and the off-limits directories. A per-task frame that names the goal and the files in play. Tightly scoped permissions with a sandbox boundary. A branch, a fast test loop, and a log I can read when something breaks.

That setup sits underneath the larger loop I run for every task, which I wrote up in [the agentic workflow playbook](/blog/agentic-workflow-playbook/). The setup is the part that does not change between tasks. The frame is the part that does. Together they turn a capable model into an agent that finishes the job instead of one that produces an impressive-looking start and quietly falls apart by the end.

The model will keep improving and I will keep swapping it. The setup is what makes that swap painless, because none of it depends on which model is best this month. Good context and tight guardrails make a modest agent reliable, and they make a strong agent genuinely useful.

## FAQ

**What is the most important part of setting up a coding agent?**

The rules file the agent reads on every run. It carries the build and test commands, the conventions the team follows, and the directories that are off limits. Concrete, specific instructions matter far more than the model you pick.

**How do I stop a coding agent from editing the wrong files?**

Scope its permissions and name the off-limits directories in the rules file. Let it act freely inside the project and require approval for anything outside the working directory or anything that reaches the network or production.

**Why does my coding agent forget what it was doing?**

A context window has fixed capacity, so a long task eventually evicts the early context where the constraints lived. Keep tasks small enough to fit, and have the agent write its progress to a file it can re-read when the window fills up.

**Do I need a top-tier model for coding agents?**

No. A capable mid-tier model with good context and tight guardrails behaves like a careful colleague. Use a stronger model for architecture and large refactors, where the extra reasoning earns its cost.

**What guardrails make agent mistakes safe?**

Work on a branch so every change is reversible, run the test suite after each meaningful change for a fast signal, and keep a structured log of every command and edit so you can see where a wrong result came from.
