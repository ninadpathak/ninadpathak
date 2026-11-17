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

On October 26 Cloudflare published [a report](https://blog.cloudflare.com/kv-cache-exposure-remediation/) on a bug that sent 155 Workers AI responses back with text from other customers' requests. I've written up the mechanism on my page about the [KV cache](/articles/kv-cache-eviction/), and here I want to look at the report as a piece of writing.

An incident report is [technical documentation](/articles/technical-documentation/) with the hardest audience there is. The readers are customers deciding whether they were affected and engineers deciding whether to trust you again, and I think this one serves both well.

## The count comes before the explanation

I'd copy the order of the opening first. The dates, the model and the number of affected responses are all in the first two paragraphs, before a word about how the cache works.

That's the right order because it's the reader's order. Somebody who used that model in early September has one question, and the report answers it with a threshold they can check against their own logs: only prompts longer than 681,280 tokens were affected.

The technical account is long and good, and it comes after. A report that makes a customer read the root cause to find out whether they were exposed has its sections in the wrong order.

## The sentence I'd copy

The line I keep returning to sits in the explanation of the misconfiguration: "We were aware of this mismatch before launch."

Nobody is forced to write that. The report could have said the pool was undersized and left the reader to assume it was an oversight, and the facts would have been identical.

What the sentence adds is the belief behind the decision. The team expected the engine to return an error for any prompt it couldn't process, and their long-context tests came back successful, so the mismatch looked safe.

I think that's the part of a postmortem that teaches. A bug is specific to one system, and "our tests passed, so we assumed the error path worked" is a mistake any team reading it can recognize in its own launch checklist.

## The title names the wrong thing

Here's my one disagreement. The title is "Cross-request KV cache exposure in the GLM-5.3 Workers AI model", and a [commenter on Hacker News](https://news.ycombinator.com/item?id=50253748) objected that the bug has little to do with the model, writing that Cloudflare should own it "instead of naming other (imo innocent) parties in the title".

I agree with the complaint and I can see why the title happened. The model's name is how an affected customer finds the page, and the report's own text is clear that the causes were a pool configuration and an engine bug.

But a title is the only part of a report that travels without the rest. Anyone who saw the headline in a feed came away connecting a leak with a model that, on the report's own account, did nothing wrong.

I'd have put the cause in the title and the model in the first sentence. Customers searching for the model name still land on the page, and the headline stops assigning the fault by accident.

## The fixes can be checked

The last thing I'd copy is how the remediation is written. The timeline is in UTC to the minute, and the hardening section lists each upstream change by pull request number and the release it shipped in.

That turns "we fixed it" into something a reader can verify. It's the same instinct as in [release notes developers trust](/articles/writing-release-notes/), where every line has to help a reader act on a change or verify it.

The report also names what it couldn't rule out. It says there's no evidence of deliberate exploitation and explains what the evidence was, the timing and volume of the requests, which is different from claiming it didn't happen.

When agents start closing incidents by themselves, this is the standard I'd hold their write-ups to as well. My essay on [SREs, agents and runbooks](/articles/agents-on-call-runbooks/) asks for a short account after every incident, and Cloudflare's report is what the long version looks like: the count, the belief that turned out wrong, and fixes with numbers on them.
