---
category: technical-documentation
primary_query: none
siblings:
- shorter-documentation
- runbook-template
bridges:
- slug: nobody-understands-the-code
  reason: Both essays ask what a written page proves once text costs nothing to produce.
date: 2026-11-17
description: Ghostty's release notes say people wrote them. I read that as an invitation, I think it's fading as agents become the readers, and I say who should keep doing it.
slug: written-by-a-human
status: published
title: "Thoughts on Ghostty's hand-crafted release notes"
work_note: "I'm Ninad Pathak, a freelance technical writer for developer-tool companies. Release notes are among the pages I write, and I run the product before I write about it. [Hire me to write yours](/services/)."
---

Ghostty's [1.4.0 release notes](https://ghostty.org/docs/install/release-notes/1-4-0), published on October 27, stop after the contributor thanks to tell you who wrote them: "These release notes are painstakingly and lovingly hand-crafted by human Ghostty maintainers, including the full changelog." They add that the job took a combined 16-plus hours.

That line worked on me. It made me want to read the notes the way I read something a person wrote, slowly and to the end.

I also think it's a fading thing, and that it will last only where someone really cares. Both halves matter for how I think about [technical documentation](/articles/technical-documentation/).

## An invitation to a human reader

I read the label as an invitation. It doesn't prove anything, and it isn't trying to: it says a person spent time on this, so you might spend some too.

Why does that need saying now? A commenter in [a Hacker News thread](https://news.ycombinator.com/item?id=50481870) on November 13 put it better than I can: models let people produce prose faster than anyone can read it, which breaks an old bargain where a piece of writing always took its author longer than it took you.

Under that bargain a long page told you somebody had judged it worth a week. Ghostty's sixteen hours state the cost out loud, for a world where the page no longer implies it.

I made the related point in [the case for shorter documentation](/articles/shorter-documentation/), that length has stopped telling a reader anything about effort.

## Why I think it's fading

The invitation is addressed to people, and people are a shrinking share of who reads a changelog. Fern's [State of Docs report](https://buildwithfern.com/post/state-of-docs) from November 10 found agents reading the changelog about twice as often as people do, across the docs sites Fern hosts.

Now, that's one vendor's logs, and beyond them I'm going on impression. But the direction seems plain to me, and my guide on [how to write a changelog](/articles/writing-changelogs/) goes through what it changes about each entry.

An agent doesn't care who typed the notes. It wants to know which versions are affected and what to change, and sixteen hours of craft are invisible to it.

So I expect the label to fade. Hand-written release notes cost hours every release, and once the first reader is a tool, fewer teams will find a reason to spend them.

## What the label can't do

Even for a human reader the label has a limit, which is that nobody can check it. The Reddit complaint in [my essay on code nobody understands](/articles/nobody-understands-the-code/) read to me like a tired engineer, and a commenter reported that a detector scored it as fully machine-written.

And a technical reader wants something else proved anyway. A commenter in that thread complained about coworkers who send round generated runbooks without testing them, and a runbook typed by hand and never run fails the engineer on call in the same way.

What I want evidence of is the checking. Somebody ran the command, on a stated version, and it printed a stated result.

Ghostty's notes carry that too, in advisory lines such as "This affects Ghostty 1.3.0 and 1.3.1." You can check your installed version against a line like that, and so can an agent.

It's why the [runbook template](/articles/runbook-template/) on this site has a header field called Last tested, for the date someone last ran every step. I'd copy that field onto other kinds of page before I'd copy the label.

## Who should keep writing by hand

Teams that want developers to come back and read. That's where I think the label keeps its value.

Ghostty is that kind of project. Its release notes read to me like the story of a release, and the line about sixteen hours is part of why.

If your changelog is a place developers return to for the writing, say that people wrote it, and mean it. If it's a list an agent will parse on its way to an upgrade, spend the hours on lines that are tested and exact.

My [about page](/about/) says how AI figures in the writing on this site, for research and for attacking a draft. So I'd sooner show you a command and its output than tell you who typed the page.
