---
title: "Contextual Compression for Agent Memory: What Stays and What Goes"
date: "2026-05-05"
slug: "contextual-compression-for-agent-memory"
description: "How agents decide what to keep in memory when context space is finite, and the three compression strategies that actually work."
tags: ["ai-agents", "agent-memory", "context-windows"]
status: published
---

Around week three, the problem shows up. After running long enough, the context window that once felt spacious has filled halfway with memory data, and the agent starts missing things it knew two weeks ago, or it loses track of what happened yesterday. Either way, something has broken in how the agent manages memory over time.

I ran into this with a codebase navigation agent I built last year. The agent needed to remember which files it had already analyzed, what it found in each, and which paths were dead ends. After about 200 interactions, the memory payload was eating 40% of the context window, and the agent spent more tokens looking up memory than doing the analysis I had asked for.

Compression stops being optional once context is finite. Something has to give.

<div class="visual-wrapper">
  <div class="visual-title">Contextual Compression Pipeline</div>
  <div class="visual-container">
    <iframe src="/static/visuals/context-compression.html" title="Token count before and after contextual compression" loading="lazy"></iframe>
  </div>
</div>

## Why Standard RAG Compression Does Not Work Here

Anyone who has built a RAG system knows contextual compression is close to solved in that setting. You retrieve the relevant chunks, then run a compressor that strips out the parts that do not answer the query. Simple and effective.

Agent memory compression works on a harder question. RAG lets you compress against what a query needs right now. Agent memory forces you to compress against what the agent will need in some future situation you cannot see yet, so you are predicting relevance across time and shifting task context, never just a single query. The [three memory types in AI agents](/blog/episodic-vs-semantic-vs-working-memory-agents/) tolerate that compression very differently. Episodic memory loses precision on details, semantic memory risks going stale, and working memory cannot be compressed at all without breaking the task in progress.

Recency, frequency of use, and predicted future relevance all have to feed into the compression decision. A memory accessed ten times in the past week is far more likely to matter than one touched once three weeks ago. Knowledge about the user's primary project earns its space in a way that a memory about a one-off debugging session for a side repo does not.

Different memory types serve different purposes, which I covered in the [memory hierarchy in AI systems](/blog/memory-hierarchy-in-ai-systems/). That hierarchy is the foundation. The compression layer I am describing here sits on top of it and decides how much of each tier survives.

## The Three Approaches That Work

After testing several compression strategies, I found three that hold up in production.

### Summary-Based Compression

Store a generated summary of each memory item instead of the full content. When the agent needs the memory, it uses the summary and can optionally retrieve the full item on demand.

Your savings track summary length directly. Squeezing a 512-token memory down to 64 tokens buys you an 8x storage gain, though the quality of that summary decides whether the compression is lossless or lossy. A sloppy summary drops the one detail you needed later.

I tested this with a customer support agent that had to remember bug reports. The original memory items ran 300 to 500 tokens each, describing a bug and its resolution. Summarized to 50 tokens, the agent still recognized the bug type but lost the specific steps to reproduce it. It could route a ticket to the right queue and never walk an engineer through the repro. That is a real degradation in capability, the kind you only notice when a user asks the follow-up question the summary cannot answer.

### Hierarchical Forgetting

Keep detailed memory for recent items and progressively abstract older items. Recent memory stays at full fidelity. Memory older than 7 days gets summarized. Memory older than 30 days gets reduced to key facts only.

Mapping cleanly onto how [LLM context windows](/blog/llm-context-windows-explained/) actually behave, this approach treats recent context as both more accessible and more relevant. Older context that nobody has touched recently rarely surfaces in retrieval results anyway, so abstracting it costs little.

A decay function drives the whole thing. For a task-tracking agent I used a simple exponential decay with a 30-day half-life, so a memory item scores 0.5 of its original relevance after 30 days and 0.25 after 60. That fit the task tracker, where last month's tickets really were dead weight. It needed retuning for a research assistant, where a paper I read two months ago still shaped the questions I was asking today.

### Relevance-Gated Retention

