---
title: "How Memory Works in Claude Code: A Deep Dive into Anthropic's Coding Agent"
date: 2026-04-19
description: "An in-depth exploration of how Claude Code stores, retrieves, and forgets information across sessions, and how to leverage its memory architecture for better workflows."
tags: [ai, claude, agents, memory, anthropic, coding]
status: published
---

You open Claude Code on Monday. It knows your Express API routes. You close it. You reopen it on Thursday. It still knows your Express API routes. But ask it what you were working on at 2 PM on Tuesday and it draws a blank. That inconsistency is not a bug. It is the intended behavior of a layered memory system that Anthropic built specifically to handle the gap between ephemeral conversation context and persistent project knowledge.

I spent the last few weeks digging into how Claude Code actually remembers things, what it stores where, and why some information survives session boundaries while other stuff vanishes the moment you close the terminal. The architecture is more sophisticated than most people realize. Here is what I found.

## The Three-Layer Memory Architecture

Claude Code does not have one memory system. It has three distinct layers that operate at different timescales and serve different purposes. Understanding which layer owns what piece of information is the key to making Claude Code work with you instead of against you.

**Project-level memory lives in CLAUDE.md files.** These are markdown files you write and place in specific locations. They persist indefinitely, survive sessions, and load into every conversation until you change them. This is the most durable form of memory Claude Code has.

**Session-level memory lives in auto memory.** Claude Code writes these notes itself. It captures learnings from your corrections, build commands it discovers, debugging patterns it observes. This auto memory lives in `.claude/auto-memory.md` and is limited to 200 lines or 25KB per working tree. It survives sessions but undergoes periodic consolidation that can drop older or lower-priority entries.

**Conversation-level memory is the context window.** This is everything in your current session. The history, the files you have open, the commands you ran, the errors you hit. This vanishes when you close the session. There is no recovering it.

The official documentation puts it plainly: each session begins with a fresh context window. The mechanisms that carry knowledge across sessions are CLAUDE.md files and auto memory. Everything else is temporary.

### Project Memory: The CLAUDE.md System

The primary vehicle for project-level memory is the CLAUDE.md file. You write it in plain markdown. Claude reads it at the start of every session. The file sits in one of several locations depending on what scope you want it to have.

The project-level CLAUDE.md lives at `./CLAUDE.md` or `./.claude/CLAUDE.md` in your repository root. This file gets shared with your team through version control, so it should contain project-wide standards that anyone working on the codebase needs to know. Build commands, test instructions, coding conventions, architectural decisions, naming standards. The `/init` command can generate a starter CLAUDE.md by analyzing your codebase structure and tech stack.

Personal preferences go in `~/.claude/CLAUDE.md`. This file applies to every project you work on. The documentation gives the example of code styling preferences or personal tooling shortcuts.

Local overrides that should not be committed to version control go in `./CLAUDE.local.md`. This file is gitignored by convention. It lives at the project root and contains your sandbox URLs, preferred test data, or other settings that do not belong in the shared project context.

For organization-wide rules managed by IT or DevOps, there is a managed policy location. On macOS this is `/Library/Application Support/ClaudeCode/CLAUDE.md`. On Linux and WSL it is `/etc/claude-code/CLAUDE.md`. On Windows it is `C:\Program Files\ClaudeCode\CLAUDE.md`. These load for every user in the organization.

When you have CLAUDE.md files at multiple levels, more specific locations take precedence. A local `./CLAUDE.local.md` overrides a project `./CLAUDE.md` which overrides a user `~/.claude/CLAUDE.md`. The resolution order follows standard filesystem precedence.

### Session Memory: Auto Memory and Consolidation

Auto memory is where Claude Code becomes interesting. Unlike CLAUDE.md which you write, auto memory is synthesized by Claude itself based on your corrections, preferences, and discoveries during a session.

The auto memory file lives at `.claude/auto-memory.md` within each working tree. It captures things like build commands you used successfully, debugging patterns that worked, mistakes Claude made that you corrected, and preferences you expressed repeatedly. The documentation describes it as "learnings and patterns" versus CLAUDE.md which is "instructions and rules."

Auto memory loads into every session for that working tree. But here is the important part: it only loads the first 200 lines or 25KB, whichever limit it hits first. This is a hard constraint. Claude consolidates auto memory periodically to stay within this limit.

The consolidation process, sometimes internally referred to as memory compaction or auto-dream consolidation, runs in the background. It resolves contradictions, deletes outdated entries, and keeps the memory concise. The trigger factors include time elapsed and the number of new sessions since the last consolidation. The goal is to keep the most relevant recent learnings while pruning stale information.

