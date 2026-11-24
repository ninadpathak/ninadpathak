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
description: "My essay skill's log holds eleven openings a model wrote in September and my corrections on ten of them. I reran the brief on Haiku 5.5, and the words \"Paul Graham's style\" alone produced the sentence pattern I had rejected, three times in every run."
slug: eleven-rejected-essay-drafts
status: published
title: "Rereading the log of eleven drafts behind my essay-writing skill"
work_note: "I use AI to prepare research and to attack a draft, and I check the product myself before I sign off on a claim. I'm Ninad Pathak, a freelance technical writer, and I write explainers and comparisons for engineers who will check them. [Ask me about an article](/services/technical-articles/)."
---

On September 5 and 6 of 2026, a model wrote eleven essay openings from a skill file I was building, and I read each one. I complained about ten of them, and the log marks the eleventh "no complaint yet; closest so far".

The skill is a folder of instructions for a model, and my [Claude Code skills](/articles/claude-code-skills/) page takes that folder apart file by file. Its essay file tells a model how to write in Paul Graham's register, and the [log of my corrections](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/essay-research/feedback-log-2026-09-05.md) went public on November 23 with [the rest of the skills I write with](https://github.com/ninadpathak/ninadpathak/tree/main/skills), next to the notes a model kept while it rewrote the skill.

I write [developer content](/articles/developer-experience/) with these skills, and a model following the essay skill drafted this piece. So I reread the log to find what in my instructions had produced each bad draft, and then a brief of my own ran on Haiku 5.5 on November 23 to test the log's answer.

<!-- evidence-three: "draft 3" is the feedback log's own number for the third of its eleven drafts, a label and not a count, and the log's entry for that draft says the model used the two patterns three times in four paragraphs -->

## The log blames a list in the skill for draft 3

The log's diagnosis of draft 3 is that the skill had listed two of Paul Graham's sentence patterns as moves, and I think that diagnosis is half right. The patterns are these, and draft 3 used the first one three times in four paragraphs:

- `X is not Y. It's Z.`
- `Why would X? Not because Y.`

My [comparison with the Claude Code docs pitfalls list](/articles/pitfalls-list-for-ai-drafted-docs/) repeated that diagnosis without testing it.

The rewrite on September 6 took out the skill's quotas, such as a deadline for the thesis at word 60, and removed the two patterns as things to draft with. The [rewrite's notes](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/essay-research/decisions.md) say it chose that over allowing each pattern once per essay.

## Naming Paul Graham was enough to produce the pattern

<!-- evidence-three: the twelve runs of November 23 were four briefs at three runs each, and every run of the style brief has three pairs in its four paragraphs, as the table below shows --> On Haiku 5.5, the sentence "Write it in Paul Graham's style." produced the first pattern three times in four paragraphs with no list in the brief. The test was four briefs, each run three times on November 23 with Claude Code 2.1.330, as `claude -p --model haiku` with the system prompt replaced by "You are a writer." and tools and skills switched off.

<!-- evidence-three: drafts 3 to 11 are the feedback log's own draft numbers, labels and not a count --> The first brief uses the title of the log's drafts 3 to 11:

```text
Write the first four paragraphs of an essay titled "Claude Code Context Window: What Fills It, What It Costs". The readers are senior engineers who use Claude Code every day. Reply with the four paragraphs only.
```

The other three briefs each add text before the last sentence:

- The style brief adds `Write it in Paul Graham's style.`
- The moves brief adds the style sentence and `Paul Graham's moves include "X is not Y. It's Z." and "Why would X? Not because Y."`
- The ban brief adds the style sentence and `Do not use the "X is not Y. It's Z." construction.`

A pair counted when a sentence denied one description and the next sentence started with "It" or "They" and gave another. A script listed the candidates and I read each one, the same split [my writing guide for engineers](/articles/technical-writing-for-engineers/) makes between rules a script can check and habits it can't.

<!-- evidence-three: each brief ran three times on November 23, and every cell is a count read from that brief's three saved outputs -->
| Across each brief's three runs | No author named | Style | Moves | Ban |
|---|---|---|---|---|
| Pairs in each run | 1, 1, 0 | 3, 3, 3 | 4, 3, 3 | 1, 0, 0 |
| Runs with a "Why" question answered by "Not because" | 0 | 0 | 3 | 0 |
| Runs that open on a claim about the majority | 0 | 3 | 2 | 2 |
| Runs with a narrator who used Claude Code "for months" | 0 | 2 | 0 | 1 |

