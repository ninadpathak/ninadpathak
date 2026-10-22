---
category: ai-search-optimization
date: 2026-10-22
description: Which robots.txt rules block AI training crawlers like GPTBot and which block AI search, plus what 12 developer documentation sites allow.
slug: ai-crawlers
status: published
takeaways:
- GPTBot and ClaudeBot collect training data, and blocking them leaves ChatGPT search and Claude search to OAI-SearchBot and Claude-SearchBot.
- All 12 developer documentation hosts checked on 2026-10-22 allowed every AI and search agent the site's checker knows, and none named an AI agent.
- A crawler follows only the user-agent group that names it, so a named group drops the wildcard rules for that crawler.
title: 'GPTBot, ClaudeBot and OAI-SearchBot: AI Crawlers in robots.txt'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for developer products, including the docs pages that search engines and AI assistants crawl and cite.'
---

GPTBot is the crawler OpenAI uses to collect content that may train its models, and ClaudeBot does the same job for Anthropic. Blocking either one leaves ChatGPT search and Claude's search untouched, because those run on separate agents called OAI-SearchBot and Claude-SearchBot.

None of 12 developer documentation hosts blocks either one. Their robots.txt files, fetched on 2026-10-22, allowed all 17 AI and search agents the [AI crawler checker](/ai-crawler-checker/) knows.

## What each AI crawler does

Each platform names a separate agent for each job, and OpenAI and Anthropic separate their training crawlers from their search agents:

| Platform | Search and citation | Fetches for a user's question | Training |
|---|---|---|---|
| ChatGPT (OpenAI) | `OAI-SearchBot` | `ChatGPT-User` | `GPTBot` |
| Claude (Anthropic) | `Claude-SearchBot` | `Claude-User` | `ClaudeBot` |
| Perplexity | `PerplexityBot` | `Perplexity-User` | None listed |
| Google | `Googlebot`, which covers AI Overviews and AI Mode | None listed | `Google-Extended`, which also controls grounding in Gemini apps and Vertex AI |

OpenAI's [crawler page](https://developers.openai.com/api/docs/bots) says sites that opt out of OAI-SearchBot "will not be shown in ChatGPT search answers, though can still appear as navigational links." It also says "each setting is independent of the others," so a GPTBot block leaves OAI-SearchBot alone.

Anthropic's [crawler article](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler), updated 2026-04-07, says blocking Claude-SearchBot "prevents our system from indexing your content for search optimization." Blocking ClaudeBot signals that new material should be excluded from its model training datasets.

Google-Extended has no crawler of its own. Google's [crawler documentation](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers), updated 2026-10-15, says it "doesn't have a separate HTTP request user agent string" and "does not impact a site's inclusion in Google Search."

So Google-Extended never appears as a user agent in server logs, because Google reads it as a rule while crawling with its usual agents. Google's [AI features page](https://developers.google.com/search/docs/appearance/ai-features) names robots.txt directives for Googlebot as the control for AI Overviews and AI Mode.

## User-triggered fetchers may skip robots.txt

OpenAI says that for ChatGPT-User, "robots.txt rules may not apply," because a person started the request. Perplexity's [crawler guide](https://docs.perplexity.ai/guides/bots) says Perplexity-User "generally ignores robots.txt rules" for the same reason.

A Disallow for either agent states a preference that the fetch may not follow. Anthropic says its bots honor "industry standard directives in robots.txt," and its article doesn't exempt Claude-User.

To see what user fetchers request on your site, count their paths in a combined-format access log. The command matches only the quoted user-agent field, so a referrer that happens to contain an agent's name isn't counted:

```bash
awk -F'"' '$6 ~ /ChatGPT-User|Perplexity-User|Claude-User/ { split($2, req, " "); print req[2] }' access.log | sort | uniq -c | sort -rn | head
```

If a path you disallowed for one of these agents shows up, check the request's IP against the vendor's published ranges below before deciding the rule was ignored. Any client can send those user-agent strings.

## What 12 developer documentation sites allow

The table comes from the engine behind the AI crawler checker, run at path `/` on robots.txt files fetched with curl at 15:53 UTC on 2026-10-22. A site can serve different robots.txt content to different clients, so these results describe what that request received:

| Host | Response | Content-Signal line | AI agents allowed at `/` |
|---|---|---|---|
| docs.stripe.com | 200 | Yes | 17 of 17 |
| developers.cloudflare.com | 200 | Yes | 17 of 17 |
| supabase.com | 200 | Yes | 17 of 17 |
| platform.claude.com | 200 | No | 17 of 17 |
| platform.openai.com | 200 | No | 17 of 17 |
| docs.github.com | 200 | No | 17 of 17 |
| vercel.com | 200 | No | 17 of 17 |
| docs.aws.amazon.com | 200 | No | 17 of 17 |
| learn.microsoft.com | 200 | No | 17 of 17 |
| developer.mozilla.org | 200 | No | 17 of 17 |
| docs.python.org | 200 | No | 17 of 17 |
| nextjs.org | 404 | No | 17 of 17 |

Every file that exists has a single `User-agent: *` group, so none of them names an AI agent or disallows the whole site. Their rules keep crawlers out of specific paths, such as old documentation versions on docs.python.org, and docs.github.com's file has no rules at all.

[RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html), the robots.txt standard, says a crawler that gets a 404 "MAY access any resources on the server," so nextjs.org allows everything too.

The Stripe and Supabase files carry the same `Content-Signal: ai-train=yes, search=yes, ai-input=yes` line as Cloudflare's. Cloudflare's file defines `ai-input` as content used for "real-time taking of content for generative AI search answers" and `ai-train` as "training or fine-tuning AI models."

Content signals add a stated preference for each use on top of the user-agent rules. The crawler pages cited above name the user-agent rules as their control.

## How publishers that block AI crawlers split the jobs

News and publishing sites fetched 20 seconds later do name AI agents, and each splits the jobs differently:

| Site | Training agents blocked at `/` | Search agents blocked at `/` |
|---|---|---|
| nytimes.com | 7 of 7 | OAI-SearchBot, Claude-SearchBot and PerplexityBot |
| theguardian.com | 5 of 7, with GPTBot and Google-Extended allowed | Claude-SearchBot, PerplexityBot and Amazonbot |
| medium.com | 5 of 7, with CCBot and Google-Extended allowed | Amazonbot |

The New York Times file also blocks every user fetcher the checker knows. Its search-agent blocks cover only AI assistant platforms, so Googlebot and Bingbot stay open.

Medium's file refuses training crawlers and keeps the AI assistants' search agents open, apart from Amazonbot. That is the split OpenAI and Anthropic document, with training and search as separate decisions.

## The robots.txt rule that reverses a casual reading

RFC 9309 says a crawler obeys the group that names its user agent, and falls back to the `*` group only "if no matching group exists." So a named group replaces the wildcard group for that crawler, and nothing in `*` carries over.

Here a site keeps every crawler out of `/admin/` and adds a GPTBot group to keep it out of drafts:

```text
User-agent: *
Disallow: /admin/

User-agent: GPTBot
Disallow: /drafts/
```

The checker reports GPTBot allowed at `/admin/`, because its own group has no rule for that path, and every other agent blocked there. Repeating `Disallow: /admin/` inside the GPTBot group closes it.

Within a group, the rule with the longest matching path wins, and RFC 9309 prefers an `Allow` over an equally long `Disallow`.

## The edge can block what robots.txt allows

RFC 9309 says "these rules are not a form of access authorization," and the gap runs both ways. My site's robots.txt is `User-agent: *` with `Allow: /`, yet on 2026-10-22 a request for that file with Python's urllib user agent got a Cloudflare 403:

```bash
curl -s -A "Python-urllib/3.12" -w "\nHTTP %{http_code}\n" https://ninadpathak.com/robots.txt
# error code: 1010
# HTTP 403
```

The same request with curl's own user agent, or a Googlebot one, returned the 88-byte file with HTTP 200. So a crawler that robots.txt allows can still be stopped at the CDN before it reads a page.

Server logs show whether an agent reached your pages. OpenAI publishes IP ranges for each agent, such as [gptbot.json](https://openai.com/gptbot.json) for GPTBot, and Anthropic publishes [bots.json](https://claude.com/crawling/bots.json), so you can confirm that a request claiming their user agent came from them.

OpenAI says search results can take about 24 hours to reflect a robots.txt change, and Perplexity says up to 24 hours. Check the logs after a day, not straight after the edit.

## A robots.txt for docs that want to be cited

For documentation, I'd allow every search agent and user fetcher, then decide on training separately. Here is a file that refuses the training agents and leaves everything else open:

```text
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: CCBot
User-agent: meta-externalagent
User-agent: Bytespider
Disallow: /

User-agent: *
Allow: /
```

Pasted into the [AI crawler checker](/ai-crawler-checker/), it reports "citation allowed, training opted out," with all 7 search agents allowed and all 7 training agents blocked at `/`. A docs team that wants its pages in model training too can keep a wildcard-only file like the docs hosts above.

Google-Extended isn't a training-only control, because Google says it also governs grounding in Gemini apps and in Grounding with Google Search on Vertex AI. Drop its line if you want Gemini to ground answers in your docs, and Google Search's AI features follow Googlebot either way.

Crawler access is the first of the [checks for AI search](/articles/aeo-for-developer-docs/), and it doesn't make a page quotable on its own. The [technical SEO checklist for documentation](/articles/docs-seo/) covers indexing, and an [llms.txt file](/articles/llms-txt/) is a separate, optional index that grants or blocks nothing.

## FAQ

### What is ClaudeBot?

ClaudeBot is Anthropic's crawler for collecting web content that may be used to train Claude models. Blocking it in robots.txt leaves Claude-SearchBot and Claude-User, the agents for search and user requests, unaffected.

### What is GPTBot?

GPTBot is OpenAI's crawler for content that may be used to train its foundation models. OpenAI says a GPTBot block is independent of OAI-SearchBot, which surfaces sites in ChatGPT search.

### Does blocking GPTBot remove a site from ChatGPT search?

No. ChatGPT search uses OAI-SearchBot, and OpenAI documents the two settings as independent, so block OAI-SearchBot only if you want out of ChatGPT search answers.

### Does Google-Extended affect AI Overviews?

No. Google says Google-Extended does not affect inclusion in Google Search, and its AI features page names Googlebot's robots.txt rules as the control for AI Overviews and AI Mode.