This is the layer that causes the frustration people describe as "Claude forgets things." It does not forget randomly. It consolidates. Lower-priority learnings get dropped when space runs out. If you spent three sessions debugging a tricky race condition and then did not reference it for two weeks, that entry might get pruned during consolidation.

### Conversation Memory: The Context Window

The context window is the working memory of any given session. It holds the full conversation history, loaded files, tool outputs, system instructions, and everything Claude is actively reasoning about. Claude 3.5 Sonnet supports a 200,000 token context window. Opus 4.7, released April 16, 2026, supports 200,000 tokens as well. Claude Code also has access to a one million token context window in beta for Sonnet 4.

The context window is a shared resource. As it fills up, performance degrades. This phenomenon is called "context rot." Claude Code proactively compacts its context window, sometimes triggering compaction around 64 to 75 percent usage to preserve enough working memory for planning and evaluation.

You can manually trigger compaction at natural task boundaries using the `/compact` command. This lets you reset context efficiency without ending the session.

## What Gets Remembered and What Gets Forgotten

The distinction matters more than most documentation makes it. Here is the explicit breakdown.

**Remembered across sessions:**
- Everything in your CLAUDE.md files at any scope level
- Auto memory entries that survived consolidation
- Project structure and file layout (from filesystem scanning)
- Coding standards and conventions from CLAUDE.md
- Build and test commands discovered and stored in auto memory

**Forgotten between sessions:**
- Conversation history from previous sessions
- Files you had open but did not reference in CLAUDE.md or auto memory
- Debugging context from prior sessions unless it made it into auto memory
-临时 notes or thoughts you did not write down
- What you were working on at 2 PM on Tuesday unless it became a stored learning

This is why you can ask Claude Code about your Express API routes on Thursday and get a coherent answer, but asking what you were debugging on Tuesday produces something like "I do not have information about that."

The architecture is designed around project knowledge, not personal journaling. If you want something remembered, you have to put it in CLAUDE.md or have it surface naturally as a pattern strong enough to survive auto memory consolidation.

## How to Manually Add Memory to Claude Code

You have several tools for this. The right one depends on the type of information and how widely you want it shared.

**Write or update CLAUDE.md directly.** The simplest approach. Open your project root and create or edit `./CLAUDE.md`. Write instructions that you want Claude to follow in every session. The documentation recommends treating CLAUDE.md as the place where you write down what you would otherwise re-explain at the start of every conversation.

When you notice Claude making the same mistake a second time, that is a signal to add it to CLAUDE.md. When a code review catches something Claude should have known about the codebase, that belongs in CLAUDE.md. When you type the same correction you typed last session, that is a CLAUDE.md entry.

Keep entries specific and concise. Claude treats these as context, not enforced configuration. The more specific and concise your instructions, the more consistently Claude follows them. Vague or rambling entries get partially ignored.

**Use the `/init` command for new projects.** Running `/init` in a fresh project directory causes Claude to analyze the codebase structure and generate a starter CLAUDE.md. It discovers build commands, test instructions, and project conventions automatically. If a CLAUDE.md already exists, `/init` suggests improvements rather than overwriting the existing file.

**Use CLAUDE.local.md for personal project overrides.** Create `./CLAUDE.local.md` at the project root and add personal settings that should not be committed. Things like your local development server URL, preferred test fixtures, or custom aliases. This file is gitignored by convention.

**Use `.claude/rules/` for path-scoped instructions.** For large projects or monorepos, you can break instructions into topic-specific files using project rules. Rules let you scope instructions to specific file types or subdirectories. The `.claude/rules/` directory can contain multiple markdown files that load on demand when Claude reads files in those directories.

**Manage auto memory directly.** The `/memory` command shows you what is currently stored in auto memory. You can view and edit entries. The `/clear-memory` command wipes auto memory for the current project if you want a clean slate.

**Use hooks for session-end capture.** Claude Code's hook system lets you register scripts that run at specific points in the session lifecycle, including at session end. These hooks can capture session transcripts, extract structured insights using Claude, and store them in an external knowledge base like Obsidian. The captured knowledge can then be fed back into future Claude Code sessions via CLAUDE.md.

The mindstudio.ai blog documents a pattern where you set up a hook that runs at session end, uses Claude to extract lessons, patterns, and decisions from the session transcript, and writes those to a daily note in Obsidian. That Obsidian note becomes project memory that you can reference in future CLAUDE.md files.

## Memory File Locations and Format

Here is the concrete structure of where Claude Code stores memory on a Linux system.

