# Attribution

Maintained by `tools/gsc_attribution.py`, one authoritative section per day.
Every page shipped or substantially rewritten recently, and every tool, is
measured from its own publish date rather than sitewide — the only way to see
which lever works while the sitewide numbers are zero.

`no data yet` means younger than the Search Console lag. `not yet, Nd` means N
observable days and still nothing, which is a real measurement. Neither is
written as a zero. Named-human figures are floors. Every dated section gives
their exact query-coverage denominator and a floor-to-ceiling interval for
withheld impressions; the ceiling is an error bound, not an estimate.

## 2026-08-17 — attribution since 2026-08-14

Search Console data through 2026-08-14 (3-day lag). Days are counted from each page's own ship date, or from its last substantial rewrite where there was one.

`no data yet` means the page is younger than the lag, so silence proves nothing. `not yet, Nd` means N observable days with no impression, which **is** a measurement. Neither is written as a zero, because a zero would read as "it happened immediately".

Across tracked pages, named-query rows expose **642 of 4667 impressions (13.8%)**; **4025 are withheld**. The visible named-human count is a floor of 320; its defensible interval is **320–4345**, where the ceiling assumes every withheld impression was human. That ceiling is an error bound, not an estimate.


### Tools

Every tool, whatever its age, because the calendar weighting rests on them.

| Page | Cluster | Shipped | Obs. days | 1st impr | 1st named-human impr | 1st named-human click | Impr | Named-human floor | Withheld | Human interval |
|---|---|---|---:|---|---|---|---:|---:|---:|---:|
| /linter/ | 4 | 2026-03-14 *(rewritten)* | 153 | 65d | not yet, 153d | not yet, 153d | 9 | 0 | 9 | 0–9 |
| /llms-txt-generator/ | 4 | 2026-07-31 | 14 | not yet, 14d | not yet, 14d | not yet, 14d | 0 | 0 | 0 | 0–0 |
| /llms-txt-validator/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 | 0 | 0–0 |
| /ai-overviews-checker/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 | 0 | 0–0 |
| /ai-crawler-checker/ | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 | 0 | 0–0 |

### Articles shipped since tracking began

These are the like-for-like comparison against the tools.

| Page | Cluster | Shipped | Obs. days | 1st impr | 1st named-human impr | 1st named-human click | Impr | Named-human floor | Withheld | Human interval |
|---|---|---|---:|---|---|---|---:|---:|---:|---:|
| API Documentation Best Practices: Reference, | 1 | 2026-08-14 | 0 | not yet, 0d | not yet, 0d | not yet, 0d | 0 | 0 | 0 | 0–0 |
| API Documentation Examples: What the Best De | 1 | 2026-08-15 | — | no data yet | no data yet | no data yet | 0 | 0 | 0 | 0–0 |
| API Documentation Tools: A Workflow Comparis | 1 | 2026-08-16 *(rewritten)* | — | no data yet | no data yet | no data yet | 0 | 0 | 0 | 0–0 |
| AI Crawlers in robots.txt: Training, Citatio | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 | 0 | 0–0 |
| API Documentation Template: The Pages Every  | 1 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 | 0 | 0–0 |
| llms.txt Examples: Four Public Files Audited | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 | 0 | 0–0 |
| What Makes a Page Extractable by an Answer E | 4 | 2026-08-17 | — | no data yet | no data yet | no data yet | 0 | 0 | 0 | 0–0 |

### Pre-existing articles, rewritten but not newly shipped

66 article(s) shipped before 2026-08-14 and are excluded from the comparison: 66 were substantially rewritten in this window and 0 carry impressions predating their current source file, because the AI cluster was recovered from 404 and its URLs ranked long before the files were restored. Days-to-first-impression is meaningless for both. The ten largest by impressions:

