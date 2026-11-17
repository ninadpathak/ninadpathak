---
category: coding-agents
primary_query: none
bridges:
- slug: code-documentation
  reason: The files that configure a coding agent are documentation.
- slug: llm-token-budgets
  reason: Context limits and token cost decide how a coding agent is configured.
date: 2026-11-17
description: Simon Willison says coding models hit an inflection point in October. The same month, the best of them passed one staged-change checkpoint in six. Both are true.
slug: coding-models-new-code-vs-change
status: published
title: 'Coding Models Got Better at New Code. Changing Code Is Still at 16%'
work_note: 'I write about coding agents for developer-tool companies, and this essay is my reading of two October results that seem to disagree. [My portfolio](/portfolio/) has the client work.'
---

"I think October represents another inflection point in capabilities for coding agents and the models that drive them: Claude Opus 5.5 can now build video games that are actually fun". Simon Willison [posted that on Bluesky](https://bsky.app/profile/simonwillison.net/post/3mywwaogdac23) on October 28, with a [write-up](https://simonwillison.net/2026/Oct/28/vibe-game-development/) of four browser games built with "no looking at the code at all".

I believe it, because the games are linked and playable. The same month produced a benchmark run in which the same model passed 28 of 196 checkpoints.

The distance between those two results is the question for anyone choosing [coding agents](/articles/coding-agents/).

That run is Dex Horthy's [October SlopCodeBench update](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-new-models-on-slop-code-bench.md), published on October 15. Its best result across every frontier model and effort setting belonged to OpenAI's Astra at the highest effort: 32 of 196, a strict pass rate of 16.33%.

A model that can make a game fun on request and a model that fails six staged changes out of seven are the same model. The two results stop contradicting each other once you look at what each one asks for.

## What the two results measure

Willison's games are new code with one author and no reader. The test is whether the result is fun, and nobody has to change it next month.

SlopCodeBench is built the other way round, and Horthy's summary of it runs to two sentences.

"It writes a program, gets new requirements, and changes the existing code. Later checkpoints test both new behavior and old behavior."

A strict pass means every test passed, including the regression tests from earlier checkpoints. The benchmark also reports a looser core rate, which asks only that a checkpoint's core tests pass, and on that measure the same campaigns score from 65.8% up to 74.0%.

So the models built the new thing about seven times in ten and built it without breaking the old thing about one time in seven. The final snapshots say where the failures sit: for the leading campaign, 1,178 of 1,435 failing test cases at the end were regressions.

That is the difference between producing software and changing it. Maintenance is the second kind, and it is the kind the headline numbers leave out.

## Paying more did not buy the second kind

The same run tested effort settings, and the result should change how teams budget. Opus 5.5 passed 28 checkpoints strictly at medium effort and 25 at the highest setting, which cost 4.22 times as much.

Horthy is careful about the claim, and the careful version is the one to repeat: "higher effort was not a reliable way to buy more strict passes in these runs". A single campaign per setting can't separate effort from run-to-run noise, and the post says so.

Real-SWE 1.1, which Specific Labs [published in October](https://withspecific.com/blog/real-swe), shows why the ranking matters less than it looks. It "expands the benchmark to 25 tasks across TypeScript, Go, Python, Ruby and Java codebases and compares 18 models", and its top two, Opus 5.5 at 56.80% and Astra at 56.00%, sit inside each other's error bars.

Astra's estimated cost per run in that table is under a third of Opus's. A leaderboard that ends in a tie at the top and a wide spread in price is telling you the ranking question is the wrong one to be asking.

## What the leaderboards don't charge for

Dan Luu went through two popular coding benchmarks in [a post from July](https://danluu.com/exercise-7/) and concluded that "very few of the publicly available benchmarks seem like reasonable things to rely on for getting a general idea of how good coding agents are." I agree, and my reason is narrower.

Nearly all of them score the patch and ignore what the patch costs the next person. [Parsimony](https://parsimony.lasu.dev/), a small project that reached Hacker News on October 13, exists to count that: "Existing benchmarks measure solve rate and cost, but don't punish excess code, which makes a codebase harder to work with in the long term."

Excess code is the same complaint I wrote about in the [code documentation guide](/articles/code-documentation/), where a model told to add no comments added them in a third of tasks. It is also what a regression failure is made of, since every extra branch is something the next change can break.

My own [best LLMs for coding](/articles/best-llms-for-coding/) page, written in March around a single benchmark score, needs rebuilding for that reason. A ranking by solve rate answers which model writes new code best, and Willison's games already answer that well enough.

The question worth a test of your own is the other one. Take a change you made last month, give a model the repository as it stood before, and count a pass only if your whole suite stays green afterwards.

A suite tells you that only as long as a red result still stops someone, which is the argument of [the red build nobody stops for](/articles/red-build-nobody-reads/).

Run it at medium effort first, since the [token bill](/articles/llm-token-budgets/) for the highest setting bought nothing for Opus or SOL in Horthy's runs and a handful of extra passes for Astra. Until a public benchmark prints strict regression passes beside its headline number, read every "best coding model" claim as a claim about new code.
