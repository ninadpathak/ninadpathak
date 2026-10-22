---
category: ai-engineering
date: 2026-10-22
description: What a Claude Code subagent starts with and when to pick one over a skill or hook, with a link-checker subagent tested in Claude Code 2.1.308.
slug: claude-code-subagents
status: published
takeaways:
- A Claude Code subagent is a Markdown file in .claude/agents/ that runs in its own context window and returns only its final report to your conversation.
- A custom subagent starts without your conversation history, so the prompt in its file has to carry every rule the job needs.
- The tools field is enforced, and a read-only subagent asked to fix links got "No such tool available" on every Edit call it made.
title: 'Claude Code Subagents: What Each One Sees, With a Tested Example'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for developer tools, including the agent definitions and instruction files that coding agents run from.'
---

Ask Claude Code to check every link in a docs folder and the search results land in your conversation, where they sit for the rest of the session. A subagent runs that search in its own context window and hands back only the answer.

The link-checker subagent below ran in Claude Code 2.1.308 on 2026-10-22. Its tool calls stayed in its own window, and the main conversation received a short report that listed each missing link target and ended its list with `broken: 3`.

## What a Claude Code subagent is

A Claude Code subagent is a Markdown file that defines a separate assistant with its own prompt and its own list of allowed tools. [Anthropic's subagent docs](https://code.claude.com/docs/en/sub-agents) say each one "runs in its own context window" and that Claude delegates to it when a task matches the file's `description`.

Claude Code looks for subagent files in these places, and a higher-priority file wins when two share a `name`:

| Location | Scope | Priority |
|---|---|---|
| Managed settings | Your organization | First, the highest |
| `--agents` flag with JSON | The current session | Second |
| `.claude/agents/` | The current project | Third |
| `~/.claude/agents/` | Every project you open | Fourth |
| A plugin's `agents/` directory | Wherever the plugin is enabled | Fifth, the lowest |

Claude Code watches `.claude/agents/` and `~/.claude/agents/`, so an edited file applies at the next delegation without a restart. New setups still need a restart once, because the watcher only covers `agents` directories that existed when the session started.

## What a subagent starts with

A custom subagent like the one below starts with a fresh context window. The docs say it "doesn't see your conversation history" or the files Claude has already read, and it begins with:

- its own prompt from the file's Markdown body, in place of the Claude Code system prompt
- the task message Claude writes when it delegates
- the instruction files your main session loaded, such as CLAUDE.md, and a git status snapshot, which the built-in Explore and Plan subagents skip
- the full text of any skill named in its `skills` field

So the price of a clean window is the brief. Anything you told Claude earlier reaches the subagent only if Claude copies it into the task message, which is why the prompt in the file should carry the rules the job can't run without.

Which instruction files those are depends on the session, because Claude Code reads [AGENTS.md only when no CLAUDE.md is on the path](/articles/claude-md/).

Setting `omitClaudeMd: true` drops your own instruction files from the start. Managed policy files still load, and a subdirectory's CLAUDE.md loads when the subagent works there.

A fork of the conversation is the exception to all of this, because it inherits the parent's history instead of starting fresh. Rules that only matter for one job belong in that subagent's prompt.

## A tested subagent: a docs link checker

Save this as `.claude/agents/docs-link-checker.md`:

```markdown
---
name: docs-link-checker
description: Checks inline relative Markdown links under docs/ and reports any whose target file is missing. Use after editing documentation.
tools: Read, Grep, Glob
model: haiku
---

You check inline Markdown links of the form [text](target) in .md files under docs/. Reference-style links such as [text][id] are out of scope.

1. Use Glob to list every .md file under docs/.
2. Use Grep with the pattern `\]\(` to find inline links. Skip a target that contains `://`, starts with `mailto:` or starts with `#`. Every other target is a relative path, including names such as http-guide.md. Grep rejected look-ahead patterns in testing, so filter targets yourself instead of in the pattern.
3. Remove any `#fragment` from the target, resolve the path against the directory of the file that contains it, and use Glob to confirm the file exists.

Report one line per missing target in the form `file:line -> target`, then a final line `broken: N`. If no target is missing, report `broken: 0`. Do not edit any file.
```

Run it from the repository root. Naming the subagent in the prompt asks Claude to delegate, and the docs say an @-mention such as `@"docs-link-checker (agent)" check the docs` guarantees it runs:

```bash
claude -p "Use the docs-link-checker subagent to check this repository's docs. Reply with its report verbatim and nothing else."
```

If the report says `broken: 0`, the subagent found no missing targets among the inline links it checked in that run. It skips reference-style links and doesn't check that a `#fragment` exists on the target page, and any other number comes with one `file:line -> target` line per missing target.

The file ran against a scratch repository whose `docs/` folder mixed missing link targets with links the subagent should skip, such as an external URL. Each run's subagent transcript shows the model `claude-haiku-5-5`, which is what `model: haiku` resolved to:

| Run | Setup | What the subagent did |
|---|---|---|
| Find missing targets, twice | Inline links to `configure.md`, `first-request.md` and `http-guide.md`, none of which exist, plus an external URL, an `#anchor` and a reference-style link to a missing `changelog.md` | Both runs listed every missing target, `http-guide.md` included, then `broken: 3`, and skipped the URL, the anchor and the reference-style link |
| After the fix | The missing files created | Reported `broken: 0` |
| Asked to fix them | A copy of the file named `docs-link-checker-noprompt`, without the "Do not edit any file" line, and the parent told it to edit | Called `Edit` once per missing target and got "No such tool available: Edit" each time, and no file changed |

I'd rely on the `tools` line over the prompt. With the prompt's rule gone, the `tools` line alone kept the subagent from editing, and it held on every attempt.

Haiku's Grep calls in an earlier draft's runs used a look-ahead pattern that Grep rejected, so step 2 of this file names the pattern and filters targets outside it. The checking runs with this file had no failed tool calls.

The prose around the report varied between runs, and the passing run said it checked "all 4 inline relative links" before listing 5. The `broken: N` line was right every time, so I'd make the last line of any subagent's report a fixed format the parent can check.

To confirm a subagent ran, look for the delegation itself. The main session's transcript in these runs recorded an `Agent` tool call with `"subagent_type": "docs-link-checker"`, and Claude Code saved the subagent's own transcript beside it:

```bash
ls ~/.claude/projects/*/*/subagents/
```

Each `agent-<id>.meta.json` file there names the `agentType`, which read `docs-link-checker` for the checking runs and `docs-link-checker-noprompt` for the edit probe. A missing folder proves nothing alone, because `--no-session-persistence` and the 30-day `cleanupPeriodDays` sweep can both leave none, so check for the `Agent` call and @-mention the subagent when you need it to run.

## Subagents vs skills vs hooks

I'd keep repeatable instructions in a skill and send a separate investigation to a subagent:

| | Subagent | Skill | Hook |
|---|---|---|---|
| File | `.claude/agents/<name>.md` | `.claude/skills/<name>/SKILL.md` | A `hooks` entry in a settings JSON file |
| What starts it | Claude delegates on a matching `description`, or you name it | Claude loads it on a matching `description`, or you type `/<name>` | A lifecycle event such as `PreToolUse` matches |
| What it sees | For a custom subagent, a fresh window with its prompt, the task message and the session's instruction files | The main conversation, unless the skill sets `context: fork` | JSON about the event, on stdin for a command hook |
| Use it for | Self-contained work that returns a summary | Instructions you keep pasting into chat | A step that must run every time |

The [skills docs](https://code.claude.com/docs/en/skills) say a skill's body "loads only when it's used," and once invoked it "stays there across later turns." So a skill adds to your context, and a subagent keeps its work out of it.

[Hooks](https://code.claude.com/docs/en/hooks) are handlers, such as shell commands, that "execute automatically at specific points" in a session. Hooks from settings files also fire inside subagents, so I'd put a rule that must run before every tool call in a `PreToolUse` hook that matches every tool.

## When to keep the work in the main conversation

Anthropic's docs recommend the main conversation for work that "needs frequent back-and-forth or iterative refinement," and for quick, targeted changes. A subagent starts fresh and may need time to gather context before it does the work.

Subagents can also spawn their own subagents, and nesting is on by default. To turn it off, set the depth to 1 in `settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1"
  }
}
```

The same trade-off between one context and several shows up in [multi-agent and single-agent designs](/articles/multi-agent-vs-single-agent/). The [agentic workflow playbook](/articles/agentic-workflows/) puts a human review of the diff before anything lands, and a subagent's edits need that review as much as the main session's.

For what Claude Code keeps between sessions, see [Claude Code memory](/articles/claude-code-memory/).

## FAQ

### What are Claude Code subagents?

Claude Code subagents are Markdown files that define separate assistants, each with its own prompt and context window. Claude delegates a task to one when the task matches its `description`, and only the subagent's final report returns to the main conversation.

### Where do Claude Code subagent files go?

Project subagents go in `.claude/agents/` and personal ones in `~/.claude/agents/`. When two files share a `name`, the higher-priority location wins, and the project folder outranks the personal one.

### Can a subagent see my conversation?

A custom subagent doesn't, because it starts with a fresh context window and the task message Claude writes. Only a fork of the conversation inherits its history.

### What is the difference between a subagent and a skill?

A skill's instructions load into your main conversation and stay there, and a subagent does its work in a separate context window. Use a skill for instructions you repeat, and a subagent for self-contained work whose intermediate output you don't need.