```
~/.claude/
  CLAUDE.md              # User-level instructions, applies to all projects
  auto-memory.md        # Auto-generated learnings (per working tree)

/path/to/project/
  CLAUDE.md              # Project-level instructions, version controlled
  CLAUDE.local.md        # Local overrides, gitignored
  .claude/
    CLAUDE.md            # Alternative project location
    rules/               # Path-scoped rule files
    auto-memory.md       # Auto memory for this working tree
    logs/                # Session logs
    hooks/               # Hook scripts
```

The managed policy location on Linux is `/etc/claude-code/CLAUDE.md`. This requires elevated permissions to modify and applies organization-wide.

Auto memory files use a simple markdown format. Entries are organized with headers and plain text descriptions. The file looks something like this:

```markdown
# Auto Memory

## Build Commands
- Use `pnpm dev` to start the development server
- Tests require `pnpm test` and a running database

## Debugging Patterns
- React state issues: check console for stale closures first
- API errors: always check the network tab before reading code

## Project Conventions
- Components go in `src/components`
- API routes go in `src/routes`
```

Claude consolidates this file periodically, keeping the most recent and relevant entries while pruning older ones. If you want to manually remove an entry, you can edit the file directly.

## How This Compares to Stateless AI Coding

Traditional AI coding assistants are stateless. Each conversation starts fresh. You paste context, explain the codebase, describe the problem, and get an answer. Close the tab and start over. Every session requires you to re-establish context from scratch.

Claude Code with its CLAUDE.md and auto memory system is closer to a stateful agent. It maintains project context across sessions without requiring you to re-explain fundamentals. The first time you introduce your stack, it remembers. The second time, it already knows.

This is a fundamental architectural shift. Stateless tools treat every problem as new. Stateful agents build up knowledge over time. Claude Code is in the latter category, but the state is scoped to specific files and mechanisms rather than being automatic or magical.

The tradeoff is that stateful memory requires active management. You have to write CLAUDE.md entries. You have to verify that auto memory remains accurate as the codebase evolves. A stale CLAUDE.md can cause Claude to follow outdated patterns. Auto memory can drift from reality if consolidation drops context that would have been relevant.

Stateless tools do not have this problem, but they also do not have the benefit. If you want stateless behavior from Claude Code, you can achieve it by keeping CLAUDE.md minimal and clearing auto memory regularly. If you want deep stateful memory, you invest in maintaining rich CLAUDE.md files and monitoring auto memory quality.

## Limitations of Claude Code Memory

The system is powerful but not magic. Here are the concrete limitations you will encounter.

**The 200-line auto memory cap is real.** When auto memory hits this limit, consolidation kicks in. Lower-priority learnings get dropped. If you are working on a complex project with many distinct patterns, some will get pruned. You cannot expand this limit. Your only recourse is to keep auto memory focused and rely on CLAUDE.md for information that must persist.

**Cross-project memory does not exist.** Auto memory is scoped to a specific working tree. CLAUDE.md at the user level (`~/.claude/CLAUDE.md`) applies to all projects, but it is not aware of project-specific context. If you want knowledge from one project to influence another, you have to explicitly reference it or add it to your user-level CLAUDE.md. The system does not connect project learnings automatically.

**Self-skeptical verification means memory is a hint, not a source of truth.** Claude Code verifies information against the actual codebase before acting on it. This is by design. It prevents hallucinations from stale memory. But it also means that if you refactor code significantly, auto memory entries that referenced the old structure will be treated with skepticism. Claude will prefer direct filesystem verification over trusting stored notes.

**Long-horizon planning across weeks or months is not supported.** The memory system is scoped to a project session. If you are working on a six-month refactoring effort, the system does not track your overall progress. It tracks project knowledge, not project status. You are responsible for maintaining a separate record of where you are in a long-running effort.

**CLAUDE.md is context, not memory.** Entries in CLAUDE.md are loaded into the context window at session start. This means they consume tokens. If you write a massive CLAUDE.md file, you are burning context window space on background information that may not be relevant to the current task. The documentation recommends keeping CLAUDE.md focused and using skills or path-scoped rules for specific, task-focused instructions.

**Hooks and plugins are not built-in.** The memory system covers basic needs. If you want advanced patterns like automatic Obsidian integration or cross-project memory aggregation, you need to build hooks or install plugins like claude-mem. These are not included by default.

## Best Practices for Leveraging Claude Code Memory

After working with this system extensively, here is what actually works in daily practice.

**Use `/init` on every new project.** It generates a baseline CLAUDE.md in under a minute. You get build commands, test instructions, and project conventions that Claude discovered from your codebase structure. Refine the output rather than starting from scratch.

