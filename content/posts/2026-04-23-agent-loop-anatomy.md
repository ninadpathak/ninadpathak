---
title: "The Anatomy of an Agent Loop: Perceive, Think, Act, Remember"
date: "2026-04-23"
slug: "agent-loop-anatomy"
description: "The agent loop is not one thing. It is four distinct phases that run in sequence, and understanding each one is how you debug what breaks."
tags: ["ai agents", "agent architecture", "loop design"]
status: published
---

Whenever a system I built starts misbehaving, I come back to the agent loop. The literature describes it as a single construct. The actual implementation has four separate phases, and a failure in any one of them looks like a failure in the whole thing. An agent that loops forever, an agent that ignores a tool error, an agent that forgets what it was doing halfway through a task: those are three different broken phases that all read as "the agent is dumb" until you take the loop apart.

Perceive, think, act, and remember are the four phases. Every agent loop runs some version of this sequence. What differs between agents is what each phase contains and how much work it does.

## Why the loop has four phases and not one

The instinct is to treat the agent as a single inference call that produces an action. That model breaks down the moment the agent needs to call a tool, wait for a result, and then decide what to do next. A single inference call cannot wait. It cannot read a search result and then choose its next query based on what came back.

Because the agent needs a cycle it can repeat, the loop exists at all. Each cycle adds a little more to the task state, the way a person debugging a problem runs one command, reads the output, and forms the next command from it. The loop terminates when the task is complete or when a stop condition is hit.

How different agent architectures handle this loop is something I covered in my post on [the taxonomy of AI agents](/blog/the-taxonomy-of-ai-agents/). Reflex agents skip the think phase almost entirely. Deliberative agents spend significant compute in think before acting. That structural difference matters more than most framework documentation suggests.

<div class="visual-wrapper">
  <div class="visual-title">THE FOUR-PHASE AGENT LOOP</div>
  <div class="visual-container">
    <iframe src="/static/visuals/agent-loop-cycle.html" title="A continuous loop cycling through perceive, think, act, and remember, with a pulse traveling the circle and highlighting each phase in turn" loading="lazy"></iframe>
  </div>
</div>

## Perceive: what the agent sees before it decides

Reading its current context and forming an internal picture of the task state is what the agent does in perceive. The phase is not passive. The agent actively selects what to attend to in the context window.

Scanning the conversation history, any retrieved documents, tool results from the previous step, and the current task instruction is the concrete work of perceive. Out of all of that, the agent builds a working representation of the situation.

Context contamination is the failure mode here. When the context window contains stale information from a previous step, the perceive phase can lock onto the wrong picture. I have seen this happen when a file-read tool returns "permission denied," a later step retries and the retry scrolls the error out of view, and the agent then proceeds as though the file were already loaded. The agent perceives the error as resolved when it is not.

Structured logging in the [agent harness](/blog/agent-harnesses/) is what lets you detect this. Without a record of what the agent was attending to at each perceive step, you cannot diagnose why it made the wrong call.

## Think: reasoning over the perceived state

Think is where the agent reasons about what it has perceived and decides what to do next. No phase varies more between implementations. Some agents use chain-of-thought prompting and generate visible reasoning tokens. Others treat think as a latent computation inside the model weights.

Whether it has enough information to act is the first thing the model evaluates here. The same phase decides which tool to call, if any, and with what arguments.

Engineers new to agent design tend to be surprised that the think phase cannot be observed directly in most frameworks. You get the output of think, not the process. That opacity is harmless on the happy path. It becomes a serious debugging problem when the agent decides, on step three, that a directory exists and you only find out on step twenty-three when a write into it fails.

Token budget management happens here too. The think phase consumes tokens. A deliberative agent that reasons extensively before acting will spend more per step than a reflex agent that acts on pattern matching. I covered token budget strategies in [LLM token budgets and cost control](/blog/llm-token-budgets-cost-control/). The think phase is usually where that budget gets eaten.

