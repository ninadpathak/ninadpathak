# Human-only Search Console baseline

Appended by `tools/gsc_human_baseline.py`. Separates machine query fan-out
from people and reports the human-only series monthly. Read the denominator
note in each run: shares are measured within the named-query subset, the
sitewide machine share is a range rather than a number, and the human series
is a floor because Search Console withholds low-volume queries.

## 2026-08-17 — machine fan-out share and human-only baseline

Span 2025-04-01 to 2026-08-14. Classifier shared with `tools/gsc_report.py`; fan-out model built once over every query in the span, because family detection needs 3 variants to see a family at all.

### The denominator problem, first

Sitewide: **237 clicks / 33549 impressions**. Named queries account for 72 clicks and 16416 impressions — **48.9% of sitewide impressions**. Search Console withholds the rest, so:

- Every share below is measured **within the named-query subset**, which is the only denominator that exists.
- The sitewide machine share is a **range**: **1.8% to 52.9%** of all impressions. Lower bound assumes every withheld impression is human, upper assumes every one is machine. There is no point estimate and the midpoint is not one.

### Composition of named queries, whole span

| Bucket | Queries | Clicks | Impressions | Share of named impressions |
|---|---:|---:|---:|---:|
| Human | 1395 | 20 | 15265 | 93.0% |
| Machine fan-out | 123 | 3 | 599 | 3.6% |
| Brand | 39 | 49 | 549 | 3.3% |
| Pasted blob | 2 | 0 | 3 | 0.0% |
| **Named total** | 1559 | 72 | 16416 | 100% |
| *Withheld by Search Console* | — | 165 | 17133 | *unclassifiable* |

### Human-only monthly baseline

Human clicks, impressions and impression-weighted position, with fan-out, brand and blobs removed. A **floor** on human traffic: withheld queries are excluded entirely and some of them are certainly human.

| Month | Site impr | Named impr | Human impr | Human clicks | Human pos | Machine impr | Machine % of named |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2025-04 | 3822 | 2604 | 2532 | 3 | 44.2 | 43 | 1.7% |
| 2025-05 | 5555 | 3750 | 3641 | 0 | 39.2 | 60 | 1.6% |
| 2025-06 | 6499 | 3535 | 3362 | 1 | 38.6 | 133 | 3.8% |
| 2025-07 | 4106 | 2062 | 1967 | 5 | 36.4 | 60 | 2.9% |
| 2025-08 | 3860 | 1965 | 1916 | 3 | 34.6 | 28 | 1.4% |
| 2025-09 | 1294 | 533 | 517 | 2 | 32.6 | 3 | 0.6% |
| 2025-10 | 904 | 240 | 221 | 6 | 15.9 | 0 | 0.0% |
| 2025-11 | 244 | 38 | 13 | 0 | 30.7 | 0 | 0.0% |
| 2025-12 | 110 | 31 | 7 | 0 | 35.9 | 0 | 0.0% |
| 2026-01 | 134 | 43 | 2 | 0 | 52.5 | 0 | 0.0% |
| 2026-02 | 174 | 79 | 49 | 0 | 73.7 | 3 | 3.8% |
| 2026-03 | 652 | 473 | 437 | 0 | 77.4 | 4 | 0.8% |
| 2026-04 | 194 | 62 | 30 | 0 | 73.3 | 2 | 3.2% |
| 2026-05 | 825 | 207 | 171 | 0 | 52.6 | 10 | 4.8% |
| 2026-06 | 1754 | 254 | 202 | 0 | 52.3 | 19 | 7.5% |
| 2026-07 | 2476 | 330 | 152 | 0 | 41.1 | 114 | 34.5% |
| 2026-08 | 946 | 210 | 46 | 0 | 56.7 | 120 | 57.1% |

### Fan-out families found

Collapsed, not dropped. A genuine topic with many close human variants would cluster here too, so read this list rather than trusting the split blindly.

| Variants | Shared core | Impressions | Clicks | Avg pos | Example |
|---:|---|---:|---:|---:|---|
| 69 | `anthropic contextual retrieval` | 328 | 0 | 8.7 | anthropic contextual retrieval bm25 embeddings r |
| 3 | `app right ticktick todoist` | 63 | 0 | 44.0 | ticktick vs todoist which app is right for you |
| 15 | `css grid table` | 34 | 0 | 13.5 | css grid table layout example |
| 4 | `creating css div table` | 16 | 0 | 33.0 | creating a table using div and css |
| 3 | `any.do calendar google integration` | 9 | 0 | 97.3 | any.do google calendar integration |
| 3 | `agent ai classification taxonomy` | 7 | 0 | 18.0 | ai agent classification taxonomy |
| 6 | `css layout table` | 6 | 0 | 59.8 | css div table layout |
| 3 | `3 microsoft things todo` | 6 | 0 | 71.0 | things 3 vs microsoft todo |
| 3 | `books content marketing top` | 6 | 0 | 80.5 | top content marketing books |
| 4 | `grid html show table` | 4 | 0 | 27.0 | html table show grid |
| 4 | `3 things ticktick todoist` | 4 | 1 | 22.8 | ticktick vs todoist vs things 3 |
| 3 | `2023 document embeddings hyde hypothetical paper` | 3 | 0 | 68.0 | hyde hypothetical document embeddings paper 2023 |
| 3 | `affect agent audits decisions explainability isolated memory shared` | 3 | 0 | 5.0 | how does shared versus isolated memory affect th |
