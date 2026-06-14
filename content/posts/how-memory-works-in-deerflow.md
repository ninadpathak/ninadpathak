---
title: "How Memory Works in DeerFlow"
date: 2026-04-19
description: "A deep dive into the memory architecture of DeerFlow: layered context passing, session state files, sub-agent isolation, and how it compares to Letta, AutoGen, and CrewAI."
tags: [ai, agents, memory, deerflow, infrastructure]
status: published
---

Structured context passing is what I call the way DeerFlow organizes memory. Rather than relying on a central vector store or a global knowledge graph, DeerFlow passes memory between agents through explicit JSON state files and Markdown context documents. Each agent in a workflow receives exactly what it needs at the moment it needs it, nothing more.

What you get is an architecture you can audit, debug, and reason about at scale. The first time I traced a failed run by opening a single JSON file in my editor, instead of grepping through interleaved logs from five agents, the appeal was obvious. Anyone who has watched an opaque agent system lose track of what happened three steps ago will recognize the relief.

<div class="visual-wrapper">
  <div class="visual-title">DeerFlow Memory Architecture</div>
  <div class="visual-container">
    <iframe src="/static/visuals/deerflow-memory.html" title="DeerFlow layered memory architecture" loading="lazy"></iframe>
  </div>
</div>

##The Layered Architecture Of DeerFlow Memory

Three distinct layers organize memory in DeerFlow, and they map cleanly to how humans actually think. Working memory lives in the prompt at execution time. Session memory lives in structured files that persist across turns. Long-term memory lives in a configurable store you plug in.

Working memory in DeerFlow is the current context window. It contains the system prompt, the task description, the conversation history, and any retrieved documents. Between major workflow stages, that layer resets. What matters here is that DeerFlow does not treat working memory as a dump of everything known. It treats it as a curated snapshot of what matters right now, the way a surgeon lays out only the instruments for the current step rather than wheeling in the entire supply room.

Session memory captures the accumulated state of a research or task workflow. When a DeerFlow workflow runs across multiple stages, each stage writes its outputs to a session file. The next stage reads that file and folds its contents into working memory. You can stop a workflow mid-execution and resume it later by reading that one file, which is exactly what saved me the afternoon a benchmark run died at stage eleven of fourteen and I picked it back up without rerunning the first ten.

```python
# DeerFlow session state structure (simplified)
session_state = {
    "workflow_id": "research-2026-04-19-001",
    "current_stage": "web_research",
    "completed_stages": ["task_decomposition", "initial_planning"],
    "stage_outputs": {
        "task_decomposition": {
            "subtasks": ["gather_prerequisites", "run_benchmark", "compile_results"],
            "next_stage": "web_research"
        },
        "initial_planning": {
            "goals": ["measure_latency_p50", "compare_qps_limits"],
            "constraints": ["budget < $50", "max 2 hour runtime"]
        }
    },
    "memory_snapshots": [
        {"stage": "task_decomposition", "summary": "Decomposed into 3 subtasks"},
        {"stage": "initial_planning", "summary": "Set latency and budget constraints"}
    ]
}
```

Long-term memory in DeerFlow is where the design earns its keep. You plug in your own store. The framework ships with adapters for vector databases, PostgreSQL with pgvector, and plain file-based retrieval. The long-term store holds facts and findings that survive beyond the current session, say the benchmark results from last week that this week's run wants to compare against. When a new session starts, DeerFlow retrieves relevant long-term context and injects it into working memory at the beginning of the workflow.

Splitting memory into three layers means you never pay the token cost of loading your entire knowledge base for every single agent invocation. You only load what the current stage needs.

##Session Continuity Via State Files

DeerFlow's structured file passing for session continuity rests on the same principle behind [checkpointing in production AI agents](/blog/production-ai-agent-errors/). DeerFlow enforces it at the workflow level rather than the tool call level. Should the workflow crash, restart, or get handed off to a different process, it reads the state file and resumes from exactly where it left off.

The state file tracks three things: which stages completed, what each stage produced, and what the next stage should be. Deliberate simplicity is the point. Complex systems fail in complex ways. A plain JSON file that a human can read and edit holds up far better than a binary state store that needs special tooling to inspect, the same reason most of us would rather debug a config file than a memory dump.

```yaml
# deerflow_session.yaml — session configuration
session:
  id: "research-2026-04-19-latency-benchmark"
  storage_backend: "postgresql"
  vector_store:
    provider: "pgvector"
    connection: "postgresql://user:pass@localhost:5432/deerflow"
    collection: "session_memories"
  checkpoint_interval: 2  # checkpoint every 2 stages

memory:
  working_memory:
    max_tokens: 128000
    eviction_policy: "oldest_first"

  session_memory:
    persist: true
    path: "/var/lib/deerflow/sessions/{session_id}.json"

  long_term_memory:
    retrieval_top_k: 10
    rerank: true
    rerank_model: "cross-encoder/ms-marco-MiniLM-L-12-v2"
```