Only store memories that meet a minimum relevance threshold relative to the agent current goals. Everything else gets discarded.

Of the three, this is the most aggressive and the one I find hardest to tune. The relevance score has to fuse several signals: embedding similarity to the current task, how often the memory was accessed before, and explicit importance flags the agent set when it first stored the item.

A feedback loop is the danger. Any blind spot in the scoring function means the agent quietly drops every memory that falls outside the pattern the scorer favors. I watched this in a support agent that kept discarding memories about one class of issue, billing-related edge cases, because those tickets did not look like the dominant query patterns the scorer had learned. The agent got worse at that class month over month, and the cause traced back to relevant memories being filtered out before retrieval ever had a chance at them.

## The Structured Memory Approach

The approach I keep coming back to is designing memory for compression from the start, rather than compressing unstructured memory after the fact.

Instead of storing a long narrative about what the agent did in a session, I store atomic facts with timestamps and access counts. Each fact is independently meaningful and compresses cleanly.

A narrative memory might read: "The agent analyzed the authentication module and found that the token validation was using an outdated cryptographic library that had a known vulnerability."

A structured version: `{"type": "finding", "subject": "auth-token-validation", "status": "vulnerable", "library": "crypto-1.4.2", "severity": "high", "session_id": 142}`

The structured version is 256 bytes, the narrative is 180 tokens. Compressed, the structured record shrinks to 80 bytes and keeps every field. The narrative might compress to 60 tokens, and somewhere in that squeeze the specific library name and the severity level fall out, which are exactly the two facts you would reach for during an incident.

That structured design is what I used in the memory serialization system I wrote about in [how agents persist state across sessions](/blog/memory-serialization-between-sessions/). Building for compression from the start beats bolting a compressor onto narrative memory after it already exists.

## What I Would Do Differently

If I were starting fresh on an agent memory system today, I would implement three things from day one.

Tracking access frequency per memory item comes first, alongside content and timestamp rather than instead of them. Access frequency is the strongest signal I have for predicting future relevance, since a memory the agent keeps pulling up will almost certainly get pulled up again, where one sitting untouched for weeks usually stays untouched. The [short-term memory patterns](/blog/short-term-memory-for-ai-agents/) I described elsewhere handle the in-session side, and the same access-frequency intuition decides what gets promoted from short-term into long-term storage.

A two-tier storage model comes second. Hot storage holds full-fidelity recent memories, cold storage holds compressed summaries of older items, and a retrieval against cold storage returns the summary first so the agent can choose whether to decompress to full fidelity. Picture how a CPU cache hierarchy works: a small, fast L1 close to the core and a larger, slower main memory behind it, with the hardware constantly deciding which lines deserve the fast tier. Agent memory faces the identical squeeze, limited fast storage and a need to decide what stays close.

A rare-event preservation rule comes third. Memories that capture infrequent but high-impact events should stay at full fidelity no matter how rarely they are accessed. A one-off failure that cost the user three hours of debugging is worth keeping verbatim, because access frequency alone would happily forget it.

## The Honest Tradeoff

No compression strategy is free. You trade recall for capacity, and each one drops something on the way. The [state of AI agent memory in 2026](/blog/state-of-ai-agent-memory-2026/) shows that trade-off playing out across the memory tooling ecosystem, where most production teams I have seen settle on tiered storage rather than committing to one compression policy.

Summary-based compression sheds nuance, hierarchical forgetting sheds older detail, relevance-gated retention sheds coverage in the quiet corners of the input space. Your right choice depends on what your agent can afford to forget.

A codebase navigation agent that loses the exact steps to reproduce a rare crash has a real problem on its hands. A research assistant that forgets a file path it opened once is barely inconvenienced. Decide what your agent cannot afford to lose, then build the compression strategy around that one constraint.

The best agent memory systems I have seen layer all three approaches together. Summary compression runs as the baseline, hierarchical forgetting handles temporal decay, and relevance gating shields the high-value memories that decay would otherwise erode. No single strategy carries the load on its own. The combination is what holds up once the agent has been running for months.
