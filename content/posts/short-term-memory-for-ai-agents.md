---
title: "Short-Term Memory for AI Agents: A Practical Guide"
date: 2026-04-19
description: "Context windows are not memory. Here is what every production AI agent engineer needs to understand about token budgets, overflow handling, and how short-term and long-term memory actually work together."
tags: [ai, agents, memory, context-window, infrastructure]
status: published
---

Context windows are not memory. That is the first thing engineers get wrong when building AI agents. A context window is a fixed-size buffer. Memory is what you build on top of that buffer. Understanding the distinction will save you weeks of debugging flaky agents.

Every production AI agent I have shipped runs into the same failure mode eventually: it starts forgetting recent conversation turns, dropping critical instructions, or producing responses that ignore what the user just said. The root cause is almost always a misunderstanding of how short-term memory works inside the context window architecture.

<div class="visual-wrapper">
  <div class="visual-title">The Short-Term Memory Window</div>
  <div class="visual-container">
    <iframe src="/static/visuals/short-term-memory.html" title="Short-term memory window for AI agents" loading="lazy"></iframe>
  </div>
</div>

##What The Context Window Actually Is

The context window is a contiguous token buffer that feeds into the transformer's attention mechanism. When you send a 128k token context to Claude or GPT-4o, the model does not "remember" everything equally. Attention scores distribute across all tokens, but research has consistently shown that performance degrades for information placed in the middle of long contexts.

A context window has three properties you must track as an agent engineer. First, total capacity in tokens. GPT-4o supports 128k tokens. Claude 3.5 Sonnet supports 200k tokens. Gemini 1.5 Pro supports 1 million tokens. Second, current fill level, which is the sum of your system prompt, conversation history, retrieved documents, and scratchpad. Third, headroom, which is the remaining capacity for the next response and tool call arguments.

I track fill level programmatically in every agent I build. Here is the pattern:

```python
def estimate_tokens(text: str) -> int:
    """Rough token estimation. Use tiktoken for production."""
    return len(text) // 4  # rough approximation for English

def build_context_window(
    system_prompt: str,
    conversation_history: list[dict],
    retrieved_context: list[str],
    max_tokens: int = 128000,
    reserved_headroom: int = 2000
) -> list[dict]:
    """
    Construct a context window within token budget.
    
    Returns a list of message dicts that fit within the budget.
    """
    available = max_tokens - reserved_headroom
    
    messages = [{"role": "system", "content": system_prompt}]
    
    system_tokens = estimate_tokens(system_prompt)
    available -= system_tokens
    
    # Add conversation history in reverse (newest first)
    for msg in reversed(conversation_history):
        msg_tokens = estimate_tokens(msg["content"]) + 10  # overhead
        if available - msg_tokens < 0:
            break
        messages.insert(1, msg)
        available -= msg_tokens
    
    # Fill remaining with retrieved context
    for ctx in retrieved_context:
        ctx_tokens = estimate_tokens(ctx) + 10
        if available - ctx_tokens < 0:
            break
        messages.append({"role": "user", "content": ctx})
        available -= ctx_tokens
    
    return messages
```

This is a sliding window over your conversation history. It guarantees you never overflow the context window, but it has a brutal limitation: it discards the oldest messages indiscriminately. If a user asked something critical forty turns ago and you have been chatting about unrelated things since, that information is gone.

##Token Budgets And Overflow Handling

The overflow problem has three canonical solutions. The first is naive truncation, which is what most chatbot backends do. You cut the oldest messages until the context fits. This is simple to implement and destroys agent reliability in multi-turn conversations.

The second solution is a priority queue for messages. You score each message by recency, user importance, and semantic relevance to the current task. Then you fill the context window with the highest-scoring items. This requires a retriever or an embedding model to compute relevance scores, which adds latency and cost.

The third solution is summarization-based compression. You periodically summarize the conversation history into a condensed form that fits in fewer tokens. This preserves context across many turns but introduces summarization artifacts and latency. You also need a separate model or prompt to perform the summarization.

I use a combination for production agents. Recency gets the highest weight, but I also boost messages that match keywords in the current user query. Here is a scoring function I use:

```python
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime
    user_mentioned: bool = False

def score_message(msg: Message, current_time: datetime, query_keywords: list[str]) -> float:
    """
    Score a message for context window inclusion.
    
    Higher scores = more likely to be retained.
    """
    age_minutes = (current_time - msg.timestamp).total_seconds() / 60
    
    recency_score = max(0, 1 - (age_minutes / 1440))  # decay over 24 hours
    
    role_score = 0.5 if msg.role == "user" else 0.3 if msg.role == "assistant" else 0.1
    
    keyword_boost = 0.0
    content_lower = msg.content.lower()
    for kw in query_keywords:
        if kw.lower() in content_lower:
            keyword_boost += 0.2
    
    mention_boost = 0.3 if msg.user_mentioned else 0.0
    
    return (recency_score * 0.5) + (role_score * 0.2) + keyword_boost + mention_boost

def select_messages(
    messages: list[Message],
    current_time: datetime,
    query: str,
    max_tokens: int,
    token_estimator: callable
) -> list[Message]:
    """
    Select messages that fit within token budget using importance weighting.
    """
    query_keywords = query.split()[:10]  # simple keyword extraction
    
    scored = [(msg, score_message(msg, current_time, query_keywords)) for msg in messages]
    scored.sort(key=lambda x: x[1], reverse=True)
    
    selected = []
    current_tokens = 0
    
    for msg, score in scored:
        msg_tokens = token_estimator(msg.content) + 10
        if current_tokens + msg_tokens > max_tokens:
            continue
        selected.append(msg)
        current_tokens += msg_tokens
    
    selected.sort(key=lambda x: x.timestamp)  # chronological for context
    return selected
```

This gives you an importance-weighted buffer that adapts to the current conversation. It is not perfect, but it preserves critical messages better than pure recency.

##The Architecture Of Agent Memory Systems

A production agent memory system has three layers. The first layer is the context window, which is short-term memory. It holds the current conversation, active retrieved documents, and working scratchpad. Everything in this layer is "alive" for the current turn.

The second layer is episodic memory, which stores summaries of past interactions. When a user reconnects after a week, the agent should know who they are and what they were working on. Episodic memory is built by summarizing past conversation sessions and storing those summaries in a database.

The third layer is semantic memory, which is external knowledge retrieval. This is your RAG pipeline, your product documentation, your codebases. The agent retrieves relevant documents from this layer on each turn based on the current query.

