# Attribution

Appended by `tools/gsc_attribution.py`. Every page shipped or substantially
rewritten recently, and every tool, measured from its own publish date rather
than sitewide — which is the only way to see which lever works while the
sitewide numbers are zero.

`no data yet` means younger than the Search Console lag. `not yet, Nd` means N
observable days and still nothing, which is a real measurement. Neither is
written as a zero. Human figures come from the three-dimension pull and are a
hard floor: it keeps about a fifth of sitewide impressions.

## 2026-08-17 — attribution since 2026-08-14

Search Console data through 2026-08-14 (3-day lag). Days are counted from each page's own ship date, or from its last substantial rewrite where there was one.

`no data yet` means the page is younger than the lag, so silence proves nothing. `not yet, Nd` means N observable days with no impression, which **is** a measurement. Neither is written as a zero, because a zero would read as "it happened immediately".


### Tools

Every tool, whatever its age, because the calendar weighting rests on them.

| Page | Cluster | Shipped | Obs. days | 1st impr | 1st human impr | 1st human click | Impr | Human impr |
|---|---|---|---:|---|---|---|---:|---:|
| /linter/ | 4 | 2026-03-14 *(rewritten)* | 153 | 65d | not yet, 153d | not yet, 153d | 9 | 0 |
| /llms-txt-generator/ | 4 | 2026-07-31 | 14 | not yet, 14d | not yet, 14d | not yet, 14d | 0 | 0 |
| /llms-txt-validator/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| /ai-overviews-checker/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| /ai-crawler-checker/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |

### Articles shipped since tracking began

These are the like-for-like comparison against the tools.

| Page | Cluster | Shipped | Obs. days | 1st impr | 1st human impr | 1st human click | Impr | Human impr |
|---|---|---|---:|---|---|---|---:|---:|
| API Documentation Best Practices: Reference, | 1 | 2026-08-14 | 0 | not yet, 0d | not yet, 0d | not yet, 0d | 0 | 0 |
| API Documentation Examples: What the Best De | 1 | 2026-08-15 | — | no data yet | no data yet | no data yet | 0 | 0 |
| API Documentation Tools: A Workflow Comparis | 1 | 2026-08-16 *(rewritten)* | — | no data yet | no data yet | no data yet | 0 | 0 |
| AI Crawlers in robots.txt: Training, Citatio | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| API Documentation Template: The Pages Every  | 1 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| llms.txt Examples: Four Public Files Audited | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| What Makes a Page Extractable by an Answer E | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |

### Pre-existing articles, rewritten but not newly shipped

66 article(s) shipped before 2026-08-14 and are excluded from the comparison: 66 were substantially rewritten in this window and 0 carry impressions predating their current source file, because the AI cluster was recovered from 404 and its URLs ranked long before the files were restored. Days-to-first-impression is meaningless for both. The ten largest by impressions:

| Page | Cluster | Impr | Human impr | 1st impr vs ship |
|---|---|---:|---:|---|
| How Anthropic's Contextual Retrieval Changes | 3 | 2420 | 3 | 61d |
| Context Engineering as Heap Management: Accu | 3 | 144 | 0 | 67d |
| How Memory Works in Claude Code | 3 | 138 | 14 | 35d |
| Vector Embeddings: a Guide to the Geometry o | 3 | 120 | 0 | 92d |
| Shared Memory vs Isolated Memory in Multi-Ag | 3 | 120 | 1 | 12d |
| How Stripe's Technical Blog Became a Competi | 2 | 116 | 21 | 72d |
| Prompt Caching: What It Is and When the Math | 3 | 111 | 102 | 7d |
| Fine-Tuning vs RAG for Agent Memory: When Ea | 3 | 87 | 2 | 46d |
| Vector Search in the Browser: PGlite vs. SQL | 3 | 86 | 0 | 72d |
| Multi-Agent vs Single-Agent Systems: The Rea | 3 | 80 | 35 | 31d |

### What the pages with real age already show

Only pages observable for 30+ days. The like-for-like comparison below will stay unanswerable for weeks, but this evidence exists now and it is the only evidence about tools there is.

