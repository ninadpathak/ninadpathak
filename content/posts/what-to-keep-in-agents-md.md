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
description: "PostHog says to delete any AGENTS.md line that prevents no failure you can name. Its own stale merge-queue rule passes that test, and Claude Code's prompt audit kept the rule in both of my runs. Claude Code 2.1.330 also read AGENTS.md with telemetry off."
slug: what-to-keep-in-agents-md
status: published
title: "What I'd keep in AGENTS.md after PostHog's advice to prune it"
work_note: "Running the product before writing about it is how this essay confirmed that a reported bug was fixed on the day the report came out. I'm Ninad Pathak, a freelance technical writer, and I write tutorials and technical articles for AI companies the same way. [Get in touch](/services/freelance-technical-writer-for-ai-companies/)."
---

PostHog's coding agents spent 21 hours working from a wrong rule in the company's AGENTS.md. The rule sent every merge into master through a merge queue and banned `gh pr merge`, and the team forgot to update it when they paused the queue to fix failing tests.

<!-- evidence-three: Yoon's post says "here are three practical ways to maintain your context" and numbers them 1 to 3 --> Jina Yoon tells the story in [Read this before deleting your AGENTS.md](https://newsletter.posthog.com/p/your-agentsmd-is-holding-you-back), which PostHog's newsletter published on August 31. The post argues that newer models need less written context, and it gives three ways to prune an instruction file without starting from scratch.

I agree with the pruning, and I think the 21 hours show what it misses, a line worth keeping that had stopped being true. Instruction files are the first thing I cover under [coding agents](/articles/coding-agents/), so two claims were tested in Claude Code 2.1.330 on November 23.

Yoon says Claude Code's `/doctor` checkup couldn't have caught the stale rule, and a September blog post reported that Claude Code skipped AGENTS.md whenever telemetry was off.

## PostHog's deletion test is the one I'd start with

I'd run every line of an instruction file through the test Yoon gives, "For each line, if you can't name the failure it prevents, delete it." The `/doctor` checkup automates part of that pass, and [Anthropic's docs](https://code.claude.com/docs/en/memory#my-claude-md-is-too-large) say it proposes cutting what Claude can derive from the codebase, such as directory layouts and dependency lists.

The numbers in Yoon's post support a trim. PostHog ran the checkup on the AGENTS.md of its website repository, and the report put the file at about 1,780 tokens and proposed cutting about 350, which is a fifth.

And I couldn't find in the post an AGENTS.md line that a better model had made harmful. Yoon's example of old context hurting an agent is PostHog's onboarding wizard landing on the wrong project in a monorepo, and the post traces that to scripts that pointed at the repository root by default.

Which means the only AGENTS.md failure the post documents is the merge-queue rule, and no model upgrade caused it.

## The merge-queue rule passes the deletion test

The merge-queue rule would survive Yoon's test, because anyone can name the failure it prevents, an agent merging a pull request around the queue. While the rule was wrong, one engineer's pull request sat stuck for 10 hours and a second engineer spent 45 minutes finding the cause.

