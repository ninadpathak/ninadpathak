---
category: agent-memory
primary_query: agent state persistence
siblings:
- memory-compression
- memory-versioning
- context-windows-vs-memory
bridges:
- slug: coding-agent-memory
  reason: Claude Code, Codex and Gemini CLI each write agent notes to a different place and format.
date: '2026-04-30'
description: 'Memory serialization is how an agent persists state across sessions. Three ways to do it, a run of a versioned state record, and why to keep the log.'
slug: memory-serialization
status: published
work_note: 'I led Mem0''s team of 13 writers and did its technical reviews. This page is my own account of how an agent''s state gets written out and read back, with a run of one small record. [My portfolio](/portfolio/) has the case study.'
title: 'Memory Serialization: How Agents Persist State Across Sessions'
updated: 2026-11-17
---

Zork let players save their position to disk, and BYTE magazine explained in 1981 what the feature was for, in a line [Wikipedia's article on saved games](https://en.wikipedia.org/wiki/Saved_game) preserves: "it was intended to let players play over many weeks". A game too long for one sitting needed a way to write down where the player stood.

Memory serialization is that feature for an agent. Persisting agent state across sessions means writing what the agent knows and what it was doing to storage, in a form that a later process can load and continue from.

So I'll go through the usual ways to save an agent's state, run one of them, and then get to the catch a game never had, which is that the save itself can be wrong. That catch is the part of [agent memory](/articles/agent-memory/) worth your attention.

## What are the ways to persist agent state?

The common approaches are full replay, a log with a recent window, and a structured state record. They differ in what is stored and in what the next session has to do with it.

| Approach | What is stored | What the next session does | Main cost |
| --- | --- | --- | --- |
| Full replay | Every message and tool result | Reads the whole history again | Tokens and time on every restart |
| Log plus recent window | Every message, in a database | Loads the last few and searches the rest | Has to work out where things stand |
| Structured state | A small record of facts, task and open items | Loads the record and continues | Someone has to design the record |

Full replay loses nothing and scales worst, since a long history is paid for again at each start. A log is cheap to write and leaves the next session to reconstruct the situation from raw messages.

Structured state is the one that behaves like a save file. It's small and quick to load, but it holds only what the writer thought to put in it.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/memory-serialization/serialize-restore.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/memory-serialization/serialize-restore.narrow.svg" width="288" height="1176"><img class="np-has-narrow" src="/static/images/diagrams/memory-serialization/serialize-restore.svg" width="720" height="544" alt="Two sessions across a restart. With serialization, the agent writes its state to a store at session end and restores it after the restart, so the new session starts where the old one stopped. Without it, the restart wipes the session and the agent starts from zero." loading="lazy" decoding="async"></picture></a>
  <figcaption>A session that cannot be serialized will not survive a restart.</figcaption>
</figure>

## What goes wrong after a restart?

Old state meets new code, and old facts meet a changed world. The script below saves a record the way older code would have, then loads it with a loader that expects a newer shape.

```python
"""Save an agent's state, restart with newer code, and load it back.

The loader migrates an old schema version and marks facts that are too old
to act on without checking. Dates are fixed so the output is repeatable.
"""
import json
import os
import tempfile
from datetime import date

SCHEMA_VERSION = 2
RECHECK_AFTER_DAYS = 3


def save_v1(path):
    """What older code wrote: version 1, with no plan field."""
    state = {
        "version": 1,
        "saved_on": "2026-11-10",
        "task": "migrate billing service to the v2 payments API",
        "facts": [
            {"text": "customer is on the enterprise plan", "confirmed_on": "2026-11-03"},
            {"text": "invoices table has been backfilled", "confirmed_on": "2026-11-10"},
        ],
        "open_items": ["switch webhook handler", "remove v1 client"],
    }
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def migrate(state):
    if state["version"] == 1:
        state["plan"] = None  # field added in version 2
        state["version"] = 2
    if state["version"] != SCHEMA_VERSION:
        raise ValueError(f"cannot read state version {state['version']}")
    return state


def load(path, today):
    with open(path) as f:
        state = migrate(json.load(f))
    for fact in state["facts"]:
        age = (today - date.fromisoformat(fact["confirmed_on"])).days
        fact["status"] = "recheck" if age > RECHECK_AFTER_DAYS else "trusted"
    return state


path = os.path.join(tempfile.mkdtemp(), "state.json")
save_v1(path)
state = load(path, today=date(2026, 11, 12))

print("loaded version:", state["version"], "| plan:", state["plan"])
for fact in state["facts"]:
    print(f"  {fact['status']:<8} {fact['text']} (confirmed {fact['confirmed_on']})")
print("open items:", ", ".join(state["open_items"]))

with open(path, "w") as f:
    json.dump({"version": 3}, f)
try:
    load(path, today=date(2026, 11, 12))
except ValueError as error:
    print("newer file, older code:", error)
```

Run as `python3 state_roundtrip.py`, it loads the old record and then refuses a newer one.

```text
loaded version: 2 | plan: None
  recheck  customer is on the enterprise plan (confirmed 2026-11-03)
  trusted  invoices table has been backfilled (confirmed 2026-11-10)
open items: switch webhook handler, remove v1 client
newer file, older code: cannot read state version 3
```

The version field is what let the loader add the missing `plan` key, and it is also what let older code refuse a file from the future. Without it, a missing key reads as a fact that was never established.

And the `recheck` label is the other half. A fact confirmed nine days earlier is loaded and marked as unverified, so the agent can ask before acting on it.

Why bother with the date? Because a saved fact was true when it was written, and the loader has no other way to know how long ago that was.

## Can a saved state be wrong from the start?

Yes, and a save from a game shows it. Anthropic's post on [the components of agent memory](https://www.anthropic.com/research/components-of-agent-memory), published on November 6, follows a model playing Pokémon Red that recorded the wrong side of a mountain for a landmark.

The model then updated its notes with the words "Mt Moon DONE." The mountain was still ahead of it, and in the run that kept the bad note the model fell back to an earlier route repeatedly and never reached the next city.

So what fixed it? The post's author, Lance Martin, describes a pass in which the model rereads its notes against the session log, a process he says "is often called dreaming".

"Claude checked the note against the session transcript, caught its error, and rewrote it."

Martin draws the conclusion himself: "The transcript gave Claude a ground truth to validate its memory against." The run with the corrected note went back into the cave and got through.

Now, that's one experiment by a vendor on its own model, and I think the design lesson holds anyway. A structured record with no log behind it can't be audited, so keep both and treat the record as a cache of the log.

My essay on [storing how the agent knew](/articles/agent-memory-evidence/) argues the same for single notes.

## What belongs in the state record?

Put in what the next session can't cheaply find out, and date every fact. A workable record has four parts.

- **Task.** What the agent was asked to do, in a sentence.
- **Facts.** What has been established, each with the date it was confirmed.
- **Open items.** What is left, in the order to do it.
- **Version.** The schema number, so a loader can migrate or refuse.

Leave out anything the agent can read again from its environment, such as file contents. [Contextual compression for agent memory](/articles/memory-compression/) makes that argument at length.

History is a separate decision. A record that overwrites a fact loses what was believed before, and [memory versioning](/articles/memory-versioning/) covers keeping every version when someone may ask later.

## What can't serialization fix?

It can't make a bad note good, and it can't share one. A record written by one tool is unreadable by the next, which is the complaint behind Mads Thines's proposal for [a shared format for agent memory](https://www.lorekit.io/blog/open-agent-memory-format).

You can see it in [coding agent memory](/articles/coding-agent-memory/), where Claude Code, Codex and Gemini CLI each write their own notes to a different place.

And it doesn't decide what the model sees. Loading state puts it in the context window, and [context windows vs memory](/articles/context-windows-vs-memory/) explains why a large record crowds out the work.

## FAQ

**What is memory serialization in an AI agent?**

It is writing the agent's state to storage in a form a later session can load. The state is a small structured record, a message log, or both.

**Why does an agent forget after a restart?**

The conversation lived in the memory of one process. Unless something wrote it to disk, a new process starts with nothing.

**Should an agent store the full transcript or a summary?**

Both, where it can. The summary is what gets loaded, and the transcript is what the summary can be checked against.
