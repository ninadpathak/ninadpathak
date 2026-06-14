---
title: "How Memory Works in HyperAgents"
date: 2026-04-19
description: "A deep dive into how HyperAgents retain context across interactions, layer memory architectures, and handle session continuity in production."
tags: [ai, agents, memory, hyperagents, infrastructure]
status: published
---

<div class="visual-wrapper">
  <div class="visual-title">HyperAgents Memory Architecture</div>
  <div class="visual-container">
    <iframe src="/static/visuals/hyperagents-memory.html" title="HyperAgents memory architecture" loading="lazy"></iframe>
  </div>
</div>

##What Is a Hyperagent And Why Does Memory Matter

A HyperAgent is not a single language model call. It is a composed system of models, tools, and a reasoning loop that can run for minutes or hours across many steps. Build something that lives inside a long-running process and you quickly hit a wall: the model forgets. Context windows fill up. Sessions collapse. Lacking a memory architecture, every turn starts from scratch and every user experience degrades. I watched one of my early agents spend three turns re-reading the same config file because it had already pushed the earlier read out of its context window.

Giving the agent somewhere to store what it knows, what it has done, and what it still needs to do is what memory in HyperAgents actually buys you. The architecture I am describing here is the one I built into my own agent runner, and it has handled sessions with 500+ turns without degradation.

##The Three-layer Memory Architecture

HyperAgents do not use a single memory store. They use three distinct layers, each with a different access pattern and purpose. Knowing what each layer does is the difference between an agent that feels smart and one that actually is. Picture the layers the way an operating system stacks storage: CPU registers for what you need this instant, RAM for the active session, disk for everything you might recall later. Each tier trades speed for capacity, and you reach for the slow one only when the fast one cannot hold the answer.

###Layer 1: Working Context (In-Memory)

Living in RAM during a session, the working context holds the current conversation history, the agent's current goal, and a sliding window of recent tool results. Every model call reads from this layer directly, so whatever sits here is what the agent can reason over right now.

```python
class WorkingContext:
    def __init__(self, max_turns: int = 50):
        self.messages: list[dict] = []
        self.goal: str = ""
        self.tool_results: deque = deque(maxlen=20)
        self.max_turns = max_turns

    def add_turn(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_turns:
            self.messages.pop(0)
```

How far back the agent can "see" is set by the `max_turns` parameter. Setting it to 50 gives you roughly 100K tokens of context history assuming average turns at 1K tokens each. On a model with a 128K context window, you have room to spare. Running against a 4K window, you need to be more aggressive, dropping `max_turns` to something like 6 and leaning harder on the lower layers.

###Layer 2: Episodic Memory (Durable Store)

Working context evaporates when the session ends. Episodic memory persists across sessions by writing structured summaries to disk or a database. Each episode captures what happened, what was decided, and what outstanding threads remain, the way a good standup note records "shipped the auth refactor, decided to defer rate limiting, still need to fix the flaky test" rather than replaying every keystroke.

```python
class EpisodicMemory:
    def __init__(self, store_path: str):
        self.store = SQLiteStore(store_path)
        self.session_id: str = ""

    def start_session(self, session_id: str):
        self.session_id = session_id
        self.store.execute(
            "INSERT INTO sessions (id, started_at) VALUES (?, ?)",
            (session_id, datetime.utcnow().isoformat())
        )

    def save_episode(self, episode: dict):
        self.store.execute(
            """INSERT INTO episodes
               (session_id, turn, summary, decisions, open_threads, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                self.session_id,
                episode["turn"],
                episode["summary"],
                json.dumps(episode["decisions"]),
                json.dumps(episode["open_threads"]),
                datetime.utcnow().isoformat()
            )
        )
```

An episode gets written every N turns (I default to 10) or when the user goes quiet for more than 30 seconds. A separate call to the LLM generates the summary, condensing the last N turns into a 2-3 sentence synopsis. Storing the synopsis instead of the transcript keeps episodic storage small while retaining the shape of what happened.

###Layer 3: Knowledge Base (Long-Term Store)

Knowledge base is where you put things the agent should know but does not need in every prompt: factual knowledge, learned procedures, and accumulated user preferences such as "this user always wants TypeScript, never JavaScript" or "deploy targets are us-east-1 by default". The agent queries this layer only when relevant, not on every turn.

