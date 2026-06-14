---
title: "Short-Term Memory for AI Agents: A Practical Guide"
date: 2026-04-19
description: "Context windows are not memory. Here is what every production AI agent engineer needs to understand about token budgets, overflow handling, and how short-term and long-term memory actually work together."
tags: [ai, agents, memory, context-window, infrastructure]
status: published
---

Context windows are not memory, and that is the first thing engineers get wrong when building AI agents. A context window is a fixed-size buffer. Memory is what you build on top of that buffer, the way a desk surface is not the same thing as a filing system even though both hold paper. Understanding the distinction will save you weeks of debugging flaky agents.

Every production AI agent I have shipped runs into the same failure mode eventually. It starts forgetting recent conversation turns, dropping a critical instruction the user gave ten messages back, or answering as if the last thing the user typed never happened. Almost always the cause traces back to a misunderstanding of how short-term memory works inside the context window architecture.

<div class="visual-wrapper">
  <div class="visual-title">The Short-Term Memory Window</div>
  <div class="visual-container">
    <iframe src="/static/visuals/short-term-memory.html" title="Short-term memory window for AI agents" loading="lazy"></iframe>
  </div>
</div>

##What The Context Window Actually Is

The context window is a contiguous token buffer that feeds into the transformer's attention mechanism. Send a 128k token context to Claude or GPT-4o and the model does not "remember" everything equally. Attention scores distribute across all tokens, and research has consistently shown that performance degrades for information placed in the middle of long contexts. I have watched an agent flawlessly cite a config value from the very top of a 90k-token prompt and then completely miss a constraint buried around token 50,000.

Three properties of a context window need tracking as an agent engineer. There is total capacity in tokens: GPT-4o supports 128k tokens, Claude 3.5 Sonnet supports 200k tokens, Gemini 1.5 Pro supports 1 million tokens. There is current fill level, the sum of your system prompt, conversation history, retrieved documents, and scratchpad. And there is headroom, the remaining capacity for the next response and tool call arguments.

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

A sliding window over your conversation history is what that code implements. It guarantees you never overflow the context window, and it carries a brutal limitation: it discards the oldest messages indiscriminately. Say a user told you "the production database is the read replica, never write to it" forty turns ago, and the chat has wandered through unrelated questions since. That instruction is gone, and the agent has no idea it ever existed.

##Token Budgets And Overflow Handling

Three canonical solutions exist for the overflow problem. Naive truncation comes first, the approach most chatbot backends reach for. You cut the oldest messages until the context fits. Cheap to implement, and it quietly destroys agent reliability in multi-turn conversations.

A priority queue for messages is the second option. You score each message by recency, user importance, and semantic relevance to the current task, then fill the context window with the highest-scoring items. Computing those relevance scores means running a retriever or an embedding model, which adds latency and cost on every turn.

Summarization-based compression is the third. You periodically fold the conversation history into a condensed form that fits in fewer tokens, which preserves context across many turns at the price of summarization artifacts and extra latency. A separate model or prompt has to do the summarizing.

For production agents I use a combination. Recency gets the highest weight, and I also boost messages that match keywords in the current user query, so that a turn where the user said "always deploy to staging first" resurfaces the moment they ask about deployment again. Here is a scoring function I use:

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

What you get is an importance-weighted buffer that adapts to the current conversation. It is not perfect, and it preserves critical messages far better than pure recency does.

##The Architecture Of Agent Memory Systems

A production agent memory system has three layers. The context window sits at the first layer as short-term memory. It holds the current conversation, active retrieved documents, and working scratchpad. Everything in this layer is "alive" for the current turn.

Episodic memory forms the second layer, storing summaries of past interactions. When a user reconnects after a week, the agent should know who they are and what they were working on, the way a good account manager glances at last quarter's notes before a call. You build episodic memory by summarizing past conversation sessions and storing those summaries in a database.

Semantic memory makes up the third layer, the external knowledge retrieval side: your RAG pipeline, your product documentation, your codebases. The agent retrieves relevant documents from this layer on each turn based on the current query.