| | Pages | Reached an impression | Median days to first | Median impr | Total impr | Total human impr | Pages with any human impr |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tools | 1 | 1 | 65 | 9 | 9 | 0 | 0 |
| Articles | 65 | 59 | 67 | 19 | 4658 | 320 | 26 |

Aged tools individually:

- `/linter/` — 153d live, 65d to first impression, 9 impressions, 0 human

**The aged evidence does not support the tools bet, and it is the only evidence there is.** Time to a first impression is indistinguishable from articles — median 65d against 67d, which on 1 tool(s) is not a difference. On volume the gap is not close: 1 aged tool(s) hold 9 impressions and 0 human, against 4658 and 320 across 65 aged article(s). 0 of the tools have earned a single human impression, against 26 of the articles. Two caveats that matter before anyone reweights the calendar. The sample is 1 tool(s), which is not a basis for a decision on sixty rows. And the aged tool is `/linter/`, a documentation linter that predates the AI-search cluster — the four tools the bet actually rests on are days old. This is a reason to wait for those four rather than a reason to abandon the bet, and it is equally not a reason to add more tool rows before they report.


### The bet: do tools reach search sooner than articles?

Newly shipped pages only. A pre-existing page carries history that says nothing about how fast a new publish reaches search, and a recovered URL carries impressions older than its own source file.

| | Tracked | Eligible | Observable | Reached an impression | Median days | Impressions | Human impr | Clicks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Tools | 5 | 3 | 0 | 0 | n/a | 0 | 0 | 0 |
| Articles | 73 | 7 | 1 | 0 | n/a | 0 | 0 | 0 |

Excluded from the comparison: tools 2 pre-existing / 0 recovered, articles 66 pre-existing / 0 recovered.

**Not answerable yet, and that is now a measurement rather than a wait.** 0 tool(s) and 1 article(s) have been observable and neither side has earned a single impression. No lever is working yet; the question of which works better cannot be opened until one of them does.

**What this cannot test.** The tools bet rests on no build-a-tool keyword carrying an AI Overview while all 15 top niche keywords do. That is a claim about other people's SERPs, taken from Ahrefs. **Search Console has no AI Overview dimension**, so there is no first-party way to confirm an AI Overview appeared above one of our own results, and Ahrefs is unavailable. The measurable consequence is impression-to-click conversion at comparable positions, which needs clicks; the site has none, so that column is empty rather than filled with zeros.

## 2026-08-17 — attribution since 2026-08-14

Search Console data through 2026-08-14 (3-day lag). Days are counted from each page's own ship date, or from its last substantial rewrite where there was one.

`no data yet` means the page is younger than the lag, so silence proves nothing. `not yet, Nd` means N observable days with no impression, which **is** a measurement. Neither is written as a zero, because a zero would read as "it happened immediately".


### Tools

Every tool, whatever its age, because the calendar weighting rests on them.

| Page | Cluster | Shipped | Obs. days | 1st impr | 1st human impr | 1st human click | Impr | Human impr |
|---|---|---|---:|---|---|---|---:|---:|
| /linter/ | 4 | 2026-03-14 *(rewritten)* | 153 | 65d | not yet, 153d | not yet, 153d | 9 | 0 |
| /llms-txt-generator/ | 4 | 2026-07-31 | 14 | not yet, 14d | not yet, 14d | not yet, 14d | 0 | 0 |
| /llms-txt-validator/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| /ai-overviews-checker/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| /ai-crawler-checker/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |

### Articles shipped since tracking began

These are the like-for-like comparison against the tools.

| Page | Cluster | Shipped | Obs. days | 1st impr | 1st human impr | 1st human click | Impr | Human impr |
|---|---|---|---:|---|---|---|---:|---:|
| API Documentation Best Practices: Reference, | 1 | 2026-08-14 | 0 | not yet, 0d | not yet, 0d | not yet, 0d | 0 | 0 |
| API Documentation Examples: What the Best De | 1 | 2026-08-15 | — | no data yet | no data yet | no data yet | 0 | 0 |
| API Documentation Tools: A Workflow Comparis | 1 | 2026-08-16 *(rewritten)* | — | no data yet | no data yet | no data yet | 0 | 0 |
| AI Crawlers in robots.txt: Training, Citatio | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| API Documentation Template: The Pages Every  | 1 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| llms.txt Examples: Four Public Files Audited | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| What Makes a Page Extractable by an Answer E | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |

