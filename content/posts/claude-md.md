---
category: technical-documentation
date: 2026-10-22
description: Which coding agent reads CLAUDE.md and which reads AGENTS.md with default settings, tested in four repositories, plus a copyable AGENTS.md template.
slug: claude-md
status: published
takeaways:
- With default settings, Claude Code prefers CLAUDE.md and falls back to AGENTS.md. Codex reads AGENTS.md, and reads CLAUDE.md only if you configure it as a fallback filename.
- Keep AGENTS.md as the shared file and put a CLAUDE.md beside it that imports it with @AGENTS.md.
- Write commands and rules an agent cannot infer from the code, and keep the file under 200 lines.
title: 'CLAUDE.md and AGENTS.md: Which File Loads, and a Template'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for developer tools, including the instruction files coding agents read before they change a repository.'
---

Put a CLAUDE.md and an AGENTS.md in the same repository and ask Claude Code and Codex what their instructions say. With default settings, Claude Code quotes CLAUDE.md, Codex quotes AGENTS.md, and neither mentions the other file.

So the file you write depends on which agents your team runs, and one `@AGENTS.md` line lets a single file serve both.

## What CLAUDE.md and AGENTS.md are

CLAUDE.md is the Markdown file Claude Code loads at the start of a session as project instructions. AGENTS.md is the open format other agents read for the same job, Codex and Cursor among them, and [agents.md](https://agents.md/) describes it as "a simple, open format for guiding coding agents".

Both are plain Markdown with no required fields. Since v2.1.277, Claude Code also reads AGENTS.md, but only when no CLAUDE.md or CLAUDE.local.md sits in the working directory or above it, according to [Anthropic's memory docs](https://code.claude.com/docs/en/memory#agents-md).

Both defaults can be changed. Claude Code's **Project instructions** setting can load both files or only CLAUDE.md, and Codex reads CLAUDE.md once you list it in `project_doc_fallback_filenames` in its config.

## Which file each agent loads

Each case below is a fresh git repository in a temporary directory with no instruction file above it. Each instruction file carries one codeword, `AGENTS-4417` in AGENTS.md and `CLAUDE-2093` in CLAUDE.md.

Claude Code ran with every tool and MCP server switched off and without user settings. Codex kept its read-only shell, with its two file-loading settings pinned to their defaults, and the script prints TOOLS in place of an answer if either agent's event trace shows Claude Code with a tool available or either agent using one.

Both agents were asked to list the codewords they had been given:

| Repository contains | Claude Code answered | Codex answered |
|---|---|---|
| AGENTS.md only | AGENTS-4417 | AGENTS-4417 |
| CLAUDE.md only | CLAUDE-2093 | NONE |
| AGENTS.md and CLAUDE.md | CLAUDE-2093 | AGENTS-4417 |
| AGENTS.md, and a CLAUDE.md that starts with `@AGENTS.md` | both codewords | AGENTS-4417 |

Running the script twice on 2026-10-22, with Claude Code 2.1.308 and Codex CLI 0.162.0, gave the same codewords in each case, and no trace showed a tool available or used. Both vendors document the same default behavior.

A stray CLAUDE.md hides AGENTS.md from Claude Code (third row), and an `@AGENTS.md` import brings it back (fourth row).

You can rerun the test with the [script](/static/examples/which-instructions-load.sh), which needs `claude`, `codex` and `python3` on your PATH. It takes no arguments, works only inside a temporary directory it creates, and deletes that directory when it finishes:

```bash
bash which-instructions-load.sh
```

If Claude Code answers NONE in the first case, check `claude --version`, because direct AGENTS.md support needs v2.1.277 or later. Then type `/config` and confirm that **Project instructions** is not set to `claude-md` or `managed-only`.

## Keep one file for every agent

I'd keep AGENTS.md as the source file, because it is the one more agents read. Then add a CLAUDE.md next to it that imports it, with any Claude-only rules underneath:

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```

Claude Code expands the import at launch and reads the imported file first, which is the fourth row of the table. A symlink (`ln -s AGENTS.md CLAUDE.md`) also works, but Anthropic's docs point out that Git checks a committed symlink out as a plain text file on Windows unless `core.symlinks` is enabled, so the import is the safer default for a shared repository.

## What to put in the file

Treat it as [documentation whose reader is an agent](/articles/documentation-types/) that can already read your code. Anthropic's guidance is to write down what you would otherwise re-explain, and to make each instruction concrete enough to verify:

| Put in | Leave out |
|---|---|
| Exact build, test and lint commands | A directory tree or dependency list the agent can read from the repository |
| Conventions that differ from tool defaults, like "use pnpm, not npm" | Rules no one could check, like "format code properly" |
| Changes that need a human, like migrations | Multi-step procedures, which fit a [skill](https://code.claude.com/docs/en/skills) better |
| The test command to run before calling a change done | Rules for one folder only, which fit a path-scoped rule in `.claude/rules/` |

I keep repository-wide commands in the shared file and move folder-specific rules into a scoped rule. Anthropic's docs also ask for related instructions grouped under headings, and [task-based headings](/articles/documentation-headings/) work for an agent reader the same way they do for a person.

## Copy the template

The [AGENTS.md template](/static/templates/agents-md-template.md) has four sections, and each placeholder asks for a command or a checkable rule:

```markdown
[One sentence: what this repository builds and who runs it.]

## Commands
- Install: `[exact command]`
- Test everything: `[exact command]`
- Test one file: `[exact command with a path placeholder]`

## Conventions that differ from the defaults
- [A rule a new contributor would get wrong, e.g. "Use pnpm, not npm."]

## Do not
- [A change that needs a human, e.g. "Do not edit migrations under db/migrations/."]

## Pull requests
- [Commit message or PR title format.]
```

The template's header comment repeats the size limits below, and Claude Code strips block-level HTML comments before it reads the file, so the note adds nothing to the agent's context.

## Where the files live and how big they can get

The two agents look in different places and cap size differently:

| | Claude Code | Codex |
|---|---|---|
| Project file | `./CLAUDE.md` or `./.claude/CLAUDE.md`, or `AGENTS.md` when no CLAUDE.md is on the path | `AGENTS.md`, or `AGENTS.override.md` when present |
| Personal file | `~/.claude/CLAUDE.md` for all projects, `./CLAUDE.local.md` for one | `~/.codex/AGENTS.md` |
| Directories read | The working directory and each directory above it at launch, subdirectories when the agent opens a file there | The project root down to the working directory |
| Size guidance | Target under 200 lines per file, and files over 4 MiB are skipped | `project_doc_max_bytes`, 32 KiB by default |

Both concatenate the files they find, from the broadest directory down to the working directory, so the closest file is read last. The Claude Code details come from [Anthropic's memory docs](https://code.claude.com/docs/en/memory) and the Codex details from [OpenAI's AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Check that your file loaded

For Claude Code, run `/context` and look for the file under **Memory files**, or run `/memory`, which lists an AGENTS.md that Claude Code read directly. A subdirectory's CLAUDE.md never appears under **Memory files**, because it loads on demand when Claude opens a file in that subdirectory.

For Codex, run `codex --ask-for-approval never "Summarize the current instructions."` and check that the summary quotes your file. If either agent answers without your rules, the codeword script above narrows down which layout it is reading.

## FAQ

### Does Claude Code read AGENTS.md?

Yes, from v2.1.277, and with default settings it reads AGENTS.md only when no CLAUDE.md, .claude/CLAUDE.md or CLAUDE.local.md is in the working directory or above it. With a CLAUDE.md present, add `@AGENTS.md` to it or set **Project instructions** to `claude-md-and-agents-md` in `/config`.

### Should I use CLAUDE.md or AGENTS.md?

Use AGENTS.md if more than one agent works in the repository, and add a CLAUDE.md that imports it for Claude-only rules. Use CLAUDE.md alone only if Claude Code is the sole agent.

### How long should a CLAUDE.md be?

Anthropic's docs target under 200 lines per file, because longer files use more context and reduce adherence. Move rules for one part of the codebase into path-scoped rules, which load only when Claude works on matching files.

### What is CLAUDE.local.md?

It is a personal, project-level instruction file that loads after CLAUDE.md and belongs in `.gitignore`. It also counts as a CLAUDE.md, so adding one stops Claude Code from reading AGENTS.md by default.
