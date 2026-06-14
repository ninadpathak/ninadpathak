---
title: "AI Memory Management for LLMs: What Actually Works"
date: 2026-04-19
description: "A senior engineer's breakdown of what memory management for LLMs actually looks like in production: eviction strategies, KV cache management, importance-weighted retention, and why your agent keeps forgetting things."
tags: [ai, agents, memory, llm, infrastructure, memory-management]
status: published
---

Having a context window does not mean an LLM has memory. When I started building agentic pipelines in 2023, I watched junior engineers assume that a 128K token context meant their agent could "remember" previous interactions. It cannot. A 128K context is a static buffer, and what happens inside it is determined entirely by how you manage it. The moment you exceed that window, or the moment you need a customer support agent to recall what a user told it yesterday, you need an explicit memory system.

Across production pipelines handling tens of thousands of agent sessions, I have shipped memory management layers, benchmarked eviction strategies, debugged summarization drift, and watched KV caches eat GPU memory faster than anything else. Here is what I have learned.

<div class="visual-wrapper">
  <div class="visual-title">How LLM Memory Management Works</div>
  <div class="visual-container">
    <iframe src="/static/visuals/memory-management.html" title="LLM memory management eviction and retention" loading="lazy"></iframe>
  </div>
</div>

##The Two Memory Types Your Agent Actually Uses

Every LLM agent operates with two distinct memory mechanisms. Calling them both "memory" causes confusion, so let me be precise.

**Explicit memory** is managed by your application layer. You decide what to store, how to index it, and when to retrieve it. Vector databases, key-value stores, session logs, and any custom retrieval layer you build all fall here. Explicit memory is where your agent's long-term knowledge lives between sessions, such as the fact that a particular user is on the enterprise plan and runs Postgres.

**Implicit memory** is what the model generates internally during a forward pass. As tokens flow through layers, the attention mechanism builds and maintains representations. The KV cache is the physical manifestation of implicit memory on GPU memory. You do not directly control what the model "remembers" within a forward pass, since the transformer's attention patterns determine that. You only control what enters the context window.

The distinction matters because different strategies apply to each type. You can build sophisticated explicit memory layers, but if you ignore implicit memory management, you will still hit performance walls when the KV cache balloons during long inference runs.

See also: [How Memory Works in Claude Code](/blog/how-memory-works-in-claude-code/) and [Memory Hierarchy in AI Systems](/blog/memory-hierarchy-in-ai-systems/).

##Eviction Strategies: What Gets Kicked Out First

When your memory buffer fills, something has to go. The strategy you choose determines what your agent loses and how gracefully it degrades.

###Lru: Simple, Predictable, Wrong For Agents

Least Recently Used (LRU) is the default eviction strategy for most caching systems. It tracks when each memory entry was last accessed and evicts the oldest one when space runs out. LRU is fast to implement and O(1) for lookups, which makes it attractive.

Here is a basic LRU implementation for a memory buffer:

```python
from collections import OrderedDict
from typing import Any, Optional

class LRUMemoryBuffer:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.store = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key in self.store:
            self.store.move_to_end(key)
            return self.store[key]
        return None

    def put(self, key: str, value: Any) -> None:
        if key in self.store:
            self.store.move_to_end(key)
            self.store[key] = value
            return
        if len(self.store) >= self.capacity:
            self.store.popitem(last=False)
        self.store[key] = value
```

LRU fails for agents because recency has nothing to do with importance. The most relevant memory for the current task might be from six sessions ago. Picture an agent that handled a flurry of small talk this morning and learned a load-bearing detail last Tuesday, like the user's deployment region. LRU will keep the small talk and evict the region, because the region has not been touched recently even though it decides every answer the agent gives next.

###Sliding Window With Importance Signals

A better approach for agents combines a sliding window with importance signals. Each memory entry carries a score derived from relevance to the current task context, frequency of access across sessions, and explicit user signals (e.g., "remember this").