### Pre-existing articles, rewritten but not newly shipped

66 article(s) shipped before 2026-08-14 and are excluded from the comparison: 66 were substantially rewritten in this window and 0 carry impressions predating their current source file, because the AI cluster was recovered from 404 and its URLs ranked long before the files were restored. Days-to-first-impression is meaningless for both. The ten largest by impressions:

| Page | Cluster | Impr | Human impr | 1st impr vs ship |
|---|---|---:|---:|---|
| How Anthropic's Contextual Retrieval Changes | 3 | 2420 | 3 | 61d |
| Context Engineering as Heap Management: Accu | 3 | 144 | 0 | 67d |
| How Memory Works in Claude Code | 3 | 138 | 14 | 35d |
| Vector Embeddings: a Guide to the Geometry o | 3 | 120 | 0 | 92d |
| Shared Memory vs Isolated Memory in Multi-Ag | 3 | 120 | 1 | 12d |
| How Stripe's Technical Blog Became a Competi | 2 | 116 | 21 | 72d |
| Prompt Caching: What It Is and When the Math | 3 | 111 | 102 | 7d |
| Fine-Tuning vs RAG for Agent Memory: When Ea | 3 | 87 | 2 | 46d |
| Vector Search in the Browser: PGlite vs. SQL | 3 | 86 | 0 | 72d |
| Multi-Agent vs Single-Agent Systems: The Rea | 3 | 80 | 35 | 31d |

### What the pages with real age already show

Only pages observable for 30+ days. The like-for-like comparison below will stay unanswerable for weeks, but this evidence exists now and it is the only evidence about tools there is.

| | Pages | Reached an impression | Median days to first | Median impr | Total impr | Total human impr | Pages with any human impr |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tools | 1 | 1 | 65 | 9 | 9 | 0 | 0 |
| Articles | 65 | 59 | 67 | 19 | 4658 | 320 | 26 |

Aged tools individually:

- `/linter/` — 153d live, 65d to first impression, 9 impressions, 0 human

**The aged evidence does not support the tools bet, and it is the only evidence there is.** Time to a first impression is indistinguishable from articles — median 65d against 67d, which on 1 tool(s) is not a difference. On volume the gap is not close: 1 aged tool(s) hold 9 impressions and 0 human, against 4658 and 320 across 65 aged article(s). 0 of the tools have earned a single human impression, against 26 of the articles. Two caveats that matter before anyone reweights the calendar. The sample is 1 tool(s), which is not a basis for a decision on sixty rows. And the aged tool is `/linter/`, a documentation linter that predates the AI-search cluster — the four tools the bet actually rests on are days old. This is a reason to wait for those four rather than a reason to abandon the bet, and it is equally not a reason to add more tool rows before they report.


### The bet: do tools reach search sooner than articles?

Newly shipped pages only. A pre-existing page carries history that says nothing about how fast a new publish reaches search, and a recovered URL carries impressions older than its own source file.

| | Tracked | Eligible | Observable | Reached an impression | Median days | Impressions | Human impr | Clicks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Tools | 5 | 3 | 0 | 0 | n/a | 0 | 0 | 0 |
| Articles | 73 | 7 | 1 | 0 | n/a | 0 | 0 | 0 |

Excluded from the comparison: tools 2 pre-existing / 0 recovered, articles 66 pre-existing / 0 recovered.

**Not answerable yet, and that is now a measurement rather than a wait.** 0 tool(s) and 1 article(s) have been observable and neither side has earned a single impression. No lever is working yet; the question of which works better cannot be opened until one of them does.

