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
description: 'Why shorter technical documentation works better, why AI-written docs run long, how to cut a page without losing detail, and when length is earned.'
status: published
work_note: "I'm Ninad Pathak, and I freelance as a technical writer for developer-tool companies. Docs run long, more so now that models draft them, and cutting a page down without losing what's true is work we can [do together](/services/)."
title: The Case for Shorter Technical Documentation
updated: 2026-11-16
slug: shorter-documentation
---

Simon Willison wrote on November 9 about [hiding agent-written pull request descriptions behind a details tag](https://simonwillison.net/2026/Nov/9/details-summary/). The descriptions are accurate and thorough, and the reaction the post reports is one I've had to agent-written text all year: "I'm not reading all of that".

Shorter documentation works better because a reader arrives with one task, and every sentence that doesn't serve it is something they have to read past and you have to keep true. Willison's fix applies that to pull requests by keeping the full text one click away and choosing an opening that is "the shortest text a human can read that will help get them up to speed."

The argument covers every kind of [technical documentation](/articles/technical-documentation/), from a README to a reference page.

That was the argument before 2026 too. What changed this year is what a long page says about its author.

Length used to stand in for effort, and [my essay on written-by-a-human labels](/articles/written-by-a-human/) follows what replaces it.

## Why is shorter technical documentation better?

Shorter documentation is better because it spends the reader's attention on the task and leaves you fewer sentences to keep accurate. Cognitive load theory has a name for the waste, extraneous load, which is effort spent decoding the page that should have gone to the work.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/shorter-documentation/cognitive-load.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/shorter-documentation/cognitive-load.narrow.svg" width="288" height="440"><img class="np-has-narrow" src="/static/images/diagrams/shorter-documentation/cognitive-load.svg" width="720" height="432" alt="Three kinds of cognitive load share a reader's limited working memory. Intrinsic load is the difficulty of the task itself. Extraneous load is effort wasted on poor documentation design, marked as the load to remove. Germane load is the productive effort of building a mental model of the system, drawn as the path that should get the freed capacity." loading="lazy" decoding="async"></picture></a>
  <figcaption>Good docs zero out extraneous load so the reader's bandwidth goes to the task and the mental model.</figcaption>
</figure>

The idea is older than the web. John Carroll's [The Nurnberg Funnel](https://openlibrary.org/works/OL4792482W), published by MIT Press in 1990, carries the subtitle "Designing Minimalist Instruction for Practical Computer Skill".

Maintenance is the second cost, and writers undercount it. A button gets renamed and a parameter gets deprecated, so a page with one job has one promise to re-check, and a page with five has five.

## Why is AI-written documentation so long?

AI-written documentation runs long because a model can produce every true sentence about a subject and has no way to know which one this reader came for. Rishabh Mishra put the reader's side of it bluntly on November 10: "It is too big for no reason."

The same [short note](https://rsbh.dev/notes/technical-writing-in-the-ai-era) names the cause better than the longer essays I've read: "AI writes in a zig-zag flow. It doesn't know about the reader."

Until recently a long page was at least evidence of work, because someone had to type it. Agents took that cost to zero, so length now tells the reader nothing about care, and Willison's phrase for the result is exact: "It's not necessarily slop, but it reads like slop!"

Developers are already trying to fix this in the tools. A plugin called [i-have-adhd](https://github.com/ayghri/i-have-adhd) reached 542 points on Hacker News on September 8, and its README describes it as "A skill for your coding assistant that stops it from burying the answer."

Its rules read like a documentation style guide written for a machine, and the same list would serve a human writer. The first is "Lead with the next action." and the last bans preamble, recaps and closers.

The thread under it was less hopeful than the README. A user there, sleazebreeze, reported that the skill holds for a few turns before the verbosity returns, and concluded "I don't think we can skill our way out of this one."

A human writer handed a style guide hits the same limit. A style rule can shorten sentences, and it can't decide what a page is for, which is where the length comes from.

## How do you shorten documentation without losing detail?

Give each page one job, answer it on the first screen, and move everything else to a page with its own job. The detail survives because it moves, and the reader who needs it follows a link.

A page that feels long gets four questions.

1. What does the reader need to do or decide after reading it?
2. Does every paragraph support that outcome?
3. Should this detail live on a troubleshooting or reference page?
4. Does this sentence exist because I was afraid to cut it?

The fourth question matters more than the others, because fear is what writes the paragraph about a legacy flag nobody has set in years. My post on [changelogs](/articles/writing-changelogs/) applies the same cut to release entries, where not every commit deserves a line.

The opening block carries the heaviest load. A line such as "This page explains" spends that room telling readers they are on a page.

Willison's details tag is a good patch for a pull request and a poor fit for docs. A collapsed section still has to be kept true, and a toggle gives it no URL and no title of its own.

Splitting by page does the same job with those problems solved. Sections with their own headings are the halfway step, and [documentation headings](/articles/documentation-headings/) has the rule for naming them.

The [agent harnesses](/articles/agent-harnesses/) page is built that way, as one page whose seven sections can each be linked.

## Does shorter documentation matter when agents read it?

Yes, because an agent pays for every token it fetches, and the Markdown it asks for has no toggles. [Fern's State of Docs report](https://buildwithfern.com/post/state-of-docs), from November 10, says "Agents now make up more than half of the requests to the docs we host" and that they ask for the Markdown version of a page.

I argue with that headline in [my essay on agents reading docs](/articles/agents-reading-docs/), and the Markdown finding holds either way.

A collapsed section is plain text in Markdown, so progressive disclosure by toggle doesn't exist for that reader. Disclosure by page still does: Fern describes the pattern as "an agent reads llms.txt once, then fetches the Markdown for the pages it needs."

Small pages with one job are therefore the unit an agent can select, and a page that mixes five intents makes it buy four it didn't want.

Chrome's guides for coding agents are edited to that standard, and my [notes on Modern Web Guidance](/articles/chrome-modern-web-guidance-notes/) look at what they cut.

## When should documentation be long?

Documentation can be long when nobody reads it from the top, and reference is the clear case. Fern's report has agents spending 31% of their reading on API reference, a page type that is exhaustive by design and entered at one parameter.

DocSpring shows the same thing at a larger size. Nathan Broadbent [wrote on November 13](https://docspring.com/blog/posts/ponytail-vs-agents-md/) that "We have 42 AGENTS.md files, about 65,000 words in all: a root file with the rules every change follows, and a nested file next to each part of the code that has its own pitfalls (migrations, background jobs, the public API, CI)."

At 65,000 words that is a book, and its structure means no reader, human or agent, meets more than the root file and the one beside the code being changed. Specifications, architecture references and incident runbooks earn their length the same way, by giving every section an address.

A migration guide is the exception that gets read in order, and there each section should map to a decision, such as whether to run the backfill before or after flipping the feature flag. The length this page argues against is the kind that comes from never editing.

## FAQ

**How short should a technical doc be?**

There is no universal word count. The target is the smallest amount of information that lets the reader succeed without guessing, which is brief for a quickstart and substantial for a migration guide.

**Do shorter docs risk leaving out important edge cases?**

Only if you delete them without a plan. Edge cases move to dedicated troubleshooting or reference pages, which keeps the primary path clean and still answers the reader who hits one.

**Should I split one long page into many tiny pages?**

Only when each small page has a clear, independent job. Excessive fragmentation is as bad as excessive length, and the goal is fewer mixed-purpose pages.

**What kind of documentation should always stay long?**

Specifications and formal standards. They are the source of truth for an implementation and have to be exhaustive to prevent ambiguity.

**How can I tell if my page is too long?**

Check the first screen and count the intents. If the first screen doesn't answer the reader's immediate question, or the page serves several different reader tasks, it is too long for its purpose.
