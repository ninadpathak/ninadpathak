# Leading indicators

Maintained by `tools/gsc_leading.py`, one authoritative section per date. The earliest signals that move on
this domain, so the first one arrives as news rather than as a retrospective
discovery — the autumn 2025 spam injection went unnoticed for ten months
because nothing read the record that showed it.

Time-to-first-impression is reported **by ship era**, not by cluster. Grouping
by cluster across eras reports a seven-fold effect that does not exist; the
clusters shipped at different times and the domain's indexing speed changed
underneath them. Cluster is only compared inside a single era.

A section reading "no data yet" is working. A zero would mean "nothing
happened"; these sections say "we cannot see yet" and how long until they can.

## 2026-08-17 — leading indicators

Search Console data through 2026-08-14 (3-day lag). Read daily. A section reading "no data yet" is working correctly — the point is that the first real signal shows up in days rather than being found retrospectively.

### 1. Time to first impression — the variable is the era, not the cluster

73 of 90 published pages are at least 14 days old; 17 are younger and are excluded rather than counted as failures.

| Ship quarter | Pages earned | Median days to 1st impression | Min | Max |
|---|---:|---:|---:|---:|
| 2026-Q1 | 12 | **96** | 7 | 138 |
| 2026-Q2 | 51 | **66** | 4 | 94 |
| 2026-Q3 | 3 | **4** | 3 | 8 |

**2026-Q1 to 2026-Q3: 96d → 4d.** The domain now surfaces a new page far faster than it did, which is what makes any of these indicators usable as feedback rather than as history. **The latest era is n=3**, so treat the 4d figure as an early reading rather than an established rate; the direction across three eras is better supported than the level in any one of them.

**By cluster, only within an era — because across eras it is a confound.**

| Era | Cluster | Pages | Median days |
|---|---|---:|---:|
| 2026-Q2 | ai-engineering | 40 | 62 |
| 2026-Q2 | developer-experience | 6 | 72 |
| 2026-Q2 | technical-documentation | 5 | 72 |

Grouping by cluster across all eras would report documentation at 9d against AI-engineering at 65d. That is a seven-fold effect that does not exist: documentation shipped in 2026-Q3 and AI-engineering in Q1–Q2. Within a shared era the clusters land within ten days of each other, so **cluster choice is close to neutral on indexing speed** and the calendar reweighting is neither helped nor punished by it.

**Earn rate — does a page ever earn an impression at all.**

| Cluster | Pages aged | Earned | Rate |
|---|---:|---:|---:|
| ai-engineering | 57 | 52 | 91% |
| developer-experience | 7 | 6 | 86% |
| technical-documentation | 9 | 8 | 89% |

### 2. Recovery watchlist

Previously-indexed URLs we still serve that have earned nothing for 28+ days. Defined from the record, not from an event date, so it catches any cause. **14 URL(s), 197 impressions of history between them.** When one returns, the silence length is the return lag — the number that decides whether recovery beats new publishing.

| URL | Impressions ever | Last seen | Silent |
|---|---:|---|---:|
| /glossary/tool-calling/ | 43 | 2026-06-05 | 70d |
| /glossary/agentic-engineering/ | 25 | 2026-07-02 | 43d |
| /glossary/react-prompting/ | 21 | 2026-07-12 | 33d |
| /glossary/pagedattention/ | 17 | 2026-07-10 | 35d |
| /glossary/graphrag/ | 15 | 2026-07-08 | 37d |
| /glossary/dspy/ | 14 | 2026-06-11 | 64d |
| /glossary/flow-engineering/ | 12 | 2026-07-11 | 34d |
| /glossary/hypothetical-document-embeddings-hyde/ | 11 | 2026-07-11 | 34d |
| /glossary/cross-encoder-reranking/ | 10 | 2026-06-28 | 47d |
| /glossary/plan-and-solve-framework/ | 8 | 2026-06-23 | 52d |
| /glossary/model-context-protocol/ | 7 | 2026-04-15 | 121d |
| /glossary/semantic-caching/ | 7 | 2026-05-25 | 81d |
| /glossary/context-engineering/ | 5 | 2026-06-05 | 70d |
| /work/mem0/ | 2 | 2026-07-16 | 29d |

