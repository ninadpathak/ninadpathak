---
category: coding-agents
primary_query: none
siblings:
- best-llms-for-coding
- red-build-nobody-reads
bridges:
- slug: code-documentation
  reason: That guide covers the benchmark in which a model told to omit comments added them anyway.
- slug: llm-token-budgets
  reason: Context limits and token cost decide how a coding agent is configured.
date: 2026-11-17
description: My March ranking of coding models rested on one benchmark score. An October run with 32 strict passes out of 196 made me rebuild the page, and this essay says what the page does now.
slug: coding-models-new-code-vs-change
status: published
title: "Why I rebuilt my best-LLMs-for-coding page"
work_note: "I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. I write developer documentation, tutorials and technical articles, and I run the product before I write about it. [See how I work](/services/freelance-technical-writer-for-ai-companies/) and tell me what you're shipping."
---

Simon Willison [said on October 28](https://bsky.app/profile/simonwillison.net/post/3mywwaogdac23) that the month was another turning point for coding agents, because Claude Opus 5.5 can now build video games that are fun to play. His [write-up](https://simonwillison.net/2026/Oct/28/vibe-game-development/) covers four browser games built with "no looking at the code at all".

I believe him, because the games are linked and playable. And in the same month, the same model passed 28 of 196 checkpoints on a benchmark that asks it to change code it wrote earlier.

I think both results are true, and that the difference between writing new code and changing existing code is the thing to know when you choose among [coding agents](/articles/coding-agents/). It's also why I rebuilt my [best LLMs for coding](/articles/best-llms-for-coding/) page this month.

## These are two different jobs

Willison's games are new code with one author and no reader. The test is whether the result is fun, and nobody has to change it next month.

The benchmark is Dex Horthy's [October SlopCodeBench update](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-new-models-on-slop-code-bench.md), published on October 15, and it tests the opposite job. A model writes a program, gets new requirements and has to change its own code, and later checkpoints test the old behaviour along with the new.

A strict pass means every test passed, regression tests included. The best result across every frontier model and effort setting was OpenAI's Astra at the highest effort, with 32 of 196, a strict pass rate of 16.33%.

The benchmark also reports a looser core rate, which only asks that a checkpoint's own core tests pass, and there the same campaigns score from 65.8% up to 74.0%. So the models built the new thing about seven times in ten, and built it without breaking the old thing about one time in seven.

That's the difference between producing software and changing it, to my mind. Maintenance is changing it, and for the leading campaign 1,178 of the 1,435 test cases failing at the end were regressions.

## Paying more didn't buy safer changes

The effort result in the same run should change how a team budgets. Opus 5.5 passed 28 checkpoints strictly at medium effort and 25 at the highest setting, which cost 4.22 times as much.

Horthy is careful here, and I'd repeat his careful version: "higher effort was not a reliable way to buy more strict passes in these runs". A single campaign per setting can't separate effort from run-to-run noise, and his post says so.

I also think the order of models on a leaderboard matters less than it looks. Real-SWE 1.1, which Specific Labs [published in October](https://withspecific.com/blog/real-swe), compares 18 models on 25 tasks, and its top two sit inside each other's error bars: Opus 5.5 at 56.80% and Astra at 56.00%.

Astra's estimated cost per run in that table is under a third of Opus's. When a leaderboard ends in a tie at the top with a wide spread in price, I'd stop asking which model is best and start asking what a run costs.

## What I think the leaderboards leave out

Nearly all of them score the patch and ignore what the patch costs the next person. Dan Luu went through two popular coding benchmarks in [a post from July](https://danluu.com/exercise-7/) and came away trusting very few public ones, and I agree for that narrower reason.

[Parsimony](https://parsimony.lasu.dev/), a small project that reached Hacker News on October 13, exists to count the cost. Its complaint is that benchmarks measure solve rate and price and never punish excess code, which makes a codebase harder to work in later.

I made the same complaint in the [code documentation guide](/articles/code-documentation/), where a model told to add no comments added them in a third of tasks. And excess code is what a regression is made of, since every extra branch is something the next change can break.

So I changed the page. The March version of my best-LLMs page had a section headed "Why SWE-bench Verified is the only metric that matters" and ranked models on that one score, and a best result of 32 strict passes out of 196 made that ranking impossible to defend.

A ranking by solve rate answers which model writes new code best, and Willison's games already answer that well enough. The rebuilt page dates its answer, reports the cost of a run beside the resolution rate on a newer benchmark, and ends on a test for your own repository.

That test asks about changing code. Take a change you made last month, give a model the repository as it stood before, and count a pass only if your whole suite stays green afterwards.

Your test suite can answer that only as long as a red result still stops someone, which is the argument of [my essay on a build that is always red](/articles/red-build-nobody-reads/).

And run it at medium effort first, since the [token bill](/articles/llm-token-budgets/) for the highest setting bought no extra strict passes for Opus 5.5 or GPT-6 SOL in Horthy's runs and a few more for GPT-6 Astra, 32 against 29. Until a public benchmark prints strict regression passes beside its headline number, I read every "best coding model" claim as a claim about new code.
