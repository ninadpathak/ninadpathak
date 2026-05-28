---
title: "How Memory Works in DeerFlow"
date: 2026-04-19
description: "A deep dive into the memory architecture of DeerFlow: layered context passing, session state files, sub-agent isolation, and how it compares to Letta, AutoGen, and CrewAI."
tags: [ai, agents, memory, deerflow, infrastructure]
status: published
---

DeerFlow structures its memory system around something I call structured context passing. Rather than relying on a central vector store or a global knowledge graph, DeerFlow passes memory between agents through explicit JSON state files and Markdown context documents. Each agent in a workflow receives exactly what it needs at the moment it needs it, nothing more.

The result is an architecture that is auditable, debuggable, and surprisingly easy to reason about at scale. If you have been burned by opaque agent systems that lose track of what happened three steps ago, DeerFlow's approach will feel like a breath of fresh air.

<div class="visual-wrapper">
  <div class="visual-title">DeerFlow Memory Architecture</div>
  <div class="visual-container">
    <iframe src="/static/visuals/deerflow-memory.html" title="DeerFlow layered memory architecture" loading="lazy"></iframe>
  </div>
</div>

##The Layered Architecture Of DeerFlow Memory

DeerFlow organizes memory into three distinct layers that map cleanly to how humans actually think. Working memory lives in the prompt at execution time. Session memory lives in structured files that persist across turns. Long-term memory lives in a configurable store you plug in.

Working memory in DeerFlow is the current context window. It contains the system prompt, the task description, the conversation history, and any retrieved documents. This layer resets between major workflow stages. The key insight is that DeerFlow does not treat the working memory as a dump of everything known. It treats it as a carefully curated snapshot of what matters right now.

Session memory captures the accumulated state of a research or task workflow. When a DeerFlow workflow runs across multiple stages, each stage writes its outputs to a session file. The next stage reads that file and incorporates its contents into working memory. This design means you can stop a workflow mid-execution and resume it by reading the session file.

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

Long-term memory in DeerFlow is where things get interesting. You plug in your own store. The framework ships with adapters for vector databases, PostgreSQL with pgvector, and simple file-based retrieval. The long-term store holds facts and findings that persist beyond the current session. When a new session starts, DeerFlow retrieves relevant long-term context and injects it into working memory at the beginning of the workflow.

The three-layer model means you never pay the token cost of loading your entire knowledge base for every single agent invocation. You only load what the current stage needs.

##Session Continuity Via State Files

DeerFlow's structured file passing for session continuity is the same principle behind [checkpointing in production AI agents](/blog/production-ai-agent-errors/). The difference is that DeerFlow enforces it at the workflow level rather than the tool call level. If the workflow crashes, restarts, or gets handed off to a different process, it reads the state file and resumes from exactly where it left off.

The state file tracks three things: which stages completed, what each stage produced, and what the next stage should be. This is deliberately simple. Complex systems fail in complex ways. A plain JSON file that a human can read and edit is far more robust than a binary state store that requires special tooling to inspect.

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

The checkpoint interval tells DeerFlow how often to write a durable state snapshot. Setting it to 2 means every two completed stages produce a checkpoint. If you have a twenty-stage workflow, you have ten recovery points. A failure at stage seventeen restarts from the last checkpoint at stage sixteen.

I have tested this by killing a DeerFlow process mid-workflow and restarting it. The session file had the full state. The workflow resumed exactly where it left off. No lost work, no corrupted state.

##Sub-agent Isolation In Multi-stage Workflows

DeerFlow workflows compose multiple specialized agents. A research workflow might use a planner agent, a web search agent, a code execution agent, and a synthesis agent. Each agent operates in its own context window. Each agent writes its outputs to the shared session file when it completes.

Sub-agent isolation in this context means two things. First, each agent sees only the context it was explicitly given. A code execution agent does not see the raw web search results. It sees a curated summary written by the web search agent. Second, each agent runs to completion before the next agent starts. There is no concurrent execution where two agents write to the session file simultaneously.

This sequential isolation eliminates a class of race conditions that plague more loosely coupled multi-agent systems. The cost is latency. If you have four agents that each take thirty seconds, your workflow takes at least two minutes. For research tasks where depth matters more than speed, this trade-off is worth it.

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

The isolation model means you can also swap agents in and out without changing the surrounding infrastructure. If you want to replace the web search agent with a different provider, you only change the agent configuration. The session store interface stays the same.

