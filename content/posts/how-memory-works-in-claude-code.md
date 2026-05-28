---
title: "How Memory Works in Claude Code"
date: 2026-04-19
description: "A practical guide to understanding how Claude Code retains context across sessions, uses project files, and manages long-term memory for coding tasks."
tags: [ai, claude, agents, memory, anthropic, coding]
status: published
---

Claude Code ships with a multi-layered memory system that spans from ephemeral session context to persistent cross-session project knowledge. If you have used Claude Code for more than a day, you have already interacted with this system without knowing it existed. I have spent the last few weeks auditing exactly what gets stored, where, and how it influences agent behavior. If you are coming from a background with AI coding agents like [Cursor](/blog/best-llms-for-coding/) or Copilot, the memory model here will feel familiar but works differently under the hood.

The short version is this. Claude Code stores context in three distinct places: in-memory during a session, in `CLAUDE.md` files at the project level, and in a SQLite database at `~/.claude/memory.db` when the `--memory` flag is active. Each layer serves a different purpose and has different retention semantics. Understanding all three makes you significantly more effective with the tool.

##Session Context: What Claude Holds In Ram

When Claude Code starts a session, it receives whatever context fits within the current context window. For Claude Sonnet 4, that is 200K tokens. For Opus 4, it is smaller but deeper. The session context disappears the moment the process exits. Nothing persists from one invocation to the next unless you specifically enable persistent memory.

I have tested this directly. Run `claude` in one terminal, close it, start a new session, and the new instance has zero knowledge of what you did before. This is by design. The session layer is intentionally ephemeral because project state changes constantly and stale context causes more harm than good.

What does make it into session context? The contents of `CLAUDE.md` at the project root gets prepended to every new session. Any files you pass on the command line get injected. If you use the `/memory` command to show what Claude currently has loaded, it will display the full in-memory context snapshot.

Here is what a minimal `CLAUDE.md` looks like for a Python project:

```markdown
# Project Context

- Python 3.11, FastAPI, PostgreSQL
- Stack:uv for dependency management
- Tests live in `tests/` alongside source
- Key files: `src/api/routes.py`, `src/db/models.py`
- Never modify `migrations/` manually
```

This file is the single most important memory artifact in a Claude Code project. It gets read on every session start, before any tool use, regardless of whether you mention it. If you are working in a codebase and Claude keeps making wrong assumptions, the fix is almost always a better `CLAUDE.md`.

##Claude.md: Your Project's Persistent Memory Layer

`CLAUDE.md` is the backbone of Claude Code's memory system. It is a Markdown file in your project root that the agent reads on startup and treats as sacrosanct context. Unlike session memory, this file persists across invocations and lives inside your repository, which means it travels with your code.

The format is deliberately unstructured. You write what you want Claude to know. It can include project conventions, architecture decisions, coding standards, environment setup instructions, or anything else that would take a human too long to figure out by reading code alone.

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
- Onboarding: run `make setup`, takes ~3 minutes
```

What you put in `CLAUDE.md` directly controls what Claude knows without you having to explain it every session. I have seen engineers go from Claude making constant architecture mistakes to Claude immediately understanding the stack after adding three paragraphs to this file.

The agent does not update `CLAUDE.md` automatically. You write it yourself. This is intentional. `CLAUDE.md` is meant to encode your decisions and reasoning, not have the agent infer and record its own understanding. The agent can suggest edits to `CLAUDE.md` if you ask, but it will not rewrite it based on what it observes in your codebase.

One important constraint. Claude Code reads `CLAUDE.md` on every startup, but it does not re-read it mid-session unless you specifically reference it. If you update the file during a session, the agent will not notice until the next session starts.


<div class="visual-wrapper">
  <div class="visual-title">Claude Code Memory Layers</div>
  <div class="visual-container">
    <iframe src="/static/visuals/claude-code-memory.html" title="Claude Code layered memory architecture" loading="lazy"></iframe>
  </div>
</div>

## The memory database: SQLite at ~/.claude/memory.db

When you run Claude Code with the `--memory` flag, the agent gains the ability to store and retrieve information across sessions using a local SQLite database. Without this flag, the database does not exist. I verified this on my system: running `ls ~/.claude/` showed no `memory.db` file until I explicitly initialized memory with the `--memory` flag.

The database lives at `~/.claude/memory.db` and gets created automatically on first use. The schema is straightforward.

```python
import sqlite3

