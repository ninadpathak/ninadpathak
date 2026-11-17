---
category: ai-agents
primary_query: agent harness
siblings:
- agent-loop-anatomy
- agent-error-handling
- ai-agent-taxonomy
bridges:
- slug: what-agent-harness-means
  reason: That essay covers how vendor docs use the word this page defines.
date: 2026-03-10
description: An agent harness is the code around the model that runs the loop, calls the
  tools, manages context and saves state. What it contains, why the choice of harness
  shows up in benchmark cost, and a checkpointing example.
status: published
work_note: "Tutorials, explainers and comparisons for AI companies are my work as a freelance technical writer. I'm Ninad Pathak, and I build the example and run it before I draft, so your engineers review working code. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'What an Agent Harness Is and What It Does'
slug: agent-harnesses
video: agent-harnesses
---

An agent harness is the code around a language model that turns the model into an agent. The harness runs the loop, calls the tools the model asks for, decides what goes into the context window, and saves state so a run can survive a failure.

Software testing used the word harness first. A [test harness](https://en.wikipedia.org/wiki/Test_harness) is the set of stubs and drivers you put around a component so the component can be run and checked, and an agent harness plays the same part for a model, which can't call a tool or read a file by itself.

Agent harnesses got their own benchmark this month. On November 17 [FrontierHarness Eval](https://runta.com/blog/introducing-frontierharness-eval-v1-1/) reached the Hacker News front page after running 18 harnesses in 22 configurations against 5 models, and the harness it picked as best value was a different one for each of the 5 models.

That result is why the choice of harness is worth a page of its own. Below is what an agent harness contains and where it sits in [AI agent architecture](/articles/ai-agents/), with a short harness you can run.

## What is an agent harness?

An agent harness is the runtime layer between your application and the model's API. You need one because an API call is stateless: a prompt goes in, a completion comes out, and the API remembers nothing about the exchange.

An agent makes many of those calls for one task. A research agent might make thirty to fifty model calls, and some piece of code has to carry each result into the next call, run the tools and stop the run when the task is done.

That piece of code is the harness, and the split of work is simple: the model reasons, and the harness does everything else. Claude Code is an example you may already use, where the model chooses to run `git diff` and the harness is the part that runs it and hands back the output.

Vendors use the word for their own products as well. Anthropic's [Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/overview) describe Managed Agents as a hosted agent harness, and LangChain calls its [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) package an agent harness.

A hosted service and a Python package are different things to call by one name, and my essay on [how agent docs use the word harness](/articles/what-agent-harness-means/) goes through the differences.

## What does an agent harness contain?

I split a harness into five parts. Each part exists in every working agent, including the agents where nobody planned the parts and the code for them is spread across the application:

- **Tool registry:** the list of tools, with a schema and a description for each one. Permissions belong in the registry too, such as which tool calls need a person's approval, and the [Model Context Protocol](/articles/model-context-protocol/) is one way to fill the registry from outside servers.
- **Prompt assembler:** the code that builds the context window on every step from instructions, history, retrieved files and tool results.
- **Execution loop:** the cycle that sends the context to the model and runs the tool the model picks, which the [four phases of an agent loop](/articles/agent-loop-anatomy/) breaks down. The loop is where a turn limit and a spending limit are enforced.
- **State manager:** the code that writes the run's progress to a file or a database, so the progress survives if the process dies.
- **Observer:** a log line for every prompt, completion and tool call, tagged with a run ID.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-harnesses/harness-layers.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-harnesses/harness-layers.narrow.svg" width="288" height="1000"><img class="np-has-narrow" src="/static/images/diagrams/agent-harnesses/harness-layers.svg" width="720" height="936" alt="The agent harness sits between the application and the model. Its five components are the execution loop, the tool registry the loop calls in both directions, the prompt assembler that builds the prompt the model receives, the state manager that holds checkpoints, and the observer that logs every step. The model only reasons." loading="lazy" decoding="async"></picture></a>
  <figcaption>The model reasons. The harness handles everything else, including the checkpoint that lets an interrupted run resume.</figcaption>
</figure>

A team that never builds these five parts on purpose still ends up with all five. The loop gets written in one file and the retry logic in another, and the result is a harness that nobody designed and nobody can test as one unit.

## Does the harness matter as much as the model?

The model matters more, and the harness still changes the bill. FrontierHarness Eval ran 22 harness configurations with 5 open-weight models on 62 terminal tasks, and across all 5 models the pass rates of the harnesses ran from 50.6% to 61.9%.

An 11-point spread in pass rate looks large, and the post warns against reading it that way. Each pass rate carries a 95% interval of about 10 points either way, and the post says a difference of a few points between two harnesses is a tie.

Cost is where the harnesses separated. Codex CLI was the cheapest harness per task when it ran GLM-5.3 and the 16th cheapest of 22 when it ran Kimi's model, so a harness that is cheap with one model can be expensive with another.

The post puts a number on how much of the cost each side controls. The model explains 92.8% of the variance in cost per task, which leaves 7.2% for everything else, the harness included.

The figure in the post that I'd take to a budget meeting is about failed runs. The post reports that "64.5% of the list-price cost of the scored runs went to trials that did not pass", which means nearly two-thirds of the money was spent on runs that produced nothing usable.

The benchmark has limits that its authors state. Runta ran it on Runta's own runtime, with open-weight models from one provider, and only one of its five per-model winners held up in nearly every resample of the tasks, while the best of the other four won 53% of the resamples.

So I wouldn't copy Runta's ranking into a purchasing decision. I'd copy the method: run two or more harnesses with the model you plan to use, on tasks from your own backlog, and compare cost per passing run.

## How does a harness recover from a failed step?

A harness recovers by saving state after every step and starting the next attempt from the last save. Say a run dies at step eighteen of twenty-five because a page server returned a 503: without a saved checkpoint, the retry begins again at step one.

The script below shows both behaviors in one small harness. The plan is a fixed list of five steps that stands in for the model's decisions, and the `read_b` tool fails with a 503 the first time it's called:

```python
"""A small agent harness: run a loop, checkpoint after every step, resume after a crash."""
import json
import os

CHECKPOINT = "run-42.json"
PLAN = ["search", "read_a", "read_b", "summarize", "save"]   # stands in for the model's decisions
calls = {"count": 0, "read_b_failures_left": 1}


def run_tool(name):
    calls["count"] += 1
    if name == "read_b" and calls["read_b_failures_left"]:
        calls["read_b_failures_left"] -= 1
        raise ConnectionError("503 from the page server")
    return f"{name} ok"


def run(max_steps=10, checkpoint=True):
    state = {"step": 0, "results": []}
    if checkpoint and os.path.exists(CHECKPOINT):
        state = json.load(open(CHECKPOINT))
        print(f"  resumed at step {state['step'] + 1} with {len(state['results'])} results saved")
    while state["step"] < len(PLAN) and state["step"] < max_steps:
        tool = PLAN[state["step"]]                # a real harness asks the model here
        state["results"].append(run_tool(tool))   # act
        state["step"] += 1
        if checkpoint:
            json.dump(state, open(CHECKPOINT, "w"))
        print(f"  step {state['step']}: {tool}")
    return state


for label, checkpoint in (("without checkpoints", False), ("with checkpoints", True)):
    calls.update(count=0, read_b_failures_left=1)
    if os.path.exists(CHECKPOINT):
        os.remove(CHECKPOINT)
    print(label)
    for attempt in (1, 2):
        try:
            run(checkpoint=checkpoint)
        except ConnectionError as error:
            print(f"  attempt {attempt} died: {error}")
    print(f"  tool calls made in total: {calls['count']}\n")
os.remove(CHECKPOINT)
```

Running `python harness_demo.py` on Python 3.13 printed:

```text
without checkpoints
  step 1: search
  step 2: read_a
  attempt 1 died: 503 from the page server
  step 1: search
  step 2: read_a
  step 3: read_b
  step 4: summarize
  step 5: save
  tool calls made in total: 8

with checkpoints
  step 1: search
  step 2: read_a
  attempt 1 died: 503 from the page server
  resumed at step 3 with 2 results saved
  step 3: read_b
  step 4: summarize
  step 5: save
  tool calls made in total: 6
```

The run without checkpoints made 8 tool calls, and the run with checkpoints made 6. The 2 calls that checkpointing saved are `search` and `read_a`, which had already succeeded before the crash and didn't need to run again.

Saving 2 calls out of 8 doesn't matter much, and saving seventeen steps of a twenty-five-step run does. Frameworks ship this ability so you don't have to write it: LangGraph's [persistence docs](https://docs.langchain.com/oss/python/langgraph/persistence) say persistence lets an agent "resume after an interruption, recover from a failure".

Resuming from a checkpoint is only safe when running a step twice does no harm. A tool that emails an invoice has to detect that it already sent that invoice, which is the idempotency-key pattern covered in [agent error handling](/articles/agent-error-handling/).

## What should a harness do when the context fills up?

A harness should apply a rule that you chose in advance for a full context window. A harness with no rule still has to do something when the window fills, and whatever it does then is a rule nobody chose.

Here are four rules to choose from, starting with the one that takes the least code:

- **Truncate:** drop the oldest messages.
- **Summarize:** replace old turns with a summary before dropping them.
- **Retrieve:** keep the full history outside the window and fetch what the current step needs.
- **Split the task:** give each subtask its own context and pass results between them.

I'd write the chosen rule into the harness code and not leave the choice to the model at run time. A rule in code, such as "summarize every turn older than the last ten", behaves the same on every run, and you can write a test for it.

## What should you check before shipping an agent?

Check each of the five parts of the harness before the agent reaches users. I'd want a yes to all four of these:

- Every tool has a schema, a timeout and an error message the model can read.
- The loop has a maximum number of turns, and somebody has run a test that hits the maximum.
- State is saved after each successful step, and somebody has killed a run and resumed it from that save.
- Every log line carries the run ID.

The run ID is the check I'd look at first. Say forty runs write to one log file and a single run misbehaves: a run ID lets you filter the log down to that run's lines, and without the ID you're reading all forty runs interleaved.

## When do you not need an agent harness?

You don't need a harness when your application code decides every step. A single model call is one example, and a fixed two-step sequence that summarizes a document and then translates the summary is another, because in both cases the model never chooses what happens next.

You need a harness once the model decides which tool to call next. The [taxonomy of AI agents](/articles/ai-agent-taxonomy/) ranks agent types by how much each type decides for itself, and an agent that plans its own steps needs every part of the harness listed above.

## FAQ

**What is a harness in an LLM system?**

A harness is the program around the model that runs the model in a loop with tools. The model produces text, and the harness executes the tool calls in that text and feeds the results back to the model.

**Is an agent harness the same as an agent framework?**

No, although people often use one word for the other. A framework such as LangGraph is a library you build with, and a harness is the running code you end up with, whether you built it with a framework or by hand.

**Is Claude Code an agent harness?**

Yes, in the sense this page uses. Anthropic's docs say the Agent SDK gives you "the same tools, agent loop, and context management that power Claude Code".

**Why is checkpointing the hard part?**

Checkpointing is hard because the loop takes a few lines of code and recovery takes design. A checkpoint has to capture enough state to continue the run, and every tool has to be safe to call a second time.

**Does a better harness make the model smarter?**

No. A better harness makes a failed run cost less and leaves a log you can read, and FrontierHarness Eval shows the choice of harness changing what a passing run costs.
