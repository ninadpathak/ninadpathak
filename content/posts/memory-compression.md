---
category: agent-memory
primary_query: context compression
siblings:
- short-term-agent-memory
- rag-vs-memory
- memory-serialization
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

A `.gitignore` file is where a repository says what it won't keep. [Git's documentation](https://git-scm.com/docs/gitignore) gives the job in a sentence, that it "specifies intentionally untracked files that Git should ignore", and the usual entries are build output and installed dependencies, which a command can produce again.

Context compression asks the same thing of an agent's context: what gets carried forward, and what gets left to be looked up again. It happens in two places, inside a session when old turns are squeezed to fit the window, and between sessions when the agent decides what to write down.

So I'll take both in turn. The rule I end up with for [AI agent memory](/articles/agent-memory/) is the `.gitignore` one, which is to keep what you can't regenerate.

## What is context compression?

Context compression is any step that reduces what a model has to carry so the work can go on. The two kinds share a name and differ in almost everything else.

| | Inside a session | Between sessions |
| --- | --- | --- |
| What is compressed | The conversation so far | What the agent learned |
| How | Old turns are dropped or summarized | The agent chooses what to write to memory and what to prune |
| Trigger | The context window filling up | The end of a task or session |
| What goes wrong | The summary leaves out something a later turn needs | The store fills with notes that are redundant or wrong |

Anthropic's post on [the components of agent memory](https://www.anthropic.com/research/components-of-agent-memory), written by Lance Martin and published on November 6, keeps the two apart. Its definition of memory is "knowledge that Claude gains from experience", kept between sessions, and it leaves compaction out.

## How does compression work inside a session?

It replaces old turns with something shorter. The same post describes compaction as "summaries written by Claude that replace its older turns so it can continue working in a new context window".

Why not keep everything? Because a full window fails outright, and a nearly full one gets worse answers, which my page on [LLM context windows](/articles/llm-context-windows/) goes into.

But a summary is a lossy copy made by a model. Whatever it leaves out is gone for the rest of the session, and [short-term memory for agents](/articles/short-term-agent-memory/) runs an example where the thing left out is the instruction that mattered.

That's the first place the `.gitignore` rule applies. A file the agent can open again doesn't need to survive in the summary, and a decision the user made in conversation does.

## What should an agent keep between sessions?

Keep what the environment can't hand back. Martin's evidence is a comparison of two models playing Pokémon Red, each with a folder to write notes in, and my page on [RAG vs memory](/articles/rag-vs-memory/) has the file counts.

What interests me here is why the note-heavy model lost. The post's reason is that its "detailed record was continuously going out of date", so it "had to spend more time and resources combing through its memories rather than playing the game."

And the better model? It wrote down what the game never showed it, since "memory files about strategy, plans, and tested rules exist only if Claude works them out, and they disappear unless Claude writes them down."

So state the agent can read again stays out, and conclusions it had to earn go in. Now, this is one run per model, reported by the company that makes both, so I take it as an illustration and no more.

## Do fixed rules decide it well?

For strong models, the post suggests they don't. Its authors gave models one rule each about what to write, and with the rule set to record only failures, "both Opus 5 and Opus 4.7 lost much of the performance boost that memory gave them".

Martin's summary of the lesson is "it helps to tell Claude what memory is for, but not how to use it." Older models went the other way, though: prompting Sonnet 4.6 to read its memory before answering, and then to test its theories, "nearly doubled its benchmark score".

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/memory-compression/compression-pass.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/memory-compression/compression-pass.narrow.svg" width="288" height="544"><img class="np-has-narrow" src="/static/images/diagrams/memory-compression/compression-pass.svg" width="720" height="392" alt="Raw agent memory, every tool response and interaction kept in full, goes through a scoring pass that weighs recency, how often each item was accessed, and explicit importance. High scorers stay in memory; low scorers are dropped." loading="lazy" decoding="async"></picture></a>
  <figcaption>A scoring pass keeps what ranks high and drops the rest, so anything the scorer can't see is lost.</figcaption>
</figure>

A scoring pass is a fixed rule in code. It ranks stored items by recency, by how often they were read and by a flag set at write time, and it drops whatever ranks low.

I think that result is a reason to be wary of the design. A half-life can't know that a rule written two months ago is the one that prevents today's mistake, and the model that wrote the note could have said so.

So where a scorer is still needed, give it the one signal the writer had. A note marked as a tested rule should outlive a note marked as an observation, whatever their ages.

## When does compression backfire?

When the compressed form is less true than what it replaced. The post has a case I haven't seen quoted elsewhere, from a test in which agents built a wiki out of a set of contracts.

Several agents wrote to one shared table of contract terms at once. When a brief was generated from the result, "Claude had included only 41 of the 57 facts (72%)", and the cause was that "agents had overwritten one another's work."

The fix was structural. Giving each contract a single agent, which wrote its own page and quoted terms word for word, kept all 57.

Here's what I take from that. Compression fails at the write as often as at the summary, and quoting the source exactly is the cheapest protection against both.

The opposite failure is in the post too. On another task "the wiki grew larger than the documents themselves", which Martin calls "an extremely detailed wiki that effectively abstracted nothing."

Either way the defence is to keep the source. A summary that can be checked against the transcript can be corrected, a point [memory serialization](/articles/memory-serialization/) takes further.

## How small should the loaded part be?

Small enough to read every time, with pointers to the rest. Claude Code is the post's worked example: "It loads only the first 200 lines or 25 KB of MEMORY.md."

That top layer is an index, and the detail sits in files the agent opens when it needs them. The guide to [Claude Code memory](/articles/claude-code-memory/) describes the layout, and [AI memory management](/articles/ai-memory-management/) has the layers in general.

And the budget is real, because every loaded line is paid for in every session. A note has to earn its place there, and the rest can wait on disk.

## FAQ

**What is context compression?**

It is reducing what an agent carries forward, by summarizing old turns within a session or by choosing what to keep in memory between sessions.

**Is compaction the same as memory?**

No. Compaction rewrites the current conversation so it fits, and memory is what a later session can read.

**What should an agent leave out of memory?**

Anything it can read again from its environment, such as file contents or current state. Conclusions, plans and tested rules are what a store is for.
