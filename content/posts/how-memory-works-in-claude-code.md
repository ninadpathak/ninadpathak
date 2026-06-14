---
title: "How Memory Works in Claude Code"
date: 2026-04-19
description: "A practical guide to understanding how Claude Code retains context across sessions, uses project files, and manages long-term memory for coding tasks."
tags: [ai, claude, agents, memory, anthropic, coding]
status: published
---

Claude Code ships with a multi-layered memory system that spans from ephemeral session context to persistent cross-session project knowledge. Anyone who has used Claude Code for more than a day has already interacted with this system without knowing it existed. I spent the last few weeks auditing exactly what gets stored, where, and how it influences agent behavior. Coming from AI coding agents like [Cursor](/blog/best-llms-for-coding/) or Copilot, you will find the memory model here familiar in shape and different under the hood.

Claude Code stores context in three distinct places: in-memory during a session, in `CLAUDE.md` files at the project level, and in a SQLite database at `~/.claude/memory.db` when the `--memory` flag is active. Each layer serves a different purpose and has different retention semantics. Knowing all three turned me from someone who re-explained the same stack every morning into someone who opens a session and gets straight to work.

##Session Context: What Claude Holds In Ram

When Claude Code starts a session, it receives whatever context fits within the current context window. For Claude Sonnet 4, that is 200K tokens. For Opus 4, it is smaller but deeper. The session context disappears the moment the process exits. Nothing persists from one invocation to the next unless you specifically enable persistent memory.

I have tested this directly. Run `claude` in one terminal, ask it to rename a function, close it, then start a fresh session and ask what you just renamed. The new instance has zero knowledge of the previous one and will happily search for the old name. The session layer stays ephemeral on purpose, because project state changes constantly and a half-remembered file tree from yesterday causes more harm than a clean read today.

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

That file is the single most important memory artifact in a Claude Code project. It gets read on every session start, before any tool use, regardless of whether you mention it. Whenever Claude keeps making the same wrong assumption in a codebase, say it reaches for `requirements.txt` in a project that moved to `uv` months ago, the fix is almost always a better `CLAUDE.md`.

##Claude.md: Your Project's Persistent Memory Layer

`CLAUDE.md` is the backbone of Claude Code's memory system. It is a Markdown file in your project root that the agent reads on startup and treats as sacrosanct context. The file persists across invocations and lives inside your repository, so it travels with your code the way a `.gitignore` does, the same on every machine that checks out the repo.

Deliberately unstructured, the format lets you write whatever you want Claude to know. It can include project conventions, architecture decisions, coding standards, environment setup instructions, or anything else that would take a human too long to figure out by reading code alone. A good rule I use: if I would say it to a new hire on their first afternoon, it belongs here.

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

What you put in `CLAUDE.md` directly controls what Claude knows without you having to explain it every session. On one team I watched Claude repeatedly wire new endpoints with synchronous DB calls in an async codebase, until someone added three paragraphs naming asyncpg and the no-blocking-calls rule. The mistakes stopped that same afternoon.

The agent does not update `CLAUDE.md` automatically. You write it yourself, on purpose. `CLAUDE.md` is meant to encode your decisions and reasoning, not have the agent infer and record its own understanding. The agent can suggest edits if you ask, and it will not rewrite the file based on what it observes in your codebase.

One important constraint trips people up. Claude Code reads `CLAUDE.md` on every startup, and it does not re-read it mid-session unless you specifically reference it. Edit the file mid-session and the agent keeps running on the version it loaded at launch, until the next session starts.


<div class="visual-wrapper">
  <div class="visual-title">Claude Code Memory Layers</div>
  <div class="visual-container">
    <iframe src="/static/visuals/claude-code-memory.html" title="Claude Code layered memory architecture" loading="lazy"></iframe>
  </div>
</div>

## The memory database: SQLite at ~/.claude/memory.db

Running Claude Code with the `--memory` flag gives the agent the ability to store and retrieve information across sessions using a local SQLite database. Skip the flag and the database does not exist. I verified this on my system: running `ls ~/.claude/` showed no `memory.db` file until I explicitly initialized memory with the `--memory` flag.

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

The agent writes to this database when you give it tasks that involve persistent state. Ask Claude Code to remember that deploys go out through `make release` and never raw `kubectl`, and it writes an entry. Come back a week later asking what it did to the CI pipeline, and it queries the database instead of guessing.

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

The memory database is scoped by project. Entries tagged with a project name only get retrieved when you are working inside that project directory, which keeps your billing service's quirks from leaking into the marketing site you open next.

