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
description: A Reddit post said nobody understands the code after a year of agents. I think the need to hold code in your head will shrink, and a record of how things shipped is what to keep writing.
slug: nobody-understands-the-code
status: published
title: "What I'd still write by hand in a codebase agents can explain"
work_note: "Building an AI product whose readers are engineers? I'm Ninad Pathak, a freelance technical writer, and I write tutorials and technical articles for companies like yours after running the product myself. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
---

On November 9 a Reddit post titled "A year after the 100% AI mandate nobody understands our code" [reached Hacker News](https://news.ycombinator.com/item?id=50433079). Commenters flagged the post itself as machine-written, on a detector score that others disputed, so I wouldn't lean on it.

The complaint is real, though.

A day later Hacker News was discussing [AI usage generates a fragile codebase](https://evanxmerz.com/post/ai-usage-generates-a-fragile-codebase/), which Evan X. Merz published on November 7 and says he wrote himself.

It argues that code written by agents leaves a company with developers who don't understand their own codebase, which is the common objection to using [coding agents](/articles/coding-agents/) at work.

So here's where I stand. People need to know what their codebase does, at the very least, and I also think that need is going to shrink.

What won't shrink is the value of a record of what happened and how things were shipped. That record is the part I'd still write by hand.

## Where I agree with Merz

Merz writes from inside a large company, and his charge is simple: "The longer a company relies on AI agents to generate the code, the fewer developers are going to understand the codebase."

I think he's describing something real. If code is written by someone with zero understanding of what's happening underneath it, nobody can point at the function or file behind a problem, because that context doesn't exist in any developer's head.

And I'd put the cost more broadly than a bad incident. Knowing what the code does is what lets you work on it effectively, and a team without that knowledge is slower at everything it touches.

Merz says incidents rise and recovery slows in agent-written codebases, and he gives no counts for either. So I agree with the worry and I can't call it proven.

## Where Anthropic has a point

The other side has numbers. The Claude Code team [wrote on October 15](https://claude.dev/blog/solving-code-review-at-anthropic/) about reviewing code at the volume agents produce it, and they report that merged pull requests more than doubled between June and September while the share that had to be reverted fell by over 40 percent.

They also answer Merz's charge, weeks before he made it. Nobody on that team keeps a complete mental model of the codebase, they say, "and we don't think anyone needs to", because anyone who wants to understand a slice of it asks Claude to write an explainer for that slice.

I don't flatly disagree. If I extrapolate a few years, we probably won't need people to remember what the code does, and a team that ships this way with fewer reverts is evidence for that.

But look at what they replaced the memory with. An explainer is a document, written at the moment someone needs it, so the argument between these two posts is about documentation whether or not either uses the word.

## What an explainer can't tell you

An explainer is made from the code, and that's its strength. It describes the code as it is today, which a hand-written architecture page can't promise a month after someone wrote it.

Being made from the code is also the explainer's limit, and Peter Naur described that limit in 1985. His paper [Programming as Theory Building](https://gwern.net/doc/cs/algorithm/1985-naur.pdf) treats a program as the visible part of a theory its programmers hold, and the person who holds that theory "can explain why each part of the program is what it is".

So what a module does and why it does it that way come from different places. What a module does can be read off the module, by a person or by a model.

The why depends on things that were never in the repository, such as the option that was tried and dropped, or the outage behind an odd timeout. Ask a model for the why and you'll get a plausible reading of the code, with nothing to mark where it guessed.

Naur went further than I would. He thought a program's theory can't be rebuilt from documentation at all, and that a program dies when the team holding its theory breaks up, even while it keeps running.

## Why explainers work at Anthropic

I think Anthropic's method works for a reason the post mentions almost in passing. The team talks in open Slack channels, and when a change heads the wrong way, someone asks why or points at an earlier decision.

Somebody remembers the earlier decision. The people who know how things were shipped are still in the room, and a norm the post calls "You land it, you own it" keeps every change attached to a person.

So the explainer covers the what, and the history is carried by people who were there. A team that copies the explainer and lacks those people should expect the result Merz describes.

[A reply to Merz](https://news.ycombinator.com/item?id=50446216) argued that understanding moves up a level, the way few programmers understand the kernel they run on. I don't buy that as it stands, because the kernel has an owner and a written contract, and a service agents generated last year has neither unless someone supplied them.

Change at that volume can also turn a build red so often that people stop looking, which is the worry [my essay on red builds](/articles/red-build-nobody-reads/) takes up. Whether the models change existing code as well as they write new code is a separate question, in [new code versus change](/articles/coding-models-new-code-vs-change/).

## The part I'd still write by hand

All of this leaves a smaller documentation job than writing down what the code does. A page that says what the code does can be regenerated whenever someone needs it, and the fresh copy will beat anything kept by hand.

What happened and how it shipped can't be regenerated, so that's the part to write, at the time it happens. Record what was chosen and what was rejected, with the outside fact that forced the choice.

A [design doc](/articles/design-doc-template/) keeps exactly that when it has non-goals and a rejected alternative. So does the comment I argued for in the [code documentation guide](/articles/code-documentation/), the one that gives a reason the code can't show.

Naur would say even this falls short of the theory, and he may be right. But it lets a successor put a question to a page, where otherwise they could only put it to the code.

To test whether a team has that record, pick a module that agents have changed many times this year, and ask why it's built the way it is and what was decided against.

If a document answers, the history no longer depends on one person's memory. If only one person can answer, write it down before they leave the team.
