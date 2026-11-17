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

MemGPT, an early paper on agent memory, took its design from the operating system. [The paper](https://arxiv.org/abs/2310.08560), from October 2023, treats the context window the way an OS treats RAM: a small fast space with a larger, slower store behind it, and a manager that moves data between the two.

The MemGPT project is called Letta now, and other teams have built their own answers since. Agent memory frameworks in 2026 are the libraries and services that store what an agent learns outside the context window and bring the relevant part back on a later turn.

The MemGPT paper made the model itself the manager that moves data, and the frameworks no longer agree on that choice. I read the current docs for four of them, and I think the clearest way to compare [agent memory](/articles/agent-memory/) frameworks is with two questions: who decides that a fact is worth writing down, and in what form is the fact stored?

I managed the writing team at Mem0 earlier this year, so weigh what I say about Mem0 with that in mind.

## What does an agent memory framework do?

An agent memory framework writes facts from a conversation into a store and reads the relevant facts back into the prompt in a later conversation. A RAG pipeline only reads, from documents somebody else wrote, and a memory framework also has to decide what to write.

Say a support agent learns on Monday that a customer is on the enterprise plan. The agent should still treat that customer as an enterprise customer on Tuesday without being told again, and it should stop on the day the customer downgrades.

Reading works the same way in every framework here that uses search. The memories sit in storage, a retrieval step finds candidate memories for the current turn, and a ranking step picks the few candidates that go into the context window.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/agent-memory-2026/memory-stack.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/agent-memory-2026/memory-stack.narrow.svg" width="288" height="648"><img class="np-has-narrow" src="/static/images/diagrams/agent-memory-2026/memory-stack.svg" width="720" height="256" alt="The read path of an agent memory framework that searches, left to right: a storage layer holds memories outside the context window, a retrieval layer finds candidates, a ranking layer orders them, and the few that are left reach the agent's context window." loading="lazy" decoding="async"></picture></a>
  <figcaption>A framework that searches reads this way: storage, then retrieval, then ranking. Only what survives ranking reaches the context window.</figcaption>
</figure>

Because reading a memory is a retrieval problem, the tools built for retrieval apply to it. [Hybrid search](/articles/hybrid-search/) finds the candidate memories, and the metrics from [RAG evaluation](/articles/rag-evaluation/) score whether the right ones came back.

Writing is where the four frameworks differ, and the rest of this page is about writing.

## How do the main agent memory frameworks differ?

The main agent memory frameworks differ on who writes a memory and on the form the memory is stored in. The table gives each framework's answer, taken from its docs on November 18, 2026:

| Framework | Who decides what to write | What gets stored |
|---|---|---|
| [Letta](https://docs.letta.com/concepts/memfs/) | The agent, by editing files, and background subagents that consolidate | Markdown files in a git repository the agent owns |
| [Mem0](https://docs.mem0.ai/core-concepts/how-it-works) | The service, which extracts facts from the messages you send | Short facts with metadata and embeddings, plus the entities they mention |
| [Graphiti](https://help.getzep.com/graphiti/getting-started/overview) | The framework, which extracts entities and relationships | A knowledge graph whose facts carry time |
| [Anthropic's memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) | The model, by asking for file operations | Files in a directory your application owns |

I'd choose between these frameworks by the "who decides" column first. When the agent writes its own memory, as in Letta, you can ask the agent why it saved a fact, and when a service extracts facts in the background, as in Mem0, there's no reasoning to ask about.

## How does Letta manage memory?

Letta gives each agent a git repository of Markdown files, which Letta calls MemFS. The agent reads and edits the files with ordinary file tools, and an edit becomes part of the agent's memory once the agent commits and pushes it.

The location of a file decides whether the model sees it on every turn. Files at the root of the repository, or under `system/` on older agents, are loaded into the system prompt each turn, and files in subdirectories stay out of the prompt until the agent opens them.

Letta also has a second writer besides the agent. Letta's [memory docs](https://docs.letta.com/configuration/memory/) describe a feature called dreaming, in which "background subagents" review recent conversations and update the memory files while the main agent keeps working.

So in Letta today, both the agent and a background process decide what to write. The earlier Letta design, with memory blocks pinned in the prompt and a searchable archive behind them, is the design from the MemGPT paper, and Letta's pages for it are now marked as the legacy SDK.

## How does Mem0 manage memory?

Mem0 takes the decision about what to write away from the agent. Your application sends Mem0 the conversation turns, and by default Mem0 extracts facts from them, so the message "I prefer aisle seats" is stored as a seating preference and the rest of the transcript is not kept.

Reading from Mem0 is a search call scoped by `user_id`, `agent_id` or `run_id`. Mem0 returns the matching memories and stops there, and its docs put the next step on you: "Your app decides which returned memories to include in the prompt."

You can turn extraction off by passing `infer=False`, which makes Mem0 store the raw messages. If a memory you expected is missing, the first thing I'd check is which of the two modes the deployment runs in.

## How does Graphiti handle facts that change?

Graphiti stores memory as a graph in which every fact has a period when it was true. Zep, the company that builds Graphiti, uses it in Zep's hosted product, and the Graphiti docs list a bi-temporal model and fact invalidation among its features.

Graphiti's docs explain the design by pointing at Microsoft's GraphRAG, which they say was "primarily designed for static documents". A customer's plan is not a static document, and the enterprise-plan example above needs a store that can record that the enterprise fact stopped being true on the day of the downgrade.

An agent can act on a stale fact without knowing the fact is stale, which is why "what happens to the old fact?" is the question I'd ask of every framework in the table. [Memory versioning](/articles/memory-versioning/) shows one good answer, an append-only ledger that you can run.

Mem0's answer to that question is weaker than Graphiti's, and Mem0's docs say so. When a user says they moved from Austin to Seattle, Mem0 "can store the new fact without silently rewriting the old one", so both cities stay in memory until your code calls update or delete on the Austin fact.

## What is Anthropic's memory tool?

Anthropic's memory tool gives Claude a directory of files and leaves the storage to your application. Claude asks to create, read or edit a file under `/memories`, and your application carries out each request against storage that it controls.

The memory tool is the plainest of the four designs, and I mean that as praise. You can open one of its memory files in a text editor and read what the model saved, which is the same quality I liked in [DeerFlow's Markdown files](/articles/deerflow-memory/).

Letta's MemFS is a close relative of the memory tool: both store Markdown files, and Letta adds git history and the dreaming subagents.

The cost of plain files is retrieval. A directory has no ranking step, so whether Claude finds the right note next week depends on the file name it chose this week, and Letta's docs say MemFS likewise has no semantic or vector index by default.

## Can these frameworks be swapped over MCP?

MCP lets you swap the connection and not the data. Mem0 and Graphiti each publish a server for the [Model Context Protocol](/articles/model-context-protocol/), so an MCP client such as Claude Code can add and search memories in either one without custom code, and Graphiti's docs label their server experimental.

The stored memories don't transfer between the two. A sentence-sized fact in Mem0 and an edge between two entities in Graphiti's graph are different records, so moving from Mem0 to Graphiti still means exporting the facts and loading them again.

## How should you evaluate an agent memory framework?

Evaluate an agent memory framework by testing whether the agent does its job better with the memory than without it. Retrieval scores such as recall are the cheap first check, and a framework can pass that check and still leave the agent worse off.

[LongMemEval](https://arxiv.org/abs/2410.10813), from October 2024, is the benchmark I'd read before building my own test. Its authors split memory into indexing, retrieval and reading, and they report "a 30% accuracy drop" for commercial assistants and long-context models when the needed information is spread across long interactions.

Reading is the stage where the model uses what was retrieved, and it's the stage I'd make sure a test covers. The right facts in the wrong order can still produce a worse decision, for the reason [context windows vs memory](/articles/context-windows-vs-memory/) gives from the Lost in the Middle paper: where a fact sits in the prompt changes whether the model uses it.

So I'd build the test set around updates and contradictions. A customer who changed plans is a harder case than a customer who only stated a plan, and the changed plan is the case that produces a wrong invoice.

A pair of neighbouring pages covers what this page leaves out. [AI memory management](/articles/ai-memory-management/) covers what stays in the context window, and [short-term memory for AI agents](/articles/short-term-agent-memory/) covers memory within one session.

## FAQ

**What is the difference between agent memory and RAG?**

RAG retrieves from documents that already exist. Agent memory also writes, which means deciding which facts from a conversation to keep and which older fact a new one replaces.

**Is MemGPT still a thing?**

Yes, under the name Letta. The Letta repository describes the project as formerly known as MemGPT, and Letta's current docs have moved from the paper's memory blocks to a git-backed filesystem of Markdown files.

**Which agent memory framework should I start with?**

I'd start with the plainest design that fits, which for a single agent may be a directory of files like Anthropic's memory tool. Move to Mem0's extraction or Graphiti's graph when you can name a question the files can't answer, such as "which plan was this customer on in March?".

**Does a bigger context window replace a memory framework?**

LongMemEval's results say no, and the results are two years old. The paper reports the 30% accuracy drop for long-context models as well as for commercial assistants, and the models it tested are from 2024.

**Do agent memory frameworks support MCP?**

Mem0 and Graphiti do, and Letta does in a different way. Mem0 and Graphiti publish MCP servers for their memory, and Letta has a hosted MCP server through which another agent can create and message Letta agents.
