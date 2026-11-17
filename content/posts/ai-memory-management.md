---
category: agent-memory
primary_query: llm memory
siblings:
- rag-vs-memory
- short-term-agent-memory
- agent-memory-2026
bridges:
- slug: claude-code-memory
  reason: A coding agent is the memory system a developer uses every day.
- slug: llm-inference-optimization
  reason: Sizing the KV cache is the inference-side limit on how much context a session can hold.
date: 2026-04-19
description: 'AI memory management for LLMs: the memory layers, who should decide what gets written, eviction and scope with runnable examples, and the smallest system worth building.'
status: published
work_note: "I'm Ninad Pathak, a freelance technical writer for AI companies that build agents, agent memory and LLM infrastructure. I write their tutorials and technical articles, and I run each product before I write about it. [Let's work on yours](/services/freelance-technical-writer-for-ai-companies/)."
title: "AI Memory Management for LLMs"
slug: ai-memory-management
video: ai-memory-management
updated: 2026-11-17
---

AI memory management for LLMs is the set of decisions about what an application writes down, which scope each fact belongs to, when it loads into the context window and when it is replaced or dropped. A context window is a buffer for one request, so anything that has to outlive the window or the session needs those decisions made on purpose.

The clearest account of what happens without them came from Drew Breunig, who is writing a handbook on context engineering. Breunig's [talk transcript, posted on October 24, 2026](https://www.dbreunig.com/2026/10/24/the-state-of-context-engineering.html), asks the audience who keeps memory switched on in ChatGPT or Claude and answers "I turn it off.", because with work and family projects in one account "The model will take notes on both, mix up those contexts, and the confusion grows from there."

Those decisions are the whole of [AI agent memory](/articles/agent-memory/), whatever store sits underneath.

## Memory hierarchy separates active context from persistent state

Memory in an LLM system lives in two places: state the application stores and retrieves, and state the model holds while it processes one request. The first is explicit memory, the second is the attention state kept in the KV cache, and retrieval over a document corpus is a separate job that the [RAG vs memory](/articles/rag-vs-memory/) comparison covers.

### Explicit and implicit memory solve different constraints

Explicit memory is whatever your application decides to keep between requests, such as session logs, extracted facts and notes a model wrote to a folder. Implicit memory is built inside a forward pass, and the only control you have over it is what you put in the context window.

Anthropic's [The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory), from November 6, 2026, draws the same line from the other side. It defines agent memory as knowledge retained between sessions and excludes compaction, which it describes as "summaries written by Claude that replace its older turns so it can continue working in a new context window".

The [Claude Code memory](/articles/claude-code-memory/) article shows one product's version of the explicit side.

Implicit memory is paid for in GPU memory, at 2 × layers × KV heads × head dimension × bytes per value for every token in the window. Meta's [Llama paper](https://arxiv.org/abs/2407.21783), from July 2024, lists 80 layers, a model dimension of 8,192, 64 attention heads and 8 key/value heads for its 70B model, which gives a head dimension of 128.

