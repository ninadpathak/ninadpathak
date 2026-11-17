---
category: technical-documentation
date: 2026-11-17
description: Release notes and blog posts now carry a line saying a human wrote them. For technical writing the label a reader can check is different, the date the page was last run.
slug: written-by-a-human
status: published
title: 'Written by a Human Proves Little. Last Tested Proves More'
work_note: 'I sell technical writing, so I have an interest in what makes a page worth trusting now that text is free to produce. This essay is my answer, and [my portfolio](/portfolio/) has the work.'
---

Ghostty's [1.4.0 release notes](https://ghostty.org/docs/install/release-notes/1-4-0), published on October 27, pause after thanking contributors to say something release notes never used to say.

"These release notes are painstakingly and lovingly hand-crafted by human Ghostty maintainers, including the full changelog. They take a combined 16+ hours to write, so please enjoy."

Evan X. Merz put a similar line in the introduction of [a post](https://evanxmerz.com/post/ai-usage-generates-a-fragile-codebase/) that reached the front page of Hacker News in November: "every word of this article was written by a human".

I think the label is aimed at a real problem and proves the wrong thing.

## The bargain the label tries to restore

The best account of the problem I've read is a comment by auntienomen in [a Hacker News thread](https://news.ycombinator.com/item?id=50481870) from November 13 about trust between writers and readers. It says that models let people "generate prose faster than readers can read it", and it calls the result "a fundamental break in the bargain between readers and writers: However long it takes someone to consume a piece of writing, it almost certainly took the author longer to write it."

Under that bargain a reader could infer care from the fact that a document existed. A long page had cost someone a week, so somebody had judged it worth a week.

Ghostty's sixteen hours restate that cost for a world where the page no longer implies it. I made the related point in [the case for shorter documentation](/articles/shorter-documentation/), that length has stopped telling a reader anything about effort.

## Why an assertion can't carry it

The label is text, and text is the thing that became free. The Reddit complaint I wrote about in [another essay](/articles/nobody-understands-the-code/) had the voice of a tired engineer, and commenters reported that a detector scored it as fully machine-written.

A reader can't check "written by a human". A commenter in the same thread described a tool built to try, on the grounds that "The one thing that we can prove with reasonable ease is that the time it took to write was compatible with the author being a human".

Proof of time answers the wrong question for technical writing. A release note can be typed slowly by a person and still be wrong about which versions are affected.

## What a technical reader wants proved

The thread also contains the technical version of the complaint. A commenter there wrote "I can't trust that my coworkers are actually testing the crap they're generating before wasting my time with runbooks that aren't even validated."

The objection in that sentence is to a runbook nobody ran. A runbook typed by hand and never tested fails the engineer on call in the same way.

So the cost a technical reader wants evidence of is the checking. Somebody ran the command, on a stated version, and it printed a stated result.

That evidence can sit on the page, and it differs from the label in the way that matters: the reader can run the command too. Ghostty's notes carry it alongside their label, in advisory lines such as "This affects Ghostty 1.3.0 and 1.3.1.", which anyone holding either version can test.

## A label the reader can check

The [runbook template](/articles/runbook-template/) on this site has a header field called Last tested, for the date someone last ran every step. Its checker can fail a runbook whose date is too old.

I think that field is the one worth copying onto other kinds of page. It says the page was tested on a date, against a version, with the output shown.

My site makes no claim to be written without AI, and my [about page](/about/) says I use it to prepare research and to attack a draft. What I try to put on a page is the other kind of proof, a script with the output it printed or a count with the page it was taken from.

A reader can rerun those. I prefer being checked to being believed.

The comment I started from ends with a rule its author's team follows: "you should spend more time writing something than you expect the audience to spend reading it." For a docs team the rule needs one change, which is to spend that time running what the page tells the reader to run and to leave the proof where they can see it.
