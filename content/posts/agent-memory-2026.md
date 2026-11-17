---
category: agent-memory
primary_query: agent memory frameworks
siblings:
- context-windows-vs-memory
- ai-memory-management
- short-term-agent-memory
bridges:
- slug: hybrid-search
  reason: A memory read path is a retrieval problem.
- slug: model-context-protocol
  reason: Mem0 and Graphiti both publish a server that exposes memory over the protocol.
- slug: rag-evaluation
  reason: A memory read path is a retrieval problem.
date: 2026-04-19
description: Agent memory frameworks in 2026 differ on who writes a memory and what shape
  it's stored in. How Letta, Mem0, Graphiti and Anthropic's memory tool answer those
  questions, read from their current docs.
status: published
work_note: "Building an AI product whose readers are engineers? I'm Ninad Pathak, a freelance technical writer, and I write tutorials and technical articles for companies like yours after running the product myself. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: Agent Memory Frameworks in 2026
updated: '2026-08-17'
slug: agent-memory-2026
video: agent-memory-2026
---

An early paper in this category borrowed its idea from the operating system. [MemGPT](https://arxiv.org/abs/2310.08560), from October 2023, treats the context window the way an OS treats RAM: a small fast space, with a larger slow one behind it and something deciding what moves between them.

That project is called Letta now, and it has company. Agent memory frameworks in 2026 are the libraries and services that store what an agent learns outside the context window and bring the relevant part back on a later turn.

They've stopped agreeing on what that "something" is. Having read the current docs for four of them, I think the useful way to sort [agent memory](/articles/agent-memory/) frameworks is by two questions: who decides that a fact is worth writing down, and what shape it's stored in.

I managed the writing team at Mem0 earlier this year, so read my notes on that one knowing it.

## What does an agent memory framework do?

An agent memory framework writes facts from a conversation into a store and reads the relevant ones back into the prompt later. A RAG pipeline reads a corpus somebody else wrote, and a memory framework also has to decide what to write.

Say a support agent learns on Monday that a customer is on the enterprise plan. It should still treat them as an enterprise customer on Tuesday without being told again, and it should stop the day they downgrade.

The read side looks the same in every framework I checked. Memories sit in storage, a retrieval step finds candidates for the current turn, and a ranking step picks the few that go into the context window.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-memory-2026/memory-stack.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-memory-2026/memory-stack.narrow.svg" width="288" height="648"><img class="np-has-narrow" src="/static/images/diagrams/agent-memory-2026/memory-stack.svg" width="720" height="256" alt="The read path of an agent memory framework, left to right: a storage layer holds memories outside the context window, a retrieval layer finds candidates, a ranking layer orders them, and the few that are left reach the agent's context window." loading="lazy" decoding="async"></picture></a>
  <figcaption>Every framework here reads the same way: storage, then retrieval, then ranking. Only what survives ranking reaches the context window.</figcaption>
</figure>

So the read path is a retrieval problem, and the tools for it carry over: [hybrid search](/articles/hybrid-search/) for finding candidates, and the retrieval metrics from [RAG evaluation](/articles/rag-evaluation/) for scoring them. The write path is where the frameworks part ways.

## How do the main agent memory frameworks differ?

They differ on who writes a memory and on the shape it's stored in. Here's how four of them answer, from their docs as of November 18, 2026:

| Framework | Who decides what to write | What gets stored |
|---|---|---|
| [Letta](https://docs.letta.com/guides/agents/memory) | The agent, by calling memory tools | Text blocks pinned in the prompt, plus a searchable archive |
| [Mem0](https://docs.mem0.ai/core-concepts/memory-types) | The service, which extracts facts from the messages you send | Short facts with metadata and embeddings |
| [Graphiti](https://help.getzep.com/graphiti/getting-started/overview) | The framework, which extracts entities and relationships | A knowledge graph whose facts carry time |
| [Anthropic's memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) | The model, by asking for file operations | Files in a directory your application owns |

I'd pick between them on the first column before the second. An agent that writes its own memory spends turns on it and can be asked why it wrote something, and a service that extracts in the background costs the agent nothing and is harder to question.

## How does Letta manage memory?

Letta keeps a small set of memory blocks inside the prompt and lets the agent edit them. Its docs describe the blocks as strings that the agent changes through memory tools, and a block attached to an agent is pinned to the system prompt.

Everything that doesn't fit lives outside. Letta stores all messages, so the old ones can still be fetched after they've been compacted out of the window, and a separate [archival memory](https://docs.letta.com/guides/agents/archival-memory) holds what the agent chooses to file.

That's the MemGPT design carried forward, and I think its cost is still the one the paper signed up for. The model manages its own paging, so some of every long task goes to deciding what to keep.

## How does Mem0 manage memory?

Mem0 takes the writing decision away from the agent. You send it the conversation turns, and by default it stores facts extracted from them, so "I prefer aisle seats" becomes a stored preference and the transcript is dropped.

Reads are a search call scoped by `user_id`, `agent_id` or `run_id`. The docs say plainly where its job ends: "Your app decides which returned memories to include in the prompt."

If you'd rather extract nothing, there's a switch. Passing `infer=False` stores the raw messages, and I'd know which mode a deployment runs in before debugging a missing memory.

## How does Graphiti handle facts that change?

Graphiti stores memory as a graph in which a fact has a period when it was true. Zep, the company behind it, uses Graphiti in its hosted product, and the docs list a bi-temporal model and fact invalidation among its parts.

The reason is in its own docs, which say Microsoft's GraphRAG was "primarily designed for static documents". A customer's plan isn't a static document, and the enterprise example above needs a store that can say the old fact ended.

An agent can act on a stale fact without knowing it's stale, so it's the question I'd put to any framework on the list. [Memory versioning](/articles/memory-versioning/) covers what an honest answer looks like, with an append-only ledger you can run.

## What is Anthropic's memory tool?

Anthropic's memory tool gives Claude a directory of files and leaves the storage to you. Claude asks to create, read or edit a file under `/memories`, and your application carries out each request against storage it controls.

It's the plainest design of the four, and I mean that as praise. A memory you can open in a text editor is a memory you can review, which is the same thing I liked about [DeerFlow's Markdown files](/articles/deerflow-memory/).

What you give up is retrieval. A directory has no ranking step, so finding the right note depends on how the model named its files.

## Can these frameworks be swapped over MCP?

Partly. Mem0 and Graphiti each publish a server for the [Model Context Protocol](/articles/model-context-protocol/), so an MCP client can add and search memories in either without custom code, and Graphiti's docs call their server experimental.

The protocol moves the calls and leaves the contents alone. A fact extracted by Mem0 and an edge in Graphiti's graph aren't the same record, so changing provider still means migrating the data.

## How should you evaluate an agent memory framework?

Test whether the agent does its job better with the memory than without it. Retrieval scores come first because they're cheap, and they aren't the end of it.

[LongMemEval](https://arxiv.org/abs/2410.10813) is the benchmark I'd read before building my own test. Its authors split memory into indexing, retrieval and reading, and they report "a 30% accuracy drop" for commercial assistants and long-context models on information spread across long interactions.

Reading is the stage people skip. The right facts in the wrong order can still produce a worse decision, for the reason the Lost in the Middle section of [context windows vs memory](/articles/context-windows-vs-memory/) gives: where a fact sits in the prompt changes whether the model uses it.

So I'd write the test set around updates and contradictions. A customer who changed plans is a harder case than a customer who stated one, and it's the case that sends a wrong invoice.

For the layer under all of this, [AI memory management](/articles/ai-memory-management/) covers what stays in the window, and [short-term memory for AI agents](/articles/short-term-agent-memory/) covers the session itself.

## FAQ

**What is the difference between agent memory and RAG?**

RAG retrieves from documents that already exist. Agent memory also writes, which means deciding what's worth keeping and what an older fact should give way to.

**Is MemGPT still a thing?**

Yes, under another name. The project's repository describes Letta as formerly known as MemGPT, and the paper's design of in-context blocks with outside storage is still how Letta works.

**Which agent memory framework should I start with?**

I'd start with the plainest one that fits, which for a single agent may be a directory of files. Move to extraction or a graph when you can name the question the plain version can't answer.

**Does a bigger context window replace a memory framework?**

Not on LongMemEval's evidence. The paper reports the accuracy drop for long-context models as well as for commercial assistants.

**Do agent memory frameworks support MCP?**

Some do. Mem0 and Graphiti publish MCP servers, and Letta's docs list MCP tools among the tools an agent can call.
