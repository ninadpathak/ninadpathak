---
title: "The Four Types of Memory in AI Agents (And Why Most Systems Only Use One)"
date: 2026-03-08
description: "Sensory, short-term, episodic, semantic -- AI agents can use all four types of memory. Most implementations use only the context window and wonder why they fail at long tasks."
tags: [ai, agents, memory, architecture]
status: published
---

When cognitive scientists talk about memory, they usually break it into four categories: sensory, short-term, episodic, and semantic. These categories emerged from studying how humans store and retrieve information. They also, as it turns out, map remarkably well onto the architecture decisions you face when building AI agents that need to remember things.

The parallel isn't perfect. Biological memory and vector stores are not the same thing. But the framework is useful because it forces you to ask a question that most agent implementations skip entirely: what *kind* of memory does this agent actually need, for which tasks, at which timescales?

The question gets answered by accident in most implementations. Everything goes in the context window, context runs out, RAG gets added as an afterthought, and nobody understands why the agent can't maintain coherent behavior across a long task. Getting memory architecture right requires being deliberate about it from the start.

## Sensory memory: the input buffer

Sensory memory in humans is extremely short-lived, around 200-500 milliseconds for visual input. It's the brief persistence of raw sensory data before it's either processed into short-term memory or discarded.

For AI agents, the analog is the raw input stream: the tokens the model is currently processing, the tool call that just returned, the image that was just passed in. Sensory memory is automatic. You don't design it; you just accept that the model processes inputs as they arrive and that unprocessed context evaporates if you don't do anything with it.

The practical implication: raw tool outputs that aren't explicitly stored somewhere are gone after the current context. An agent that reads a file, does something with the content, and then needs to reference the original file content three steps later will fail unless that content was deliberately captured. The model's "memory" of the file isn't persistent. It's sensory.

## Short-term memory: the context window

Short-term memory in humans holds roughly 7 (+/- 2) items and decays rapidly without rehearsal. The context window is the direct analog: a fixed-capacity, immediately accessible workspace that holds the current task state.

The context window is the only memory type that almost every LLM application uses. Conversations go in, tool outputs get appended, reasoning traces accumulate. The model has instant access to everything in the window. The cost is that the window is finite and linear.

Two problems compound each other here.

The first is the capacity problem. A 200k token context sounds large until you're running a multi-hour task and filling it with tool outputs, reasoning traces, and intermediate state. Tokens per minute varies by provider, but at Claude's output speeds, a moderately complex agent can burn through 100k tokens of context in under an hour of active work.

The second is the [lost-in-the-middle problem](/posts/lost-in-the-middle/). Information at the beginning and end of the context window is reliably attended to. Information in the middle gets deprioritized. An agent that accumulates 50k tokens of intermediate state before reaching the final task step is operating with degraded access to much of that history, even though it's technically in the window.

The fix for capacity is context compression: summarizing earlier turns, rolling up completed subtask results, truncating irrelevant intermediate steps. The fix for position bias is more subtle: structure the context deliberately, put the most important persistent information at the front (system prompt, core task spec), and keep the working area near the end.

Neither fix is automatic. Both require explicit implementation decisions.

## Episodic memory: what happened before

Human episodic memory stores specific events tied to context: you remember *that* meeting, with *those* people, where *that* decision was made. It's retrievable, but retrieval requires a cue.

For AI agents, episodic memory is any persistent record of past interactions, sessions, or task executions that can be retrieved when relevant. The context window doesn't provide this -- it's session-scoped. Episodic memory persists across sessions.

A customer support agent without episodic memory handles every conversation as if the customer is new. One with episodic memory can retrieve: "Last time this user contacted us about billing, the issue was a duplicate charge that we resolved with a credit. Mentioning that credit proactively might save five minutes." The information isn't in the current context. It needs to be retrieved from somewhere.

The implementation options range from simple to complex:

**Conversation logs with semantic search.** Store every past conversation as a text blob, chunk it, embed it, retrieve by similarity at the start of each new session. Simple to implement, covers most cases. The quality of retrieval depends entirely on your chunking strategy and embedding model.

**Structured episode storage.** Instead of raw logs, extract structured records: what was the task, what was the outcome, what intermediate decisions were made, what failed and why. Retrieving structured records gives the agent much cleaner context than dumping raw conversation history.