<!-- evidence-three: the table above gives the style brief 3, 3, 3 pairs and the moves brief the "Why" pattern in all three of its runs --> So the style sentence alone gave three pairs in each run, and the list's clear addition was the second pattern in all three of its runs.

<!-- evidence-three: the narrator row of the table above adds up to three runs, two under the style brief and one under the ban brief --> Of the nine runs that named Paul Graham, seven open on a claim about the majority, the fault I rejected draft 5 for, such as the run saying the majority of engineers who use Claude Code every day "have never looked inside its context window". And in three runs a narrator nobody asked for has used Claude Code "for months" before looking at what filled the window, the surprised author I rejected in draft 7.

Draft 3 came from a model working from the whole skill, so these runs are evidence about a brief and leave the cause of draft 3 open. In them, taking the list out left the pattern in, and a ban took it down to one pair across three runs.

## Each correction named one fault and the next draft had another

I think my corrections were a second cause, because each one named a single fault and the next draft arrived with a different one. After draft 4 I wrote, "The person reading the topic already knows about context windows enough to search about it."

Draft 5 stopped telling the reader to open a session and opened on a claim about the larger share of the window. After draft 6 I asked for "the backstory, the narrative" in an intro, and draft 7 brought the narrator who is surprised by a full window.

After draft 8 I wrote "write from first principles", and draft 9 opened with "A language model remembers nothing between calls." I called that one dumbed down, and the log doesn't record what was edited in the skill between any two of drafts 4 to 11.

<!-- evidence-three: the ban brief ran three times on November 23, and the table above has the majority claim opening two of those runs --> My ban brief behaved the same way. The claim about the majority still opened two of its three runs and the narrator appeared in one, so a correction that names one fault leaves the model's other defaults where they were.

The rewrite's notes record a trial draft on a second topic that avoided the banned quantifier and still overclaimed, and they say its failure "required an evidence rule, not another keyword ban".

The [essay reference](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/essay.md) now carries four sentences in documentation register with the same fact said aloud beside each. I'd start there next time, because nowhere in the log is there a sentence of mine showing the draft I wanted.

## The draft I didn't complain about became a template

<!-- evidence-three: test-rounds.md records three rounds on the Claude Code context window title, so three trial openings on that topic --> The trial drafts written after draft 11 reused its opening, and I'd warn about this cause first because it starts when a draft is approved. The rewrite's notes treat draft 11 as the accepted anchor, and all three [trial openings](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/essay-research/test-rounds.md) on that topic begin on draft 11's first fact, that Claude Code sends the retained conversation with every request.

The notes for the next pass record that trial as rejected and keep draft 11 as "a voice anchor, not blanket endorsement of its opener or its technical claims". The next trial opens on clearing a session halfway through a bug.

I had no complaint about draft 11, which ends on the words "measured one session", and the notes say no session was measured. They also say Claude Code's documentation, checked on September 6, doesn't support the flat five-minute cache lifetime in the draft.

So when a draft is approved, I'd tell the model which sentences to learn from and what it must not reuse, starting with the opening and the numbers. The skill's [checking reference](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/checking.md) has the short version, which is to describe a sample's mechanics and never paste it.

## What one reviewer and eleven drafts can show

The log can show which instruction came before which draft. It holds one reviewer's reactions to openings on two topics, so the fair objection is that it records my taste.

Part of it is taste, such as "still trying too hard rather than explaining like you understand it" on draft 10. Part of it can be checked, such as the bill that draft 1 invented and the measurement that draft 11 claimed.

The log can't show cause, because it doesn't name the model and no draft was regenerated with one instruction changed. The later trial rounds were reviewed by the model that wrote them, and their notes call them "sequential self-tests".

<!-- evidence-three: the twelve runs of November 23 are four briefs at three runs each, and three earlier runs that day used a first wording of the moves brief --> My page on [technical writing for AI products](/articles/writing-for-ai-products/) asks that an example's output be printed with the model snapshot and the date. My own log fails that test, and my twelve runs are three per brief on one small model, after three with an earlier wording of the moves brief.

The rewrite's trials are all introductions, and its notes say they don't establish that a model can keep the reasoning up over a complete essay.

<!-- evidence-three: three is the number of runs each brief got in this post's test on November 23, repeated here as the suggested count --> Before I add another rule to this skill, I'd run the bare brief three times on the model that will use it and read what the author's name brings in. Then I'd write the model and the date in the log beside each draft.
