---
category: technical-documentation
primary_query: none
siblings:
- writing-technical-tutorials
- documentation-review
- documentation-headings
date: 2026-11-18
description: "The post Docker is weird explains containers in under 500 words, with headings that make claims. Two of the claims come with a command or path to check, and the fifth is seven years out of date. I'd write explainer headings that way and fact-check them first."
slug: docker-is-weird-explainer
status: published
title: "Why 'Docker is weird' works as an explainer"
work_note: "An explainer is worth reading when the reader can check its claims. I'm Ninad Pathak, a freelance technical writer for developer-tool companies, and I run the product before I write about it. [Let's work together](/services/)."
---

Simon Willison keeps a [separate site](https://til.simonwillison.net/) for TILs, the short notes he files under the line "Things I've learned". On October 22 a post called [Docker is weird](https://codeandcake.dev/posts/2026-10-22-docker-is-weird) put five such notes under one title, and by November 18 it had 887 points on Hacker News, where Docker's creator Solomon Hykes [turned up](https://news.ycombinator.com/item?id=50202931) to answer questions.

The author is building a container runtime for fun and wrote down what surprised them, in under 500 words. I think the post is a good model for the explainer pages in [technical documentation](/articles/technical-documentation/), including the one heading it gets wrong.

## Each heading is a claim I can check

The post's headings are sentences that could be false, such as "Images are just folders". I'd write explainer headings the same way, because a heading that makes a claim tells the reader what they'll know after the section and gives them something to test.

A concept page headed, say, Overview and Architecture names two topics, and a reader can't agree or disagree with a topic. My page on [task-based documentation headings](/articles/documentation-headings/) argues the same for how-to pages, where a heading should name what the reader does.

## Only two of the claims come with a place to look

For two of its claims the post tells me where to look. After saying that a container is an ordinary process, it adds that I can find that process in `/proc` on the host, and for images it walks through what `docker run -it --rm ubuntu /bin/bash` does.

I'd hold an explainer to that standard for every claim: one command or file path each, so a reader can confirm the claim on their own machine in a minute. The post's remaining claims have none, and those are the ones I had to take on trust.

A commenter, kazinator, [took the `/proc` point further](https://news.ycombinator.com/item?id=50203573) and described attaching gdb from the host to a process inside a container, which is the kind of reply a checkable claim invites.

My guide to [writing a technical tutorial](/articles/writing-technical-tutorials/) is built on the same idea, a result the reader can see. An explainer has no steps to finish, so the command or path is how its reader sees a result.

## The author says what they haven't understood

The post is open about its limits. Its sentence on network isolation includes "a whole bunch of networking magic I don't understand", and the author says twice that they've only just started the project.

I like that in a personal post, and I'd handle it differently in product docs. A blogger can admit they haven't learned container networking yet, and a docs page should say which topics it leaves out and link to the page that covers them.

## The heading about root is out of date

The fifth heading is "Docker requires root!", and I think it shows what a claim heading costs when the claim is wrong.

The two paragraphs under it are careful: they say the kernel APIs used to need root, that the daemon usually runs as root, and that rootless runtimes exist with networking as the hard part. A reader who skims takes away the heading.

Docker's release notes say that running the daemon as a non-root user, called rootless mode, [arrived in Engine 19.03](https://docs.docker.com/engine/release-notes/19.03/) on July 22, 2019 and [left experimental status in 20.10](https://docs.docker.com/engine/release-notes/20.10/) on December 8, 2020. A commenter, 0xbadcafebee, [made the correction](https://news.ycombinator.com/item?id=50203658) about two hours after the post reached Hacker News: Docker hasn't required root for seven years.

Rootless is still a mode you set up, and its [documentation](https://docs.docker.com/engine/security/rootless/) lists prerequisites, so the two careful paragraphs hold up better than the heading above them. A [documentation review](/articles/documentation-review/) that starts with the product would have caught the heading by reading those release notes, and an edit for style would have left it alone.

## A reader who knows Docker found nothing weird

A commenter, j16sdiz, [wrote](https://news.ycombinator.com/item?id=50203265) that every statement in the post made them ask "what's weird about it?" I read that comment as a sign the post chose its reader, someone who types `docker run` every day and hasn't looked underneath.

For that reader each of the five claims is news, and for a kernel developer none of them is. I'd accept that trade in any explainer.

The post's first sentence says its author is new to building runtimes, which tells a kernel developer in one line that the page is written for someone else. I'd say who an explainer is for that early.
