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
work_note: "I'm Ninad Pathak, and I write documentation for companies building agents, agent memory and LLM infrastructure. I build the example and run it before I draft, so your engineers review working code. [Here's what that looks like](/services/freelance-technical-writer-for-ai-companies/)."
---

On October 29 Rachel Laycock, the CTO of Thoughtworks, published [Why are good developers so wary of agentic development?](https://martinfowler.com/rachels-ramblings/good-devs-wary.html), and the middle of it reports an experiment. A group of senior engineers, infrastructure consultants and product people built an airline application for a week under one constraint.

"No code written by anyone. Everything built by agents."

By her account "they got 80% done", and the result she dwells on is the build.

"The application ran. The build was red."

I think that red build is the part of her post a team working with [coding agents](/articles/coding-agents/) can act on today. On-call engineers met the failure years ago and wrote down the fix.

Laycock's worry is what the colour stops meaning.

"A red build should mean something: stop, investigate, fix it. If it's red so often that people stop paying attention, how do we spot the next real failure?"

Her post leaves the cause open, and one of the candidates she lists is "were changes simply arriving faster than the checks could finish?" Her larger argument is that experienced developers hold back because "built isn't the same as working in production", and that nobody will know how agent-built systems behave until they have run for a while.

She is right about that wait, and the build light doesn't need it.

## Signals were sized for people

Google's Site Reliability Engineering book, published in 2016, has a rule about pagers in [its chapter on monitoring](https://sre.google/sre-book/monitoring-distributed-systems/). Rob Ewaschuk wrote it in the first person.

"Every time the pager goes off, I should be able to react with a sense of urgency. I can only react with a sense of urgency a few times a day before I become fatigued."

The rule treats an engineer's attention as a budget that the alerting system spends. A red build asks every engineer on a team to stop and look, so each one spends from it.

Continuous integration depends on a failure being rare enough that somebody stops, and the pager rule says how rare that is: a few times a day.

The comparison is loose in one respect. A pager wakes one named person, and a red build addresses everyone on the team, each of whom can assume somebody else is looking.

The build light is only one of the signals with this property.

The count in [my guide to writing changelogs](/articles/writing-changelogs/) covers the Claude Code changelog over the thirty days to November 16, which held 1,807 entries. The project folds 1,372 of them into collapsed lists of bug fixes and improvements, which is its own way of rationing a reader's attention.

An entry in that month told users that a feature they depended on would start returning errors on a set date. It was written well, and it was one of 293 entries filed under "Changed" that month, in the part of the page left open.

Pull request descriptions have gone the same way. Simon Willison [wrote on November 9](https://simonwillison.net/2026/Nov/9/details-summary/) about the long generated ones, and his reaction to them was "I'm not reading all of that".

His remedy is in the post's title, which tells authors to hide such descriptions behind a collapsed block. That is the changelog's move again, and it works only when the line left outside the fold is the one that matters.

Each of these was a message whose value depended on how seldom it arrived. A commenter on [the Hacker News thread](https://news.ycombinator.com/item?id=50291974) about Laycock's post put the change in one clause, writing that accounting for every failure "becomes much harder when an automated system is pushing through 10x as much code."

## A team that reports the opposite

The strongest evidence against my worry comes from the Claude Code team, whose post I also read for [my essay on code nobody understands](/articles/nobody-understands-the-code/). Their [post on code review](https://claude.dev/blog/solving-code-review-at-anthropic/) of October 15 says that between June and September "merged pull requests to Claude Code's codebase more than doubled while the share that had to be reverted fell by more than 40 percent."

So more change did not make that codebase less stable. Laycock cites research pointing the other way, writing that "DORA's 2025 research found AI adoption is now linked to higher delivery throughput, but to lower delivery stability."

The two can both hold, and the Anthropic post says what its team did differently. "We want to preserve human time and attention for issues only humans can solve and make sure automated checks catch the rest."

The mechanism is a filter in front of the person. "Every pull request gets a Claude review before a person looks."

The post also names the cost of an unfiltered signal when the reader is a machine: "Noise costs more when the author is an agent." A person waves off a small complaint, and an agent acts on it and opens another round.

## Ration what reaches a person

The on-call fix was to send fewer pages, and Ewaschuk's list goes on to say "Every page should be actionable." That test fits every signal an agent can now produce faster than a team can read.

A build that people must stop for has to fail seldom. That means a small set of checks that turn the build red, with everything else collected in a report that someone reads on a schedule.

A changelog puts the entries that require action above the ones that don't. A pull request description opens with the decision the reviewer is being asked to make.

None of that is new, and all of it is editing. Deciding what a busy reader must see first is the work a technical writer does on a page, applied to a build light.

Laycock's team estimated that they spent "about ⅔ of their time at the whiteboard and ⅓ on the harness".

The harness is where these signals get designed, beside the [CLAUDE.md file](/articles/claude-md/) that tells the agent the rules. The first number to settle there is how many times a day a person can be asked to stop.
