---
category: ai-engineering
date: 2026-04-19
description: A practical guide to understanding how Claude Code retains context across
  sessions, uses project files, and manages long-term memory for coding tasks.
status: published
tags:
- ai
- claude
- agents
- memory
- anthropic
- coding
title: How Memory Works in Claude Code
updated: '2026-08-17'
---

Claude Code carries instructions across sessions through `CLAUDE.md` files and auto memory. Conversation context itself remains session-bound.

##Session Context: What Claude Holds In Ram

Each session starts with a fresh context window whose size depends on the selected model.

Conversation context disappears when the session ends. Project instructions and auto memory persist because Claude Code stores them on disk.

A fresh session does not retain the previous conversation unless the relevant information was saved in `CLAUDE.md` or auto memory.

The new instance has zero knowledge of the previous one and will happily search for the old name. The session layer stays ephemeral on purpose, because project state changes constantly and a half-remembered file tree from yesterday causes more harm than a clean read today.

What does make it into session context? The contents of `CLAUDE.md` at the project root gets prepended to every new session.

Any files you pass on the command line get injected. If you use the `/memory` command to show what Claude currently has loaded, it will display the full in-memory context snapshot.

Here is what a minimal `CLAUDE.md` looks like for a Python project:

```markdown
# Project Context

- Python 3.11, FastAPI, PostgreSQL
- Stack:uv for dependency management
- Tests live in `tests/` alongside source
- Key files: `src/api/routes.py`, `src/db/models.py`
- Never modify `migrations/` manually
```

That file is the single most important memory artifact in a Claude Code project. It gets read on every session start, before any tool use, regardless of whether you mention it.

Whenever Claude keeps making the same wrong assumption in a codebase, say it reaches for `requirements.txt` in a project that moved to `uv` months ago, the fix is almost always a better `CLAUDE.md`.

##Claude.md: Your Project's Persistent Memory Layer

`CLAUDE.md` is the backbone of Claude Code's memory system. It is a Markdown file in your project root that the agent reads on startup and treats as sacrosanct context.

The file persists across invocations and lives inside your repository, so it travels with your code the way a `.gitignore` does, the same on every machine that checks out the repo.

Deliberately unstructured, the format lets you write whatever you want Claude to know. It can include project conventions, architecture decisions, coding standards, environment setup instructions, or anything else that would take a human too long to figure out by reading code alone.

A good rule I use: if I would say it to a new hire on their first afternoon, it belongs here.

A more complete `CLAUDE.md` for a FastAPI project might look like this:

```markdown
# FastAPI Backend Context

##Architecture
- Monolith API with asyncpg for PostgreSQL
- Background tasks via Celery with Redis broker
- Migrate with `alembic upgrade head`, never touch SQL directly

##Code Standards
- All DB functions live in `src/db/`, return `dict` not ORM objects
- Pydantic v2 for all request/response schemas
- Type hints required on all public functions

##Testing
- pytest with `pytest-asyncio`
- Fixtures in `tests/conftest.py`
- Mock external APIs with `responses` library, never with real HTTP

##People
- Backend lead: Sarah (slack @sarah)
- Onboarding: run `make setup`
```

A project `CLAUDE.md` can tell Claude Code to use an async database client and avoid blocking calls, so that constraint is present in each session.

The agent does not update `CLAUDE.md` automatically. You write it yourself, on purpose. `CLAUDE.md` is meant to encode your decisions and reasoning, not have the agent infer and record its own understanding.

The agent can suggest edits if you ask, and it will not rewrite the file based on what it observes in your codebase.

One important constraint trips people up. Claude Code reads `CLAUDE.md` on every startup, and it does not re-read it mid-session unless you specifically reference it.

Edit the file mid-session and the agent keeps running on the version it loaded at launch, until the next session starts.


<div class="visual-wrapper">
  <div class="visual-title">Claude Code Memory Layers</div>
  <div class="visual-container">
    <iframe src="/static/visuals/claude-code-memory.html" title="Claude Code layered memory architecture" loading="lazy"></iframe>
  </div>
</div>


