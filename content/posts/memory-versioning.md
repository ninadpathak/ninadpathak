---
category: ai-engineering
date: '2026-05-05'
description: 'How to make agent memory auditable: append-only versions, a source for every write and a hash chain, with a runnable SQLite ledger and its output.'
slug: memory-versioning
status: published
work_note: 'I ran the writers at a memory vendor, Mem0, and here I take the question an auditor would ask of any such product: what did the agent know when it decided? The case study is [in my portfolio](/portfolio/).'
title: Memory Versioning and Audit Trails for Regulated AI Agents
updated: 2026-11-17
---

An auditor asks two things about any decision an agent made: what the agent knew at that moment, and what put each fact there. Memory versioning is how a store answers, by keeping every version of a fact with the time it held and the source that produced it, and never overwriting one.

The same demand is showing up in tools for coding agents. Stroq, shown on Hacker News on November 5, scans an agent's sessions and promises to ["trace risky commands to the content that dictated them"](https://github.com/AGGIB/Stroq).

## How do you make agent memory auditable?

Agent memory is auditable when it has an append-only history, a source for every write and a way to detect edits. With those in place you can reconstruct what the agent knew at any moment and show where each fact came from.

The parts map to questions an auditor asks.

| Question | What the store needs |
| --- | --- |
| What did the agent know on that date? | Every version kept, with the times it was valid |
| Why did it believe that? | A source recorded with each write |
| Has the record been changed since? | A hash that chains each row to the one before |

## Why does overwriting memory break an audit?

An overwrite destroys the state that explains earlier decisions. Suppose an advisory agent stores `risk tolerance: low` for a user, recommends bonds, and two weeks later replaces the value with `high` after a new conversation.

A reviewer who asks why the agent recommended bonds finds a store that says the user's tolerance is high. The recommendation now looks like an error, and nothing in the database can show otherwise.

Software has had the remedy for a long time. Martin Fowler's [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html), dated December 12, 2005, describes it as ensuring "that all changes to application state are stored as a sequence of events", so that "we can also use the event log to reconstruct past states".

## What does an append-only memory ledger look like?

It is a table in which each change adds a row, the previous row is closed with an end time, and each row carries a hash of its content and of the row before. The version below runs on Python's standard library.

```python
"""An append-only memory ledger in SQLite: as-of queries and a tamper check."""
import hashlib
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("""create table memory (
    id integer primary key, entity text, fact text, source text,
    valid_from text, valid_to text, prev_hash text, hash text)""")


def digest(prev_hash, entity, fact, source, valid_from):
    return hashlib.sha256("|".join([prev_hash, entity, fact, source, valid_from]).encode()).hexdigest()


def write(entity, fact, source, at):
    """Close the current row for this entity, then append the new one."""
    db.execute("update memory set valid_to = ? where entity = ? and valid_to is null", (at, entity))
    last = db.execute("select hash from memory order by id desc limit 1").fetchone()
    prev_hash = last[0] if last else ""
    db.execute("insert into memory (entity, fact, source, valid_from, prev_hash, hash) values (?,?,?,?,?,?)",
               (entity, fact, source, at, prev_hash, digest(prev_hash, entity, fact, source, at)))


def as_of(entity, at):
    return db.execute("""select fact, source from memory where entity = ? and valid_from <= ?
                         and (valid_to is null or valid_to > ?)""", (entity, at, at)).fetchone()


def verify():
    prev_hash = ""
    for row in db.execute("select id, entity, fact, source, valid_from, prev_hash, hash from memory order by id"):
        if row[5] != prev_hash or row[6] != digest(prev_hash, *row[1:5]):
            return f"chain broken at row {row[0]}"
        prev_hash = row[6]
    return "chain intact"


write("user-17:risk", "risk tolerance is low", "turn 4: 'I can't afford to lose this money'", "2026-11-03T10:00")
write("user-17:risk", "risk tolerance is high", "turn 31: 'put some of it into crypto'", "2026-11-12T16:30")

print("as of Nov 10:", as_of("user-17:risk", "2026-11-10T09:00"))
print("as of Nov 14:", as_of("user-17:risk", "2026-11-14T09:00"))
print("rows kept:", db.execute("select count(*) from memory").fetchone()[0])
print(verify())

db.execute("update memory set fact = 'risk tolerance is high' where id = 1")
print("after editing row 1 in place:", verify())
```

