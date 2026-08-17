# Position analysis

Appended by `tools/gsc_position.py`. The funnel breaks at position, so this asks
what moves it and refuses to answer past the sample.

Position is measured per (page, query) pair, never per page: a page's average
position moves whenever its query mix moves, and that confound has already
produced two false readings on this campaign. Clicks on the injected
`/products/` spam pages are excluded — real people, but not readers of this site.

## 2026-08-17 — what moves position

Search Console through 2026-08-14, human non-brand queries, fan-out removed, and pages outside this site's URL structure excluded — that last filter drops 9 click(s) and 1032 impressions on the injected `/products/` spam pages, which were real people but not readers of this site.

Position is measured **per (page, query) pair**. A page's average position moves when its query mix moves, with no ranking change at all.

### 1. What top-20 pages have that 31+ pages do not

Of 90 published posts, 33 have ever had a human impression and **0 have ever had a human click**.

| | Ever top-20 | Best 21–30 | 31+ only |
|---|---:|---:|---:|
| Pages | 14 | 1 | 18 |
| Inbound body links, median | 4.0 | 7 | 4.0 |
| Pages with zero inbound | 0 | 0 | 0 |
| Word count, median | 1996 | 1239 | 1797 |
| Age in days, median | 132 | 109 | 118 |
| Human impressions, total | 79 | 35 | 253 |
| Human clicks, total | 0 | 0 | 0 |
| Clusters | {'ai-engineering': 11, 'developer-experience': 2, 'technical-documentation': 1} | {'ai-engineering': 1} | {'ai-engineering': 11, 'technical-documentation': 6, 'developer-experience': 1} |

**No feature separates the two groups.** Inbound links, word count and age are within a third of each other, and both groups are dominated by the same cluster. On n=14 against n=18 this is underpowered, but the honest reading is not "we cannot tell" — it is that **the features the campaign can control show no relationship to whether a page reached the top 20.**

### 2. Does position improve over time?

| Cohort | Pairs | Median Δ | Mean Δ | Improved | Worsened | Flat |
|---|---:|---:|---:|---:|---:|---:|
| All | 247 | +1.0 | +1.3 | 80 | 58 | 109 |
| Campaign content | 2 | -2.8 | -2.8 | 1 | 1 | 0 |
| Legacy URLs | 245 | +1.0 | +1.4 | 79 | 57 | 109 |

Δ is places gained, so positive means the pair moved up. A move counts as material at more than 5 places.

**The campaign's own content cannot answer this: n=2.** Almost all the history long enough to show a trend belongs to the previous site (245 pairs), so what follows describes a site that no longer exists.

On legacy URLs the median pair is essentially flat over its own span, with 79 improving materially against 57 worsening and 109 flat. That is much closer to a random walk than to a climb. **Read as a prior rather than a finding, it says pages land near where they will stay, and that publishing more pages at position 40 should not be expected to fix itself with time.** It cannot be transferred to campaign content with any confidence: different pages, different cluster, and a domain whose indexing behaviour has measurably changed since.

### 3. Movers, and whether anything was done to them

84 pair(s) moved more than 10 places. Intervention is read from whether the page's source file was substantially changed during the movement window; for legacy URLs there is no source file, so **82 of them cannot be attributed either way**.