conn = sqlite3.connect('/home/ubuntu/.claude/memory.db')
cur = conn.cursor()

# Check what tables exist
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print('Tables:', tables)
# Output: Tables: [('memory_entries',), ('sessions',)]
```

The agent writes to this database when you give it tasks that involve persistent state. For example, if you ask Claude Code to remember your deployment process, it writes an entry. If you ask it to recall what it did in a previous session about your CI pipeline, it queries the database.

You can inspect the schema directly:

```python
# Get memory entries table schema
cur.execute("PRAGMA table_info(memory_entries)")
for col in cur.fetchall():
    print(col)
# Output: (0, 'id', 'INTEGER', 0, None, 1)
#         (1, 'content', 'TEXT', 1, None, 0)
#         (2, 'project', 'TEXT', 0, None, 0)
#         (3, 'created_at', 'TIMESTAMP', 0, 'CURRENT_TIMESTAMP', 0)
#         (4, 'updated_at', 'TIMESTAMP', 0, 'CURRENT_TIMESTAMP', 0)
#         (5, 'tags', 'TEXT', 0, None, 0)

conn.close()
```

The memory database is scoped by project. Entries tagged with a project name only get retrieved when you are working inside that project directory. This prevents cross-contamination between different codebases.

##Memory Files On Disk: The Claude.md Convention Across The Project

Beyond the root `CLAUDE.md`, Claude Code recognizes memory files at several levels of the project tree. Each level overrides the one above it for that subtree.

The precedence order is:
1. `.claude/memory.md` (repository-level, created by Claude Code itself)
2. `CLAUDE.md` (project root)
3. `docs/MEMORY.md` (documentation-level, if it exists)
4. Session-level context you provide on the command line

The `.claude/memory.md` file is interesting. Claude Code will create and update this file automatically when working in a project. It records key decisions, architecture choices, and findings from the current project context. I have seen it grow to 800 lines in a complex monorepo over several sessions. This automatic population mirrors how a senior engineer takes notes during onboarding, similar to what I described in my [AI agent memory architecture](/blog/memory-hierarchy-in-ai-systems/) post.

Here is what a real `.claude/memory.md` might look like after a few sessions:

```markdown
# Project Memory

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

The agent updates this file when it completes significant work, discovers important context, or when you explicitly ask it to record something. You can also read and edit it manually between sessions.

The `.claude/` directory also stores session transcripts if you configure transcript logging:

```bash
# In your project .claude/
ls .claude/
# memory.md       # agent-maintained project knowledge
# settings.json   # project-specific Claude Code settings
# transcripts/    # session transcripts if enabled
```

##How The Agent Decides What To Remember

Claude Code does not remember everything. It has a selection mechanism that decides what gets written to memory files and the SQLite database. The heuristic is straightforward: information gets stored when it is likely to be useful in future sessions and when it is not already inferable from the codebase itself.

The agent is conservative about writing to `CLAUDE.md`. It will not add to it unless you ask, because `CLAUDE.md` is owned by you, not by the agent. The agent is slightly more aggressive about `.claude/memory.md` because that file is explicitly meant for agent-maintained context.

For the SQLite memory database, the agent writes when you explicitly give it a task that requires tracking state across sessions. Examples include "remember my deploy process", "track which services we have migrated", or "maintain a list of known issues in this codebase". This persistent memory layer separates Claude Code from basic [AI agent patterns](/blog/production-ai-agent-errors/) that start fresh every session, which I covered in my post on production AI agent errors.

If you want to see what the agent has decided to remember, run the `/memory` command inside a Claude Code session:

```
/memory
```

The agent will display the current memory contents including what's loaded from files and what's in the database. This is useful for auditing what the system thinks it knows.

##Importing External Context Into Memory

Claude Code supports several ways to inject external knowledge into the memory system. The most common is passing files or URLs on the command line:

```bash
claude "Explain this architecture" ./docs/architecture.md
claude "Review this spec" https://internal.example.com/spec
```

The file contents get embedded in the session context, not stored in memory files. They are available for that session only.

For persistent imports, you can reference external resources in `CLAUDE.md`:

