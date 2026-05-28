---
title: "Contextual Compression for Agent Memory: What Stays and What Goes"
date: "2026-05-05"
slug: "contextual-compression-for-agent-memory"
description: "How agents decide what to keep in memory when context space is finite, and the three compression strategies that actually work."
tags: ["ai-agents", "agent-memory", "context-windows"]
status: published
---

The problem shows up around week three. Your agent has been running for a while, and the context window that once felt spacious is now half-filled with memory data. The agent starts missing things it knew two weeks ago. Or it starts losing track of what happened yesterday. Either way, something is broken in how the agent is managing memory over time.

I ran into this with a codebase navigation agent that I built last year. The agent needed to remember which files it had already analyzed, what it found in each, and which paths were dead ends. After about 200 interactions, the memory payload was eating 40% of the context window. The agent was spending more tokens on memory lookup than on actual work.

The core issue is that compression is not optional when context is finite. Something has to give.

<div class="visual-wrapper">
  <div class="visual-title">Contextual Compression Pipeline</div>
  <div class="visual-container">
    <iframe src="/static/visuals/context-compression.html" title="Token count before and after contextual compression" loading="lazy"></iframe>
  </div>
</div>

## Why Standard RAG Compression Does Not Work Here

If you have looked at RAG systems, you know that contextual compression is a solved problem in that space. You retrieve relevant chunks, then run a compressor to strip out the parts that do not answer the query. Simple and effective.

Agent memory compression is different. With RAG, you compress based on what a query needs right now. With agent memory, you compress based on what the agent will need in an unknown future situation. You are making a prediction about relevance across time and task context, not just across a single query. The [three memory types in AI agents](/blog/episodic-vs-semantic-vs-working-memory-agents/) have very different compression tolerances: episodic memory loses precision on details, semantic memory risks stale facts, and working memory cannot be compressed at all without breaking the current task.

This means the compression decision for agent memory has to factor in recency, frequency of use, and predicted future relevance. A memory that has been accessed ten times in the past week is more likely to matter than one accessed once three weeks ago. A memory about the user's primary project is more likely to matter than a memory about a one-off debugging session.

I wrote about the [memory hierarchy in AI systems](/blog/memory-hierarchy-in-ai-systems/) and how different memory types serve different purposes. The hierarchy is the theoretical foundation. What I am describing here is the compression layer that sits on top of it.

## The Three Approaches That Work

After testing several compression strategies, I found three that hold up in production.

### Summary-Based Compression

Store a generated summary of each memory item instead of the full content. When the agent needs the memory, it uses the summary and can optionally retrieve the full item on demand.

The math here depends on your summary length. A 512-token memory compressed to 64 tokens gives you an 8x storage gain. But the quality of the summary determines whether the compression is lossless or lossy. Poor summaries lose critical nuance.

I tested this with a customer support agent that needed to remember bug reports. The original memory items were 300-500 tokens each describing a bug and its resolution. Summarized to 50 tokens, the agent could still recognize the bug type but lost the specific steps to reproduce it. The agent could triage correctly but could not help with the exact reproduction steps. That is a real degradation in capability.

### Hierarchical Forgetting

Keep detailed memory for recent items and progressively abstract older items. Recent memory stays at full fidelity. Memory older than 7 days gets summarized. Memory older than 30 days gets reduced to key facts only.

This approach maps well to how [LLM context windows](/blog/llm-context-windows-explained/) actually work. Recent context is both more accessible and more relevant. Older context that has not been accessed recently is less likely to surface in relevant retrieval results.

The implementation requires a decay function. I used a simple exponential decay with a 30-day half-life for a task-tracking agent. After 30 days, a memory item is scored at 0.5 of its original relevance value. After 60 days, 0.25. This worked well for that use case but needed tuning for a research assistant where context from two months ago was still relevant.

### Relevance-Gated Retention

Only store memories that meet a minimum relevance threshold relative to the agent current goals. Everything else gets discarded.

This is the most aggressive approach and the hardest to get right. The relevance score needs to combine multiple signals: embedding similarity to current task context, frequency of past access, and explicit importance flags set by the agent when storing the memory.

The risk here is a feedback loop. If the relevance scoring function has a blind spot, the agent will systematically lose memories that do not fit the scoring pattern. I saw this happen in a support agent that kept losing memories about a specific class of issues because those issues did not match the dominant query patterns in the training data. The agent was performing worse on that class of issues over time, and the root cause was that relevant memories were being filtered out before they could be retrieved.

## The Structured Memory Approach

The approach I keep coming back to is designing memory for compression from the start, rather than compressing unstructured memory after the fact.

Instead of storing a long narrative about what the agent did in a session, I store atomic facts with timestamps and access counts. Each fact is independently meaningful and compresses cleanly.

A narrative memory might read: "The agent analyzed the authentication module and found that the token validation was using an outdated cryptographic library that had a known vulnerability."

A structured version: `{"type": "finding", "subject": "auth-token-validation", "status": "vulnerable", "library": "crypto-1.4.2", "severity": "high", "session_id": 142}`

The structured version is 256 bytes. The narrative is 180 tokens. When compressed, the structured version compresses to 80 bytes while preserving every fact. The narrative might compress to 60 tokens but you lose the specific library name and severity level in the process.

This is the approach I used in the memory serialization system I wrote about in [how agents persist state across sessions](/blog/memory-serialization-between-sessions/). Designing for compression from the start produces better results than trying to compress narrative memory after the fact.

## What I Would Do Differently

If I were starting fresh on an agent memory system today, I would implement three things from day one.

First, I would track access frequency per memory item, not just content and timestamp. Access frequency is the strongest signal for predicting future relevance. Memory that has been accessed repeatedly is far more likely to be accessed again than memory that has been sitting unused. The [short-term memory patterns](/blog/short-term-memory-for-ai-agents/) I described elsewhere address the in-session side of this, but the same access-frequency intuition applies when deciding what to promote from short-term to long-term storage.

Second, I would use a two-tier storage model. Hot storage holds the full-fidelity recent memories. Cold storage holds compressed summaries of older items. When the agent retrieves from cold storage, it gets the summary and can decide whether to decompress to full fidelity. This is similar to how CPU cache hierarchies work, and the analogy is apt because the problem is fundamentally the same: you have limited fast storage and need to decide what stays close.

Third, I would add a rare-event preservation rule. Memories that describe infrequent but high-impact events should be preserved at full fidelity regardless of access frequency. A one-off event that cost the user three hours of debugging time is worth remembering even if it only happened once.

## The Honest Tradeoff

No compression strategy is free. You are trading recall for capacity, and every strategy loses something. The [state of AI agent memory in 2026](/blog/state-of-ai-agent-memory-2026/) shows this trade-off playing out across the whole memory tooling ecosystem, with most production teams settling on tiered storage rather than a single compression policy.

Summary-based compression loses nuance. Hierarchical forgetting loses older detail. Relevance-gated retention loses coverage in low-signal areas. The right choice depends on what your agent can afford to forget.

For a codebase navigation agent, losing the exact steps to reproduce a rare bug is a real problem. For a research assistant, losing a specific file path you visited once is less critical. Know what your agent cannot afford to lose, and design your compression strategy around that constraint.

The best agent memory systems I have seen combine all three approaches in layers. They use summary compression as a baseline, hierarchical forgetting for temporal decay, and relevance gating to protect high-value memories from decay. No single strategy is sufficient. The combination is what makes it work.
