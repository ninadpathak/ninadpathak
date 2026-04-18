---
title: "Memory Hierarchy in AI Systems: From Sensory to Semantic"
date: 2026-04-19
description: "How layered memory architecture helps AI systems achieve long-term context, personalization, and continuous learning — and why flat memory fails."
tags: [ai, agents, memory, cognitive-architecture, infrastructure]
status: published
---

Human brains do not store every experience equally. They layer it: sensory input gets filtered into working memory, some of that gets compressed into long-term storage, and the rest evaporates. This is not a bug in human cognition. It is the feature that makes it scalable. AI systems work the same way, and the teams that understand this build agents that actually remember things. The teams that treat memory as a flat document store end up with systems that forget the moment context runs out.

I have implemented layered memory architectures in three different agent systems over the past two years. The difference between a flat memory approach and a hierarchical one is the difference between an agent that degrades over a long session and one that stays sharp. The Atkinson-Shiffrin model from 1968 maps almost perfectly onto what modern AI memory systems are building, and that is not a coincidence.

## The Atkinson-Shiffrin model and its AI mapping

Richard Atkinson and Richard Shiffrin proposed a three-system memory model in 1968: the sensory register, the short-term store, and the long-term store. Fifty years later, AI architects are building the same architecture without having read the paper. The sensory register becomes the input buffer. The short-term store becomes working context. The long-term store becomes persistent memory across sessions.

Here is how that mapping actually works in a production AI system.

```
Sensory Register  ->  Input buffer (audio/text/raw features)
Short-Term Store ->  Working context (current context window)
Long-Term Memory ->  Persistent store (vector DB, KG, function store)
```

The key insight is that each layer has different retention characteristics. Sensory memory holds raw input for milliseconds. Short-term memory holds curated content for seconds to minutes. Long-term memory holds compressed representations for days to years. You need all three layers, and they need to interact through explicit policies, not through a single flat store.

## Layer 1: Sensory memory — the input buffer

Sensory memory in AI systems is the raw input layer. For a voice agent, this is the audio stream before ASR transcription. For a text agent, this is the raw token sequence before any processing. For a multimodal agent, this might be video frames or sensor readings.

The retention time at this layer is effectively zero for practical purposes. The buffer exists only to feed into the next layer. What matters here is what gets selected for promotion to short-term memory. This is where Voice Activity Detection lives for voice agents, and where relevance filtering lives for text agents.

The mistake engineers make is trying to store too much at this layer. You cannot retain the full raw audio stream for a two-hour conversation. The cost would be astronomical and the retrieval value would be near zero. Instead, you summarize and compress at this boundary.

## Layer 2: Short-term memory — working context

Short-term memory in AI is the context window. It holds what the model is currently reasoning about. In a transformer, this is the full token sequence that gets attention computed across. In an agent, this also includes the working variables, retrieved documents, and intermediate outputs from tool calls.

The capacity of short-term memory is your context window size. For GPT-4o, that is 128K tokens. For Claude 3.5 Sonnet, that is 200K tokens. For Gemini 1.5 Pro, that is 1 million tokens. The numbers keep growing, but the fundamental problem does not change: you cannot fit everything you want to remember into this window.

The selection policy for what gets kept in short-term memory is where the engineering gets interesting. Most systems use recency as the primary signal. Newer content stays, older content gets evicted. But recency is a poor proxy for importance. A message from three turns ago that established a user preference is more important than a message from ten turns ago about an unrelated topic.

Importance-weighted eviction performs significantly better than recency-only. Here is the pattern I use in production.

```python
from dataclasses import dataclass
from typing import List

@dataclass
class MemoryItem:
    content: str
    importance: float
    timestamp: float
    access_count: int = 0

def importance_score(item: MemoryItem, current_time: float) -> float:
    recency = 1.0 / (1.0 + (current_time - item.timestamp) / 300)
    importance = item.importance
    access = min(item.access_count / 10.0, 1.0)
    return 0.5 * importance + 0.3 * recency + 0.2 * access

def select_for_context_window(
    items: List[MemoryItem],
    budget: int
) -> List[MemoryItem]:
    current_time = items[0].timestamp if items else 0
    scored = [(importance_score(item, current_time), item) for item in items]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:budget]]
```

The important thing is that short-term memory is volatile. When the context window resets or the session ends, working context disappears unless you explicitly promote selected items to long-term memory.

## Layer 3: Episodic memory — what happened

Episodic memory stores particular events or interactions. In an AI system, this maps to session logs, conversation transcripts, and event sequences. The defining characteristic is that episodic memory is indexed by time and context, not by semantic similarity.

When a user asks "what did we discuss about the API design last Tuesday?", that is an episodic retrieval problem. The system needs to find the session from last Tuesday and extract the relevant portion. Vector similarity search on a flat embedding store is a poor fit for this. You need time-based indexing with semantic filtering on top.

The implementation I use stores session summaries with timestamps and topic tags. Individual turns get embedded and stored with a session ID foreign key. Retrieval first narrows by time range and topic, then does semantic similarity within that subset.

```python
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('episodic_memory.db')
cur = conn.cursor()

# Store a session summary
cur.execute("""
    INSERT INTO sessions (project, summary, topic_tags, started_at)
    VALUES (?, ?, ?, ?)
""", ('my-project', 'Discussed API versioning strategy...', 'api,design,v1', datetime.now()))

# Retrieve sessions by time range and topic
def get_relevant_sessions(project: str, topic: str, days_back: int = 7):
    cutoff = datetime.now() - timedelta(days=days_back)
    cur.execute("""
        SELECT summary, started_at FROM sessions
        WHERE project = ?
          AND topic_tags LIKE ?
          AND started_at > ?
        ORDER BY started_at DESC
    """, (project, f'%{topic}%', cutoff))
    return cur.fetchall()
```