**Already returned once:** 15 URL(s) have a silence of 28+ days inside the record followed by impressions again, median silence 49d. That is a historical return lag, not a controlled measurement — nothing here confirms the URL was unreachable during the gap rather than simply not shown.

| URL | Impressions ever | Longest silence |
|---|---:|---:|
| /glossary/matryoshka-representation-learning/ | 13 | 113d |
| /glossary/speculative-decoding/ | 23 | 87d |
| /glossary/json-mode-vs-structured-outputs/ | 4 | 56d |
| /glossary/cross-encoder-reranking/ | 10 | 53d |
| /glossary/pagedattention/ | 17 | 52d |
| /glossary/test-time-compute/ | 7 | 52d |
| /work/mem0/ | 2 | 51d |
| /glossary/bi-encoder/ | 17 | 49d |

### 3. Revision cohort — does rewriting move anything

76 page(s) substantially rewritten in the last 7 days. Impressions in the 14 days before the change against everything since.

Of those: **3 have at least one observable day**, **3 of those earned nothing before the rewrite** and so cannot show a revision effect either way, leaving **0 informative**.

**No answer yet, and this is the honest state rather than a null result.** The rewrites with an observable day all sit on pages that had zero impressions to begin with, so nothing here can distinguish "the rewrite did nothing" from "we cannot see yet". The first informative comparison needs a rewritten page that was already earning impressions.

### What this cannot answer yet

- **Whether cluster 3 genuinely indexes faster than cluster 1** — within the one shared era the gap is under ten days on small samples, which is too close to call and too small to test. Not decidable now, and it is probably not the question that matters.
- **Whether substantive revision moves impressions** — 76 rewrites in the window and the 3 with an observable day all sit on pages that earned nothing beforehand, so there is no signal for a rewrite to move. Needs a rewritten page that was already earning.
- **Whether recovery re-ranks faster than new publishing earns** — the watchlist is populated but no listed URL has returned inside the data window, so there is no return lag to compare against the time-to-first-impression figures above.
- **Anything about clicks.** Human non-brand clicks are zero and have been for ten months; every indicator here is an impression indicator, and an impression is not a reader.

## 2026-08-18 — leading indicators

Search Console data through 2026-08-15 (3-day lag). Read daily. A section reading "no data yet" is working correctly — the point is that the first real signal shows up in days rather than being found retrospectively.

### 1. Time to first impression — the variable is the era, not the cluster

74 of 90 published pages are at least 14 days old; 16 are younger and are excluded rather than counted as failures.

| Ship quarter | Pages earned | Median days to 1st impression | Min | Max |
|---|---:|---:|---:|---:|
| 2026-Q1 | 12 | **96** | 7 | 138 |
| 2026-Q2 | 51 | **66** | 4 | 94 |
| 2026-Q3 | 4 | **4** | 3 | 8 |

**2026-Q1 to 2026-Q3: 96d → 4d.** The domain now surfaces a new page far faster than it did, which is what makes any of these indicators usable as feedback rather than as history. **The latest era is n=4**, so treat the 4d figure as an early reading rather than an established rate; the direction across three eras is better supported than the level in any one of them.

**By cluster, only within an era — because across eras it is a confound.**

| Era | Cluster | Pages | Median days |
|---|---|---:|---:|
| 2026-Q2 | ai-engineering | 40 | 62 |
| 2026-Q2 | developer-experience | 6 | 72 |
| 2026-Q2 | technical-documentation | 5 | 72 |

Grouping by cluster across all eras would report documentation at 9d against AI-engineering at 65d. That is a seven-fold effect that does not exist: documentation shipped in 2026-Q3 and AI-engineering in Q1–Q2. Within a shared era the clusters land within ten days of each other, so **cluster choice is close to neutral on indexing speed** and the calendar reweighting is neither helped nor punished by it.

