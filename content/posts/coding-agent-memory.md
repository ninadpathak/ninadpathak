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
description: 'A coding agent forgets between sessions because the model keeps no state. What Claude Code, Codex, Gemini CLI and Cursor each load back in, from their docs.'
slug: coding-agent-memory
status: published
work_note: 'Mem0 sells memory for agents, and I joined it in February 2026 to run its writers. That makes me an interested party on why coding agents forget, and [my portfolio](/portfolio/) shows the work.'
title: 'Why Your Coding Agent Keeps Forgetting Everything: Memory Persistence in AI
  Coding Assistants'
updated: 2026-11-17
---

A coding agent forgets everything in a new session because the model keeps nothing between sessions. What looks like memory is a file that the tool reads back in at the start of each one.

HTTP had this problem first. [Wikipedia's history of the cookie](https://en.wikipedia.org/wiki/HTTP_cookie) dates the fix to June 1994 at Netscape, a small piece of data that the browser sends back "with every request, introducing states (memory of previous events) into otherwise stateless HTTP transactions."

A server sets its own cookie, and the file a coding agent reads is one that you write. On the pages cited below, only Claude Code's describes the agent adding notes of its own, which is the main difference among the four [coding agents](/articles/coding-agents/) compared here.

## Why does a coding agent forget between sessions?

Because the model has no memory of its own, and the session is the only place the conversation was held. Cursor's [documentation on rules](https://cursor.com/docs/rules) says it without decoration.

"Large language models don't retain memory between completions. Rules provide persistent, reusable context at the prompt level."

Anthropic's docs put the same fact as the first line of [their memory page](https://code.claude.com/docs/en/memory): "Each Claude Code session begins with a fresh context window." A decision made on Tuesday reaches Wednesday's session only if it was written to a file the tool loads.

## What does each tool carry into a new session?

Each of the four reads instruction files from a personal location and from the project. The table is taken from each vendor's documentation as it read on November 17, 2026.

| Tool | File you write | Personal location | Loading rule the docs state |
| --- | --- | --- | --- |
| Claude Code | `CLAUDE.md`, or an existing `AGENTS.md` | `~/.claude/CLAUDE.md` | Files above the working directory load at launch |
| Codex | `AGENTS.md` | `~/.codex/AGENTS.md` | Read "once per run", up to 32 KiB combined by default |
| Gemini CLI | `GEMINI.md` | `~/.gemini/GEMINI.md` | Concatenated and sent "to the model with every prompt" |
| Cursor | Rules in `.cursor/rules`, or `AGENTS.md` | User rules, "Global to your Cursor environment" | Included "at the start of the model context" when applied |

Codex and Claude Code both state a hard size limit. Codex's [AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md) stops adding files "once the combined size reaches the limit defined by `project_doc_max_bytes` (32 KiB by default)", so a long file near the root can crowd out a nearer one.

Claude Code's memory page sets its limit per file, for instruction files that load on demand: 40,000 characters in a session with a 200K context window. A file over the limit reaches the model only in part, with a note telling it to read the rest.

Gemini CLI's [page on GEMINI.md](https://geminicli.com/docs/cli/gemini-md/) carries a banner saying that unpaid users were moved to another tool in June 2026. I've kept the row because the file convention is the point of comparison.

## Which of them takes notes for you?

Claude Code does, and the other pages cited here describe only files that a person writes. Anthropic calls the feature auto memory and describes it as "notes Claude writes itself based on your corrections and preferences".

Those notes stay on the machine that wrote them, and only the top of their index loads into a session. The limits are set out in the guide to [Claude Code's memory files](/articles/claude-code-memory/).

An agent that writes its own notes will also write wrong ones. Whichever tool you use, a note that is loaded every session is trusted every session, so the files need the review any shared document gets.

## Can one file serve every tool?

For instructions, yes. [AGENTS.md](https://agents.md/) describes itself as "A simple, open format for guiding coding agents, used by over 60k open-source projects", and asks you to "Think of AGENTS.md as a README for agents".

Codex and Cursor read it by name, and Anthropic's memory page says Claude Code can read it "so a repository already set up for other coding agents works without adding a `CLAUDE.md`". The site says the format "is now stewarded by the Agentic AI Foundation under the Linux Foundation."

So a team using several tools can keep one instruction file. What stays tool-specific is everything beyond instructions, such as Cursor's path-scoped rules and Claude Code's auto memory.

## Is forgetting inside a session the same problem?

No. A long session can lose its own early turns once the context window fills, because the harness has to drop or summarize something to make room.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/coding-agent-memory/sliding-window.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/coding-agent-memory/sliding-window.narrow.svg" width="288" height="200"><img class="np-has-narrow" src="/static/images/diagrams/coding-agent-memory/sliding-window.svg" width="720" height="232" alt="A row of conversation turns with the context window bracketed over the latest ones. As each new turn is appended on the right, the oldest turns fall off the left edge and out of the model's view." loading="lazy" decoding="async"></picture></a>
  <figcaption>Each new turn joins on the right in a harness that truncates, and the oldest fall out of the model's view.</figcaption>
</figure>

That loss happens with every instruction file loaded and working. [Short-term memory for agents](/articles/short-term-agent-memory/) covers it, including which instructions survive a compaction.

## What about the conversation itself?

The transcript is on disk, and no tool reads it back by default. Ellie Huxtable made the point when announcing [Atuin Threads](https://blog.atuin.sh/threads-agent-sessions/) on October 27, a feature that syncs agent sessions between machines.

"Agent sessions store the lot of it. Every command, its output, my intent, and everything I tried along the way to the eventual solution."

Her complaint is that the record goes unused: "while my shell history follows me everywhere, my agent sessions do not." The tool's answer is to make sessions searchable and resumable, including in a different agent from the one that started them.

I think that is the right layer to add next, and it is a different thing from memory. A resumed session brings back everything, and a memory file holds the few lines that were worth keeping.

## How do you check what your agent remembers?

Ask the tool to show what it loaded. Each one has a way.

- Claude Code: `/memory` lists the instruction and memory files in the session.
- Codex: the guide suggests `codex --ask-for-approval never "Summarize the current instructions."`
- Gemini CLI: `/memory show` prints the combined context.

If a rule you care about is absent from that output, the agent never had it. If it is present and ignored, the file is too long or the rule too vague, and [the CLAUDE.md guide](/articles/claude-md/) has the fixes.

For work that spans sessions, write the handoff yourself before closing the terminal: what is done, what is next, and what was decided. [Memory serialization](/articles/memory-serialization/) covers the general form of that note.

## FAQ

**Why does my coding agent forget everything when I start a new session?**

The model keeps no state between sessions. Only the instruction files the tool loads, and any notes the tool saves, carry over.

**Does AGENTS.md work in Claude Code?**

Yes. Anthropic's memory documentation says Claude Code can read an existing `AGENTS.md` as the project instructions.

**Is a resumed session the same as memory?**

No. Resuming reloads one conversation, and memory is a small set of notes that every later session reads.