| Page | Cluster | Impr | Named-human floor | Withheld | Human interval | 1st impr vs ship |
|---|---|---:|---:|---:|---:|---|
| How Anthropic's Contextual Retrieval Changes | 3 | 2420 | 3 | 2168 | 3–2171 | 61d |
| Context Engineering as Heap Management: Accu | 3 | 144 | 0 | 144 | 0–144 | 67d |
| How Memory Works in Claude Code | 3 | 138 | 14 | 124 | 14–138 | 35d |
| Vector Embeddings: a Guide to the Geometry o | 3 | 120 | 0 | 120 | 0–120 | 92d |
| Shared Memory vs Isolated Memory in Multi-Ag | 3 | 120 | 1 | 114 | 1–115 | 12d |
| How Stripe's Technical Blog Became a Competi | 2 | 116 | 21 | 89 | 21–110 | 72d |
| Prompt Caching: What It Is and When the Math | 3 | 111 | 102 | 9 | 102–111 | 7d |
| Fine-Tuning vs RAG for Agent Memory: When Ea | 3 | 87 | 2 | 64 | 2–66 | 46d |
| Vector Search in the Browser: PGlite vs. SQL | 3 | 86 | 0 | 86 | 0–86 | 72d |
| Multi-Agent vs Single-Agent Systems: The Rea | 3 | 80 | 35 | 45 | 35–80 | 31d |

### What the pages with real age already show

Only pages observable for 30+ days. The like-for-like comparison below will stay unanswerable for weeks, but this evidence exists now and it is the only evidence about tools there is.

| | Pages | Reached an impression | Median days to first | Median impr | Total impr | Named-human interval | Pages with a named-human impr |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tools | 1 | 1 | 65 | 9 | 9 | 0–9 | 0 |
| Articles | 65 | 59 | 67 | 19 | 4658 | 320–4336 | 26 |

Aged tools individually:

- `/linter/` — 153d live, 65d to first impression, 9 impressions, named-human interval 0–9 (9 withheld)

**The aged evidence does not support the tools bet, and it is the only evidence there is.** Time to a first impression is indistinguishable from articles — median 65d against 67d, which on 1 tool(s) is not a difference. On page-level volume the gap is not close: 1 aged tool(s) hold 9 impressions, against 4658 across 65 aged article(s). Named-human impressions are floors, not totals: tools 0–9, articles 320–4336, where each ceiling assigns every withheld impression to a human. 0 of the tools expose a named-human impression, against 26 of the articles; withheld queries prevent this from proving the remainder had no human demand. Two caveats that matter before anyone reweights the calendar. The sample is 1 tool(s), which is not a basis for a decision on sixty rows. And the aged tool is `/linter/`, a documentation linter that predates the AI-search cluster — the four tools the bet actually rests on are days old. This is a reason to wait for those four rather than a reason to abandon the bet, and it is equally not a reason to add more tool rows before they report.


### The bet: do tools reach search sooner than articles?

Newly shipped pages only. A pre-existing page carries history that says nothing about how fast a new publish reaches search, and a recovered URL carries impressions older than its own source file.

| | Tracked | Eligible | Observable | Reached an impression | Median days | Impressions | Named-human interval | Clicks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Tools | 5 | 3 | 0 | 0 | n/a | 0 | 0–0 | 0 |
| Articles | 73 | 7 | 1 | 0 | n/a | 0 | 0–0 | 0 |

Excluded from the comparison: tools 2 pre-existing / 0 recovered, articles 66 pre-existing / 0 recovered.

**Not answerable yet, and that is now a measurement rather than a wait.** 0 tool(s) and 1 article(s) have been observable and neither side has earned a page-level impression. No lever is working yet; the question of which works better cannot be opened until one of them does. Across these eligible pages, 0 impressions are withheld from named-query rows; that bound matters once page impressions exist, but it cannot turn page-level silence into demand.

**What this cannot test.** The original tools bet rested on keyword research claiming no build-a-tool keyword carried an AI Overview; live SERP reads later falsified that premise and tool building stopped at five. **Search Console has no AI Overview dimension**, so this instrument cannot reproduce either external SERP claim. The measurable consequence is impression-to-click conversion at comparable positions, which needs named human clicks; the visible floor is empty. Withheld queries prevent that floor from proving no human demand.