```python
class KnowledgeBase:
    def __init__(self, kb_path: str):
        self.kb = ChromaDBClient(kb_path)

    def store_fact(self, key: str, value: str, metadata: dict):
        self.kb.upsert(
            collection="facts",
            id=key,
            text=value,
            metadata=metadata
        )

    def query(self, query: str, top_k: int = 5) -> list[str]:
        results = self.kb.query(
            collection="facts",
            query_texts=[query],
            n_results=top_k
        )
        return [doc["text"] for doc in results["documents"][0]]
```

The retrieval step happens at the start of a new session when you load the user's history. You pull their last 10 episode summaries, rank them by recency, and inject the top 3 into the working context as a "here is where we left off" block.

##Session Continuity In Practice

Session continuity is where most agent frameworks fall apart. A user kicks off a multi-step data migration at 6pm, closes the laptop, and comes back the next morning expecting the agent to pick up exactly where it left off. Absent explicit architecture, the agent has no idea what happened before and cheerfully starts the migration over from row one.

The continuity flow I use:

1. On session resume, load the last episodic summary for this user.
2. Inject it as a system message with a special prefix `[RESUMED_SESSION]`.
3. Pull any open threads from the last episode and add them to the agent's goal state.
4. Confirm back to the user with "Resuming from where we left off: [summary]".

```python
def resume_session(user_id: str) -> WorkingContext:
    last_episodes = db.query(
        "SELECT * FROM episodes WHERE user_id = ? ORDER BY created_at DESC LIMIT 3",
        (user_id,)
    )

    context = WorkingContext()
    context.add_turn("system",
        f"[RESUMED_SESSION] Last active: {last_episodes[0]['summary']}")
    context.goal = last_episodes[0].get("open_threads", [])

    return context
```

Handling the "I left off mid-task" problem this way keeps the resume clean. The agent sees the summary, knows what was unfinished, and can reorient immediately. No hallucination about what happened, no wasted turns re-discovering the context.

##Tool Memory And Intermediate Results

When a HyperAgent calls a tool, the result of that call is transient unless you capture it. Say the agent runs a code execution tool and gets back a 500-line stack trace plus test output. That blob needs to live somewhere the moment the agent might want to quote a specific line of it later.

I use a tool result buffer that stores the last N tool calls with their outputs. As the context window gets tight, I compress older tool results into summaries rather than dropping them entirely.

```python
class ToolResultBuffer:
    def __init__(self, max_entries: int = 15):
        self.entries: deque = deque(maxlen=max_entries)

    def store(self, tool_name: str, input_params: dict, output: str, compressed: bool = False):
        self.entries.append({
            "tool": tool_name,
            "input": input_params,
            "output": output if not compressed else compress(output),
            "compressed": compressed
        })

    def compress_oldest(self, compression_model="gpt-4o-mini"):
        oldest = self.entries[0]
        summary = call_llm(
            f"Compress this tool output to 3 sentences: {oldest['output']}"
        )
        oldest["output"] = summary
        oldest["compressed"] = True
```

A cheaper, smaller model handles the compression fine, since it only needs to extract gist-level information. gpt-4o-mini is more than sufficient for this. The compressed entry preserves the fact that something happened and what the outcome was, for example "ran the test suite, 3 of 47 failed, all in the billing module", without storing 500 lines of raw output.

##Context Window Management

Context windows are finite. A HyperAgent running 200 turns against a 128K context window will eventually fill up, especially with verbose tool outputs mixed in. Managing long sessions actively beats trying to avoid them, because the useful work is in the long sessions.

I use a tiered truncation strategy. At 70% context usage, the agent gets a warning and I trigger mid-level compression of older tool results. Once usage crosses 85%, I run full summarization of the oldest half of the conversation. At 95%, I force-persist the current state to episodic memory and start a new working context with only the last 5 turns plus the episode summary.

```python
def check_context_pressure(context: WorkingContext, model: str):
    usage = count_tokens(context.messages + context.tool_results)
    max_ctx = {"gpt-4o": 128000, "gpt-4o-mini": 128000,
               "claude-3-5-sonnet": 200000}.get(model, 128000)

    pressure = usage / max_ctx

    if pressure > 0.95:
        persist_and_reset(context)
    elif pressure > 0.85:
        summarize_oldest_turns(context, keep=10)
    elif pressure > 0.70:
        compress_tool_results(context, oldest_first=True)
```

