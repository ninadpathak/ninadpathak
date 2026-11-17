---
category: ai-agents
primary_query: why ai agents fail
siblings:
- agent-error-handling
- ai-agent-taxonomy
- multi-agent-vs-single-agent
bridges:
- slug: red-build-nobody-reads
  reason: A check only reduces guessing while a failed one still makes a person stop, which that essay argues.
- slug: short-term-agent-memory
  reason: Remembering is a step in the agent loop, and the memory hub covers it in full.
- slug: agent-memory-2026
  reason: Remembering is a step in the agent loop, and the memory hub covers it in full.
date: '2026-04-22'
description: 'Why AI agents fail in production: a measured breakdown of failed runs, why they resist postmortems, how chains of agents compound errors, and what helps.'
slug: ai-agent-failures
status: published
work_note: 'I wrote Firecrawl''s guide to agent sandboxes, which exist because agents fail in ways worth containing. The failures themselves are collected here, and [the guide is in my portfolio](/portfolio/).'
title: Why AI Agents Fail in Production
updated: 2026-11-17
---

AI agents fail in two ways, and only one of them looks like a bug. The ordinary kind is a timeout that was retried or state that went missing, and the other kind has no faulty line in it: the model acted on something it never checked.

Operations teams already have a method for the first. Google's SRE book, published in 2016, [defines the postmortem](https://sre.google/sre-book/postmortem-culture/) as "a written record of an incident, its impact, the actions taken to mitigate or resolve it, the root cause(s), and the follow-up actions to prevent the incident from recurring", and the method assumes a root cause sits in code or configuration.

The second kind has nothing for that method to find. It is also the larger share in the one public breakdown of failed runs, which makes it the main subject for anyone working on [AI agent architecture](/articles/ai-agents/).

## Why do AI agents fail?

The best count available says they fail by proceeding on a guess more often than for any other reason. That count comes from a benchmark and not from production incidents, which nobody publishes in this form.

Real-SWE 1.1, a benchmark Specific Labs [published in October](https://withspecific.com/blog/real-swe), ran 18 coding models on tasks from private company codebases and sorted every failed run by cause.

| Cause of a failed run, all 18 models | Share |
| --- | --- |
| Unverified assumption | 33.1% |
| Missed requirement | 28.7% |
| Misunderstood task | 16.4% |
| Integration error | 14.7% |
| Wrong logic | 4.4% |
| Regression | 2.0% |
| Wrong file | 0.8% |

Wrong logic, the failure a traditional bug hunt looks for, is under one run in twenty. The top row is defined as a run that "Builds on a guess about the system instead of checking it in the workspace", and with the next two it accounts for 78% of the failures.

The benchmark covers coding agents on 25 tasks, so the shares won't transfer to a support bot unchanged. They also differ by model, and the report's own heading over the per-model table is "Different models fail in different ways".

| Model | Unverified assumption | Missed requirement | Misunderstood task |
| --- | --- | --- | --- |
| All 18 models | 33.1% | 28.7% | 16.4% |
| Opus 5.5, ranked first | 22.2% | 11.1% | 38.9% |
| GPT 6 Astra, ranked second | 58.2% | 0% | 16.4% |

The top-ranked model fails differently from the field, by misreading the task more often than by guessing. What the rows share is that the leading causes are about finding out what the work is, with wrong logic far behind.

## Why does a failed agent run resist a postmortem?

A postmortem looks for a cause that will produce the failure again, and an agent may not fail the same way twice.

Real-SWE reports each score as "pass@1, averaged over five independent runs per task". The report gives no reason for the five, and mine is that one run of a model on a task doesn't settle whether it can do it.

The record is thinner too. A stack trace names a line, and an agent's wrong assumption leaves no line behind unless every tool call and result was logged.

Michael Lynch's [catalogue of coding-agent annoyances](https://mtlynch.io/why-are-coding-agents-so-dumb/) from October 9 has a failure with no error in it at all. After starting a long task overnight, Lynch found that the agent "stopped two minutes after I left to ask me what it should name a git branch and then sat all night waiting for my answer."

## How do multiple agents change the odds?

They multiply them. A chain succeeds only when every step does, so per-step reliability compounds downward with length.

```python
"""Chance that a chain of steps all succeed, for a few per-step success rates."""
for rate in (0.90, 0.95, 0.99):
    cells = "  ".join(f"{steps:>2} steps {rate ** steps:5.1%}" for steps in (5, 10, 20))
    print(f"per-step {rate:.0%}:  {cells}")
```

```text
per-step 90%:   5 steps 59.0%  10 steps 34.9%  20 steps 12.2%
per-step 95%:   5 steps 77.4%  10 steps 59.9%  20 steps 35.8%
per-step 99%:   5 steps 95.1%  10 steps 90.4%  20 steps 81.8%
```

A chain of five steps at 90% each succeeds 59% of the time. The arithmetic assumes the steps fail independently, which flatters a real system, since one agent's wrong output becomes the next agent's input.

That is the case for keeping a design small until a measurement justifies more. [Multi-agent versus single-agent tradeoffs](/articles/multi-agent-vs-single-agent/) covers when the split pays, and the [types of AI agents](/articles/ai-agent-taxonomy/) page sets out what each step up in autonomy adds.

## Which failures are ordinary engineering?

Timeouts, retries and lost state are, and they have known fixes. A tool call that times out and is retried can run twice, and if the call was, say, a refund, the customer is paid twice.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/ai-agent-failures/failure-modes.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/ai-agent-failures/failure-modes.narrow.svg" width="288" height="888"><img class="np-has-narrow" src="/static/images/diagrams/ai-agent-failures/failure-modes.svg" width="720" height="488" alt="The agent loop drawn as a ring of perceive, think, act and remember, with two failure points marked. At act, a tool call times out, the agent retries, and the action executes twice. At perceive, context left over from earlier work reaches the model's prompt." loading="lazy" decoding="async"></picture></a>
  <figcaption>The ordinary class of agent failure: a timed-out call that is retried runs twice, and stale context reaches the next step.</figcaption>
</figure>

The fixes are the distributed-systems ones: idempotency keys and a cap on retries, with a circuit breaker that halts the loop after repeated errors. The [error handling guide](/articles/agent-error-handling/) works through them with a run example.

Lost state belongs to that class too. A long session pushes early instructions out of the context window, the failure [short-term memory for AI agents](/articles/short-term-agent-memory/) starts from, and the [state of agent memory](/articles/agent-memory-2026/) surveys the tools for keeping it.

## What reduces the guessing?

Give the agent a way to check and a reason to use it. The measured failures are about verification, so the countermeasures are the things that make checking cheap: tests the agent can run, tool results that say what happened, and instructions that name the checks.

The cheapest checks are ones a program can grade, as in the [lambda calculus exercise](/articles/lambda-calculus-ai/), where a short script confirms each answer.

A check only helps while a failing one still makes somebody stop. My essay on [a build that is red too often](/articles/red-build-nobody-reads/) is about how agent-rate change wears that signal out.

Protocols help with the plumbing. The [Model Context Protocol](/articles/model-context-protocol/) gives tools a standard way to report an error, and that still leaves the decision about what to do next.

The table earlier on this page is someone else's count, and I have none from production to set beside it. What it shows is a problem located less in the model's reasoning than in what the model was allowed to assume.
