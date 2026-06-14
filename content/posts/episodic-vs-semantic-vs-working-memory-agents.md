---
title: "Episodic, Semantic, and Working Memory in AI Agents: A Practical Map"
date: "2026-05-04"
slug: "episodic-vs-semantic-vs-working-memory-agents"
description: "AI agents juggle three distinct memory types. Getting them wrong is the source of most agent memory failures I see in production."
tags: ["ai-agents", "agent-memory", "llm-architecture"]
status: published
---

For two weeks I debugged an agent that kept forgetting what it had just done. The logs looked fine, the retrieval pipeline was fast, and the context window was spacious. The problem was a category error: the agent was storing episodic memories in a semantic memory system, and semantic facts in episodic storage. Everything was there. Nothing was useful. When I asked it what it had changed in the last hour, it answered with a vector-similarity dump of every config edit it had ever made, ranked by topic instead of by time.

That distinction is what I want to map out here, because it sits underneath most agent memory failures I see in code reviews and production postmortems.

## The three memory types your agent is actually running

### Working memory: the scratchpad

Whatever the model has right now is working memory. For an LLM, that means the context window. I think of it as the agent's immediate scratchpad: what was said in the last few turns, what the current task is, what tools are available.

Fast and volatile, working memory disappears when the context resets. I ran into that wall building a long-running customer support agent. Between turns, the agent would lose track of what the customer had already been told and re-offer a refund it had offered two messages earlier. A better retrieval system did nothing for it. What worked was persisting a one-paragraph session summary back into working memory at the start of every turn.

The context window also caps how much working memory you get. Pushing an agent toward 200 turns in a single session, I start seeing degradation even when retrieval is working perfectly, because the model has too much to reason over at once. It is like trying to keep a forty-item grocery list in your head while someone keeps adding to it: past a point you stop holding the early items at all.

If you want to understand how context windows fit into this picture, I wrote about [LLM context windows explained](/blog/llm-context-windows-explained/) and how they interact with different memory systems.

### Episodic memory: what happened

Specific experiences live in episodic memory. I think of it as the agent's autobiographical record: this task was attempted on this date, failed with this error, the user corrected it this way.

When a DevOps agent recalls that "the last deployment on Friday failed because the database migration timed out," that is episodic retrieval. The agent is pulling a single event out of its history rather than a general fact about deployments.

Treating episodic memory like a database is the failure mode I run into most. Engineers build retrieval pipelines that query episodic storage with semantic similarity, so when the user asks "what went wrong with my deployments" the agent returns semantically similar past events. Almost all of them are useless here, because the user wants a chronological account of the last few runs and gets a topic cluster spanning six months instead.

Why that asymmetry breaks RAG pipelines is something I covered in [asymmetric retrieval and why it breaks your agent memory](/blog/asymmetric-retrieval-agent-memory/). Episodic recall is directional in a way that semantic search has no way to model.

### Semantic memory: what is true

Facts, knowledge, and learned abstractions live in semantic memory. Plenty of people mean exactly this when they say "knowledge base" or "world model." Nothing in it is tied to a specific time or experience.

A coding agent's semantic memory holds facts like "Python's list.sort() is stable" or "React components re-render when state changes." Those are general truths that apply across contexts, with no date attached.

A wrong semantic memory makes the agent confidently misinform you, citing a function signature that changed three versions ago. A wrong episodic memory makes the agent contradict itself, insisting it already ran the test suite when it never did. The error signatures look nothing alike, and debugging them takes different tools.

Whenever I reason about where semantic memory sits relative to retrieval, I come back to the [memory hierarchy in AI systems](/blog/memory-hierarchy-in-ai-systems/). The hierarchy framing helps because it makes one thing obvious: semantic memory is a single layer, the slow-changing reference shelf the agent reads from, far from the whole system. Treating it as the whole system is how teams end up dumping yesterday's task logs into the same store as their hard-won API facts and wondering why answers drift.

<div class="visual-wrapper">
  <div class="visual-title">THE THREE MEMORY TYPES</div>
  <div class="visual-container">
    <iframe src="/static/visuals/three-memory-types.html" title="Working, episodic, and semantic memory side by side: what each stores and its lifespan" loading="lazy"></iframe>
  </div>
</div>

## Why agents get the types confused

Most agent frameworks expose a single "memory" interface and call it done. You hand it `agent.add_to_memory(message)` and the framework decides what to do with the message. That decision usually rides on token budget or retrieval latency, never on what kind of information you just handed it.

Reviewing a widely used agent framework last year, I found every user message getting stored in episodic memory regardless of content. The agent's learned knowledge about Python, Git, and deployment pipelines sat in the same bucket as "ok thanks, try that again." Retrieval came back noisy because episodic memory had been flooded with transient chatter.

We fixed it with a content-type router. Factual statements and learned patterns went into semantic memory, session events and task outcomes went into episodic memory. The framework gave us no hook for that distinction, so we patched it at the tool layer.

## What this means for your retrieval pipeline

An agent that retrieves from a single vector store is almost certainly mixing memory types. A semantic query like "what is the architecture" comes back with episodic results, and an episodic query like "what happened in the last session" comes back with semantically similar events from weeks ago that have nothing to do with last night.

Splitting retrieval by memory type moved accuracy a long way for me. Semantic queries went to a knowledge base with relatively static embeddings, refreshed weekly. Episodic queries went to an event store with recency weighting, fetched by time range or session ID rather than embedding similarity.

None of that is a novel architecture. It mirrors how human memory works. You do not run the same cognitive process to recall a phone number that you run to recall what you ate yesterday.

## A practical implementation pattern

After testing several variations, here is the pattern I settled on.

Three separate storage systems sit behind a routing layer. The router inspects each piece of information before storing it and decides which system handles it.

Factual knowledge that the agent has confirmed: semantic store.
Task outcomes, user corrections, session events: episodic store.
Current working context, summaries of recent events: working memory, refreshed every turn.

My routing rules are far from perfect, and I still catch cross-contamination, like a learned API quirk landing in the episodic store because the user happened to phrase it as a complaint. Even so, the error surface shrinks dramatically against a single-store approach, and the failure modes get easier to debug.

## The failure signatures to watch for

Working memory that is too small shows up as the agent losing track of the current task mid-execution, abandoning step three of a five-step migration to re-ask what it was doing. That is the most common failure I see in agent demos. A better model rarely fixes it. A session summary prepended to the context every turn usually does.

Wrong episodic retrieval shows up as the agent contradicting itself across sessions. It claims it finished a task it never finished, or reports that a previous approach failed when that approach actually shipped. You are looking at a retrieval ranking problem here, never a storage problem.

Wrong semantic memory shows up as plausible, confident, incorrect information, the kind of answer that reads clean until you check the docs. The user catches it before the agent does. Updating the knowledge base fixes it. Touching the retrieval system does nothing.

Those three failure modes look nothing alike. Debugging with a single memory system, you cannot tell them apart, and that blindness is the real cost of the category error.

## Conclusion

These three memory types are no academic distinction. They carry different information, lean on different retrieval mechanisms, and break in different ways. An agent that files a learned fact the same way it files a past event will fail in predictable ways. An agent that routes information by type stays easier to debug and more reliable in production.

My earlier hierarchy post did not go far enough in pulling these types apart, which is why I wrote this one. The [state of AI agent memory in 2026](/blog/state-of-ai-agent-memory-2026/) covers the wider landscape. What I cared about here is the set of architectural decisions that determine whether your agent's memory actually works.