I have written about [how Anthropic's contextual retrieval changes RAG architecture](/blog/how-anthropics-contextual-retrieval-changes-rag-architecture/) and about [RAG evaluation metrics that actually matter](/blog/rag-evaluation-metrics-what-actually-matters/). Both posts are relevant here because the retrieval quality in your semantic memory layer directly affects how much you need to rely on raw context window capacity.

The key insight is that these three layers are not separate systems. They are one memory hierarchy. Your context window is the top of that hierarchy. Semantic and episodic memory feed into it. When the context window is full, you evict from the bottom (old episodic memories) before you lose information from the top (current conversation).

##Designing Your Memory Architecture

Start with the token budget. Calculate the maximum tokens available for conversation history in your context window. Subtract your system prompt, your reserved headroom for responses, and any retrieved context you must include on every turn. What remains is your budget for conversation history.

Once you have that number, work backwards. If you have 32k tokens for conversation history and your average turn is 500 tokens, you can retain roughly 64 conversation turns. That sounds like a lot until you have a twenty-turn debugging session with a user and then need to reference something from turn five.

I track token usage per session in production. Every agent session gets a running tally of context window fill percentage, and I log warning events when fill exceeds 75 percent. That gives me data to tune the budget allocation over time.

The overflow strategy matters more than the raw budget size. An agent with a 32k context window and smart eviction will outperform an agent with 128k and naive truncation. The eviction strategy determines which information survives.

Your episodic memory layer should capture summaries of every session. I use a structured format:

```python
from dataclasses import asdict

@dataclass
class SessionSummary:
    session_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    topic: str
    key_outcomes: list[str]
    unresolved_issues: list[str]
    user_preferences: list[str]

def summarize_session(messages: list[dict]) -> SessionSummary:
    """
    Generate a session summary from message history.
    
    In production, use a separate LLM call to generate this.
    """
    return SessionSummary(
        session_id=generate_session_id(),
        user_id=messages[0].get("user_id", "unknown"),
        start_time=messages[0]["timestamp"],
        end_time=messages[-1]["timestamp"],
        topic=extract_topic(messages),
        key_outcomes=extract_outcomes(messages),
        unresolved_issues=extract_unresolved(messages),
        user_preferences=extract_preferences(messages)
    )
```

This summary goes into your episodic store. When the user starts a new session, you retrieve relevant past sessions and inject their summaries into the context window before the conversation begins.

##Common Failure Modes

The most common failure mode I see is context window exhaustion without warning. The agent receives a long prompt, consumes most of the context window, and then the next user message causes an overflow. The system either errors or silently truncates, and the user loses context.

The fix is to monitor fill level before every LLM call. If fill exceeds a threshold like 80 percent, trigger eviction or summarization before proceeding. Do not wait for the overflow to happen.

The second failure mode is semantic retrieval that conflicts with recent conversation context. The user says "use the new API endpoint instead" and the agent retrieves documents about the old endpoint because the retrieved context is based on keywords, not conversation state. The agent then ignores the user's instruction and follows the old documentation.

You can address this by prepending recent conversation turns to your retrieval query. The retrieval query becomes "previous instruction: use new API endpoint instead, plus user query: how do I authenticate" instead of just the authentication query.

The third failure mode is summarization degradation. After multiple summarization rounds, the conversation history becomes a sequence of increasingly abstracted summaries. Specific details get dropped. The agent loses track of exact values, names, or decisions made in earlier turns.

Track the number of summarization passes each message has undergone. After two or three passes, consider freezing the original message into the episodic store rather than continuing to compress it.

##Relationship To Long-term Memory

Short-term and long-term memory are not competing systems. They are a hierarchy. The context window is the working table. Semantic and episodic stores are the filing cabinets. You pull relevant files from the cabinets onto the table, work with them there, and file updated versions back when the session ends.

The mistake is treating long-term memory as optional or secondary. If your agent only has access to the context window, it has no memory of previous sessions, no knowledge of the user's past preferences, and no ability to retrieve relevant documentation beyond what fits in the current context.

I have written about [token counting and cost control](/blog/token-counting-isnt-optional-a-practical-guide-to-llm-cost-control/) and [prompt caching and when the math works](/blog/prompt-caching-what-it-is-and-when-the-math-works/). Both are relevant here because the memory architecture you design has direct cost implications. Every retrieval call, every summarization pass, and every context window refill costs money.

The pattern I follow: maximize context window efficiency first, then build episodic memory as a reliability layer, then invest in semantic retrieval quality. This sequence gives you the best return on engineering effort.

Context window management is not a solved problem. The approaches in this post represent current practice, but the field is moving fast. The architectures that work in 2026 will look primitive by 2028. Build for replaceability, not permanence.



##Related Articles

- [Context windows vs memory](/blog/context-windows-vs-memory/)
- [AI memory management for LLMs](/blog/ai-memory-management-for-llms/)
- [How memory works in HyperAgents](/blog/how-memory-works-in-hyperagents/)
- [State of AI agent memory 2026](/blog/state-of-ai-agent-memory-2026/)

##Faq

**How do I calculate context window fill in real time?**

Use a tokenizer matching your model. For OpenAI models, use `tiktoken`. For Claude, use the Anthropic tokenizer SDK. Track the cumulative token count of your system prompt, conversation history, and retrieved context before every API call. If you are within 80 percent of the limit, trigger eviction or summarization.

**What is the best overflow strategy for production agents?**

Use importance-weighted eviction over simple truncation. Score each message by recency, role (user messages score higher), and keyword relevance to the current query. Fill the context window with the highest-scoring messages. Summarize older messages periodically and store summaries in episodic memory.

**Should I use summarization or retrieval for long conversations?**

Both. Summarization compresses the conversation history itself. Retrieval adds external knowledge. Use retrieval to pull in relevant documents from your semantic store. Use summarization to compress conversation history that cannot be retrieved but is still relevant. The combination outperforms either approach alone.

**How does episodic memory differ from semantic memory?**

Episodic memory stores summaries of past interactions with a specific user or session. It answers "what did we do in previous sessions?" Semantic memory stores structured knowledge about the world, your product, or your domain. It answers "what is this thing and how does it work?" Both feed into the context window, but they serve different purposes.

**When should I flush episodic memory to disk versus keeping it in the context window?**

Keep recent episodic content (sessions from the last 7 days) in the context window on session start. Archive older sessions to a database or vector store. You do not need every past session in context for every query. Retrieve the most relevant ones based on the current topic or user profile.

**How do I handle context window overflow with tool calls?**

Tool call arguments consume context window space. Reserve a portion of your token budget for tool arguments (typically 1k-2k tokens). If you are approaching the limit, pause tool use, evict low-priority messages, then continue. Long tool call chains can exhaust context faster than equivalent conversation turns because arguments tend to be verbose.

**What models should I target for context window efficiency?**

Any model with at least 128k context window capacity gives you enough room to implement meaningful eviction strategies. Models with smaller windows (8k-32k) force you into aggressive compression that degrades conversation quality. I recommend targeting models with 128k+ windows for production agents with complex memory requirements.