---
category: technical-documentation
primary_query: none
siblings:
- shorter-documentation
- written-by-a-human
bridges:
- slug: agents-reading-docs
  reason: Fern's logs show agents fetching an index and then single Markdown pages, which is the delivery this essay argues for.
date: 2026-11-17
description: Chrome shipped more than 200 guides written for coding agents. I think its rule of cutting what the model already knows is worth copying, a plain Markdown index should come before the npm install, and it's fair to ask who decides what every agent writes by default.
slug: chrome-modern-web-guidance-notes
status: published
title: "Notes on Chrome's Modern Web Guidance for coding agents"
work_note: "Docs for coding agents are still docs, and someone has to run the product before writing them. I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. [Work with me on yours](/services/)."
---

On November 10 a member of the Chrome team posted [Modern Web Guidance](https://github.com/GoogleChrome/modern-web-guidance) to [Hacker News](https://news.ycombinator.com/item?id=50443812): more than 200 guides, shipped in collaboration with Firefox, Edge and MDN, that tell a coding agent to use what browsers now do natively. The guides are written for a model to read, not a person.

I read the project as [technical documentation](/articles/technical-documentation/) with a new kind of reader, and I think its guides are tightly edited in a way human docs should copy. I also think the project leads with the wrong way to get the guides, an npm install where a plain web page would do.

## The editing is the part to copy

The first thing I'd take from Modern Web Guidance is its rule about what to leave out of a guide. The README says the team runs evals so it can "prune lowest-common-denominator content that models already know".

Cutting what the reader already knows is the right standard, and it applies to human readers as much as to models. I argued for the same standard, with expert human readers in mind, in [the case for shorter documentation](/articles/shorter-documentation/).

The one guide I opened, on building a navigation drawer, follows that rule. The guide says which approach to use and why it beats animating with JavaScript, and it never stops to explain what a dialog element is.

The navigation drawer guide also tells the agent what to assume when the user's request doesn't specify a detail. I'd add a line like that to human documentation as well, because two readers who each have to guess a default will guess two different defaults.

## They measured it, with their own ruler

The README publishes a measurement of whether the guides work, and the fact that it publishes one impresses me more than the figure. The README carries a table of runs with and without the guides, and on November 8 Claude Code on Opus 5.5 went from 57% of checks passed to 88%, over 215 tasks.

The Chrome team wrote the guides, the tasks and the graders, so I read the jump from 57% to 88% as a sign the guides help and not as a measured size of the help. A commenter in the thread ran the project's legacy scan on their own code and it found only two issues, and a maintainer replied that the scan covers about a fifth of the guides so far.

The legacy scan checks existing code and the eval table checks newly generated code, and I haven't run either one myself. Even so, I can't name many docs teams that publish a table of pass rates with and without their docs.

## The front door is where I disagree

The README offers the guides first as an agent skill installed with an npm command, and I think a web page should come first. Documentation should be readable by a person or an agent that has installed nothing.

The guides can be read without installing anything, to be fair. The launch post links readable versions on Chrome's developer site, and the README links every guide's Markdown file.

Simon Willison [asked in the thread](https://news.ycombinator.com/item?id=50444594) for one more step beyond readable pages: a plain Markdown index on a public URL, written to be searched with grep, so any agent that can make an HTTP request finds the right guide. The maintainers agreed, and one replied "We'll make this happen."

So my disagreement is only with what the README presents first, and the maintainers' reply to Willison has made it smaller than it was on launch day. I'd put the Markdown index at the top of the README and present the npm install as an optional extra.

Installing the tool also has a privacy cost that fetching a web page doesn't have. The README says the command-line tool sends Google anonymous usage data, including the search queries an agent generates, and gives an environment variable that turns it off.

An index file plus one Markdown page per guide is also the shape agents already request from docs sites, going by the server logs in [my notes on Fern's agent traffic report](/articles/agents-reading-docs/).

## Who writes the agent's defaults

An objection in the thread stayed with me: Chrome already has a great deal of influence over the web, and these guides would let it steer the code that everyone's coding agent writes. I think that worry is fair, and I think it applies to anyone who writes docs for agents, not only to Chrome.

The project's answer is that four browser and documentation teams steward it and that its guides lean on shared compatibility data. Shared stewardship answers part of the worry, though a Chrome engineer said in the same thread that Mozilla had joined only in the last few weeks.

Whoever writes the page an agent reads is setting a default for every codebase that agent works on. Documentation has always set defaults this way, one developer at a time over months, and an agent applies the same default within seconds of fetching the page.

The post called the guides hand-crafted, which is the word Ghostty used for its release notes.

I said in [my thoughts on that label](/articles/written-by-a-human/) that "hand-crafted" was losing its meaning as agents became the readers. Here the label is attached to writing made for agents, and it's aimed at the developers who choose which guides their agent reads.

So I'd read "hand-crafted" as a claim that people took care over the guides, and then I'd ask for the evidence, which this project does supply: the date of the last eval run, and the tasks it was run on.