Waiting until the context is full to act is the mistake I made first, and it bit me when a single large tool result blew past the limit mid-turn and the call failed outright. The 70/85/95 thresholds give the system room to breathe and prevent forced truncation mid-turn.

##Embedding And Retrieval For Context Injection

When a session resumes or when an agent needs to know something from three sessions ago, you cannot just dump all history into the prompt. You need to retrieve the relevant pieces.

Embedding-based retrieval works well here. Each episodic summary gets embedded at save time and stored in a vector index. To find relevant history, you embed the current conversation state and do a nearest-neighbor search against the summary index, the same move a librarian makes when you describe a book you half-remember and they walk you to the right shelf instead of reciting the whole catalog.

```python
def retrieve_relevant_history(current_context: str, user_id: str, top_k: int = 5) -> list[dict]:
    query_embedding = embed(current_context)

    results = db.query(
        """SELECT e.* FROM episodes e
           JOIN sessions s ON e.session_id = s.id
           WHERE s.user_id = ?
           ORDER BY cosine_distance(e.embedding, ?) ASC
           LIMIT ?""",
        (user_id, query_embedding, top_k)
    )
    return results
```

The embedding model matters. `text-embedding-3-small` from OpenAI gives good results at low cost. `bge-m3` from BAAI is a solid open-source alternative if you need to stay on-premises. Embed at save time, not at query time. Paying the embedding cost once on write beats recomputing it on every read, and the extra storage is cheap by comparison.

##Multi-agent Memory Sharing

When you have multiple HyperAgents working together on a problem, memory becomes a coordination problem. A research agent finishes gathering sources and a writer agent needs to know what it found. A third agent rejoining a project needs the shared context from a previous joint session.

I use a shared episodic store with a concept called "shared context episodes". Working together, agents write to a shared session with their own episode streams. Other agents read from that shared store by querying across agent IDs, the way a team channel lets anyone scroll back through what colleagues posted without sitting in every meeting themselves.

```python
class SharedMemoryStore:
    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)

    def write_shared_episode(self, agent_id: str, session_id: str, episode: dict):
        self.db.execute(
            """INSERT INTO shared_episodes
               (agent_id, session_id, turn, summary, embedding, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                agent_id,
                session_id,
                episode["turn"],
                episode["summary"],
                embed(episode["summary"]),
                datetime.utcnow().isoformat()
            )
        )

    def read_shared_history(self, session_id: str, requesting_agent: str) -> list[dict]:
        rows = self.db.execute(
            """SELECT * FROM shared_episodes
               WHERE session_id = ?
               ORDER BY created_at ASC""",
            (session_id,)
        ).fetchall()
        return [{"agent": r[0], "turn": r[2], "summary": r[3]} for r in rows]
```

The pattern lets agents contribute to a collective memory without stepping on each other's context. The embedding column exists specifically for cross-agent relevance queries, so the writer agent can pull "everything the researcher logged about pricing" rather than reading all of it.

##Production Considerations

If you want to understand how this compares to other memory systems, see my post on [context windows vs memory](/blog/context-windows-vs-memory/). For a deeper look at memory hierarchy in AI systems, check out [memory hierarchy in AI systems](/blog/memory-hierarchy-in-ai-systems/).

Memory architecture that looks clean in a notebook breaks in production if you do not account for latency, storage growth, and failure modes.

**Write latency** is the first trap. Writing to SQLite on every turn adds 5-10ms per operation. At 500 turns per session, that is 2.5-5 seconds of overhead spread across the session. For a smooth user experience, you want to batch writes or do them asynchronously. I use a background thread that flushes the episodic buffer every 30 seconds or every 10 turns, whichever comes first.

**Storage growth** is the second trap. Episodic summaries are small but they compound. With 100 users doing 10 sessions per day, you write 1000 episodes daily. At 500 bytes per summary, that is 500KB per day, or 180MB per year. Negligible. But if you store full tool result logs instead of summaries, that number jumps by two orders of magnitude. Be deliberate about what you store and for how long.

**Failure recovery** is the third trap. Should the agent crash mid-session, what survives? Working context is gone. Episodic memory on disk survives. Knowledge base survives. The failure mode you want to avoid is a crash mid-write that leaves the episodic store half-flushed and corrupt, taking the only durable record down with it. Use append-only writes and validate integrity on startup.

