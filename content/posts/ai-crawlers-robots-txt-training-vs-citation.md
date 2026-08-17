---
category: ai-search-optimization
date: 2026-08-17
description: Separate AI training crawlers from citation crawlers, audit robots.txt safely, and understand what each block prevents.
slug: ai-crawlers-robots-txt-training-vs-citation
status: published
tags:
- ai-search
- answer-engines
- ai-crawlers
takeaways:
- Blocking a training crawler does not necessarily block the same company's search or citation crawler.
- A robots.txt response can change with the requesting user agent, so one scripted fetch may not show what a crawler receives.
- Robots.txt states a preference. Server logs and edge controls show whether a crawler can actually reach the site.
title: 'AI Crawlers in robots.txt: Training, Citation, and What Each Block Costs'
updated: 2026-08-17
---

Ninadpathak.com blocks eight crawlers associated with AI training and leaves its citation routes open. I checked the live robots.txt on 17 August 2026 because a block on `GPTBot` or `ClaudeBot` looks broader than it is.

The distinction is simple: training crawlers collect material that may shape a future model, while citation crawlers find or retrieve pages at request time. A site can refuse the first use without disappearing from the second.

## A company name does not identify what its crawler does

OpenAI documents `OAI-SearchBot` as the agent that surfaces sites in ChatGPT search and `GPTBot` as the agent for possible model training. Its [crawler documentation](https://developers.openai.com/api/docs/bots) says the settings are independent.

Anthropic separates model development from search and user-requested retrieval. Its [crawler table](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) assigns those jobs to distinct agents.

The cost of a block therefore belongs to the token, not the company name.

| Platform | Agent used for citation or retrieval | Agent used for training | What a full block costs |
| --- | --- | --- | --- |
| ChatGPT | `OAI-SearchBot` | `GPTBot` | Blocking `OAI-SearchBot` removes the site from ChatGPT search answers, apart from possible navigational links. |
| Claude | `Claude-SearchBot` and `Claude-User` | `ClaudeBot` | Blocking the search or user agent can reduce retrieval in Claude. Blocking `ClaudeBot` opts future material out of training. |
| Perplexity | `PerplexityBot` and `Perplexity-User` | No training agent listed in its crawler guide | Blocking `PerplexityBot` removes the route Perplexity uses to surface and link sites in search results. |
| Google Search | `Googlebot` | `Google-Extended` controls separate Gemini uses | Blocking `Googlebot` affects Search, including AI Overviews and AI Mode. Blocking `Google-Extended` does not. |

Perplexity states that `PerplexityBot` surfaces and links sites but does not crawl for foundation-model training. Its [official crawler page](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) also warns that a WAF can deny access even when robots.txt permits it.

Google's naming creates the easiest mistake. [Google's crawler documentation](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers) says `Google-Extended` does not affect inclusion or ranking in Google Search, while `Googlebot` governs Search features.

## This site's training opt-out keeps citation crawlers open

The live file blocks `GPTBot` and `ClaudeBot`. It also blocks `CCBot`, `Google-Extended`, and `Applebot-Extended`.

The remaining blocked group contains `Bytespider`, `meta-externalagent`, and `Amazonbot`. Cloudflare classifies those agents as AI crawlers in its [bot reference](https://developers.cloudflare.com/ai-crawl-control/reference/bots/), distinct from the AI Search and AI Assistant categories used for citation or user retrieval.

None of those rules blocks `OAI-SearchBot`, `Claude-SearchBot`, or `Claude-User`. The wildcard group allows them at the site root, as it does `PerplexityBot` and `Googlebot`.

That policy is a training opt-out with citation access preserved. It is not a promise that any assistant will cite the site, because access only removes one possible technical obstacle.

The [AI crawler access checker](/ai-crawler-checker/) makes this separation explicit for a pasted file or domain. It reports the rule selected for each agent instead of treating every AI-related `Disallow` as the same failure.

## Cloudflare manages the block list before the origin file

The first part of this site's robots.txt is managed by Cloudflare. Cloudflare's [managed robots.txt documentation](https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/) shows the same block list and explains that it prepends managed rules to an existing origin file.

That matters during an audit because the repository may contain only the origin portion. The response at `/robots.txt` is the artifact a crawler reads after the edge has changed it.

The managed file also carries a content signal that permits search while refusing AI training. That signal expresses a use preference, but it does not replace the user-agent rules understood by the named crawlers.

## One robots.txt fetch may not show what a crawler receives

Cloudflare varied this site's robots.txt by requesting user agent during the 17 August audit. Python's default urllib agent received a shorter response with no `Sitemap` line, while Googlebot, curl, and a browser agent received the full file.

The current responses measured 1,836 bytes for urllib and 1,924 bytes for Googlebot. The important result is not the byte count itself: the auditing client changed the policy document it was trying to inspect.

A script that fetches robots.txt once under its own user agent can therefore report the wrong file for the crawler under review. Fetch the file using the target crawler's token, record the response status, and compare the body with an ordinary browser request.

The [llms.txt evidence audit](/articles/llms-txt-examples-real-files-audited/) reaches the same boundary from another file type: publishing a machine-readable file does not prove that an assistant fetches or uses it. Server logs remain the evidence for retrieval.

## Robots.txt matching can reverse a casual reading

The Robots Exclusion Protocol selects the most specific matching user-agent group. A named group replaces the wildcard group for that crawler rather than inheriting its rules.

Within the selected group, the longest matching path rule wins. An `Allow` wins when equally specific allow and disallow rules match, so reading top to bottom is not enough.

A generic text search for `Disallow: /` is therefore a poor audit. The question is which group applies to one crawler at one path.

## Robots.txt cannot prove that access works

The limitation is enforcement: robots.txt is advisory. Cloudflare states that its managed file expresses a preference, and an edge rule is needed to enforce a block.

The reverse failure also exists. A file may allow `PerplexityBot`, but a WAF can still challenge its request before the crawler reaches the page.

Access also says nothing about whether a passage can stand on its own in an answer. The guide to [page extractability for answer engines](/articles/what-makes-a-page-extractable-by-answer-engines/) separates that editorial test from crawler access.

Use logs to confirm that the expected agent requested robots.txt and content pages. Verify published IP ranges or signed bot identity where the platform provides them, because any client can copy a user-agent string.

## Block the use you reject, then verify the route you kept

Start with the outcome, not a list of bot names. If the goal is to refuse model training while remaining available for search answers, block the documented training token and leave the search token open.

Then test the exact path under the exact citation agent. A clean robots.txt result is the policy layer, and a successful page fetch is the evidence that the route works.
