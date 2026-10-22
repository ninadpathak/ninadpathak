---
category: ai-search-optimization
date: 2026-10-22
description: What an llms.txt file is, what the proposal requires, what Google, Chrome and server logs say about its use, and four real files checked against the proposal.
slug: llms-txt
status: published
takeaways:
- llms.txt is a Markdown index of a site for language models, and an H1 is its only required part.
- Google Search does not use it, and an Ahrefs study found 97% of published files got no request in May 2026.
- Validate the structure and read your server logs separately, because a clean file and a fetched file are different facts.
title: 'llms.txt: What It Is, What It Does, and Four Real Files Checked'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for developer products, including the indexes and reference pages that AI tools and readers use to find them.'
---

Cloudflare's root llms.txt lists its products, and each entry links to that product's own llms.txt with the full index of its pages. Stripe's file opens with prose instructions for coding agents before its first list of links.

Both are valid Markdown, and both answer to the same short proposal. They read nothing alike, and the validator on this site finds no errors in one and 21 in the other, though neither result says whether anything fetches the file.

## What llms.txt is

llms.txt is a Markdown index for the site or section where it lives, written for language models and the tools around them. It sits at the root path `/llms.txt` or at a subpath such as `/docs/llms.txt`, where it covers the pages under that path.

The [llms.txt proposal](https://llmstxt.org/index.md), published by Jeremy Howard on 2024-09-03, defines its parts in this order:

1. An H1 with the name of the project or site, the only required section.
2. A blockquote with a short summary.
3. Zero or more sections of any Markdown except headings, for detail.
4. Zero or more H2 sections containing "file lists": links to pages with more detail, each with optional notes.

Everything after the H1 is optional. A file with a title and nothing else meets the proposal, and it helps no one find anything.

## Does llms.txt work?

Google's [guide to generative AI search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), updated 2026-07-10, says you don't need AI text files to appear in Google Search and that "Google Search itself doesn't use them."

Chrome's [Lighthouse llms.txt audit](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt), updated 2026-05-05, treats the file as optional. A missing file gets a Not Applicable result, and the audit flags only a server error when the file is requested.

Server logs answer whether anything fetches the file. An [Ahrefs study published on 2026-06-15](https://ahrefs.com/blog/llmstxt-study/) used its Web Analytics and Bot Analytics data across 137,210 domains and found that 97% of published llms.txt files received no request in May 2026, from bots or people.

Ahrefs notes that its customers skew technical and SEO-aware, and it didn't check whether the files followed the proposal.

## Four real files, checked against the proposal

The table comes from the same validation engine that powers the [llms.txt validator](/llms-txt-validator/), run on four public files fetched with curl at 14:58 UTC on 2026-10-22. Each owner can change its file at any time, and Stripe's server varies its response by request headers, so these counts are a snapshot of what that request received:

| File | Lines | Errors | Warnings |
|---|---|---|---|
| [llmstxt.org](https://llmstxt.org/llms.txt) | 11 | 0 | 0 |
| [Cloudflare Developer Documentation](https://developers.cloudflare.com/llms.txt) | 144 | 0 | 1 |
| [Anthropic Developer Documentation](https://platform.claude.com/llms.txt) | 887 | 24 | 159 |
| [Stripe Documentation](https://docs.stripe.com/llms.txt) | 743 | 21 | 75 |

Errors and warnings measure distance from the proposal's structure as the validator reads it. They don't rank the files, and they say nothing about whether an agent found a file useful.

### llmstxt.org: the proposal at its smallest

The proposal's own file has a title, a one-sentence summary in a blockquote, and one Docs section of annotated links: the proposal, its Python library docs and an ed demo. Each line either names the site or points somewhere, which makes it the cleanest example for a small site.

### Cloudflare: an index of indexes

Cloudflare's root file groups 112 product links under nine H2 headings such as Application performance, and each product links to its own llms.txt. That keeps the root file to 144 lines while the full page lists live one level down.

The single warning is an ordering detail. A sentence sits between the H1 and the summary blockquote, where the proposal puts the summary first.

### Anthropic and Stripe: documentation exports

Anthropic's file opens with Root URL and MCP server sections, then lists 808 links, with 12 nested `###` headings inside its H2 sections. Its 24 errors are those 12 nested headings and 12 list items without a link, and 147 of its 159 warnings are links followed by text without the colon the proposal uses to introduce a note.

Stripe's file opens with instructions for coding agents, such as checking the npm registry for current package versions, before its first section.

Its 21 errors fall into three kinds: 16 nested headings, list items without a link, and 2 malformed links. Across 27 sections and 468 links, 58 of its 75 warnings are lines that aren't list items inside link sections.

Both files are readable Markdown. They work more like documentation exports than the flat H2-and-list shape the proposal describes, which is why the counts are high.

## How to write one

For a small site, I prefer the llmstxt.org pattern: one clear summary, a few sections, and a note on each link saying why the page matters. For a large documentation set, Cloudflare's index-of-indexes keeps the root file from turning into a second sitemap.

The [llms.txt generator](/llms-txt-generator/) drafts a file from a site's discovered pages when writing the first version by hand adds nothing. Someone still has to choose which pages earn a place and keep the file current.

The [validator](/llms-txt-validator/) checks the structure, and your server logs show whether anything requests `/llms.txt`. For the checks Google and OpenAI do document for AI search, see [AEO vs GEO vs SEO for developer docs](/articles/aeo-for-developer-docs/).

## FAQ

### What is llms.txt?

llms.txt is a Markdown index for the site or section where it lives, listing the pages its owner wants language models and AI tools to read first. The proposal at llmstxt.org requires only an H1 and suggests a summary and H2 sections of annotated links.

### Does Google use llms.txt?

No. Google's guide to generative AI search says Google Search doesn't use llms.txt or other AI text files, and you don't need one to appear in Search.

### Do AI crawlers request llms.txt?

Ahrefs found that 97% of published llms.txt files received no request in May 2026, from bots or people. Check your own server logs before assuming yours is fetched.

### What is the difference between llms.txt and robots.txt?

robots.txt tells crawlers which paths they may fetch. llms.txt is an optional index of pages worth reading, and it grants or blocks nothing.
