---
title: "Short-Term Memory for AI Agents: What It Is, Why It Matters, and How to Implement It"
date: 2026-04-19
description: "A practical guide to understanding and implementing short-term memory for AI agents in 2026 — from context windows to sliding buffers to importance-weighted systems."
tags: [ai, agents, memory, infrastructure, context-window]
status: published
---

I have been thinking about why so many AI agent demos feel hollow. You have seen them. A chatbot that remembers your name for three messages and then forgets. An agent that solves a multi-step problem beautifully in step four and then re-explains step one as if it has never seen it before. The issue is not the model. The issue is short-term memory, and most developers are getting it wrong.

Human short-term memory holds roughly seven items for about thirty seconds. AI agent short-term memory is nothing like that. It is a conversation window that costs money, degrades in quality as it fills up, and has to be explicitly managed. When I design an agent now, I treat the context window as the most precious resource in the system, and I am going to show you how to do the same.

## The Context Window Is Not Memory, It Is a Canvas

Let me be precise about terminology because the confusion here causes real architectural problems. The context window is not memory. It is a fixed-size input buffer that you load with information. The model reads it, reasons over it, and produces an output. Nothing in the context window persists unless you explicitly persist it and re-load it on the next turn.

When you send a 128,000-token context to GPT-4.5 or Gemini 3 Pro, the model processes all of it. Performance does not stay flat across the full window. Research from 2026 shows that effective performance degrades well before the advertised maximum context length. A model advertised at 1 million tokens might reliably perform complex reasoning only within the first 400,000 tokens, with sharp quality drops in the middle region. This is what the field calls the "lost in the middle" problem and it matters enormously when you design your memory buffers.

The distinction that matters is this: the context window is your agent's immediate workspace. Short-term memory is how you populate and manage that workspace across turns. Long-term memory is where you store what you want the agent to remember beyond the current session. These are three different systems, and conflating them is where most agent architectures break down.

## How Short-Term Memory Differs From Working Memory and Episodic Memory

The cognitive science terms get borrowed constantly and imprecisely. Here is how I think about them as an engineer building production systems.

**Working memory** is what the model uses at inference time to hold intermediate reasoning steps. When a chain-of-thought model produces a scratchpad of 2,000 tokens, that is working memory in the cognitive sense. You generally do not manage this directly. The model does it internally through attention patterns, though you can influence it with prompting.

**Short-term memory** in an AI agent is the conversation history plus any auxiliary information you deliberately include in the context window for the current session. It is bounded by your token budget. It is explicit, engineer-controlled, and per-session by default. When the session ends, short-term memory is gone unless you explicitly save something to a persistent store.

**Episodic memory** is a specific implementation pattern where you log significant events, actions, and outcomes from past sessions. Think of it as a structured journal of what happened. Mem0 and similar frameworks implement something like episodic memory when they extract entities, facts, and interaction histories and store them in a retrievable format.

Human short-term memory is associative, fuzzy, and automatic. AI short-term memory is precise, bounded, and entirely manual. Every token you want in the context window, you have to decide to put there. That is a fundamentally different mental model and it changes how you build.

## The Context Window as Short-Term Memory: Token Budgets and Pressure

Your context window has a hard ceiling. Every token you spend on old conversation history is a token you cannot spend on new context, retrieved documents, tool definitions, or system prompts. This is the fundamental tension of short-term memory management.

Consider a concrete scenario. You are running a customer support agent with a 128,000-token context window. Your system prompt takes 2,000 tokens. You have 15 tools, each averaging 500 tokens in definition. That is 9,500 tokens committed before the conversation even starts. A typical user message might be 200 tokens, and your response 300 tokens. After 100 turns of conversation, you have consumed 50,000 tokens just in history. You now have 66,500 tokens of headroom for retrieved context, but you are paying for all 128,000 tokens on every single API call.

This is the token budget pressure that does not show up in demos but shows up immediately in production cost bills. The math is brutal. A 100-turn conversation at average costs is not 100 times the cost of a 1-turn conversation. It is 100 times the cost of the full context window per turn. Your short-term memory strategy directly determines your cost per conversation.

Gemini 3 Pro advertises 10 million tokens. Claude Opus 4 offers 200,000 tokens. GPT-4.5 turbo sits at 128,000 tokens. These numbers look large until you do the math on a 500-message conversation with tool outputs, retrieved documents, and intermediate reasoning traces. Large context windows reduce the frequency of overflow problems. They do not eliminate the need for a memory management strategy.

## Implementation Approaches: Sliding Window vs Importance-Weighted Buffer

There are two dominant patterns for managing short-term memory in production systems, and the right choice depends on your use case.

### Sliding Window

A sliding window keeps the N most recent tokens or the M most recent messages in the context. Everything older than that gets discarded. This is simple, predictable, and works well when the recent past matters more than the distant past.

