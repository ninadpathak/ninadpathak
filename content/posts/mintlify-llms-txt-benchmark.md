---
category: ai-search-optimization
primary_query: none
siblings:
- llms-txt
- agents-reading-docs
- vercel-agent-study-by-harness
date: 2026-11-23
description: "Mintlify ran 2,400 agent lookups on 20 docs sites and published the rows. I regenerated its tables. The llms.txt link removes the 404s, a 404 cost Claude Code about 2.8 cents, and serving Markdown saved more of the bill than the link did."
slug: mintlify-llms-txt-benchmark
status: published
title: "Recomputing Mintlify's llms.txt benchmark from its published runs"
work_note: "A valid llms.txt can still sit where no agent finds it. I'm Ninad Pathak, a freelance technical writer, and my AI-ready documentation audit validates the file and tests whether AI crawlers may fetch your docs, with tools I built and published so you can rerun every finding. [Get in touch about an audit](/services/ai-ready-documentation-audit/)."
---

The CEO of Browserbase told Mintlify in November 2025 that Claude Code kept hitting 404s on Mintlify-hosted docs, Mintlify's own included. Mintlify's account of the cause, in [a post by Aadit Shah](https://mintlify.com/blog/llms-txt-agent-benchmark) from July 17, 2026, is that the Markdown version of each page had dropped the site navigation, so the agent guessed at URLs.

Mintlify's fix was a link to llms.txt on every Markdown page. The post tests that fix with 2,400 agent runs on 20 docs sites, where the average number of 404s per task fell from 2.23 on HTML to 0.11 with llms.txt linked or inlined.

The [benchmark repository](https://github.com/mintlify/url-discovery-bench) holds a row for each run, so I regenerated its tables and then worked out what one 404 cost and where the saving came from. Whether a link to llms.txt helps an agent that's already on your docs is one question inside [AI search optimization](/articles/ai-search-optimization/) for documentation.

My line in the [llms.txt guide](/articles/llms-txt/) has been that the file is good to have and that the evidence that models fetch it is thin, so I also read the rows for what they say about fetching.

## The benchmark tests a link the agent has already seen

I read the benchmark as a test of a link, because every run starts with the agent already on the docs site. The prompt in `run.py` gives the agent the docs URL and a question, and asks it to explore with curl and return the URL of the page that answers it.

<!-- evidence-three: the benchmark's README gives the design as 20 sites × 5 questions × 4 arms × 2 agents × 3 attempts = 2,400 attempts --> Claude Code on Sonnet 5 and Codex on GPT-5.5 each took 100 questions three times in each format, through a local proxy that served the same pages in four formats:

- `html`: HTML pages, with every `.md` path and `/llms.txt` answered 404.
- `md`: Markdown pages with the llms.txt pointer stripped out and `/llms.txt` answered 404.
- `md-link`: Markdown pages that carry the pointer.
- `md-inline`: Markdown pages with the whole llms.txt pasted above the content.

The grader in `grade.py` marks a run correct when the path of the URL the agent returned matches an accepted path for the question. So accuracy here means the agent found the page, and no run was graded on an answer or on code.

## The published rows reproduce the post's figures

The post's figures regenerate from the repository. I cloned it at commit `5f055a8` on November 23 and ran the README's five Tier 0 commands, and four printed figures that match [`RESULTS.md`](https://github.com/mintlify/url-discovery-bench/blob/main/RESULTS.md).

The command that splits the 404s by cause exited with `no log files in data/full/logs`. `RESULTS.md` says the proxy logs are committed and no branch of the repository has them, so the split by cause in the next section is Mintlify's count, unchecked.

I rebuilt the 2,400 runs by format with this script, on Python 3.12.3:

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

| Format | 404s per task | Runs graded wrong, of 600 | Claude Code's reported cost per run (cents) |
|---|---|---|---|
| HTML | 2.23 | 19 | 19.4 |
| Markdown, no pointer | 1.42 | 29 | 15.8 |
| Markdown with the link | 0.13 | 15 | 13.8 |
| Markdown with llms.txt inlined | 0.10 | 5 | 17.1 |

The cost column covers Claude Code alone, because Codex reported no cost.

I agree with the post that accuracy doesn't separate HTML from the link. HTML runs were graded wrong 19 times in 600 and linked runs 15 times, and counted by question, HTML did worse than the link on 6 questions and better on 5.

Against Markdown with no pointer the two llms.txt formats did better, at 15 and 5 wrong runs against 29. So on a small count, llms.txt did make agents more right than the format Mintlify had been serving.

## On HTML the proxy refuses the two files agents ask for

By Mintlify's count, 93% of the 404s in the HTML runs were requests the proxy was built to refuse. `RESULTS.md` puts 59% down to `.md` requests for pages that exist and 34% to requests for `/llms.txt`, which leaves 7% as wrong guesses.

So I wouldn't read 2.23 as agents getting lost in HTML. Counting only wrong guesses, `RESULTS.md` gives Claude Code 0.12 per task on HTML and 0.10 with the link, and Codex 0.20 and 0.15.

Agents did get lost on Markdown with no pointer, where Claude Code made 0.46 wrong guesses per task and Codex made 1.15. Markdown with no navigation is what Mintlify served before its fix, so the benchmark is strong evidence that the link repairs Mintlify's own Markdown export and weaker evidence about a site that only serves HTML.

Nothing in the HTML runs pointed at llms.txt, and 34% of their 1,336 dead requests works out to roughly 450 requests for the file across 600 runs. [Fern's logs](/articles/agents-reading-docs/) and [Vercel's traces](/articles/vercel-agent-study-by-harness/) had already shown coding agents fetching the file, and here Claude Code and Codex guessed its path with no link to follow.

I wrote that the evidence of models fetching llms.txt was thin, and for coding agents I'd stop saying that. The benchmark has no answer engine such as ChatGPT in it, so for answer engines my line stands.

## What a 404 cost in these runs

Each extra 404 cost Claude Code about 2.8 cents and 9 seconds on HTML. I got that by fitting a line to how Claude Code's reported cost rose with each extra 404 across its HTML attempts at the same question.

The proxy's reply to a refused request is the nine-byte body `Not Found`, so the 404 itself adds almost nothing to read. An attempt with one more 404 took 1.4 more turns, and each turn sends the conversation so far back to the model.

An attempt with more 404s also took more turns for reasons the fit can't separate from the 404s, so I'd treat 2.8 cents as a rough price.

The bill is also where I part with the post's claim that "markdown itself wasn't the fix, the map was". Going by the cost column above, 3.6 of the 5.6 cents Claude Code saved per run between HTML and linked Markdown arrived with Markdown alone, before any llms.txt.

Codex's input tokens per run fell by 129,000 from HTML to Markdown with no pointer, and by another 41,000 with the link.

Adam Altman of Redocly, which also sells a docs platform, [wrote on September 9](https://redocly.com/blog/llms-txt-still-overhyped) that Redocly's logs show the Markdown copies of pages read many times more often than the llms.txt that links to them. Both vendors can be right, because the link removes the 404s and the Markdown removes more of the tokens.

## Every site in the sample is hosted by Mintlify

The README describes all 20 sites as Mintlify docs sites, and [Mintlify's docs](https://www.mintlify.com/docs/ai/llmstxt) say it generates a site's llms.txt from the site's pages and keeps it up to date. So the benchmark never meets an llms.txt that somebody wrote by hand and stopped updating, and a link to a stale index could send an agent to pages that no longer exist.

Mintlify hosts docs for a living, and the post ends by telling readers that a new Mintlify site gets llms.txt and Markdown routes automatically. It also published its harness and every row, the 272 failed attempts included, which is why I could check any of this.

On November 23 I checked what a Mintlify page serves today, with curl 8.5.0:

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

<!-- evidence-three: the 529-byte body ends with a Related topics list of three links --> The pointer opens the page, and the made-up path `llms-text.md` returned a 529-byte Markdown 404 that repeats the pointer and lists three related pages. The same path without `.md` returned a 171,185-byte HTML 404.

## What I'd change on a docs site

I'd serve the two things agents asked for unprompted, a Markdown copy of each page at its URL plus `.md` and an index at `/llms.txt`. If the docs already serve Markdown, I'd put the pointer to llms.txt in the first lines of every Markdown page and return a short Markdown 404 that repeats it.

The two curl commands above show what an agent gets from your own docs, and the [llms.txt validator](/llms-txt-validator/) checks the file the pointer leads to.

I'd report the result as cents and seconds per lookup, which is what the benchmark measured. Its runs stop at a URL, so none of the 6,000 runs across five models says whether an agent that found the right page went on to write working code.
