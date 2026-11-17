---
category: agent-memory
primary_query: deerflow memory
siblings:
- agent-memory-types
- agent-memory-evidence
- memory-compression
bridges:
- slug: agent-harnesses
  reason: DeerFlow describes itself as an agent harness, and memory is one part of what a harness supplies.
date: 2026-04-19
description: 'DeerFlow memory is DeerMem by default: one Markdown file per fact, written after a gate and injected into later prompts. Read from the repository on November 17, 2026.'
status: published
work_note: "I write tutorials and technical articles for AI companies, and I run the product before I write a line. I'm Ninad Pathak, a freelance technical writer, and [we can work together](/services/freelance-technical-writer-for-ai-companies/)."
title: How Memory Works in DeerFlow
slug: deerflow-memory
updated: 2026-11-17
---

DeerFlow's memory is a local store called DeerMem that keeps each remembered fact as its own Markdown file. DeerMem extracts those facts by itself after a conversation has been quiet for 30 seconds, and it puts the facts with the highest confidence scores into the prompt of later conversations.

Around 1995, Daniel Bernstein's [Maildir](https://en.wikipedia.org/wiki/Maildir) format gave every email message its own file in place of one shared mailbox.

DeerFlow stores facts the way Maildir stores messages, one file each. Everything below is from the [DeerFlow repository](https://github.com/bytedance/deer-flow) at the commit of November 17, 2026 that the links point to, and it's one worked case of [AI agent memory](/articles/agent-memory/).

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/deerflow-memory/stage-handoff.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/deerflow-memory/stage-handoff.narrow.svg" width="288" height="728"><img class="np-has-narrow" src="/static/images/diagrams/deerflow-memory/stage-handoff.svg" width="720" height="256" alt="A conversation passes through fact extraction and then a write gate. Facts that pass are saved as one Markdown file each, and a later conversation has the highest-confidence ones injected into its prompt until a token budget is full." loading="lazy" decoding="async"></picture></a>
  <figcaption>DeerMem's default mode extracts facts after a quiet period, checks each against a write gate, stores one Markdown file per fact and injects the highest-confidence ones into later prompts.</figcaption>
</figure>

## How does DeerFlow store memory?

DeerFlow stores memory as plain files on your disk. The [memory guide](https://github.com/bytedance/deer-flow/blob/3751eb8daf491324e728f63bcc773e0f081eb7e5/docs/guide/memory.md) describes one `memory.json` per user, holding two summaries, and one Markdown file per fact under `agents/{agent_name}/facts/`.

The contributor notes for the memory code state the storage rule in one sentence: "Facts are one Markdown file each." The JSON file never holds facts or an index of them.

DeerMem's search uses a SQLite full-text index, and the contributor notes treat that index as derived data that can be rebuilt from the Markdown files at any time.

So the Markdown files are the memory, and you can open any fact in a text editor. If you edit a fact file by hand, DeerFlow doesn't see the change until you trigger a reload.

My page on the [types of agent memory](/articles/agent-memory-types/) would call DeerMem's store semantic memory with a short summary on top. DeerMem keeps facts, and it doesn't keep a log of episodes.

## What does DeerFlow write to memory, and when?

DeerFlow writes facts extracted from what the user said and from the assistant's final replies. A turn in which the assistant asked for a tool is left out, and the [contributor notes](https://github.com/bytedance/deer-flow/blob/3751eb8daf491324e728f63bcc773e0f081eb7e5/backend/packages/harness/deerflow/agents/memory/AGENTS.md) give the reason as a rule: "Tool-call intent is not memory."

Extraction waits for a pause in the conversation. The guide gives a quiet period of 30 seconds by default, with a cap of 300 seconds from the first pending update.

The next step is the one I'd copy into my own memory design. DeerMem's default mode classifies every proposed fact by scope, durability and authority, and a write gate made of fixed rules, not a model, decides whether the fact is stored.

The gate accepts durable, descriptive facts about the user, say a preferred language. Temporary task state and one-off permissions stay in the conversation's own state, and duplicates are skipped when the update is applied.

DeerMem has a second mode that skips the write gate. With memory set to tool mode, the model writes and edits facts itself through memory tools, which the guide calls a separate, model-directed path.

## How does DeerFlow decide what to forget?

DeerFlow's default is to forget the facts it's least confident about. When a scope reaches its maximum number of facts, the default policy evicts in order of confidence alone.

An optional policy called `hybrid-v1` weighs three signals: confidence at 65%, how recently the user confirmed the fact at 25%, and how often searches returned it at 10%. A small share of the slots can be reserved for corrections.

A rule in the contributor notes matters more than those percentages. The notes say "Confirmation needs human evidence", which means only evidence from the user counts as confirming a fact, and a repeat by the model doesn't.

The confidence score itself still comes from the model that extracted the fact. My essay on [evidence in agent memory](/articles/agent-memory-evidence/) argues for a neighbouring rule, that a note should carry its source.

## How does memory get back into the prompt?

Memory gets back into the prompt through two separate paths, injection and search. Default injection adds the user's two summaries and then the agent's facts in order of confidence, until a token budget is full.

Search is a tool the model calls when it wants a fact that wasn't injected, and it ranks facts by a full-text score combined with time decay and confidence. DeerMem can also choose which facts to inject based on the current question, and that setting is off by default.

Injection can be switched off for the whole system or for one agent. When it's off for an agent, the guide says the previously injected block is removed from that agent's state before the next model call.

DeerMem handles compaction separately from ordinary turns. It takes a snapshot of the messages a compaction is about to remove, and queues it for extraction separately, so facts from a long session are extracted before the summary replaces the messages that held them.

[Memory compression](/articles/memory-compression/) covers what a summary can drop.

## What other memory backends does DeerFlow support?

DeerFlow has optional backends for mem0, OpenViking and Honcho, as of this reading. DeerMem stays the default, and you switch backends with one line of configuration.

The repository also includes an empty backend as a template for writing your own.

| Backend | Where memory lives | What the guide says about it |
| --- | --- | --- |
| DeerMem | Local files | The default |
| mem0 | The hosted mem0 platform or a compatible self-hosted server | Opt-in |
| OpenViking | OpenViking sessions | Opt-in, one user in the first integration |
| Honcho | A Honcho server, hosted or self-hosted | Opt-in, with no fact editing from DeerFlow's settings page |

I managed the writing team at Mem0 earlier this year, so weigh what I say about the mem0 row with that in mind. I'd start with DeerMem, the default, because you can open its fact files and read what the agent remembered.

## What do I make of DeerFlow's memory?

DeerMem's default write path is the strictest I've read in an open-source agent project. Its design effort went into deciding which facts may be written and who may confirm them, and comparatively little went into retrieval, which is a full-text search.

DeerMem also has a lot of settings: the guide documents flags for deduplication, eviction, relevance ranking and shutdown. A team that adopts DeerMem has to understand each flag it changes.

Memory is one part of DeerFlow, which calls itself an agent harness, and it sits beside its sandboxes and sub-agents in the way [agent harnesses](/articles/agent-harnesses/) describes.

## FAQ

**How does memory work in DeerFlow?**

DeerFlow extracts facts from conversations after a quiet period, checks each against a write gate, stores accepted facts as Markdown files and injects the highest-confidence ones into later prompts. The default backend is called DeerMem.

**Where does DeerFlow store its memory?**

On local disk by default, as one `memory.json` of summaries per user and one Markdown file per fact. Optional backends store memory in mem0, OpenViking or Honcho.

**Can you edit DeerFlow's memory by hand?**

Yes, and DeerFlow needs a reload afterwards to see the edit. The fact files are Markdown and the search index is rebuilt from them, and the application also has a memory page in its settings.