I have written about [how Anthropic's contextual retrieval changes RAG architecture](/blog/how-anthropics-contextual-retrieval-changes-rag-architecture/) and about [RAG evaluation metrics that actually matter](/blog/rag-evaluation-metrics-what-actually-matters/). Both posts are relevant here because the retrieval quality in your semantic memory layer directly affects how much you need to rely on raw context window capacity.

Treating these three layers as separate systems is the mistake. They are one memory hierarchy. Your context window is the top of it, and semantic and episodic memory feed into it from below. When the context window fills up, you evict from the bottom (old episodic memories) before you lose information from the top (the current conversation).

##Designing Your Memory Architecture

Start with the token budget. Calculate the maximum tokens available for conversation history in your context window. Subtract your system prompt, your reserved headroom for responses, and any retrieved context you must include on every turn. What remains is your budget for conversation history.

Once you have that number, work backwards. With 32k tokens for conversation history and an average turn of 500 tokens, you can retain roughly 64 conversation turns. That sounds generous right up until a twenty-turn debugging session where the agent needs the exact stack trace the user pasted back at turn five.

Token usage per session is something I track in production. Every agent session gets a running tally of context window fill percentage, and I log a warning event when fill crosses 75 percent. That stream of data is what lets me tune the budget allocation over time.

Raw budget size matters less than the overflow strategy. An agent with a 32k context window and smart eviction will outperform an agent with 128k and naive truncation. Which information survives comes down entirely to the eviction strategy.

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

That summary goes into your episodic store. When the user starts a new session, you retrieve the relevant past sessions and inject their summaries into the context window before the conversation begins, so the agent opens already knowing the user prefers TypeScript examples and left a migration half-finished last Thursday.

##Common Failure Modes

Context window exhaustion without warning is the failure mode I see most. The agent receives a long prompt, consumes most of the context window, and the next user message tips it into overflow. The system either throws an error or silently truncates, and the user loses context mid-task with no explanation.

Monitoring fill level before every LLM call is the fix. Once fill crosses a threshold like 80 percent, trigger eviction or summarization before proceeding rather than waiting for the overflow to land.

Semantic retrieval that conflicts with recent conversation context is the second one. The user says "use the new v2 API endpoint instead," and the retriever, matching on keywords rather than conversation state, pulls back the docs for the deprecated v1 endpoint. The agent dutifully ignores the user's instruction and follows the old documentation.

Prepending recent conversation turns to your retrieval query addresses this. The query sent to the retriever becomes "previous instruction: use new v2 API endpoint instead, plus user query: how do I authenticate" rather than the bare authentication question, so conversation state steers the retrieval.

Summarization degradation is the third failure mode. After several summarization rounds, the conversation history turns into a sequence of increasingly abstracted summaries. Specific details drop out. The agent loses the exact port number, the customer's name, or the decision the user locked in six turns ago, because each pass smooths another detail away.

Track the number of summarization passes each message has been through. Once a message has survived two or three passes, freeze the original into the episodic store rather than compressing it again, the same way you would photocopy a fading receipt before it becomes illegible.

##Relationship To Long-term Memory

Short-term and long-term memory are not competing systems. They form a hierarchy. The context window is the working table, and the semantic and episodic stores are the filing cabinets. You pull the relevant files from the cabinets onto the table, work with them there, and file the updated versions back when the session ends.

Treating long-term memory as optional or secondary is the mistake. Give your agent nothing but the context window and it has no memory of previous sessions, no knowledge that this user always wants metric units, and no way to retrieve documentation beyond what already fits in the current context.

I have written about [token counting and cost control](/blog/token-counting-isnt-optional-a-practical-guide-to-llm-cost-control/) and [prompt caching and when the math works](/blog/prompt-caching-what-it-is-and-when-the-math-works/). Both are relevant here because the memory architecture you design carries direct cost implications. Every retrieval call, every summarization pass, and every context window refill bills against your account.

My own ordering goes like this. Maximize context window efficiency first, then build episodic memory as a reliability layer, then invest in semantic retrieval quality. Following that sequence gives you the best return on engineering effort, because each step removes the failure that would otherwise dominate the next.

Context window management is not a solved problem. The approaches in this post reflect current practice, and the field is moving fast. The architectures that work in 2026 will look primitive by 2028. Build for replaceability, not permanence.



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