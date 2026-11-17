---
category: ai-agents
primary_query: agent loop
siblings:
- ai-agent-taxonomy
- agent-harnesses
- agent-error-handling
bridges:
- slug: llm-token-budgets
  reason: Every pass through the loop is another model call, and that page adds up what the calls cost.
- slug: llm-structured-outputs
  reason: The act phase depends on tool arguments that match a schema.
- slug: context-windows-vs-memory
  reason: A loop that only appends runs into the context window, which is a different thing from memory.
date: '2026-04-23'
description: 'An agent loop is the cycle of model call, tool call and result that an agent repeats until it stops. Perceive, think, act and remember, a loop you can run, and how two SDKs end one.'
slug: agent-loop-anatomy
status: published
work_note: "Explainers like this one are what I write for AI companies as a freelance technical writer. I'm Ninad Pathak, and I run the product before I write about it. [Let's work on yours](/services/freelance-technical-writer-for-ai-companies/)."
title: 'The Four Phases of an Agent Loop'
video: agent-loop-anatomy
updated: 2026-11-17
---

An agent loop is the cycle an AI agent repeats until its task is done: the model reads the state so far, picks a tool call, the tool runs, and the result goes back into the state. A single pass is a turn, and an agent is whatever keeps taking turns without a person in between.

Programmers have typed into a loop like this since at least 1964, when Deutsch and Berkeley's Lisp for the PDP-1 described its read-eval-print cycle. A [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) reads a line, evaluates it, prints the result and waits for you.

An agent loop has nobody to wait for. The model reads the printed result itself and writes the next line.

That's the whole mechanism under [AI agent architecture](/articles/ai-agents/), and the four phases below are a way to find which part of it broke.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-loop-anatomy/agent-loop.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-loop-anatomy/agent-loop.narrow.svg" width="288" height="1064"><img class="np-has-narrow" src="/static/images/diagrams/agent-loop-anatomy/agent-loop.svg" width="720" height="664" alt="The agent loop drawn as a circular track: perceive, think, act, and remember in sequence, returning to perceive until the task is complete or a stop condition ends the run. A task enters at perceive, the run exits from remember, and the context window at the centre fills with each pass until its newest tokens spill past the edge." loading="lazy" decoding="async"></picture></a>
  <figcaption>One pass through the loop. A tool call with bad arguments is an act failure, and a history that outgrows the context window is a remember failure.</figcaption>
</figure>

## What is an agent loop?

It's a `while` loop around a model call. Both big vendor SDKs document theirs in a few lines, and the two descriptions agree.

