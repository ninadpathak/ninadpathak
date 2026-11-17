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

Developers keep a public graveyard for products that Google has shut down. The site is called [Killed by Google](https://killedbygoogle.com/), and its entry for "Google Gemini (CLI and Code Assist)" went up this year.

So a Claude Code vs Gemini CLI comparison now has to start with whether you can still use Gemini CLI. Claude Code is Anthropic's coding agent for the terminal and Gemini CLI is Google's, and on June 18 Gemini CLI [stopped serving requests](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/) for Google's consumer plans in favour of a successor called Antigravity CLI.

The Killed by Google entry makes Gemini CLI sound more dead than it is. Google's post says enterprise licences are unchanged and that Gemini CLI still works with a paid API key, and the Gemini CLI docs and open-source repository are still online.

I've compared Claude Code and Gemini CLI below from their docs as they stood on November 18. The comparison is about how much each of these [coding agents](/articles/coding-agents/) lets you supervise its work, and I haven't run the two on a shared task, so this page doesn't name a winner.

## Can you still use Gemini CLI?

Yes, you can still use Gemini CLI if you pay for a Gemini API key or your company has a licence. Google's post keeps access for Gemini Code Assist Standard and Enterprise customers and for paid Gemini API keys, and ends access for the Google AI Pro and Ultra consumer plans and for free use.

The Gemini CLI docs carry a second notice, and it matters more than the June cutoff for anyone starting a new project. A banner on every docs page says Gemini CLI "has not been optimized for Gemini 4 Argon" and sends you to Antigravity to use that model.

Taken together, the two notices tell me Google is maintaining Gemini CLI and building new features into Antigravity. If you're choosing a terminal agent today and you aren't already on Gemini CLI through work, the comparison you want is probably Claude Code against Antigravity CLI, which this page doesn't make.

## How do Claude Code and Gemini CLI differ on control?

Claude Code and Gemini CLI have the same control features and ship them with different defaults. Both tools have a planning mode, a way to undo the agent's edits and an operating-system sandbox, and the table shows how each feature is set when you first install the tool:

| | Claude Code | Gemini CLI |
|---|---|---|
| Planning before edits | [Plan mode](https://code.claude.com/docs/en/permission-modes), one of six permission modes; a new install starts in `auto` | [Plan Mode](https://geminicli.com/docs/cli/plan-mode/), enabled by default |
| Undoing edits | [Checkpoints](https://code.claude.com/docs/en/checkpointing) are automatic, with `/rewind` | [Checkpointing](https://geminicli.com/docs/cli/checkpointing/) is off until you enable it in `settings.json`, then `/restore` |
| Sandbox for shell commands | [Built in](https://code.claude.com/docs/en/sandboxing), off by default | [Seatbelt, Docker or Podman, gVisor and two more](https://geminicli.com/docs/cli/sandbox/); off until you pass `--sandbox` or set it in `settings.json` |
| Project instructions | `CLAUDE.md`, or `AGENTS.md` when there's no `CLAUDE.md` | `GEMINI.md` by default |
| Source | Closed | Open source under Apache 2.0 |

The row I'd look at first is undoing edits. Claude Code snapshots the files its edit tools change from the first session on, and Gemini CLI snapshots the whole project only after you enable checkpointing in `settings.json`.

## What does plan mode do in each?

Both tools' plan modes let the agent read and propose while edits are held back. Claude Code's docs say that in plan mode Claude "reads files, runs shell commands to explore, and writes a plan, but does not edit your source".

Gemini CLI's Plan Mode allows fewer tools. Its docs list the only tools allowed: file reads, search, read-only MCP tools, and writes to the plan's own Markdown file, and `run_shell_command` isn't on the list.

Whether a planner can run shell commands decides what the plan is based on.

Claude Code can run `npm test` while planning and see which tests fail. Gemini CLI in Plan Mode reads the test files and infers what would fail, unless you add a policy rule that allows that one command.

Claude Code has six permission modes. A new install on v2.1.283 or later starts in `auto`, where a classifier reviews each action in place of a prompt, while `default` asks you before edits and commands and `bypassPermissions` asks about nothing.

The docs recommend `bypassPermissions` for "Isolated containers and VMs only", and I'd follow that advice to the letter.

## How does undo work, and what does it miss?

Both tools snapshot your files so you can go back to an earlier state, and they differ in what a snapshot covers. Claude Code keeps snapshots for the 100 latest checkpoints in a session and restores them with `/rewind`.

Claude Code's docs state the limits of checkpoints, which I appreciate. A file that was changed only by a shell command, such as a file rewritten by a formatter, isn't tracked, and the docs say plainly that checkpoints are "Not a replacement for version control".

Gemini CLI snapshots the whole project. Each checkpoint is a commit in a shadow Git repository under `~/.gemini/history/`, taken when you approve a tool that modifies files, and `/restore` reverts every file in the project to that commit.

So I'd make a Git commit before a long run with either tool. Claude Code's `/rewind` leaves alone any file that only a shell command changed, and Gemini CLI takes no checkpoint during a turn that only runs shell commands.

## Which one should you pick for a refactor?

I don't have evidence for a universal winner, and I'd distrust any page that named one without publishing the run it's based on.

For a refactor that crosses several files, Claude Code has undo on from the first prompt, and you can switch to plan mode to review its plan before any edit. Gemini CLI can also edit, run your tests and fix what fails without stopping, and a green run from either tool proves only what your tests check.

If you have access to both tools, run both on the same task from the same commit and judge the two patches with the same tests. The model matters as much as the interface, and [which LLM to use for coding](/articles/best-llms-for-coding/) is a separate choice.

Claude Code and Gemini CLI also share one setup step. Each tool reads a project instruction file at the start of a session, `CLAUDE.md` for Claude Code and `GEMINI.md` for Gemini CLI, and [coding agent memory](/articles/coding-agent-memory/) covers what to put in that file.

## FAQ

**Is Gemini CLI discontinued?**

Gemini CLI is discontinued for Google's consumer plans and free use, and still works with an enterprise licence or a paid API key. Google stopped serving Gemini CLI requests for its Pro and Ultra plans and for free use on June 18, 2026, and kept Gemini CLI available for enterprise licences and paid API keys.

**What replaced Gemini CLI?**

Antigravity CLI replaced Gemini CLI. Google's announcement says Antigravity CLI is built in Go and shares an agent harness with the Antigravity desktop application.

**Is Gemini CLI open source?**

Yes. Its GitHub repository is published under the Apache 2.0 licence.

**Does Claude Code have a sandbox?**

Yes, Claude Code has a sandbox for shell commands, and the sandbox is off by default. On macOS the sandbox uses the built-in Seatbelt framework, and on Linux it relies on `bubblewrap`.

**Can either tool undo its changes?**

Both can. Claude Code does it automatically for files its edit tools changed, with `/rewind`, and Gemini CLI restores the whole project with `/restore`, once you've enabled checkpointing in `settings.json`.
