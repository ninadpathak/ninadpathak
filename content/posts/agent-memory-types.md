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

So the type you're storing comes before the store you pick, in any design for [AI agent memory](/articles/agent-memory/).

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-memory-types/memory-types.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-memory-types/memory-types.narrow.svg" width="288" height="624"><img class="np-has-narrow" src="/static/images/diagrams/agent-memory-types/memory-types.svg" width="720" height="288" alt="Working, episodic, semantic and procedural memory side by side. Working memory is the context window, and it lasts until the session ends or the window is compacted. Episodic memory is the record of what happened across sessions, kept in time order. Semantic memory holds what is true, such as a fact about the user. Procedural memory holds the rules the agent acts by, such as its system prompt." loading="lazy" decoding="async"></picture></a>
  <figcaption>Working memory is the context window. Episodic memory keeps what happened, semantic memory keeps what is true, and procedural memory keeps the rules the agent acts by.</figcaption>
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

Because a question about events is usually a question about time, and similarity search doesn't know what time it is. The script below asks one question of a five-line event log I wrote for the purpose, by meaning in several wordings and then by time.

```python
"""Ask one question of the same event log by meaning, in three wordings, then by time."""
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
QUESTIONS = [
    "What did you change in the last hour?",
    "What did you modify in the last hour?",
    "What did you do in the last hour?",
]

model = TextEmbedding("BAAI/bge-small-en-v1.5")


def embed(texts):
    vectors = np.array(list(model.embed(texts)))
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def age(when):
    delta = NOW - when
    return f"{delta.days} days" if delta.days else f"{int(delta.total_seconds() // 60)} min"


events = embed([text for _, text in EVENTS])
print("by meaning (a semantic lookup), all five scores for each wording:")
for question in QUESTIONS:
    scores = events @ embed([question])[0]
    print(f"\n  {question}  spread {scores.max() - scores.min():.3f}")
    for i in np.argsort(-scores):
        when, text = EVENTS[i]
        print(f"    {scores[i]:.3f}  {age(when):>7} ago  {text}")

print("\nby time, last 60 minutes (an episodic lookup):")
for when, text in EVENTS:
    if NOW - when <= timedelta(hours=1):
        print(f"    {age(when):>7} ago  {text}")
```

Run on November 17, it printed this.

```text
by meaning (a semantic lookup), all five scores for each wording:

  What did you change in the last hour?  spread 0.034
    0.592  12 days ago  Changed the request timeout from 30s to 60s in config.yaml
    0.581   3 days ago  Changed the log level from INFO to DEBUG in config.yaml
    0.580   50 min ago  Deleted the stale feature flag for the old checkout page
    0.577   20 min ago  Renamed the billing worker queue to invoices
    0.558  41 days ago  Changed the database pool size from 10 to 25 in config.yaml

  What did you modify in the last hour?  spread 0.030
    0.590   50 min ago  Deleted the stale feature flag for the old checkout page
    0.589  12 days ago  Changed the request timeout from 30s to 60s in config.yaml
    0.589   3 days ago  Changed the log level from INFO to DEBUG in config.yaml
    0.585   20 min ago  Renamed the billing worker queue to invoices
    0.560  41 days ago  Changed the database pool size from 10 to 25 in config.yaml

  What did you do in the last hour?  spread 0.048
    0.490   20 min ago  Renamed the billing worker queue to invoices
    0.486  12 days ago  Changed the request timeout from 30s to 60s in config.yaml
    0.485   50 min ago  Deleted the stale feature flag for the old checkout page
    0.484   3 days ago  Changed the log level from INFO to DEBUG in config.yaml
    0.441  41 days ago  Changed the database pool size from 10 to 25 in config.yaml

by time, last 60 minutes (an episodic lookup):
     50 min ago  Deleted the stale feature flag for the old checkout page
     20 min ago  Renamed the billing worker queue to invoices
```

Read the scores before the order. The five events, from 20 minutes to 41 days old, score within 0.05 of each other on every wording, so the ranking among them is close to noise.

And the order changes with one word of the question. "Change" puts a 12-day-old edit first, "modify" puts a 50-minute-old one first by 0.001, and "do" puts the newest first.

So similarity carries no signal about time here. The time lookup returns the two events from the last hour on every wording, because it never reads the words.

I wrote the log, and it's five lines against one small model, so it shows a mechanism and no rate. But the mechanism is general: episodes want an index on time or session, and facts want an index on meaning.

[RAG vs memory](/articles/rag-vs-memory/) goes further into how the two differ.

## Where does procedural memory fit?

It's the part people forget to call memory. Procedural memory holds the instructions the agent follows, which for a language-model agent means the system prompt and the code around it.

An agent that edits its own instructions after a correction is writing to procedural memory.

That's the riskiest write, since a bad rule changes every later run. The paper calls it significantly riskier than writing to episodic or semantic memory.

## How does each type fail?

Each type fails in a way you can recognise, and a single store hides which one you're looking at.

- **Working memory** fails by loss. The agent forgets a constraint from early in a long session.
- **Episodic memory** fails by contradiction. The agent says it finished something it never ran.
- **Semantic memory** fails by confidence. The agent states an outdated fact as current.
- **Procedural memory** fails by repetition. The agent makes one mistake on every run, because the mistake is a rule.

The layered design in [AI memory management](/articles/ai-memory-management/) keeps them apart from the start.

## FAQ

**What are the types of agent memory?**

Working memory, which is the context window, and three long-term types: episodic memory for past events, semantic memory for facts and procedural memory for the rules the agent follows.

**Is semantic memory the same as semantic search?**

No. Semantic memory is stored knowledge, and semantic search is a way of finding text by meaning, so a store of facts is semantic memory however you search it.

**Which memory type should an agent have first?**

Start with working memory managed well, then add semantic memory for facts that must survive a session. Add episodic memory when the agent has to answer questions about what it did.