**What this cannot test.** The tools bet rests on no build-a-tool keyword carrying an AI Overview while all 15 top niche keywords do. That is a claim about other people's SERPs, taken from Ahrefs. **Search Console has no AI Overview dimension**, so there is no first-party way to confirm an AI Overview appeared above one of our own results, and Ahrefs is unavailable. The measurable consequence is impression-to-click conversion at comparable positions, which needs clicks; the site has none, so that column is empty rather than filled with zeros.

## 2026-08-17 — attribution since 2026-08-14

Search Console data through 2026-08-14 (3-day lag). Days are counted from each page's own ship date, or from its last substantial rewrite where there was one.

`no data yet` means the page is younger than the lag, so silence proves nothing. `not yet, Nd` means N observable days with no impression, which **is** a measurement. Neither is written as a zero, because a zero would read as "it happened immediately".


### Tools

Every tool, whatever its age, because the calendar weighting rests on them.

| Page | Cluster | Shipped | Obs. days | 1st impr | 1st human impr | 1st human click | Impr | Human impr |
|---|---|---|---:|---|---|---|---:|---:|
| /linter/ | 4 | 2026-03-14 *(rewritten)* | 153 | 65d | not yet, 153d | not yet, 153d | 9 | 0 |
| /llms-txt-generator/ | 4 | 2026-07-31 | 14 | not yet, 14d | not yet, 14d | not yet, 14d | 0 | 0 |
| /llms-txt-validator/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| /ai-overviews-checker/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| /ai-crawler-checker/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |

### Articles shipped since tracking began

These are the like-for-like comparison against the tools.

| Page | Cluster | Shipped | Obs. days | 1st impr | 1st human impr | 1st human click | Impr | Human impr |
|---|---|---|---:|---|---|---|---:|---:|
| API Documentation Best Practices: Reference, | 1 | 2026-08-14 | 0 | not yet, 0d | not yet, 0d | not yet, 0d | 0 | 0 |
| API Documentation Examples: What the Best De | 1 | 2026-08-15 | — | no data yet | no data yet | no data yet | 0 | 0 |
| API Documentation Tools: A Workflow Comparis | 1 | 2026-08-16 *(rewritten)* | — | no data yet | no data yet | no data yet | 0 | 0 |
| AI Crawlers in robots.txt: Training, Citatio | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| API Documentation Template: The Pages Every  | 1 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| llms.txt Examples: Four Public Files Audited | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| What Makes a Page Extractable by an Answer E | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |

### Pre-existing articles, rewritten but not newly shipped

66 article(s) shipped before 2026-08-14 and are excluded from the comparison: 66 were substantially rewritten in this window and 0 carry impressions predating their current source file, because the AI cluster was recovered from 404 and its URLs ranked long before the files were restored. Days-to-first-impression is meaningless for both. The ten largest by impressions:

| Page | Cluster | Impr | Human impr | 1st impr vs ship |
|---|---|---:|---:|---|
| How Anthropic's Contextual Retrieval Changes | 3 | 2420 | 3 | 61d |
| Context Engineering as Heap Management: Accu | 3 | 144 | 0 | 67d |
| How Memory Works in Claude Code | 3 | 138 | 14 | 35d |
| Vector Embeddings: a Guide to the Geometry o | 3 | 120 | 0 | 92d |
| Shared Memory vs Isolated Memory in Multi-Ag | 3 | 120 | 1 | 12d |
| How Stripe's Technical Blog Became a Competi | 2 | 116 | 21 | 72d |
| Prompt Caching: What It Is and When the Math | 3 | 111 | 102 | 7d |
| Fine-Tuning vs RAG for Agent Memory: When Ea | 3 | 87 | 2 | 46d |
| Vector Search in the Browser: PGlite vs. SQL | 3 | 86 | 0 | 72d |
| Multi-Agent vs Single-Agent Systems: The Rea | 3 | 80 | 35 | 31d |

### What the pages with real age already show

Only pages observable for 30+ days. The like-for-like comparison below will stay unanswerable for weeks, but this evidence exists now and it is the only evidence about tools there is.

| | Pages | Reached an impression | Median days to first | Median impr | Total impr | Total human impr | Pages with any human impr |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tools | 1 | 1 | 65 | 9 | 9 | 0 | 0 |
| Articles | 65 | 59 | 67 | 19 | 4658 | 320 | 26 |