**Write CLAUDE.md entries as context, not commands.** The documentation says Claude treats these as context, not enforced configuration. Phrase things like "Components in `src/components` follow a `.tsx` pattern" rather than "You must put all components in `src/components`." Context gets integrated naturally. Commands get partially followed and partially ignored.

**Be specific with language.** Vague instructions produce vague behavior. Instead of "follow project conventions," write "API routes follow REST conventions, use `async/await`, and return JSON with a `data` field." Specificity is the difference between Claude following your notes and Claude improvising.

**Trigger `/compact` at natural task boundaries.** Do not wait for context rot to degrade performance. After you finish a feature, fix a bug, or complete a refactoring, run `/compact` to reset context efficiency. This keeps Claude operating at full capacity for reasoning and planning.

**Review auto memory periodically.** Run `/memory` and read what Claude has stored. Verify accuracy against the current codebase. Remove outdated entries. Add missing patterns. Auto memory quality depends on active maintenance.

**Use CLAUDE.local.md for personal project settings.** Keep your sandbox URLs, test data paths, and personal tooling preferences in the local file. This keeps them available without cluttering the shared project CLAUDE.md.

**Write hooks for session capture if you want long-term memory.** If you need Claude to remember what happened in sessions from three months ago, build a hook that extracts insights from session transcripts and stores them in an external system. Claude Code itself does not retain session history, but you can build that layer on top.

**Verify critical memory entries.** For important architectural decisions stored in CLAUDE.md, do not assume Claude will follow them perfectly. Ask Claude to explain the current architecture and compare it against your stored notes. Memory drift is real and checking takes seconds.

## Frequently Asked Questions

**Can I expand the 200-line auto memory limit?**
No. The limit is fixed at 200 lines or 25KB per working tree. If you need to store more, move information to CLAUDE.md which does not have a hard size limit, though larger files consume more context window tokens.

**Does Claude Code share memory across team members?**
Project-level CLAUDE.md files at `./CLAUDE.md` or `./.claude/CLAUDE.md` are shared through version control. Auto memory is not shared. User-level CLAUDE.md at `~/.claude/CLAUDE.md` is private to you. Organization-level managed policy files at `/etc/claude-code/CLAUDE.md` apply to all users.

**What happens to memory when I change branches?**
Auto memory is stored in `.claude/auto-memory.md` which is typically gitignored. Switching branches does not affect it. CLAUDE.md files that are version controlled will change when you switch branches, reflecting the conventions and architecture of the target branch.

**How do I clear all memory for a project?**
Run `/clear-memory` to wipe auto memory for the current project. To reset CLAUDE.md, edit or delete the file directly. For a complete reset, remove both `./CLAUDE.md` and `./.claude/` directory contents.

**Can Claude Code remember what we discussed in a previous session about the architecture?**
Only if that discussion produced a CLAUDE.md entry or a learned pattern that survived auto memory consolidation. Raw conversation history is not stored. The architecture discussion itself, if you formalized it into a CLAUDE.md entry, will persist.

**Is there a way to see exactly what Claude Code remembers about my project?**
Run `/memory` to see the current auto memory contents. CLAUDE.md contents are visible in the files themselves. There is no single command to view everything Claude has loaded, but the `/status` command shows session-level context including loaded CLAUDE.md files.

**How does Claude Code memory compare to using a context manager or vector database?**
Claude Code memory is file-based and text-native. It does not use embeddings or semantic search. Information retrieval is based on file loading and context inclusion. Vector databases and semantic memory systems can layer on top through hooks and plugins, but that is custom infrastructure, not built-in Claude Code functionality.

The memory architecture in Claude Code is deliberately simple. Files on disk, loaded into context at session start. Auto memory written by the model itself, consolidated periodically. A CLI command to view and clear memory. There is no hidden magic, no opaque vector store, no mysterious retrieval mechanism. What you see is what you get, and what you get is enough for most coding workflows if you invest the time to maintain it properly.

If you want to understand more about how Claude Code compares to other AI coding tools, see my post on [the best LLMs for coding in 2026](/blog/best-llms-for-coding/). For a deeper look at common errors in production AI agent deployments, check out [production AI agent errors and how to avoid them](/blog/production-ai-agent-errors/).

The memory system will likely evolve. The leaked KAIROS daemon documentation suggests future always-on background memory monitoring. But for now, the three-layer architecture of CLAUDE.md, auto memory, and context window is the system you work with. Understand it, maintain it, and it will serve you well across months of project work.