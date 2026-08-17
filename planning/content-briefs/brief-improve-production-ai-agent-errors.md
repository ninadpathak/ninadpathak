# Brief: improve `/articles/production-ai-agent-errors/`

**Type:** IMPROVEMENT to a live page. **Not a new article, and no new keyword research.**
**Cluster:** AI agents, memory, RAG, inference · **Experience: A**
**Queue position:** behind Codex's merge revisions and glossary backlinks.

## Why this page and not a row on the calendar

It is the only page on this domain that ranks for genuinely human demand. Both target queries are
measured in Search Console and both resolve here:

| Query | Impr | Clicks | Position |
|---|---:|---:|---:|
| `how do you handle errors when ai agents make mistakes in production?` | 11 | 0 | **10.6** |
| `how do companies debug ai agents that fail in production?` | 4 | 0 | **10.2** |

Position 10.5 on a question the page does not answer in its structure is worth more than any new
row. It needs no research: the queries are measured, the page is live, and connectivity is already
fine at 14 inbound and 3 outbound.

**The diagnosis in one line: the page ranks for a question it never asks.** It contains the phrase
`handle errors` **zero times** and the word `mistake` **zero times**, and it contains `diagnos`
**zero times** while ranking for a debugging query. Eight flat noun-phrase H2s, no FAQ schema, no
`takeaways`, and no `updated` since publication on 2026-04-16.

## Sequencing: do this WITH batch 3, not before

Two of its three outbound links point at pages this consolidation is merging:

- `/articles/memory-attribution-errors/` retires in **batch 1** and must be repointed to
  `/articles/ai-memory-management-for-llms/`.
- `/articles/why-ai-agents-keep-failing-in-production/` **merges into this page** in batch 3.

So batch 3 already rewrites this page. Doing the improvement separately means writing it twice and
risks the two passes disagreeing. **Fold this brief into the batch-3 merge revision.** The merge
brings in the failure survey; this brief decides the structure that survey lands in.

## 1. The opening claim: remove it

Current first line:

> Two years of running AI agents in production taught me that error handling separates a system
> that survives reality from one that falls over the moment something goes wrong.

This fails the 2c test. It claims two years of operating agents in production, which is a specific
engagement that did not happen. A reader who knows the subject can call it, and one such claim
costs the whole page. **Remove it. Do not soften it to "I have spent time around production
agents", which is unfalsifiable and worthless.**

The replacement is not a different claim. **It is the answer**, which the next section requires
anyway. Deleting the false provenance and leading with the direct answer fixes the voice problem
and the extractability problem in the same edit.

What may stay is judgment: the error taxonomy, the idempotency argument, and the non-negotiables
are positions he can hold as a technical writer who reads and documents these systems. What may not
stay is a claimed operating history.

## 2. The question-shaped heading and the direct answer

The page currently opens its substantive content with `## The core problem: agents are undefined
state machines`, which is a thesis, not an answer.

**Add an H2 that is the query, in the reader's words**, close to `How do you handle errors when an
AI agent makes a mistake in production?` Keep it a real question with a question mark. Google
already matches this page to that question; the heading makes the match explicit and gives an
answer engine something to quote.

**The direct answer goes in the first two sentences under that heading**, and it must name:

- the three error classes by name (transient, permanent, ambiguous), because classification is the
  actual first move and it is already the page's strongest section
- what each class does to the retry decision, in one clause each
- the state question: whether the agent can tell if the action completed

That passage has to survive being retrieved with no page around it. Name the subject in the
sentence rather than relying on the heading for the antecedent.

**Second question heading, for the debugging query:** something close to `How do you debug an AI
agent that failed in production?`. Its answer must name the artifacts a person actually reads: the
step trace, the tool call and its raw response, the state at the point of failure. The word
`diagnose` and the word `debug` should both appear in that section; neither `diagnos` nor `mistake`
appears anywhere on the page today.

## 3. Nested structure to replace the eight flat H2s

Eight sibling noun-phrases give a reader no map and give a retrieval system no hierarchy. Group
them under three question-shaped H2s, with the existing sections becoming H3s. **The existing
content mostly survives; this is re-nesting, not rewriting.**

| New H2 | H3s underneath, from the current page |
|---|---|
| `How do you handle errors when an AI agent makes a mistake in production?` | Classify errors first · Idempotent tool design · Timeout strategy |
| `How do you debug an AI agent that failed in production?` | Explicit state transitions · Checkpointing for long-horizon tasks · What actually breaks in practice |
| `What makes an agent recoverable rather than restartable?` | The core problem: agents are undefined state machines · The non-negotiables |

The third H2 is where the batch-3 merge lands: the failure survey from
`why-ai-agents-keep-failing-in-production` is the general pattern behind the specific recoveries,
so it belongs there rather than at the top.

## 4. FAQ schema: yes, and it costs nothing

`templates/post.html` emits `FAQPage` JSON-LD whenever a post has `faqs`, and `build.py`'s
`extract_faqs` populates that automatically from a `## FAQ` section using `### Question` or a bold
`**Question?**` line. **So adding an FAQ section is sufficient; no frontmatter edit is needed.**

Warranted here because the page ranks for two literal questions and has no FAQ at all. Four
questions, each answerable in two or three sentences, each genuinely distinct from the body:

1. `What is the difference between a transient and an ambiguous error?` — the distinction the retry
   decision turns on.
2. `Should an AI agent retry a failed tool call automatically?` — the idempotency answer, stated as
   a decision rather than a principle.
3. `How do you know whether an agent's action actually completed?` — the state question, which is
   the hardest one and the one with no clean answer.
4. `What should an agent do when it cannot tell whether it succeeded?` — the escalation path.

**Do not restate body text as an FAQ.** An FAQ answer that duplicates a section is padding and the
slop reviewer will reject it.

## 5. Also set while there

- **`updated`**, but only after the claims are re-verified. `build.py` substitutes the publication
  date when `updated` is missing, so a false freshness date is worse than none.
- **`takeaways`**, which the template renders as the "short version" block. Three, each a standalone
  claim rather than a topic label.
- **Preserve the completed batch-1 repoint** to `/articles/ai-memory-management-for-llms/`;
  `/articles/memory-attribution-errors/` is a merged source and must not return to the draft.
- **Two outbound links minimum** must survive the batch-3 merge, since one of the three current
  targets is being absorbed into this page and one is being retired. `agent-harnesses` survives;
  a second live target is needed. `tools/check_link_retrofit.py` enforces this.

## What this brief does not do

It does not chase a keyword. The position is already 10.5 and the demand is measured, so the work
is making the page answer the question it already ranks for. **No new research, no new row, no
title change to the URL.** The slug stays.
