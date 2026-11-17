---
category: coding-agents
primary_query: claude code vs gemini cli
siblings:
- coding-agent-memory
- best-llms-for-coding
date: 2026-04-12
description: Claude Code vs Gemini CLI, read from both tools' docs in November 2026. Google
  moved consumer plans to Antigravity CLI in June, so the comparison starts with who
  can still run Gemini CLI, then permissions, undo and sandboxing.
status: published
work_note: "I'm Ninad Pathak, and I freelance as a technical writer for AI companies. I build the example and run it before I draft a tutorial, so your engineers review working code. [Here's how we'd work together](/services/freelance-technical-writer-for-ai-companies/)."
title: Claude Code vs Gemini CLI in Late 2026
updated: '2026-08-17'
slug: claude-vs-gemini-cli
video: claude-vs-gemini-cli
---

Developers keep a graveyard for Google products. [Killed by Google](https://killedbygoogle.com/) lists the discontinued ones, and the entry for "Google Gemini (CLI and Code Assist)" went up this year.

So a Claude Code vs Gemini CLI comparison has to start somewhere it didn't in the spring. Claude Code is Anthropic's coding agent for the terminal and Gemini CLI is Google's, and on June 18 Gemini CLI [stopped serving requests](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli) for Google's consumer plans in favour of a successor called Antigravity CLI.

The graveyard entry overstates it a little. Google's post says enterprise licences are unchanged and that Gemini CLI stays reachable with a paid API key, and its docs and its open-source repository are still up.

I've compared the two below from their docs as they stood on November 18, as a question about [coding agents](/articles/coding-agents/) and how much each one lets you supervise. I haven't run a head-to-head task, so there's no winner at the end.

## Can you still use Gemini CLI?

Yes, if you pay through the API or your company has a licence. Google's post keeps access for Gemini Code Assist Standard and Enterprise customers and for paid Gemini API keys, and ends it for the Pro and Ultra consumer plans and for free use.

The docs carry a second notice that matters more for a new project. A banner on every page says Gemini CLI "has not been optimized for Gemini 4 Argon" and sends you to Antigravity to use that model.

I read the two notices together as a tool in maintenance. If you're choosing a terminal agent today and you aren't already on Gemini CLI through work, the comparison you want is probably Claude Code against Antigravity CLI, which this page doesn't make.

## How do Claude Code and Gemini CLI differ on control?

They agree on the big pieces and differ on defaults. Both have a planning mode, a way to undo the agent's edits and an operating-system sandbox, and here is how each one ships:

| | Claude Code | Gemini CLI |
|---|---|---|
| Planning before edits | [Plan mode](https://code.claude.com/docs/en/permission-modes), one of six permission modes | [Plan Mode](https://geminicli.com/docs/cli/plan-mode/), enabled by default |
| Undoing edits | [Checkpoints](https://code.claude.com/docs/en/checkpointing) are automatic, with `/rewind` | [Checkpointing](https://geminicli.com/docs/cli/checkpointing/) is off until you enable it in `settings.json`, then `/restore` |
| Sandbox for shell commands | [Built in](https://code.claude.com/docs/en/sandboxing), off by default | [Several methods](https://geminicli.com/docs/cli/sandbox/), enabled with a flag or a setting |
| Project instructions | `CLAUDE.md`, or `AGENTS.md` when there's no `CLAUDE.md` | `GEMINI.md` by default |
| Source | Closed | Open source under Apache 2.0 |

The row I'd look at first is undo. Claude Code snapshots your files before each prompt without being asked, and Gemini CLI does the same thing only after you've turned it on.

## What does plan mode do in each?

Both tools' plan modes let the agent read and propose while edits are held back. Claude Code's docs say that in plan mode Claude "reads files, runs shell commands to explore, and writes a plan, but does not edit your source".

Gemini CLI's version is stricter about tools. Its docs list the only tools allowed in Plan Mode, and they cover reading and searching, so a shell command isn't among them.

That difference decides what a plan can know. A planner that can run the test suite has seen the failure it's planning around, and a planner that can only read has to infer it.

Claude Code's other modes are a ladder from asking about everything to asking about nothing. The docs recommend the top rung, `bypassPermissions`, for "Isolated containers and VMs only", which is a sentence I'd tape to the monitor.

## How does undo work, and what does it miss?

Both tools snapshot files so you can go back, and both leave holes that Git has to cover. Claude Code keeps snapshots for the 100 latest checkpoints in a session and restores them with `/rewind`.

Its limits are written down, which I appreciate. A file that only a shell command changed isn't tracked, and the docs say plainly that checkpoints are "Not a replacement for version control".

Gemini CLI takes a heavier snapshot. Each checkpoint is a commit in a shadow Git repository under `~/.gemini/history/`, taken before a tool modifies files, together with the conversation up to that point.

So I'd commit before a long run with either tool. Their undo features cover the agent's own edits, and a refactor that runs a code generator or a formatter changes files by other means.

## Which one should you pick for a refactor?

I don't have evidence for a universal winner, and I'd distrust a page that named one without a logged run. What the docs support is narrower.

Claude Code gives you more out of the box for a refactor that crosses several files: you can review its plan or approve sensitive tool calls first, and undo is on from the first prompt. Gemini CLI also supports an edit-and-verify loop, but automation isn't proof, so the result depends on whether your checks catch the failures.

If you do have access to both, run them on the same task from the same commit and judge the patches with the same tests. The model matters as much as the interface, and [which LLM to use for coding](/articles/best-llms-for-coding/) is a separate choice.

A last point carries across any pair of tools. Each reads a project instruction file at the start of a session, and what's in that file is the subject of [coding agent memory](/articles/coding-agent-memory/).

## FAQ

**Is Gemini CLI discontinued?**

For consumer plans, yes. Google stopped serving Gemini CLI requests for its Pro and Ultra plans and for free use on June 18, 2026, and kept it for enterprise licences and paid API keys.

**What replaced Gemini CLI?**

Antigravity CLI. Google's announcement says it's built in Go and shares an agent harness with the Antigravity desktop application.

**Is Gemini CLI open source?**

Yes. Its GitHub repository is published under the Apache 2.0 licence.

**Does Claude Code have a sandbox?**

Yes, for shell commands, and it's off by default. On macOS it uses the built-in Seatbelt framework, and on Linux it relies on `bubblewrap`.

**Can either tool undo its changes?**

Both can undo the edits their own tools made. Claude Code does this automatically with `/rewind`, and Gemini CLI needs checkpointing enabled before `/restore` has anything to restore.
