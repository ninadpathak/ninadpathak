---
title: "Memory Hierarchy in AI Systems: From Sensory to Semantic"
date: 2026-04-19
description: "How分层记忆架构帮助AI系统实现长期上下文、个性化和持续学习——以及为什么平坦记忆会失败。"
tags: [ai, agents, memory, cognitive-architecture, infrastructure]
status: published
---

为什么AI模型在对话中途突然失忆，却声称自己记得一切？为什么一个Agent前几轮说的话，下一轮就像没发生过？问题不在模型本身，在于记忆架构。

人类大脑从不把全部经验平铺存储。它分层管理：从感官输入到工作记忆，再到长期记忆，层层过滤，层层抽象。AI系统借鉴这套机制，才能真正具备持续性和一致性。

##The Atkinson-shiffrin Model And Its Ai Mapping

Richard Atkinson和Richard Shiffrin在1968年提出经典的三系统记忆模型：感觉记忆(sensory register)、短时记忆(short-term store)和长时记忆(long-term store)。五十年后，AI架构师不约而同地复制了这套设计。

```
┌─────────────────────────────────────────────┐
│           COGNITIVE ARCHITECTURE             │
│                                             │
│   Human Memory        →  AI System Memory   │
│   ─────────────        ─  ──────────────    │
│   Sensory Register    →  Input Buffer       │
│   Short-Term Store    →  Working Context    │
│   Long-Term Memory    →  Persistent Store   │
│     (Episodic)          (Vector DB)         │
│     (Semantic)          (Knowledge Graph)   │
│     (Procedural)        (Function Store)    │
└─────────────────────────────────────────────┘
```

每层的物理实现完全不同。人类大脑靠神经元群和突触权重；AI靠上下文窗口、向量数据库和代码存储。功能映射却惊人地一致。

##The Five Layers Of Ai Memory Hierarchy

###Sensory Memory: Raw Input Capture

这是最底层，寿命以毫秒计。在AI系统里，这对应原始用户输入——文字、语音 token、图像像素。你不会永久存储这些，它们进入系统的方式是一次性burst。

```python
# Sensory layer: raw input capture
class SensoryMemory:
    def __init__(self, ttl_ms: int = 500):
        self.buffer = RingBuffer(capacity=128)
        self.ttl_ms = ttl_ms

    def capture(self, input_token: str) -> None:
        self.buffer.write({
            "token": input_token,
            "timestamp": time.now(),
            "decay": self.ttl_ms
        })
```

Sensory memory的目的是保真度。不压缩，不索引，直接pass through。当用户说了一句话，前50个token还留在sensory buffer里，可以快速检索用于共指解析(coreference resolution)。

###Working Memory: The Context Window

GPT-4的128K上下文窗口，Claude的200Ktoken，这些是AI的working memory——或者说，是对它的拙劣模拟。真实working memory有容量限制，大约7±2个chunk；LLM的上下文窗口是固定token配额，没有内在优先级机制。

Working memory的特性是：**易失、有限、当前聚焦**。你在这个窗口里做的推理，决定了系统此刻的行为质量。

```
Working Memory State (example, simplified):

[0] system: "You are a helpful assistant..."
[1] user: "My dog Max is 3 years old..."
[2] user: "He's always scratching behind his ear..."
[3] assistant: "That sounds like it could be..."
[4] user: "What shampoo should I use?"

Current focus: shampoo recommendation for dog's ear issue
Relevant context: Max, 3yr dog, scratching behavior
Discarded (evicted): earlier parts of conversation
```

Eviction策略决定系统表现。FIFO是naive的；LLM用attention scores动态决定什么重要。这产生了一个AI特有的悖论：**上下文越长，推理质量不一定越高**。噪声稀释信号，相关token的attention weight被稀释。

Letta在2024年的研究量化了这个问题：在128K上下文中，中间25%的token平均attention weight只有边缘token的23%。

###Episodic Memory: Experience Storage

Episodic memory存储特定经历的时间、地点、情感标记。对AI，这对应对话历史、交互序列、任务执行轨迹。不同于working memory的volatile特性，episodic是persistent的——你希望它跨session存活。

```sql
-- Episodic memory schema (simplified)
CREATE TABLE episodic_memory (
    id SERIAL PRIMARY KEY,
    session_id UUID,
    timestamp TIMESTAMP,
    episode_type TEXT,  -- 'conversation', 'task', 'error'
    content_vector VECTOR(1536),  -- embedding
    raw_text TEXT,
    importance_score FLOAT,  -- 0-1, computed by relevance model
    decay_factor FLOAT DEFAULT 1.0  -- for forgetting curve
);
```

