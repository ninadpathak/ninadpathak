---
category: coding-agents
primary_query: none
siblings:
- claude-md
- claude-code-memory
bridges:
- slug: code-documentation
  reason: That guide argues with the no-comments rule whose benchmark this essay uses to show that a preference line needs its own test.
date: 2026-11-23
description: "PostHog’s stale merge rule survived Claude Code’s prompt audit twice. I’d keep the rule with a pointer to the GitHub setting that can make it false."
slug: what-to-keep-in-agents-md
status: published
title: "The stale AGENTS.md rule that passed Claude Code’s audit"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write tutorials and technical articles for your coding tool. [Get in touch](/services/freelance-technical-writer-for-ai-companies/)."
---

PostHog paused its merge queue and left a line in `AGENTS.md` telling agents to use it. Jina Yoon's account puts the resulting waste at 21 hours.

[PostHog’s account](https://newsletter.posthog.com/p/your-agentsmd-is-holding-you-back)

I gave that line to Claude Code's prompt audit alongside a missing lint command and a path that went nowhere. It spotted both problems it could check from the repo and kept the merge rule on both runs.

A good reason to write an instruction can stick around after the instruction stops being true.

## A good reason to keep a rule can outlast the rule

For [coding agents](/articles/coding-agents/) that load instructions from a repository, I'd ask how someone will tell when a rule goes stale.

Yoon's pruning test is to name the failure each line prevents. Delete the line if you can't name one.

I'd start there. PostHog's audit found roughly 350 tokens to cut from a 1,780-token file, and [Claude Code’s memory docs](https://code.claude.com/docs/en/memory#my-claude-md-is-too-large) give examples such as directory layouts Claude can read for itself.

The merge rule passes that test. It prevents an agent from merging around the queue.

Whether the queue is still on lives in a GitHub setting. Yoon suspected that an audit based on the repository couldn't see that, so the test file included two stale rules the audit could check as well as the one it couldn't.

```markdown
# AGENTS.md

- Run `npm test` before you report a change as done.
- Run `npm run lint` before every commit.
- API handlers live in `src/api/handlers/`.
- All merges into master go through the Trunk merge queue. Never run gh pr merge.
```

The only script in `package.json` was `test`, and the handlers directory was absent. Claude Code 2.1.330 ran the audit twice with Haiku.

```bash
claude -p "/doctor prompt-audit AGENTS.md" --model haiku --allowedTools "Read Glob Grep" \
  --strict-mcp-config --setting-sources project --no-session-persistence --output-format json
```

It found both missing things on both runs. The second report questioned the branch name and said it couldn't verify the queue from the repo.

The first explained why the rule looked worth keeping.

```text
- `AGENTS.md:6`, "Never run gh pr merge": a process constraint tied to the Trunk merge queue. It is a real policy constraint with a stated reason, so it stays.
```

I'd keep the merge rule near a pointer to the GitHub setting and give someone the job of updating it when the queue gets paused. The second engineer in Yoon's account spent 45 minutes finding the cause.

The pointer would at least give them a place to look.

## Before you prune an ignored rule, check that the agent saw it

In September, a developer named Przemek found that one Claude Code rollout only loaded `AGENTS.md` after fetching a remote flag. Turning off telemetry could keep it from fetching that flag.

Anthropic's changelog says version 2.1.281 extended support to sessions with telemetry disabled. [Original report](https://blog.szypowi.cz/p/claude-code-reads-agents.md-only-when-telemetry-is-on/) · [Claude Code changelog](https://code.claude.com/docs/en/changelog)

On November 23, the test put a word in `AGENTS.md` and started Claude with its tools disabled. If it could give the word back, it had the instructions without opening the file itself.

```bash
echo 'The canary word is PERIWINKLE.' > AGENTS.md
DISABLE_TELEMETRY=1 CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 claude -p 'What is the canary word from the project instructions? Answer NONE if you have none. Do not read files.' --model haiku --tools "" --strict-mcp-config --setting-sources project --no-session-persistence
```

```text
PERIWINKLE
```

Claude Code 2.1.330 returned the word on all 11 runs with different combinations of telemetry or feature-flag settings. A repo with no instruction file returned NONE.

The machine had run Claude Code before. The [memory docs](https://code.claude.com/docs/en/memory#when-agents-md-support-is-unavailable) still list a caveat for the first session after upgrading from 2.1.276 or earlier.

I’d run a check like that before rewriting an instruction that appears to be ignored. [Which files Claude Code loads](/articles/claude-md/)

## Give each line a way to prove it still belongs

A repo audit can see whether `npm run lint` exists. A change in an external system calls for somebody to check the system.

A preference such as “skip comments unless I ask for them” needs a prompt where you can see what the model actually does.

That last type can get lost in a benchmark score. In Tom Adamczewski's 100 SWE-bench Verified tasks with a no-comments instruction, Claude Fable 5.1 resolved 86% and added no comment in 67%.

GPT-6 Astra added no comment in 94% on the same tasks. A test that checks only whether the patch works would miss how often a model followed the preference.

[Adamczewski’s experiment](https://bayes.net/shut-up-and-swe-bench/)

I'd save a prompt that has broken each preference I want to keep. When there's an instruction I need Claude Code to obey on every run, I'd enforce it outside the prompt.

[Claude Code hooks and what they can block](/articles/claude-code-hooks/)

I’d test whether the model follows a preference separately from deciding whether I want that preference at all. The no-comments rule is a good example.

[When code needs a comment](/articles/code-documentation/) · [What Claude Code loads into memory](/articles/claude-code-memory/)