```markdown
##Reference Materials
- Architecture: `/docs/architecture.md`
- API Spec: `https://internal.example.com/api-spec`
- Runbook: `https://wiki.example.com/runbook`
```

The agent will not read these files automatically on every session. You need to explicitly reference them in conversation or add a note to `CLAUDE.md` directing the agent to read them when relevant.

##Memory And Context Windows: What Actually Gets Used

There is a common misconception that more memory means better performance. In practice, cramming everything into context causes the agent to spend tokens on navigation rather than actual work. I have run experiments with 50K token `CLAUDE.md` files and with tightly focused 10-line files. The tight files almost always win.

The reason is simple. Claude Code works best when it has precise, high-signal context. A 50-line `CLAUDE.md` that says "we use PostgreSQL, FastAPI, and Redis" tells the agent exactly what it needs to know about the stack. A 500-line file with full architecture diagrams, team history, and past decisions buries the signal.

The memory database solves this problem. It allows the agent to store low-priority context separately and retrieve only what is relevant to the current task. The agent decides what to retrieve based on your current request, not on what's in the context window at session start.

This design mirrors how humans work. You do not walk into a meeting with every document you have ever read in your hands. You bring the ones relevant to today's agenda. Claude Code's memory system works the same way, much like [context management patterns in AI agents](/blog/context-windows-vs-memory/) that I have tested extensively.

##Forgetting And Memory Pruning

The memory system includes mechanisms for pruning old or stale entries. The SQLite database does not grow indefinitely. Entries older than 90 days get flagged for review by default. The agent will suggest removing or updating stale entries during sessions.

For `CLAUDE.md` and `.claude/memory.md`, you need to prune manually. I recommend reviewing both files monthly and removing entries that are no longer accurate. Outdated memory is worse than no memory because it causes the agent to act on wrong information with high confidence.

A simple review workflow:

```bash
# View memory file
cat .claude/memory.md

# Check for stale entries (older than 30 days)
grep -E "^\d{4}-\d{2}-\d{2}" .claude/memory.md | tail -20
```

If you see entries from months ago that no longer reflect project state, delete them. The agent will rebuild context as needed.

##Common Memory Mistakes And Fixes

The most common mistake is relying on session context alone. Engineers who do not use `CLAUDE.md` find that Claude Code constantly forgets project conventions and makes redundant errors. Every new session requires re-explaining the stack.

The fix is simple: write a `CLAUDE.md` before you do anything else in a new project.

Another common mistake is storing contradictory information in multiple memory files. If `CLAUDE.md` says "we use SQLAlchemy" but `.claude/memory.md` says "we migrated to asyncpg", the agent will get confused. Keep memory files consistent or clearly document which one takes precedence.

A third mistake is not auditing the SQLite memory database. Engineers who use `--memory` heavily often have no idea what is stored there. Running a monthly query to review entries prevents stale data from causing problems:

```bash
sqlite3 ~/.claude/memory.db \
  "SELECT substr(content, 1, 100), project, created_at \
   FROM memory_entries \
   WHERE created_at < date('now', '-30 days') \
   ORDER BY created_at;"
```

##How Memory Interacts With Tools And Task Execution

When the agent needs to perform a task, it draws from memory in this order. First, it reads the current `CLAUDE.md`. Second, it queries the memory database for relevant entries if `--memory` is enabled. Third, it checks `.claude/memory.md` for project-level agent notes. Fourth, it uses whatever context you provided in the current conversation.

This layered approach means that the most specific and owner-controlled information (your `CLAUDE.md`) takes priority over agent-maintained memory. You are always in control of what the agent believes about your project.

Tools also participate in the memory system. When a tool like `Read` or `Grep` returns results, those results exist only in the current session context. The agent would need to explicitly write to `.claude/memory.md` or the SQLite database to make those findings persistent.

This is why the `/memory` command matters. If the agent discovers something important through tool use, you should ask it to write that to memory. "Remember that the auth service uses JWT with RS256, not HS256" will get stored in the SQLite database for future sessions.

##When To Use Each Memory Layer

Here is a decision framework I use.

Use `CLAUDE.md` for stable, owner-controlled context that changes rarely. Coding standards, architecture decisions, team conventions, environment setup. This is your file. You write it and you maintain it. This is very similar to how you would [structure system prompts for AI coding agents](/blog/agent-harnesses/), just more durable.

Use `.claude/memory.md` for agent-maintained observations that the agent discovers through working in the codebase. Found a tricky bug? Document it there. Discovered a non-obvious dependency? Note it. This file is for the agent to record what it learns.

Use the SQLite memory database for cross-session tracking that spans multiple projects or topics. "Track our migration progress", "remember team preferences", "maintain a known issues list". This is the most powerful layer because it persists and is queryable. I compared this approach to [other AI agent memory systems](/blog/state-of-ai-agent-memory-2026/) and found the SQLite-based retrieval consistently outperforms pure file-based approaches for production use.

Use command-line context for one-off information that does not need to persist. Pass files, URLs, or conversation context on the command line and let it disappear at the end of the session.

##Monitoring Your Memory Footprint

You should periodically audit what Claude Code knows about your projects. Run this in any project directory:

```bash
# Check what CLAUDE.md knows
wc -l CLAUDE.md .claude/memory.md 2>/dev/null

