---
category: coding-agents
primary_query: none
siblings:
- red-build-nobody-reads
- coding-models-new-code-vs-change
bridges:
- slug: design-doc-template
  reason: A design doc with non-goals and a rejected alternative is where the reasons behind code get recorded.
- slug: code-documentation
  reason: The comment worth writing is the one that gives a reason the code cannot show.
date: 2026-11-17
description: A Reddit post said nobody understands the code after a year of agents. The Claude Code team says nobody needs the whole picture. Naur's 1985 paper shows what both miss.
slug: nobody-understands-the-code
status: published
title: 'An Agent Can Explain What Code Does. The Why Has to Be Written'
work_note: 'I write documentation for a living, so I have a stake in whether a generated explainer can replace it. This essay is my answer, and [my portfolio](/portfolio/) has the client work.'
---

On November 9 a Reddit post titled "A year after the 100% AI mandate nobody understands our code" [reached Hacker News](https://news.ycombinator.com/item?id=50433079), and the first thing commenters settled was that the post itself looked machine-written. "Pangram said the op post is 100% AI generated", one wrote, and another told readers not to "fall for the bait".

The complaint outlived its source, and a day later the same site was discussing [AI usage generates a fragile codebase](https://evanxmerz.com/post/ai-usage-generates-a-fragile-codebase/), a post by Evan X. Merz dated November 7.

It is the standing objection to [coding agents](/articles/coding-agents/) at work.

Merz notes that "every word of this article was written by a human", and he makes the charge from inside a large company: "The longer a company relies on AI agents to generate the code, the fewer developers are going to understand the codebase."

I think Merz is describing something real, and that an answer published the month before his post is right about half of it.

## The answer from a team that ships this way

That answer is in a post the Claude Code team [published on October 15](https://claude.dev/blog/solving-code-review-at-anthropic/), written by Addy Osmani and two colleagues, about reviewing code at the volume agents produce it.

It says code review has always had a second job, spreading understanding of the codebase, and then asks Merz's question for him. With machines doing the reading, "how does anyone learn the code?"

The reply opens "We don't have a formal process for this."

"Nobody on the team keeps a complete mental model of Claude Code in their head, and we don't think anyone needs to. When someone wants to understand a part of the codebase, they ask Claude to write an explainer for exactly that slice."

The post brings results with it. Between June and September, it says, "merged pull requests to Claude Code's codebase more than doubled while the share that had to be reverted fell by more than 40 percent."

Merz brings none. His post says incidents rise and recovery slows in codebases written by agents, and it gives no counts for either, so on evidence the exchange is lopsided in Anthropic's favour.

Both sides are arguing about documentation, whether or not they use the word. An explainer is a document, written at the moment someone needs it.

## What an explainer is made from

An explainer is made from the code. That is its strength, because it "reflects the code as it is today", which is more than a hand-written architecture page can promise a month after someone wrote it.

It is also the limit, and the limit was described in 1985.

Peter Naur's paper [Programming as Theory Building](https://gwern.net/doc/cs/algorithm/1985-naur.pdf) argues that a program is the visible part of a theory its programmers hold, with "any documentation being an auxiliary, secondary product". The programmer who has the theory, Naur writes, "can explain why each part of the program is what it is".

The what and the why come from different places. What a module does can be read off the module, by a person or by a model.

Why it does it that way depends on things that were never in the repository, such as the option that was tried and dropped, or the outage that accounts for an odd timeout. A model asked for the why will supply one, and it will be a plausible reading of the code with nothing to mark the places where it guessed.

Naur was stricter than I am being. He held that "reestablishing the theory of a program merely from the documentation, is strictly impossible", and that "The death of a program happens when the programmer team possessing its theory is dissolved."

A dead program, in his account, keeps running. What stops is the ability to answer a request for a change well, which is close to what Merz reports from the inside.

## Why it works for them

The Anthropic post describes more than explainers, and the rest is where the theory lives. The team works in open Slack channels, and when a change heads the wrong way, "Usually someone in the channel asks why, points at an earlier decision, or suggests a simpler route".

Somebody remembers the earlier decision. The people who hold the theory are present, and a norm the post calls "You land it, you own it" keeps each change attached to a person.

So the explainer covers the what, and the why is carried by people who were there. A team that copies the explainer and lacks the rest should expect the result Merz describes.

Change at that volume also wears on the signals a team relies on, and [my essay on red builds](/articles/red-build-nobody-reads/) takes up what happens to a build light. Whether the models change existing code as well as they write new code is a separate question, in [new code versus change](/articles/coding-models-new-code-vs-change/).

[A reply to Merz](https://news.ycombinator.com/item?id=50446216) argued that understanding "does not decrease, it just moves up a level or two", the way few programmers understand the kernel they run on. I think the comparison holds only where the level below has an owner and a written contract, and a service that agents generated last year has neither unless someone supplied them.

## The part worth writing by hand

This leaves a smaller documentation job than the one teams used to skip, and a more exact one. A page that says what the code does can be regenerated whenever it is needed, and the regenerated copy will be fresher than anything kept by hand.

The decisions can't be regenerated, so they are the part to write, at the time they are made. Record what was chosen and what was rejected, with the outside fact that forced the choice.

That is what a [design doc](/articles/design-doc-template/) keeps when it has non-goals and a rejected alternative. It is also the comment I argued for in the [code documentation guide](/articles/code-documentation/), the one that gives a reason the code can't show.

Naur would say even this falls short of the theory, and I agree with him. It is still the difference between a successor who can put a question to a page and one who can only put it to the code.

A test follows for any team. Pick a module that agents have changed many times this year, and ask why it is built the way it is and what was decided against.

If a document answers, the theory has a second home. If only one person can answer, write it down before they leave the team, and if nobody can, the Reddit post was about you, whoever wrote it.
