---
category: ai-search-optimization
primary_query: none
siblings:
- agents-reading-docs
- mintlify-llms-txt-benchmark
- ai-crawlers
bridges:
- slug: api-documentation
  reason: An agent copies code from the page it fetched, so the reference entry it copies from has to be checked against the service.
date: 2026-11-23
description: "Vercel and Ora traced 1,033 agent runs and published the rows. I recomputed the figures and split them by harness. The advice to fix the HTML first holds, and all 2,259 Markdown requests came from one harness, Vercel's own eve."
slug: vercel-agent-study-by-harness
status: published
title: "Splitting Vercel's agent study by harness and model"
work_note: "Whether an AI crawler can fetch your docs, and whether the answer is on the page it gets back, is what I test first in an AI-ready documentation audit. I'm Ninad Pathak, a freelance technical writer, and I built and published the tools the audit runs on, so you can rerun every finding. [Ask me about an audit](/services/ai-ready-documentation-audit/)."
---

My essay on [Fern's agent traffic report](/articles/agents-reading-docs/) ended on the point that no traffic log shows whether the code an agent wrote after reading a page worked. On August 28, Vercel and the research lab Ora published [Make your site readable by AI agents](https://vercel.com/kb/guide/make-your-site-readable-by-ai-agents), a guide built on 1,033 traced agent runs across 25 product sites, where each run is followed from its first fetch to the page its final answer took its wording from.

The guide links [its data](https://github.com/agentready-org/standard/tree/main/data), a CSV with one row per run, so I recomputed its figures and then split them by harness and by model. Its main advice survived the split, and its Markdown figure turned out to describe one of the study's two harnesses.

What an agent does after it fetches a page is one part of [AI search optimization](/articles/ai-search-optimization/) for documentation.

## The advice to fix the HTML first holds up

I'd follow the guide's central instruction as written: "Make the HTML work before adding a Markdown mirror." The instruction rests on a controlled experiment, in which Ora served one documentation site under 19 configurations and tested whether two fetch clients could retrieve an answer planted on each page.

The answer became unreachable under three of the 19 configurations: one page kept its answer inside a JavaScript payload and failed for the client that doesn't run JavaScript, and two configurations returned 403 to agent user agents and failed for both clients.

The 16 other configurations passed, including the plain server-rendered baseline with nothing added. That baseline is the limit of the experiment, because a page that already passes can't pass harder, so the test can show that llms.txt or a Markdown mirror isn't required and can't show whether either one helps.

The trace data points the same way as the experiment. I recomputed the guide's counts from the CSV, and agents reached a docs page in 855 of the 1,033 runs, while 394 of the 844 answers that Ora could trace to a fetched page traced to a docs page.

Vercel hosts websites, and Ora runs the is-agentic.com scanner that the guide's last section sends you to, so both gain when a reader acts on the advice. They also published every row, and the rest of this essay exists because they did.

## Every Markdown request came from one harness

<!-- evidence-three: the web_fetch_calls column of the study's trace CSV sums to 3,470 and its markdown_calls column to 2,259, which is 65.1% --> All 2,259 Markdown requests in the study came from eve, one of its two harnesses, and eve is [Vercel's own open-source agent framework](https://vercel.com/eve). The guide reports those requests as 65.1% of 3,470 web fetches, under a heading that does say "in the study harnesses".

Here is the same figure split by harness and model, using the model names as the CSV writes them:

| Harness | Model | Runs | Web fetches | Fetches that asked for Markdown |
|---|---|---|---|---|
| eve | `gpt-5.4` | 236 | 1,087 | 1,049 |
| eve | `claude-haiku-4-5` | 142 | 1,401 | 1,190 |
| eve | `claude-fable-5` | 114 | 465 | 20 |
| Claude Agent SDK | `claude-sonnet-4-6` | 236 | 517 | 0 |
| Claude Agent SDK | `claude-haiku-4-5` | 185 | 0 | 0 |
| Claude Agent SDK | `claude-fable-5` | 120 | 0 | 0 |

You can rebuild the table from `traces.csv` at commit `a6b0976` of the data repository with this script:

```python
import csv
from collections import defaultdict

totals = defaultdict(lambda: [0, 0, 0])
for row in csv.DictReader(open("traces.csv")):
    pair = totals[(row["harness"], row["model"])]
    pair[0] += 1
    pair[1] += int(row["web_fetch_calls"])
    pair[2] += int(row["markdown_calls"])

for (harness, model), (runs, fetches, markdown) in sorted(totals.items()):
    print(f"{harness:17}{model:19}{runs:5}{fetches:7}{markdown:7}")
```

So inside eve the habit belongs to two models. `gpt-5.4` asked for Markdown on 1,049 of its 1,087 fetches and `claude-haiku-4-5` on 1,190 of its 1,401, while `claude-fable-5` asked on 20 of 465 through the same harness.

The Claude Agent SDK runs can't confirm or contradict that habit, because the CSV records zero web fetches for 373 of the harness's 541 runs. Agents in 265 of those 373 runs still reached a docs page, so the Agent SDK runs read pages through some tool that the web-fetch column doesn't count.

I read 65.1% as a fact about one fetch tool that accepts a format and two models that like to set it. The data also doesn't say whether a Markdown request reached the site as an `Accept: text/markdown` header or was converted inside the harness, and only the header would ask a server for a mirror.

So I wouldn't write "two thirds of agents want Markdown" in a planning doc, and I wouldn't build a Markdown mirror on this number.

The number I'd build one on is a cost. In [Mintlify's llms.txt benchmark](/articles/mintlify-llms-txt-benchmark/), Claude Code's reported cost per lookup was 19.4 cents on HTML pages and 15.8 cents on Markdown copies of the same pages.

## Agents fetched llms.txt on six of fifteen sites that ship one

Every one of the 329 runs that reached an llms.txt happened on the six sites with the largest run counts. The sample has nine more sites that publish the file, Twilio and Notion among them, and none of their 162 runs fetched it.

The models don't explain those nine zeros. The 162 runs used `gpt-5.4` on eve and `claude-sonnet-4-6` on the Claude Agent SDK, and on the six larger sites those same two pairings reached llms.txt in 72 of 130 runs.

A link might explain them. The guide found that agents arrived at llms.txt through a link in 356 of 416 fetches and guessed the path in the other 60, so on November 23 I fetched the six homepages with curl and searched the HTML for the file name:

| Site | Runs | Runs that reached llms.txt | Homepage links llms.txt on November 23 |
|---|---|---|---|
| ora.ai | 119 | 81 | Yes |
| telnyx.com | 122 | 76 | Yes |
| attio.com | 122 | 71 | Yes |
| zapier.com | 124 | 62 | Yes |
| monday.com | 124 | 21 | No |
| stripe.com | 80 | 18 | No |

On the four sites whose homepage links the file, agents reached llms.txt in 290 of 487 runs, and on the two that don't link it they reached the file in 39 of 204. That compares today's homepages with runs from June to August, and Twilio's footer links the file today while none of its 18 runs fetched it, so I'd call the pattern a hint.

My view of llms.txt was that the file is good to have and that the evidence that models fetch it is thin. Fern's logs were one dataset where coding agents fetched the file, and these traces are a second, so I'd now add an instruction: link llms.txt from the homepage, in the `head` or the footer, where an agent that starts at the homepage will see it.

The notes inside the file matter as well, because 120 of the 844 traced answers took their wording from llms.txt itself. A one-line description beside a link in that file can become the agent's answer, so each description has to be as accurate as the page it points to.

## Agents paste the code they find

Agents copied code straight from the pages they fetched in 73 of the 119 runs whose answer included code. A sample of 119 runs is small, and I'd still plan around it, because a wrong code sample now reaches a developer's project through an agent, and the developer may never open the page it came from.

So I'd spend a week running every code sample in the docs before I'd spend it on a Markdown mirror. The [API documentation guide](/articles/api-documentation/) shows one way to do that, with a script that checks a reference entry against the running service.

## What I'd check on a docs site first

Start with the guide's own command, which requests a page under `Claude-User`, the user agent Anthropic uses when a person asks Claude to fetch a page:

```bash
curl -iL -A 'Claude-User/1.0' https://example.com/your-page
```

The request passes if it ends in a 200 and the answer is in the returned HTML, and a 403 or an empty app shell fails it.

The guide warns that this request can't confirm whether a real agent is blocked, since bot blockers judge where a request comes from. Your server logs, filtered to the IP ranges OpenAI and Anthropic publish, are the stronger check.

The [AI crawlers guide](/articles/ai-crawlers/) covers the robots.txt side of access, and the [AI crawler access checker](/ai-crawler-checker/) tests a robots.txt against the agents it names.

Borrow the study's percentages with care, because six sites supply 691 of the 1,033 runs and Ora's own site is one of the six. Dropping ora.ai's 119 runs leaves docs reach at 763 of 914, which is 83.5%, so the lab's own site doesn't move the headline figure.

The runs were product tasks, which the data README lists as finding the pricing, looking up the rate limits and integrating the API. A docs site with no pricing page and no public API isn't in this sample, and I wouldn't assume its agents behave the same way.