##Memory Files On Disk: The Claude.md Convention Across The Project
Beyond the root `CLAUDE.md`, Claude Code loads instructions from managed, user, project, and local scopes. Anthropic documents the current scopes and load behavior in its [memory guide](https://code.claude.com/docs/en/memory).

Claude Code stores auto memory under `~/.claude/projects/<project>/memory/`. `MEMORY.md` is the entry point, and topic files hold additional notes.


An illustrative auto-memory file might look like this:

```markdown
# Auto Memory Example

##Architecture (confirmed With Team)
- Microservices: auth, billing, core-api, notifier
- Auth service: JWT, 1-hour expiry, refresh tokens stored in Redis
- Billing: Stripe webhook at `/webhooks/stripe`, signature verified with `STRIPE_WEBHOOK_SECRET`

##Decisions Made
- 2026-04-15: Chose asyncpg over SQLAlchemy for auth service due to connection pooling needs
- 2026-04-17: All timestamps stored as UTC, never as naive datetime

##Current Work (as Of 2026-04-18)
- Implementing Stripe subscription management
- Done: webhook handler, proration logic
- Todo: invoice PDF generation, email notifications via SendGrid

##Team Conventions
- PRs require 1 review, squash merge to main
- Deploys happen on merge to main via GitHub Actions
```

Claude Code can update auto memory while it works. Anthropic documents `MEMORY.md` as a concise index and recommends topic files for detailed notes.

`CLAUDE.md` remains owner-controlled. The agent may suggest additions, but project instructions should stay deliberate and reviewable.

If you want to see what the agent has decided to remember, run the `/memory` command inside a Claude Code session:

```
/memory
```

Use `/memory` to inspect loaded memory and remove instructions that no longer match the codebase.

##Importing External Context Into Memory

Claude Code supports several ways to inject external knowledge into the memory system. The most common is passing files or URLs on the command line:

```bash
claude "Explain this architecture" ./docs/architecture.md
claude "Review this spec" https://internal.example.com/spec
```

The file contents get embedded in the session context rather than written to memory files, so they are available for that session only and gone the moment you exit.

For persistent imports, you can reference external resources in `CLAUDE.md`:

```markdown
##Reference Materials
- Architecture: `/docs/architecture.md`
- API Spec: `https://internal.example.com/api-spec`
- Runbook: `https://wiki.example.com/runbook`
```

The agent will not read these files automatically on every session. You need to explicitly reference them in conversation or add a note to `CLAUDE.md` directing the agent to read them when relevant.

##Memory And Context Windows: What Actually Gets Used

A common misconception holds that more memory means better performance. Cramming everything into context, in practice, makes the agent spend tokens on navigation rather than actual work.


Claude Code works best with precise, high-signal context. A short `CLAUDE.md` that says "we use PostgreSQL, FastAPI, and Redis" tells the agent exactly what it needs about the stack.

A concise file with current instructions gives the agent less irrelevant context to sort through than a long project history.


##Forgetting And Memory Pruning

Anthropic says Claude Code loads the first 200 lines or 25KB of `MEMORY.md` at startup. Review `CLAUDE.md` and auto memory regularly so stale instructions do not survive refactors.

Outdated memory is worse than no memory, because a confident agent acting on a note that says "auth tokens never expire" will write code that breaks the day the tokens start expiring.


##Common Memory Mistakes And Fixes

The most common mistake is relying on session context alone. Engineers who skip `CLAUDE.md` find that Claude Code forgets project conventions and re-derives the same wrong answers, and every new session opens with another round of re-explaining the stack.

Writing a `CLAUDE.md` before you do anything else in a new project fixes that in one stroke.

A second mistake is storing contradictory information across memory files. When `CLAUDE.md` says "we use SQLAlchemy" and `.claude/memory.md` says "we migrated to asyncpg", the agent has two bosses giving opposite orders and follows whichever it read last.

Keep memory files consistent or clearly document which one wins.


##How Memory Interacts With Tools And Task Execution


##When To Use Each Memory Layer

Here is a decision framework I use.

Reach for `CLAUDE.md` when the context is stable and owner-controlled and changes rarely. Coding standards, architecture decisions, team conventions, environment setup.

The file belongs to you, and you write and maintain it. The job resembles how you would [structure system prompts for AI coding agents](/articles/agent-harnesses/), with a longer shelf life.

Use auto memory for useful project knowledge Claude Code discovers while working. Keep detailed notes in topic files and let `MEMORY.md` act as the index.


Reach for command-line context when the information is a one-off that does not need to survive. Pass files, URLs, or conversation notes on the command line and let them disappear at the end of the session.

##Monitoring Your Memory Footprint

Use `/memory` to inspect the files and auto memory loaded into the current session. Keep the startup content concise enough that the important instructions remain visible.

The same [context window optimization](/articles/llm-context-windows-explained/) advice I give for LLM deployment applies here: quality over quantity.

For larger teams, fold a `CLAUDE.md` convention into code review. Whoever changes the architecture updates `CLAUDE.md` in the same PR, which keeps memory current and spreads ownership across the people who actually make the changes.

Teams building a [multi-agent system](/articles/multi-agent-vs-single-agent-tradeoffs/) need these conventions even more, since several agents read and write the shared context at once and one stale line propagates to all of them.

##Faq

**How does Claude Code handle memory in very large codebases?**

In a large codebase, Claude Code reads files on demand and uses scoped `CLAUDE.md` files for instructions. Keep `CLAUDE.md` concise and use imports or scoped files to document module boundaries and ownership.

**Can I use Claude Code memory across different projects?**

A user-level `~/.claude/CLAUDE.md` can provide instructions across projects. Project `CLAUDE.md` files and auto memory remain scoped to their projects.

Use `/memory` to inspect and edit the active memory sources when an instruction is stale or conflicting.

If you are debugging memory issues in a production AI agent, also check my post on [debugging AI agent errors](/articles/production-ai-agent-errors/) which covers similar diagnostic patterns.

**Does Claude Code learn from my codebase automatically?**

Claude Code does not automatically update `CLAUDE.md`. Auto memory can record project knowledge while the agent works, and `/memory` shows the active memory sources.

Session transcripts are separate from memory. Do not treat a transcript as an instruction that Claude Code will automatically load in a later session.

**How often should I update CLAUDE.md?**

Review `CLAUDE.md` when the architecture or team conventions change, or when Claude repeatedly makes an assumption that the file could correct. Treat it like documentation that lives next to the code.

**Is memory encrypted or stored securely?**

Memory files live on the local filesystem with the permissions of the current user. Do not store secrets or credentials in them.
