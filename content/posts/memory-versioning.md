---
category: agent-memory
primary_query: agent memory audit trail
siblings:
- memory-serialization
- ai-memory-management
date: '2026-05-05'
description: 'Memory versioning and audit trails for AI agents: append-only versions, a source for every write, and a hash chain anchored outside the database.'
slug: memory-versioning
status: published
work_note: "I'm Ninad Pathak, a freelance technical writer. If your AI product's tutorials have fallen behind the product, I write them, and I run the product first. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: Memory Versioning and Audit Trails for Regulated AI Agents
updated: 2026-11-17
---

An auditor asks two things about any decision an agent made: what the agent knew at that moment, and what put each fact there. Memory versioning is how a store answers, by keeping every version of a fact with the time it held and the source that produced it, and never overwriting one.

Memory versioning is the part of [AI agent memory](/articles/agent-memory/) built for people outside the team, such as auditors.

Tools for coding agents are starting to ask a similar question about commands. Stroq, shown on Hacker News on November 5, scans an agent's sessions and promises to ["trace risky commands to the content that dictated them"](https://github.com/AGGIB/Stroq), and I use it here only as an analogy, since it guards against prompt injection and stores no memory.

## How do you make agent memory auditable?

Agent memory is auditable when it has an append-only history, a source for every write, and a copy of its newest hash held where the database's editors can't reach. With those in place you can reconstruct what the agent knew at any moment, show where each fact came from, and tell whether the record was changed afterwards.

| Auditor's question | What the store needs |
| --- | --- |
| What did the agent know on that date? | Every version kept, with the time it took effect |
| Why did it believe that? | A source recorded with each write |
| Has the record been changed since? | A hash chain whose newest hash is also stored outside the database |

## Why does overwriting memory break an audit?

An overwrite destroys the state that explains earlier decisions. Suppose an advisory agent stores `risk tolerance: low` for a user, recommends bonds, and two weeks later replaces the value with `high` after a new conversation.

A reviewer who asks why the agent recommended bonds finds a store that says the user's tolerance is high. The recommendation now looks like an error, and nothing in the database can show otherwise.

With two agents writing to that store, an overwrite can also happen by accident, which [shared vs isolated memory](/articles/shared-vs-isolated-memory/) shows in a short run.

Software has had the remedy for a long time. Martin Fowler's [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html), dated December 12, 2005, describes it as ensuring "that all changes to application state are stored as a sequence of events", so that "we can also use the event log to reconstruct past states".

## What does an append-only memory ledger look like?

An append-only memory ledger is a table in which each change adds a row and no row is updated. A version ends where the next one for the same subject begins, and each row carries a hash of its content and of the row before.

```python
"""An append-only memory ledger in SQLite: as-of queries, a hash chain, and what the chain misses."""
import hashlib
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("""create table memory (
    id integer primary key, entity text, fact text, source text,
    valid_from text, prev_hash text, hash text)""")


def digest(prev_hash, entity, fact, source, valid_from):
    return hashlib.sha256("|".join([prev_hash, entity, fact, source, valid_from]).encode()).hexdigest()


def write(entity, fact, source, at):
    """Append a row. Nothing is updated: a version ends where the next one starts."""
    last = db.execute("select hash from memory order by id desc limit 1").fetchone()
    prev_hash = last[0] if last else ""
    db.execute("insert into memory (entity, fact, source, valid_from, prev_hash, hash) values (?,?,?,?,?,?)",
               (entity, fact, source, at, prev_hash, digest(prev_hash, entity, fact, source, at)))


def as_of(entity, at):
    return db.execute("""select fact, source from memory where entity = ? and valid_from <= ?
                         order by valid_from desc limit 1""", (entity, at)).fetchone()


def head():
    row = db.execute("select hash from memory order by id desc limit 1").fetchone()
    return row[0] if row else ""


def verify(anchor=None):
    """Check the chain row by row, then compare its newest hash with one held elsewhere."""
    prev_hash = ""
    for row in db.execute("select id, entity, fact, source, valid_from, prev_hash, hash from memory order by id"):
        if row[5] != prev_hash or row[6] != digest(prev_hash, *row[1:5]):
            return f"chain broken at row {row[0]}"
        prev_hash = row[6]
    if anchor is not None and prev_hash != anchor:
        return "chain is consistent, but its newest hash does not match the anchor"
    return "chain intact"


def rehash():
    """What an editor with write access can do: recompute every hash after changing a row."""
    prev_hash = ""
    for row in db.execute("select id, entity, fact, source, valid_from from memory order by id").fetchall():
        new_hash = digest(prev_hash, *row[1:5])
        db.execute("update memory set prev_hash = ?, hash = ? where id = ?", (prev_hash, new_hash, row[0]))
        prev_hash = new_hash


write("user-17:risk", "risk tolerance is low", "turn 4: 'I can't afford to lose this money'", "2026-11-03T10:00")
write("user-17:risk", "risk tolerance is high", "turn 31: 'put some of it into crypto'", "2026-11-12T16:30")
anchor = head()          # in practice, sent to a system the database's editors cannot write to

print("as of Nov 10:", as_of("user-17:risk", "2026-11-10T09:00"))
print("as of Nov 14:", as_of("user-17:risk", "2026-11-14T09:00"))
print("untouched:              ", verify(anchor))

db.execute("update memory set fact = 'risk tolerance is high' where id = 1")
print("row 1 edited in place:  ", verify(anchor))

rehash()
print("edited, hashes redone:  ", verify())
print("same, checked to anchor:", verify(anchor))

db.execute("delete from memory where id = 2")
rehash()
print("newest row deleted:     ", verify(anchor))
```

