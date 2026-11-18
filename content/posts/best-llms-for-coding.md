---
category: coding-agents
primary_query: best llm for coding
siblings:
- claude-vs-gemini-cli
- coding-models-new-code-vs-change
- nobody-understands-the-code
bridges:
- slug: agent-harnesses
  reason: A coding agent is one agent loop with a harness around it.
- slug: lambda-calculus-ai
  reason: The lambda calculus exercise is a composition-level check that a leaderboard of single tasks lacks.
- slug: mixture-of-experts
  reason: One of the models compared is a dense design chosen over a mixture of experts.
date: 2026-03-12
description: 'The best LLMs for coding on Real-SWE 1.1 (October 2026): the leaders, the cost per resolved task, open-weight options and a test for your own repo.'
status: published
work_note: "Tutorials, explainers and comparisons for AI companies are my work as a freelance technical writer. I'm Ninad Pathak, and I build the example and run it before I draft, so your engineers review working code. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'The Best LLMs for Coding in 2026: An Engineering Review'
slug: best-llms-for-coding
updated: 2026-11-17
---

The March version of this page named a best LLM for coding in each of five kinds of work, and none of the models it picked is among the 18 tested by Real-SWE 1.1, the benchmark I now trust for this question. A list like that lasted eight months, so this version gives its answer with a date and spends more of its length on how to read a benchmark, which stays true longer.

