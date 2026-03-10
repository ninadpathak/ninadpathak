---
title: "AI Agents Keep Failing in Production. Here's Why."
date: 2026-02-08
description: "95% of enterprise AI systems fail to reach production. The ones that do mostly fail within six months. The reasons aren't mysterious."
tags: [ai, agents, production, llm]
status: published
---

There's a version of this post that's politely hedged and says things like "while agents show promise, there are challenges to address." This is not that post.

Only 5% of enterprise-grade AI systems make it to production. Of the ones that do, over 80% fail within the first six months. Gartner projected that 40% of agentic AI projects would be scrapped by 2027. Tool call success rates hovered around 15% in late 2024 and climbed to roughly 80% by late 2025. 80% sounds good until you remember that a 1-in-5 failure rate on individual tool calls, in an agent that makes dozens of tool calls per task, produces compounding failure rates that make the system unreliable.

These aren't vibes. They're published numbers from [Composio](https://composio.dev/blog/why-ai-agent-pilots-fail-2026-integration-roadmap) and [Arize](https://arize.com/blog/common-ai-agent-failures/). The question worth asking is why.

## The planning problem is not the execution problem

The [ReAct paper](https://arxiv.org/abs/2210.03629) from Yao et al. in 2022 was important. It showed you could interleave reasoning traces and actions -- Thought, Act, Observe, repeat -- and get agents that could handle tasks on HotpotQA and ALFWorld that pure chain-of-thought couldn't. ALFWorld improvements were substantial: +34% success rate over imitation and RL methods. People read this and got excited about autonomous agents.

What the paper didn't claim was that this approach scales to complex, long-horizon tasks without problems. And a 2025 analysis makes the reason explicit: reasoning is not planning.

Chain-of-thought is a "step-wise greedy policy based on local scores." At each step, the model picks the next action that looks most plausible given what it knows so far. Works fine when tasks are short and each step is independent. It breaks down when you're 15 steps into a multi-hour task and realize that a decision you made at step 3 was wrong, but you can't go back and restructure the plan because you've already executed downstream actions that depend on it.

Human planners deal with this by building out task DAGs before starting execution. You identify dependencies, sequence operations, identify the checkpoints where the plan might need to change. A [2025 paper on Plan-and-Act](https://arxiv.org/html/2503.09572v3) formalizes this: decompose tasks into directed acyclic graphs of subgoals, confine planning to the active node, don't start executing until you know the shape of the work. The benchmark improvements on long-horizon tasks are real.

The SWE-bench leaderboard tracks coding agent performance on real GitHub issues. In early 2024, the best agents were solving around 14% of issues. Claude and Gemini-based agents were in the 75-80% range on the verified subset by early 2026. But SWE-bench tasks are bounded and well-defined: here's a repository, here's a failing test, make it pass. Real agentic workflows are messier than that.

## Errors compound

Here's a thing that seems obvious but has non-obvious implications: in a chain of 20 tool calls, if each call has a 90% success rate (10% failure), your probability of completing the chain without any failure is 0.9^20 = 12%. You'd fail 88% of the time.

Even at 95% per-call success, a 20-step chain succeeds 36% of the time. You need roughly 99.5% per-call reliability to get 90% chain completion at 20 steps. That's a hard engineering target.

The tool call reliability improvements of 2025 (15% to 80%) are real progress. But 80% per-call is not close to good enough for anything that requires sequential tool calls on production data. The improvement hasn't been linear, and the path from 80% to 99.5% is not just better models -- it requires better error handling, retry logic, checkpointing, and probably task decomposition so individual chains are shorter.

## Hallucination accumulates differently in agents

Hallucination works differently in agents than in single-turn Q&A. A chat system produces a discrete error: the model either gets the answer right or it makes something up. Agents have a contamination problem instead. The model reasons about tool outputs. When those outputs contain hallucinated information from a previous step, the subsequent reasoning treats that as ground truth and builds on it.

After a 20-step task, errors from step 2 can be deeply embedded in the agent's working understanding of the task state. You often can't trace the final wrong answer back to the original hallucination without full traces.

The hallucination rates by task type are sobering. [Vectara's 2023 research](https://vectara.com/blog/cut-the-bull-detecting-factual-errors-in-llm-responses/) found ~3% hallucination rate for text summarization. Medical systematic reviews: 28-40%. Legal citation generation: 69-88% (per Stanford research). These are single-turn tasks. In multi-step agents operating in specialized domains, there's no principled reason to expect rates to be lower.

## The context window is a fixed resource and agents burn through it

Every tool output gets appended to the agent's context. Every reasoning trace. Every observation. For a complex, long-running task, you can fill a 200k token context window faster than you'd expect.

What happens when the context fills up varies by implementation. Some truncate from the beginning (losing task context). Some summarize (introducing information loss and potential distortion). Some just fail. None of these are great.

[MemGPT](https://arxiv.org/abs/2310.08560) from UC Berkeley treated this as an operating system problem: the context window is like RAM, external storage is like disk, and the model needs to actively manage paging between them. The system uses OS-style interrupts to control flow when context limits are approached. It's the right framing. The practical implementations are getting better, but most production agents aren't doing this properly yet.

## The actual failure modes in order of frequency

Based on what's reported in failure analyses and post-mortems from teams that have deployed:

**1. Tool integration failures.** APIs change, authentication expires, response formats are inconsistent, rate limits hit unexpectedly. The agent gets a 429 or a changed response schema and either fails silently or spirals. The most common failure mode and the most fixable: robust error handling, typed tool definitions, retry logic with backoff.

**2. Context overflow.** The task grows longer than expected and context fills. At best, the agent degrades gracefully. Usually it doesn't.

**3. Goal drift.** On very long tasks, agents lose track of the original objective and optimize for something adjacent. They complete the task as they currently understand it, which isn't the task as specified. Happens more often than it should when initial instructions are ambiguous.

**4. Hallucination propagation.** Discussed above. Particularly bad in domains with specialized knowledge (legal, medical, financial) where the model's training knowledge is unreliable and tool outputs should be the ground truth.

**5. Plan rigidity.** The agent makes a planning decision early that turns out to be wrong, but continues executing based on that decision because it has no mechanism for detecting that the plan needs to change.

## What actually works

The systems I've seen work well in production have a few things in common.

They're scoped narrowly. The agent does one class of task, in a constrained environment, with a small set of tools. Scope creep kills agent reliability. An agent that "helps with customer support" is harder to make reliable than an agent that "classifies incoming support tickets into five categories and routes them."

They use structure, not natural language, for tool outputs wherever possible. JSON schema validation on tool responses, typed interfaces, explicit error codes rather than error messages that the model has to interpret. The less the model has to reason about tool output format, the less it can get wrong.

They checkpoint. For tasks longer than five steps, they write state to durable storage at each step. If something fails, you restart from the last checkpoint, not from scratch.

They have human-in-the-loop gates for high-stakes decisions. Human oversight at this stage isn't a failure of the system -- it's the right design for the current state of agent reliability. The goal is to extend agent autonomy over time as you build confidence in specific decision types, not to remove humans from the loop on day one.

Anthropic's [Model Context Protocol](https://modelcontextprotocol.io/specification/2025-11-25) is worth paying attention to for the tool integration problem specifically. Instead of each agent integration being a custom implementation, MCP provides a standard for how LLM applications connect to external tools and data sources. The adoption has been broad enough that it's looking like the default standard for agent-to-tool connections. Fewer bespoke integrations means fewer failure modes.

---

The fundamental issue isn't that agents are bad. It's that agents are deployed as if they were reliable at tasks they haven't demonstrated reliability on, in environments they haven't been tested in, with expectations calibrated to demos rather than production behavior.

The teams getting agents to work in production are treating them like the unreliable systems they currently are: narrow scope, explicit error handling, checkpoint-based recovery, conservative expansion of autonomous decision-making. That's not a limitation to engineer around. That's the right way to build with the current technology.