##Memory Files On Disk: The Claude.md Convention Across The Project

Beyond the root `CLAUDE.md`, Claude Code recognizes memory files at several levels of the project tree. Each level overrides the one above it for that subtree.

The precedence order is:
1. `.claude/memory.md` (repository-level, created by Claude Code itself)
2. `CLAUDE.md` (project root)
3. `docs/MEMORY.md` (documentation-level, if it exists)
4. Session-level context you provide on the command line

The `.claude/memory.md` file is the one that surprised me most. Claude Code creates and updates it automatically while working in a project, recording key decisions, architecture choices, and findings from the current context. I watched it grow to 800 lines in a complex monorepo over several sessions, each entry stamped with the date the agent learned it. The automatic note-taking mirrors how a senior engineer fills a notebook during onboarding, jotting down the things nobody bothered to write in the README, similar to what I described in my [AI agent memory architecture](/blog/memory-hierarchy-in-ai-systems/) post.

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

Claude Code does not remember everything. A selection mechanism decides what gets written to memory files and the SQLite database, and the heuristic is straightforward: information gets stored when it is likely to be useful in future sessions and when it is not already inferable from the codebase itself. The fact that you use pytest is sitting right there in your imports, so it stays out. The fact that one flaky test only passes when run single-threaded is worth recording, because no amount of reading code reveals it.

Conservative by default, the agent will not add to `CLAUDE.md` unless you ask, because that file is owned by you and not by the agent. It is slightly more willing to write to `.claude/memory.md`, since that file exists for agent-maintained context in the first place.

For the SQLite memory database, the agent writes when you explicitly hand it a task that requires tracking state across sessions. Examples include "remember my deploy process", "track which services we have migrated", or "maintain a list of known issues in this codebase". The persistent memory layer separates Claude Code from basic [AI agent patterns](/blog/production-ai-agent-errors/) that start fresh every session, which I covered in my post on production AI agent errors.

If you want to see what the agent has decided to remember, run the `/memory` command inside a Claude Code session:

```
/memory
```

The agent will display the current memory contents including what's loaded from files and what's in the database. Running it once a week is how I catch the moment the agent starts believing something that stopped being true two refactors ago.

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

A common misconception holds that more memory means better performance. Cramming everything into context, in practice, makes the agent spend tokens on navigation rather than actual work. I ran the same refactoring task against a 50K-token `CLAUDE.md` and a tightly focused 10-line file, and the tight file finished cleaner nearly every time.

Claude Code works best with precise, high-signal context. A short `CLAUDE.md` that says "we use PostgreSQL, FastAPI, and Redis" tells the agent exactly what it needs about the stack. A 500-line file with full architecture diagrams, team history, and three years of past decisions buries that one useful line under noise the agent has to read past on every call.

The memory database solves the same problem from the other side. It lets the agent store low-priority context separately and pull back only what is relevant to the current task, deciding what to retrieve based on your current request rather than on whatever happened to be in the window at session start.

Think of it the way a doctor works between appointments. The full chart sits in the filing cabinet, and only the two pages relevant to today's visit come out onto the desk. Claude Code's memory system pulls the same trick, keeping the bulk on disk and surfacing only what the moment calls for, much like [context management patterns in AI agents](/blog/context-windows-vs-memory/) that I have tested extensively.

##Forgetting And Memory Pruning

The memory system includes mechanisms for pruning old or stale entries, so the SQLite database does not grow without bound. Entries older than 90 days get flagged for review by default, and the agent will suggest removing or updating stale ones during sessions.

For `CLAUDE.md` and `.claude/memory.md`, you prune by hand. I review both files monthly and delete anything no longer accurate. Outdated memory is worse than no memory, because a confident agent acting on a note that says "auth tokens never expire" will write code that breaks the day the tokens start expiring.

A simple review workflow:

```bash
# View memory file
cat .claude/memory.md

# Check for stale entries (older than 30 days)
grep -E "^\d{4}-\d{2}-\d{2}" .claude/memory.md | tail -20
```

If you see entries from months ago that no longer reflect project state, delete them. The agent will rebuild context as needed.

##Common Memory Mistakes And Fixes

The most common mistake is relying on session context alone. Engineers who skip `CLAUDE.md` find that Claude Code forgets project conventions and re-derives the same wrong answers, and every new session opens with another round of re-explaining the stack.

Writing a `CLAUDE.md` before you do anything else in a new project fixes that in one stroke.

