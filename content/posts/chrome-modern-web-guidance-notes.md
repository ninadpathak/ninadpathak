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
description: Chrome shipped 200-odd guides written for coding agents. I think the editing is the part to copy, the packaging is wrong, and the question of who writes an agent's defaults is fair.
slug: chrome-modern-web-guidance-notes
status: published
title: "Notes on Chrome's Modern Web Guidance for coding agents"
work_note: "Docs for coding agents are still docs, and someone has to run the product before writing them. I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. [Hire me to write yours](/services/)."
---

On November 10 a member of the Chrome team posted [Modern Web Guidance](https://github.com/GoogleChrome/modern-web-guidance) to [Hacker News](https://news.ycombinator.com/item?id=50443812): more than 200 guides, written with the Firefox, Edge and MDN teams, that tell a coding agent to use what browsers now do natively. The reader they're written for is a model.

I read the project as [technical documentation](/articles/technical-documentation/) with a new kind of reader, and I think it's the best-edited example of that I've come across. I also think it ships in the wrong container.

## The editing is the part to copy

What I'd take from this project first is a rule about what to leave out. The README says the team runs evals so it can "prune lowest-common-denominator content that models already know".

I think that's the right standard, and it isn't new. It's what you owe any expert reader, and I argued for it with people in mind in [the case for shorter documentation](/articles/shorter-documentation/).

The guide I opened holds to it. Written for a navigation drawer, it says which approach to use and why it beats animating with JavaScript, and it never stops to explain what a dialog element is.

It also tells the agent what to assume when the request is silent. That's a line I'd add to a lot of human documentation, because a reader who has to guess will guess differently every time.

## They measured it, with their own ruler

I'm more impressed that there's a number at all than by the number. The README carries a table of runs with and without the guides, and on November 8 Claude Code on Opus 5.5 went from 57% of checks passed to 88%, over 215 tasks.

That's the vendor grading its own documentation with its own graders, so I read it as a direction and not a result. A commenter in the thread ran the project's legacy scan on their own code and reported it found two issues.

I haven't run it myself, so I can't add a third data point. But I can't name many docs teams that publish any measure of whether a page changes what its reader does next.

## The container is where I disagree

The guides arrive as an agent skill and an npm command, and I think that's the wrong way round. Documentation should be readable with nothing installed.

Simon Willison [made the case in the thread](https://news.ycombinator.com/item?id=50444594) better than I would. He asked for a plain Markdown index on a public URL, written to be searched with grep, so that any agent that can make an HTTP request can find the right guide.

I'd go further for a reason he didn't give. The README says the command-line tool reports the search queries an agent generates back to Google, and a file on a web server asks for nothing but a fetch.

An index plus single pages is also what agents already ask docs sites for, going by the logs in [my notes on Fern's agent traffic report](/articles/agents-reading-docs/).

## Who writes the agent's defaults

An objection in the thread stayed with me, which is that Chrome already has a great deal of say over the web, and now it would be steering what everyone's agent writes. I think the worry is fair, and I don't think it's special to Chrome.

The project's answer is that four browser and documentation teams steward it and that its guides lean on shared compatibility data. That helps.

But whoever writes the page an agent reads is setting a default for every codebase that agent touches. Documentation always did that, slowly, one developer at a time, and now it happens at the speed of a tool call.

The post called the guides hand-crafted, which is the word Ghostty used for its release notes. I said in [my thoughts on that label](/articles/written-by-a-human/) that it was fading as agents became the readers, and here it's on writing made for agents, addressed to the people who choose what their agent reads.

So I'd read the label as a claim about care, and then ask for what this project does supply: the date of the last eval run, and the tasks it was run on.
