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
description: "Every recorded Markdown request in Vercel’s agent study came from one fetch tool. The stronger finding was what happened when agents couldn’t read the HTML."
slug: vercel-agent-study-by-harness
status: published
title: "Which agents asked for Markdown in Vercel’s study?"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you test whether AI agents can read your docs. [Ask me about an audit](/services/ai-ready-documentation-audit/)."
---

Vercel and Ora reported that agents asked for Markdown on 65.1% of the fetches they counted. When I grouped their data by the software that ran the model, every recorded request for Markdown came from one framework.

I'd still follow their advice to get the HTML working first. In a separate test, they put an answer on a page and changed how it was served.

That showed what could stop an agent from getting to the text at all. [Vercel and Ora’s guide](https://vercel.com/kb/guide/make-your-site-readable-by-ai-agents) · [Trace data](https://github.com/agentready-org/standard/tree/main/data)

## What stopped the fetch from working?

For [AI search optimization](/articles/ai-search-optimization/), the first question is whether the agent can get to the text at all. [Fern’s agent traffic logs](/articles/agents-reading-docs/) can show a fetch.

The experiment here can show whether the fetched page contains the answer.

Ora served the same documentation site in 19 configurations. It planted an answer on a page and checked whether two fetch clients could retrieve it.

The plain server-rendered page passed.

The clients couldn't get the answer when the server returned 403 to their user agents. The client that didn't run JavaScript also failed when the answer was only in JavaScript.

A Markdown copy might help on another test, but this one already passed with HTML that contained the answer.

On a site I was checking, I'd start with the guide’s curl command. I'd look for a 200 response with the answer in the HTML.

```bash
curl -iL -A 'Claude-User/1.0' https://example.com/your-page
```

A request from my machine can only show what the server returned to my machine. To find out whether a real agent got blocked, I'd check the server logs.

## Which model actually asked for Markdown?

If a real agent is blocked at the server, the [crawler guide](/articles/ai-crawlers/) shows where I'd look before changing how I serve the pages.

<!-- evidence-three: The trace CSV sums to 3,470 web fetches and 2,259 Markdown requests. -->
The CSV records 2,259 Markdown requests across 3,470 web fetches. They all came through eve, Vercel's framework.

The difference inside eve is as interesting as the difference between frameworks.

| Harness | Model | Runs | Web fetches | Fetches that asked for Markdown |
|---|---|---|---|---|
| eve | `gpt-5.4` | 236 | 1,087 | 1,049 |
| eve | `claude-haiku-4-5` | 142 | 1,401 | 1,190 |
| eve | `claude-fable-5` | 114 | 465 | 20 |
| Claude Agent SDK | `claude-sonnet-4-6` | 236 | 517 | 0 |
| Claude Agent SDK | `claude-haiku-4-5` | 185 | 0 | 0 |
| Claude Agent SDK | `claude-fable-5` | 120 | 0 | 0 |

Fable 5 asked for Markdown on just 20 of 465 eve fetches. Haiku 4.5 did so on 1,190 of 1,401 through the same tool.

I wouldn't expect the format preference of one model to carry over to another.

There's another limit in the data. The Claude Agent SDK showed zero counted web fetches on 373 runs, and 265 of those runs still reached a docs page.

Some way of reading pages is missing from the web-fetch count. The CSV also can't tell us whether the request for Markdown reached the server or was handled inside eve.

For a Markdown mirror I'd want a test that measures how much time or money it saves. [Mintlify’s benchmark](/articles/mintlify-llms-txt-benchmark/) gives an example using the same pages in HTML and Markdown.

To reproduce this breakdown, run the script on `traces.csv` at commit `a6b0976`.

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

## How did agents find the index?

Agents fetched `llms.txt` on six of the 15 sites that had one. Vercel and Ora say a link led the agent there in 356 of 416 fetches.

The rest came from guessing the path.

I checked those six homepages on November 23 to see which linked the file.

| Site | Runs | Runs that reached llms.txt | Homepage links llms.txt on November 23 |
|---|---|---|---|
| ora.ai | 119 | 81 | Yes |
| telnyx.com | 122 | 76 | Yes |
| attio.com | 122 | 71 | Yes |
| zapier.com | 124 | 62 | Yes |
| monday.com | 124 | 21 | No |
| stripe.com | 80 | 18 | No |

The sites with a homepage link saw the index in 290 of 487 runs. The other two saw it in 39 of 204.

I checked the homepages months after the runs, so I can't tell which links the agents saw. Twilio had a footer link when I checked and none of its 18 runs had fetched the file.

I'd still link the index so an agent starting at the homepage has a route to it. I'd read the descriptions in it as if they were part of the docs.

The study traced 120 of 844 answers to wording from the index itself.

## What people get back from those fetches

In 73 of the 119 runs where an answer included code, the agent copied code from a fetched page. The developer might never open that page.

That's where I'd spend time before building a Markdown mirror. Run the examples, starting with the ones someone could paste into a new project.

[Testing an API reference against a running service](/articles/api-documentation/)
