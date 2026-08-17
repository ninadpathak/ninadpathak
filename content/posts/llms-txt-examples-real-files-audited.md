---
category: ai-search-optimization
date: 2026-08-17
description: See how four public llms.txt files differ, which parts match the proposal,
  and why valid syntax cannot prove that an AI system will use them.
slug: llms-txt-examples-real-files-audited
status: published
tags:
- llms-txt
- ai-search
- answer-engines
takeaways:
- A public llms.txt file is a Markdown index, not a crawler directive or a citation
  signal.
- Real files range from small curated maps to generated documentation exports that
  do not follow the proposal closely.
- Validation can check a file's structure, but only server logs can show whether
  anything fetched it.
title: 'llms.txt Examples: Four Public Files Audited Against the Proposal'
updated: 2026-08-17
---

An llms.txt file can be a compact map of documentation, but it is not evidence that an AI system will fetch, use, or cite the site. I built the validator on this site to separate the proposal's rules from conventions.

The audit below applies it to four public files retrieved on 17 August 2026.

Two files stayed close to the proposed structure. The other two worked more like generated documentation exports, with nested headings and prose that the proposal does not place inside link sections.

## Four live files use llms.txt in two different ways

The [llms.txt proposal](https://llmstxt.org/index.md) defines a Markdown index with one required H1. It permits a summary, free-form detail, and H2 sections containing lists of links in that order.

The audit used the production [llms.txt validator](/llms-txt-validator/) on each public file. The counts are dated because every owner can regenerate or edit its file after publication.

| Public file, retrieved 17 August 2026 | What the file contained | Validator result |
| --- | --- | --- |
| [llmstxt.org](https://llmstxt.org/llms.txt) | Eleven lines, one section, and an annotated link list | No errors or warnings |
| [Cloudflare Developer Documentation](https://developers.cloudflare.com/llms.txt) | One hundred thirty-seven lines, nine sections, and 105 links | No errors and one warning because the summary did not sit directly below the H1 |
| [Anthropic Developer Documentation](https://platform.claude.com/llms.txt) | Six hundred thirty-seven lines and 566 links, including language inventories and nested heading groups | Twenty-four errors and 98 warnings, mostly for plain list items, nested headings, and link text outside the proposed form |
| [Stripe Documentation](https://docs.stripe.com/llms.txt) | Six hundred forty-one lines and 454 links, mixed with explanatory product prose | Twenty errors and 66 warnings, including nested headings, prose inside link sections, and repeated destinations |

Those counts describe conformance with this validator's reading of the v2 proposal. They do not rank the files, and they do not show whether an agent found the file useful.

## llmstxt.org shows the proposal in its smallest useful form

The llmstxt.org file names the project, explains the proposal in one blockquote, and groups its annotated links under a Docs heading. Its structure leaves little room for ambiguity because every line either identifies the file or points to a resource.

The file is the cleanest example when the job is orientation. An agent or a person can see the proposal, library documentation, and demonstration without scanning a full site map.

The example also exposes how permissive the proposal is. A lone H1 meets its only stated requirement, even though a file with no links would not help a reader find anything.

## Cloudflare uses one index to route readers into smaller indexes

Cloudflare's root file groups products under headings such as Application performance and Developer platform. Each list item names a product, links to that product's own llms.txt file, and explains what the product does.

The useful pattern is delegation rather than completeness. The root file stays navigable by sending a reader to a narrower index instead of listing every documentation page in one enormous file.

The validator raised one warning because Cloudflare places a plain sentence between the H1 and its summary blockquote. That is a small ordering difference, not evidence that the links are broken or that an agent will reject the file.

## Anthropic and Stripe treat llms.txt as a documentation export

Anthropic's file starts with site information, a language inventory, and a raw platform URL before its large English documentation index. It then uses nested subheadings to divide hundreds of links inside broader sections.

That shape is easy for a person to scan, but it is not the flat H2-and-link-list shape the proposal describes. The validator therefore reports structural errors even though the file remains readable Markdown and its links are usable.

Stripe takes the export idea further by mixing link lists with substantial product guidance. Its file explains concepts such as Elements and Connect, then uses nested subheadings and additional prose to organize detailed routes.

The Stripe file may give an agent useful context if the agent deliberately fetches it. The audit cannot establish that premise, and a high error count cannot establish the opposite.

## Syntax validation tells you about the file, not its audience

A validator can answer whether a file has an H1, whether its links are parseable, and whether optional sections follow the proposed order. It cannot tell you whether ChatGPT, Claude, Perplexity, or another system discovers the file and acts on it.

Google's [generative AI guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), updated 10 July 2026, is explicit about its own products: Google Search does not use llms.txt or other AI text files. Google also says creating one will neither help nor harm Search visibility or rankings.

Chrome's [Lighthouse llms.txt audit](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt), updated 5 May 2026, treats the file as optional. A missing file receives a not-applicable result.

The audit flags a server error during retrieval.

Server logs are the evidence for actual retrieval. An [Ahrefs study published 15 June 2026](https://ahrefs.com/blog/llmstxt-study/) examined 137,210 domains using its Web Analytics and Bot Analytics data and found that 97% of published llms.txt files received no request in May 2026.

The Ahrefs sample skews toward technical and SEO-aware sites, and the study did not test whether the files followed the proposal. It still establishes a useful boundary: publication and valid structure are not evidence of readership.

## A fetched file still does not prove a visibility effect

A bot request proves that a URL was requested. It does not prove that the bot parsed the file, followed a link, used the retrieved page in an answer, or changed a citation decision.

The cats.txt falsification makes that distinction concrete. The [fictional standard](https://catstxt.org/) and [AI bot requests for a fake file](https://www.linkedin.com/posts/markseo_i-can-confirm-that-the-catstxt-file-on-i83-activity-7371576836121587712-2okf) were both still public when checked on 17 August 2026.

[ChatGPT also described cats.txt as if it were real](https://www.linkedin.com/posts/markseo_people-look-this-is-why-using-chatgpt-activity-7372345447602089985-ZvJj). A fetch, an index entry, or a model repeating the file's claims therefore cannot distinguish a useful convention from a fabricated one.

## Publish llms.txt as a utility, not a visibility claim

An llms.txt file is defensible when you want to maintain a concise, machine-readable map for tools or people that choose to request it. The file should earn its maintenance cost through that direct utility, not through a promise of AI citations.

For a small site, I prefer the llmstxt.org pattern: one clear description, a few sections, and notes that explain why each destination matters. For a large documentation estate, Cloudflare's index-of-indexes pattern avoids turning the root file into another unfiltered sitemap.

The [llms.txt generator](/llms-txt-generator/) can produce an editable draft from a site's discovered pages when writing that first index by hand would add no value. Generation does not settle the editorial work.

Someone still has to choose which pages deserve a place and keep the file current.

Run the finished file through the validator to catch structural mistakes, then inspect server logs if you need to know whether anything requests it. Keep those two questions separate, because a clean file and a read file are different facts.