Anthropic's [Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/agent-loop) say Claude "evaluates your prompt, calls tools to take action, receives the results, and repeats until the task is complete." OpenAI's [Agents SDK docs](https://openai.github.io/openai-agents-python/running_agents/) list the same steps for its runner: call the model, return if the output is final, and otherwise run the tool calls, append the results and go round again.

Neither vendor uses the words perceive, think, act and remember. Those four names are a teaching split, and I keep them because each one points at a different place to look when a run goes wrong.

| Phase | What happens | Where you see it |
| --- | --- | --- |
| Perceive | The model is sent the system prompt, the tool definitions and the history so far | The request your code sends |
| Think | The model decides between answering and calling a tool | The response, as text or a tool call |
| Act | Your code runs the tool the model asked for | The tool's own logs and side effects |
| Remember | The result is appended to the history for the next turn | The message list after the turn |

## What does an agent loop look like in code?

About thirty-five lines. The script below swaps the model for a list of canned decisions, so the loop is the only moving part, and its task follows the worked example in Anthropic's docs.

```python
"""A whole agent loop in one function, with a scripted stand-in for the model."""


def scripted_model(script):
    """Return a 'model' that replays canned decisions, one per call."""
    turns = iter(script)
    return lambda messages: next(turns)


STATE = {"fixed": False}


def run_tests(arg):
    return "all tests pass" if STATE["fixed"] else "2 failed: test_login, test_logout"


def edit_file(arg):
    STATE["fixed"] = True
    return f"edited {arg}"


TOOLS = {"run_tests": run_tests, "read_file": lambda arg: f"contents of {arg}", "edit_file": edit_file}


def run(model, task, max_turns):
    messages = [("user", task)]                      # remember: the state starts as the task
    for turn in range(1, max_turns + 1):
        decision = model(messages)                   # perceive and think: one model call
        if decision["tool"] is None:                 # no tool call means the loop is done
            print(f"turn {turn}: final answer: {decision['text']}")
            return "finished"
        result = TOOLS[decision["tool"]](decision["arg"])   # act
        messages.append(("tool", result))            # remember: the result joins the state
        print(f"turn {turn}: {decision['tool']}({decision['arg']}) -> {result}")
    return "stopped at the turn limit"


fix = [
    {"tool": "run_tests", "arg": ""},
    {"tool": "read_file", "arg": "auth.py"},
    {"tool": "edit_file", "arg": "auth.py"},
    {"tool": "run_tests", "arg": ""},
    {"tool": None, "text": "Both tests pass now."},
]
print("run 1:", run(scripted_model(fix), "Fix the failing tests", max_turns=10))

STATE["fixed"] = False
stuck = [{"tool": "read_file", "arg": "auth.py"}] * 50
print("run 2:", run(scripted_model(stuck), "Fix the failing tests", max_turns=3))
```

`python3 loop_demo.py` prints both runs.

```text
turn 1: run_tests() -> 2 failed: test_login, test_logout
turn 2: read_file(auth.py) -> contents of auth.py
turn 3: edit_file(auth.py) -> edited auth.py
turn 4: run_tests() -> all tests pass
turn 5: final answer: Both tests pass now.
run 1: finished
turn 1: read_file(auth.py) -> contents of auth.py
turn 2: read_file(auth.py) -> contents of auth.py
turn 3: read_file(auth.py) -> contents of auth.py
run 2: stopped at the turn limit
```

The first run ends the way a healthy loop ends, with a turn that calls no tool. The second run is an agent reading one file forever, and the only thing that stops it is the number passed as `max_turns`.

## How does an agent loop stop?

It stops when the model answers without asking for a tool, or when your code says enough. The first is the model's judgment, so a production loop needs the second as well.

Both SDKs give you that limit, and both raise an error when a run hits it. OpenAI's runner raises a `MaxTurnsExceeded` exception when a run passes `max_turns`.

Anthropic's SDK first yields a result whose subtype is `error_max_turns`, with the cost and session id and no final answer, and then raises. It also has a second limit in dollars called `max_budget_usd`.

Its docs are plain about leaving both off: the loop then runs until Claude decides it's finished, which they call fine for a well-scoped task and a risk on an open-ended prompt.

So set a limit, and treat hitting it as a result your code handles. What to do next is a policy question, which [error handling for agents](/articles/agent-error-handling/) takes up.

## Where does each phase fail?

Each phase has a failure of its own, and they get mistaken for one another. A model that reasons badly and a model that was shown the wrong history both produce a wrong tool call.

**Perceive.** The model can only use what's in the request. If an old error message is still in the history, or the file it needs was never read, the decision that follows will be wrong for a reason the model can't see.

**Think.** You get the decision and not the reasoning behind it. That's harmless on the happy path, and it's why the logging in an [agent harness](/articles/agent-harnesses/) records the request beside the response.

**Act.** A tool call fails when its arguments don't match what the tool accepts, such as a date sent as "next Tuesday". A strict schema catches that before the tool runs, and [structured outputs](/articles/llm-structured-outputs/) covers how.

**Remember.** Appending every result works until the history outgrows the context window. Anthropic's SDK then compacts the history into a summary, and its docs warn that instructions from early in the conversation may not survive.

And every turn costs a model call, on a history that's longer than the turn before. The [token budgets guide](/articles/llm-token-budgets/) runs that arithmetic.

## Which phase should you check first?

Check perceive, then remember. A wrong decision is more often a wrong input than a wrong thought, in my reading of how these loops are built, and both of those phases are fully visible in the message list.

So print the request for the turn that went wrong. If the fact the model needed isn't in it, find the earlier turn that should have put it there.

Past that, the question becomes what the agent should keep between turns and between sessions. The context window holds one run, and [context windows vs memory](/articles/context-windows-vs-memory/) explains why that isn't the same thing as memory.

How much of the loop an agent runs alone is what separates the [types of AI agents](/articles/ai-agent-taxonomy/).

## FAQ

**What is an agent loop?**

It's the cycle an AI agent repeats: a model call, a tool call if the model asks for one, and the result added to the history for the next call. The loop ends when the model answers without a tool call or a limit is reached.

**What is the difference between an agent loop and a ReAct loop?**

[ReAct](/glossary/react-prompting/) is one pattern for the loop, in which the model writes its reasoning between actions. Every ReAct agent runs an agent loop, and an agent loop doesn't have to show its reasoning.

**How many turns should an agent loop be allowed?**

Enough for the longest task you expect, with a hard limit above that. Both OpenAI's and Anthropic's SDKs accept a turn limit, and Anthropic's also accepts a spending limit.
