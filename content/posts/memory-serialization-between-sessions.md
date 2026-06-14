---
title: "Memory Serialization: How Agents Persist State Across Sessions"
date: "2026-04-30"
slug: "memory-serialization-between-sessions"
description: "Why agents forget everything on restart, and the serialization patterns that actually solve it"
tags: ["ai-agents", "agent-memory", "agent-architecture"]
status: published
---

The first time I deployed an agent to production, I watched it handle 200 conversations perfectly. Then I restarted the service for a routine deployment at 2 AM. The next morning the agent greeted the same users as if it had never seen them, asking one person their timezone for the second time after they had spelled it out the day before. No memory of preferences they had confirmed. No record of issues already resolved. Back to zero.

Burned by that, I learned the rule that governs agent memory: a session that cannot be serialized will not survive a restart. The whole conversation you just had, the facts you established, the reasoning you built across dozens of turns, all of it lives only in the context window of a running process. Kill that process and you have nothing left to greet anyone with.

Serialization is the problem underneath all of it, and it fights back harder than a first pass suggests.

<div class="visual-wrapper">
  <div class="visual-title">SERIALIZE / RESTART / RESTORE</div>
  <div class="visual-container">
    <iframe src="/static/visuals/memory-serialization.html" title="An agent serializing state to a store at session end and restoring it on restart, versus forgetting everything without serialization" loading="lazy"></iframe>
  </div>
</div>

## The Three Approaches Engineers Actually Use

Three real patterns have shown up across the production systems I have worked on. Each one solves the problem and bills you in a different currency.

**Full state serialization** means dumping the entire conversation history plus the system prompt into a structured format on disk. JSON works. So does msgpack if you want speed. The agent restarts, reads the file, and gets its full context back.

Completeness is what you buy here. Nothing gets lost. The cost lands in latency and tokens. A six-month support thread, say a customer who has filed eleven tickets and changed plans twice, becomes enormous. You cannot fit that into a context window, or if you can, you pay to re-process it on every restart. Re-processing a 500-message history added roughly 3 seconds of latency in my measurements, on a Claude Sonnet call with a 200k context window.

Cheaper than that is **conversation log storage**, where you write every message to a database as it happens. On restart, you retrieve the recent messages and hand the agent the raw log. Plenty of teams I have watched reach for this first, usually a Postgres table with a row per message and a session id.

Reconstruction from a raw log is where it gets imprecise. The agent still has to work out what matters, what to act on first, what to ignore. A short conversation reconstructs fine. For a months-long relationship with a user, the agent burns a real slice of its tokens figuring out where things stand before it can help with anything. It is like asking someone to resume a project by handing them the full email thread and saying "you were on this," instead of a one-line status.

**Selective serialization** is the pattern I recommend once you know your agent well enough. You define a state schema that captures what actually matters. User preferences, confirmed facts, current task status, unresolved issues. The agent updates this schema as it goes.

```python
# A minimal serialization schema for a research agent
{
    "user_preferences": {
        "communication_style": "concise",
        "timezone": "America/New_York"
    },
    "confirmed_facts": [
        {"fact": "user is working on a RAG pipeline",
         "confirmed_at": "2026-04-28T14:22:00Z"},
        {"fact": "user prefers pgvector over Pinecone",
         "confirmed_at": "2026-04-29T09:15:00Z"}
    ],
    "active_task": {
        "description": "benchmark hybrid search accuracy",
        "status": "in_progress",
        "last_action": "ran evaluation script, results pending"
    }
}
```

What you pay upfront is design work. Knowing what your agent needs to remember has to come before you can define the schema, which usually means running the agent in the messy way first and watching what it keeps relearning. The resulting state, though, is small, fast to load, and semantically meaningful. A 200-message support thread that compresses into a 2KB state object loads in a few milliseconds and tells the agent exactly where it stood.

## When Serialization Fails in Practice