**Earn rate — does a page ever earn an impression at all.**

| Cluster | Pages aged | Earned | Rate |
|---|---:|---:|---:|
| ai-engineering | 57 | 52 | 91% |
| developer-experience | 7 | 6 | 86% |
| technical-documentation | 10 | 9 | 90% |

### 2. Recovery watchlist

Previously-indexed URLs we still serve that have earned nothing for 28+ days. Defined from the record, not from an event date, so it catches any cause. **12 URL(s), 168 impressions of history between them.** When one returns, the silence length is the return lag — the number that decides whether recovery beats new publishing.

| URL | Impressions ever | Last seen | Silent |
|---|---:|---|---:|
| /glossary/tool-calling/ | 43 | 2026-06-05 | 71d |
| /glossary/agentic-engineering/ | 25 | 2026-07-02 | 44d |
| /glossary/react-prompting/ | 21 | 2026-07-12 | 34d |
| /glossary/pagedattention/ | 17 | 2026-07-10 | 36d |
| /glossary/flow-engineering/ | 12 | 2026-07-11 | 35d |
| /glossary/hypothetical-document-embeddings-hyde/ | 11 | 2026-07-11 | 35d |
| /glossary/cross-encoder-reranking/ | 10 | 2026-06-28 | 48d |
| /glossary/plan-and-solve-framework/ | 8 | 2026-06-23 | 53d |
| /glossary/model-context-protocol/ | 7 | 2026-04-15 | 122d |
| /glossary/semantic-caching/ | 7 | 2026-05-25 | 82d |
| /glossary/context-engineering/ | 5 | 2026-06-05 | 71d |
| /work/mem0/ | 2 | 2026-07-16 | 30d |

**Already returned once:** 15 URL(s) have a silence of 28+ days inside the record followed by impressions again, median silence 49d. That is a historical return lag, not a controlled measurement — nothing here confirms the URL was unreachable during the gap rather than simply not shown.

| URL | Impressions ever | Longest silence |
|---|---:|---:|
| /glossary/matryoshka-representation-learning/ | 13 | 113d |
| /glossary/speculative-decoding/ | 23 | 87d |
| /glossary/json-mode-vs-structured-outputs/ | 4 | 56d |
| /glossary/cross-encoder-reranking/ | 10 | 53d |
| /glossary/pagedattention/ | 17 | 52d |
| /glossary/test-time-compute/ | 7 | 52d |
| /work/mem0/ | 2 | 51d |
| /glossary/bi-encoder/ | 17 | 49d |

### 3. Revision cohort — does rewriting move anything

76 page(s) substantially rewritten in the last 7 days. Impressions in the 14 days before the change against everything since.

Of those: **4 have at least one observable day**, **4 of those earned nothing before the rewrite** and so cannot show a revision effect either way, leaving **0 informative**.

**No answer yet, and this is the honest state rather than a null result.** The rewrites with an observable day all sit on pages that had zero impressions to begin with, so nothing here can distinguish "the rewrite did nothing" from "we cannot see yet". The first informative comparison needs a rewritten page that was already earning impressions.

### What this cannot answer yet

- **Whether cluster 3 genuinely indexes faster than cluster 1** — within the one shared era the gap is under ten days on small samples, which is too close to call and too small to test. Not decidable now, and it is probably not the question that matters.
- **Whether substantive revision moves impressions** — 76 rewrites in the window and the 4 with an observable day all sit on pages that earned nothing beforehand, so there is no signal for a rewrite to move. Needs a rewritten page that was already earning.
- **Whether recovery re-ranks faster than new publishing earns** — the watchlist is populated but no listed URL has returned inside the data window, so there is no return lag to compare against the time-to-first-impression figures above.
- **Anything about clicks.** Human non-brand clicks are zero and have been for ten months; every indicator here is an impression indicator, and an impression is not a reader.
