---
category: technical-documentation
primary_query: none
siblings:
- documentation-review
- shorter-documentation
- written-by-a-human
date: 2026-11-23
description: "Sarah Deaton traces each false claim in the Claude Code docs to its cause and adds it to a pitfalls list. I keep the same kind of list for my writing skill. Its checker, run on ten logged drafts, passed drafts 4, 6 and 7, which I had rejected."
slug: pitfalls-list-for-ai-drafted-docs
status: published
title: "Comparing the Claude Code docs pitfalls list with my own"
work_note: "When a model drafts the docs, somebody still has to check each claim against the product. I'm Ninad Pathak, a freelance technical writer, and I run the commands on a page before your engineers review it. [Talk to me about developer documentation](/services/developer-documentation/)."
---

Sarah Deaton is a technical writer at Anthropic who works on the Claude Code docs, and on [a podcast episode Tom Johnson published on August 2](https://idratherbewriting.com/blog/podcast-deaton-anthropic-tw-automation) Deaton said Claude now drafts those pages and a person approves each merge.

The practice I'd copy first is a file Deaton calls a pitfalls doc. It lists the places the docs have been wrong, and a skill called `verify-docs-PR` checks docs pull requests against it.

I keep the same kind of list for the agent skills I write with, and on November 23 the skills and the list went into [this site's public repository](https://github.com/ninadpathak/ninadpathak/tree/main/skills). Deaton's list records false claims about a product and mine records drafts that read as generated or invented, so I put the two side by side.

Johnson marks the episode's show notes as AI-generated, so everything I attribute to a speaker comes from the transcript on that page. Reviewing a model's draft for false claims is now part of the job in [technical documentation](/articles/technical-documentation/).

## A pitfalls entry records where one false claim came from

I think the list works because it's built from specific false claims, each traced back to how it got written. Deaton sends a wrong claim to Claude Tag, the Claude integration for Slack, and describes the job as "trace every single false claim", including claims that the docs site's AI assistant makes in an answer.

Asked by Johnson for root causes, Deaton gave two from Claude's work. Claude had read a value set in one source file and missed a second file that overrides it, and Claude had described a feature as available to everyone when a feature flag limited it to certain customers.

Deaton's repair for the feature-flag error was to write down where feature flags are set and the customer levels behind them, and Deaton said the error got through until then.

The [essay reference](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/essay.md) in my writing skill has a failure table built the same way, with eleven rows, one per draft. Each row names what failed in that draft and the repair it required, and a separate [feedback log](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/essay-research/feedback-log-2026-09-05.md) keeps my corrections word for word.

A trace can end at your own instructions. Under the third draft, the log's diagnosis is that the skill had listed two of Paul Graham's sentence patterns as moves to imitate, and the recorded repair is to cap each pattern at once per piece or take it off the skill's list.

## A false claim about a product has source code to check it against

I think a tool can enforce Deaton's list in a way it can't enforce mine, because a false claim about a product can be checked against the product's source code. The `verify-docs-PR` skill holds the pitfalls plus the paths in the source code where different facts live, and it sends any incorrect claim it finds to Slack to be added to the list.

But a draft that reads as generated has no source file to check against, so the test is a person reading it. To see how much of my list a script can enforce, the skill's checker, [`check_prose.py`](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/scripts/check_prose.py), ran on November 23 with Python 3.12.3 on the ten draft excerpts quoted in the feedback log.

The script failed seven of the ten, five for a word on the skill's banned list and two for a sentence that begins with a number word. It passed drafts 4, 6 and 7 with `result: pass (0 failures, 1 notes)`, and these are the rows the failure table keeps for those drafts:

| Draft | Failure to catch | Repair required |
|---|---|---|
| 4 | "Open a fresh Claude Code session"; "[N]k of the 200k-token window." | Assume daily use. Use checked numbers only when their magnitude matters. |
| 6 | An intro dispensing compaction, cost, and the rest of the article. | Establish circumstances and purpose; leave an investigation for the body. |
| 7 | A narrator surprised that something besides their own messages filled context. | A discovery must be worthy of the claimed experience. Ordinary behaviour is shared knowledge. |

Those rows are judgments about what the reader already knows and what an intro is for, and a word list can't test either. The script also failed draft 11 on two banned words, and the log marks draft 11 as the closest attempt with no complaint recorded.

So the script passed drafts I'd rejected and failed the one that came closest, and the skill's [`checking.md`](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/checking.md) calls my reading of a draft "the standard no grep detects".

Deaton has a style rule that no check enforces yet. The reader should be the actor in each sentence, and Deaton said that rule isn't codified in a skill.

## A rule without its example gets followed in one place

I'd give a model the bad sentence and its rewrite before I'd give it another rule, because a rule alone gets obeyed in the sentence it was aimed at and broken somewhere else. My `checking.md` records a run of prohibitions against filler and buildup that each "produced local compliance and recurrence elsewhere", and says my own rewritten passages moved the work further than any of them.

Deaton gave one rewrite for the reader-as-actor rule aloud on the podcast, where a sentence saying a hook will do something for you becomes one telling you to enable the hook. Deaton already leaves suggestions on pull requests in GitHub, so those before-and-after pairs exist, and I'd show the drafting skill a few of them before writing the rule another way.

The [case for shorter documentation](/articles/shorter-documentation/) has a public case of a rule wearing off, a brevity skill that a Hacker News user said held for a few turns before the verbosity returned.

## A list covers only the errors someone already found

A pitfalls list holds only the errors someone has already found, so I wouldn't let a clean check stand in for a person's approval. Deaton made the same point about the time-to-correction metric, which runs from the moment a false claim is introduced to its correction and can count only the claims somebody found.

My `checking.md` carries the same warning, "A checker only finds what it was told to look for", and it records that the first pass over the skill never counted dashes and let thirty-one through.

Deaton's setup requires a human's approval in GitHub before a docs pull request merges, and Deaton said errors have still slipped past that review.

Fabrizio Ferri-Benedetti, the episode's co-host, said they work differently, trusting the model's output and reviewing it later, and allowed that some areas can't accept that. I'd put product docs among those areas, because whoever reads the page between the publish and the review acts on the false claim.

The claim ledger in my [documentation review checklist](/articles/documentation-review/) does for one page what `verify-docs-PR` does for a pull request, as a table where each claim has to point at a source outside the draft.

My essay on [Ghostty's hand-crafted release notes](/articles/written-by-a-human/) argued that a technical reader wants proof a page was tested more than proof of who typed it, and a pull request checked against a list of past errors carries that kind of proof.

## What I'd copy from the Claude Code docs workflow

I'd copy the pitfalls list first, because it's a text file, and I'd add each entry on the day the error is found. My skill's rules are to add a newly named tell to the checker's lists the same day and to sweep for the whole family of an error, since fixing the one line someone pointed at leaves the others in place.

The episode doesn't say whether a new pitfall sends Claude back through the published Claude Code pages for the same cause, and that sweep is the step I'd add.

I'd also collect corrections where Deaton does, in GitHub review comments that can feed back into a skill. A Slack channel counts those corrections per pull request every day, which my own log doesn't do.

Deaton's advice to label values came from an AI assistant that kept reporting an example value as the default, because a table column held a number and the assistant skipped the header that marked it as an example.

I checked the [Claude Code settings reference](https://code.claude.com/docs/en/settings-reference) on November 23, and 249 of its 250 key entries have a line labelled Default, separate from any JSON example. The one entry without that line is a key the page marks as removed.

Deaton didn't name the table, so I can't say the settings reference is the page that assistant misread.

Deaton works at Anthropic and runs the drafting and the review on Claude with what Deaton called "unlimited tokens", so the episode can't tell you what the pipeline costs. The daily release job alone runs for about two hours, and a team that pays per token should measure that job before copying it.
