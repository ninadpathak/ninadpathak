---
category: ai-search-optimization
date: 2026-10-22
description: What AEO, GEO and SEO each mean, what Google and OpenAI document about AI search, and six checks that decide whether developer docs can be found and quoted.
slug: aeo-for-developer-docs
status: published
takeaways:
- SEO, AEO and GEO name the same goal from different sides, and Google says optimizing for its generative AI search is still SEO.
- Google's AI features need an indexed page that can show a snippet and a site included in Search Console's generative AI control, with no special schema or AI text files.
- Check crawler access by agent and whether each passage survives being quoted alone.
title: 'AEO vs GEO vs SEO: What Changes for Developer Docs'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for developer products, with pages that search engines and AI assistants can find, quote and cite.'
---

Google's [guide to generative AI search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) says that optimizing for it "is optimizing for the search experience, and thus still SEO." The [GEO paper](https://arxiv.org/abs/2311.09735), accepted to KDD 2024, reported that rewriting content could raise its visibility in generative engine responses by up to 40% on its own benchmark.

Both are about getting a page into an answer, and for developer documentation they lead to the same work. I treat AEO and GEO as names for the editing SEO already asks of docs, plus two checks: crawler access by agent, and passages that still make sense when quoted alone.

## What AEO, GEO and SEO mean

The terms come from different places, and only SEO and GEO have a defining source:

| Term | What it aims at | Where the definition comes from |
|---|---|---|
| SEO (search engine optimization) | Being found and shown in search results, including Google's AI Overviews and AI Mode | Search engines' own documentation, such as Google Search Central |
| AEO (answer engine optimization) | Being the passage an answer engine quotes, from featured snippets to AI assistants | An industry term with no single defining document |
| GEO (generative engine optimization) | Visibility in the responses of generative engines | The 2023 GEO paper by Aggarwal and colleagues, which also built the GEO-bench benchmark |

Google's guide says you don't need to write in a specific way for generative AI search, which puts AI Overviews inside ordinary SEO.

## What Google and OpenAI document about AI search

Google's page on [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) requires a page in AI Overviews and AI Mode to be indexed and eligible to show in Search with a snippet. It adds that "there are no additional technical requirements," and that no special schema.org structured data is needed.

Google's generative AI search guide adds a site-level condition: the site must be included in Search generative AI features in Search Console. The [Search generative AI control](https://support.google.com/webmasters/answer/16908024) includes every property by default, and a property inherits an exclusion from its closest configured parent.

The same page names the controls that limit what Google shows: `nosnippet`, `data-nosnippet`, `max-snippet` and `noindex`. A `nosnippet` added to keep a page out of AI answers also removes its snippet from regular results.

OpenAI documents [two separate crawlers](https://developers.openai.com/api/docs/bots). OAI-SearchBot surfaces sites in ChatGPT's search features and GPTBot gathers training data, and OpenAI says "each setting is independent of the others."

So a docs site can allow OAI-SearchBot and disallow GPTBot. That allows search crawling while opting out of GPTBot's collection for model training.

Google Search doesn't read [llms.txt](/articles/llms-txt/) or other AI text files, and its AI features need no extra schema.

## Six checks for a documentation page

I'd check access first, partly with the tools on this site, then read each passage on its own. Each check says what to fix when it fails:

1. **The page can show a snippet.** Paste the page's HTML into the [AI Overviews checker](/ai-overviews-checker/), which flags `noindex`, `nosnippet` and `max-snippet:0`. If one of them is set, remove it unless keeping the page out of search was the point. A positive `max-snippet` only shortens the snippet and can stay.
2. **The site is included in Search Console.** Open the Search generative AI control for the property and its parents, and confirm the site is included. If it is excluded, or inherits an exclusion, change the control on the property that set it.
3. **The crawlers you want can reach it.** Run your domain through the [AI crawler access checker](/ai-crawler-checker/), which reports search crawlers and training crawlers separately. If a search crawler you want is blocked, fix that agent's `robots.txt` rule and leave the training rules as you chose them.
4. **The opening answers first.** Read the first paragraph alone, and if it introduces the topic without answering the question in the title, rewrite it so the answer comes first.
5. **Each section stands alone.** Read one section without the rest of the page, and if it opens with "this" or "it" pointing back to an earlier paragraph, name the subject again.
6. **Evidence sits next to its claim.** A version, date or number quoted alone should still say what it counts and where it came from, so move the date or source into the same sentence if it lives elsewhere on the page.

The snippet, Search Console and crawler checks are about access, and Google documents the snippet and Search Console checks as requirements. The opening, section and evidence checks are editing heuristics: the AI Overviews checker flags likely problems, and neither tool predicts whether a page will be cited.

## What a documentation team adds

An indexed, snippet-eligible docs page on a site included in the Search generative AI control meets both documented eligibility conditions for Google's AI features. What it may still need is a `robots.txt` rule per crawler, and an editing pass for passages that lose their meaning when lifted out.

The [technical SEO checklist for documentation](/articles/docs-seo/) covers crawling, rendering and indexing, which come before any of this. A page Google can't index can't appear in AI Overviews either.

## FAQ

### What is the difference between AEO, GEO and SEO?

SEO is about being found and shown in search results. AEO is an industry term for being the passage an answer engine quotes, and GEO, from a 2023 paper, is about visibility in generative engine responses.

### Is GEO replacing SEO?

For Google, no: its guide says optimizing for generative AI search is still SEO. For other engines, check each one's own documentation for its crawlers and controls.

### Do I need schema markup or llms.txt for AI Overviews?

No. Google says AI Overviews and AI Mode need no special schema.org markup, and Google Search doesn't use llms.txt or other AI text files.

### How do I allow ChatGPT search crawling but opt out of GPTBot?

Allow OAI-SearchBot and disallow GPTBot in `robots.txt`. OpenAI documents the two settings as independent, and it describes GPTBot as the crawler it uses to make its generative AI foundation models more useful and safe.