A second mistake is storing contradictory information across memory files. When `CLAUDE.md` says "we use SQLAlchemy" and `.claude/memory.md` says "we migrated to asyncpg", the agent has two bosses giving opposite orders and follows whichever it read last. Keep memory files consistent or clearly document which one wins.

A third mistake is never auditing the SQLite memory database. Engineers who use `--memory` heavily often have no idea what is stored there. Running a monthly query to review entries keeps stale data from causing problems:

```bash
sqlite3 ~/.claude/memory.db \
  "SELECT substr(content, 1, 100), project, created_at \
   FROM memory_entries \
   WHERE created_at < date('now', '-30 days') \
   ORDER BY created_at;"
```

##How Memory Interacts With Tools And Task Execution

When the agent needs to perform a task, it draws from memory in a fixed order. First, it reads the current `CLAUDE.md`. Second, it queries the memory database for relevant entries when `--memory` is enabled. Third, it checks `.claude/memory.md` for project-level agent notes. Fourth, it uses whatever context you provided in the current conversation.

A layered order like that means the most specific and owner-controlled information, your `CLAUDE.md`, takes priority over agent-maintained memory. You stay in control of what the agent believes about your project.

Tools also feed the memory system, with one catch. When `Read` or `Grep` returns results, those results live only in the current session context. The agent has to explicitly write to `.claude/memory.md` or the SQLite database for any of those findings to survive past the session.

The `/memory` command matters for exactly that reason. When the agent discovers something important through tool use, ask it to record the finding. Telling it "remember that the auth service signs JWTs with RS256" puts that fact in the SQLite database for future sessions, so the next session does not re-grep the codebase to learn it again.

##When To Use Each Memory Layer

Here is a decision framework I use.

Reach for `CLAUDE.md` when the context is stable and owner-controlled and changes rarely. Coding standards, architecture decisions, team conventions, environment setup. The file belongs to you, and you write and maintain it. The job resembles how you would [structure system prompts for AI coding agents](/blog/agent-harnesses/), with a longer shelf life.

Reach for `.claude/memory.md` when the agent discovers something through working in the codebase. Found a tricky bug where a retry loop double-charges on timeout? Document it there. Discovered that the search service quietly depends on a Redis key the indexer sets? Note it. The file exists for the agent to record what it learns.

Reach for the SQLite memory database when you need cross-session tracking that spans multiple projects or topics. "Track our migration progress", "remember team preferences", "maintain a known issues list". It is the most capable layer, since it persists and you can query it. I compared the approach against [other AI agent memory systems](/blog/state-of-ai-agent-memory-2026/) and found the SQLite-based retrieval consistently outperforms pure file-based approaches for production use.

Reach for command-line context when the information is a one-off that does not need to survive. Pass files, URLs, or conversation notes on the command line and let them disappear at the end of the session.

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

Once `memory.db` runs into hundreds of megabytes or `CLAUDE.md` passes 500 lines, schedule a review. The memory system is meant to be lean and high-signal, and bloated memory recreates the exact confusion you adopted it to avoid. The same [context window optimization](/blog/llm-context-windows-explained/) advice I give for LLM deployment applies here: quality over quantity.

For larger teams, fold a `CLAUDE.md` convention into code review. Whoever changes the architecture updates `CLAUDE.md` in the same PR, which keeps memory current and spreads ownership across the people who actually make the changes. Teams building a [multi-agent system](/blog/multi-agent-vs-single-agent-tradeoffs/) need these conventions even more, since several agents read and write the shared context at once and one stale line propagates to all of them.

##Faq

**How does Claude Code handle memory in very large codebases?**

In large codebases, Claude Code relies heavily on `CLAUDE.md` for high-level context and uses the memory database to track project-specific findings. It does not load the entire codebase into context. Instead, it reads files on demand through tools and writes important discoveries to `.claude/memory.md`. For codebases over 100K lines, I strongly recommend a well-maintained `CLAUDE.md` with clear module boundaries and ownership.

**Can I use Claude Code memory across different projects?**

The SQLite database supports multiple projects in the same way a database supports multiple tables. Set the project tag when writing entries and filter by project when querying. The database is shared across all Claude Code usage on your machine. `CLAUDE.md` is project-specific by nature since it lives in the project directory.

**What happens if my CLAUDE.md conflicts with the memory database?**

`CLAUDE.md` takes precedence. It is owner-controlled and explicitly maintained by you. When `CLAUDE.md` says one thing and the memory database says another, the agent follows `CLAUDE.md`, which is the whole reason consistency between memory layers matters.

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