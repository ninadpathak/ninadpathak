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
description: Cloudflare's report on a KV cache leak in Workers AI puts the count first and admits what the team knew before launch. I'd copy both, and I'd change the title, which names a model for an infrastructure bug.
slug: cloudflare-kv-cache-incident-report
status: published
title: "What I'd copy from Cloudflare's KV cache incident report"
work_note: "An incident report is documentation written on the worst day, and it gets read more closely than anything else a company publishes. I'm Ninad Pathak, a freelance technical writer for developer-tool companies, and I run the product before I write about it. [Let's work together](/services/)."
---

On October 26 Cloudflare published [a report](https://blog.cloudflare.com/kv-cache-exposure-remediation/) on a bug that sent 155 Workers AI responses back with text from other customers' requests. My page about the [KV cache](/articles/kv-cache-eviction/) explains how the leak happened, and this essay looks at Cloudflare's report as a piece of writing.

An incident report is [technical documentation](/articles/technical-documentation/) with two demanding readers. A customer reads the report to find out whether their data leaked, an engineer reads it to decide whether to trust Cloudflare again, and I think this report serves both of them well.

## The count comes before the explanation

The first thing I'd copy from Cloudflare's report is the order of its opening. The dates of the exposure, the name of the model and the number of affected responses are all in the first two paragraphs, before the report explains anything about how a KV cache works.

That order matches the order of a customer's questions. A customer who used GLM-5.3 on Workers AI in early September wants to know one thing first, and the report answers with a number the customer can check against their own logs: only prompts longer than 681,280 tokens were affected.

The technical explanation takes up the larger part of the report, and it comes after those two paragraphs. A report that puts the root cause first makes a customer read about prefill pools before learning whether their data was exposed.

## The sentence I'd copy

The sentence I keep returning to is in the report's explanation of the misconfiguration: "We were aware of this mismatch before launch."

Cloudflare didn't have to write that sentence. The report could have said that the cache pool was smaller than the context window and stopped, and every reader would have assumed nobody at Cloudflare had noticed.

The sentence tells the reader what the team believed when it shipped. The team expected the inference engine to return an error for any prompt too long for the pool, and their long-context tests came back successful, so the smaller pool looked safe.

I think the belief is the part of a postmortem that other teams can learn from. The bug itself is specific to Cloudflare's setup, and "our tests passed, so we assumed the error path worked" is a mistake that any team can find in its own launch checklist.

## The title names the GLM-5.3 model for a Cloudflare bug

The title is my one disagreement with the report. Cloudflare titled it "Cross-request KV cache exposure in the GLM-5.3 Workers AI model", and a [commenter on Hacker News named jacquesm](https://news.ycombinator.com/item?id=50253748) objected that the bug has little to do with GLM-5.3, writing that Cloudflare should own it "instead of naming other (imo innocent) parties in the title".

I agree with jacquesm, and I can see why Cloudflare chose the title. A customer who used GLM-5.3 will search for the model's name, and the body of the report says clearly that the causes were Cloudflare's pool configuration and a bug in the SGLang engine.

The problem is that a title gets read without the report under it, in a feed or in a search result. A reader who saw this headline and nothing else would connect a data leak with GLM-5.3, a model that, by the report's own account, did nothing wrong.

I'd have named the cause in the title and the model in the first sentence, for example "Cross-request data exposure from an undersized KV cache pool on Workers AI". A customer searching for GLM-5.3 would still find the page through its first sentence, and the headline would no longer blame Z.ai's model.

## The fixes are listed by pull request number

The last thing I'd copy is the way the report describes the fixes. Its timeline gives each step in UTC to the minute, and its hardening section lists each change made to SGLang by pull request number and by the release that shipped it.

A list of pull request numbers lets an engineer open each change and read the code, which the sentence "we fixed it" doesn't. My page on [release notes developers trust](/articles/writing-release-notes/) asks for the same thing, that every line helps a reader act on a change or verify it.

The report is also careful about what Cloudflare could not prove. It says Cloudflare found no evidence of deliberate exploitation and then states the evidence, which was the timing and volume of the long requests, and that is a weaker and more honest claim than saying no exploitation happened.

Coding agents are starting to close incidents without a person, and I'd hold an agent's incident write-up to the standard of this report. My essay on [SREs, agents and runbooks](/articles/agents-on-call-runbooks/) asks an agent for a short account after every incident, and Cloudflare's report shows what a full account contains: how many customers were affected, what the team wrongly believed, and each fix with a number a reader can look up.