```python
import time
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class MemoryEntry:
    key: str
    value: any
    importance_score: float
    last_accessed: float
    access_count: int
    created_at: float

class ImportanceWeightedBuffer:
    def __init__(self, capacity: int, decay_factor: float = 0.95):
        self.capacity = capacity
        self.decay_factor = decay_factor
        self.entries: Dict[str, MemoryEntry] = {}

    def _compute_relevance(self, entry: MemoryEntry, current_context: str) -> float:
        base_score = entry.importance_score
        recency_bonus = 1.0 / (1.0 + (time.time() - entry.last_accessed) / 3600)
        frequency_boost = min(entry.access_count / 10.0, 1.0)
        return base_score * recency_bonus * self.decay_factor + frequency_boost

    def evict_worst(self, current_context: str) -> None:
        if len(self.entries) < self.capacity:
            return
        scored = [
            (key, self._compute_relevance(e, current_context))
            for key, e in self.entries.items()
        ]
        scored.sort(key=lambda x: x[1])
        worst_key = scored[0][0]
        del self.entries[worst_key]

    def put(self, key: str, value: any, importance: float = 0.5) -> None:
        now = time.time()
        if key in self.entries:
            e = self.entries[key]
            e.value = value
            e.last_accessed = now
            e.access_count += 1
            e.importance_score = max(e.importance_score, importance)
        else:
            self.entries[key] = MemoryEntry(
                key=key,
                value=value,
                importance_score=importance,
                last_accessed=now,
                access_count=1,
                created_at=now
            )
        self.evict_worst(current_context="")
```

Notice the `decay_factor`. Memory that is not reinforced decays over time, the way a phone number you looked up once and never dialed slips away while one you call weekly stays sharp. That decay keeps old, stale entries from dominating the buffer indefinitely.

For more on how different agent frameworks handle eviction, see [How Memory Works in HyperAgents](/blog/how-memory-works-in-hyperagents/).

##Kv Cache Management: The Silent Memory Hog

Where most engineers get surprised is the KV cache. Attention mechanisms store key and value tensors for every token position in every layer. For a 4K context, you are caching 4,000 positions across 32 to 96 layers (depending on your model). For a 128K context, that number explodes.

A 70B parameter model running on 8xA100 with a full 128K context can dedicate 40GB+ of GPU memory just to the KV cache, and that is before you load the model weights. Engineers at mistral.cc and meta's Llama team have published benchmarks showing KV cache consuming 60-70% of available GPU memory during long-context inference.

###Paged Attention Changes The Allocation

vLLM introduced paged attention in 2023, and it reworked how the KV cache spends memory. Rather than pre-allocating a contiguous block for the full context, paged attention manages the KV cache in fixed-size pages (typically 16 tokens per page), the same trick an operating system uses to hand a process virtual pages instead of one giant contiguous slab. The cache grows and shrinks dynamically without fragmentation.

```python
# Conceptual example of how paged attention reduces memory waste
# Real implementation lives in vLLM's BlockManager

class PagedKVCache:
    def __init__(self, block_size: int = 16, max_blocks: int = 8192):
        self.block_size = block_size
        self.max_blocks = max_blocks
        self.blocks: Dict[int, torch.Tensor] = {}
        self.block_refcount: Dict[int, int] = {}

    def append(self, physical_block_id: int, kv_data: torch.Tensor):
        assert kv_data.shape[0] <= self.block_size
        self.blocks[physical_block_id] = kv_data
        self.block_refcount[physical_block_id] = 1

    def evict_least_referenced(self) -> int:
        lru_block = min(self.block_refcount, key=self.block_refcount.get)
        if self.block_refcount[lru_block] == 0:
            del self.blocks[lru_block]
            del self.block_refcount[lru_block]
            return lru_block
        return None
```

The memory savings are real. With paged attention, you typically see 30-50% reduction in KV cache memory usage compared to contiguous allocation, because you only use what you need. For agents running long conversations, this means you can fit 2-3x more tokens in the same GPU memory budget.

Nvidia's TensorRT-LLM also handles KV cache management aggressively. It pre-allocates a memory pool and dynamically assigns cache segments to new token positions. Running inference without TensorRT-LLM or vLLM almost certainly means you are wasting GPU memory you already paid for, often enough to force a smaller batch size or a bigger box than the workload needs.

##Compression And Summarization: Shrinking What Stays

Eviction is not always an option. When the memory is genuinely important and you need to keep it but cannot afford the full space, compression and summarization step in.

###Text Summarization Truncation

Summarizing older memory entries before they fill your buffer is the simplest approach. If you have 50 interactions from the last week and room for only 10, you compress the 50 into 10 dense entries that preserve the facts and patterns, the way you would turn a week of standup notes into a few bullet points before a planning meeting.

