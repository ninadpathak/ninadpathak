---
category: coding-agents
primary_query: none
siblings:
- nobody-understands-the-code
- claude-md
bridges:
- slug: writing-changelogs
  reason: The changelog count is the essay's second example of a signal produced faster than it can be read.
date: 2026-11-17
description: A team that let agents write every line found its build frequently red. Google's pager rule from the SRE book says how often a person can be asked to stop.
slug: red-build-nobody-reads
status: published
title: "Applying Google's pager rule to a build that is always red"
work_note: "I write tutorials and technical articles for AI companies, and I run the product before I write a line. I'm Ninad Pathak, a freelance technical writer, and [you can hire me](/services/freelance-technical-writer-for-ai-companies/)."
---

On October 29 Rachel Laycock, the CTO of Thoughtworks, published [Why are good developers so wary of agentic development?](https://martinfowler.com/rachels-ramblings/good-devs-wary.html), and the middle of it reports an experiment. A group of senior engineers, infrastructure consultants and product people built an airline application for a week with agents writing every line, and by her account they finished about four fifths of it.

They ended the week with a result I keep coming back to: "The application ran. The build was red."

I think that red build is the part of her post a team working with [coding agents](/articles/coding-agents/) can act on today. On-call engineers met the same failure years ago and wrote down the fix.

Laycock's worry is what the colour stops meaning. If the build is red so often that people stop looking, she asks, how does anyone spot the next real failure?

Her larger argument is that experienced developers hold back because nobody knows how agent-built systems behave until they've run in production for a while. I think she's right about that wait, and I don't think the build light needs it.

## A red build spends attention

A red build asks every engineer on a team to stop and look, so it spends something the team has little of.

Google's Site Reliability Engineering book, published in 2016, says how little. Rob Ewaschuk wrote the pager rule in [its chapter on monitoring](https://sre.google/sre-book/monitoring-distributed-systems/) in the first person: "I can only react with a sense of urgency a few times a day before I become fatigued."

So that's the budget, a few times a day. Continuous integration depends on a failure being rare enough that somebody stops, and a build that is always red has spent the budget before the real failure arrives.

The comparison is loose in one respect. A pager wakes one named person, and a red build addresses a whole team, where each person can assume somebody else is looking.

And the build light isn't the only signal agents are wearing down. The count in [my guide to writing changelogs](/articles/writing-changelogs/) found 1,807 entries in thirty days of the Claude Code changelog, and the project folds 1,372 of them into collapsed lists.

That folding is rationing, and I think it's the right instinct. Simon Willison [made the same move on November 9](https://simonwillison.net/2026/Nov/9/details-summary/) for long generated pull request descriptions, which he tells authors to hide behind a collapsed block.

Each of these was a message whose value depended on how seldom it arrived. A commenter on [the Hacker News thread](https://news.ycombinator.com/item?id=50291974) about Laycock's post made the point about scale: accounting for every failure gets much harder once an automated system pushes through ten times the code.

## The team that reports the opposite

The best evidence against my worry comes from the Claude Code team, whose post I also read for [my essay on code nobody understands](/articles/nobody-understands-the-code/). Their [account of code review](https://claude.dev/blog/solving-code-review-at-anthropic/) from October 15 says merged pull requests more than doubled between June and September while the share that had to be reverted fell by over 40 percent.

So more change didn't make that codebase less stable. Laycock points to DORA's 2025 research, which links AI adoption to higher throughput and lower stability, and I think both can hold.

Why? Because the Anthropic team put a filter in front of the person, with a Claude review on every pull request before anyone looks at it.

What struck me is the reason they give for keeping that filter quiet: "Noise costs more when the author is an agent." A person waves off a small complaint, and an agent acts on it and opens another round.

## Ration what reaches a person

The on-call fix was to send fewer pages, and Ewaschuk's list has the test I'd apply to everything an agent can now produce faster than a team can read: "Every page should be actionable."

So a build that people must stop for has to fail seldom. I'd keep a small set of checks that turn the build red and collect everything else in a report someone reads on a schedule.

The same goes for the other signals. A changelog puts the entries that need action above the ones that don't, and a pull request description opens with the decision the reviewer is being asked to make.

None of that is new, and all of it is editing. Deciding what a busy reader must see first is the work a technical writer does on a page, applied here to a build light.

Laycock's team reckoned they spent about two thirds of their time at the whiteboard and the rest on the harness. The harness is where these signals get designed, beside the [CLAUDE.md file](/articles/claude-md/) that tells the agent the rules.

And the first number I'd settle there is how many times a day a person can be asked to stop.
