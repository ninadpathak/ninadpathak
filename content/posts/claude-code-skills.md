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
description: "Claude Code skills explained through my published writing skill, with what its description, SKILL.md and reference files cost and when each one loaded."
slug: claude-code-skills
status: published
takeaways:
- A Claude Code skill is a folder with a SKILL.md file, and only its description sits in context until Claude matches a task to it or you type its name.
- The writing skill's description takes 136 tokens of context in every session and its SKILL.md takes 1,904 when loaded, while 137,612 bytes of reference files load one file at a time.
- In headless runs on Claude Code 2.1.330, Haiku 5.5 skipped the skill for a LinkedIn post that Sonnet 5.5 loaded it for, and typing /writing loaded it in all three runs that used it.
title: "Claude Code Skills: What Loads and When, With a Tested Skill"
work_note: "I took one published skill apart and ran it before I wrote this page, and I'd write a tutorial for your product the same way. I'm Ninad Pathak, a freelance technical writer for AI companies, and I write setup tutorials and concept explainers. [Ask me about yours](/services/freelance-technical-writer-for-ai-companies/)."
---

My writing skill is a folder of 38 files and 691,892 bytes, published in this site's repository on 2026-11-23. Claude Code keeps 372 characters of it in every session, the `description` line, and reads the rest only when a task calls for it.

So a Claude Code skill is a folder with a `SKILL.md` file. The description is always listed for the model, and the body loads when Claude matches your request to it or you type `/` and the skill's name.

