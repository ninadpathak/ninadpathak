---
category: coding-agents
primary_query: claude code skills
siblings:
- claude-code-subagents
- claude-md
- claude-code-memory
bridges:
- slug: pitfalls-list-for-ai-drafted-docs
  reason: That essay runs the writing skill's checker script on ten logged drafts.
date: 2026-11-23
description: "My writing skill has 38 files. See which ones Claude Code reads, when it loads them, and what to do when a headless run fails."
slug: claude-code-skills
status: published
takeaways:
- "The skill description helps Claude decide when to open SKILL.md. The instructions inside tell it which reference to read."
- "The essay advice stayed on disk during the LinkedIn runs that loaded the writing skill."
- "An explicit /writing command loaded the skill every time it was tried. When the prompt left the choice to the model, Haiku skipped it once."
title: "Claude Code Skills: What Loads and When, With a Tested Skill"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write the tutorials and explainers for your AI product. [Let's talk](/services/technical-tutorials/)."
---

My writing skill has 38 files. When I ask Claude Code for a LinkedIn post, I want it to read the social writing rules and leave 23 KB of essay advice on disk.

The runs that loaded the skill left the essay file on disk. In one run, Haiku wrote the post without loading the skill at all.

When you write a skill, try the request you'd normally type and see whether Claude picks it up. Then check which files it reads.

## What Claude sees before it opens a skill

Start with a skill when you want [coding agents](/articles/coding-agents/) to pick up instructions for one kind of job, such as editing an error message.

A skill is a folder with a `SKILL.md` file. The YAML at the top tells Claude what it's for.

The Markdown body tells it what to do after it loads. The body can tell it to read a reference for a particular job or run a script.

[Claude Code skills docs](https://code.claude.com/docs/en/skills) · [Agent Skills specification](https://agentskills.io/specification)

| Level | When it loads | Size in the writing skill |
|---|---|---|
| `name` and `description` | Listed at the start of every session | 372 characters, 136 tokens |
| `SKILL.md` | When Claude matches a task or you type `/writing` | 79 lines, 6,133 bytes, 1,904 tokens |
| Files that `SKILL.md` links | When the body sends Claude to one | 15 reference files of 137,612 bytes, plus 2 scripts |

Here's the start of my `writing` skill.

```yaml
---
name: writing
description: "Ninad's writing standard for long-form work: articles, how-tos, explainers, docs, tutorials, READMEs, founder (Paul Graham-style) essays, personal and narrative nonfiction, spoken-narrative articles, video scripts and social posts. Also edits a draft to strip AI slop, or audits one without rewriting. Use for any of these; short messages need only the always-loaded core."
---
```

The description names the kinds of writing I ask for and includes editing as a reason to load the skill. It also says short messages can use the rules already loaded.

I'd put the words you actually use in your requests in the description and try a request with and without the skill name.

## How I keep essay rules out of a LinkedIn post

I keep rules that apply throughout a session in [CLAUDE.md](/articles/claude-md/). To decide which rules belong there, check when [Claude Code loads its memory files](/articles/claude-code-memory/).

The body of my `SKILL.md` has a table of jobs and the file to read for each one. An editing request goes to `references/editing.md`.

A LinkedIn post goes to `references/social.md`. The larger essay reference stays on disk unless the job calls for it.

[My skill folder](https://github.com/ninadpathak/ninadpathak/tree/main/skills)

I put sentence rules that apply all the time in `core.md` and import it from `CLAUDE.md`. Those rules added 1,594 tokens to the first request in one test, so I'd do that only for instructions I want in every session.

```markdown
@~/.agents/skills/writing/core.md
```

A skill can also tell Claude to run a script and read what it prints. The writing skill uses this command to check a finished draft.

```bash
python3 ~/.agents/skills/writing/scripts/check_prose.py draft.md
```

In one run the checker caught stacked headings and Claude fixed the relevant lines. The script can identify a rule it knows how to test.

I still have to read the draft to find where it loses the reader. [The drafts the checker passed and I rejected](/articles/pitfalls-list-for-ai-drafted-docs/)

## Test the prompt people will actually type

Typing `/writing` loaded the skill in every explicit run. When I asked for a LinkedIn post without naming the skill, Sonnet loaded it and Haiku didn't.

Here’s what the event stream showed in Claude Code 2.1.330 on November 23.

| Prompt | Model | What the stream showed |
|---|---|---|
| A question about `git rebase --onto` | Haiku 5.5 | No `Skill` call and no file read |
| A 150-word explainer on webhooks | Haiku 5.5 | A `Skill` call, then `Read` of `core.md` and `references/article.md` |
| The LinkedIn prompt above | Haiku 5.5 | No `Skill` call, and the post used a word from the Hard list |
| The LinkedIn prompt above | Sonnet 5.5 | A `Skill` call, then `Read` of `core.md` and `references/social.md` |
| `/writing` plus the LinkedIn prompt | Haiku 5.5 | No `Skill` call, then `Read` of `core.md`, `references/social.md` and `references/openings.md` |

For a scripted run, use the event stream to distinguish a load from a guess. A `Skill` call shows that Claude loaded the skill.

A later `Read` shows which reference it opened.

```bash
claude -p "Write a LinkedIn post about why a README should show the output of its first command. Print it in your reply." \
  --model haiku --output-format stream-json --verbose \
  --strict-mcp-config --no-session-persistence \
  --allowedTools 'Read(~/.claude/skills/**)' 'Read(~/.agents/skills/**)'
```

```json
{"type":"tool_use","name":"Skill","input":{"skill":"writing","args":"LinkedIn post: why a README should show the output of its first command"}}
```

In headless mode, loading the skill didn't grant permission to read its references or run its checker. I had the personal skill installed as a symlink, so the working command allows both the requested and resolved paths.

[Claude Code permission rules](https://code.claude.com/docs/en/permissions)

```text
Claude requested permissions to read from /home/dev/.claude/skills/writing/references/article.md, but you haven't granted it yet.
```

## Install one skill and make sure you got the right copy

Put a project skill in `.claude/skills/<name>/SKILL.md` and a personal one in `~/.claude/skills/<name>/SKILL.md`. A personal skill won when I gave the project copy the same name.

If editing the project file changes nothing in a test, check for a personal copy first.

| Location | Path | Loads in |
|---|---|---|
| Personal | `~/.claude/skills/<name>/SKILL.md` | Every project on your machine |
| Project | `.claude/skills/<name>/SKILL.md` | Sessions in that repository |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Wherever the plugin is enabled, as `/plugin-name:<name>` |
| Enterprise | `.claude/skills/<name>/SKILL.md` in the managed settings directory | Users on machines the organization deploys it to |

This [downloadable example](/static/templates/skill-md-template.md) rewrites an error message. Save it in `.claude/skills/error-message/SKILL.md`.

```markdown
---
name: error-message
description: Rewrites a user-facing error message so it says what happened, why, and what to do next. Use when the user asks to write, fix or review an error message, a validation message or a CLI error.
---

Rewrite the message in three parts, in this order.

1. What happened, in the user's words, with the value that caused it.
2. Why it happened, if the program knows.
3. What to do next, as one command or one action.

End your reply with the line `error-message skill applied`.
```

Try `/error-message "Upload failed"`. Once Claude returns the marker from the sample, remove it and try the request you'd normally type without the slash command.

That second run is the check I'd keep.

If a job needs its own context instead of a few extra instructions in the current session, I’d give it to a [Claude Code subagent](/articles/claude-code-subagents/).