The checkpoint interval tells DeerFlow how often to write a durable state snapshot. Setting it to 2 means every two completed stages produce a checkpoint. A twenty-stage workflow then gives you ten recovery points, so a failure at stage seventeen restarts from the last checkpoint at stage sixteen rather than from scratch.

To test this, I killed a DeerFlow process mid-workflow with a hard SIGKILL and restarted it. The session file held the full state. The workflow resumed exactly where it left off, with no lost work and no corrupted state.

##Sub-agent Isolation In Multi-stage Workflows

DeerFlow workflows compose multiple specialized agents. A research workflow might use a planner agent, a web search agent, a code execution agent, and a synthesis agent. Each agent operates in its own context window and writes its outputs to the shared session file when it completes.

Sub-agent isolation here means two things. First, each agent sees only the context it was explicitly handed. A code execution agent never sees the raw web search results. It sees a curated summary written by the web search agent, the same way a contractor works from the architect's drawings rather than the architect's entire pile of notes and site photos. Second, each agent runs to completion before the next agent starts, so no two agents ever write to the session file at the same moment.

Running agents in strict sequence eliminates a class of race conditions that plague more loosely coupled multi-agent systems. The cost is latency. Four agents that each take thirty seconds add up to a workflow of at least two minutes. For research tasks where depth matters more than speed, I happily take that trade.

```python
# DeerFlow multi-agent execution loop (simplified)
def run_deerflow_workflow(workflow_config: dict, session_store: SessionStore):
    workflow_id = workflow_config["id"]
    stages = workflow_config["stages"]  # ordered list of stage configs

    for stage in stages:
        agent = load_agent(stage["agent_type"])
        previous_outputs = session_store.read_latest(workflow_id)

        # Inject previous stage outputs into working memory
        context = build_context(
            system_prompt=stage["system_prompt"],
            task=workflow_config["task"],
            prior_outputs=previous_outputs,
            long_term_context=retrieve_from_memory(workflow_id)
        )

        # Agent runs to completion
        result = agent.run(context)

        # Write outputs to session store
        session_store.append(workflow_id, stage["name"], result)
        session_store.checkpoint(workflow_id)

    final_output = session_store.get_final_outputs(workflow_id)
    return final_output
```

Keeping agents isolated also lets you swap them in and out without touching the surrounding infrastructure. Replacing the web search agent with a different provider, say moving from a general search API to a domain-specific one, means changing the agent configuration and nothing else. The session store interface stays the same.

##How Context Gets Passed Between Agents

Context passing in DeerFlow runs through a structured summary protocol. The output of each stage is never raw tool calls or raw LLM completions. It arrives as a formatted summary document the next agent can use as input.

Passing raw conversation logs between agents and expecting each one to figure out what matters is the mistake I see most multi-agent frameworks make. DeerFlow enforces a contract instead: each stage writes a summary in a known schema, and the next stage reads that schema.

```python
# Stage output schema (enforced by DeerFlow)
stage_output = {
    "stage_name": "web_research",
    "summary": "String — what was found and why it matters",
    "key_findings": [
        {"fact": "string", "source": "url or document ID"},
        {"fact": "string", "source": "url or document ID"}
    ],
    "confidence": "high | medium | low",
    "next_stage_recommendations": ["suggested focus areas for synthesis"],
    "raw_data_refs": ["pointers to stored raw outputs"]
}
```

The confidence field earns its place. When a stage marks its confidence as low, downstream stages know to treat the findings as provisional, and the synthesis agent can spend more time cross-checking a shaky claim, like a single-source statistic, before it lands in the final output. The same pattern shows up in my [agent harness](/blog/agent-harnesses/) post, where explicit state transitions stop the model from improvising recovery.

Raw data refs point to stored artifacts. When the web research agent crawls twelve pages, those pages get stored and referenced by ID. The synthesis agent can pull the actual text whenever it needs to verify a finding against the source.

##Memory Retrieval At Workflow Initialization

When a DeerFlow workflow starts, it refuses to start with a blank slate. It queries the long-term memory store for relevant content from previous sessions, which is where the vector store or pgvector adapter does its work.

The retrieval query comes from the workflow task description and any session initialization parameters. DeerFlow embeds the task description, runs similarity search against the memory store, and returns the top-k results. Those results get injected into working memory before the first agent runs.

```python
def initialize_workflow(workflow_id: str, task: str, config: dict):
    # Retrieve relevant long-term context
    query_embedding = embed(task, model="text-embedding-3-large")
    relevant_memories = vector_store.query(
        vector=query_embedding,
        top_k=config.get("memory_retrieval_top_k", 10),
        filters={"session_tag": config.get("topic_tag", "general")}
    )

    # Build initial context
    context = {
        "task": task,
        "retrieved_memories": relevant_memories,
        "session_id": workflow_id,
        "config": config
    }

    # Write initial session state
    session_store.init(workflow_id, context)
    return context
```

