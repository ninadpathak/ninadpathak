---
category: technical-documentation
primary_query: none
siblings:
- agents-on-call-runbooks
- writing-release-notes
bridges:
- slug: kv-cache-eviction
  reason: That page explains the cache the incident report is about.
date: 2026-11-18
description: Cloudflare's report on a KV cache leak in Workers AI puts the count of affected responses first and admits what the team knew before launch. I'd copy both. I'd change the title, which puts a model's name ahead of Cloudflare's own configuration, and I'd tell the customers whose text leaked what to check.
slug: cloudflare-kv-cache-incident-report
status: published
title: "What I'd copy from Cloudflare's KV cache incident report"
work_note: "An incident report is documentation that customers read line by line. I'm Ninad Pathak, a freelance technical writer for developer-tool companies, and I run the product before I write about it. [Let's work together](/services/)."
---

On October 26 Cloudflare published [a report](https://blog.cloudflare.com/kv-cache-exposure-remediation/) on a bug that sent 155 Workers AI responses back with text from other customers' requests. My page about the [KV cache](/articles/kv-cache-eviction/) explains how the leak happened, and this essay looks at Cloudflare's report as a piece of writing.

An incident report is [technical documentation](/articles/technical-documentation/) with two demanding readers. A customer reads the report to find out whether they were involved, an engineer reads it to decide whether to trust Cloudflare again, and I think this report serves the engineer well and the customer only in part.

## The count comes before the explanation

The first thing I'd copy from Cloudflare's report is the order of its opening. The dates of the exposure, the name of the model and the number of affected responses are all in the first two paragraphs, before the report explains anything about how a KV cache works.

That order matches the order of a customer's questions. A customer who used GLM-5.3 on Workers AI between August 27 and September 9 wants to know first whether they were involved, and the report gives a number to check against their own logs: all 155 affected responses went to prompts longer than 681,280 tokens.

The report does less for the other group of customers, the ones whose prompts may have been the text that leaked. It gives them nothing to check, and it doesn't say whether Cloudflare told them.

The technical explanation takes up the larger part of the report, and it comes after those two paragraphs. A report that puts the root cause first makes a customer read about prefill pools before learning whether their data was exposed.

## Cloudflare says it knew about the mismatch before launch

The sentence I keep returning to is in the report's explanation of the misconfiguration: "We were aware of this mismatch before launch."

Cloudflare didn't have to write that sentence. The report could have said that the cache pool was smaller than the context window and stopped, and I'd have assumed nobody at Cloudflare had noticed.

The sentence tells the reader what the team believed when it shipped. The team expected the inference engine to return an error for any prompt too long for the pool, and their long-context tests came back successful, so the smaller pool looked safe.

I think the belief is the part of a postmortem that other teams can learn from. The bug is specific to Cloudflare's SGLang setup, and the mistake behind it is one any team can find in its own launch checklist: the tests checked for a 200 status code and nobody read the response.

## The title names the GLM-5.3 model for a Cloudflare bug

The title is my one disagreement with the report. Cloudflare titled it "Cross-request KV cache exposure in the GLM-5.3 Workers AI model, and our remediation with SGLang", and a [commenter on Hacker News named jacquesm](https://news.ycombinator.com/item?id=50253748) objected that the bug has little to do with GLM-5.3, writing that Cloudflare should own it "instead of naming other (imo innocent) parties in the title".

I agree with jacquesm, and I can see why Cloudflare chose the title. A customer who used GLM-5.3 will search for the model's name, and the title does name SGLang, the engine with the bug.

But the title puts the model first and never says the undersized pool was Cloudflare's own configuration.

The problem is that a title gets read without the report under it, in a feed or in a search result. A reader who saw this headline and nothing else would connect a data leak with GLM-5.3, a model that, by the report's own account, did nothing wrong.

I'd have named the cause in the title and the model in the first sentence, for example "Cross-request data exposure from an undersized KV cache pool on Workers AI". A customer searching for GLM-5.3 would still find the page through its first sentence, and the headline would say whose pool it was.

## The fixes are listed by pull request number

The last thing I'd copy is the way the report describes the fixes. Its timeline gives each step on September 9 in UTC to the minute, and a table near the end lists each change to SGLang by pull request number and by the release that shipped it.

A list of pull request numbers lets an engineer open each change and read the code, which the sentence "we fixed it" doesn't. My page on [release notes developers trust](/articles/writing-release-notes/) asks for the same thing, that every line helps a reader act on a change or verify it.

The report is also careful about what Cloudflare could not prove: it gives the evidence first, the timing and volume of the long requests, and then says Cloudflare found no evidence of deliberate exploitation. That is a weaker and more honest claim than saying no exploitation happened.

Coding agents are starting to close incidents without a person, and I'd hold an agent's incident write-up to the standard of this report. My essay on [SREs, agents and runbooks](/articles/agents-on-call-runbooks/) asks an agent for a short account after every incident, and Cloudflare's report shows what a full account contains: how many responses were affected, what the team wrongly believed, and each fix with a number a reader can look up.