The naive version drops messages entirely when they fall out of the window. A more sophisticated version keeps the most recent 3 to 5 turns in full detail and compresses everything before that into a summary. This "sliding window with compression" is what most production conversational agents use.

Here is what a basic sliding window buffer looks like in Python.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Message:
    role: str
    content: str
    tokens: int

class SlidingWindowBuffer:
    def __init__(self, max_tokens: int, max_messages: Optional[int] = None):
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.messages: list[Message] = []

    def add(self, role: str, content: str, tokens: int):
        self.messages.append(Message(role, role, content, tokens))
        self._prune()

    def _prune(self):
        # Remove oldest messages until we fit within token budget
        while (
            sum(m.tokens for m in self.messages) > self.max_tokens
            or (self.max_messages and len(self.messages) > self.max_messages)
        ) and self.messages:
            self.messages.pop(0)

    def build_context(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages]
```

This implementation discards oldest messages first. For a customer support agent, that is probably fine. For a coding agent where a definition from message 3 matters at message 50, you need something smarter.

### Importance-Weighted Buffer

The sliding window treats all messages as equal. An importance-weighted buffer ranks messages by relevance and evicts the lowest-ranked ones first. Relevance can be determined by recency, by semantic similarity to the current query, by explicit user signal, or by a model-generated importance score.

The architecture looks like this. You maintain a priority queue of messages with associated importance scores. When the token budget fills, you evict the lowest-scoring message. Scores are updated on each turn using a lightweight relevance check against the current conversation state.

```python
import heapq
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ScoredMessage:
    importance: float
    timestamp: float
    message: Message
    # Tiebreaker for heapq: negate timestamp so newest has higher priority
    seq: int = 0
    def __lt__(self, other):
        if self.importance == other.importance:
            return self.timestamp > other.timestamp
        return self.importance < other.importance

class ImportanceWeightedBuffer:
    def __init__(self, max_tokens: int, max_messages: int = 200):
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.heap: list[ScoredMessage] = []
        self.seq = 0
        self.total_tokens = 0

    def _score_message(self, msg: Message, current_turn: int) -> float:
        # Higher score = more important
        recency_score = 1.0 / (1 + (current_turn - msg.turn_number))
        length_penalty = msg.tokens / 512  # penalize very long messages
        return recency_score - (0.1 * length_penalty)

    def add(self, role: str, content: str, tokens: int, turn_number: int):
        msg = Message(role, content, tokens, turn_number)
        importance = self._score_message(msg, turn_number)
        entry = ScoredMessage(importance, turn_number, msg, self.seq)
        self.seq += 1
        heapq.heappush(self.heap, entry)
        self.total_tokens += tokens
        self._prune()

    def _prune(self):
        while (
            self.total_tokens > self.max_tokens
            or len(self.heap) > self.max_messages
        ):
            evicted = heapq.heappop(self.heap)
            self.total_tokens -= evicted.message.tokens

    def build_context(self) -> list[dict]:
        # Return messages sorted by importance (highest first)
        sorted_msgs = sorted(self.heap, key=lambda x: -x.importance)
        return [
            {"role": m.message.role, "content": m.message.content}
            for m in sorted_msgs
        ]
