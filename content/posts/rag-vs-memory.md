---
category: agent-memory
primary_query: rag vs memory
siblings:
- ai-memory-management
- memory-versioning
- voice-agent-memory
bridges:
- slug: llm-context-windows
  reason: The context window limit is the reason an agent needs memory.
- slug: hybrid-search
  reason: A memory read path is a retrieval problem.
date: 2026-04-19
description: RAG selects evidence for one request and memory governs state across requests. This page argues that memory which only recalls is RAG over old chats, and shows how to run both in one request.
status: published
work_note: "I write tutorials and technical articles for AI companies, and I run the product before I write a line. I'm Ninad Pathak, a freelance technical writer, and [we can work together](/services/freelance-technical-writer-for-ai-companies/)."
title: 'RAG vs Memory: What AI Developers Need to Know'
updated: '2026-11-16'
slug: rag-vs-memory
---

<!-- evidence-three: October 3, 2026 is the publication date printed on liao.gg/blog/agents-dont-need-memory -->
"It's All Just RAG" is a section heading in [a post Kevin Liao published on October 3](https://liao.gg/blog/agents-dont-need-memory) about memory plugins for coding agents. RAG selects source evidence for the current request, and memory governs state that has to survive, change or expire across requests, so the heading is an accusation that these products store and recall and do nothing else.

I joined Mem0 in February 2026 and ran a team of 13 writers there, and Mem0 sells this kind of memory layer, so weigh what follows with that in mind. My argument is that the replacement Liao built is a memory system by that definition, and a better one than the plugins the post attacks.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/rag-vs-memory/two-inputs.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/rag-vs-memory/two-inputs.narrow.svg" width="288" height="560"><img class="np-has-narrow" src="/static/images/diagrams/rag-vs-memory/two-inputs.svg" width="720" height="600" alt="Two inputs feed one bounded context window before the model. Retrieval selects source evidence from documents for the current request. Memory supplies saved state that must survive, change, expire, or return across requests." loading="lazy" decoding="async"></picture></a>
  <figcaption>RAG selects evidence for this request, and memory governs state across requests. Both land in the same bounded context.</figcaption>
</figure>

## What is the difference between RAG and memory?

RAG answers "what do the sources say about this question", and memory answers "what is still true about this user or task". Both put text in front of the model, and both can sit on the same vector index.

[AI agent memory](/articles/agent-memory/) is the work of keeping the answer about the user or task current.

| | RAG | Memory |
| --- | --- | --- |
| Job | Select evidence for one request | Keep state across requests |
| Source of truth | A corpus someone else maintains | Records the application wrote itself |
| Goes stale when | The corpus is reindexed late | A later fact contradicts an earlier one |
| Needs | Retrieval, ranking, citation | Write rules, supersession, expiry, access scope |
| Failure looks like | A confident answer from the wrong passage | An old preference returning as if it were current |

A retriever isn't supposed to decide whether a document is still true, because the corpus owner is meant to have done that. A memory layer has nobody else to ask.

The [context window](/articles/llm-context-windows/) owns neither job. It is the container both land in, and a large one doesn't decide which of its contents is authoritative.

## Is agent memory just RAG?

A memory system that recalls by similarity alone is RAG over transcripts, and the plugins Liao describes work that way: they cut session transcripts into snippets, store them in a vector database, and "On every prompt, retrieve the top 5 and inject". The post's two sharpest complaints about the result are "The past is treated as truth." and "Agents can't search for what they don't know."

Liao's replacement is Operator, a workspace of Markdown documents the agent reads before a task and maintains after it. The storage is the least interesting part, and the rules are where the post answers its own complaints.

| Liao's complaint about memory plugins | Operator's rule, in the post's words | What that rule is |
| --- | --- | --- |
| "The past is treated as truth." | "Facts should be rewritten when truth changes. No appending." | Supersession |
| "Agents can't search for what they don't know." | "At the start of every session, Operator only injects this lean catalog into context" | A read policy |
| Every transcript is mined into snippets | Agents are directed "to record only what the code cannot provide" | A write rule |

Supersession, a read policy and a write rule are needs listed under Memory in the first table, so a post titled against memory ends up specifying a memory system. The post shows that recall without those rules fails, which criticizes the plugins and supports the idea of agent memory.

A Hacker News commenter, CapitalistCartr, went from objection to agreement inside a single reply the next day. It [starts with the obvious objection](https://news.ycombinator.com/item?id=49953780), "it look to me like his objections apply to his own solution", and ends, after a look at the repository, on "Every scope has a catalog file".

Anthropic's [The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory), from November 6, adds a result on the write rule. Each model got one run of Pokémon Red with a folder of memory files, and "Sonnet 3.7 wrote 413 memory files across 225 folders and earned one badge", and Fable 5 wrote nine files plus a top-level `global.md` and earned four.

A pair of runs from very different models proves little about retrieval, and the comparison never varies it. They do show what the stronger model chose to write: strategy and tested rules, with nothing it could read off the screen.

Liao and Anthropic disagree on who should repair a bad note. Liao wants documentation written by the working agent with the full picture still in context, "Not some background "dreamer" agent.", and Anthropic's post calls its repair pass dreaming and uses it to check notes against the original transcripts.

Anthropic's reason is that "a note that's wrong from the start or that drifts as the environment changes can be read, and trusted, by Claude in a later session." A note that was wrong when the working agent wrote it is the case a rewrite-on-change rule can't catch, so I think a serious memory system ends up needing both.

"RAG vs memory" is a question about who is responsible for truth over time. Under RAG the corpus owner is, and under memory your application is, whatever the files look like.

## How do RAG and memory work together in one request?

A RAG pipeline with memory reads memory first to shape the question, retrieves evidence second, and treats the memory write as a separate decision at the end.

1. **Read scoped memory.** Apply identity and access rules before any similarity search, and return only state relevant to this task.
2. **Retrieve evidence.** Use that state to form a better query against the external corpus, because a stored constraint can name the service and only the documentation can say what the service supports.
3. **Assemble a bounded context.** Label which passages are memory and which are sources, and decide in advance which wins when they conflict.
4. **Answer from evidence.** Citations point at source records, never at a memory summary of them.
5. **Decide the write separately.** Nothing becomes durable because the model said it, so the application decides what is worth storing and what it replaces.

The write decision in step five is where the 413-file run went wrong. The [five-layer memory hierarchy](/articles/ai-memory-management/) covers which kinds of record deserve which rules.

Keeping every version of a record, so that a correction can be traced, is the job of [memory versioning](/articles/memory-versioning/). The rules change again for [voice agent memory](/articles/voice-agent-memory/), where a caller can cut a reply short.

## Which retrieval methods does agent memory need?

Agent memory needs dense search for meaning, lexical search for exact identifiers, and metadata filters for anything that must never be approximate. Agents make retrieval harder than human search does, because an agent forms its query partway through a task.

A person asks "What were the deployment steps for this service?", and an agent that has already tried the deployment asks "What failed last time?" Both need the same record from different starting points, so a test set built from polished human questions hides the mismatch.

| Problem | Method | What it can't do |
| --- | --- | --- |
| Query and record use different words | Dense retrieval | Match an exact error code |
| An identifier must match exactly | Lexical retrieval such as BM25 | Find a paraphrase |
| Tenant, time range or permission | A metadata filter applied before ranking | Rank by relevance |
| The query lacks the document's vocabulary | [HyDE](/glossary/hypothetical-document-embeddings-hyde/), which embeds a drafted answer | Serve as evidence, since the draft is invented |
| Constraints are buried in a sentence | [Self-querying retrieval](/glossary/self-querying-retrieval/), which splits search text from typed filters | Grant access the caller lacks |

Anthropic's [Contextual Retrieval explanation](https://www.anthropic.com/research/contextual-retrieval) uses an error code to show the dense and lexical split, and the [hybrid search guide](/articles/hybrid-search/) covers merging the two result lists. The metadata filter is the method a similarity score can't replace, because an embedding score can't prove a record belongs to the current tenant.

## How do you test RAG and memory together?

Test retrieval, answer use and memory writes as separate assertions, on queries captured from the agent mid-task. Each fixture holds the agent's goal and partial state at that step, the exact query it generated, and the records and access scope that should apply.

Retrieval checks ask whether expected records appear and forbidden ones stay out. Answer checks ask whether the model used that evidence and respected the stored constraints.

The write gets its own assertions: whether the fact was allowed to be stored, whether the conversation supports it and when it expires. A correct answer can produce no durable update at all, and the Pokémon runs suggest that is often the right outcome.

## Should you use RAG, memory or both?

Use RAG when the answer lives in a corpus, memory when state has to return later, and both when stored state shapes the question and outside evidence answers it. Which database holds the records is the last thing to decide.

| The request needs | Use | Because |
| --- | --- | --- |
| Documentation, code, policy or another corpus | RAG | The answer can be checked against the selected records |
| A preference, a prior outcome or a standing constraint | Memory | Your application has to decide what gets stored, what replaces it, when it expires and who can read it |
| Stored state to form the question and sources to answer it | The loop above | Memory shapes the query, and the sources stay the evidence |

Mads Thines's [Agent memory needs its OpenTelemetry moment](https://www.lorekit.io/blog/open-agent-memory-format), from November 7, compares nine memory formats and reduces them to one idea: "a note an agent left for its future self, stored at some address, true for a while." The last four words are the definition of memory worth keeping, and they are the part no retriever supplies.

The same survey shows how little agreement there is on forgetting. Instruction files such as AGENTS.md forget only when a person edits them, and GitHub Copilot's repository facts are "Deleted after 28 days unused".

So the practical test for any memory product is to ask what happens to a fact after it stops being true. Operator has an answer, which is to rewrite the fact, and the top-five-snippets pipeline has none.