Skills are among the things a person writes to configure [coding agents](/articles/coding-agents/). So in this article I'll walk you through [the skill's folder](https://github.com/ninadpathak/ninadpathak/tree/main/skills) file by file, then the headless runs on Claude Code 2.1.330 that show when it loaded.

## What is a Claude Code skill?

A Claude Code skill is a directory that holds a `SKILL.md` file, which is YAML frontmatter followed by Markdown instructions. [Anthropic's skills docs](https://code.claude.com/docs/en/skills), read on 2026-11-23, say Claude Code skills follow the [Agent Skills](https://agentskills.io/specification) open standard, the format [Anthropic introduced on October 16, 2025](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills).

The standard requires `name` and `description` in the frontmatter, and Claude Code makes both optional and uses the folder name when `name` is missing. Loading happens in three levels, measured here on the writing skill:

| Level | When it loads | Size in the writing skill |
|---|---|---|
| `name` and `description` | Listed at the start of every session | 372 characters, 136 tokens |
| `SKILL.md` | When Claude matches a task or you type `/writing` | 79 lines, 6,133 bytes, 1,904 tokens |
| Files that `SKILL.md` links | When the body sends Claude to one | 15 reference files of 137,612 bytes, plus 2 scripts |

The bytes come from `wc -c`. Each token figure is the difference in first-request input tokens between two `claude -p` runs on Haiku 5.5, such as the same prompt with and without `/writing`.

## Where skill files go and which location wins

Skill files go in a `skills` folder, and when two skills share a name the personal one beats the project one. Anthropic's docs list seven locations, and a team writing a skill chooses between these four:

| Location | Path | Loads in |
|---|---|---|
| Personal | `~/.claude/skills/<name>/SKILL.md` | Every project on your machine |
| Project | `.claude/skills/<name>/SKILL.md` | Sessions in that repository |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Wherever the plugin is enabled, as `/plugin-name:<name>` |
| Enterprise | `.claude/skills/<name>/SKILL.md` in the managed settings directory | Users on machines the organization deploys it to |

The docs give the order for a shared name as "Enterprise over personal, and personal over project." Subagents resolve the other way round, with the project's `.claude/agents/` ahead of `~/.claude/agents/`.

I added a second `writing` skill to a scratch project, with one marker line for a body, and `/writing` still loaded the personal skill from `~/.claude/skills/writing`. That folder is a symlink to `~/.agents/skills/writing`, which is how my README installs it.

## What goes in the description

The `description` says what the skill does and when to use it, and with `name` it is all Claude has read of the skill when it decides whether to load the rest. The writing skill's frontmatter has two fields:

```yaml
---
name: writing
description: "Ninad's writing standard for long-form work: articles, how-tos, explainers, docs, tutorials, READMEs, founder (Paul Graham-style) essays, personal and narrative nonfiction, spoken-narrative articles, video scripts and social posts. Also edits a draft to strip AI slop, or audits one without rewriting. Use for any of these; short messages need only the always-loaded core."
---
```

Its first sentence names the forms a request might mention, and the second adds editing and auditing a draft. The closing clause, "short messages need only the always-loaded core", tells Claude when to leave the skill alone.

Claude Code cuts each listing entry at 1,536 characters, counting `description` and the optional `when_to_use` field together, and the Agent Skills standard caps `description` at 1,024. So the main use goes first, because the end gets cut.

## How a short SKILL.md routes to reference files

The writing skill's `SKILL.md` stays at 79 lines because it holds two routing tables and four steps, and each form's rules live in a separate file. The table under "Pick the job" sends an edit or an audit to `references/editing.md`, and the one under "Choose the shape" maps seven forms to seven files, with `references/social.md` for a LinkedIn or X post.

The line above that table says "Read the one reference that matches before drafting." So a LinkedIn post should load `social.md` at 2,250 bytes and leave `essay.md`, at 23,092 bytes, on disk.

The 15 reference files add up to 137,612 bytes, 22 times the size of `SKILL.md`. Another 18 research files sit in two subfolders of `references/`, linked only from `essay.md` and `narrative.md`, which is how the folder reaches 691,892 bytes while an idle session pays for 372 characters.

A loaded body stays in the conversation for the rest of the session, so I'd keep rules for a single kind of task in linked files.

## A script inside a skill

A skill can ship a script that Claude runs with Bash, so the script's code stays out of context and only its output comes back. Step 4 of the writing skill is one command:

```bash
python3 ~/.agents/skills/writing/scripts/check_prose.py draft.md
```

`check_prose.py` is 216 lines of standard-library Python that reads its word lists from `core.md`, so the banned words live in one file. It runs eleven checks and exits 1 on the ones marked Fail:

| Check | Result |
|---|---|
| A word from the Hard or Slop list | Fail |
| A sentence or heading that starts with a number | Fail |
| A heading directly after a heading | Fail |
| A word banned in one named sense | Note |
| A sentence with three or more commas | Note |
| A third prose paragraph in a row | Note |
| One of 24 framing phrases | Note |
| Em or en dashes | Note |
| Curly quotes | Note |
| A hard-wrapped paragraph | Note |
| The count of first-person words | Note |

<!-- evidence-three: that run's event stream records three Edit calls on post.md and each replaces one line --> During one test run Haiku saved a LinkedIn post as `post.md` and ran that command with Python 3.12.3, and the first pass ended `result: FAIL (1 failures, 5 notes)` on one Hard-list word. Claude edited three lines, and the second pass printed this:

```text
== post.md
note line 5: third consecutive prose paragraph
note line 17: third consecutive prose paragraph
note first-person tokens: 0
result: pass (0 failures, 3 notes)
```

<!-- evidence-three: the pitfalls-list essay says the script passed drafts 4, 6 and 7 of ten, all rejected by hand --> So the script blocked the banned word and left the paragraph notes to a person. My [notes on a pitfalls list for AI-drafted docs](/articles/pitfalls-list-for-ai-drafted-docs/) record the same script passing three drafts I had rejected.

## What stays in CLAUDE.md instead of the skill

Rules that apply to every message stay in CLAUDE.md, the [instruction file Claude Code loads at the start of a session](/articles/claude-md/). For the writing skill those are the sentence rules and banned-word lists in `core.md`, which the README tells you to load with an import line in CLAUDE.md:

```markdown
@~/.agents/skills/writing/core.md
```

`core.md` is 33 lines and 4,532 bytes, and it added 1,594 tokens to the first request of a run. A skill costs its description until it loads, and a subagent works in a separate context window, which the table on the [Claude Code subagents](/articles/claude-code-subagents/) page sets beside skills and hooks.

With that line in a project's CLAUDE.md, a headless run of Haiku answered `NONE` when I asked it to list the Hard banned words from its instructions. The [memory docs](https://code.claude.com/docs/en/memory) call an import from outside the project external, and it waits for an approval dialog that `claude -p` never shows.

After I copied `core.md` into the project and imported it by a relative path, the same question returned the 11 words. The docs say an import in your user file, `~/.claude/CLAUDE.md`, needs no dialog, which I didn't test, and the [Claude Code memory](/articles/claude-code-memory/) page covers that file.

## Tests: when the skill loaded and when it didn't

<!-- evidence-three: three recorded runs began with /writing: the LinkedIn row in the table below, the run with the checker script and the duplicate-name run. The three description-only matching runs are the webhooks row and the two LinkedIn rows without /writing --> Typing `/writing` loaded the skill in all three runs that used it, and the description alone loaded it in two of three matching runs. Haiku 5.5 skipped it for a LinkedIn post that Sonnet 5.5 loaded it for.

These runs used Claude Code 2.1.330 on 2026-11-23, in a scratch git repository with no CLAUDE.md, with the skill installed the README's way and my other personal skills switched off through `skillOverrides`. Each run was one headless command that prints its events as JSON:

```bash
claude -p "Write a LinkedIn post about why a README should show the output of its first command. Print it in your reply." \
  --model haiku --output-format stream-json --verbose \
  --strict-mcp-config --no-session-persistence \
  --allowedTools 'Read(~/.claude/skills/**)' 'Read(~/.agents/skills/**)'
```

A load shows up in that stream as a `Skill` tool call, trimmed here from the Sonnet run:

```json
{"type":"tool_use","name":"Skill","input":{"skill":"writing","args":"LinkedIn post: why a README should show the output of its first command"}}
```

Each reference file then appears as a `Read` call with its path.

| Prompt | Model | What the stream showed |
|---|---|---|
| A question about `git rebase --onto` | Haiku 5.5 | No `Skill` call and no file read |
| A 150-word explainer on webhooks | Haiku 5.5 | A `Skill` call, then `Read` of `core.md` and `references/article.md` |
| The LinkedIn prompt above | Haiku 5.5 | No `Skill` call, and the post used a word from the Hard list |
| The LinkedIn prompt above | Sonnet 5.5 | A `Skill` call, then `Read` of `core.md` and `references/social.md` |
| `/writing` plus the LinkedIn prompt | Haiku 5.5 | No `Skill` call, then `Read` of `core.md`, `references/social.md` and `references/openings.md` |

No run opened `references/essay.md`, and each row is a single run, so repeat your own prompts before trusting a description. The `/writing` row has no `Skill` call because the body arrives with the prompt, and that first request carried 1,904 more input tokens than the same prompt without `/writing`.

## What failed in headless mode, and the fix

Reference files and the checker script were both denied under `claude -p` until I added allow rules. A [headless run](https://code.claude.com/docs/en/headless) in the default mode denies any call that needs approval, and a personal skill's folder sits outside the project directory:

```text
Claude requested permissions to read from /home/dev/.claude/skills/writing/references/article.md, but you haven't granted it yet.
```

Claude wrote the explainer without the reference. The two `Read(...)` rules in the command above fixed that, and I passed both paths because the [permission docs](https://code.claude.com/docs/en/permissions) say an allow rule covers a symlinked file only when the requested path and the resolved path both match.

The `Write` call for the draft and the Bash call for `check_prose.py` were denied too. The run in the script section passed with `--permission-mode acceptEdits` and one more rule, `Bash(python3 ~/.agents/skills/writing/scripts/check_prose.py *)`.

## How to write a minimal SKILL.md

A minimal `SKILL.md` is a `name`, a `description` that says what the skill does and when to use it, and a short body. The one below was tested as a project skill at `.claude/skills/error-message/SKILL.md`, and you can [download it](/static/templates/skill-md-template.md):

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

The standard wants `name` in lowercase letters, numbers and hyphens, matching the folder name. The body's last line is a marker to delete once you've seen it in a reply.

With Haiku 5.5, a request to rewrite `"Error: invalid input"` from a photo upload form produced a `Skill` call for `error-message` and a reply that ended with the marker. Typing `/error-message "Upload failed"` ended with the marker too.

A looser wording, `Fix this error message from our upload form: "Error: invalid input"`, sent Haiku searching the repository with `grep` in both runs, and the skill never loaded.

## FAQ

Short answers to common questions follow.

### What are Claude Code skills?

Claude Code skills are folders that each hold a `SKILL.md` file of instructions, with optional reference files and scripts. Claude sees each skill's description at the start of a session and loads the body when a task matches or you type `/` and its name.

### Where do Claude Code skills go?

Personal skills go in `~/.claude/skills/<name>/SKILL.md`, and project skills go in `.claude/skills/<name>/SKILL.md` inside the repository. When both locations hold a skill with the same name, the personal one runs.

### Do skills work in headless mode with claude -p?

Yes, both by description and by typing `/name` at the start of the prompt. A personal skill's reference files and scripts need allow rules, because a headless run denies any call that would prompt.
