---
category: ai-agents
primary_query: why ai agents fail
siblings:
- agent-error-handling
- ai-agent-taxonomy
- multi-agent-vs-single-agent
bridges:
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
video: ai-agent-failures
updated: 2026-11-17
---

Operations teams have a settled way of learning from a failure. Google's SRE book [defines the postmortem](https://sre.google/sre-book/postmortem-culture/) as "a written record of an incident, its impact, the actions taken to mitigate or resolve it, the root cause(s), and the follow-up actions to prevent the incident from recurring", and the method assumes a root cause can be found in the code or the configuration.

AI agents fail in production in ways that fit only part of that form. An agent has ordinary causes too, such as a timeout that was retried, and it has a second kind where nothing in the code is wrong and the model acted on something it never checked.

That second kind is where the measured failures sit, so it is where this page spends its length.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/ai-agent-failures/failure-modes.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/ai-agent-failures/failure-modes.narrow.svg" width="288" height="888"><img class="np-has-narrow" src="/static/images/diagrams/ai-agent-failures/failure-modes.svg" width="720" height="488" alt="The agent loop drawn as a ring of perceive, think, act, and remember, with two failure points marked. At act, a tool call times out, the agent retries, and the action executes twice. At perceive, context pollution lets one agent's scratch work leak into another's prompt." loading="lazy" decoding="async"></picture></a>
  <figcaption>Timeouts, retries, partial failure, and drifting state: underneath, a distributed systems problem.</figcaption>
</figure>

## Why do AI agents fail in production?

They fail by proceeding on a guess more often than for any other reason. Real-SWE 1.1, a benchmark Specific Labs [published in October](https://withspecific.com/blog/real-swe), ran 18 coding models on tasks from private company codebases and sorted every failed run by cause.

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

The benchmark covers coding agents on 25 tasks, so the shares won't transfer to a support bot unchanged. The ordering is still the useful part: the model could usually have done the work, and it didn't find out what the work was.

## Why does a failed agent run resist a postmortem?

A postmortem looks for a cause that will produce the failure again, and an agent may not fail the same way twice. Real-SWE reports each score as "pass@1, averaged over five independent runs per task", because one run of the same model on the same task doesn't settle whether it can do it.

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

Timeouts, retries and lost state are, and they have known fixes. A tool call that times out and is retried can run twice, which is how a refund gets issued twice.

The fixes are the distributed-systems ones: idempotency keys and a cap on retries, with a circuit breaker that halts the loop after repeated errors. The [error handling guide](/articles/agent-error-handling/) works through them with a run example.

Lost state is the same class of problem in a different place. A long session pushes early instructions out of the context window, which [short-term memory for AI agents](/articles/short-term-agent-memory/) covers, and the [state of agent memory](/articles/agent-memory-2026/) surveys the tools for keeping it.

## What reduces the guessing?

Give the agent a way to check and a reason to use it. The measured failures are about verification, so the countermeasures are the things that make checking cheap: tests the agent can run, tool results that say what happened, and instructions that name the checks.

Protocols help with the plumbing. The [Model Context Protocol](/articles/model-context-protocol/) gives tools a standard way to report an error, and that still leaves the decision about what to do next.

I have no production incident data of my own to add to the table above. Its value is that someone counted, and the count points away from the model's reasoning and toward what the model was allowed to assume.
