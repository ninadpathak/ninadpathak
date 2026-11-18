---
category: coding-agents
primary_query: coding agent memory
siblings:
- claude-code-memory
- claude-md
bridges:
- slug: memory-serialization
  reason: A handoff note written before closing a session is a small case of serialized state.
- slug: short-term-agent-memory
  reason: Forgetting inside one session is a separate failure, covered there.
date: '2026-05-06'
description: 'Coding agent memory compared across Claude Code, Codex, Gemini CLI and Cursor: the files each loads into a new session, and which ones write their own notes.'
slug: coding-agent-memory
status: published
work_note: "Explainers like this one are what I write for AI companies as a freelance technical writer. I'm Ninad Pathak, and I run the product before I write about it. [Let's work on yours](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Why Your Coding Agent Keeps Forgetting Everything: Memory Persistence in AI
  Coding Assistants'
updated: 2026-11-17
---

A coding agent forgets everything when you start a new session because the model keeps nothing between sessions. Coding agent memory is whatever files the tool reads back in at the start of the next one, and the four tools compared here differ on who writes those files.

A `.env` file is one you write once and a program reads on every start. The [dotenv README](https://github.com/motdotla/dotenv) describes a module "that loads environment variables from a `.env` file".

A coding agent's instruction file is written by you and read by the tool at the start of each session. Claude Code, Codex and Gemini CLI now add something a `.env` file never had, which is notes the agent writes for itself.

Cursor, the fourth of the [coding agents](/articles/coding-agents/) compared here, doesn't. So I'll go through what each tool loads, which ones take notes, and how you can check what yours has in front of it.

## Why does a coding agent forget between sessions?

A coding agent forgets because the model has no memory of its own, and the session is the only place the conversation was held. Cursor's [documentation on rules](https://cursor.com/docs/rules) says "Large language models don't retain memory between completions."

Anthropic's [memory page](https://code.claude.com/docs/en/memory) opens on the same fact: "Each Claude Code session begins with a fresh context window." So a decision you made on Tuesday reaches Wednesday's session only if it got written to a file the tool loads.

## What does each tool carry into a new session?

Each of the four reads instruction files you write, and all but Cursor can also write notes of their own. Every cell comes from the vendor's documentation as it read on November 17, 2026.

| Tool | File you write | Notes the agent writes | Default |
| --- | --- | --- | --- |
| Claude Code | `CLAUDE.md`, falling back to `AGENTS.md` | Auto memory, a `MEMORY.md` index with topic files | On in local sessions |
| Codex | `AGENTS.md` | Memories generated from earlier chats | Off |
| Gemini CLI | `GEMINI.md` | A memory tool that edits its Markdown files, plus Auto Memory | Auto Memory off |
| Cursor | Rules in `.cursor/rules`, or `AGENTS.md` | None documented | |

Codex and Claude Code both state a size limit on the files you write. Codex's [AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md) stops adding files "once the combined size reaches the limit defined by `project_doc_max_bytes` (32 KiB by default)", so a long `AGENTS.md` at the repository root can use up the 32 KiB before Codex reaches the file in the directory you're working in.

Claude Code loads the whole of an instruction file at launch as long as the file is 4 MiB or smaller. Files that load on demand, such as a `CLAUDE.md` in a subdirectory, have a tighter limit of 40,000 characters in a session with a 200K context window.

An on-demand file over 40,000 characters reaches the model only in part, with a note telling it to read the rest.

## Which of them takes notes for you?

Claude Code, Codex and Gemini CLI all do, and they disagree about how much to trust the agent with it.

Claude Code trusts the agent furthest, with auto memory on by default. Anthropic describes it as "notes Claude writes itself based on your corrections and preferences", and [my guide to Claude Code's memory files](/articles/claude-code-memory/) goes through how much of it loads.

Codex makes you opt in. Its [Memories page](https://learn.chatgpt.com/docs/customization/memories) says "Local Codex memories are off by default", and once enabled, "Codex can turn useful context from eligible prior chats into local memory files."

Gemini CLI splits the job in two. Its [memory tool](https://geminicli.com/docs/tools/memory) "persists durable facts, user preferences, and project details by editing Markdown memory files directly", and a separate feature called [Auto Memory](https://geminicli.com/docs/cli/auto-memory/) mines old sessions for more.

Auto Memory is the cautious one. Its page calls it "an experimental feature", says "Auto Memory is off by default", and holds every proposed note "in a project-local inbox until you approve or discard them."

And Cursor? Its documentation describes rules, which people write, and has no page for agent-written memory.

An agent that writes its own notes will also write wrong ones, and a note that loads every session gets trusted every session, so the review step Gemini builds in is one you'd want to do by hand in the other two.

## Can one file serve every tool?

A single file can serve every tool for instructions, with a condition for Claude Code and Gemini CLI. [AGENTS.md](https://agents.md/) describes itself as "A simple, open format for guiding coding agents, used by over 60k open-source projects", and the site says the format "is now stewarded by the Agentic AI Foundation under the Linux Foundation."

Codex and Cursor read it by name. Claude Code reads it too, with a condition the docs spell out: "By default, Claude reads `AGENTS.md` only when you have no `CLAUDE.md` in your working directory or above it."

So if your repository has both files, Claude Code uses `CLAUDE.md` and ignores the other unless you import it or change the Project instructions setting. Gemini CLI needs a setting, since `GEMINI.md` is its default name and the `context.fileName` property is where you add `AGENTS.md`.

Those two tools differ on permissions and undo as well, which [Claude Code vs Gemini CLI](/articles/claude-vs-gemini-cli/) compares.

So one shared `AGENTS.md` works once Claude Code and Gemini CLI are pointed at it. [The CLAUDE.md guide](/articles/claude-md/) has the one-line import that makes Claude Code read the shared file.

## Is forgetting inside a session the same problem?

No. A long session can lose its own early turns once the context window fills, because the harness has to drop or summarize something to make room.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/coding-agent-memory/sliding-window.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/coding-agent-memory/sliding-window.narrow.svg" width="288" height="200"><img class="np-has-narrow" src="/static/images/diagrams/coding-agent-memory/sliding-window.svg" width="720" height="232" alt="A row of conversation turns with the context window bracketed over the latest ones. As each new turn is appended on the right, the oldest turns fall off the left edge and out of the model's view." loading="lazy" decoding="async"></picture></a>
  <figcaption>Each new turn joins on the right in a harness that truncates, and the oldest fall out of the model's view.</figcaption>
</figure>

That loss happens even when every instruction file has loaded correctly. [Short-term memory for agents](/articles/short-term-agent-memory/) explains which instructions survive a compaction.

## What about the conversation itself?

The transcript is on disk in every one of these tools, and two of them have started reading it back. Codex builds its memories from prior chats, and Gemini's Auto Memory page says it "scans those transcripts for durable facts".

A third approach leaves the transcript whole. Ellie Huxtable announced [Atuin Threads](https://blog.atuin.sh/threads-agent-sessions/) on October 27, a feature that syncs agent sessions between machines, with the complaint that "while my shell history follows me everywhere, my agent sessions do not."

She adds that the record is already complete: "Agent sessions store the lot of it. Every command, its output, my intent, and everything I tried along the way to the eventual solution."

So a tool now has a choice of what to do with an old conversation: distill it into notes without asking, propose notes for you to approve, or keep it searchable and resumable. I'd take a tool that proposes notes, or one that keeps the transcript searchable, over one that distills without asking, because both leave a person able to see what was kept.

## How do you check what your agent remembers?

Ask the tool to show what it loaded, and each one has a command for that.

- Claude Code: `/context all` lists the loaded files under Memory files, and `/memory` opens them for editing.
- Codex: the guide suggests `codex --ask-for-approval never "Summarize the current instructions."`
- Gemini CLI: `/memory show` prints the combined context.

If a file you care about is missing from that output, the agent never had it. And for work that spans sessions, write the handoff yourself before you close the terminal: what's done, what's next, and what was decided.

That note is a small piece of serialized state, and [memory serialization](/articles/memory-serialization/) describes the general form.

## FAQ

**Why does my coding agent forget everything when I start a new session?**

The model keeps no state between sessions. Only the instruction files the tool loads, and any notes the tool has saved, carry over.

**Which coding agents write their own memory?**

Claude Code does by default. Codex does once you enable memories, and Gemini CLI has a memory tool plus an experimental Auto Memory feature that asks for approval.

**Does AGENTS.md work in Claude Code?**

Yes, when the repository has no `CLAUDE.md`. If both exist, Claude Code reads `CLAUDE.md`, which can import the other file.

**Is a resumed session the same as memory?**

No. Resuming reloads one conversation, and memory is a small set of notes that every later session reads.