Schema mismatch is the failure mode I run into most often in production. You designed your serialization schema six months ago, then the agent grew. You added new capabilities, maybe a field for tracking which integrations the user connected. The new code writes state using keys that did not exist in the original schema, so old sessions deserialize with those keys missing. The agent does not crash. It quietly behaves as if certain facts were never established, like greeting a long-time user who once confirmed they were on the enterprise plan as a brand-new free-tier signup.

Versioning the schema explicitly is how I handle this. The serialized state carries a schema version field, and on deserialization I run a migration function that maps old versions onto the current schema before the agent processes anything. A database migration does the same job for table columns, and the discipline transfers directly.

Stale state is a separate problem. A customer support agent serialized three days ago holds state that may no longer match reality. The customer might have resolved their issue through live chat, or the product might have shipped a change that voids the agent's last assumption. An agent proceeding from stale state can do more damage than an agent with no memory at all, since it acts with false confidence.

Validating and refreshing on deserialization is the fix. Check timestamps. Confirm critical facts before acting on them, the way a good support rep opens with "I see you reported a billing error last week, is that still happening?" rather than assuming. Give the agent a way to flag that it needs to re-verify something instead of treating old state as gospel.

## The Schema Design Decisions That Matter

Context window size drives a lot of the serialization strategy. A 1M token context window from Gemini 2.5 Pro changes what you can serialize compared to a 200k window from Claude 3.5 Sonnet. Given a large window, you can afford to serialize full recent history and let the agent sort through it on load. A smaller window forces you to be surgical about what goes into serialized state.

Separating the conversation log from structured state is a habit I always keep. The log is append-only and grows unbounded, a transcript of everything said. The structured state is the small set of facts the agent actively uses to make decisions. A sliding window of recent log entries covers reconstruction, and the structured state gets serialized on its own track.

Running multiple agent instances is where cloud-native serialization starts to matter. SQLite is plenty for a single instance. Spread across containers or regions, the serialized state needs to live somewhere shared. S3 with JSON covers most of my projects. The added latency for a GET on startup typically stays under 50ms for a well-designed schema under 100KB.

## What Serialization Cannot Solve

Serialization handles session continuity. Retrieval is a different problem it leaves untouched. Serialize a conversation with no way to find the relevant parts quickly, and you end up with context that is technically present but practically unusable, like a filing cabinet stuffed with every document you own and no folder labels.

The memory hierarchy matters here. Serialized state is one layer. How you index and retrieve from that state is another. [My post on the memory hierarchy](/blog/the-memory-hierarchy-why-rag-is-not-enough/) goes into this in detail, and the short version is that serialization and retrieval are separate problems you have to design together.

Agent memory retrieval is also asymmetric. What you serialize is not always what you retrieve. I wrote about this in my post on [asymmetric retrieval in agent memory](/blog/asymmetric-retrieval-agent-memory/). The schema you design for serialization shapes what retrieval looks like, and if you get the schema wrong, the retrieval will be wrong in predictable ways.

The serialization format itself matters less than the discipline of using it consistently. JSON is fine for most cases. Writing to disk on every action for an agent handling 10,000 requests per minute is the case where you need something faster. msgpack or Protocol Buffers cut serialization overhead by 5x in my benchmarks. For the vast majority of agents, JSON with a clear schema stays readable, debuggable, and sufficient.

## Where This Leaves You

Building an agent that users come back to over days or weeks makes serialization non-negotiable. It is the mechanism that lets a long-term relationship exist at all. Whichever pattern you choose shapes everything downstream: retrieval quality, context window utilization, latency on restart, and the agent's ability to actually use what it learned.

Start with a clear state schema. Serialize what matters. Validate on deserialization. Test your restart path on purpose, by actually killing the process mid-conversation and watching what comes back. An agent that performs flawlessly in a long-running session and loses everything on restart is an agent your users will stop trusting the morning after.