| Query | Page | Δ | From → to | Span | Impr | Intervened |
|---|---|---:|---|---:|---:|---|
| table css template | /guides/css-grid-layouts-webfl | +50.0 | 98.0 → 48.0 | 25d | 3 | unknowable |
| grid in table | /guides/css-grid-layouts-webfl | -47.0 | 27.0 → 74.0 | 60d | 5 | unknowable |
| any.do trello integration | /productivity/any-do-vs-trello | +45.3 | 98.7 → 53.3 | 27d | 8 | unknowable |
| any do vs todoist | /todoist-vs-any-do/ | +43.9 | 44.9 → 1.0 | 358d | 465 | unknowable |
| grid tables | /guides/css-grid-layouts-webfl | -41.5 | 32.5 → 74.0 | 85d | 9 | unknowable |
| todoist vs any.do | /todoist-vs-any-do/ | +37.6 | 38.6 → 1.0 | 344d | 515 | unknowable |
| asana for marketing teams | /marketing-research/asana-mark | +34.6 | 72.3 → 37.7 | 71d | 108 | unknowable |
| todoist or things 3 | /todoist-vs-things-3/ | -34.0 | 1.0 → 35.0 | 101d | 5 | unknowable |
| todoist pro pricing | /todoist-vs-notion/ | +34.0 | 93.0 → 59.0 | 25d | 6 | unknowable |
| kiwi size | /customers/kiwi-sizing/ | +33.0 | 94.0 → 61.0 | 39d | 2 | unknowable |
| marketing asana | /essays/asana-marketing-case-s | +30.9 | 81.5 → 50.6 | 25d | 17 | unknowable |
| todoist comparison | /todoist-vs-things-3/ | -30.2 | 62.5 → 92.7 | 77d | 12 | unknowable |
| table layout in css | /guides/css-grid-layouts-webfl | -29.0 | 53.0 → 82.0 | 72d | 18 | unknowable |
| asana brand book | /marketing-research/asana-mark | +29.0 | 101.0 → 72.0 | 27d | 2 | unknowable |
| best books on content marketin | /blog/best-content-marketing-b | -29.0 | 60.0 → 89.0 | 26d | 2 | unknowable |

**Every campaign-content pair with enough history to show a trend — all 2 of them.** This is the entire evidence base for whether campaign pages move, and both were edited during the window, so neither is a clean natural experiment:

| Query | Page | Δ | From → to | Span | Impr | Intervened |
|---|---|---:|---|---:|---:|---|
| stripe tech blog | /blog/how-stripes-technical-blog-b | +10.5 | 18.5 → 8.0 | 50d | 12 | yes |
| voice ai context retention | /blog/memory-for-voice-ai-agents/ | -16.0 | 81.0 → 97.0 | 22d | 2 | yes |

One up, one down, both intervened. **n=2 with one outcome each way is not evidence in either direction** — it is the sample telling you it is not ready to be asked.

**The clearest improvement nobody caused.** `/todoist-vs-any-do/` moved 44.9 → 1.0 on `any do vs todoist` over 358 days, carrying 465 impressions — the largest sustained gain in the record. It has no source file in this repo and no campaign work has ever touched it. Whether anyone edited it before the March 2026 rebuild is unknowable, but no campaign intervention did.

| Query | Page | Δ | From → to | Span | Impr |
|---|---|---:|---|---:|---:|
| any do vs todoist | /todoist-vs-any-do/ | +43.9 | 44.9 → 1.0 | 358d | 465 |
| todoist vs any.do | /todoist-vs-any-do/ | +37.6 | 38.6 → 1.0 | 344d | 515 |
| todoist any.do integration | /todoist-vs-any-do/ | +14.3 | 59.5 → 45.1 | 168d | 283 |
| any.do vs todoist | /todoist-vs-any-do/ | +11.6 | 45.3 → 33.7 | 168d | 535 |
| asana marketing | /marketing-research/asana-market | +10.9 | 38.7 → 27.8 | 97d | 515 |

The uncomfortable reading: the best-performing pages on this domain by human impressions are legacy comparison pages on topics outside the campaign's niche, which climbed by aging rather than by anything anyone did.

- **Improved without any intervention:** 0 pair(s).
- **Improved with an intervention:** 1 pair(s).
- **Unattributable (legacy, no source file):** 82 pair(s).

### Where the sample is too small to carry a conclusion

- **Feature comparison is n=14 against n=18.** Directional at best, and it currently shows no separation at all rather than a weak one. Do not read the absence of a link effect as evidence that links do not matter; read it as this site having no page whose link profile is unusual enough to test the question.
- **Trajectory on campaign content is n=2.** That is not directional, it is nothing. The legacy figure (n=245) is a prior about a different site.
- **0 of 90 published posts has ever earned a human click**, and only 33 have earned a human impression. Every human click in the record belongs to legacy URLs or to the injected spam pages, so there is no campaign-content click behaviour to analyse — not a small sample, an empty one.
- **Intervention is unknowable for 82 of the movers**, because legacy URLs have no source file to check. Any statement about what caused a legacy page to move is inference from timing alone.
- **The date+page+query pull keeps 17120 of 33549 sitewide impressions (51.0%).** Every count here is a floor, and a page can have moved without appearing at all.
