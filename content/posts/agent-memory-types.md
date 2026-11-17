---
category: agent-memory
primary_query: types of agent memory
siblings:
- rag-vs-memory
- ai-memory-management
bridges:
- slug: llm-context-windows
  reason: Working memory is the context window, and that page covers what the window can hold.
date: '2026-05-04'
description: 'The types of agent memory are working, episodic, semantic and procedural. What each holds, where the names come from, and a run showing why the type decides the lookup.'
slug: agent-memory-types
status: published
work_note: "I'm Ninad Pathak, and I freelance as a technical writer for AI companies. I build the example and run it before I draft a tutorial, so your engineers review working code. [Here's how we'd work together](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Types of AI Agent Memory'
updated: 2026-11-17
---

The types of agent memory are working memory, which is what the model can see right now, and three kinds of long-term memory: episodic for what happened, semantic for what is true, and procedural for how to act. The split comes from a 2023 paper, [Cognitive Architectures for Language Agents](https://arxiv.org/abs/2309.02427), which borrowed it from older work on human and machine cognition.

The two middle names are older still. Endel Tulving coined [episodic memory](https://en.wikipedia.org/wiki/Episodic_memory) in 1972 to separate remembering an event from knowing a fact.

An agent needs the same separation for a practical reason. An event and a fact get looked up in different ways, and a store built for one answers badly for the other.

That choice of store is the first design decision in [AI agent memory](/articles/agent-memory/).

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-memory-types/memory-types.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-memory-types/memory-types.narrow.svg" width="288" height="488"><img class="np-has-narrow" src="/static/images/diagrams/agent-memory-types/memory-types.svg" width="720" height="288" alt="Working, episodic, and semantic memory side by side. Working memory is the scratchpad for the current turn, backed by the context window and gone when the turn ends. Episodic memory is the agent's autobiographical record of what happened across sessions, such as a task that failed on Friday with a given error, kept in an event store in time order. Semantic memory holds what is true, such as the fact that list.sort() is stable, in a durable knowledge base." loading="lazy" decoding="async"></picture></a>
  <figcaption>Working memory holds the current turn, episodic memory keeps what happened in order across sessions, and semantic memory holds facts until they stop being true.</figcaption>
</figure>

## What are the types of agent memory?

There are four: working memory, which is short-term, and the long-term types episodic, semantic and procedural. The paper defines them for agents built on language models, and LangGraph's [memory documentation](https://docs.langchain.com/oss/python/langgraph/memory) gives each long-term type a plain example.

| Type | What it holds | An agent example |
| --- | --- | --- |
| Working | What's active in the current decision: inputs, goals, intermediate results | The context window during a task |
| Episodic | Experiences from earlier runs | A log of past actions and how they turned out |
| Semantic | Facts about the world and the user | "The user deploys on Fridays" |
| Procedural | The rules the agent acts by | The system prompt and the agent's own code |

Product names don't always follow the table. A feature called memory in one tool may store only facts, and in another only a history of sessions.

## What is working memory in an agent?

It's the context window. Everything the model can use on this turn is there, and nothing else is.

So working memory is fast, complete and temporary. When the session ends or the window is compacted, whatever wasn't written somewhere else is gone, which is the limit my page on [context windows](/articles/llm-context-windows/) covers.

Long-term memory is the "somewhere else". The long-term types differ in what gets written and in how it's read back.

## What is the difference between episodic and semantic memory?

Episodic memory records events and semantic memory records facts. "The deploy on Friday failed on a migration timeout" is an episode, and "migrations on this database need a longer timeout" is the fact someone drew from it.

The paper puts the two writes side by side, and LangGraph's docs repeat it: experiences go to episodic memory, and facts go to semantic memory. An agent that reflects on its episodes can turn them into facts.

The name hides a trap. LangGraph's docs point out that semantic memory is a term from psychology for stored knowledge, and semantic search is a retrieval method, so a vector index doesn't make a store semantic memory.

## Why does the memory type decide the lookup?

Because a question about events is usually a question about time, and similarity search doesn't know what time it is. The script below asks one question of a five-line event log I wrote for the purpose, first by meaning and then by time.

```python
"""Ask one question of the same event log two ways: by meaning, and by time."""
from datetime import datetime, timedelta

import numpy as np
from fastembed import TextEmbedding

NOW = datetime(2026, 11, 17, 15, 0)
EVENTS = [
    (NOW - timedelta(days=41), "Changed the database pool size from 10 to 25 in config.yaml"),
    (NOW - timedelta(days=12), "Changed the request timeout from 30s to 60s in config.yaml"),
    (NOW - timedelta(days=3), "Changed the log level from INFO to DEBUG in config.yaml"),
    (NOW - timedelta(minutes=50), "Deleted the stale feature flag for the old checkout page"),
    (NOW - timedelta(minutes=20), "Renamed the billing worker queue to invoices"),
]
QUESTION = "What did you change in the last hour?"

model = TextEmbedding("BAAI/bge-small-en-v1.5")


def embed(texts):
    vectors = np.array(list(model.embed(texts)))
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


scores = embed([text for _, text in EVENTS]) @ embed([QUESTION])[0]
print(QUESTION)
print("\nby meaning, top 2 of 5 (a semantic lookup):")
for i in np.argsort(-scores)[:2]:
    when, text = EVENTS[i]
    print(f"  {scores[i]:.3f}  {(NOW - when).days:>2} days ago  {text}")

print("\nby time, last 60 minutes (an episodic lookup):")
for when, text in EVENTS:
    if NOW - when <= timedelta(hours=1):
        print(f"  {int((NOW - when).total_seconds() // 60)} min ago  {text}")
```

Run on November 17, it printed this.

```text
What did you change in the last hour?

by meaning, top 2 of 5 (a semantic lookup):
  0.592  12 days ago  Changed the request timeout from 30s to 60s in config.yaml
  0.581   3 days ago  Changed the log level from INFO to DEBUG in config.yaml

by time, last 60 minutes (an episodic lookup):
  50 min ago  Deleted the stale feature flag for the old checkout page
  20 min ago  Renamed the billing worker queue to invoices
```

The similarity lookup returned two old config edits, because they share the word "changed" with the question. The time lookup returned the two things that happened in the last hour, neither of which uses that word.

I wrote the log to make the effect plain, so it shows the mechanism and says nothing about how often it bites. But the mechanism is general: episodes want an index on time or session, and facts want an index on meaning.

How retrieval and memory differ beyond that is the subject of [RAG vs memory](/articles/rag-vs-memory/).

## Where does procedural memory fit?

It's the part people forget to call memory. Procedural memory holds the instructions the agent follows, which for a language-model agent means the system prompt and the code around it.

An agent that edits its own instructions after a correction is writing to procedural memory.

That's the riskiest write, since a bad rule changes every later run. The paper calls it significantly riskier than writing to episodic or semantic memory.

## How does each type fail?

Each fails in its own recognisable way, which is the practical reason to keep them apart.

- **Working memory** fails by loss. The agent forgets a constraint from early in a long session.
- **Episodic memory** fails by contradiction. The agent says it finished something it never ran.
- **Semantic memory** fails by confidence. The agent states an outdated fact as current.
- **Procedural memory** fails by repetition. The agent makes one mistake on every run, because the mistake is a rule.

A single store hides which of these you're looking at. The layered design in [AI memory management](/articles/ai-memory-management/) keeps them apart from the start.

## FAQ

**What are the types of agent memory?**

Working memory, which is the context window, and three long-term types: episodic memory for past events, semantic memory for facts and procedural memory for the rules the agent follows.

**Is semantic memory the same as semantic search?**

No. Semantic memory is stored knowledge, and semantic search is a way of finding text by meaning, so a fact store can be searched by key and an event log by meaning.

**Which memory type should an agent have first?**

Start with working memory managed well, then add semantic memory for facts that must survive a session. Add episodic memory when the agent has to answer questions about what it did.