Letta的实现是这个方向最成熟的例子。它的MemFree协议定义了如何在episodic layer做检索：先用embedding similarity找到候选episodes，再用水印验证事实一致性，最后用reranker排序。实际召回率比纯向量搜索高40%。

###Semantic Memory: Structured Knowledge

Semantic memory存储事实、概念、词义关系——去除了一切个人经历的具体细节。这是知识库的本质：脱离上下文仍然为真的东西。

AI的semantic memory通常实现为知识图谱或结构化数据库。

```python
# Semantic memory: knowledge graph node
class Concept:
    def __init__(self, name: str, definition: str):
        self.name = name
        self.definition = definition
        self.relations = {}  # {relation_type: [target_concepts]}
        self.properties = {}
        self.confidence = 0.0
        self.last_updated = None

    def merge(self, new_info: dict) -> None:
        """Update concept with new evidence."""
        self.confidence = min(1.0, self.confidence + 0.1)
        self.last_updated = time.now()
```

MemGPT用tiered memory架构处理这个：热点事实驻留在GPU memory（HBM），冷数据下沉到CPU内存或NVMe SSD。关键问题是**何时把信息从episodic提升到semantic**。MemGPT用访问频率+重要性评分联合决策：访问超过10次且重要性>0.7的episodes触发蒸馏(consolidation)。

###Procedural Memory: How To Act

这是最古老、最自动化的记忆形式——骑车不会忘记怎么骑车。对AI，procedural memory是function definitions、agent loops、prompt templates和工具调用模式。

```python
# Procedural memory: stored action patterns
PROCEDURAL_STORE = {
    "web_search": {
        "trigger": "user asks about current events or facts",
        "action": "invoke search API with query extraction",
        "fallback": "ask user to rephrase question"
    },
    "code_execution": {
        "trigger": "user asks to run code or analyze data",
        "action": "spin up sandbox, execute, return output",
        "fallback": "explain limitations of execution environment"
    }
}
```

强化学习里的policy gradient就是procedural memory的机器版本。Agent通过梯度更新改变行为模式，这些更新直接编码在模型权重里——不是在context里， 是模型本身。

##Why Flat Memory Architecture Fails

平坦记忆是大多数简单RAG系统的做法：**把所有文档塞进一个向量索引，检索时做相似度搜索，返回top-k结果拼进context**。

这套方案有三个致命缺陷。

**第一个缺陷：语义密度不均。** 一次一小时的对话，前5分钟和最后5分钟 embedding 可能完全不相关——用户在不同时间讨论完全不同的话题。Top-k检索无法捕捉这种多主题结构。

**第二个缺陷：检索质量与上下文相关。** 用户问"上次我们讨论的那个问题"——这个query的embedding可能与当时讨论的embedding不在同一语义空间。跨session检索是平坦系统的死穴。

**第三个缺陷：无法区分时效性。** 两篇文档，一篇写于2020年，一篇写于2024年。向量相似度不考虑时间。用户的保险政策在2023年变了，RAG系统不知道。

层次架构解决了这三个问题：

```
Flat Memory:
[Doc1] [Doc2] [Doc3] ... [DocN]  →  retrieve top-k →  context
                                   ↑ random access, no structure

Hierarchical Memory:
Sensory → Working → Episodic → Semantic → Procedural
   ↑          ↑         ↑          ↑           ↑
   │          │         │          │           │
   └──────────┴──────────┴──────────┴───────────┘
   Cross-layer inference: retrieval propagates up
   Temporal awareness: episodic layer tracks recency
   Priority: importance scores gate access at each layer
```

每层有明确的职责边界。Sensory处理原始输入，Working维持当前焦点，Episodic存储事件序列，Semantic抽象知识，Procedural定义行为。三星半导体在内部AI助手里用这套架构，对话连贯性比flat RAG高67%（内部数据，2024年）。

##Implementing Memory Hierarchy: Letta And MemGPT

###Letta's Approach

Letta（原名 MemGPT）构建了一套生产级的记忆层次系统。它的核心是**记忆虚拟化**：把长期记忆当作外部存储，用 streaming 方式管理。

```
Letta Memory Architecture:

User Input
    ↓
[Sensory Buffer] ←── ephemeral, 500ms TTL
    ↓
[Working Context] ←── context window, LLM direct access
    ↓
[Episodes Store] ←── PostgreSQL + pgvector
    ↓
[Core Memory] ←── semantic facts, knowledge graph
    ↓
[Procedural Memory] ←── system prompts, function defs
```

Letta的创新是**分层召回(layzed recall)**：不每次都查询所有层。根据query type决定访问深度。简单的事实查询直接走 semantic；需要上下文的复杂推理才会触发 episodic 检索。召回延迟从平均 340ms 降到 89ms。

