---
category: ai-search-optimization
primary_query: none
siblings:
- llms-txt
- agents-reading-docs
- vercel-agent-study-by-harness
date: 2026-11-23
description: "The llms.txt link cut dead ends in Mintlify’s benchmark. Serving Markdown accounted for more of Claude Code’s savings than adding the link did."
slug: mintlify-llms-txt-benchmark
status: published
title: "What actually saved money in Mintlify’s llms.txt benchmark"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you check whether coding agents can find and fetch your docs. [Ask me about an audit](/services/ai-ready-documentation-audit/)."
---

Mintlify added a link to `llms.txt` and the agents in its docs benchmark hit far fewer 404s. When I worked through the reported costs, a different change accounted for more of Claude Code’s savings.

The same pages had been served as Markdown.

Mintlify published the individual runs, so I could see what each change bought. I could also see why I wouldn't read every 404 as an agent getting lost.

The benchmark's HTML setup deliberately returned 404 when agents asked for a Markdown page or the index. [Mintlify’s benchmark](https://mintlify.com/blog/llms-txt-agent-benchmark) · [Data and runner](https://github.com/mintlify/url-discovery-bench)

## Give the agent a question and a docs URL

For [AI search optimization](/articles/ai-search-optimization/), this experiment covers one step. The agent already knows where the docs are and has to find a page inside them.

Browserbase had told Mintlify that Claude Code kept hitting 404s. Mintlify's Markdown pages lacked the site navigation, leaving the agent to guess URLs.

Mintlify put an index link at the top of those pages and tested whether that helped the agent find the one page it needed.

In the benchmark, every run started with the docs site and a question. Claude Code on Sonnet 5 and Codex on GPT-5.5 used curl to explore.

A proxy served the same 20 sites as HTML, plain Markdown, Markdown with the index linked, or Markdown with the whole index pasted up top.

The grader looked at the URL the agent returned. A pass means it found an accepted page.

The test ended before the agent had to answer the question or use a code sample.

## Read the bill next to the 404 count

The table came from the published runs at commit `5f055a8`. Only Claude Code reported a cost.

| Format | 404s per task | Runs graded wrong, of 600 | Claude Code's reported cost per run (cents) |
|---|---|---|---|
| HTML | 2.23 | 19 | 19.4 |
| Markdown, no pointer | 1.42 | 29 | 15.8 |
| Markdown with the link | 0.13 | 15 | 13.8 |
| Markdown with llms.txt inlined | 0.10 | 5 | 17.1 |

Plain Markdown brought the bill to 15.8 cents from 19.4. Adding a link brought it down another two cents.

Pasting the whole index into each page cut the wrong answers further, and it raised the bill compared with keeping the link.

I wouldn't put much weight on the difference between 19 wrong HTML runs and 15 wrong runs with the link. On a question-by-question count HTML did worse on six and better on five.

The comparison I'd use is the one closest to the original problem. Markdown with no navigation produced 29 wrong runs, and both ways of adding the index brought that count down.

To repeat the calculation, use `data/full/results.jsonl` from the benchmark repository.

```python
import json

rows = [json.loads(line) for line in open("data/full/results.jsonl")]
for arm in ("html", "md", "md-link", "md-inline"):
    runs = [r for r in rows if r["arm"] == arm and not r.get("error")]
    dead = sum(r["notFound"] for r in runs)
    wrong = sum(not r["correct"] for r in runs)
    cost = [r["costUsd"] for r in runs if r["agent"] == "claude"]
    print(f"{arm:10}{dead / len(runs):6.2f}{wrong:4}{sum(cost) / len(cost):7.3f}")
```

## What the agent was asking for when it hit a 404

[Fern’s traffic logs](/articles/agents-reading-docs/) also show agents fetching the index. The Mintlify runs add cases where the agent had no link to follow.

The HTML condition was set up to return 404 for every `.md` URL and for `/llms.txt`. Mintlify attributes 93% of the misses in that condition to those requests.

Its proxy logs weren't in the repository when I checked, so that breakdown is Mintlify’s. The counts in the table are reproducible from the run results.

Once Mintlify counts only wrong guesses at page paths, Claude Code goes to 0.10 per task with the link from 0.12 on HTML. Plain Markdown without the link was the rougher starting point at 0.46.

I’d use this result to fix Markdown pages that have lost their navigation.

The HTML runs tell me something else. The pages gave the agents no link to `llms.txt`, and Mintlify’s count implies about 450 requests for it anyway.

I used to say the evidence that models fetch it was thin. For coding agents, I'd change that line.

For answer engines, I still want a dataset that includes them. [My llms.txt guide](/articles/llms-txt/) · [Vercel’s agent traces](/articles/vercel-agent-study-by-harness/)

## What I'd measure on another site

In Claude Code's HTML runs, each additional 404 came with about 2.8 cents and nine seconds more on attempts at the same question. The rejected response was only nine bytes.

A run with another 404 took 1.4 more turns, so the agent spent time trying again. I'd treat the price as an association because harder attempts can also take more turns for other reasons.

All 20 sites were hosted by Mintlify, which generates and updates the index. I tried a working Markdown URL and a made-up one on Mintlify's own docs.

Both responses included the link back to the index.

```bash
curl -s https://www.mintlify.com/docs/ai/llmstxt.md | head -3
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://www.mintlify.com/docs/ai/llms-text.md
```

```text
> ## Documentation Index
> Fetch the complete documentation index at: https://www.mintlify.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.
404 529
```

If my Markdown pages already stripped the navigation, I'd add a link to the index and try the same lookup with and without it. I'd record whether the agent found the right page, how long it took, and what it cost.

If I cared whether the example solved the developer's problem, I'd give the agent that task separately and test what it built.
