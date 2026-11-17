---
category: ai-search-optimization
primary_query: ai agent traffic to documentation
siblings:
- ai-crawlers
- llms-txt
bridges:
- slug: api-documentation
  reason: A reference entry written to be read without its neighbours is the model for a page an agent fetches.
- slug: release-notes-template
  reason: A release note that leads with the required action is the model for a page an agent fetches.
date: 2026-11-16
description: Fern says agents are now over half of the requests to the docs it hosts. A close read of the numbers, what they change for docs teams, and what they leave out.
slug: agents-reading-docs
status: published
title: "What Fern's agent traffic report made me change in my llms.txt article"
work_note: "I'm Ninad Pathak, a freelance technical writer. I also run AI-ready documentation audits, which test whether AI crawlers can fetch your docs and whether an answer engine can lift the answers. [Hire me for one](/services/ai-ready-documentation-audit/)."
---

My llms.txt article from October cites one study as its main evidence on whether anything fetches the file, an Ahrefs finding that 97% of published llms.txt files got no request in May 2026. On November 10 Fern published [State of Docs: Agents are your top readers](https://buildwithfern.com/post/state-of-docs), built on logs from January to September across the docs sites it hosts, and those logs say something my article didn't.

They also say less than the title does. The report opens with "Agents now make up more than half of the requests to the docs we host", and a request is not a reader.

The difference decides how much [AI search optimization](/articles/ai-search-optimization/) a docs team should take on.

## What the report counts

Fern sells a docs platform, and nearly every finding is followed by a paragraph headed "How Fern helps". It also publishes its method, which is rarer than the sales copy and is the reason the report deserves a close read.

The headline number is 60.6%, the agent share of all requests in September. The method section defines the two things being compared, and they come from different instruments.

"Agent requests are server-side requests for Markdown routes and llms.txt. Human page loads are browser page views from client-side analytics."

A person who reads one guide for ten minutes counts as one page load, and a coding agent wiring up one endpoint can fetch the index and a string of Markdown pages on the way. The ratio of those two counts measures traffic, and it can't be read as a share of readers.

The report lists its own limits, and the first two pull in opposite directions.

"Human page loads miss people with ad blockers, which raises agent share. Agents that fetch HTML instead of Markdown aren't counted, which lowers it."

The second one cuts against my argument. The report says "ChatGPT, Gemini and Perplexity fetch only HTML", so those agents appear nowhere in the agent count.

The other limit concerns the label: "68% of September's agent requests carry a browser or generic user agent, so for those requests "agent" rests on the route rule." Counting only requests whose user agent names an AI agent or crawler, the report gets 32.8% for September, "up from 2.3% in January."

So the real share sits somewhere this data can't pin down, and "top readers" is a claim it doesn't support. The 32.8% figure belonged in the title, because a roughly fourteenfold rise in named agents needs no help.

The totals hold one more number the headline skips: "Agent requests grew from 1.3 million a month to 7.9 million, while human page loads slipped from 5.9 million to 5.1 million." People read 14% less, by my arithmetic on those two figures, which is a dip.

Agents arrived as a second population alongside the first. The people are still there, and they still decide whether to use your API before any agent fetches a page of it.

## The page mix is the finding to act on

The report's best sentence is "Agents spend 31% of their reading on API reference, while people spend 18%", and it adds that agents read the changelog twice as much as people do. That split makes sense once you treat an agent request as a developer's question arriving through a tool, after the developer has chosen the product, when the question is what a parameter accepts and what changed last month.

Fern's instruction follows from it: "Put the next round of work into the reference and the changelog, not just more guides." The first half is right, and its sharpest line names a page writers skip: "Every error code says what causes it and how to fix it."

Both pages have a worked model on this site. The [API documentation guide](/articles/api-documentation/) writes one reference entry in full, errors included, and the [release notes template](/articles/release-notes-template/) is a starting point for a changelog keyed to endpoint and date.

The second half of the instruction needs a limit. Guides and comparisons are what a person reads before choosing a product, and no log of Markdown fetches can show that reading, because it happens before an integration exists.

The spread across Fern's own sites makes the same point: "Among the 89 Fern sites with at least 5,000 human page loads in September, agents made up less than 10% of traffic on some sites and more than 90% on others." A product called from code sits at one end of that range and a product used through a UI sits at the other.

That makes counting your own traffic the first job, with the definitions written down. Fern removed 17 million of its own cache and monitoring requests before counting, and says of that step "That's why anyone publishing a number like this should say what they threw out."

Agents only appear in such a count if they can fetch the pages, and the [AI crawlers guide](/articles/ai-crawlers/) covers which user agents to allow.

## llms.txt, revisited

Fern counted 448,667 fetches of llms.txt in September, with Claude Code the largest named source. Its summary is "The file was designed with crawlers in mind, but it found its audience in coding agents."

Ahrefs and Fern can both be right, since Ahrefs sampled 137,210 domains across its analytics customers and Fern hosts API docs. My [llms.txt guide](/articles/llms-txt/) ends by telling readers to check their own server logs, and Fern's are the largest set of docs logs I know of.

The usage pattern is the useful part: "an agent reads llms.txt once, then fetches the Markdown for the pages it needs." An index earns its place under that pattern, and a single file holding the whole site doesn't, which is why Fern says it stopped generating llms-full.txt.

What my article should say is narrower than either study: on an API docs site the file gets fetched, by coding agents, as an index. So I've changed it, and the llms.txt guide now sets Fern's figures beside the Ahrefs study where it used to cite Ahrefs alone.

No traffic log shows whether the integration an agent wrote after reading a page worked. Until someone publishes that, request share measures fetching, and the writing decision is the one it always was: finish the reference and the changelog first, and keep the guides for the person who chooses.
