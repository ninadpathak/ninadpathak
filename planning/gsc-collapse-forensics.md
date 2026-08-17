# Collapse forensics

Appended by `tools/gsc_collapse_forensics.py`. Decomposes a traffic drop into
step-or-slope, page, query, device and country, and flags URL paths belonging
to no version of the site. Search Analytics cannot see manual actions,
security issues, or algorithm updates, so causes are named as inferences.

## 2026-08-17 — collapse forensics, 2025-08-04 to 2025-12-28

**Largest weekly fall by volume:** week of 2025-09-01 to 2025-09-08, legitimate impressions 791 -> 260, a loss of 531 (67%). This is the event.

The steepest *proportional* fall was a different week — 2025-09-15 to 2025-09-22, 56 -> 10 (82%) — which is the tail of the same decline and not a second event. Ranking by proportion alone would have pointed at the wrong week.

### Weekly series, legitimate against foreign URLs

| Week | Legit impr | Legit pages | Foreign impr | Foreign pages |
|---|---:|---:|---:|---:|
| 2025-08-04 | 1055 | 22 | 0 | 0 |
| 2025-08-11 | 911 | 18 | 0 | 0 |
| 2025-08-18 | 863 | 9 | 0 | 0 |
| 2025-08-25 | 718 | 13 | 0 | 0 |
| 2025-09-01 | 791 | 17 | 0 | 0 |
| 2025-09-08 | 260 | 14 | 18 | 16 |
| 2025-09-15 | 56 | 5 | 99 | 76 |
| 2025-09-22 | 10 | 4 | 188 | 128 |
| 2025-09-29 | 11 | 4 | 381 | 233 |
| 2025-10-06 | 35 | 7 | 366 | 201 |
| 2025-10-13 | 30 | 7 | 71 | 50 |
| 2025-10-20 | 62 | 10 | 32 | 15 |
| 2025-10-27 | 37 | 8 | 22 | 19 |
| 2025-11-03 | 65 | 8 | 28 | 17 |
| 2025-11-10 | 51 | 8 | 33 | 18 |
| 2025-11-17 | 44 | 7 | 60 | 58 |
| 2025-11-24 | 67 | 10 | 35 | 20 |
| 2025-12-01 | 37 | 9 | 45 | 35 |
| 2025-12-08 | 36 | 7 | 58 | 31 |
| 2025-12-15 | 19 | 8 | 19 | 19 |
| 2025-12-22 | 16 | 3 | 23 | 23 |

### Pages

22 pages before, 104 after. 3 survived, 19 vanished, carrying 2764 impressions.

| Page | Before | Pos | After |
|---|---:|---:|---:|
| /guides/css-grid-layouts-webflow-table/ | 962 | 26.4 | GONE |
| /marketing-research/stripe-documentation-case-study/ | 762 | 6.3 | GONE |
| /marketing-research/asana-marketing-case-study/ | 713 | 26.4 | GONE |
| /todoist-vs-any-do/ | 529 | 31.1 | 6 |
| /todoist-vs-things-3/ | 146 | 43.7 | GONE |
| /todoist-vs-airtable/ | 110 | 24.9 | GONE |
| / | 61 | 4.3 | 86 |
| /ticktick-vs-any-do/ | 18 | 56.5 | GONE |
| /portfolio/ | 16 | 28.1 | 1 |
| /process/ | 11 | 8.3 | GONE |
| /essays/notion-api-documentation-case-study/ | 9 | 5.9 | GONE |
| /guides/ | 9 | 13.4 | GONE |

### Queries

119 before, 15 after, **1 in both**. 1569 impressions sat on queries that stopped appearing entirely.

Position band of the vanished impressions, before the fall:

| Band | Impressions |
|---|---:|
| 1-10 | 32 |
| 11-20 | 194 |
| 21-30 | 573 |
| 31-50 | 609 |
| 51+ | 161 |

| Surviving query | Impr before | after | Pos before | after |
|---|---:|---:|---:|---:|
| ninad pathak | 18 | 27 | 4.4 | 3.2 |

### Device

- **before**: DESKTOP=2974@22, MOBILE=318@31, TABLET=5@4
- **after**: DESKTOP=175@8, MOBILE=120@5, TABLET=4@6

### Country

- **before**: usa=2172@21, gbr=177@34, ind=107@27, can=88@25, aus=66@35, fra=57@31
- **after**: usa=100@7, ind=60@6, jpn=56@7, can=5@4, idn=5@6, tur=5@9

### What this cannot settle

Search Analytics reports impressions, clicks and position only. It cannot see manual actions, security issues, or algorithm updates, so a demotion and a deindexing look alike here and co-timing is not causation. The Manual Actions and Security Issues reports in the Search Console UI are the only thing that settles whether a penalty was applied.