The script runs on Python's standard library, and `python3 memory_ledger.py` reports seven results.

```text
as of Nov 10: ('risk tolerance is low', "turn 4: 'I can't afford to lose this money'")
as of Nov 14: ('risk tolerance is high', "turn 31: 'put some of it into crypto'")
untouched:               chain intact
row 1 edited in place:   chain broken at row 1
edited, hashes redone:   chain intact
same, checked to anchor: chain is consistent, but its newest hash does not match the anchor
newest row deleted:      chain is consistent, but its newest hash does not match the anchor
```

The two `as of` results are the audit answer. On November 10 the agent believed the user's tolerance was low, and the stored source says why.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/memory-versioning/append-vs-overwrite.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/memory-versioning/append-vs-overwrite.narrow.svg" width="288" height="1000"><img class="np-has-narrow" src="/static/images/diagrams/memory-versioning/append-vs-overwrite.svg" width="720" height="544" alt="A memory changed in either of two ways. The append-only ledger inserts a new row and leaves the old ones in place, so v1, v2, and v3 all remain and any point in time can be recovered. A destructive update overwrites the row: v2 replaces v1, and the prior state is gone." loading="lazy" decoding="async"></picture></a>
  <figcaption>Appending a new version and keeping the old ones lets the store answer for any past date.</figcaption>
</figure>

## What does the hash chain catch, and what does it miss?

The chain alone catches a careless edit and misses a careful one. The run above detects a row changed in place, then reports "chain intact" for that edit once the editor has recomputed every hash down the table.

The chain lives in the same database as the data, so anyone who can edit a row can rewrite the chain. What makes it evidence is the anchor, a copy of the newest hash kept in a second system, in a signed export or with the auditor.

The results labelled `same, checked to anchor` and `newest row deleted` use the anchor. With the anchor held outside, the rewritten chain no longer matches, and deleting the newest row is caught the same way.

An earlier version of this script closed each row by writing an end time into it, and that field sat outside the hash. Moving it would have erased the November 10 answer with the chain intact, which is why this version stores no end time and derives it from the next row.

## How do you link a memory to the reasoning behind it?

Record the source at write time, as a required field, because it can't be recovered afterwards. The `source` column in the ledger above holds the turn and the words that justified the fact.

That argument applies to any note an agent keeps, and [my essay on evidence in agent memory](/articles/agent-memory-evidence/) makes it for a shared memory format.

Where the model writes memory through a tool, make the tool's source parameter required, so a write without one is rejected by the schema. A fact with no source is one nobody can tell apart from an inference the model made out of a passing remark.

Stroq's own README states the limit of tracing by text: "Matching is text-level, so a command the model writes from scratch does not trace back to a source." A memory's source field has that limit too, since it records what the model cited and can't prove the citation was the real cause.

The stakes are higher for memory than for a command, because a stored fact is reused. A wrong command runs once, and a wrong memory is loaded as true in every later session until someone traces it.

## What does a regulator ask for?

The clearest written requirement I know of is in the EU AI Act, adopted in 2024. [Article 12](https://artificialintelligenceact.eu/article/12/) says "High-risk AI systems shall technically allow for the automatic recording of events (logs) over the lifetime of the system."

The article is about high-risk systems and about event logs, and it doesn't mention agent memory. I read a memory write as an event that changes what the system will do next, so a team under that rule should want it in the record.

## How do you audit a vector database?

Keep the ledger as the record and treat the vector index as a copy that can be rebuilt from it. That is a design choice on my part, made because an index built for similarity search stores vectors and has no field for which version of a fact is current.

That choice comes with two rules. Only the newest row for each subject is embedded for retrieval, so a superseded fact can't outrank the current one, and the index is rebuilt from the ledger when the two disagree.

Frameworks separate short-lived and durable state along a similar line. LangGraph's [persistence documentation](https://docs.langchain.com/oss/python/langgraph/persistence) says its layer "gives agents short-term memory through checkpointers and long-term memory through stores", and the versioning described here applies to stores, the long-term kind.

Version history is useful only if state survives a restart in a readable form, the subject of the guide to [serializing agent memory between sessions](/articles/memory-serialization/). Deciding what deserves a row at all is covered in [AI memory management for LLMs](/articles/ai-memory-management/).

## What does versioning cost?

Versioning costs storage and a filter on every read. A fact occupies one row for every version it has had, and every query has to say whether it wants the current row or the row for a past date.

The anchor adds an operational cost of its own, since some second system has to receive the newest hash after each write or each batch. That is the price of a record someone outside the team can trust.

## FAQ

**Doesn't keeping every version risk confusing the agent?**

Only if old versions reach the prompt. Retrieval should read current rows, and the history is for people and for audits.

**Can I use git for this?**

For a single agent that keeps its memory as files, yes, since commits give versions and a pushed remote acts as the anchor. A database ledger fits better when many users or agents write at once.

**Is the hash chain proof that nobody edited a row?**

No, and the run above shows why. The chain is proof only together with a copy of the newest hash that the editor could not have changed.
