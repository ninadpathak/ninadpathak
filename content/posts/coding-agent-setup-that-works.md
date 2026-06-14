---
title: "How I Set Up a Coding Agent That Actually Finishes the Task"
date: 2026-06-13
slug: "coding-agent-setup-that-works"
description: "A coding agent succeeds or fails before it writes a line. Here is the setup I use, the rules file, repository context, tools, permissions, and guardrails, that turns a capable model into an agent I trust with real work."
tags: [ai, agents, devtools, developer-experience]
status: published
---

A coding agent fails or succeeds before it writes a line. The difference is the setup, the context I hand it and the limits I put around it. I have watched the same model produce careful, correct work in one repository and confident nonsense in another. The model was identical. The setup was not.

Almost every complaint I hear about coding agents traces back to setup. The agent committed directly to main because nobody told it to branch. It rewrote a config file the whole team treats as sacred. It ran for twenty minutes refactoring an auth module and forgot, halfway through, the test command I gave it at the start. None of those are model problems. All of them are things I fix before the agent starts.

## The setup is a context problem, not a model problem

The model is the part I control least and worry about least. I pick a capable one and move on. I wrote about how I choose in [the best LLMs for coding](/blog/best-llms-for-coding/), and the headline is that the right model depends on the job, with a fast cheap one for small edits and a stronger one for architecture and large refactors.

Everything else about the setup is context. A coding agent is a reasoning engine pointed at a codebase it has never seen. My job is to hand it the same context a new senior engineer would need on day one, in a form it can read every time it starts a task. The agent reads that context the way an engineer reads the onboarding doc on their first morning, except it reads it fresh at the start of every single task, having retained nothing from yesterday. Get the context right and a mid-tier model behaves like a careful colleague. Get it wrong and the best model on the market still guesses.

<div class="visual-wrapper">
  <div class="visual-title">WHAT A CODING AGENT READS BEFORE IT ACTS</div>
  <div class="visual-container">
    <iframe src="/static/visuals/coding-agent-context-stack.html" title="A stack of context layers a coding agent reads in order: rules file, repository map, the task brief, available tools, and guardrails, with each layer highlighting in turn" loading="lazy"></iframe>
  </div>
</div>

## The rules file: what the agent should always know

The single most useful piece of setup is a rules file the agent reads on every run. Tools like Claude Code load a project file at startup and treat it as standing instructions. I covered the mechanics of that in [how memory works in Claude Code](/blog/how-memory-works-in-claude-code/). The file is where I put the conventions the agent cannot infer from the code fast enough to be useful.

What goes in it: the commands to build and test, the conventions the team actually follows, the directories that are off limits, and the patterns I want copied. What stays out of it: anything the agent can read straight from the code itself. A bloated rules file is as bad as an empty one, because the agent spends attention parsing it on every single run.

Short and specific is the standard I hold mine to. Run the suite with `pnpm test`, not `npm test`. Never touch the `generated/` folder, those files come from a codegen step. Match the error-handling style in `lib/errors.ts`, where every failure returns a typed result instead of throwing. Concrete instructions the agent can act on beat principles it has to interpret. Vague guidance like "write clean code" does nothing, because the agent already believes it is doing that.

## Repository context: helping the agent find its way

A large codebase is mostly noise to a fresh agent. Pointing it at the signal is the part that takes judgment. I do not expect the agent to read the whole repository, and I do not want it to, because every irrelevant file it reads is tokens spent and attention diluted.

Each task brief I write names the files I expect to be involved. That gives the agent a starting point instead of a search. When the work touches an area I know well, say a change to how we paginate API responses, I name the handler and the serializer and let the agent expand from there. For an area I do not know, I let it explore first and report back what it found before it changes anything, so I can correct a wrong mental map before it has written a line.

The agent's first move on any non-trivial task should be reading, not writing. I want it to build a picture of the relevant code before it edits, the same way I would. A coding agent that starts editing in the first thirty seconds is an agent that has not understood the problem yet.

## Tools and permissions: what the agent is allowed to touch

A coding agent without tools is a chat window. The tools are what let it read files, run commands, and edit code. The permissions are what keep those tools from doing damage.

Tight scoping is how I set up permissions. The agent can read the repository, run the test suite, and edit code inside the project. It cannot touch anything outside the working directory, and anything that reaches the network or a production system needs my explicit approval. I want it to stop and ask before it runs a database migration or pushes to a remote, the two moves where being wrong costs real money or a midnight rollback. The default posture is that the agent acts freely inside a sandbox and asks before stepping outside it.

Tool design earns its keep here. A tool with a clear schema and good validation catches a bad argument before it runs. A vague tool invites the agent to call it wrong. I treat tool schemas as part of the setup, not an afterthought, and I went deep on what makes them reliable in [structured outputs and function calling](/blog/structured-outputs-llms-json-mode-function-calling/).

## Guardrails: making failure cheap

The goal of guardrails is not to stop the agent from ever being wrong. The goal is to make being wrong cheap to catch and easy to undo.

Version control is the first guardrail. Working on a branch, never on the main line, means every change is reversible with one command. A run that goes sideways costs me a `git branch -D`, not an afternoon of untangling a botched commit out of shared history.

For the second guardrail I lean on the test suite. An agent that can run the tests gets a fast signal about whether its change broke something. I want that loop tight, because a suite that takes four minutes turns a self-correcting agent into one that ships untested guesses rather than wait around for the result. Running the tests after every meaningful change is the difference between an agent that converges on correct and one that drifts.

Observability is the third. I keep a structured log of every command the agent ran and every file it changed, which is the same instrumentation I argued for in [agent harnesses](/blog/agent-harnesses/). When the result is wrong, the log tells me where the agent went off course, so I can fix the setup rather than blame the model.

## Keeping context alive across a long task

What breaks a long task is that the agent forgets. A context window has fixed capacity, and a task that runs for twenty minutes generates more history than the window holds. The agent drops the early context to make room, and the early context is often where the constraints lived. Picture a whiteboard you keep writing on without erasing your own plan at the top, the constraints scroll off the top edge as the agent keeps working at the bottom.

Keeping tasks scoped small is partly for this reason. A change I can review in one sitting is also a change short enough that the agent never runs out of room. When a task genuinely has to run long, like migrating fifty call sites to a new function signature, I lean on the agent writing its progress to a file it can re-read, so its working state survives the window filling up. I broke down why this happens and the patterns that fix it in [why coding agents keep forgetting everything](/blog/why-coding-agents-lose-their-memory/).

Once you know the signal that an agent has lost context, it is unmistakable. It re-solves a problem it already solved. It contradicts a decision it made ten minutes ago, switching back to the error pattern you steered it away from. It asks for the database name you handed it at the start. Every one of those is the window having evicted something that mattered.

## The setup I actually run

My working setup comes down to four things. A short rules file with the build and test commands and the off-limits directories. A per-task brief that names the goal and the files in play. Tightly scoped permissions with a sandbox boundary. A branch, a fast test loop, and a log I can read when something breaks.

Underneath the larger loop I run for every task, which I wrote up in [the agentic workflow playbook](/blog/agentic-workflow-playbook/), sits that same setup. The setup stays fixed between tasks. The brief changes with each one. Together they turn a capable model into an agent that finishes the job instead of one that produces an impressive-looking start and quietly falls apart by the end.

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