The filters on the query let you scope retrieval to specific topic areas. Running a workflow about latency benchmarking, you have no use for memories about code style debates resurfacing in the planner's context. Tag-based filtering keeps retrieval focused.

##Production Considerations

Running DeerFlow in production surfaces three concerns the documentation underplays.

**Token budget management.** A twenty-stage workflow piles up serious context when each stage writes verbose summaries, and I have watched a research run quietly drift toward the model's context ceiling by stage fifteen because nobody capped the summaries. Set hard limits on working memory size and enforce truncation or summarization at stage boundaries. The YAML config above lets you set `max_tokens` on the working memory layer. Leaving that at the default and assuming it will scale is how runs start silently dropping early context.

**State file durability.** DeerFlow writes session state to disk. Should the disk fill up or the write permissions get revoked, the workflow fails silently on the next restart. Reach for a durability-checked storage backend (postgresql works well) rather than the filesystem adapter for anything mission-critical.

**Memory store query latency.** Long-term memory retrieval adds latency at workflow initialization. A cold vector store with no cached embeddings can take two to three seconds per retrieval query. For workflows that run hundreds of times per day, those seconds compound into real wall-clock time. Warm your vector store cache, or accept that initialization takes a few seconds and budget for it.

##Comparison To Other Frameworks

Letta treats memory as an operating system, paging context in and out of the LLM window like RAM. DeerFlow takes the inverted approach: keep context small and explicit, pass it between stages as structured documents, and lean on the long-term store for anything that needs to survive across sessions.

Letta wins when you have a single agent that needs to hold an identity over thousands of interactions, like a personal assistant that remembers your preferences across months. DeerFlow wins when you have a workflow that decomposes into specialized stages and you need to audit what each stage found.

AutoGen exposes a more flexible, less opinionated message-passing model where multiple agents run concurrently and exchange messages freely. Such flexibility pays off for complex collaboration patterns. Debugging gets harder for the same reason, since messages can arrive in non-deterministic order and state scatters across many agents rather than concentrating in one session file.

CrewAI uses role-based agents with shared goals and a manager agent that assigns tasks. Its memory model sits implicit inside the manager's task assignment logic. DeerFlow's explicit session files run more verbose, yet they are far easier to inspect when something goes wrong, because the state is sitting right there in a file you can open.

The table below summarizes the differences.

| Concern | DeerFlow | Letta | AutoGen | CrewAI |
|---|---|---|---|---|
| Memory model | Structured file passing | OS-style paging | Message passing | Manager task assignment |
| Session continuity | Deterministic file-based | Virtual memory protocol | Message history | Task context |
| Sub-agent isolation | Sequential, stage-gated | Per-agent memory spaces | Concurrent message exchange | Role-based task isolation |
| Auditability | High (human-readable JSON) | Medium | Low | Medium |
| Long-term memory | Pluggable adapter | Built-in | Do-it-yourself | Do-it-yourself |
| Best for | Structured research workflows | Long-horizon single agents | Complex multi-agent collaboration | Role-based task automation |

DeerFlow is not the right tool for every agent problem. Building a chatbot that needs to remember a user's preferences over months, reach for Letta. Building a research pipeline that needs to be auditable and resumable, reach for DeerFlow.

##Faq

**How does DeerFlow handle memory in short sessions versus long sessions?**

Short sessions (a few stages, under an hour) rely primarily on working memory and session memory. Long-term memory retrieval is lightweight or skipped. Long sessions trigger full memory initialization on startup and checkpoint more aggressively. The threshold is configurable via the session config.

**Can I use DeerFlow without a vector database?**

Yes. DeerFlow ships with a filesystem-based memory adapter that stores summaries as Markdown files and retrieves via keyword matching. It is slower for large knowledge bases but requires zero infrastructure. Switch to pgvector or a managed vector store when you need scale.

**What happens if a stage produces output that the next stage cannot parse?**

DeerFlow enforces schema validation on stage outputs. If a stage produces malformed output, the workflow halts and writes an error to the session file with the stage name, the validation error, and the raw output. You can fix the output manually and restart from the failed stage.

**How does DeerFlow compare to Model Context Protocol for memory standardization?**

DeerFlow predates MCP but aligns with its philosophy. MCP standardizes how agents talk to memory servers over a network protocol. DeerFlow standardizes how stages in a workflow pass context through structured files. Both approaches solve the fragmentation problem, just at different layers. You can use DeerFlow with an MCP-compatible memory server if your infrastructure already speaks MCP.

**Is DeerFlow suitable for real-time conversational agents?**

DeerFlow is built for task-oriented workflows, not free-form conversation. The stage-gated execution model means it is optimized for research, analysis, and code generation tasks where depth matters more than response latency. For real-time conversation, use a framework designed for that, like VAPI or a simple RAG pipeline. If you want to understand the long-term memory tradeoffs better, read my [breakdown of context retrieval](/blog/how-anthropics-contextual-retrieval-changes-rag-architecture/).