##How Context Gets Passed Between Agents

Context passing in DeerFlow happens through a structured summary protocol. The output of each stage is not raw tool calls or raw LLM completions. It is a formatted summary document that the next agent can use as input.

This is the part that most multi-agent frameworks get wrong. They pass raw conversation logs between agents and expect each agent to figure out what matters. DeerFlow enforces a contract: each stage writes a summary in a known schema, and the next stage reads that schema.

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

The confidence field is especially useful. When a stage marks its confidence as low, downstream stages know to treat the findings as provisional. The synthesis agent might spend more time cross-checking facts before including them in the final output. This is the same pattern I described in my [agent harness](/blog/agent-harnesses/) post where explicit state transitions prevent the model from improvising recovery.

Raw data refs point to stored artifacts. If the web research agent crawled twelve pages, those pages are stored and referenced by ID. The synthesis agent can pull the actual text if it needs to verify a finding.

##Memory Retrieval At Workflow Initialization

When a DeerFlow workflow starts, it does not start with a blank slate. It queries the long-term memory store for relevant content from previous sessions. This is where the vector store or pgvector adapter does its work.

The retrieval query is built from the workflow task description and any session initialization parameters. DeerFlow embeds the task description, runs similarity search against the memory store, and returns the top-k results. Those results get injected into the working memory before the first agent runs.

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

The filters on the query let you scope retrieval to specific topic areas. If you are running a workflow about latency benchmarking, you do not want to pull in memories about code style debates. Tag-based filtering keeps retrieval focused.

##Production Considerations

Running DeerFlow in production surfaces three concerns that the documentation does not emphasize enough.

**Token budget management.** A twenty-stage workflow can accumulate significant context if each stage writes verbose summaries. Set hard limits on working memory size and enforce truncation or summarization at stage boundaries. The YAML config above lets you set `max_tokens` on the working memory layer. Do not leave that at the default and assume it will scale.

**State file durability.** DeerFlow writes session state to disk. If the disk fills up or the write permissions get revoked, the workflow fails silently on the next restart. Use a durability-checked storage backend (postgresql works well) rather than the filesystem adapter for anything mission-critical.

**Memory store query latency.** Long-term memory retrieval adds latency at workflow initialization. If your vector store is cold (no cached embeddings), a retrieval query can take two to three seconds. For workflows that run hundreds of times per day, that latency compounds. Warm your vector store cache or accept that initialization takes a few seconds.

##Comparison To Other Frameworks

Letta treats memory as an operating system, paging context in and out of the LLM window like RAM. DeerFlow takes the opposite approach: keep context small and explicit, pass it between stages as structured documents, and rely on the long-term store for anything that needs to survive across sessions.

Letta wins when you have a single agent that needs to maintain identity over thousands of interactions. DeerFlow wins when you have a workflow that decomposes into specialized stages and you need auditability about what each stage found.

AutoGen exposes a more flexible but less opinionated message-passing model. Multiple agents can run concurrently and exchange messages freely. This flexibility is powerful for complex collaboration patterns. It is also harder to debug because messages can arrive in non-deterministic order and state gets spread across many agents rather than concentrated in one session file.

CrewAI uses role-based agents with shared goals and a manager agent that assigns tasks. The memory model is implicit in the manager's task assignment logic. DeerFlow's explicit session files are more verbose but far easier to inspect when something goes wrong.

The table below summarizes the differences.

| Concern | DeerFlow | Letta | AutoGen | CrewAI |
|---|---|---|---|---|
| Memory model | Structured file passing | OS-style paging | Message passing | Manager task assignment |
| Session continuity | Deterministic file-based | Virtual memory protocol | Message history | Task context |
| Sub-agent isolation | Sequential, stage-gated | Per-agent memory spaces | Concurrent message exchange | Role-based task isolation |
| Auditability | High (human-readable JSON) | Medium | Low | Medium |
| Long-term memory | Pluggable adapter | Built-in | Do-it-yourself | Do-it-yourself |
| Best for | Structured research workflows | Long-horizon single agents | Complex multi-agent collaboration | Role-based task automation |

DeerFlow is not the right tool for every agent problem. If you are building a chatbot that needs to remember a user's preferences over months, use Letta. If you are building a research pipeline that needs to be auditable and resumable, use DeerFlow.

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