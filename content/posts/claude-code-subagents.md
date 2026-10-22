---
category: ai-engineering
date: 2026-10-22
description: What a Claude Code subagent starts with and when to pick one over a skill or hook, with a link-checker subagent tested in Claude Code 2.1.308.
slug: claude-code-subagents
status: published
takeaways:
- A Claude Code subagent is a Markdown file in .claude/agents/ that runs in its own context window and returns only its final report to your conversation.
- A subagent doesn't see your conversation history, so the prompt in its file has to carry every rule the job needs.
- The tools field is enforced, and a read-only subagent asked to fix links got "No such tool available" on both of its Edit calls.
title: 'Claude Code Subagents: What Each One Sees, With a Tested Example'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for developer tools, including the agent definitions and instruction files that coding agents run from.'
---

Ask Claude Code to check every link in a docs folder and the search results land in your conversation, where they sit for the rest of the session. A subagent runs that search in its own context window and hands back only the answer.

The link-checker subagent below ran in Claude Code 2.1.308 on 2026-10-22. Its tool calls stayed in its own window, and the main conversation received a short report with two broken-link lines and `broken: 2`.

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

Each subagent starts with a fresh context window. The docs say it "doesn't see your conversation history" or the files Claude has already read, and it begins with:

- its own prompt from the file's Markdown body, in place of the Claude Code system prompt
- the task message Claude writes when it delegates
- your CLAUDE.md files and a git status snapshot, which the built-in Explore and Plan subagents skip
- the full text of any skill named in its `skills` field

So the price of a clean window is the brief. Anything you told Claude earlier reaches the subagent only if Claude copies it into the task message, which is why the prompt in the file should carry the rules the job can't run without.

Your [CLAUDE.md and AGENTS.md files](/articles/claude-md/) do reach a custom subagent, unless its frontmatter sets `omitClaudeMd: true`. Rules that only matter for one job belong in that subagent's prompt.

## A tested subagent: a docs link checker

Save this as `.claude/agents/docs-link-checker.md`:

```markdown
---
name: docs-link-checker
description: Checks relative Markdown links under docs/ and reports any that point to a file that does not exist. Use after editing documentation.
tools: Read, Grep, Glob
model: haiku
---

You check relative links in Markdown files under docs/.

1. Use Glob to list every .md file under docs/.
2. Use Grep with the pattern `\]\(` to find links, then drop any target that starts with http, https or #. Grep runs ripgrep, which has no look-ahead, so filter those targets yourself.
3. Resolve each path against the directory of the file that contains it, and use Glob to confirm the target exists.

Report one line per broken link in the form `file:line -> target`, then a final line `broken: N`. If every link resolves, report `broken: 0`. Do not edit any file.
```

Run it from the repository root. Naming the subagent in the prompt asks Claude to delegate, and the docs say an @-mention such as `@"docs-link-checker (agent)" check the docs` guarantees it runs:

```bash
claude -p "Use the docs-link-checker subagent to check this repository's docs. Reply with its report verbatim and nothing else."
```

If the reply ends with `broken: 0`, every relative link under `docs/` resolves. Any other number comes after one `file:line -> target` line per broken link, and those are the links to fix.

The file ran against a scratch repository whose `docs/` folder held two broken relative links. Each run's subagent transcript shows the model `claude-haiku-5-5`, which is what `model: haiku` resolved to:

| Run | Setup | What the subagent did |
|---|---|---|
| Find broken links | Two links point to missing files | Reported both as `file:line -> target`, then `broken: 2` |
| After the fix | Both missing files created | Reported `broken: 0` |
| Asked to fix them | An earlier draft of the file with the "Do not edit any file" line removed, and the parent told it to edit | Called `Edit` twice and got "No such tool available: Edit" both times, and no file changed |
| Asked to fix them again | The final file with that line removed | Didn't call `Edit`, and reported that its tools can't write files |

I'd rely on the `tools` line over the prompt. With the prompt's rule gone, the `tools` line alone kept the subagent from editing, and it held whether or not the subagent tried.

Haiku's Grep calls in the early runs used a look-ahead pattern that ripgrep rejected, so step 2 of the final file names the pattern and the limit. The final file's runs had no failed tool calls.

The prose around the report also varied between runs, and one run said it "found 2 relative links" before listing 3. The `broken: N` line was right every time, so I'd make the last line of any subagent's report a fixed format the parent can check.

To confirm a subagent ran, list its transcripts. Claude Code stores each one under the session:

```bash
ls ~/.claude/projects/*/*/subagents/
```

Each `agent-<id>.meta.json` file there names the `agentType`, which read `docs-link-checker` in these runs. If your session has no `subagents` folder, Claude did the work in the main conversation, so @-mention the subagent to make it run.

## Subagents vs skills vs hooks

Each feature starts at a different moment, and the context it sees decides which one fits:

| | Subagent | Skill | Hook |
|---|---|---|---|
| File | `.claude/agents/<name>.md` | `.claude/skills/<name>/SKILL.md` | A `hooks` entry in a settings JSON file |
| What starts it | Claude delegates on a matching `description`, or you name it | Claude loads it on a matching `description`, or you type `/<name>` | A lifecycle event such as `PreToolUse` matches |
| What it sees | A fresh window with its prompt, the task message and CLAUDE.md | The main conversation, unless the skill sets `context: fork` | JSON about the event, on stdin for a command hook |
| Use it for | Self-contained work that returns a summary | Instructions you keep pasting into chat | A step that must run every time |

The [skills docs](https://code.claude.com/docs/en/skills) say a skill's body "loads only when it's used," and once invoked it "stays there across later turns." So a skill adds to your context, and a subagent keeps its work out of it.

[Hooks](https://code.claude.com/docs/en/hooks) are handlers, such as shell commands, that "execute automatically at specific points" in a session. A hook in `settings.json` also fires before every tool a subagent uses, so a rule that must hold inside subagents belongs there.

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

No. A subagent starts with a fresh context window and gets the task message Claude writes, plus your CLAUDE.md files unless its definition turns them off.

### What is the difference between a subagent and a skill?

A skill's instructions load into your main conversation and stay there, and a subagent does its work in a separate context window. Use a skill for instructions you repeat, and a subagent for self-contained work whose intermediate output you don't need.
