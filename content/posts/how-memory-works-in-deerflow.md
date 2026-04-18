---
title: "How Memory Works in DeerFlow: A Deep Dive into the 2026 Agent Harness"
date: 2026-04-19
description: "DeerFlow 2.0 hit #1 on GitHub Trending in February 2026. I explored its multi-layer memory architecture: within-session summarization, cross-session long-term storage, and isolated sub-agent contexts."
tags: [ai, agents, memory, deerflow, infrastructure]
status: published
---

I have been building agentic systems for three years. The hard problems are never about model capability. They are about memory. A model that cannot remember what happened five minutes ago cannot reason about a multi-step task. A system that loses state between sessions cannot build on past work. DeerFlow 2.0, the ByteDance open-source super agent harness that topped GitHub Trending on February 28th 2026, makes memory a first-class architectural concern. Here is what I found inside its design.

## What DeerFlow Actually Is

DeerFlow stands for Deep Exploration and Efficient Research Flow. The project lives at [github.com/bytedance/deer-flow](https://github.com/bytedance/deer-flow) and it is a ground-up rewrite from v1. The team abandoned backward compatibility to build something that works as a production runtime, not a research prototype.

The core architecture runs on LangGraph for agent orchestration and LangChain for tool integration. You configure models in `config.yaml` using any OpenAI-compatible endpoint. The system supports Doubao-Seed-2.0-Code, DeepSeek v3.2, and Kimi 2.5 as recommended models, but the framework is model-agnostic. You can point it at any endpoint that speaks the ChatCompletions API.

What makes DeerFlow different from a bare LangChain app is everything it ships with: skills as structured Markdown workflows, sandboxed code execution, sub-agent spawning, IM channel integrations (Telegram, Slack, Feishu, WeChat, WeCom), and a memory system that operates at three distinct layers. That memory system is the focus of this piece.

## The Three Memory Layers in DeerFlow

Most agent frameworks conflate memory into one bucket. DeerFlow splits it deliberately. Each layer serves a different purpose and operates on a different timescale.

### Layer 1: Thread State and Context Memory

The first layer is session-scoped and lives in LangGraph's thread state. Every conversation lives in a ThreadState object that extends LangGraph's base AgentState. The data structure looks like this in the codebase:

```python
class ThreadState(AgentState):
    # Core state from AgentState
    messages: list[BaseMessage]

    # DeerFlow extensions
    sandbox: dict             # Sandbox environment info
    artifacts: list[str]      # Generated file paths
    thread_data: dict         # {workspace, uploads, outputs} paths
    title: str | None         # Auto-generated conversation title
    todos: list[dict]        # Task tracking (plan mode)
    viewed_images: dict       # Vision model image data
```

The ThreadState lives in memory during the session and gets checkpointed to disk by LangGraph's checkpointer. If you restart the server, the thread state is reloaded from the last checkpoint, so the agent picks up exactly where it left off. This is not trivial. Getting checkpointing right across a distributed setup with multiple processes requires the LangGraph server to be the source of truth for state.

### Layer 2: Within-Session Summarization

Long conversations blow past token limits fast. DeerFlow handles this with a SummarizationMiddleware that runs inside the LangGraph agent before each model call. The middleware monitors message token counts and triggers compression when any configured threshold is hit.

The configuration in `config.yaml` looks like this:

```yaml
summarization:
  enabled: true
  model_name: null  # null = use default model

  trigger:
    - type: tokens
      value: 4000
    - type: messages
      value: 50

  keep:
    type: messages
    value: 20

  trim_tokens_to_summarize: 4000
```

The trigger uses OR logic. If token count hits 4000 or message count hits 50, summarization fires. The `keep` setting says preserve the 20 most recent messages. Everything older gets condensed into a single summary message injected back into the conversation.

The system is careful about message boundaries. AI messages and their corresponding tool result messages are kept together. If a cutoff point falls in the middle of an AI/Tool pair, the middleware adjusts to preserve the entire exchange. This matters because splitting a tool call from its result would break context continuity.

The summarization middleware runs at position 4 in the middleware chain, after ThreadDataMiddleware sets up paths and UploadsMiddleware processes files, but before TitleMiddleware generates conversation titles. The order matters: you want sandbox and file context established before the model generates a summary.

### Layer 3: Cross-Session Long-Term Memory

This is the layer most other agent frameworks skip. DeerFlow stores a persistent memory file at `backend/.deer-flow/memory.json`. This file accumulates facts about the user across sessions. You can view it via the `/memory` command in IM channels, and the Settings UI exposes a full editor.

The memory schema includes content, category, and confidence fields. You can add facts manually or let the system infer them from conversation. The fixture file at `backend/docs/memory-settings-sample.json` shows what the structure looks like:

```json
{
  "facts": [
    {
      "content": "Reviewer-added memory fact",
      "category": "testing",
      "confidence": 0.88,
      "source": "Manual"
    }
  ]
}
```

The architecture doc shows that memory lives in the Gateway API layer, not in the LangGraph server. The Gateway API (`app/gateway/app.py`) serves REST endpoints for skills management, file uploads, and thread cleanup. Long-term memory is part of this same surface. This means memory operations do not go through the agent runtime, which keeps them fast and isolated from agent state churn.

The memory is stored locally and stays under your control. There is no external service dependency. If you want encryption at rest, you handle it at the filesystem level. This design reflects DeerFlow's philosophy: the user owns their data.

## How Sub-Agent Context Isolation Works

DeerFlow decomposes complex tasks by spawning sub-agents. A research task might fan out into a dozen parallel sub-agents, each exploring a different angle, then converge into a single output. This is where most frameworks trip up.

DeerFlow enforces strict context isolation between sub-agents. The documentation puts it plainly: each sub-agent runs in its own isolated context and cannot see the main agent's context or other sub-agents' contexts. This is a deliberate architectural decision. If every sub-agent could see the full parent context, context window usage would explode and you'd lose the ability to run truly parallel work.

The isolation works through LangGraph's thread system. When the lead agent spawns a sub-agent, it creates a new thread with a scoped context, its own tools, and its own termination conditions. The sub-agent reports back structured results. The lead agent then synthesizes everything. You can see this pattern in the Go implementation (deer-flow-go) which has explicit agent roles: coordinator, planner, researcher, coder, reporter.

The implication for memory is important. Sub-agents do not have access to long-term memory by default. They operate with only what the lead agent explicitly passes in. If you want a sub-agent to know something about the user, the lead agent must inject it into the sub-agent's context. This keeps sub-agents focused and predictable.

## The Sandbox and Context Interaction

DeerFlow runs every task inside an isolated Docker container (or Kubernetes pod in production mode). The sandbox has its own filesystem with virtual paths:

| Virtual Path | Physical Path |
|-------------|---------------|
| `/mnt/user-data/workspace` | `backend/.deer-flow/threads/{thread_id}/user-data/workspace` |
| `/mnt/user-data/uploads` | `backend/.deer-flow/threads/{thread_id}/user-data/uploads` |
| `/mnt/user-data/outputs` | `backend/.deer-flow/threads/{thread_id}/user-data/outputs` |
| `/mnt/skills` | `deer-flow/skills/` |

The agent reads, writes, and edits files inside the sandbox. Intermediate results go to workspace. Uploads land in the uploads directory. Final deliverables go to outputs. This filesystem is the out-of-band memory channel. When summarization fires and old messages get compressed, the artifacts from those messages are still on disk in the workspace. The agent can retrieve them if needed.

The sandbox system is abstract. `LocalSandboxProvider` runs code directly on the host for development. `AioSandboxProvider` uses Docker containers for isolation. In production with Kubernetes, a provisioner service spins up pods dynamically. The agent code does not care which provider is active; the abstraction holds.

## Session Continuity and Thread Checkpointing

Most chat interfaces treat each message as independent. DeerFlow treats each conversation as a thread that persists. The LangGraph server manages threads with a checkpointer that saves state after every step. If the server crashes and restarts, threads resume from their last checkpoint.

The Gateway API handles filesystem cleanup when threads are deleted. The flow is split: LangGraph handles `DELETE /api/langgraph/threads/{thread_id}` for thread state, and then the Gateway's threads router removes DeerFlow-managed filesystem data via `Paths.delete_thread_dir()`. This separation keeps the LangGraph server focused on agent state while the Gateway handles file lifecycle.

Thread state includes the auto-generated title, task todos (when plan mode is enabled), viewed images (for vision model support), and the full message history. When a thread resumes, the model sees the complete conversation, not just the last message.

## Comparing DeerFlow Memory to Other Frameworks

LangChain agents typically store conversation in a BaseChatMessageHistory object that persists to a backing store. The abstraction is clean but the implementation is left to the developer. DeerFlow makes concrete choices: checkpoint to LangGraph's checkpointing system, store long-term memory in a local JSON file, summarize with a middleware component.

AutoGPT and similar frameworks write task outputs to disk and read them back as context. DeerFlow formalizes this with its sandbox filesystem. The difference is that DeerFlow's sandbox paths are first-class citizens that the middleware manages automatically. You do not manually inject file contents into prompts; the system handles it.

CrewAI uses a "bag of tasks" approach where agents share context loosely. DeerFlow's sub-agent isolation is stricter. You spawn a sub-agent with exactly the context it needs. If you want shared context, you pass it explicitly. This trades flexibility for predictability.

## Production Considerations

If you run DeerFlow as a long-running server, the memory system has specific operational implications. The long-term memory file grows over time. There is no built-in eviction policy in the documentation; you manage it through the Settings UI or by editing the JSON directly. For high-volume deployments, you will want to consider a memory compaction strategy.

Summarization has a cost. The middleware makes an additional model call when thresholds are hit. The default configuration uses the same model for summarization as for the main task, which works but is not cheap. The documentation recommends a lightweight model like `gpt-4o-mini` for summarization to reduce costs.

Checkpointing adds latency to every step. For latency-sensitive applications, you need to benchmark the overhead. The checkpointer saves state to disk after each agent step; for I/O-bound storage, this can add measurable delay.

The sandbox isolation layer adds overhead that pure in-process agents do not have. If your tasks are short and stateless, this overhead may not be worth it. If your tasks involve code execution or file manipulation, the isolation is worth the cost.

## FAQ

**Does DeerFlow use vector storage for memory retrieval?**

No. The long-term memory system stores structured facts in a JSON file. There is no semantic search over memory built into the framework. You manage retrieval yourself if you need it.

**Can sub-agents access long-term memory?**

Sub-agents do not have direct access to the long-term memory file. The lead agent must inject relevant facts into the sub-agent's context. This is a design choice to keep sub-agent contexts small and predictable.

**What happens when summarization triggers mid-conversation?**

The middleware preserves the last N messages (configured via `keep`) and compresses everything older into a single summary message injected as a HumanMessage. The AI/Tool message pairs are kept intact. The conversation continues with the summary as context.

**How does DeerFlow handle concurrent sessions?**

Each thread is independent in LangGraph. The Gateway API manages concurrency through async tasks in Gateway mode (experimental), or through the LangGraph server's job queue in standard mode. Gateway mode reduces process count from 4 to 3 and removes the LangGraph Platform license requirement.

**Is memory encrypted at rest?**

No. The memory file at `backend/.deer-flow/memory.json` is plain JSON on disk. Encryption is your responsibility at the filesystem level.

**Can I use DeerFlow without Docker?**

Yes. The `LocalSandboxProvider` runs sandbox code directly on the host machine. Docker is the recommended production path but not the only option. Local mode is intended for development and evaluation.

## The Architecture in One View

DeerFlow's memory system is not a single component. It is a composition of three layers operating at different timescales. The ThreadState holds the active conversation. The SummarizationMiddleware compresses it when needed. The memory.json file holds facts across sessions. Sub-agent isolation keeps parallel work from interfering. The sandbox filesystem provides the out-of-band storage for artifacts and intermediate results.

The design reflects a specific philosophy: memory should be explicit, controllable, and layered. When you know where each piece of information lives, you can reason about it. When the system manages memory automatically, you get surprises in production.

For me, the most interesting choice is the strict sub-agent isolation. Most frameworks let you share context freely, which makes prototyping easier but production harder. DeerFlow forces you to be explicit. If you want shared context, you pass it. This is more work upfront but it makes multi-agent systems predictable.

The framework is young. Version 2.0 launched in early 2026 and the GitHub repo shows active development. The memory system will evolve. But the core architecture, the separation of concerns, and the emphasis on user ownership of data are solid foundations to build on.

If you want to explore the codebase yourself, the key files are: `packages/harness/deerflow/agents/lead_agent/agent.py` for the lead agent and middleware chain, `packages/harness/deerflow/config/summarization_config.py` for the summarization configuration, and `backend/.deer-flow/memory.json` for the long-term memory store.