## Act: calling tools and producing outputs

Act is the phase where the agent does something. That something might be calling a tool, returning a text response to the user, or updating internal state. Of the four phases, act is the only one that produces observable side effects.

Interacting with the external world is what the loop does in act. A tool call passes arguments to an API and receives a result. The agent receives that result and feeds it back into the loop as a perceived input for the next cycle.

Tool schema design determines whether the act phase succeeds or fails. A poorly designed schema produces malformed arguments that the tool rejects, like a date field the model fills with "next Tuesday" because nothing told it to send an ISO timestamp. A schema with clear types and validation catches that argument error before the tool is even called. [Tool schema design for reliability](/blog/structured-outputs-llms-json-mode-function-calling/) goes deep on what makes schemas actually work in production.

There is an implicit cost to the act phase too. Every tool call has latency. Some tool calls fail. The loop needs policies for both. Timeout enforcement and retry logic belong in the harness, not scattered across tool implementations.

## Remember: updating state for the next iteration

Remember is the phase most agents get wrong. Here the agent updates its internal state to reflect what just happened, so the next loop iteration has accurate context.

Appending the last tool result to the conversation history is the simplest version of remember. That works for short tasks. It breaks for long ones.

A fixed-capacity context window is the root of the problem. Remembering everything means eventually forgetting something. The [memory hierarchy in AI systems](/blog/memory-hierarchy-in-ai-systems/) covers the layered approach that actually solves this. Short-term working memory lives in the context window. Long-term facts get written to external storage and retrieved when relevant.

Conflating those two is how you build expensive systems that still lose track of what they were doing, as my [context windows vs memory](/blog/context-windows-vs-memory/) post argues. Remember is more than appending. The phase decides what to keep, what to compress, and what to evict, the way a person taking notes in a long meeting writes down decisions and drops the small talk.

Checkpointing is the production version of remember. Writing state to durable storage after each successful act phase means the loop can recover from a crash without restarting from scratch, the same reason a long video render writes frames to disk as it goes instead of holding the whole job in memory. An agent that runs longer than a few minutes cannot skip this.

## Where it breaks down in practice

Described as four phases, the loop sounds clean. It stops being clean when you actually run it.

Context window exhaustion happens in remember, not in perceive. When the agent cannot recall what it did ten steps ago, the problem was set in motion two dozen steps earlier, every one of them quietly padding the window with full tool outputs nobody trimmed. Teams that track context window usage in real time catch this before it produces incoherent outputs.

Infinite loops happen in act. The agent calls a tool, gets a result that looks like it needs more work, calls the tool again with slightly different arguments, and repeats. Picture an agent told to make a test pass: it edits a file, the test still fails, it edits the same file again, and it never tries running the test from a fresh state. The stop condition never triggers because the agent keeps perceiving the task as incomplete. Explicit iteration budgets, and tests that exercise them, are not optional.

Tool result loss happens in remember. A tool call returns a result that the agent does not append to context. The next iteration proceeds as if the tool call never happened. The cause is usually a bug in how the harness handles tool results, not a model failure. Structured logging of every tool call and its result is the fix.

The [production AI agent errors](/blog/production-ai-agent-errors/) post has a fuller taxonomy of what goes wrong. The loop phases are the right frame for understanding those errors because each phase has its own failure modes.

## The loop is a design tool

Once you see the four phases, you can evaluate any agent framework by asking what each phase contains and who controls it. Some frameworks give you fine-grained control over think. Others abstract it away. Some give you hooks in remember. Others hide state management entirely.

The frameworks that win in production are the ones where each phase is observable and controllable. You cannot debug what you cannot see. You cannot improve what you cannot measure. Breaking the agent loop into four phases gives you four places to look when something goes wrong.

Start with perceive. Check what the agent actually sees at the start of each iteration. Then check what it remembered from the previous iteration. The bugs that read as reasoning failures usually turn out to be perception or memory problems instead.