```

The importance-weighted approach sounds better in theory. In practice, it is more expensive to compute scores, harder to debug, and the scoring function is application-specific. I have seen it work beautifully for research agents where early context is critical. I have seen it fail catastrophically when the scoring function drifts from real user needs.

## When Short-Term Memory Overflows and How to Handle It

Overflow happens when your conversation history exceeds your token budget. There are three ways to handle it, and the right answer is usually a combination.

**Truncation** is the default. You cut off the oldest messages until you fit. This is what happens when you do nothing and rely on the API provider's default behavior. It works until it does not, and then you lose critical context silently.

**Summarization** compresses old history into a dense summary before it falls out of the window. You run an LLM call to distill a 5,000-token conversation into 200 tokens of key facts, decisions, and outstanding questions. This preserves the semantic gist while dramatically reducing token cost. The implementation usually triggers when you hit 70 to 80 percent of your token budget, not when you are completely full. You want headroom to fit the summary itself.

**Offloading** moves older context entirely out of the context window and into an external store. This could be a vector database, a key-value store, or a graph database. When you need something from the offloaded context, you retrieve it and load it back into the context window for specific turns. This is the foundation of RAG-augmented agents and it is the approach that scales best for long-running systems.

The practical overflow strategy I use looks like this. At 60 percent of budget, run a summary pass on the oldest 40 percent of messages. At 85 percent of budget, offload everything below the most recent 20 percent to a vector store. At 95 percent, keep only the most recent 15 percent and retrieve the rest on demand. These thresholds are not magic numbers. They are what works for agents running 50 to 200 turns per session, which covers most production use cases I encounter.

## The Relationship Between Short-Term and Long-Term Memory

Short-term memory and long-term memory are not competitors. They are a pipeline.

Short-term memory handles the immediate context. It lives in your context window and costs you money on every API call. Long-term memory lives in an external store and gets retrieved when relevant. The question is not which one to use. It is how to move information between them intelligently.

When a user tells you their name, their preference, or a constraint they care about, that information starts in short-term memory. If it matters for future sessions, you extract it and write it to long-term memory. On the next session, you retrieve it from long-term memory and load it into short-term memory as part of your system prompt or initial context.

This is exactly what Mem0 does with its user memory layer. It extracts facts from conversations and persists them. When the next session starts, those facts are available as retrieved context. Letta (formerly MemGPT) takes a different approach. It lets the model decide when to page information between a main context (analogous to RAM) and an archival store (analogous to disk). The model is explicitly instructed to move relevant facts in and out of the context window via function calls.

The architecture I prefer for production agents has three layers. The most recent 10 to 20 turns live in the context window as raw messages. Everything older gets summarized and stored in a vector database with a timestamp. User facts, preferences, and key decisions get written to a structured store (graph or key-value) as structured records. On each new turn, I retrieve from all three layers and merge the results into the context.

## Best Practices for Managing Short-Term Memory in Production

After building and shipping several agents that handle long conversations, here is what I have learned.

Keep your system prompt separate from conversation history. System prompts do not get consumed by history. A 3,000-token system prompt is a fixed cost on every call. Budget accordingly.

Use structured formats inside the context window. XML tags or JSON objects with fields for source, timestamp, and confidence make it easier for the model to distinguish between a recent user message and a retrieved fact from three sessions ago. This matters more as context grows.

Measure actual token usage, not message count. A 10-word user message that includes a 1,000-token retrieved document is not a short message. Profile your real context distributions before setting your buffer sizes.

Implement overflow handling before you need it. Waiting until you have a production incident to figure out your summarization strategy means your users experience the incident. Build the tiered overflow system (summarize at 60 percent, offload at 85 percent) from day one.

Test with long conversations. A 10-turn demo tells you nothing about how your memory system behaves at turn 500. Push your agent to 200 turns in staging and look at what falls out of the context window and when.

Budget for memory operations in your cost model. Summarization calls, retrieval calls, and embedding generation are all API costs. A well-managed memory system can increase your cost per conversation by 15 to 30 percent. That needs to be intentional, not accidental.

## The Visual: What Is Actually Happening in the Context Window

I have built a three.js visualization that shows a rolling context window in action. You can see tokens entering from one side, accumulating in the context buffer, and older tokens being pushed out as new ones arrive. The visualization uses a dark orange palette and shows the sliding window mechanics clearly.

You can open `/tmp/short-term-memory.html` in any browser to interact with it. Use your mouse to orbit around the 3D box and watch how the buffer fills, overflows, and resets.

## FAQ

**What is the difference between context window and short-term memory?**

The context window is the physical input buffer of the model, defined by its architecture. Short-term memory is the engineering layer that manages what goes into that buffer. You can think of the context window as RAM and short-term memory as the memory management system that decides what to load into RAM.

**How many tokens should I keep in short-term memory?**

The answer depends on your context window size, the model's effective performance range, and your cost constraints. For most models in 2026, keeping the most recent 50,000 to 80,000 tokens of conversation history is the practical sweet spot. Beyond that, retrieval quality degrades and cost per turn becomes significant.

**Do I need long-term memory for every agent?**

If the agent handles single-turn tasks and has no need to remember anything across sessions, long-term memory is unnecessary complexity. If the agent works on multi-session tasks, remembers user preferences, or builds on prior work, long-term memory is not optional. It is the difference between a stateless tool and a persistent agent.

**What causes context degradation in long conversations?**

Context degradation has several causes. The model assigns more attention weight to recent tokens, making older tokens less influential. Irrelevant history pollutes the context with noise. Very long contexts increase the chance that the model will attend to the wrong information. Summarization and retrieval-based context management are the primary mitigations.

**Is a larger context window always better?**

Not necessarily. Larger context windows increase cost per API call, and research shows that model performance on complex reasoning often degrades well before the advertised maximum context length. The goal is the right amount of relevant context, not maximum context. This is what context engineering as a discipline is built around.

**How does Mem0 compare to building custom short-term memory?**

Mem0 automates the extraction, storage, and retrieval of user facts and conversation summaries. Building custom gives you full control over every decision. For most production applications, starting with Mem0 or a similar framework and customizing as needed is faster and more reliable than building from scratch. For specific high-value differentiation, custom memory logic justified by concrete requirements beats framework defaults.

---

If you found this useful, you might also be interested in my post on [building reliable AI agents with structured output](/blog/production-ai-agent-errors/) or my guide to [context engineering in production](/blog/llm-context-windows-explained/). The fundamental constraint in both of those is the same one we have been discussing here: the context window is finite, and what you put in it is everything.
