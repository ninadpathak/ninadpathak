---
category: coding-agents
primary_query: claude code memory
bridges:
- slug: agent-harnesses
  reason: A coding agent is one agent loop with a harness around it.
- slug: llm-context-windows
  reason: Context limits and token cost decide how a coding agent is configured.
- slug: multi-agent-vs-single-agent
  reason: A coding agent is one agent loop with a harness around it.
- slug: agent-error-handling
  reason: A coding agent is one agent loop with a harness around it.
date: 2026-04-19
description: 'Claude Code memory is two sets of files read into each new session: CLAUDE.md files you write and auto memory Claude writes. Where they live and what loads.'
status: published
work_note: 'I ran a team of 13 writers at Mem0, which sells a memory layer for agents, so I have a commercial reason to care what Claude Code remembers without one. Read this with that in mind. [My portfolio](/portfolio/) has the case study.'
title: How Memory Works in Claude Code
updated: 2026-11-17
slug: claude-code-memory
video: claude-code-memory
---

Leonard Shelby, the lead of Christopher Nolan's Memento, can't form new long-term memories, and [Wikipedia's summary of the film](https://en.wikipedia.org/wiki/Memento_(film)) says he gets by on "an elaborate system of photos, notes, and tattoos". Claude Code is built the same way, and Anthropic's [memory documentation](https://code.claude.com/docs/en/memory) opens with the condition: "Each Claude Code session begins with a fresh context window."

Claude Code memory is the set of files that get read into that fresh window. There are two kinds, `CLAUDE.md` files that you write and auto memory that Claude writes for itself, and everything else from the last session is gone.

The parallel breaks where the film gets its plot. Leonard can't inspect his own system from outside, and you can open every one of these files, since the docs describe auto memory as "plain markdown you can edit or delete at any time."

## What does Claude Code remember between sessions?

It remembers what is in two sets of files, and the docs compare them in one table. I've kept four of its rows.

| | CLAUDE.md files | Auto memory |
| --- | --- | --- |
| Who writes it | You | Claude |
| What it contains | Instructions and rules | Learnings and patterns |
| Scope | Project, user, or org | Per repository, shared across worktrees |
| Loaded into | Every session | Every session (first 200 lines or 25KB) |

The conversation is in neither column. A decision reached in yesterday's session exists today only if you put it in `CLAUDE.md` or Claude chose to save it.

That choice is Claude's, and it is selective. The docs say "Claude doesn't save something every session", and that it skips what it can work out from the code.

## Where do the files live?

Instruction files load from four scopes, and a session reads all that apply.

| Scope | Location | Who sees it |
| --- | --- | --- |
| Managed policy | A system path such as `/etc/claude-code/CLAUDE.md` on Linux | Everyone in the organization |
| User | `~/.claude/CLAUDE.md` | You, in every project |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | The team, through source control |
| Local | `./CLAUDE.local.md` | You, in this project |

Files above the working directory load at launch, and the docs add that "Files in subdirectories load on demand." A repository that already has an `AGENTS.md` for other tools works too, since Claude Code can read it as the project instructions.

Auto memory sits outside the repository, in `~/.claude/projects/<project>/memory/`. A `MEMORY.md` file indexes the directory, with one topic file for each memory.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/claude-code-memory/memory-sources.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/claude-code-memory/memory-sources.narrow.svg" width="288" height="472"><img class="np-has-narrow" src="/static/images/diagrams/claude-code-memory/memory-sources.svg" width="720" height="416" alt="A Claude Code session reads from three sources. CLAUDE.md files, written by you, load at launch from the managed, user, project and local scopes. Auto memory, a MEMORY.md index with topic files that Claude Code writes as it works, also loads at launch. Context passed on the command line lasts for that session only." loading="lazy" decoding="async"></picture></a>
  <figcaption>Instruction files above the working directory load at launch, and auto memory loads the first 200 lines of its index.</figcaption>
</figure>

The location has a consequence the docs state in four words: "Auto memory is machine-local." What Claude learned on a laptop is absent from a cloud session and from a colleague's checkout, so anything the team needs belongs in the project file.

## How much of it gets loaded?

For auto memory, only the top of the index. "The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first, are loaded at the start of every conversation", and the topic files are read when Claude decides it needs them.

Instruction files load whole, which is why the docs ask you to "target under 200 lines per CLAUDE.md file." Their reason is that "Longer files consume more context and reduce adherence."

My [CLAUDE.md guide](/articles/claude-md/) covers what earns a line in that budget.

## Is memory a rule or a suggestion?

It is a suggestion, and I think this is the sentence in the docs to read first: "Claude treats them as context, not enforced configuration."

The mechanism explains it. "CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself", so an instruction there competes with everything else in the window, and the docs warn that when two instructions conflict "Claude may pick one arbitrarily."

For something that must never happen, the docs point away from memory and toward a hook that blocks the action before it runs. A memory file is the right place for how the team works and the wrong place for a guarantee.

## What survives a long session?

The project file does. When a session fills its window and is compacted, "Project-root CLAUDE.md survives compaction: after `/compact`, Claude re-reads it from disk and re-injects it into the session."

An instruction given only in conversation has no such protection, which is the failure [short-term memory for agents](/articles/short-term-agent-memory/) works through. The reload itself has had bugs, and the [changelog](https://code.claude.com/docs/en/changelog) entry for version 2.1.311 on October 26 reads "Fixed Claude seeing stale MEMORY.md and CLAUDE.md content right after automatic compaction when those files were edited earlier in the session".

## What goes wrong with it?

Stale notes go wrong, because a note is trusted. Nolan said of Memento's audiences, in an interview the Wikipedia article quotes, that they had spent the film looking at a captioned photograph and "they still prefer to trust that image" after the film had shown it to be unreliable.

A model reading `MEMORY.md` is in the same position. A line saying the project uses one package manager will be followed after the project has moved to another.

The maintenance is a pair of commands. `/memory` lists the files a session has loaded and opens them for editing, and `/doctor prompt-audit` has Claude look for "references to files or commands that don't exist, and files that contradict each other."

My work for Mem0, which sells a memory layer for agents, gives me a stake here, so weigh this accordingly: for one developer on one machine, I think the two file types are enough. The limits appear with a team, since auto memory doesn't travel, and with other tools, which [coding agent memory](/articles/coding-agent-memory/) compares.

A [subagent](/articles/claude-code-subagents/) starts with its own fresh window and can be given a separate memory directory. How the wider set of options is layered is the subject of [AI memory management](/articles/ai-memory-management/).

## FAQ

**Does Claude Code remember previous conversations?**

No. Each session starts with a fresh context window, and only `CLAUDE.md` files and auto memory carry over.

**Where does Claude Code store memory?**

Instruction files live in the project and in `~/.claude/`. Auto memory lives in `~/.claude/projects/<project>/memory/` on the machine where it was written.

**Can I turn auto memory off?**

Yes. Open `/memory` and use the toggle, or set `autoMemoryEnabled` to false in the project's settings.