关键API端点：
- `POST /v1/memory/ingest` — 写入 sensory/episodic
- `GET /v1/memory/search` — 多层检索
- `POST /v1/memory/consolidate` — 把 episodic 蒸馏到 semantic

###MemGPT's Memory Tiers

MemGPT（University of伯克利, 2024）更偏向研究系统。它的核心思想是**virtual memory abstraction**：把LLM的上下文当作寄存器，把外部存储当作RAM/ROM。

```
MemGPT Memory Hierarchy:

Tier 0 (Context Register)
  - LLM attention window
  - Direct read/write, O(1) access
  - Capacity: ~128K tokens (GPT-4)

Tier 1 (Primary Memory / RAM)
  - Working context summaries
  - Recent episodic buffer
  - Capacity: ~1M tokens equivalent
  - Latency: <10ms

Tier 2 (Secondary Memory / Storage)
  - Full conversation history
  - Archived episodes
  - Capacity: unlimited
  - Latency: 50-200ms (SSD)

Tier 3 (Archive / Cold Storage)
  - Semantic knowledge base
  - Fact store, long-term facts
  - Capacity: unlimited
  - Latency: 200-500ms
```

MemGPT的fifo思想：用队列管理 episodic 的进出。新 episode 入队；当队列满了，低重要性 episodes 被压缩成 summary 或推入 Tier 2。重要性由 LLM 自己判断——每次交互后，模型输出一个 importance score，决定这条记忆的命运。

##The Forgetting Curve: Why Your Ai Loses Context

艾宾浩斯1885年的实验定义了人类遗忘曲线：信息在24小时后只剩33%。AI系统有类似问题，但机制不同。

AI的遗忘是**容量危机**。上下文窗口满了，必须evict。Eviction策略决定什么被保留，什么被丢弃。

```
AI Forgetting Mechanisms:

1. Attention Dilution
   Context length ↑ → per-token attention ↓
   128K context: middle tokens get 15-20% attention weight

2. Retrieval Decay
   Older embeddings drift from original semantics
   6-month old vector: ~40% semantic drift measured

3. Consolidation Failure
   Episodic → Semantic distillation misses important details
   Estimated information loss: 15-25% per consolidation cycle
```

解决这个问题的工程手段：定期重新嵌入（re-embed）重要context；用 importance score 做主动eviction而不是被动FIFO；在semantic层维护一个"核心事实"摘要作为锚点。

##Practical Implementation Patterns

###Pattern 1: Multi-layer RAG

```
Query Flow:
User: "What happened in my meeting yesterday about the API redesign?"

Layer 1: Working Memory
  → Is this in current context? No.

Layer 2: Episodic Search
  → Semantic search: "meeting + API redesign + yesterday"
  → Returns: conversation with timestamp 2024-04-18 14:32
  → Latency: 45ms

Layer 3: Semantic Enrichment
  → Extract entities: "API redesign", "backend team"
  → Query knowledge graph for related context
  → Returns: project documentation link
  → Latency: 120ms

Final: Merge and respond
  → Combined context: episodic + semantic
  → Response grounded in both
```

###Pattern 2: Self-summary For Long Context

模型在长对话中定期输出摘要，这些摘要存入episodic层而非原始对话。这压缩了记忆占用，同时保留了关键信息。

```python
class SelfSummarizer:
    def should_summarize(self, context_length: int) -> bool:
        if context_length > 100_000:
            return True
        # Also trigger on topic shift
        if self.topic_drift_score() > 0.7:
            return True
        return False

    def summarize(self, conversation: list) -> str:
        prompt = f"""Summarize this conversation, preserving:
        - Key decisions made
        - Important facts mentioned
        - Open questions or follow-ups
        Format as bullet points, max 500 words."""

        summary = llm.generate(prompt)
        return summary
```

###Pattern 3: Priority-gated Access

每层记忆有一个重要性阈值。只有超过阈值的记忆才能被提升到更高层。这防止低价值信息污染核心记忆。

```
Importance Score Calculation:

score = α × relevance + β × recency + γ × frequency + δ × user_flag

α = 0.4 (relevance weight)
β = 0.2 (recency weight)
γ = 0.2 (frequency weight)
δ = 0.2 (user explicit flag)

Threshold: 0.65 (tuneable per use case)
Below threshold: store in episodic only
Above threshold: candidate for semantic promotion
```

##Architecture Diagram: Full Memory Pipeline