**[Mem0](https://mem0.ai/) and similar memory layers.** Projects like Mem0 wrap the storage and retrieval layer and expose it as an API. Instead of implementing semantic search over your own database, you push observations to the memory service and pull relevant memories before each agent step. The tradeoff is dependency on an external service; the benefit is not having to implement vector search, chunking, and deduplication yourself.

The challenge with episodic memory is relevance. Retrieving everything stored about a user is rarely useful. The useful retrieval is context-aware: given the current task and the current session context, what past episodes are actually informative? That's a retrieval quality problem, and it's harder than it looks.

## Semantic memory: general knowledge

Semantic memory in humans is disconnected from specific experiences. You know what photosynthesis is without remembering when or where you learned it. Knowledge that's been abstracted from its original context.

For AI agents, the model's training weights are semantic memory. The model "knows" how to write Python, what REST APIs are, how TCP/IP works -- not because of anything in the context window, but because that knowledge was baked in during training.

The limitation is obvious: training knowledge has a cutoff date and can't be updated cheaply. Semantic memory in an AI system also covers knowledge bases, documentation stores, and curated fact repositories that the agent can query.

The retrieval mechanism for semantic knowledge is usually RAG: chunk the knowledge base, embed it, retrieve the top-k relevant chunks at query time, include them in the context. The effectiveness depends on retrieval quality, and retrieval quality degrades as the knowledge base grows and as the queries become more complex.

There's a distinction worth making here between semantic memory as retrieval and semantic memory as fine-tuning. RAG retrieves knowledge at inference time. Fine-tuning bakes it into the weights. For knowledge that's stable and used constantly, fine-tuning is worth considering -- you trade flexibility for latency and quality. For knowledge that changes frequently, RAG is the only practical option.

A harder case is structured knowledge that requires reasoning, not just retrieval. If the knowledge base is a set of policies with complex interdependencies, simple chunk retrieval won't give the agent the right mental model for applying them. Knowledge graphs -- where concepts and their relationships are explicitly represented -- can help, but they're significantly more expensive to build and maintain.

## The architectures that actually work

The interesting design question is how these memory types interact. Most production agent systems that handle non-trivial tasks combine at least three of the four.

**Short + episodic** is the minimum viable setup for any agent that handles returning users or multi-session tasks. The context window handles the current conversation; episodic memory provides relevant history at session start. Retrieval quality matters enormously here.

**Short + semantic (RAG)** is standard for knowledge-intensive tasks: customer support with product docs, code assistants with codebase context, research assistants with document collections. The failure mode is retrieving irrelevant chunks that crowd out useful context.

**Full four-layer architectures** show up in systems that need to handle complex, long-running tasks across sessions. An example: an agent that helps with ongoing software projects.

- Sensory: current file contents, recent terminal output
- Short-term: current task spec, immediate error messages, the last 10 turns of the conversation
- Episodic: past sessions on this codebase, previous bugs and how they were fixed, the developer's stated preferences from prior interactions
- Semantic: language documentation, project-specific conventions extracted from the codebase and stored as structured knowledge

Building that well takes real engineering. The tricky parts are retrieval relevance (pulling the right episodic and semantic context for the current moment), context assembly (deciding what goes where in the window), and memory maintenance (knowing when old episodic records are stale enough to deprioritize).

## What this means for agent reliability

There's a practical reason most agents use only short-term memory: it's the default. The LLM SDK gives you a messages array, you append to it, you send it. No additional infrastructure required.

The failure mode is predictable: the agent works fine on tasks that fit in the context window, fails on long tasks where context fills up, can't maintain consistency across sessions, and halluccinates facts it should be looking up.

[Research on production agent failures](https://arize.com/blog/common-ai-agent-failures/) consistently lists context overflow and goal drift among the top failure modes. Both are symptoms of treating the context window as the only memory store.

The design principle that follows: memory architecture is not an afterthought. It's a first-class decision, made before you start implementing. Before writing any agent code, the questions to answer are: what does this agent need to remember across turns, across tasks, and across sessions? Which of those memory types are time-sensitive enough that they belong in the context window, and which are stable enough that they can be retrieved on demand?

Answering those questions before writing code is the difference between an agent that degrades after 30 minutes and one that handles week-long projects without losing the thread.
