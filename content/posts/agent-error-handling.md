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
work_note: "I'm Ninad Pathak, a freelance technical writer for AI companies that build agents, agent memory and LLM infrastructure. I write their tutorials and technical articles, and I run each product before I write about it. [Hire me for yours](/services/freelance-technical-writer-for-ai-companies/)."
title: "Error Handling in Production AI Agents"
slug: agent-error-handling
video: agent-error-handling
updated: 2026-11-17
---

Error handling in production AI agents turns on one question: after a tool call fails, who decides what happens next. Ordinary software answers with code that someone wrote and tested, and an agent sends the error text back to a model.

The [fallacies of distributed computing](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing), a list L Peter Deutsch assembled at Sun Microsystems in 1994, begins with "The network is reliable", and an agent that calls tools over a network meets every item on it.

What an agent adds is the reader of the error. A model shown "connection timed out" after a payment call has to guess whether the customer was charged, and nobody can unit-test that guess.

Within [AI agent architecture](/articles/ai-agents/), error handling is the code that takes such guesses away from the model.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-error-handling/error-taxonomy.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-error-handling/error-taxonomy.narrow.svg" width="288" height="704"><img class="np-has-narrow" src="/static/images/diagrams/agent-error-handling/error-taxonomy.svg" width="720" height="264" alt="Five failure modes of an agent that calls tools. Context exhaustion: tool results pile up until the context window is full and the next call is rejected. Schema drift: the model calls a tool with parameters from an older schema version. Partial failure: some parallel tool calls succeed and some fail. Ambiguous timeout: a request times out after the server may already have processed it, so a retry can execute it twice. Observability gaps: without structured logs of tool calls there is no record of what the agent tried." loading="lazy" decoding="async"></picture></a>
  <figcaption>Each mode has its own fix: a hard cap on tool history, versioned schemas, per-call tracking, idempotency keys and a log line for every tool call.</figcaption>
</figure>

## What do the protocols tell the model after a failure?

More than a bare error flag, and less than a retry decision. Anthropic's [tool use documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) gives a tool result one field for it, "is_error (optional): Set to true if the tool execution resulted in an error.", and then advice on the text that goes with the flag.

"Write instructive error messages", the page says, and "include what went wrong and what Claude should try next". The current [Model Context Protocol specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools), the revision of July 28, 2026, takes the same line, describing tool execution errors as "actionable feedback that language models can use to self-correct and retry with adjusted parameters".

That advice fits an error the model caused. A date in the wrong format is fixed by sending a better one, and the model is the right party to do it.

It fits badly when the fault is on the far side of the call. A timeout after a charge has no better parameters to try, and the right move may be to do nothing.

## Does the protocol say whether a call is safe to repeat?

