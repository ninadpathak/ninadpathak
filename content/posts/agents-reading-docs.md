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

My llms.txt article from October leaned on one study for whether anything fetches the file, an Ahrefs finding that 97% of published llms.txt files got no request in May 2026. Then on November 10 Fern published [State of Docs: Agents are your top readers](https://buildwithfern.com/post/state-of-docs), built on logs from January to September across the docs sites it hosts.

I think the report is worth your time, and I don't buy its title. On llms.txt it moved me a little: the file is good to have, and the evidence that models fetch it is still thin.

All of which bears on how much [AI search optimization](/articles/ai-search-optimization/) a docs team should take on.

## What I don't buy

The report opens on its headline claim: "Agents now make up more than half of the requests to the docs we host". I believe the number, and I don't think it means what the title says, because a request isn't a reader.

Here's why. Fern counts an agent request on the server, as any fetch of a Markdown route or of llms.txt, and it counts a human page load in the browser, through client-side analytics.

So a person who reads one guide for ten minutes is one page load, and a coding agent wiring up one endpoint can fetch the index and a string of pages on the way. That ratio measures traffic, and I wouldn't read it as a share of readers.

Now, Fern sells a docs platform, and it also publishes its method and its limits, which is why I trust the report enough to argue with it. A limit in that list cuts against me: agents that fetch HTML aren't counted at all, and the report says ChatGPT, Gemini and Perplexity do exactly that.

Another cuts my way. About two thirds of September's agent requests carried a browser or generic user agent, so calling them agents rests on which route they asked for.

Count only the requests that name an AI agent or crawler and the September share is 32.8%, up from 2.3% in January. I think that figure belonged in the title, because a rise of roughly fourteen times needs no help.

And the people didn't leave. Human page loads went from 5.9 million a month to 5.1 million while agent requests grew from 1.3 million to 7.9 million, so by my arithmetic people read about 14% less and agents arrived alongside them.

## What I'd act on

The page mix is the finding I'd change my plans for. Agents spend 31% of their reading on API reference where people spend 18%, and they read the changelog about twice as much.

That makes sense to me if you treat an agent request as a developer's question arriving through a tool. The developer has already chosen the product, and now wants to know what a parameter accepts and what changed last month.

So Fern says to put the next round of work into the reference and the changelog, and I agree. Its sharpest instruction names a page writers skip: "Every error code says what causes it and how to fix it."

Both pages have a worked model on this site. The [API documentation guide](/articles/api-documentation/) writes one reference entry in full, errors included, and the [release notes template](/articles/release-notes-template/) is a starting point for a changelog keyed to endpoint and date.

Where I part with the report is the guides, which it treats as the work to do less of. A person reads guides and comparisons before choosing a product, and no log of Markdown fetches can show that reading, because it happens before an integration exists.

Fern's own spread says as much. Among its larger sites, agents were under a tenth of traffic on some and over nine tenths on others, which I read as the difference between a product used through a UI and one called from code.

So count your own traffic first, and write down what you threw out, as Fern did when it removed 17 million of its own cache and monitoring requests. Agents only show up in that count if they can fetch the pages, and the [AI crawlers guide](/articles/ai-crawlers/) covers which user agents to allow.

## llms.txt is good to have, on thin evidence

My view of llms.txt is that it's good to have and that nobody has shown the models fetching it. Fern's report is the closest anyone has come, so here is what it does and doesn't show.

Fern counted 448,667 fetches of llms.txt in September, with Claude Code the largest named source. That's real, and it's more than my October article allowed for.

But look at who is fetching. These are coding agents working through API docs that one vendor hosts, and the assistants people put questions to, by Fern's own account, fetch only HTML.

Ahrefs looked much wider, at 137,210 domains, and found that 97% of the files got no request at all. So I think both studies hold, and together they say the file gets used as an index by coding agents on API docs and sits unread nearly everywhere else.

Fern describes that use in one line: "an agent reads llms.txt once, then fetches the Markdown for the pages it needs." An index earns its place under that pattern, and a single file holding the whole site doesn't, which is why Fern says it stopped generating llms-full.txt.

So I changed my article. The [llms.txt guide](/articles/llms-txt/) now sets Fern's figures beside the Ahrefs study where it used to cite Ahrefs alone, and it still tells you to check your own server logs.

No traffic log shows whether the integration an agent wrote after reading a page worked. Until someone publishes that, request share measures fetching, and my advice stays where it was: finish the reference and the changelog first, and keep the guides for the person who chooses.
