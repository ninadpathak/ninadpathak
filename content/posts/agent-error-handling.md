---
category: ai-agents
primary_query: ai agent error handling
siblings:
- ai-agent-failures
- agent-harnesses
bridges:
- slug: ai-memory-management
  reason: Remembering is a step in the agent loop, and the memory hub covers it in full.
date: 2026-04-16
description: 'Error handling in production AI agents: classify tool errors in code, make ambiguous failures safe with idempotency keys, and tell the model what happened.'
status: published
work_note: 'I''ve written guides to agent tools and agent APIs for Firecrawl. This page covers what an agent should do after a tool call fails, and [those guides are in my portfolio](/portfolio/).'
title: What Nobody Tells You About Error Handling in Production AI Agents
slug: agent-error-handling
video: agent-error-handling
updated: 2026-11-17
---

Peter Deutsch began a list at Sun Microsystems in 1994 of assumptions that programmers new to networked software get wrong, now known as the [fallacies of distributed computing](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing). The first is "The network is reliable", and thirty years of retry logic and timeouts exist because it isn't.

An AI agent that calls tools is a distributed system and inherits every item on that list. Error handling in production AI agents differs in one respect: in ordinary software the code that reacts to a failure is code someone wrote, and in an agent the error text goes back to a model that decides what to do next.

That decision is the part nobody can unit-test. The rest of this page is about taking it away from the model for the cases where a wrong guess costs money.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-error-handling/error-taxonomy.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-error-handling/error-taxonomy.narrow.svg" width="288" height="704"><img class="np-has-narrow" src="/static/images/diagrams/agent-error-handling/error-taxonomy.svg" width="720" height="264" alt="Five failure modes of an agent that calls tools. Context exhaustion: tool results pile up until the context window is full and the next call is rejected. Schema drift: the model calls a tool with parameters from an older schema version. Partial failure: some parallel tool calls succeed and some fail. Ambiguous timeout: a request times out after the server may already have processed it, so a retry can execute it twice. Observability gaps: without structured logs of tool calls there is no record of what the agent tried." loading="lazy" decoding="async"></picture></a>
  <figcaption>Each mode has its own fix: a hard cap on tool history, versioned schemas, per-call tracking, idempotency keys and a log line for every tool call.</figcaption>
</figure>

## Why can't the model handle its own tool errors?

A model handed a raw error string will improvise, and improvising is the wrong behaviour when an action may already have happened. It can retry a call that succeeded, or move on to a step that assumes the failed one worked.

The protocols give the model very little to go on. Anthropic's [tool use documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) offers one flag on a tool result, "is_error (optional): Set to true if the tool execution resulted in an error."

The June 2025 revision of the [Model Context Protocol specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) is similar. It says "Tools use two error reporting mechanisms", protocol errors and tool execution errors, and the second kind is a text message with `isError: true`.

Neither says whether the call can be repeated. That knowledge sits with whoever wrote the tool, so the tool or the harness around it has to carry it.

## How should an agent classify errors?

Classify every tool error in code as transient, permanent or ambiguous, and let that label decide the recovery before the model sees anything.

| Kind | Example | What the harness does |
| --- | --- | --- |
| Transient | Rate limit, overloaded server | Retry with backoff |
| Permanent | Invalid API key, missing resource | Fail fast and report |
| Ambiguous | Timeout after the request was sent | Retry only if the call is idempotent |

The ambiguous kind is the dangerous one. A timeout says the answer didn't arrive and nothing about whether the work was done.

## What does an idempotency key change?

It makes an ambiguous failure safe to retry, because the server recognises the repeat and returns the first result. Stripe's [API reference](https://docs.stripe.com/api/idempotent_requests) describes the behaviour: "Retries with the same key return the saved response, including 500 errors."

The simulation below runs three retry policies against a payment API that charges the customer and then times out on the first call.

```python
"""A charge tool that times out after it has charged, called three ways."""
import uuid


class PaymentAPI:
    def __init__(self):
        self.charges, self.seen, self.calls = [], {}, 0

    def charge(self, customer, cents, idempotency_key=None):
        self.calls += 1
        if idempotency_key in self.seen:
            return self.seen[idempotency_key]          # replay the saved response
        self.charges.append((customer, cents))
        receipt = {"status": "charged", "cents": cents}
        if idempotency_key:
            self.seen[idempotency_key] = receipt
        if self.calls == 1:
            raise TimeoutError("no response from payment API")   # the work was done
        return receipt


def classify(error):
    if isinstance(error, TimeoutError):
        return "ambiguous"      # the server may have acted
    if isinstance(error, PermissionError):
        return "permanent"      # retrying cannot help
    return "transient"


def run(label, use_key, retry_ambiguous):
    api = PaymentAPI()
    key = str(uuid.uuid4()) if use_key else None
    for attempt in (1, 2):
        try:
            api.charge("cus_42", 4_900, idempotency_key=key)
            break
        except Exception as error:
            kind = classify(error)
            if kind == "permanent" or (kind == "ambiguous" and not retry_ambiguous):
                break
    print(f"{label:<34} attempts: {api.calls}  charges made: {len(api.charges)}")


run("blind retry", use_key=False, retry_ambiguous=True)
run("classified, no key: stop and ask", use_key=False, retry_ambiguous=False)
run("classified, with idempotency key", use_key=True, retry_ambiguous=True)
```

Each line of output from `python3 retry_demo.py` is one policy.

```text
blind retry                        attempts: 2  charges made: 2
classified, no key: stop and ask   attempts: 1  charges made: 1
classified, with idempotency key   attempts: 2  charges made: 1
```

The blind retry charges twice. Classifying the timeout as ambiguous stops the loop after one charge, and the key lets the retry go through with the customer still charged once.

The simulation is a toy with one failure in it. The model was never asked what to do in any of the runs.

## Which other failure modes need their own fix?

The figure at the top of this page names five, and the ambiguous timeout is only one of them. Each has a fix that lives in the harness.

| Failure mode | What goes wrong | Fix |
| --- | --- | --- |
| Context exhaustion | Tool results fill the window until a call is rejected | A hard cap on tool history |
| Schema drift | The model calls a tool with an old parameter set | Versioned schemas |
| Partial failure | Some parallel calls succeed and some fail | Per-call tracking |
| Ambiguous timeout | A retry can run the action twice | Idempotency keys |
| Missing logs | No record of what the agent tried | A log line for every tool call |

## What should the model be told after a failure?

Tell it what happened and what it is allowed to do next, as a result the harness wrote. "The charge may have gone through and has not been retried" is a statement the model can act on, and a stack trace is an invitation to guess.

Guessing is the common failure in agent work generally. Real-SWE 1.1, an October benchmark of coding agents, classified failed runs and found the largest group to be the unverified assumption, a run that "Builds on a guess about the system instead of checking it in the workspace."

## What else belongs in the harness?

The pieces that make a failure recoverable belong there: a cap on retries per call, a log line for every tool call and result, and a checkpoint before any step that can't be undone. The [agent harness](/articles/agent-harnesses/) page covers where those live.

Reversibility is worth more than prevention where it is available.

The Claude Code team's [account of its review process](https://claude.dev/blog/solving-code-review-at-anthropic/) from October 15 lists it among the reasons a mistake stays cheap. "Everything is reversible", it says, with flags, reverts and staged releases named as the means.

Long sessions add one more source of error, which is state the agent no longer has in view. [AI memory management for LLMs](/articles/ai-memory-management/) covers that side, and the [wider pattern of agent failures](/articles/ai-agent-failures/) has its own page.
