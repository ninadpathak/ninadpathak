---
category: coding-agents
primary_query: claude code memory
siblings:
- claude-md
- coding-agent-memory
- claude-code-subagents
bridges:
- slug: short-term-agent-memory
  reason: Instructions given only in conversation are lost at compaction, which that page works through.
- slug: ai-memory-management
  reason: Claude Code's two file types are one case of the layering that page describes.
date: 2026-04-19
description: 'Claude Code memory is two sets of files read into each new session: CLAUDE.md files you write and auto memory Claude writes. Where they live and what loads.'
status: published
work_note: 'This page is my reading of how Claude Code keeps memory in plain files, checked against Anthropic''s documentation on the day I wrote it. For the developer content I''ve published, see [my portfolio](/portfolio/).'
title: How Memory Works in Claude Code
updated: 2026-11-17
slug: claude-code-memory
---

Claude Code memory is a set of files read into each new session. There are two kinds, `CLAUDE.md` files that you write and auto memory that Claude writes for itself, and unless you resume the old conversation, nothing else carries over.

Anthropic's [memory documentation](https://code.claude.com/docs/en/memory) opens with the reason: "Each Claude Code session begins with a fresh context window." 

Leonard Shelby, in Christopher Nolan's 2000 film Memento, can't form new memories, and in [Wikipedia's summary](https://en.wikipedia.org/wiki/Memento_(film)) he gets by on "an elaborate system of photos, notes, and tattoos".

So what goes wrong for Leonard? He trusts whatever his notes say, and by the film's end he is, in that summary's words, "willing to lie to himself to be happy".

Keeping the notes true is the standing chore for anyone whose [coding agents](/articles/coding-agents/) remember things, and it's where this page ends up.

## What does Claude Code remember between sessions?

It remembers what is in two sets of files, and the docs compare them row by row.

| | CLAUDE.md files | Auto memory |
| --- | --- | --- |
| Who writes it | You | Claude |
| What it contains | Instructions and rules | Learnings and patterns |
| Scope | Project, user, or org | Per repository, shared across worktrees |
| Loaded into | Every session | Every session (first 200 lines or 25KB) |

Notice that the conversation is in neither column. So a decision you reached in yesterday's session exists today only if you put it in `CLAUDE.md` or Claude chose to save it.

And that choice is Claude's, which makes it selective. The docs say "Claude doesn't save something every session", and that it skips what it can work out from the code.

A third input, text passed with a launch flag, lasts only for the session it starts.

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

Now, that location has a consequence: "Auto memory is machine-local." What Claude learned on your laptop is absent from a cloud session and from a colleague's checkout, so anything the team needs belongs in the project file.

## How much of it gets loaded?

For auto memory, only the top of the index. "The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first, are loaded at the start of every conversation", and the topic files are read when Claude decides it needs them.

Instruction files that load at launch come in whole, "as long as the file is 4 MiB or smaller", and files that load on demand are cut off at 40,000 characters in a 200K session. But the number to aim for is far lower, since the docs ask you to "target under 200 lines per CLAUDE.md file."

Why so short? Their reason is that "Longer files consume more context and reduce adherence."

What earns a line in that budget is the subject of my [CLAUDE.md guide](/articles/claude-md/).

## Is memory a rule or a suggestion?

It is a suggestion. The docs say of both file types that "Claude treats them as context, not enforced configuration", and I'd read that sentence before any other on the page.

Here's why. "CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself", so an instruction there competes with everything else in the window, and the docs warn that when two instructions conflict "Claude may pick one arbitrarily."

For something that must never happen, the docs point away from memory and toward a hook that blocks the action before it runs. A memory file is the right place for how the team works and the wrong place for a guarantee.

## What survives a long session?

The project file does. When a session fills its window and is compacted, "Project-root CLAUDE.md survives compaction: after `/compact`, Claude re-reads it from disk and re-injects it into the session."

An instruction given only in conversation has no such protection, which is the failure [short-term memory for agents](/articles/short-term-agent-memory/) works through. The reload itself has had bugs, and the [changelog](https://code.claude.com/docs/en/changelog) entry for version 2.1.311 on October 26 reads "Fixed Claude seeing stale MEMORY.md and CLAUDE.md content right after automatic compaction when those files were edited earlier in the session".

## What goes wrong with it?

Stale notes go wrong, because a note is trusted. Nolan said of Memento's audiences, in an interview the Wikipedia article quotes, that they had spent the film looking at a captioned photograph and "they still prefer to trust that image" after the film had shown it to be unreliable.

A model reading `MEMORY.md` is in the same position. A line saying the project uses one package manager will be followed after the project has moved to another.

So how do you catch a stale note? For auto memory the docs give each file a `modified` date and say "The timestamp shows how current the fact is, both to you and to Claude when it reads the memory back."

The commands split the same way. `/context all` shows which files a session loaded and `/memory` opens them for editing, and for the instruction files `/doctor prompt-audit` has Claude look for "references to files or commands that don't exist, and files that contradict each other."

My time managing the writers at Mem0, which sells a memory layer for agents, gives me a stake in this, so weigh what follows accordingly. For one developer on one machine, I think the two file types are enough.

The limits appear with a team, since auto memory doesn't travel, and with other tools, which [coding agent memory](/articles/coding-agent-memory/) compares.

A [subagent](/articles/claude-code-subagents/) starts with its own fresh window and can be given a separate memory directory. How the wider set of options is layered is the subject of [AI memory management](/articles/ai-memory-management/).

## FAQ

**Does Claude Code remember previous conversations?**

Not unless you resume one. A new session starts with a fresh context window, and only `CLAUDE.md` files and auto memory carry over.

**Where does Claude Code store memory?**

Instruction files live in the project and in `~/.claude/`. Auto memory lives in `~/.claude/projects/<project>/memory/` on the machine where it was written.

**Can I turn auto memory off?**

Yes. Open `/memory` and use the toggle, or set `autoMemoryEnabled` to false in the project's settings.
