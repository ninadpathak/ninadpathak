# Collapse forensics

Maintained by `tools/gsc_collapse_forensics.py`, one authoritative section per date. Decomposes a traffic drop into
step-or-slope, page, query, device and country, and flags URL paths belonging
to no version of the site. Search Analytics cannot see manual actions,
security issues, or algorithm updates, so causes are named as inferences.

## 2026-08-17 — collapse forensics, 2025-08-01 to 2025-12-31

**Largest weekly fall by volume:** week of 2025-09-05 to 2025-09-12, legitimate impressions 517 -> 77, a loss of 440 (85%). This is the event.

### Weekly series, legitimate against foreign URLs

| Week | Legit impr | Legit pages | Foreign impr | Foreign pages |
|---|---:|---:|---:|---:|
| 2025-08-01 | 1066 | 22 | 0 | 0 |
| 2025-08-08 | 951 | 20 | 0 | 0 |
| 2025-08-15 | 887 | 16 | 0 | 0 |
| 2025-08-22 | 775 | 12 | 0 | 0 |
| 2025-08-29 | 782 | 14 | 0 | 0 |
| 2025-09-05 | 517 | 16 | 0 | 0 |
| 2025-09-12 | 77 | 8 | 24 | 20 |
| 2025-09-19 | 15 | 4 | 216 | 148 |
| 2025-09-26 | 6 | 3 | 175 | 129 |
| 2025-10-03 | 34 | 7 | 512 | 298 |
| 2025-10-10 | 24 | 6 | 184 | 104 |
| 2025-10-17 | 53 | 10 | 36 | 26 |
| 2025-10-24 | 43 | 7 | 25 | 15 |
| 2025-10-31 | 68 | 9 | 26 | 17 |
| 2025-11-07 | 50 | 8 | 36 | 19 |
| 2025-11-14 | 42 | 9 | 10 | 10 |
| 2025-11-21 | 53 | 8 | 61 | 59 |
| 2025-11-28 | 62 | 9 | 66 | 37 |
| 2025-12-05 | 27 | 9 | 47 | 31 |
| 2025-12-12 | 31 | 8 | 36 | 23 |
| 2025-12-19 | 17 | 5 | 22 | 22 |
| 2025-12-26 | 13 | 4 | 9 | 9 |

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