It can, as a hint. The MCP [schema](https://modelcontextprotocol.io/specification/2026-07-28/schema) lets a tool carry an annotation named `idempotentHint`, which when true means "calling the tool repeatedly with the same arguments will have no additional effect on its environment."

The schema then limits what a client may do with it. "Clients should never make tool use decisions based on ToolAnnotations received from untrusted servers."

So the protocol carries the knowledge when the tool's author supplies it, and tells the client to distrust it unless it trusts the author. The decision to retry stays with the harness, which is the only party that knows which servers it trusts.

## How should an agent classify errors?

Classify every tool error in code as transient, permanent or ambiguous, and let that label decide the recovery before the model sees anything.

| Kind | Example | What the harness does |
| --- | --- | --- |
| Transient | Rate limit, overloaded server | Retry with backoff |
| Permanent | Invalid API key, missing resource | Fail fast and report |
| Ambiguous | Timeout after the request was sent, or any error the code doesn't recognise | Retry only if the call is idempotent |

The ambiguous kind is the dangerous one, and it has to be the default. A classifier that treats an unknown error as transient will repeat a payment the first time a new exception appears.

## What does an idempotency key change?

It makes an ambiguous failure safe to retry, because the server recognises the repeat and returns the first result. Stripe's [API reference](https://docs.stripe.com/api/idempotent_requests) describes the behaviour for its v1 API: "Retries with the same key return the saved response, including 500 errors."

The simulation below calls a payment API that charges the customer and then fails on the first call. It tries a timeout under each retry policy, then an error the classifier has never seen.

```python
"""A charge tool that fails after it has charged, called four ways."""
import uuid


class RateLimited(Exception):
    """The server refused the request before doing any work."""


class PaymentAPI:
    def __init__(self, failure):
        self.charges, self.seen, self.calls, self.failure = [], {}, 0, failure

    def charge(self, customer, cents, idempotency_key=None):
        self.calls += 1
        if idempotency_key in self.seen:
            return self.seen[idempotency_key]          # replay the saved response
        self.charges.append((customer, cents))
        receipt = {"status": "charged", "cents": cents}
        if idempotency_key:
            self.seen[idempotency_key] = receipt
        if self.calls == 1:
            raise self.failure                          # the work was done
        return receipt


def classify(error):
    if isinstance(error, RateLimited):
        return "transient"      # named cases only: the server did nothing
    if isinstance(error, PermissionError):
        return "permanent"      # retrying cannot help
    return "ambiguous"          # anything unrecognised may have acted


def run(label, failure, use_key, blind=False):
    api = PaymentAPI(failure)
    key = str(uuid.uuid4()) if use_key else None
    outcome = "ok"
    for attempt in (1, 2):
        try:
            api.charge("cus_42", 4_900, idempotency_key=key)
            outcome = "ok"
            break
        except Exception as error:
            kind = classify(error)
            if blind or kind == "transient" or (kind == "ambiguous" and use_key):
                outcome = "gave up"
                continue                                # safe, or assumed safe, to repeat
            outcome = f"stopped, reported as {kind}"
            break
    print(f"{label:<30} attempts: {api.calls}  charges: {len(api.charges)}  {outcome}")


timeout = TimeoutError("no response from payment API")
run("blind retry", timeout, use_key=False, blind=True)
run("classified, no key", timeout, use_key=False)
run("classified, idempotency key", timeout, use_key=True)
run("unrecognised error, no key", ConnectionResetError("reset by peer"), use_key=False)
```

`python3 retry_demo.py` reports each policy with the number of charges it made.

```text
blind retry                    attempts: 2  charges: 2  ok
classified, no key             attempts: 1  charges: 1  stopped, reported as ambiguous
classified, idempotency key    attempts: 2  charges: 1  ok
unrecognised error, no key     attempts: 1  charges: 1  stopped, reported as ambiguous
```

The blind retry charges twice and reports success. With no key, the classified run stops after one charge and reports the failure as ambiguous, and with a key the retry goes through with the customer still charged once.

The connection reset in the last run is an error the classifier has no rule for. It is treated as ambiguous and stopped, which is the behaviour the table asks for.

The simulation is a toy with one failure in it. The model was never asked what to do in any of the runs.

## Which other failure modes need their own fix?

The ambiguous timeout is one of five in the figure above. The list is my own grouping of failures that follow from the mechanics of a tool loop, and it comes with no incident counts.

| Failure mode | What goes wrong | Fix |
| --- | --- | --- |
| Context exhaustion | Tool results fill the window until a call is rejected | A hard cap on tool history |
| Schema drift | The model calls a tool with an old parameter set | Versioned schemas |
| Partial failure | Some parallel calls succeed and some fail | Per-call tracking |
| Ambiguous timeout | A retry can run the action twice | Idempotency keys |
| Missing logs | No record of what the agent tried | A log line for every tool call |

## What should the model be told after a failure?

Tell it what happened and what it is allowed to do next, in a result the harness wrote. That is Anthropic's instruction about error messages applied by the harness: "The charge may have gone through and has not been retried" is a statement the model can act on, and a stack trace is an invitation to guess.

Guessing is the largest single cause in the one breakdown of failed agent runs I know of. [Real-SWE 1.1](https://withspecific.com/blog/real-swe), an October benchmark of coding agents, classified its failed runs and found the biggest group to be the unverified assumption, a run that "Builds on a guess about the system instead of checking it in the workspace."

## What else belongs in the harness?

The pieces that make a failure recoverable belong there: a cap on retries per call, a log line for every tool call and result, and a checkpoint before any step that can't be undone. The [agent harness](/articles/agent-harnesses/) page describes where those live.

The Claude Code team's [account of its review process](https://claude.dev/blog/solving-code-review-at-anthropic/) from October 15 gives reversibility as a reason a mistake stays cheap. "Everything is reversible", it says, with flags, reverts and staged releases named as the means.

Long sessions add one more source of error, which is state the agent no longer has in view. [AI memory management for LLMs](/articles/ai-memory-management/) deals with that side, and the [wider pattern of agent failures](/articles/ai-agent-failures/) has its own page.