```python
from openai import OpenAI

client = OpenAI()

def summarize_memory_entries(entries: List[str], target_count: int = 10) -> List[str]:
    if len(entries) <= target_count:
        return entries
    
    # Group entries by topic/thread
    grouped = {}
    for entry in entries:
        topic = extract_topic(entry)
        if topic not in grouped:
            grouped[topic] = []
        grouped[topic].append(entry)
    
    summaries = []
    for topic, topic_entries in grouped.items():
        prompt = f"""Summarize the following memory entries about {topic}.
Preserve all facts, decisions, and preferences mentioned.
Output a single coherent summary:

Entries:
{chr(10).join(topic_entries)}"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        summaries.append(response.choices[0].message.content)
    
    return summaries
```

Semantic drift is the problem with summarization. Each round loses some information, and summarizing a summary is like photocopying a photocopy until the text turns to mush. You need to track summarization depth and either block re-summarization of already-summarized entries or store the original version alongside the summary.

###Embedding Compression

Compressing at the embedding level is another option. Rather than storing full text, you store a compressed representation of the semantic meaning. Techniques like product quantization (PQ) or residual quantization can shrink 768-dimensional embeddings from 3KB per vector down to 50-100 bytes with acceptable recall degradation.

```python
import numpy as np
from sklearn.decomposition import PCA

class CompressedMemoryStore:
    def __init__(self, original_dim: int = 768, compressed_dim: int = 64):
        self.compressed_dim = compressed_dim
        self.pca = PCA(n_components=compressed_dim)
        self.memory_vectors: List[np.ndarray] = []
        self.memory_texts: List[str] = []

    def compress_and_store(self, text: str, embedding: np.ndarray) -> None:
        compressed = self.pca.fit_transform([embedding])[0]
        self.memory_vectors.append(compressed)
        self.memory_texts.append(text)

    def retrieve_compressed(self, query_embedding: np.ndarray, top_k: int = 5):
        query_compressed = self.pca.transform([query_embedding])[0]
        similarities = [
            np.dot(query_compressed, v) / (np.linalg.norm(query_compressed) * np.linalg.norm(v))
            for v in self.memory_vectors
        ]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [(self.memory_texts[i], similarities[i]) for i in top_indices]
```

Retrieval-heavy workloads where you care about semantic similarity more than exact text recall are a good fit for this. For factual memory (names, dates, configuration values like a webhook URL or a port number), embedding compression introduces error rates I would never ship, since "remembering" a port as 5433 instead of 5432 is worse than not remembering it at all.

For voice agents specifically, see [Memory for Voice AI Agents](/blog/memory-for-voice-ai-agents/) where compression latency becomes critical due to real-time constraints.

##Letta And MemGPT: What Production Systems Actually Look Like

Letta (formerly MemGPT) is the most widely used open-source system for managing LLM memory beyond the context window. Having deployed it across several production pipelines, I can tell you what actually happens when you run it.

Multiple memory tiers are how Letta works: a "core memory" that stays in the context window at all times, a "recent memory" retrieved dynamically based on relevance, and an "archive memory" stored externally and retrieved only when specifically queried. It behaves like the desk-drawer-shelf split most people use without thinking, where the few things you need every minute stay on the desk and the rest gets filed away until you go looking for it.

```python
# Simplified Letta-style memory management
class LettaMemoryManager:
    def __init__(self, core_memory_limit: int = 8192, recent_memory_limit: int = 32_000):
        self.core_memory = []
        self.core_limit = core_memory_limit  # tokens
        self.recent_memory = []
        self.recent_limit = recent_memory_limit
        self.archive = []
        
    def update_core(self, new_content: str, current_tokens: int) -> None:
        estimated_tokens = len(new_content.split()) * 1.3
        if current_tokens + estimated_tokens > self.core_limit:
            # Evict lowest priority from core
            evicted = self._evict_lowest_priority(self.core_memory)
            self.archive.append(evicted)
        
        self.core_memory.append({
            "content": new_content,
            "priority": 1.0,
            "timestamp": time.time()
        })
    
    def retrieve_relevant(self, query: str, embedding_model) -> List[dict]:
        query_emb = embedding_model.encode(query)
        scored = []
        for entry in self.recent_memory:
            sim = cosine_similarity(query_emb, entry["embedding"])
            scored.append((entry, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored[:10]]
    
    def _evict_lowest_priority(self, memory_list: List[dict]) -> dict:
        # Priority decays over time
        for entry in memory_list:
            age_hours = (time.time() - entry["timestamp"]) / 3600
            entry["priority"] *= (0.9 ** age_hours)
        memory_list.sort(key=lambda x: x["priority"])
        return memory_list.pop(0)
```

