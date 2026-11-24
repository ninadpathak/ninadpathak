---
category: developer-experience
primary_query: none
siblings:
- technical-writing-for-engineers
- writing-for-ai-products
bridges:
- slug: pitfalls-list-for-ai-drafted-docs
  reason: That essay repeats the log's diagnosis of draft 3, which this one reruns on a current model.
- slug: claude-code-skills
  reason: That page takes apart the skill folder these drafts were written from.
date: 2026-11-23
description: "I rejected ten essay openings. A later test showed how much repetition and invented experience a model picked up from the author’s name alone."
slug: eleven-rejected-essay-drafts
status: published
title: "What I learned from rejecting ten AI-written openings"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write technical articles for a developer audience. [Get in touch](/services/technical-articles/)."
---

Draft seven opened with a memory I didn't have. The narrator was `[N]` messages into a Claude Code session in `[month]` and was surprised that more than their own messages had filled the window.

I'd asked the model for backstory.

What I wanted was an explanation for someone who already used Claude Code every day.

I kept [notes on eleven attempts](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/essay-research/feedback-log-2026-09-05.md) while writing my essay skill. Rereading them, I wanted to see how much of the bad writing I'd asked for.

I started by rerunning the prompt with and without the instruction to write like Paul Graham.

## What the author’s name put in the draft

I wrote the skill to help with [developer content](/articles/developer-experience/), including essays a working engineer might read without having been assigned them.

<!-- evidence-three: Draft 3 is the name used in the linked feedback log. -->
The old skill listed two sentence patterns to imitate. The first corrected a description by denying it and supplying another.

The other asked why something would happen and began its answer with “Not because.” I blamed that list for the repetition in draft 3, and repeated the diagnosis in [my essay on pitfalls lists](/articles/pitfalls-list-for-ai-drafted-docs/).

The November test started with a brief for four opening paragraphs. It named the topic and told the model what the readers already knew.

```text
Write the first four paragraphs of an essay titled "Claude Code Context Window: What Fills It, What It Costs". The readers are senior engineers who use Claude Code every day. Reply with the four paragraphs only.
```

I compared that brief with versions that named Paul Graham, named him and listed the moves, or named him and banned the first move. Each brief got the same number of runs in Haiku 5.5, with Claude Code 2.1.330 and tools and skills disabled.

To count as a pair, one sentence had to reject a description and the next had to begin with “It” or “They” and supply another.

<!-- evidence-three: Each brief ran three times in the November 23 test, and the counts below come from the saved outputs. -->
| Across each brief's three runs | No author named | Style | Moves | Ban |
|---|---|---|---|---|
| Pairs in each run | 1, 1, 0 | 3, 3, 3 | 4, 3, 3 | 1, 0, 0 |
| Runs with a "Why" question answered by "Not because" | 0 | 0 | 3 | 0 |
| Runs that open on a claim about the majority | 0 | 3 | 2 | 2 |
| Runs with a narrator who used Claude Code "for months" | 0 | 2 | 0 | 1 |

Naming Graham was enough to get the first pattern in every run. Listing the moves brought in the second pattern too.

Banning the first reduced it to one instance across the runs, but it still left openings that guessed what a majority of engineers knew. Some drafts also invented a narrator who'd used Claude Code for months.

The September draft came from the whole skill and the log doesn't name its model. I can say what changed when those lines changed in November.

I can't tell which line caused the earlier draft.

## What I was telling the model to fix

A checker can help with some of the rules in [writing for engineers](/articles/technical-writing-for-engineers/). It still needs a reader to tell it when an explanation starts too far back.

After draft 4 I told it the reader already knew enough about context windows to search for them. The next draft skipped the lesson and guessed how much room different parts of a session used.

When I asked for backstory, I got the surprised narrator. When I asked for first principles, the model opened with “A language model remembers nothing between calls.”

Each correction gave it something specific to stop doing. I hadn't shown it a passage where a writer gets straight to the question a daily user has.

The [essay reference](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/essay.md) now puts sentences from the documentation register beside the same facts said aloud. I'd start the next brief with a pair like that and with the evidence the essay can use.

## The draft I liked caused trouble too

I left no complaint on draft 11. Later trials took that as permission to reuse the opening about sending the retained conversation with each request.

The notes called it a voice sample, and the [trial notes](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/essay-research/test-rounds.md) show the same opening turning up again and again.

It also claimed to have measured a session when the notes record no measurement. I should have marked the part I liked and checked the claims before holding it up as a sample.

Next time I'd save the brief, the model version, and the date beside the drafts. I'd mark the lines worth learning from, then give it a different topic and see whether it can use the lesson without reusing the opening.

I'd keep those runs in the reference folder for the [Claude Code skill](/articles/claude-code-skills/) and include the model and date, like I would for an example in [technical writing for AI products](/articles/writing-for-ai-products/).
