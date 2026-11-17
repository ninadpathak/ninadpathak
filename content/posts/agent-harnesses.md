---
category: ai-agents
primary_query: agent harness
siblings:
- agent-loop-anatomy
- agent-error-handling
- ai-agent-taxonomy
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

An agent harness is the code around a language model that turns it into an agent. It runs the loop, calls the tools the model asks for, decides what goes into the context window, and saves state so a run can survive a failure.

The word is the one testing uses. A [test harness](https://en.wikipedia.org/wiki/Test_harness) is the set of stubs and drivers you put around a component so it can be run and checked, and an agent harness does that job for a model, which can't run anything by itself.

It's also the word of the week. On November 17 a benchmark called [FrontierHarness Eval](https://runta.com/blog/introducing-frontierharness-eval-v1-1/) reached the Hacker News front page after running 18 harnesses in 22 configurations against 5 models, and its best-value pick came out different for each model.

So the layer around the model now has its own leaderboard. Below is what an agent harness contains and where it sits in [AI agent architecture](/articles/ai-agents/), with a small one you can run.

## What is an agent harness?

An agent harness is the runtime layer between your application and the model's API. You need one because an API call is stateless: a prompt goes in, a completion comes out, and nothing is remembered.

An agent isn't one call. A research agent might make thirty to fifty model calls in one task, and something has to carry the results from each call into the next, run the tools and stop the run when it's done.

That something is the harness, and vendors now use the word for their own products. Anthropic's [Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/overview) describe Managed Agents as a hosted agent harness, and LangChain calls [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) an agent harness too.

Those uses don't all mean the same thing, and I've taken that up separately in an essay on [how agent docs use the word](/articles/what-agent-harness-means/).

The division of labor is the thing to hold on to. The model reasons, and the harness does everything else.

## What does an agent harness contain?

I split a harness into five parts, and you'll find each of them in any agent that works, whether somebody designed it or it grew:

- **Tool registry:** the list of tools with a schema and a description for each. Permissions live here too, including which calls need a person's approval, and the [Model Context Protocol](/articles/model-context-protocol/) is one way to fill it.
- **Prompt assembler:** the code that builds the context window on every step from instructions, history, retrieved files and tool results.
- **Execution loop:** the cycle that sends the context to the model and runs the tool it picks, which the [four phases of an agent loop](/articles/agent-loop-anatomy/) breaks down. Turn limits and spending limits are enforced here.
- **State manager:** where the run's progress is written, so it exists somewhere other than the context window.
- **Observer:** a log line for every prompt, completion and tool call, tagged with a run ID.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-harnesses/harness-layers.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-harnesses/harness-layers.narrow.svg" width="288" height="1000"><img class="np-has-narrow" src="/static/images/diagrams/agent-harnesses/harness-layers.svg" width="720" height="936" alt="The agent harness sits between the application and the model. Its five components are the execution loop, the tool registry the loop calls in both directions, the prompt assembler that builds the prompt the model receives, the state manager that holds checkpoints, and the observer that logs every step. The model only reasons." loading="lazy" decoding="async"></picture></a>
  <figcaption>The model reasons. The harness handles everything else, including the checkpoint that lets an interrupted run resume.</figcaption>
</figure>

If you don't build these, you still have them. The loop ends up in one file and the retry logic in another, and I'd call that a harness nobody designed.

## Does the harness matter as much as the model?

It matters enough to measure, going by FrontierHarness Eval. The benchmark ran 22 harness configurations with 5 open-weight models on 62 terminal tasks, and over all models the pass rates ran from 50.6% to 61.9%.

Read those pass rates loosely. The post puts a 95% interval of about 10 points either way on each one, and says a difference of a few points is a tie.

Cost moved more than pass rate, and it didn't follow the harness from model to model. Ranking the harnesses by cost on two halves of the runs gave a rank correlation of 0.71 with the same model and 0.26 across different models.

The post is clear about the order of things, though. The model explains 92.8% of the variance in cost per task, and the harness comes second.

The line I'd take to a budget meeting is another one. The post reports that "64.5% of the list-price cost of the scored runs went to trials that did not pass", which is money a harness spends before anyone learns the run failed.

Runta published the benchmark and ran it on its own runtime, and the post lists its limits as open models and one provider. Its per-model winners are soft too: only one of the five held up in nearly every resample of the tasks, and the others won between 25% and 53% of the time.

I'd treat the rankings as theirs and the lesson as general: test harnesses with your model on your own tasks.

## How does a harness recover from a failed step?

It saves state after every step and starts the next attempt from the last save. Say a run dies at step eighteen of twenty-five because a page server returned a 503: without a checkpoint, the retry begins at step one.

Here's that difference in a harness small enough to read. The plan is a fixed list standing in for the model's decisions, and one tool fails the first time it's called:

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

The run without checkpoints made 8 tool calls and the run with them made 6. The two calls it saved are `search` and `read_a`, which had already succeeded and didn't need doing again.

A saving of two calls is nothing, and step eighteen of a long run isn't. LangGraph's [persistence docs](https://docs.langchain.com/oss/python/langgraph/persistence) put the same ability in a framework, saying persistence lets an agent "resume after an interruption, recover from a failure".

Resuming only works if a repeated step is harmless. A tool that sends an invoice has to recognize the second attempt, which is the idempotency-key pattern in [agent error handling](/articles/agent-error-handling/).

## What should a harness do when the context fills up?

It should apply a rule you chose, because doing nothing is also a rule and a bad one. The options I know of, from least work to the largest amount of it:

- **Truncate:** drop the oldest messages.
- **Summarize:** replace old turns with a summary before dropping them.
- **Retrieve:** keep the full history outside the window and fetch what the current step needs.
- **Split the task:** give each subtask its own context and pass results between them.

Whichever you pick, I'd keep the decision in the harness and out of the model's hands. A rule in code behaves the same on every run, and you can test it.

## What should you check before shipping an agent?

Check the harness, part by part. I'd want a yes to each of these:

- Every tool has a schema, a timeout and an error the model can read.
- The loop has a maximum number of turns, and the limit has been tested.
- State is saved after each successful step, and a resume from that save has been tried.
- Every log line carries the run ID.

That last one sounds small. Without a run ID, debugging one bad run means reading the interleaved logs of every run that happened beside it.

## When do you not need an agent harness?

You don't need one when your application controls the flow. A single model call, or a fixed sequence like summarize-then-translate, is a pipeline, and wrapping it in a harness adds parts with nothing to do.

You need one once the model decides which tool to call next. The [taxonomy of AI agents](/articles/ai-agent-taxonomy/) ranks agent types by how much each one decides, and the further up that ranking you build, the more the harness has to do.

## FAQ

**What is a harness in an LLM system?**

A harness is the program around the model that runs it in a loop with tools. The model produces text, and the harness executes tool calls and feeds the results back.

**Is an agent harness the same as an agent framework?**

Not quite, though people use the words loosely. A framework is a library you build with, and a harness is the running layer you end up with, whether you built it from a framework or by hand.

**Is Claude Code an agent harness?**

In the sense used here, yes. Anthropic's docs say the Agent SDK gives you "the same tools, agent loop, and context management that power Claude Code".

**Why is checkpointing the hard part?**

Because the loop is a few lines and recovery isn't. A checkpoint has to capture enough state to continue, and every tool has to be safe to call again.

**Does a better harness make the model smarter?**

No. It makes failures cheaper and more visible, and FrontierHarness Eval suggests it changes what a passing run costs.