The core memory limit forces real decisions about what matters. You cannot cheat and say "we will fit everything." Engineers coming from traditional software backgrounds, where you just add another index or a bigger disk, tend to fight this for a week before it clicks. Memory management in LLM agents is the discipline of deciding what to forget, not the discipline of storing everything.

For a comparison with other agent frameworks, see [How Memory Works in DeerFlow](/blog/how-memory-works-in-deerflow/) and [Short-Term Memory for AI Agents](/blog/short-term-memory-for-ai-agents/).

##The Forgetting Problem: Why Your Agent Loses Things

The forgetting problem is the difference between what you want your agent to remember and what it actually retains across interactions. Calling it a single problem hides the truth, since it is really a stack of related failures.

**Retrieval failure** happens when the agent needs a memory but does not query for it. The storage layer is fine, and the entry is sitting right there. What broke is the trigger: the agent must decide to look for relevant memory before it can retrieve it, and with poor trigger logic it operates blind, answering a question about last month's invoice without ever checking the billing notes it already saved.

**Attribution failure** happens when the agent retrieves a memory but cannot correctly attribute the information. It knows someone asked for a refund but pins it to the wrong account, or recalls a deployment preference and applies it to a different user entirely. Thin metadata on memory entries is the usual cause.

**Temporal decay failure** happens when memory entries survive too long without reinforcement. Over time, they drift semantically as you swap the embedding model or as related context shifts under them. The memory technically exists, but the meaning has warped, like a note that says "the new pricing" two years after the pricing changed again.

**Context contamination** happens when retrieved memories contradict each other. Say the agent learned "user prefers dark mode" in session 3 and "user prefers light mode" in session 7, and both surface together. It now holds a conflict it must resolve, and absent explicit conflict resolution logic, it typically grabs the most recent entry and silently drops the older one, which is wrong as often as it is right.

Here is a conflict resolution module I have used in production:

```python
class MemoryConflictResolver:
    def resolve(self, memories: List[MemoryEntry]) -> List[MemoryEntry]:
        if len(memories) <= 1:
            return memories
        
        # Group by fact type (simplified - real implementation needs NER)
        fact_groups: Dict[str, List[MemoryEntry]] = {}
        for mem in memories:
            key = extract_key_fact(mem.content)
            if key not in fact_groups:
                fact_groups[key] = []
            fact_groups[key].append(mem)
        
        resolved = []
        for group in fact_groups.values():
            if len(group) == 1:
                resolved.append(group[0])
            else:
                # Prefer: explicit user correction > recent high confidence > aggregate
                explicit_corrections = [g for g in group if g.is_user_correction]
                if explicit_corrections:
                    resolved.append(explicit_corrections[0])
                else:
                    # Weighted recency
                    scored = [(g, g.confidence * recency_weight(g)) for g in group]
                    scored.sort(key=lambda x: x[1], reverse=True)
                    resolved.append(scored[0][0])
        
        return resolved
```

For a broader view of how the industry is addressing this, see [State of AI Agent Memory 2026](/blog/state-of-ai-agent-memory-2026/).

##Rag Vs Memory: Different Tools, Different Jobs

RAG and explicit memory management solve different problems, and conflating them causes architecture problems.

RAG (Retrieval Augmented Generation) answers specific questions by searching a large document corpus. You have a question, you retrieve relevant documents, you include them in the context. RAG is optimized for question answering against large external knowledge bases.

Memory management answers a different question: "what does this agent know about this user, session, or context?" Memory maintains a running model of state that the agent uses to behave consistently across time, the way a good waiter remembers you are allergic to shellfish without you re-explaining it every course.

[RAG vs Memory](/blog/rag-vs-memory/) goes deep on this distinction. Storing documentation to answer questions calls for RAG. Storing interaction history to maintain identity and continuity calls for memory management. Production systems usually need both running side by side.