As of November 17, 2026, the best LLMs for changing a real company codebase are Claude Opus 5.5 and GPT 6 Astra, which tie near 57% on [Real-SWE 1.1](https://withspecific.com/blog/real-swe), a benchmark Specific Labs published in October. GPT 6.1 Sol resolves 47% of the same tasks for under a dollar a run, and the strongest open-weight entries sit near 39%.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/best-llms-for-coding/coding-personas.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/best-llms-for-coding/coding-personas.narrow.svg" width="288" height="648"><img class="np-has-narrow" src="/static/images/diagrams/best-llms-for-coding/coding-personas.svg" width="720" height="328" alt="Five kinds of coding work, each paired with the model family the March 2026 version of this article picked for it: autonomous work with Claude Opus, repository-scale reasoning with Gemini Pro, cost-sensitive use with DeepSeek, planning with GPT Codex and autocomplete with Cursor." loading="lazy" decoding="async"></picture></a>
  <figcaption>The pairings this page made in March 2026. Choosing by the kind of work still holds, and the table below replaces the picks.</figcaption>
</figure>

The model is one of several choices a team makes about [coding agents](/articles/coding-agents/).

## Which LLM is best for coding right now?

Claude Opus 5.5 and GPT 6 Astra lead Real-SWE 1.1 at 56.80% and 56.00%, and their error ranges overlap, so the benchmark doesn't separate them. Real-SWE "expands the benchmark to 25 tasks across TypeScript, Go, Python, Ruby and Java codebases and compares 18 models", with every task taken from a private company codebase.

| Model | Harness | Resolution rate | Estimated cost per run, USD |
| --- | --- | --- | --- |
| Claude Opus 5.5 | Claude Code | 56.80% | 13.95 |
| GPT 6 Astra | Codex CLI | 56.00% | 3.78 |
| Claude Sonnet 5.5 | Claude Code | 51.20% | 10.09 |
| GPT 6.1 Sol | Codex CLI | 47.20% | 0.79 |
| Claude Fable 5.1 | Claude Code | 45.60% | 14.24 |
| Muse Wonder 1.0 | Muse Code | 42.40% | 3.76 |
| Gemini 4 Argon | Antigravity CLI | 39.20% | 4.66 |
| Kimi K3.1 Pro | Kimi Code | 39.20% | 2.03 |
| Particle-1 | mini-swe-agent | 38.40% | 0.56 |
| DeepSeek V4.1 Flash | mini-swe-agent | 38.40% | 0.19 |
| GLM-5.3 | Claude Code | 26.40% | 3.35 |

I kept the ten highest-ranked rows and added GLM-5.3 from thirteenth place, since it ran in Claude Code, a harness Anthropic built for its own models. The other seven rows are on the linked page.

Each score rests on 125 runs, since "Resolution rate is equivalent to pass@1, averaged over five independent runs per task.", and "All runs use the highest effort possible for each model with its harness."

The table is also already old. Google [announced Gemini 4 Hydrogen on November 12](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen/), after the table was published, and Artificial Analysis lists [Claude Fable 5.2](https://artificialanalysis.ai/models/claude-fable-5-2) as a November release, so neither model has a row.

The price column says more than the rank column. Dividing each cost by its resolution rate gives the price of one resolved task, and I computed it with a few lines of Python.

```python
# Real-SWE 1.1 (October 2026): resolution rate and estimated cost per run.
rows = [
    ("Claude Opus 5.5", 56.80, 13.95),
    ("GPT 6 Astra", 56.00, 3.78),
    ("Claude Sonnet 5.5", 51.20, 10.09),
    ("GPT 6.1 Sol", 47.20, 0.79),
    ("Kimi K3.1 Pro", 39.20, 2.03),
    ("Particle-1", 38.40, 0.56),
    ("DeepSeek V4.1 Flash", 38.40, 0.19),
]

print(f"{'model':<22}{'resolved':>9}{'per run':>9}{'per resolved task':>19}")
for name, rate, cost in rows:
    print(f"{name:<22}{rate:>8.1f}%{cost:>9.2f}{cost / (rate / 100):>19.2f}")
```

Saved as `cost_per_pass.py`, it gives these figures.

```text
model                  resolved  per run  per resolved task
Claude Opus 5.5           56.8%    13.95              24.56
GPT 6 Astra               56.0%     3.78               6.75
Claude Sonnet 5.5         51.2%    10.09              19.71
GPT 6.1 Sol               47.2%     0.79               1.67
Kimi K3.1 Pro             39.2%     2.03               5.18
Particle-1                38.4%     0.56               1.46
DeepSeek V4.1 Flash       38.4%     0.19               0.49
```

A resolved task costs about fifty times as much on Opus 5.5 as on DeepSeek V4.1 Flash, and Particle-1 undercuts GPT 6.1 Sol per resolved task while resolving fewer. The cheap models fail more often, and a failed run still has to be noticed by someone, which the cost column doesn't price.

## Why does a coding benchmark rank a model and its harness together?

A coding model never runs alone, so every row is a model inside one agent program. Real-SWE says so directly: "We use native harnesses to reflect how enterprise engineers work in practice, evaluating model-and-harness combinations rather than models in isolation."

GLM-5.3 ran inside Claude Code and DeepSeek V4.1 Flash ran in mini-swe-agent, so their rows measure those pairings and say little about the same weights in another tool.

The [agent harness](/articles/agent-harnesses/) decides which files the model sees and when it runs the tests, and my [Claude Code and Gemini CLI comparison](/articles/claude-vs-gemini-cli/) walks through how two harnesses handle one refactoring task. When you change the model inside a harness you already use, expect a different number from the one in the table.

## How do the top coding models fail?

The top models fail differently, and the failure mode predicts the review work a model leaves you. Real-SWE classified every failed run, and the largest group is the unverified assumption, a run that "Builds on a guess about the system instead of checking it in the workspace."

| Share of each model's failed runs | Unverified assumption | Missed requirement | Misunderstood task | Integration error |
| --- | --- | --- | --- | --- |
| All 18 models | 33.1% | 28.7% | 16.4% | 14.7% |
| Claude Opus 5.5 | 22.2% | 11.1% | 38.9% | 18.5% |
| GPT 6 Astra | 58.2% | 0% | 16.4% | 23.6% |
| GPT 6.1 Sol | 53.0% | 1.5% | 13.6% | 22.7% |
| Muse Wonder 1.0 | 12.5% | 55.6% | 13.9% | 16.7% |

The two leaders tie on score and fail for different reasons.

Astra's failures are guesses it didn't check, so I'd review its work for assumptions about the system. Opus more often misreads what was asked, so I'd spend the effort on the task description.

Regressions, where a change breaks existing behavior, are 2.0% of failures across all models on Real-SWE. That cuts against my [essay on coding models](/articles/coding-models-new-code-vs-change/) from this month, which leaned on Dex Horthy's [SlopCodeBench run](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-new-models-on-slop-code-bench.md) from October 15, where regressions were the bulk of the failing tests.

My reading is that the two benchmarks ask different things, since Real-SWE grades one change to code that people wrote. The SlopCodeBench agent "writes a program, gets new requirements, and changes the existing code", so that benchmark measures a model living with its own output.

Evan X. Merz described what that costs a team, from inside a large company, in [a post dated November 7](https://evanxmerz.com/post/ai-usage-generates-a-fragile-codebase/): "AI tends to solve the problems that can fit within its context window very well, but it's totally oblivious to the long term issues that can't be understood in that relatively small frame."

A leaderboard of single tasks can't show that cost. I take up Merz's point about understanding in [my essay on code nobody understands](/articles/nobody-understands-the-code/), and my [lambda calculus exercise](/articles/lambda-calculus-ai/) is a small test of that kind, with one right answer per problem that a script can check.

## What is the best open source LLM for coding?

On Real-SWE 1.1 the best open-weight entries are Kimi K3.1 Pro at 39.20% and DeepSeek V4.1 Flash at 38.40%, 17 to 18 points behind the leaders. DeepSeek publishes [its weights under an MIT license](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash), and the [Kimi K3.1 Pro weights](https://huggingface.co/moonshotai/Kimi-K3.1-Pro) carry Moonshot's own license, so "open weight" is the accurate term for both.

Vendor numbers put the open models closer than that. <!-- evidence-three: the Kimi launch post prints no date; October 23 is when it was submitted to Hacker News (item 50212065) --> The [Kimi K3.1 Pro launch post](https://www.kimi.ai/blog/kimi-k3-1-pro), which appeared on October 23, says that on Terminal-Bench 4.0 "K3.1 Pro scores 65.7%, ahead of GPT-6 Astra (58.2%) and narrowly behind Claude Opus 5.5 (66.4%)."

Both numbers can be true, since they come from different benchmarks. Nathan Lambert, who tracks open models, wrote [on October 28](https://www.interconnects.ai/p/artificial-analysis-v5-and-the-benchmarkers) that "The best open models do benchmax a little.", meaning they are tuned toward benchmark scores, and that "the best OpenAI and Anthropic models have been a major step ahead in their flexibility and reliability."

Lambert's post also makes the case for the other side, calling coding the use case "where open models are far more competitive and likely to keep up." The cost table agrees with him, because DeepSeek V4.1 Flash, at 38% for 19 cents a run, is a reasonable first attempt on any task you can verify with tests.

<!-- evidence-three: the Ripple page prints no date; November 4 is the creation date of ricursiveAI/Ripple-65B-Preview on Hugging Face and of Hacker News item 50369925 --> The newest entry is [Ripple-65B Preview](https://www.ricursive.com/ripple), released on November 4 [under Apache 2.0](https://huggingface.co/ricursiveAI/Ripple-65B-Preview), which is too recent for Real-SWE. Its maker claims "U.S. open-weight state-of-the-art (80.52) on TerminalBench 2.1" for a dense 65-billion-parameter model, having chosen against the [mixture-of-experts design](/articles/mixture-of-experts/) other labs use.

Read that claim with its two qualifiers, the country and the benchmark version. The Kimi figure above is on Terminal-Bench 4.0, so the two scores can't be compared.

## How should you choose an LLM for software development?

Choose by running candidates on changes your own team already made, because no public table contains your codebase. The steps below can be rerun whenever a model ships.

1. Pick two models far apart on cost, say GPT 6 Astra and DeepSeek V4.1 Flash, which sit at opposite ends of the cost column.
2. Run each in the harness its row names, since that pairing is what was measured.
3. Take five changes merged last month and reset the repository to the commit before each one.
4. Give the model the original task description and count a pass only when your whole test suite is green afterwards.
5. Record the cost of each run, then divide by the pass rate as the script above does.

Leave the effort setting at its default for the first round. Horthy's October run compared medium and extra-high effort and concluded that "higher effort was not a reliable way to buy more strict passes in these runs", at up to 4.22 times the cost.

Real-SWE ran every model at its highest effort, so its cost column is close to the ceiling for each model. I haven't run those five steps for this page, so the only evidence here is Real-SWE's published table.

## FAQ

**Should I use one model for everything?**

The cost column argues against it, because GPT 6.1 Sol resolved 47.20% of Real-SWE tasks at 79 cents a run and Opus 5.5 resolved 56.80% at nearly fourteen dollars. Sending every task to the leader pays about eighteen times more per run for under ten points.

**Can I run a coding LLM on my own hardware?**

Only Ripple-65B Preview, the smallest of the open-weight models I've linked, is built to run on a desktop machine. Hugging Face lists Kimi K3.1 Pro at 2.8 trillion parameters and DeepSeek V4.1 Flash at 763 billion, which is data-centre scale, and Ripple-65B Preview at 65 billion, which its maker says can "run efficiently on local devices such as NVIDIA DGX Spark".

**How important is context window size?**

Context window size no longer separates the models on this page. Kimi K3.1 Pro, Ripple-65B Preview and Claude Fable 5.2 each list a context window of one million tokens on the pages linked above, so the window is rarely the limit that decides between them.

**How often does the answer change?**

The answer changes within weeks. Real-SWE 1.1 came out in October, and by mid-November Google and Anthropic had each shipped a model it doesn't cover.