Aged tools individually:

- `/linter/` — 153d live, 65d to first impression, 9 impressions, 0 human

**The aged evidence does not support the tools bet, and it is the only evidence there is.** Time to a first impression is indistinguishable from articles — median 65d against 67d, which on 1 tool(s) is not a difference. On volume the gap is not close: 1 aged tool(s) hold 9 impressions and 0 human, against 4658 and 320 across 65 aged article(s). 0 of the tools have earned a single human impression, against 26 of the articles. Two caveats that matter before anyone reweights the calendar. The sample is 1 tool(s), which is not a basis for a decision on sixty rows. And the aged tool is `/linter/`, a documentation linter that predates the AI-search cluster — the four tools the bet actually rests on are days old. This is a reason to wait for those four rather than a reason to abandon the bet, and it is equally not a reason to add more tool rows before they report.


### The bet: do tools reach search sooner than articles?

Newly shipped pages only. A pre-existing page carries history that says nothing about how fast a new publish reaches search, and a recovered URL carries impressions older than its own source file.

| | Tracked | Eligible | Observable | Reached an impression | Median days | Impressions | Human impr | Clicks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Tools | 5 | 3 | 0 | 0 | n/a | 0 | 0 | 0 |
| Articles | 73 | 7 | 1 | 0 | n/a | 0 | 0 | 0 |

Excluded from the comparison: tools 2 pre-existing / 0 recovered, articles 66 pre-existing / 0 recovered.

**Not answerable yet, and that is now a measurement rather than a wait.** 0 tool(s) and 1 article(s) have been observable and neither side has earned a single impression. No lever is working yet; the question of which works better cannot be opened until one of them does.

**What this cannot test.** The tools bet rests on no build-a-tool keyword carrying an AI Overview while all 15 top niche keywords do. That is a claim about other people's SERPs, taken from Ahrefs. **Search Console has no AI Overview dimension**, so there is no first-party way to confirm an AI Overview appeared above one of our own results, and Ahrefs is unavailable. The measurable consequence is impression-to-click conversion at comparable positions, which needs clicks; the site has none, so that column is empty rather than filled with zeros.

## 2026-08-17 — attribution since 2026-08-14

Search Console data through 2026-08-14 (3-day lag). Days are counted from each page's own ship date, or from its last substantial rewrite where there was one.

`no data yet` means the page is younger than the lag, so silence proves nothing. `not yet, Nd` means N observable days with no impression, which **is** a measurement. Neither is written as a zero, because a zero would read as "it happened immediately".


### Tools

Every tool, whatever its age, because the calendar weighting rests on them.

| Page | Cluster | Shipped | Obs. days | 1st impr | 1st human impr | 1st human click | Impr | Human impr |
|---|---|---|---:|---|---|---|---:|---:|
| /linter/ | 4 | 2026-03-14 *(rewritten)* | 153 | 65d | not yet, 153d | not yet, 153d | 9 | 0 |
| /llms-txt-generator/ | 4 | 2026-07-31 | 14 | not yet, 14d | not yet, 14d | not yet, 14d | 0 | 0 |
| /llms-txt-validator/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| /ai-overviews-checker/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| /ai-crawler-checker/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |

### Articles shipped since tracking began

These are the like-for-like comparison against the tools.

| Page | Cluster | Shipped | Obs. days | 1st impr | 1st human impr | 1st human click | Impr | Human impr |
|---|---|---|---:|---|---|---|---:|---:|
| API Documentation Best Practices: Reference, | 1 | 2026-08-14 | 0 | not yet, 0d | not yet, 0d | not yet, 0d | 0 | 0 |
| API Documentation Examples: What the Best De | 1 | 2026-08-15 | — | no data yet | no data yet | no data yet | 0 | 0 |
| API Documentation Tools: A Workflow Comparis | 1 | 2026-08-16 *(rewritten)* | — | no data yet | no data yet | no data yet | 0 | 0 |
| AI Crawlers in robots.txt: Training, Citatio | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| API Documentation Template: The Pages Every  | 1 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| llms.txt Examples: Four Public Files Audited | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |
| What Makes a Page Extractable by an Answer E | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 |