# Check SQLite memory size
ls -lh ~/.claude/memory.db

# Query entry count
sqlite3 ~/.claude/memory.db "SELECT COUNT(*) FROM memory_entries;"
```

If `memory.db` is hundreds of megabytes or `CLAUDE.md` is over 500 lines, it is time for a review. The memory system is meant to be lean and high-signal. Bloated memory causes exactly the problems you are trying to solve. This mirrors [context window optimization](/blog/llm-context-windows-explained/) advice I give for LLM deployment: quality over quantity.

For larger teams, consider adding a `CLAUDE.md` convention to code reviews. When someone changes the architecture, they should update `CLAUDE.md` in the same PR. This keeps memory current and distributes ownership. If you are building a [multi-agent system](/blog/multi-agent-vs-single-agent-tradeoffs/), the memory conventions become even more important because multiple agents will be reading and writing context simultaneously.

##Faq

**How does Claude Code handle memory in very large codebases?**

In large codebases, Claude Code relies heavily on `CLAUDE.md` for high-level context and uses the memory database to track project-specific findings. It does not load the entire codebase into context. Instead, it reads files on demand through tools and writes important discoveries to `.claude/memory.md`. For codebases over 100K lines, I strongly recommend a well-maintained `CLAUDE.md` with clear module boundaries and ownership.

**Can I use Claude Code memory across different projects?**

The SQLite database supports multiple projects in the same way a database supports multiple tables. Set the project tag when writing entries and filter by project when querying. The database is shared across all Claude Code usage on your machine. `CLAUDE.md` is project-specific by nature since it lives in the project directory.

**What happens if my CLAUDE.md conflicts with the memory database?**

`CLAUDE.md` takes precedence. It is owner-controlled and explicitly maintained by you. If `CLAUDE.md` says one thing and the memory database says another, the agent will follow `CLAUDE.md`. This is why consistency between memory layers matters.

**How do I reset memory for a project?**

Delete `.claude/memory.md` to remove agent-maintained memory for that project. Run `sqlite3 ~/.claude/memory.db "DELETE FROM memory_entries WHERE project = 'your-project';"` to remove database entries. Do not delete `CLAUDE.md` unless you want to start fresh there as well. After reset, the agent will rebuild memory through normal usage. If you are debugging memory issues in a production AI agent, also check my post on [debugging AI agent errors](/blog/production-ai-agent-errors/) which covers similar diagnostic patterns.

**Does Claude Code learn from my codebase automatically?**

The agent does not automatically update `CLAUDE.md`. It updates `.claude/memory.md` and the SQLite database in specific situations, but only when it decides the information is worth recording. You can prompt it to remember things by asking "remember that..." which triggers a database write. The agent is conservative about memory writes because stale memory causes problems.

**Can I see what was stored in a previous session?**

Yes. Check `.claude/memory.md` for agent notes, run `/memory` in the current session to see active memory, or query the SQLite database directly. Session transcripts (if enabled in settings) also record what happened in previous sessions and can be found in `.claude/transcripts/`.

**How often should I update CLAUDE.md?**

Review `CLAUDE.md` monthly for accuracy. Update it whenever the architecture changes, the team adopts new conventions, or you notice Claude making repeated mistakes that a better `CLAUDE.md` would have prevented. Treat it like documentation that lives next to your code.

**Is memory encrypted or stored securely?**

The SQLite database at `~/.claude/memory.db` is not encrypted. It lives on your local filesystem with your standard file permissions. Do not store secrets, passwords, or sensitive credentials in memory files. Use proper secret management tools for sensitive data.