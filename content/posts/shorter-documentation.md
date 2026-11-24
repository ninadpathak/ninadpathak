---
category: technical-documentation
primary_query: documentation length
siblings:
- writing-changelogs
- documentation-headings
- written-by-a-human
bridges:
- slug: agent-harnesses
  reason: The agent harness page is the worked example of the structure described here.
- slug: agents-reading-docs
  reason: A docs page now has agent readers.
date: 2026-04-04
description: 'A reader arrives with one task, so shorter documentation serves them better. Give each page one job and move the rest to a page of its own.'
status: published
work_note: "I'm Ninad Pathak, and I freelance as a technical writer for developer-tool companies. Docs run long, more so now that models draft them, and cutting a page down without losing what's true is work we can [do together](/services/)."
title: The Case for Shorter Technical Documentation
updated: 2026-11-16
slug: shorter-documentation
---

Simon Willison wrote on November 9 about [hiding agent-written pull request descriptions behind a details tag](https://simonwillison.net/2026/Nov/9/details-summary/). The descriptions are accurate and thorough, and the reaction the post reports is one I've had to agent-written text all year: "I'm not reading all of that".

Shorter documentation works better because a reader arrives with one task, and every sentence that doesn't serve it is something they have to read past and you have to keep true. Willison's fix applies that to pull requests by keeping the full text one click away and choosing an opening that is "the shortest text a human can read that will help get them up to speed."

The argument covers every kind of [technical documentation](/articles/technical-documentation/), from a README to a reference page.

That was the argument before 2026 too. Agents then made length free to produce, so a long page stopped showing that someone worked on it, and [my essay on written-by-a-human labels](/articles/written-by-a-human/) follows what readers trust in its place.

## Why is shorter technical documentation better?

Shorter documentation is better because it spends the reader's attention on the task and leaves you fewer sentences to keep accurate. Cognitive load theory has a name for the waste, extraneous load, which is effort spent decoding the page that should have gone to the work.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/shorter-documentation/cognitive-load.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/shorter-documentation/cognitive-load.narrow.svg" width="288" height="440"><img class="np-has-narrow" src="/static/images/diagrams/shorter-documentation/cognitive-load.svg" width="720" height="432" alt="Three kinds of cognitive load share a reader's limited working memory. Intrinsic load is the difficulty of the task itself. Extraneous load is effort wasted on poor documentation design, marked as the load to remove. Germane load is the productive effort of building a mental model of the system, drawn as the path that should get the freed capacity." loading="lazy" decoding="async"></picture></a>
  <figcaption>Good docs remove the effort of decoding the page, so the reader's attention goes to the task and to understanding the system.</figcaption>
</figure>

Maintenance is the second cost, and writers undercount it. A button gets renamed and a parameter gets deprecated, so a page with one job has one promise to re-check, and a page with five has five.

## Why is AI-written documentation so long?

AI-written documentation runs long because a model can produce every true sentence about a subject and has no way to know which one this reader came for. Rishabh Mishra's [short note](https://rsbh.dev/notes/technical-writing-in-the-ai-era) from November 10 puts that cause in one line: "It doesn't know about the reader."

Until recently a long page was at least evidence of work, because someone had to type it. Agents took that cost to zero, so length now tells the reader nothing about care.

Developers are already trying to fix the length inside the tools. A plugin called [i-have-adhd](https://github.com/ayghri/i-have-adhd) reached 542 points on Hacker News on September 8, and its first rule tells the coding assistant to lead with the next action.

The thread under it was less hopeful than the README, where a user, sleazebreeze, reported that the skill holds for a few turns before the verbosity returns. I'd expect the same of a human writer handed a style guide, because a style rule can shorten sentences and can't decide what a page is for, which is where the length comes from.

A rule also wears off sooner when it travels without the sentence that broke it, and [my comparison of two pitfalls lists](/articles/pitfalls-list-for-ai-drafted-docs/) has the record of that from my own writing skill.

## How do you shorten documentation without losing detail?

Give each page one job, answer it on the first screen, and move everything else to a page with its own job. The detail survives because it moves, and the reader who needs it follows a link.

I'd ask four questions of a page that feels long.

1. What does the reader need to do or decide after reading it?
2. Does every paragraph support that outcome?
3. Should this detail live on a troubleshooting or reference page?
4. Does this sentence exist because I was afraid to cut it?

The question about fear matters more than the others, because fear is what writes the paragraph about a legacy flag nobody has set in years. My post on [changelogs](/articles/writing-changelogs/) applies the same cut to release entries, where not every commit deserves a line.

The first screen is the one part every visitor reads, and a line such as "This page explains" spends it telling them they are on a page.

Willison's details tag is a good patch for a pull request and a poor fit for docs. A collapsed section still has to be kept true, and a toggle gives it no URL and no title of its own.

Splitting the content into separate pages hides the detail the same way, and each page gets a URL and a title. Sections with their own headings are the halfway step, and [documentation headings](/articles/documentation-headings/) has the rule for naming them.

The [agent harnesses](/articles/agent-harnesses/) page is built that way, as one page whose seven sections can each be linked.

## Does shorter documentation matter when agents read it?

Yes, because an agent pays for every token it fetches, and the Markdown it asks for has no toggles. [Fern's State of Docs report](https://buildwithfern.com/post/state-of-docs), from November 10, says "Agents now make up more than half of the requests to the docs we host" and that they ask for the Markdown version of a page.

I argue with that headline in [my essay on agents reading docs](/articles/agents-reading-docs/), and the Markdown finding holds either way.

A collapsed section arrives as plain text in Markdown, so an agent gets the hidden part whether it wanted it or not. Separate pages still let it choose, and Fern describes the pattern as "an agent reads llms.txt once, then fetches the Markdown for the pages it needs."

Small pages with one job are therefore the unit an agent can select, and a page that mixes five intents makes the agent fetch four it didn't need.

Chrome's guides for coding agents are edited to that standard, and my [notes on Modern Web Guidance](/articles/chrome-modern-web-guidance-notes/) look at what they cut.

## When should documentation be long?

Documentation can be long when nobody reads it from the top, and reference is the clear case. Fern's report has agents spending 31% of their reading on API reference, a page type that is exhaustive by design and entered at one parameter.

DocSpring shows the same thing at a larger size. Nathan Broadbent [wrote on November 13](https://docspring.com/blog/posts/ponytail-vs-agents-md/) that "We have 42 AGENTS.md files, about 65,000 words in all: a root file with the rules every change follows, and a nested file next to each part of the code that has its own pitfalls (migrations, background jobs, the public API, CI)."

At 65,000 words that is a book, and its structure means no reader, human or agent, meets more than the root file and the one beside the code being changed. Specifications, architecture references and incident runbooks earn their length the same way, by giving every section its own heading or file that a reader can go straight to.

A migration guide is the exception that gets read in order, and there each section should map to a decision, such as whether to run the backfill before or after flipping the feature flag. The length this page argues against is the kind that comes from never editing.

## FAQ

**How short should a technical doc be?**

There is no universal word count. The target is the smallest amount of information that lets the reader succeed without guessing, which is brief for a quickstart and substantial for a migration guide.

**Do shorter docs risk leaving out important edge cases?**

Only if you delete the edge cases when you could move them to a troubleshooting or reference page.

**Should I split one long page into many tiny pages?**

Only when each small page has a clear, independent job. A site of tiny pages that each need several others to make sense is as hard to use as one long page, and the goal is fewer pages that mix purposes.

**What kind of documentation should always stay long?**

Reference pages, specifications and standards, which readers enter at one section and don't read from the top.

**How can I tell if my page is too long?**

Read the first screen: if it doesn't answer the reader's immediate question, or the page serves several reader tasks, it is too long for its purpose.
