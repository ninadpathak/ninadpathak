---
category: technical-documentation
primary_query: none
siblings:
- documentation-review
- shorter-documentation
- written-by-a-human
bridges:
- slug: eleven-rejected-essay-drafts
  reason: That essay reruns the prompt behind the writing errors discussed here.
date: 2026-11-23
description: "A checker passed three drafts I’d rejected. The Claude Code docs team’s pitfalls list shows what a check can catch when there’s a product to test."
slug: pitfalls-list-for-ai-drafted-docs
status: published
title: "What happens when you keep a list of your AI writer’s mistakes"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write the developer documentation for your AI product. [Talk to me](/services/developer-documentation/)."
---

My writing checker passed an opening where I'd told the model it made up the narrator's surprise. It also passed an opening I'd rejected for trying to explain the whole essay up front.

Sarah Deaton keeps a list of mistakes in the Claude Code docs too. In one case, the same setting had two values in two source files.

Claude had copied the first value and missed the override. I wanted to see what her team could teach a checker to look for, and where I'd still want a person to read the draft.

[Deaton’s interview with Tom Johnson](https://idratherbewriting.com/blog/podcast-deaton-anthropic-tw-automation)

## Record where the wrong value came from

For [technical documentation](/articles/technical-documentation/), the wrong value can end up in a reader's configuration. That's an error I'd want someone to be able to reproduce.

Claude read a value in one source file and wrote it down. A second file overrode it.

In another case, Claude described a feature as available to everyone after missing the flag that limited it to certain customers.

Deaton traces each false claim back to the place Claude went wrong. For the flag, that meant telling it where flags live and which customer levels they control.

The team’s `verify-docs-PR` skill can use those paths when checking a new pull request.

I'd write the entry so that another reviewer can repeat the check. Put the false claim next to the correct one and name the file or test that settles it.

That’s also how I use a claim ledger when [reviewing a single docs page](/articles/documentation-review/).

## A draft can fail in a way no word list catches

A rule about length has a related problem. A model can follow it for a few turns while the same padding comes back later.

[The case for shorter documentation](/articles/shorter-documentation/)

My [writing skill’s feedback log](https://github.com/ninadpathak/ninadpathak/blob/main/skills/writing/references/essay-research/feedback-log-2026-09-05.md) records the draft, my complaint, and what had to change. The checker failed seven of the ten excerpts it ran on.

It flagged banned words in five drafts and number-first sentences in two.

These were the drafts it passed.

| Draft | Failure to catch | Repair required |
|---|---|---|
| 4 | "Open a fresh Claude Code session"; "[N]k of the 200k-token window." | Assume daily use. Use checked numbers only when their magnitude matters. |
| 6 | An intro dispensing compaction, cost, and the rest of the article. | Establish circumstances and purpose; leave an investigation for the body. |
| 7 | A narrator surprised that something besides their own messages filled context. | A discovery must be worthy of the claimed experience. Ordinary behaviour is shared knowledge. |

The script also failed draft 11, the one I had liked best in the log. I'd keep the checker for errors it can describe precisely.

For the rest, I need to read as the intended reader and see where the draft loses me. [What happened when I reran the essay prompt](/articles/eleven-rejected-essay-drafts/)

## Sometimes the page needs the fix

Deaton gave an example of a docs assistant picking up a number in a table and calling it a default. The column header said it was an example.

If a reader gets the number without the heading, there’s nothing beside the number to tell them which it is.

On November 23, 249 of 250 entries in the [Claude Code settings reference](https://code.claude.com/docs/en/settings-reference) had a line labelled Default apart from the JSON example. The remaining entry was marked removed.

I don't know which table the assistant misread, but I'd copy the reference’s habit of labelling the value right where it appears.

## Look for the same mistake in the published pages

Deaton says a person approves each docs pull request and false claims still slip through. A list grows when someone spots a mistake, so it can't tell the team how many errors nobody has found.

When a wrong claim earns an entry, I'd also search the published docs for claims that came from the same source. If the error was a flag, read the other places that describe who can use that feature.

Fixing those pages is the one part of a new pitfalls entry that helps readers who have already landed on the docs.

I'd show the check a reader can repeat, whoever drafted the page. [What a reader can tell from Ghostty’s release notes](/articles/written-by-a-human/)