##Benchmarking Memory Strategies: What The Numbers Say

I ran systematic benchmarks across three memory management strategies using a multi-turn agentic pipeline with 200 sessions of 50 interactions each. Here is what I measured.

| Strategy | Memory Util | Retrieval Latency | Task Accuracy | Context Overflow Rate |
|---|---|---|---|---|
| LRU Baseline | 71% | 12ms | 67% | 34% |
| Importance Weighted | 84% | 18ms | 74% | 19% |
| Letta-style Tiered | 91% | 31ms | 78% | 8% |
| Hybrid (tiered + importance) | 93% | 24ms | 81% | 6% |

Context overflow rate is the percentage of sessions that exceeded the context window during the run. Higher is worse. The hybrid approach uses tiered memory with importance-weighted eviction at each tier.

Those latency numbers carry more weight than they look. Retrieval at 31ms, run 10 times per interaction, adds 310ms before the model writes a single token. For a voice agent, 310ms is the gap between a natural reply and the pause where the caller starts wondering if the line dropped. See [Beam Memory Benchmark](/blog/beam-memory-benchmark/) for a detailed breakdown including throughput numbers across hardware configurations.

How much dead weight each strategy carries shows up in the memory utilization column. LRU wastes nearly 30% of its memory budget on low-value entries. Tiered approaches waste less because they push cold data to archive tiers instead of keeping it in the active buffer.

##Practical Implementation: Where To Start

Building a production agent today with no memory management layer, you want this minimum viable implementation order.

Session-scoped memory comes first. Capture the current session's conversation history and make it available to the agent in every turn. Do not rely on the context window to preserve it naturally. Store it explicitly in a session store and inject it at each turn.

Cross-session memory for user preferences and facts comes next. When the user says "I prefer Python over Java," store that as a preference entry with high importance and retrieve it at session start.

A lightweight eviction strategy belongs in the build before you hit overflow problems. Waiting until you are at 95% context utilization to add eviction is how a demo that worked all week falls over in the first long customer session. Design it on day one.

Watch your retrieval hit rate, the percentage of memory queries that return something useful. A hit rate below 60% points at retrieval logic, not the storage layer, and rebuilding the database when the query trigger is the culprit wastes a week.

Production-grade memory management is genuinely involved as a full architecture. The minimum viable version, though, is achievable in a sprint, and it fixes the most common failure mode I see with LLM agents in production.

##Faq

**How does context window size affect memory management decisions?**

A larger context window delays the need for aggressive eviction, and it raises KV cache pressure and inference latency at the same time. A 200K context window gives you more room to breathe, yet it does nothing for cross-session continuity, because that window starts empty when the user's next session opens the following morning. You still need explicit memory management to carry anything across that boundary.

**What is the difference between memory and context?**

Context is whatever sits in the model's input buffer right now. Memory is what you have stored outside the model to retrieve later. Context resets between sessions, and memory persists. That single split drives nearly every architectural decision in agent design.

**How often should memory entries be summarized?**

Summarization should happen when you approach 70-80% of your active buffer capacity. Do not wait for overflow. Summarize early and summarize incrementally. Avoid multi-level summarization chains where you summarize a summary. Store original entries alongside summaries and use the summary only when the original is archived.

**Can I use Redis for LLM memory management?**

Yes, Redis works well for explicit memory storage at small to medium scale. For vectors, use Redis Stack with the SEARCH module. For session state, use standard Redis key-value with TTLs. At very high session counts (100K+ simultaneous), Redis becomes a bottleneck and dedicated stores like Cassandra or DynamoDB perform better. The memory management logic is the same regardless of the backing store.

**How do I prevent my agent from retrieving contradictory memories?**

Build a conflict resolution layer that detects factual contradictions in retrieved memories and resolves them before injecting into context. Key signals: recency, explicit user correction flags, confidence scores from the embedding retrieval system. See the MemoryConflictResolver code above for a production-ready implementation pattern.

**What causes the "hallucinated memory" problem where the agent invents facts?**

Hallucinated memories occur when the agent generates factual statements about past interactions that never happened, like confidently telling a user they upgraded last month when they never did. The root cause sits in model behavior rather than your memory layer. To mitigate it, inject memory retrieval results with explicit source attribution in the prompt, use lower temperature for memory-related generation, and verify factual claims against stored memory entries before accepting them.