### Pre-existing articles, rewritten but not newly shipped

66 article(s) shipped before 2026-08-14 and are excluded from the comparison: 66 were substantially rewritten in this window and 0 carry impressions predating their current source file, because the AI cluster was recovered from 404 and its URLs ranked long before the files were restored. Days-to-first-impression is meaningless for both. The ten largest by impressions:

| Page | Cluster | Impr | Human impr | 1st impr vs ship |
|---|---|---:|---:|---|
| How Anthropic's Contextual Retrieval Changes | 3 | 2420 | 3 | 61d |
| Context Engineering as Heap Management: Accu | 3 | 144 | 0 | 67d |
| How Memory Works in Claude Code | 3 | 138 | 14 | 35d |
| Vector Embeddings: a Guide to the Geometry o | 3 | 120 | 0 | 92d |
| Shared Memory vs Isolated Memory in Multi-Ag | 3 | 120 | 1 | 12d |
| How Stripe's Technical Blog Became a Competi | 2 | 116 | 21 | 72d |
| Prompt Caching: What It Is and When the Math | 3 | 111 | 102 | 7d |
| Fine-Tuning vs RAG for Agent Memory: When Ea | 3 | 87 | 2 | 46d |
| Vector Search in the Browser: PGlite vs. SQL | 3 | 86 | 0 | 72d |
| Multi-Agent vs Single-Agent Systems: The Rea | 3 | 80 | 35 | 31d |

### What the pages with real age already show

Only pages observable for 30+ days. The like-for-like comparison below will stay unanswerable for weeks, but this evidence exists now and it is the only evidence about tools there is.

| | Pages | Reached an impression | Median days to first | Median impr | Total impr | Total human impr | Pages with any human impr |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tools | 1 | 1 | 65 | 9 | 9 | 0 | 0 |
| Articles | 65 | 59 | 67 | 19 | 4658 | 320 | 26 |

Aged tools individually:

- `/linter/` — 153d live, 65d to first impression, 9 impressions, 0 human

**The aged evidence does not support the tools bet, and it is the only evidence there is.** Time to a first impression is indistinguishable from articles — median 65d against 67d, which on 1 tool(s) is not a difference. On volume the gap is not close: 1 aged tool(s) hold 9 impressions and 0 human, against 4658 and 320 across 65 aged article(s). 0 of the tools have earned a single human impression, against 26 of the articles. Two caveats that matter before anyone reweights the calendar. The sample is 1 tool(s), which is not a basis for a decision on sixty rows. And the aged tool is `/linter/`, a documentation linter that predates the AI-search cluster — the four tools the bet actually rests on are days old. This is a reason to wait for those four rather than a reason to abandon the bet, and it is equally not a reason to add more tool rows before they report.


### The bet: do tools reach search sooner than articles?

Newly shipped pages only. A pre-existing page carries history that says nothing about how fast a new publish reaches search, and a recovered URL carries impressions older than its own source file.

| | Tracked | Eligible | Observable | Reached an impression | Median days | Impressions | Human impr | Clicks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Tools | 5 | 3 | 0 | 0 | n/a | 0 | 0 | 0 |
| Articles | 73 | 7 | 1 | 0 | n/a | 0 | 0 | 0 |

Excluded from the comparison: tools 2 pre-existing / 0 recovered, articles 66 pre-existing / 0 recovered.

**Not answerable yet, and that is now a measurement rather than a wait.** 0 tool(s) and 1 article(s) have been observable and neither side has earned a single impression. No lever is working yet; the question of which works better cannot be opened until one of them does.

**What this cannot test.** The tools bet rests on no build-a-tool keyword carrying an AI Overview while all 15 top niche keywords do. That is a claim about other people's SERPs, taken from Ahrefs. **Search Console has no AI Overview dimension**, so there is no first-party way to confirm an AI Overview appeared above one of our own results, and Ahrefs is unavailable. The measurable consequence is impression-to-click conversion at comparable positions, which needs clicks; the site has none, so that column is empty rather than filled with zeros.