Running `python3 memory_ledger.py` printed this.

```text
as of Nov 10: ('risk tolerance is low', "turn 4: 'I can't afford to lose this money'")
as of Nov 14: ('risk tolerance is high', "turn 31: 'put some of it into crypto'")
rows kept: 2
chain intact
after editing row 1 in place: chain broken at row 1
```

The first two lines are the audit answer: on November 10 the agent believed the user's tolerance was low, and the stored source says why. The last line shows the chain catching an edit made directly in the database.

A single mutation is left in the design. Closing a row sets its `valid_to`, which is outside the hash, so the content of a row can't change unnoticed and its end time can.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/memory-versioning/append-vs-overwrite.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/memory-versioning/append-vs-overwrite.narrow.svg" width="288" height="1000"><img class="np-has-narrow" src="/static/images/diagrams/memory-versioning/append-vs-overwrite.svg" width="720" height="544" alt="Two ways to change a memory. The append-only ledger inserts a new row and stamps the old one as superseded, so v1, v2, and v3 all remain and any point in time can be recovered. A destructive update overwrites the row: v2 replaces v1, and the prior state is gone." loading="lazy" decoding="async"></picture></a>
  <figcaption>Inserting a new row and stamping valid_to on the old one gives point-in-time recovery for free.</figcaption>
</figure>

## How do you link a memory to the reasoning behind it?

Record the source at write time, as a required field, because it can't be recovered afterwards. The `source` column in the ledger above holds the turn and the words that justified the fact.

Where the model writes memory through a tool, make the tool's source parameter required, so a write without one is rejected by the schema. A fact with no source is one nobody can tell apart from an inference the model made out of a passing remark.

Stroq advertises that property for commands, and it matters more for memory, since a stored fact is reused. A wrong command runs once, and a wrong memory is loaded as true in every later session until someone traces it.

## What does a regulator ask for?

The clearest written requirement I know of is in the EU AI Act, adopted in 2024. [Article 12](https://artificialintelligenceact.eu/article/12/) says "High-risk AI systems shall technically allow for the automatic recording of events (logs) over the lifetime of the system."

The article is about high-risk systems and about event logs, and it doesn't mention agent memory. My reading is that a memory write is an event that changes what the system will do next, so a team under that rule should want it in the record.

## How do you audit a vector database?

Keep the ledger as the record and treat the vector index as a copy that can be rebuilt from it. A vector index has no notion of which version of a fact is current, so that knowledge has to come from the table.

A pair of rules follows from that, and both are design choices on my part. Only rows with no `valid_to` are embedded for retrieval, so a superseded fact can't outrank the current one, and the index is rebuilt from the ledger when the two disagree.

Frameworks separate the same two concerns. LangGraph's [persistence documentation](https://docs.langchain.com/oss/python/langgraph/persistence) says its layer "gives agents short-term memory through checkpointers and long-term memory through stores", and the versioning described here applies to the second kind.

Version history is useful only if state survives a restart in a readable form, which the guide to [serializing agent memory between sessions](/articles/memory-serialization/) covers.

## What does versioning cost?

It costs storage and a filter on every read. A fact occupies one row for every version it has had, and every query has to say whether it wants the current row or the row for a past date.

Both costs are small beside the cost of the question it answers. A team that can't say what its agent knew last month can't debug it either, which makes the ledger worth having with or without a regulator.

## FAQ

**Doesn't keeping every version risk confusing the agent?**

Only if old versions reach the prompt. Retrieval should read current rows, and the history is for people and for audits.

**Can I use git for this?**

For a single agent that keeps its memory as files, yes, since commits give versions and sources in the commit message. A database ledger fits better when many users or agents write at once.

**Is the hash chain necessary?**

It is necessary when someone outside the team has to trust the record. Inside a team, the append-only rule and database permissions cover the common case, and the chain adds proof that nobody edited a row.
