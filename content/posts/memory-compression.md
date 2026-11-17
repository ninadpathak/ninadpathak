---
category: agent-memory
primary_query: context compression
siblings:
- short-term-agent-memory
- memory-serialization
- ai-memory-management
bridges:
- slug: llm-context-windows
  reason: Every loaded note is paid for in the context window of every session.
- slug: claude-code-memory
  reason: Claude Code's 200-line index is the worked example of a small loaded layer.
date: '2026-05-05'
description: 'Context compression for agent memory: what an agent should keep between sessions and what to leave out, with Anthropic''s November 2026 memory tests.'
slug: memory-compression
status: published
work_note: 'At Mem0 I ran 13 writers, and compression is one of the decisions any memory layer makes out of sight. Here I look at what a compressed record is allowed to drop. [My portfolio](/portfolio/) has the case study.'
title: 'Contextual Compression for Agent Memory: What Stays and What Goes'
updated: 2026-11-17
---

Every repository has a `.gitignore`, and [Git's documentation](https://git-scm.com/docs/gitignore) gives its job in a sentence: it "specifies intentionally untracked files that Git should ignore." The usual entries are build output and installed dependencies, which a command can produce again.

Context compression for agent memory makes that call about knowledge: what an agent carries into its next step or its next session, and what it leaves to be looked up again. It is the part of [AI agent memory](/articles/agent-memory/) that decides what gets written at all.

A build directory comes back exactly from one command. A lesson an agent learned by failing comes back only if it fails again, so that lesson is the thing worth the space.

## What counts as context compression?

The name covers two different operations. Inside one session, compaction replaces old turns with a summary so the work can continue, and [short-term memory for agents](/articles/short-term-agent-memory/) covers that one.

Across sessions, compression is the choice of what to write to a memory store and what to prune from it later. Anthropic's post on [the components of agent memory](https://www.anthropic.com/research/components-of-agent-memory), published on November 6, keeps the two apart and leaves compaction out of its definition of memory.

That definition is "knowledge that Claude gains from experience", kept between sessions and "saved as context it can read later." The second kind of compression is the subject here, since it decides what an agent knows next week.

## What should stay?

Keep what the environment can't hand back. Anthropic's evidence is a comparison of two models playing Pokémon Red, each with a folder it could write notes to, taken at about 10,000 steps into the game.

| Model | Memory written | Badges earned |
| --- | --- | --- |
| Claude Sonnet 3.7 | 413 files across 225 folders | 1 |
| Claude Fable 5 | 9 files in 2 folders, plus one top-level file | 4 |

The older model recorded each battle and each item. The post explains why that failed: facts such as the player's money or position "can be read off the screen every turn, so storing it is redundant."

The newer model wrote down the opposite kind of thing, and the post gives the reason: "memory files about strategy, plans, and tested rules exist only if Claude works them out, and they disappear unless Claude writes them down."

That is the `.gitignore` rule again. State the agent can re-read stays out of memory, and conclusions it had to earn go in.

The comparison is thin as evidence, and the post says so by describing it as "one run each". It is also a vendor writing about its own models, so I take it as an illustration of the rule and no more.

## Do fixed rules decide it well?

Anthropic's post suggests they don't, for strong models.

Its authors tested giving models one rule each about what to write. With the rule set to record only failures, "both Opus 5 and Opus 4.7 lost much of the performance boost that memory gave them".

Their summary of the lesson is "it helps to tell Claude what memory is for, but not how to use it." Older models went the other way in the same tests, and prompting Sonnet 4.6 to read its memory before answering "nearly doubled its benchmark score".

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/memory-compression/compression-pass.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/memory-compression/compression-pass.narrow.svg" width="288" height="544"><img class="np-has-narrow" src="/static/images/diagrams/memory-compression/compression-pass.svg" width="720" height="392" alt="Raw agent memory, every tool response and interaction kept in full, goes through a scoring pass that weighs recency, how often each item was accessed, and explicit importance. High scorers stay in memory; low scorers are dropped." loading="lazy" decoding="async"></picture></a>
  <figcaption>A scoring pass keeps what ranks high and drops the rest, so anything the scorer can't see is lost.</figcaption>
</figure>

A scoring pass is a fixed rule in code. It ranks stored items by recency, by how often they were read and by a flag set at write time, and it drops whatever ranks low.

I think the result above is a reason to be wary of that design. A half-life can't know that a rule written two months ago is the one that prevents today's mistake, and the model that wrote the note could have said so.

Where a scorer is still needed, give it the one signal the writer had. A note marked as a tested rule should outlive a note marked as an observation, whatever their ages.

## When does compression backfire?

When the compressed form is larger or less true than what it replaced. Anthropic's post has an example of each.

A model in one test built a wiki from a set of legal documents, and "the wiki grew larger than the documents themselves". The authors compare it to Borges's map the size of the empire and call it "an extremely detailed wiki that effectively abstracted nothing."

The other failure is a wrong note. The post warns that with notes loaded into every session, "an incorrect note can be carried into every session", and a summary is trusted in the same way once the turns behind it are gone.

Both failures have the same defence, which is to keep the source. A summary that can be checked against the transcript can be corrected, a point [memory serialization](/articles/memory-serialization/) takes further.

## How small should the loaded part be?

Small enough to read every time, with pointers to the rest. Claude Code is the worked example in the post: "It loads only the first 200 lines or 25 KB of MEMORY.md."

That top layer is an index, and the detail sits in files the agent opens when it needs them. The guide to [Claude Code memory](/articles/claude-code-memory/) describes the layout, and [AI memory management](/articles/ai-memory-management/) covers the layers in general.

The budget is real because every loaded line is paid for in the [context window](/articles/llm-context-windows/) of every session. A note has to earn its place there, and the rest can wait on disk.

## FAQ

**What is context compression?**

It is reducing what an agent carries forward, by summarizing old turns within a session or by choosing what to keep in memory between sessions.

**Is compaction the same as memory?**

No. Compaction rewrites the current conversation so it fits, and memory is what a later session can read.

**What should an agent leave out of memory?**

Anything it can read again from its environment, such as file contents or current state. Conclusions, plans and tested rules are what a store is for.