```python
def startup_health_check(store: EpisodicMemory):
    try:
        latest = store.store.query("SELECT id FROM episodes ORDER BY id DESC LIMIT 1")
        store.store.execute("SELECT COUNT(*) FROM episodes")
    except sqlite3.DatabaseError as e:
        logging.critical(f"Episodes store corrupted: {e}. Re-initializing.")
        store.store.execute("VACUUM")
```

VACUUM rebuilds the SQLite file and fixes most corruption scenarios. It is not guaranteed, but it handles the common case where a crash left the WAL in an inconsistent state.

##Comparing Hyperagent Memory To Standard RAG

Standard RAG (Retrieval-Augmented Generation) relies on a vector store and a fixed corpus. You index documents, the user asks a question, you retrieve relevant chunks, and the model answers. That pattern serves static knowledge bases well. Agentic workflows break it.

HyperAgent memory differs in three fundamental ways. First, it is bidirectional. The agent writes to memory as it works, then reads its own notes back later. Second, it is temporal. Memories are tagged with when they happened and what happened before and after. Third, it is goal-directed. Memory tracks what the agent is trying to accomplish and what remains, alongside what it knows.

A standard RAG pipeline would not know that the agent is three steps into a six-step deployment. A HyperAgent memory system knows the full trajectory and can reconstruct it.



##Related Articles

- [Context windows vs memory](/blog/context-windows-vs-memory/)
- [AI memory management for LLMs](/blog/ai-memory-management-for-llms/)
- [Short-term memory for AI agents](/blog/short-term-memory-for-ai-agents/)
- [State of AI agent memory 2026](/blog/state-of-ai-agent-memory-2026/)

##Faq

**How does HyperAgent memory differ from conversation history in a chat model?**

Conversation history is raw. It contains every message in sequence. HyperAgent memory is structured and tiered. Raw history lives in working context. Structured summaries and decisions live in episodic memory. Facts and procedures live in the knowledge base. Tiering it this way lets the agent reach the right information at the right time without drowning in noise.

**Can memory be shared across different agent instances?**

Yes. Shared episodic stores let multiple agent instances read and write to a common memory space, which helps multi-agent workflows where agents need to coordinate or build on each other's work.

**What happens if the episodic store grows too large?**

You can implement a retention policy that rolls off old episodes. I keep the last 30 sessions per user in full and compress anything older than 90 days into a single yearly summary. Rolling off this way keeps storage bounded while retaining enough history to handle the "where did we leave off" question.

**How do you handle memory when switching between different LLMs?**

The memory layer is model-agnostic. Working context is a list of messages in OpenAI SDK format by default, but you can translate to Anthropic format or any other provider's schema at the adapter layer. The episodic and knowledge layers are pure data and do not care which model is consuming them.

**Is memory written synchronously or asynchronously?**

Writes to the working context are synchronous (immediate). Writes to episodic memory are asynchronous via a background flush thread, which keeps memory writes from blocking the agent's main loop. The trade-off is that a crash can lose up to 30 seconds of recent episodes, which is acceptable for most production use cases.

**How do you handle sensitive data in memory?**

Episodic summaries should be generated with a system prompt that redacts sensitive fields (passwords, tokens, PII) before storage. The summary generation call runs through a sanitizer that replaces patterns like `[A-Za-z0-9+/]{32,}` with `[REDACTED]`. Actual tool outputs with sensitive data should be stored in memory only as compression summaries, never raw.

**What context pressure thresholds do you recommend?**

For models with 128K context, I use 70/85/95 as described above. For models with smaller windows (32K or below), you want tighter thresholds. Set your compression trigger at 60% and your forced persist at 80%. The goal is to always have headroom so a large tool result does not push you over the limit mid-turn.

**Can the agent access memory mid-turn or only at turn boundaries?**

Access is available at any point. The agent can query the knowledge base between tool calls or during planning phases. The working context is always available since it lives in the same process. Episodic retrieval typically happens at session start or when the agent explicitly calls a "recall" tool that queries the episodic store.

**How does the agent know which memory layer to use?**

Through the system prompt. The agent is instructed that recent turns and tool results live in working context, that session history is in episodic memory, and that factual knowledge is in the knowledge base. The instruction carries this, not the code. Agents learn to query memory appropriately after a few sessions in practice.

The memory architecture in HyperAgents is the reason it works reliably across long sessions. Without it, you have a powerful but forgetful system. With it, you have something that can hold context, learn from experience, and pick up work where it left off. That is the difference between a demo and a product.