Episodic memory is what most teams mean when they say "conversation history." But conversation history is only useful when it can be retrieved efficiently. Storing it is not the hard part. Retrieving the right episode at the right time is.

## Layer 4: Semantic memory — what is known

Semantic memory stores facts, concepts, and world knowledge separate from the specific episodes where they were learned. In AI systems, this maps to the trained model weights, the retrieved knowledge base, and the persistent facts that persist across sessions.

The key property of semantic memory is that it survives session boundaries and can be updated without retraining. When Claude Code remembers that your project uses Python 3.12 and pytest, that is semantic memory. When it remembers the specific conversation where you decided to upgrade from Python 3.9, that is episodic memory.

The failure mode for semantic memory is staleness. Facts change. When your team switches from pytest to unittest, the semantic memory entry that says "uses pytest" is now wrong. Detecting and correcting staleness is an unsolved problem in production memory systems.

## Layer 5: Procedural memory — how to do things

Procedural memory stores skills and learned behaviors. In AI systems, this maps to system prompts, tool definitions, agent loop configurations, and the behavioral patterns encoded through fine-tuning or RLHF.

This is the most overlooked memory layer in AI agent design. When you write a system prompt that tells an agent how to behave, you are writing to procedural memory. When you define a tool schema, you are adding to procedural memory. When you configure the retry logic for API calls, that is procedural memory too.

The important insight is that procedural memory is the most stable layer. It does not change within a session. It changes through explicit editing of prompts and tool definitions. This is also where the most consequential errors live. A flawed system prompt affects every interaction.

## Why hierarchy beats flat memory

The argument for a flat memory store is simplicity. One vector database, one retrieval step, done. The problem is that flat memory treats a user's name from two weeks ago the same way it treats the current conversation turn. It treats a factual claim about your product pricing the same way it treats a transient hypothesis from the current session.

Flat memory fails at scale for three reasons. First, retrieval noise grows with the store size. As you add more documents, semantic similarity search returns more false positives. Second, importance signals are lost. A message about a user preference is scored the same as a message about an intermediate tool result. Third, staleness compounds. Old facts accumulate faster than they can be pruned, and retrieval increasingly surfaces outdated information.

Hierarchical memory addresses all three. Importance is assessed at each layer transition. Staleness is handled by eviction from short-term and compression into long-term rather than by raw deletion. Retrieval is scoped to the relevant layer, so a query about user preferences searches episodic memory, not the entire history.

## Implementation patterns from production systems

Letta implements a paged memory system inspired by operating system virtual memory. Memory gets swapped in and out of the context window based on relevance scoring. The architecture is clean and the codebase is worth studying, but the production operational burden is high.

MemGPT takes a different approach, treating memory as a managed external store with explicit summary and retrieval steps. The self-managed memory loop is clever, but the inconsistency in production is real. I have seen the memory system discard critical context mid-session because the summary threshold was crossed at an awkward moment.

The pattern I have converged on uses tiered summarization with importance-gated promotion. Items start in short-term memory. Every N turns, an importance score is computed. Items above a threshold get promoted to episodic memory as compressed summaries. Items below the threshold get discarded.

Here is the core of the promotion logic.

```python
from dataclasses import dataclass

@dataclass
class MemoryItem:
    content: str
    importance: float
    turns_old: int
    access_count: int

def should_promote_to_episodic(item: MemoryItem) -> bool:
    # Must be important AND accessed recently OR very old
    importance_gate = item.importance > 0.6
    recency_gate = item.access_count >= 2 or item.turns_old >= 5
    return importance_gate and recency_gate

def compress_for_episodic(item: MemoryItem) -> str:
    # Summarize to 2-3 sentences
    return f"[{item.turns_old} turns ago]: {item.content[:100]}..."
```

The compression is rough but the selectivity is high. Only genuinely important items survive. The episodic store stays small enough that retrieval is fast, and the summaries preserve enough context to be useful.

## FAQ

**Why not just use a large context window instead of a memory hierarchy?**

Context windows have a fixed capacity and a retrieval accuracy curve that degrades in the middle of long contexts. The BEAM benchmark shows this clearly. A 1 million token context window does not give you 1 million tokens of useful memory. It gives you about 200K tokens of usable context at high accuracy, with the rest being noise. Explicit memory systems that manage what gets stored and how it gets retrieved outperform brute-force context at scale.

**How do you handle memory conflicts?**

Memory conflicts happen when new information contradicts old information. The approach I use is last-write-wins for factual claims, with explicit conflict flags for high-stakes contradictions. If a user says their name is Alice today and Bob yesterday, the system records both with timestamps and surfaces the recency to the agent for resolution.

**What about privacy and memory?**

Memory systems that persist user data across sessions introduce privacy considerations that flat context does not. The key is segmentation. User-specific memory should be stored with user isolation at the storage layer, not just at the application layer. I use project-scoped episodic stores where each project has its own database file. A project for work conversations never shares memory with a project for personal conversations.

**How does this differ from RAG?**

RAG is a retrieval mechanism for external knowledge. Memory hierarchy is an architecture for maintaining agent state across sessions. RAG answers the question "what does the model know?" Memory hierarchy answers "what does the agent remember?" They are complementary. RAG feeds external knowledge into the working context layer. Memory hierarchy manages everything the agent has experienced.

**What is the biggest failure mode in layered memory systems?**

Staleness is the biggest failure mode. Memory systems that do not prune aggressively accumulate outdated information faster than they retrieve useful information. The fix is aggressive compression at the short-term to long-term boundary and explicit staleness thresholds that trigger deletion, not just compression.