```
                    ┌─────────────────┐
                    │   USER INPUT    │
                    │  (text/audio/   │
                    │   image tokens) │
                    └────────┬────────┘
                             │
                             ▼
┌──────────────────────────────────────────────┐
│              LAYER 0: SENSORY                 │
│  Raw capture, ring buffer, 500ms TTL        │
│  No compression, full fidelity             │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              LAYER 1: WORKING                 │
│  Context window, attention focus, ~128K      │
│  Eviction: attention-weight based           │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              LAYER 2: EPISODIC               │
│  Conversation history, event sequences      │
│  Embedding: text-embedding-ada-002          │
│  Store: PostgreSQL + pgvector               │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              LAYER 3: SEMANTIC               │
│  Facts, concepts, knowledge graph          │
│  Consolidation: episodic → semantic        │
│  Importance gating: score > 0.65           │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              LAYER 4: PROCEDURAL            │
│  Function defs, policies, agent loops       │
│  Stored in: code + model weights           │
│  Update via: RLHF, fine-tuning             │
└──────────────────────────────────────────────┘
```

##What This Means For Your Agent

平坦记忆能让你快速上线，但三个月后你会有一个充满噪声、无法检索、上下文稀释严重的系统。你不需要从第一天就实现完整的五层架构，但需要从分层设计开始。

最小可行实现：
- Sensory: input logging without storage
- Working: context truncation with summary preservation
- Episodic: session-level conversation storage in vector DB
- Semantic: entity extraction and fact store
- Procedural: function definitions as code

这套最小实现的成本：PostgreSQL + pgvector实例（每月50美元），一个 embedding 服务（每月20美元），和大约两星期的开发时间。

回报是一个可以跨session记住用户偏好的Agent，一个在长对话中保持上下文的系统，一个知识随时间真正积累而非稀释的架构。

现在开始设计你的记忆层。

---



##Related Articles

- [Context windows vs memory](/blog/context-windows-vs-memory/)
- [AI memory management for LLMs](/blog/ai-memory-management-for-llms/)
- [Short-term memory for AI agents](/blog/short-term-memory-for-ai-agents/)
- [How memory works in HyperAgents](/blog/how-memory-works-in-hyperagents/)
- [State of AI agent memory 2026](/blog/state-of-ai-agent-memory-2026/)

##Faq

**Q: How is AI working memory different from human working memory?**

Human working memory holds roughly 7 chunks (Miller, 1956). AI working memory is a fixed context window with no intrinsic capacity limit, but attention mechanisms create soft limits—longer contexts dilute the importance of individual tokens. A 128K context window sounds infinite, but research shows model performance degrades non-linearly as length increases, with middle tokens receiving disproportionately low attention.

**Q: Can I implement memory hierarchy without a vector database?**

Yes. The minimum implementation uses a relational database (PostgreSQL/MySQL) for episodic storage with JSON columns for raw text. You lose embedding-based similarity search, but gain SQL query flexibility. For small-scale systems (< 1000 sessions/day), SQLite with JSON columns performs adequately. Upgrade path: add pgvector or Pinecone when retrieval quality becomes a bottleneck.

**Q: How often should I consolidate episodic to semantic memory?**

Consolidation frequency depends on memory pressure and quality requirements. Recommended triggers: (1) episodic store exceeds 10K entries, (2) session count above 1K, (3) retrieval latency exceeds 200ms p99. Between consolidations, the system should accumulate importance scores—this is what gates which episodes get promoted.

**Q: What happens when context window fills completely?**

Without hierarchical eviction, the system either crashes, truncates arbitrarily, or loses coherence. With hierarchy: working memory evicts to episodic (with summary), episodic evicts older sessions to semantic (summarized), semantic remains stable. The cascade ensures no hard failure—only gradual quality reduction as you move down the hierarchy.

**Q: How does MemGPT's tiered storage handle latency?**

MemGPT uses a two-tier SSD/RAM architecture with automatic migration. Hot data (recent episodes, core facts) stays in RAM with < 10ms access. Cold data (archived conversations, long-term knowledge) stays on SSD with 50-200ms access. The migration threshold is user-configurable, typically based on access frequency and explicit importance tags.

**Q: Is memory hierarchy necessary for single-turn interactions?**

No. Memory hierarchy becomes critical when you have: (1) multi-turn conversations exceeding 20 exchanges, (2) cross-session continuity requirements, (3) personalization that spans days or weeks. For simple single-turn or short-conversation use cases, a flat context approach is sufficient and simpler to implement.

**Q: How do you handle conflicting information in semantic memory?**

When two sources provide contradictory facts, rank by: (1) source reliability score, (2) recency, (3) confidence in original extraction. Store the conflict as a tagged pair rather than silently overwriting. Surface conflicts to users for explicit resolution when the confidence gap is below threshold. The system should never discard contradictory evidence—conflicts are often where the most interesting insights live.