At 16-bit precision that is 2 × 80 × 8 × 128 × 2 bytes, or 327,680 bytes per token, so a 128,000-token context holds about 42 GB of attention state for one sequence. Serving engines manage that with paging, and the [PagedAttention paper](https://arxiv.org/abs/2309.06180) of September 2023, which introduced vLLM, reports "near-zero waste in KV cache memory".

That layer belongs to the serving engine, and the [LLM inference optimization guide](/articles/llm-inference-optimization/) covers sizing it. The application's lever is a smaller context, which is what the explicit layers are for.

### The five layers answer five memory questions

This page splits explicit memory into five layers: an input buffer, working context, episodic memory, semantic memory and procedural memory.

The last three names come from research on agent memory, and my page on the [types of agent memory](/articles/agent-memory-types/) says where each came from and how each is looked up.

| Layer | Question it answers | Typical lifetime |
| --- | --- | --- |
| Input buffer | What just arrived? | One step |
| Working context | What does the current step need? | One task |
| Episodic memory | What happened, and when? | Until superseded or expired |
| Semantic memory | What is known to be true? | Until a newer fact replaces it |
| Procedural memory | How should the agent act here? | Until the rule changes |

The [short-term memory guide](/articles/short-term-agent-memory/) covers the first two layers, and [agent memory in 2026](/articles/agent-memory-2026/) surveys products across all five.

### Inclusion, retrieval, and lifecycle need separate policies

An inclusion policy decides whether an observation leaves the input buffer at all. A tool's progress message can expire with the step, and a user-approved deployment constraint deserves an attributed record.

A retrieval policy filters by subject, scope and time before it ranks by similarity. A lifecycle policy covers supersession, expiry, eviction and deletion, and it should keep a path back to the original record when a summary might support a consequential decision.

## Who should decide what gets written?

With a frontier model, the model should decide what to write and the application should decide scope and lifecycle. Anthropic's post says "it helps to tell Claude what memory is for, but not how to use it", and its evidence is a rule test on the CL-Bench benchmark.

When the researchers imposed a fixed rule to record only failures, "both Opus 5 and Opus 4.7 lost much of the performance boost that memory gave them". The same post reports the opposite for an older model: prompting Sonnet 4.6 to read its memory files and test its theories "nearly doubled its benchmark score".

My reading is that hand-written write rules belong with smaller or older models and with stores no model curates. Anthropic's post doesn't test that directly: it shows a fixed rule hurting strong models and steering helping a weaker one read and test its notes.

The earlier version of this page presented scoring every entry as the default, and for current frontier models the sources no longer support that.

What stays with the application in every case is the part a model can't see from inside one session: which user and project a fact belongs to, what it replaces, and who can read it back.

## Eviction, compression and retention decide what stays

Retention should protect what a person asked the system to keep, let recency sort the rest, and compress before it deletes. Least recently used (LRU) eviction alone fails for agents because the fact that matters is often the oldest one in the buffer.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/ai-memory-management/memory-operations.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/ai-memory-management/memory-operations.narrow.svg" width="288" height="744"><img class="np-has-narrow" src="/static/images/diagrams/ai-memory-management/memory-operations.svg" width="720" height="520" alt="A new turn arrives in a full context window, and the memory layer has three moves: prioritize what a person asked to keep so those records stay, compress older records into a smaller summary, or evict the lowest-value records from memory entirely." loading="lazy" decoding="async"></picture></a>
  <figcaption>Keeping what someone asked for, compressing older records and evicting the rest are separate policies, and each fails in its own way.</figcaption>
</figure>

The example below runs the same four-entry session twice through a buffer one slot too small. The deployment region is written first and marked as pinned, which is the "remember this" case, and the greeting is touched again before the last write.

```python
from collections import OrderedDict


class Buffer:
    """A bounded memory buffer. Pinned entries are never evicted."""

    def __init__(self, capacity, respect_pins):
        self.capacity = capacity
        self.respect_pins = respect_pins
        self.entries = OrderedDict()  # key -> (text, pinned), least recently used first

    def put(self, key, text, pinned=False):
        if key not in self.entries and len(self.entries) >= self.capacity:
            self._evict()
        self.entries[key] = (text, pinned)
        self.entries.move_to_end(key)

    def touch(self, key):
        self.entries.move_to_end(key)

    def _evict(self):
        for key, (_, pinned) in self.entries.items():
            if not (self.respect_pins and pinned):
                del self.entries[key]
                return
        raise RuntimeError("every entry is pinned; raise capacity or unpin something")


def session(buffer):
    buffer.put("region", "Deploy region is eu-west-1", pinned=True)
    buffer.put("greeting", "User said good morning")
    buffer.put("weather", "User mentioned rain")
    buffer.touch("greeting")  # the small talk comes up again
    buffer.put("lunch", "User is back from lunch")
    return list(buffer.entries)


print("plain LRU:  ", session(Buffer(capacity=3, respect_pins=False)))
print("with pins:  ", session(Buffer(capacity=3, respect_pins=True)))

full = Buffer(capacity=1, respect_pins=True)
full.put("region", "Deploy region is eu-west-1", pinned=True)
try:
    full.put("lunch", "User is back from lunch")
except RuntimeError as error:
    print("all pinned: ", error, "| still holds", list(full.entries))
```

Running it with `python3 mem_evict.py` prints which entries survive.

```text
plain LRU:   ['weather', 'greeting', 'lunch']
with pins:   ['region', 'greeting', 'lunch']
all pinned:  every entry is pinned; raise capacity or unpin something | still holds ['region']
```

Plain LRU kept the small talk, because it had been used more recently, and dropped the region. The pinned version kept the region, and when every slot is pinned it refuses the new write and leaves the buffer as it was, which is the signal to raise capacity.

Compression is the step before deletion. It keeps a shorter stand-in for older material, and summarizing old turns is the common form, the one Anthropic's definition of compaction above describes.

Anthropic's [compaction documentation](https://platform.claude.com/docs/en/build-with-claude/compaction) gives the reason to do it early: it "keeps the active context small, because response quality degrades as a conversation grows." A summary of a summary loses detail the next pass can't recover, so keep the original record or a pointer to it.

Vector stores have their own version in [product quantization](/glossary/product-quantization/), which stores smaller approximate vectors and gives up some precision in what similarity search returns.

## Letta and MemGPT make memory tiers explicit

Letta, the project its [repository](https://github.com/letta-ai/letta) says was formerly known as MemGPT, names the tiers as memory blocks, stored messages and archival memory. Its [documentation](https://docs.letta.com/guides/agents/memory) says attached memory blocks "are in-context (pinned to the system prompt)", and that the agent edits them through memory tools.

Messages that fall out of the window are kept: "The Letta API stores all messages, so even after a compaction / eviction, an agent's old messages are still retrievable". The third tier is [archival memory](https://docs.letta.com/guides/agents/archival-memory), "a semantically searchable database where agents can store facts, knowledge, and information for long-term retrieval."

Other frameworks draw the tiers in different places, and the [DeerFlow](/articles/deerflow-memory/), [HyperAgents](/articles/hyperagents-memory/) and [voice agent](/articles/voice-agent-memory/) memory articles walk through other designs.

## Forgetting has four distinct failure modes

Memory fails by not finding a fact, by attaching it to the wrong scope, by keeping it after it stopped being true, or by loading facts that contradict each other.

| Failure | What it looks like | Guard |
| --- | --- | --- |
| Retrieval | The fact exists and the query never surfaces it | Filter by scope and time before similarity |
| Scope | A work detail appears in a personal chat | Address every fact by user and project |
| Temporal decay | An expired fact is still returned as current | Supersede on write, and expire what nobody confirms |
| Contamination | Incompatible facts load together | Keep one current value per key, with history kept apart |

Breunig's complaint is the scope failure. The store below addresses each fact by scope and key, replaces a value when a newer one arrives, and keeps what it replaced in a separate history.

```python
from datetime import date


class MemoryStore:
    """Facts are addressed by (scope, key). A new write supersedes the old one."""

    def __init__(self):
        self.current = {}
        self.history = []

    def write(self, scope, key, value, source, on):
        old = self.current.get((scope, key))
        if old:
            self.history.append({**old, "superseded_on": on})
        self.current[(scope, key)] = {"scope": scope, "key": key, "value": value, "source": source, "written_on": on}

    def read(self, scope):
        return {key: fact["value"] for (s, key), fact in self.current.items() if s == scope}


store = MemoryStore()
store.write("work/billing-api", "database", "Postgres 15", "session 12", date(2026, 9, 1))
store.write("home/robot-kit", "language", "MicroPython", "session 13", date(2026, 9, 2))
store.write("work/billing-api", "database", "Postgres 17", "session 40", date(2026, 11, 3))

print("work scope:", store.read("work/billing-api"))
print("home scope:", store.read("home/robot-kit"))
print("superseded:", [(h["value"], str(h["superseded_on"])) for h in store.history])
```

Running it with `python3 mem_scope.py` shows each scope reading only its own facts.

```text
work scope: {'database': 'Postgres 17'}
home scope: {'language': 'MicroPython'}
superseded: [('Postgres 15', '2026-11-03')]
```

A note can also be wrong from the moment it is written, which no write rule catches. Anthropic's post describes a repair pass that checks notes against the original transcripts, and Breunig expects the problem to grow: "Over time, overly precise memories become conflicted and messy, and nobody has yet figured out how to handle this."

## A practical implementation starts with session state

Build the smallest version in this order, and add a layer only when its absence causes a failure you can name.

1. **Store session state explicitly.** Keep the conversation in a session store and inject it each turn.
2. **Scope every durable fact.** Address facts by user and project before you store the first one.
3. **Let the model write, and tell it why.** Give a frontier model a memory folder and a statement of what memory is for.
4. **Supersede on write.** Replace the current value and keep the old one in history.
5. **Add eviction before the first long session.** Protect what users asked to keep, and let recency sort the rest.
6. **Make the store readable.** Someone has to be able to see what was saved and delete it.

## FAQ

**How does context window size affect memory management decisions?**

A larger window delays the point where something has to be dropped, and it does not decide what is still true or whose fact it is. The KV cache cost also grows with every token kept in the window.

**What is the difference between memory and context?**

Context is what the model reads during one request. Memory is state the application keeps across requests and chooses to load into that context.

**How often should memory entries be summarized?**

Summarize before the context is full, on a trigger you choose. Anthropic's compaction documentation describes two modes, on demand and "when input tokens reach the trigger you set", and recommends "Use on-demand compaction wherever it is available."

**Can I use Redis for LLM memory management?**

Yes. A key-value store is enough for session state and for scoped facts like the example above, and for similarity retrieval Redis's [vector search documentation](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/) says "Redis stores vectors and metadata in hashes or JSON objects" and "Redis supports FLAT, HNSW and SVS-VAMANA vector index types."

**How do I prevent my agent from retrieving contradictory memories?**

Keep one current value per scope and key, supersede on write, and store history apart from what gets loaded. The `MemoryStore` example above is that pattern in its smallest form.

**What causes the "hallucinated memory" problem where the agent invents facts?**

A model asked to recall something with no stored record can produce a plausible one. Verify recalled claims against stored evidence before accepting them, because prompt wording alone cannot establish whether an interaction happened.