Yoon says the checkup couldn't have caught the rule, because a merge queue's state lives in a GitHub setting and the checkup works from the code. Anthropic has since shipped an audit for stale instructions, `/doctor prompt-audit`, in [version 2.1.283 on September 25](https://code.claude.com/docs/en/changelog), so I gave it PostHog's rule.

My scratch repository had a `package.json` whose only script is `test`. Its AGENTS.md had four rules, and the last is PostHog's, word for word:

```markdown
# AGENTS.md

- Run `npm test` before you report a change as done.
- Run `npm run lint` before every commit.
- API handlers live in `src/api/handlers/`.
- All merges into master go through the Trunk merge queue. Never run gh pr merge.
```

The lint script and the `src/api/handlers/` folder don't exist, so the repository itself contradicts two of the four rules. The audit ran twice on `claude-haiku-5-5`, the model the `haiku` alias resolved to:

```bash
claude -p "/doctor prompt-audit AGENTS.md" --model haiku --allowedTools "Read Glob Grep" \
  --strict-mcp-config --setting-sources project --no-session-persistence --output-format json
```

Both runs flagged the lint command and the handlers path with high confidence. Both left the merge-queue rule in the file, and the first run's report gave its reason:

```text
- `AGENTS.md:6`, "Never run gh pr merge": a process constraint tied to the Trunk merge queue. It is a real policy constraint with a stated reason, so it stays.
```

The second run questioned the word "master", because my scratch repository's branch is `main`, and it added that the queue's configuration isn't in the repository.

So Yoon's claim holds against an audit that shipped 25 days after the post. I'd add a second question to the deletion test: can anything in the repository show that this line has stopped being true?

## Confirm the file loaded before you delete a line for being ignored

I'd confirm that AGENTS.md reached the model before deleting a line for being ignored, because for five days in September Claude Code skipped the file in some sessions and printed nothing.

A developer who signs as Przemek [reported on September 23](https://blog.szypowi.cz/p/claude-code-reads-agents.md-only-when-telemetry-is-on/) that the loader added in version 2.1.277 waited on a remote feature flag. A session with `DISABLE_TELEMETRY` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` set never fetched that flag, so it started without the file.

The post reached 486 points on [Hacker News](https://news.ycombinator.com/item?id=49814947), and 41 minutes after it was submitted a commenter, mpoteat, [answered](https://news.ycombinator.com/item?id=49815363) as the engineer responsible and called it "a rollout artifact". Anthropic's changelog dates version 2.1.281 to the same day and says it extends AGENTS.md support to sessions with telemetry disabled.

I reran Przemek's test on November 23 with both variables set:

```bash
echo 'The canary word is PERIWINKLE.' > AGENTS.md
DISABLE_TELEMETRY=1 CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 claude -p 'What is the canary word from the project instructions? Answer NONE if you have none. Do not read files.' --model haiku --tools "" --strict-mcp-config --setting-sources project --no-session-persistence
```

```text
PERIWINKLE
```

The word came back in all 11 runs, and a control repository with no instruction file answered NONE. The two variables were set in every combination across nine runs, and the other two runs set `CLAUDE_CODE_DISABLE_FEATURE_FLAGS=1`, which turns flag fetching off by name.

My machine had run Claude Code before, and [Anthropic's memory docs](https://code.claude.com/docs/en/memory#when-agents-md-support-is-unavailable) still say the first session after an upgrade from 2.1.276 or earlier can miss the file, which I didn't test. The flag Przemek found, `tengu_agents_md_mod`, is still in the 2.1.330 binary, and the code that reads it now passes `true` as its fallback where the post's excerpt from 2.1.280 passed `false`.

So the post's headline no longer describes Claude Code, but its warning still applies. A developer whose file was skipped will decide the model ignores instructions and start rewriting prompts.

My [CLAUDE.md guide](/articles/claude-md/) has the table of which file each agent loads, and Przemek found that the one-line `@AGENTS.md` import it recommends worked while the flag was off.

## What I'd keep, and what checks each kind

I'd keep three kinds of line: a command or path inside the repository, a fact about a system outside it and a preference. For each kind I'd want to know what tells me a line has gone wrong.

| Kind of line | Example | How it goes wrong | What catches it |
|---|---|---|---|
| A command or path inside the repository | Run `npm run lint` before every commit. | The script or folder is removed | `/doctor prompt-audit`, in both of my runs |
| A fact about a system outside the repository | PostHog's merge-queue rule | The system changes and the file doesn't | At PostHog, an engineer after 45 minutes |
| A preference | Tom Adamczewski's rule against unrequested comments | The model doesn't follow it | A saved prompt that you rerun |

Commands and paths are the lines I'd keep without worry, because each audit run found both stale ones and reported a cost under two cents.

A fact about an outside system is the kind I'd keep fewest of, and I'd end each one with where its state can be read. Had PostHog's rule named the GitHub setting that holds the queue's state, the engineer who lost 45 minutes would have had a place to look.

I think the post's third method is the one that could catch such a line, because it asks the agent. PostHog ends each run of its onboarding wizard by asking the agent what guidance would have prevented wasted turns, and an agent stopped by a paused queue is the first to know the rule is wrong.

I haven't tested that method, and the post links it to a product PostHog offers, Self-driving, which clusters findings into reports and opens pull requests.

A preference is where I disagree with the post's framing. Its diagram marks the context a newer model already knows as "Delete this", and no model upgrade teaches a model that one developer wants no comments.

Anthropic [wrote on July 24](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) that it removed over 80% of Claude Code's system prompt with no measurable loss on its coding evaluations, and one removed rule told Claude to default to writing no comments. On September 24 Tom Adamczewski [appended a no-comments rule](https://bayes.net/shut-up-and-swe-bench/) to the prompt for 100 SWE-bench Verified tasks, and Claude Fable 5.1 resolved 86% of them while adding no comment in 67%.

GPT-6 Astra added no comment in 94% of the same tasks. So a score for resolved tasks can't tell you whether a preference line is still needed, and two agents reading one shared AGENTS.md can follow the same line at different rates.

My [code documentation guide](/articles/code-documentation/) argues with the no-comments rule itself. For any preference I kept, I'd save the prompt that once broke it and rerun that prompt after each edit to the file, which is the post's second method.

A rule that has to hold on every run doesn't belong in an instruction file at all, and my [Claude Code memory guide](/articles/claude-code-memory/) covers the hook that Anthropic's docs point to for that case.
