# 90-Day Keyword and AI-Search Strategy

> **HISTORICAL BASELINE — DO NOT EXECUTE.** This document predates the broad-niche decision, the
> Hermes guarded queue, and the position-based requeue. `campaign-90d.md` and
> `/root/.hermes/knowledge/ninadpathak/content-queue.csv` are authoritative. The original calendar
> is preserved in `planning/research-cache/content-queue-pre-hermes-2026-08-17.csv` as evidence of
> how the campaign changed, not as a second queue.

**Window:** 2026-08-17 to 2026-11-14
**Branch:** `seo/90day-strategy`
**Research:** Ahrefs US, collected 2026-08-17, cached in `planning/research-cache/`
**Status:** superseded 2026-08-17 by `campaign-90d.md` and the guarded Hermes queue.

## What this document adds

`documentation-authority-plan.md` remains canonical for position, ICP, content
specification, and publishing gate. Nothing here overturns those. This document supplies
the four things that plan does not have:

1. A keyword universe with parent-topic resolution, so a keyword becomes a page only when
   Google does not already treat it as part of another page.
2. A cannibalization map against the real published corpus, which is 17 articles rather
   than the 85 files in `content/posts/`.
3. An AI-search plan built on measured AI Overview presence instead of assumption.
4. A day-by-day calendar at one piece per day, with each slot typed so the cadence is met
   without pretending 90 new researched articles are possible.

Two decisions from Ninad on 2026-08-17 govern everything below. The niche is
documentation only, so `ai-memory-editorial-program.md` is superseded and the empty
`ai-memory` category is removed. And the calendar runs at one piece per day.

## Corpus reality

The repository holds 85 Markdown files. The site publishes 17. The rest are 52 retired,
15 in review, and 1 draft, and `build.py` emits only `status: published`.

Every published article resolves to the `technical-documentation` category. The
`ai-memory` category in `config.toml` matches zero published posts, yet `build.py` still
generates `/articles/ai-memory/` and lists it in `sitemap.xml`. That is a live indexable
page with no articles on it. Removing it is the first task in the calendar.

## Method, and its one real limit

Ahrefs Keywords Explorer supplied volume, difficulty, traffic potential, parent topic,
intent, and SERP features across 646 raw keyword rows. After removing branded and
off-vertical noise the working universe is 350 keywords. Of those, 145 return an
`ai_overview` SERP feature.

Ahrefs Brand Radar was the intended instrument for the AI-search half. It is not
available. Every data source returns `Missing addon: Brand Radar`, so there is no
citation, share-of-voice, or cited-domain data in this plan and nothing below should be
read as if there were. What replaced it is the `ai_overview` and `ai_overview_sitelink`
flag carried on every keyword row, which is a measured property of the live SERP, plus
free reads of the pages that currently rank. That is weaker evidence about assistant
behavior and stronger evidence about Google's AI surface. The distinction matters and the
AI-search section keeps it visible.

## Two findings that change the existing plan

### The llms.txt anchor rests on a number Ahrefs does not corroborate

`documentation-authority-plan.md` makes `llms.txt generator` a Month 5 anchor at 2,400
volume and KD 35. Ahrefs puts `llms.txt generator` at 300. The demand in this cluster sits
almost entirely on the definitional term: `llms.txt` at 3,100 and `what is llms.txt` at
1,800, both with parent topic `llms.txt`, meaning one page can own them.

The generator still deserves to exist, and one already ships at `/llms-txt-generator/`.
The correction is that it is a supporting asset, not the anchor. The anchor is the page
that owns `llms.txt` as a topic.

### Technical documentation examples is not a separate article

Ahrefs reports `technical documentation example` at 350 volume, KD 2, with parent topic
`technical documentation template`. `documentation example` at 250 has parent topic
`technical documentation example`. Google resolves all of it to the page that owns the
template query.

That page already exists and is published at `/articles/technical-documentation-template/`,
targeting a 500-volume KD 0 term. So Release 10 in the canonical plan, a standalone
Month 4 examples anchor, would compete with an asset already owned. It becomes an
expansion of the template page instead. This is the single highest-return move in the 90
days, because it adds roughly 600 monthly volume to a page that already ranks rather than
starting a new URL from zero.

## Keyword universe

Clusters are defined by Ahrefs parent topic, not by theme. A parent topic is Ahrefs'
statement about which single page Google already rewards for a group of queries, so it is
the correct unit for deciding what becomes an article.

Full row-level data is in `planning/research-cache/DERIVED-clean-universe.json`. The
prioritized subset with cannibalization boundaries is in
`planning/semrush-opportunity-backlog.csv`, extended from 7 rows to 26 in the original
14-column structure with the original seven untouched. Rows sourced this round carry
`us-ahrefs` in the `Database` column so the two difficulty scales are never silently mixed
with the Semrush originals. Remaining NEW slots draw their targets from
`DERIVED-clean-universe.json` and get a backlog row when their brief is written.

### Cluster A: Documentation foundations

| Parent topic | Combined vol | Best KD | AIO | Owning page |
|---|---:|---:|:--:|---|
| technical documentation | 3,220 | 12 | yes | NEW pillar |
| software documentation / what is software documentation | 1,640 | 7 | yes | NEW |
| good documentation practices | 700 | 6 | yes | NEW |
| technical documentation service | 650 | 0 | yes | existing `what-is-technical-documentation-and-what-should-it-include` |
| product documentation | 400 | 0 | yes | NEW |
| technical document | 400 | 7 | yes | section of the pillar |

`technical documentation` at KD 12 is the correction to the canonical plan's decision to
exclude the head term as ambiguous. Ahrefs' US read is 3,100 at KD 12 with parent topic
itself, which is attainable. The canonical plan excluded it on a 1.83M global figure.

### Cluster B: Templates and examples

| Parent topic | Combined vol | Best KD | AIO | Owning page |
|---|---:|---:|:--:|---|
| technical documentation template | 2,800 across 16 keywords | 0 | yes | existing `technical-documentation-template`, EXPAND |
| api documentation template | 350 | 1 | no | NEW |
| process documentation template | 1,070 | 1 | yes | out of ICP, excluded |

### Cluster C: API documentation, the largest gap

| Parent topic | Combined vol | Best KD | AIO | Owning page |
|---|---:|---:|:--:|---|
| api documentation | 4,670 across 6 keywords | 6 | yes | NEW anchor |
| api documentation example | 690 | 2 | yes | NEW |
| swagger (api documentation tools) | 860 | 7 | partial | NEW comparison |
| openai api documentation (api reference) | 350 | 2 | yes | NEW |

Zero published articles touch this cluster. It carries the most combined volume of any
group in the universe and the site has no page in it at all.

### Cluster D: Docs as code and tooling

| Parent topic | Combined vol | Best KD | AIO | Owning page |
|---|---:|---:|:--:|---|
| docs as code | 690 across 4 keywords | 5 | yes | NEW anchor |
| documentation tools | 1,400 across 11 | 2 | yes | NEW comparison |
| technical documentation software | 1,570 across 11 | 3 | yes | same page as above |

`documentation tools` and `technical documentation software` are reciprocal parents of
each other across the two datasets, which is Ahrefs saying one page should serve both.
Splitting them would be self-inflicted cannibalization.

### Cluster E: AI-ready documentation

| Parent topic | Combined vol | Best KD | AIO | Owning page |
|---|---:|---:|:--:|---|
| llms.txt | 6,200 across 6 keywords | 39 | yes | NEW anchor |
| llms.txt long tail, no SERP history | 8,760 across 53 keywords | n/a | n/a | see AI-search plan |
| semantic chunking | 350 | 5 | yes | NEW |
| code documentation ai | 350 | 7 | yes | NEW |
| ai documentation generator | 350 | 33 | yes | NEW |
| ai search optimization | 3,500 | 48 | yes | deferred, KD too high for 90 days |

### Cluster F: Formats and operations

| Parent topic | Combined vol | Best KD | AIO | Owning page |
|---|---:|---:|:--:|---|
| release notes | 5,550 | 4 | yes | existing `writing-release-notes-that-developers-trust`, EXPAND |
| code documentation | 600 | 20 | yes | NEW |
| product requirements document | 600 | 7 | yes | NEW |
| changelogs | 30 | 3 | no | existing `how-to-write-a-changelog-developers-actually-read` |
| instruction manual / user guide | 2,800 | 24 | yes | consumer-manual intent, excluded |

The release-notes finding matters. The published article targets `release notes best
practices` at 50 volume. Its parent topic is `release notes` at 5,500 volume, KD 18. The
page is aimed at a term worth a fraction of the topic it already covers.

## Cannibalization map

Every published URL, what it owns, what it must never repeat, and its disposition. This
is the authority for briefs. A brief may not assign a boundary that contradicts this table.

| URL | Owns | Must not repeat | Vol / KD | Action |
|---|---|---|---:|---|
| `/articles/technical-documentation-template/` | The template artifact, its page inventory, and worked examples of each document type | Definitions of technical documentation; the eight-type taxonomy | 500 / 0 | **EXPAND** to absorb `technical documentation example` and `documentation example` |
| `/articles/what-is-technical-documentation-and-what-should-it-include/` | The definition and the minimum viable documentation set | Templates; format selection; best-practice review criteria | 250 / 2 | **EXPAND** with software-documentation terms |
| `/articles/types-of-technical-documentation/` | Format selection across eight types plus agent instructions | Definitions; template contents; per-format how-to depth | 90 / 4 | **LEAVE**, add links |
| `/articles/technical-documentation-best-practices-tested-real-developer-docs/` | The tested review card and task/failure/limit/ownership criteria | Templates; definitions; SEO checks | 90 / 16 | **EXPAND** toward `good documentation practices` |
| `/articles/developer-onboarding-docs-what-works-what-doesnt/` | Onboarding path design and first safe change | General tutorial construction; style rules | 150 / 2 | **REWRITE** to target `developer onboarding documentation` in title and slug |
| `/articles/writing-release-notes-that-developers-trust/` | Upgrade risk, breaking changes, migration | Changelog structure and chronology | 50 / 4 | **EXPAND** to the `release notes` parent topic |
| `/articles/how-to-write-a-changelog-developers-actually-read/` | Chronological record, Keep a Changelog, SemVer | Release-note upgrade-risk framing | 30 / 3 | **LEAVE** |
| `/articles/seo-for-technical-documentation/` | Dependency-ordered technical SEO audit for docs sites | AI retrieval and llms.txt; content structure advice | n/a | **EXPAND** with an AI Overview section |
| `/articles/how-to-organize-a-documentation-site/` | Recovering drifted documentation, IA, URL decisions | Homepage routing; version routing | 0 / 0 | **MERGE** target, see below |
| `/articles/what-a-documentation-homepage-must-help-users-do/` | Homepage as routing interface, four reader routes | Whole-site IA; navigation labels in general | 0 | **MERGE** into organize-a-documentation-site |
| `/articles/how-to-write-task-based-documentation-headings/` | Heading construction from reader tasks | IA; homepage routes | 0 | **MERGE** into organize-a-documentation-site |
| `/articles/internal-vs-external-documentation/` | Placement decision and the split test | Definitions; types taxonomy | 0 | **LEAVE**, low volume but defensible and citable |
| `/articles/documentation-review-checklist-before-you-publish/` | Pre-publish review across accuracy, code, structure | Accessibility criteria; style-guide rules | 0 | **LEAVE** |
| `/articles/documentation-accessibility-checklist/` | Release-blocking accessibility failures | General review criteria | 30 | **LEAVE** |
| `/articles/documentation-style-guide-template/` | Terminology, code evidence, UI references, ownership | Review checklist; heading construction | 30 / 38 | **LEAVE** |
| `/articles/how-to-document-multiple-product-versions/` | Version states, canonicals, redirects, route audit | General IA; SEO audit | 10 | **LEAVE** |
| `/articles/how-to-write-a-technical-tutorial-that-actually-teaches/` | Tutorial construction and tested learning path | How-to guides; reference pages | 10 | **LEAVE** |

### The three-way IA overlap

`how-to-organize-a-documentation-site`, `what-a-documentation-homepage-must-help-users-do`,
and `how-to-write-task-based-documentation-headings` all answer "how should this
documentation be structured so a reader finds the right page." All three measure at or
near zero volume. They compete with each other for a query that barely exists.

Merge the homepage and headings articles into the organize article as sections, keep their
URLs alive with 301s, and target the combined page at documentation information
architecture. Two URLs disappear, one page gets three times the depth, and the site stops
splitting one weak signal three ways.

### The zero-volume weighting problem

Ahrefs returns zero or near-zero US volume for the terms behind seven of the 17 published
articles. That is not an argument to delete them. They are defensible, low-competition,
genuinely useful, and several are strong AI Overview candidates precisely because nobody
optimizes for them.

It is an argument that the published corpus cannot be the growth engine. Of the site's 17
articles, only four target terms above 90 volume. The 90 days have to add pages in
Clusters C, D, and E, where the volume actually is.

## AI-search plan

This is separate from the keyword plan and is not a restatement of it.

### What the data supports and what it does not

Of 350 clean keywords, 145 return an `ai_overview` SERP feature. That is a measured fact
about Google's AI surface. Without Brand Radar there is no data here about what ChatGPT,
Perplexity, or Claude cite, so no claim below asserts anything about assistant citations.
Where a tactic is a hypothesis it is labeled as one.

### AI Overview presence by cluster

Computed from `DERIVED-clean-universe.json`. Cluster assignment is by keyword pattern, so
counts differ slightly from the parent-topic grouping above.

| Cluster | Keywords | AIO-triggering | Share | Combined vol |
|---|---:|---:|---:|---:|
| Documentation foundations | 35 | 21 | 60% | 10,000 |
| Docs as code and tooling | 126 | 68 | 54% | 15,270 |
| Templates and examples | 78 | 30 | 38% | 8,650 |
| API documentation | 38 | 10 | 26% | 11,470 |
| AI-ready documentation | 73 | 16 | 22% | 23,480 |
| **All** | **350** | **145** | **41%** | **68,870** |

Documentation foundations and docs-as-code trigger AI Overviews most often, at 60% and
54%. Those are the clusters where ranking alone will not deliver the click, so the page
has to be written to be the thing the Overview quotes.

Note the inversion worth understanding: the AI-ready cluster has the *lowest* AI Overview
rate. That is because most of its long tail has no SERP history at all, which is the next
section.

### The queries with no SERP history

The llms.txt pull returned 53 keywords with volume but null difficulty, null parent topic,
and no SERP features, totalling 8,760 monthly volume. Ahrefs has volume for them and no
ranking data, which means they are too new or too conversational for a stable SERP.

Their shape is the tell. `should i create an llms.txt file?`, `llms.txt go on site root or
where?`, `will llms.txt file help your seo`, `what to do with llms.txt file`, `how to see
the llms.txt file of a website`, `ai.txt vs llms.txt`. These read as things typed into an
assistant, not into Google.

They should not become 53 pages. They become the section structure and FAQ blocks of the
llms.txt anchor and its implementation guide, each phrased as the question and answered
immediately beneath it. That is the cheapest available way to be the passage an assistant
retrieves, and it costs nothing beyond writing the page well.

### What makes a page citable

Applied to this site, in priority order:

1. **A self-contained answer directly under the heading.** A retrieved passage arrives
   without the page around it. Every H2 and H3 has to make sense alone. The published
   corpus already does this well and it is the strongest existing asset.
2. **Extractable claims with the evidence attached.** A sentence stating a fact with its
   source link in the same paragraph survives extraction. A claim supported three
   paragraphs later does not.
3. **Dated verification.** `updated` is set on 15 of 17 published posts; two lack it and
   are in the calendar to be fixed. Version-sensitive claims carry a last-verified date.
4. **Clear entity definitions.** This is the glossary's actual purpose. A term with a
   standalone definition at a stable URL is the most extractable unit a site can publish.
5. **Structured data.** `TechArticle`, `BreadcrumbList`, and `FAQPage` already emit from
   `templates/post.html`. The gap is that FAQ schema only appears when `faqs` frontmatter
   exists, and most posts have none.
6. **llms.txt.** Already shipping and already good, grouped by topic with descriptions.
   It is table stakes, not an advantage, and no page should claim it guarantees inclusion.

### Existing posts closest to citable, and what each needs

| Post | Already has | Needs |
|---|---|---|
| `technical-documentation-best-practices-tested-real-developer-docs` | Named sources checked live with status codes, task/failure/limit structure | `faqs` frontmatter; a dated verification line |
| `how-to-document-multiple-product-versions` | Decision table, canonical rules, Google source, downloadable audit | `faqs` frontmatter |
| `seo-for-technical-documentation` | Dependency-ordered checklist, primary Google sources | An AI Overview section; `faqs` |
| `what-a-documentation-homepage-must-help-users-do` | Five named homepages inspected, four reader routes | Merging into the IA page, then FAQ on the combined page |
| `types-of-technical-documentation` | Eight types with public examples, agent-instruction angle | `faqs`; glossary links on each type |
| `what-is-technical-documentation-and-what-should-it-include` | Direct definition, minimum viable set | `faqs`; glossary links |

Six posts need `faqs` frontmatter, which is a frontmatter edit rather than a rewrite, and
the schema then generates itself. That is scheduled as a single FIX slot.

### Measurement, free only

No recurring paid polling. Weekly, roughly 20 minutes:

- Search Console impressions and queries per page, and the query count per URL, which is
  the earliest signal that a page is being understood as a topic rather than a phrase.
- Manual AI Overview spot-check on ten fixed queries in a logged-out browser, recorded as
  present or absent and whether the site is cited. Same ten every week, dated, in a table.
- `python build.py`, `rule_checker.py`, and `unittest` on every publish. Baseline today is
  29 checker errors, all `rule-of-three`, and one environment-only test failure from a
  missing `rsvg-convert`.
- Monthly: re-read `output/llms.txt` and confirm every new page is grouped correctly.

Review windows stay as the canonical plan sets them at 14, 45, 90, and 180 days.

## The 90-day calendar

One piece per day, 2026-08-17 to 2026-11-14. Ninad confirmed the cadence after the quality
risk was raised, so this is built at one per day without hedging. What follows is the
honest accounting of where the risk sits.

### Slot types and the risk they carry

| Type | Slots | What it is | Risk |
|---|---:|---|---|
| NEW | 44 | A researched article against a real keyword | Highest. Each needs evidence gathered before its slot. |
| EXPAND | 12 | Substantial new sections on a published post | Low. The page and its evidence already exist. |
| REWRITE | 10 | A review-status post rebuilt to pass the gate | Medium. Source exists; claims need evidence. |
| GLOSSARY | 12 | One term definition at its own URL | Low. Short, bounded, high citability. |
| MERGE | 5 | Fold a post into another, redirect, verify | Low. Editorial, not generative. |
| FIX | 7 | Remediation batch, tracked as a shipped piece | Low. |

Forty-four new researched articles in 90 days is the real constraint, and it is why the
other 46 slots are deliberately not new articles. The anchor pieces in Clusters C, D, and
E need evidence gathered weeks ahead. Anchor research runs in parallel with publishing,
exactly as the canonical plan's tiering describes, and a slipped anchor is replaced by a
prepared GLOSSARY or FIX slot rather than by a thin article.

### Remediation folded into the calendar

The August audit's open items are assigned to specific days rather than left to slack:

- The wrong `text-embedding-3d-small` identifier in `embedding-models-compared.md` at
  lines 34 and 132. That post is retired, so the fix is cheap and is bundled into the
  first FIX slot.
- 31 hard-404 internal links across 16 unpublished posts. Triaged by target status, not
  bulk-rewritten: 14 point at published posts and are mechanical `/blog/` to `/articles/`
  rewrites, 19 point at review posts and resolve only as those posts ship or the link is
  cut, 12 point at retired posts and need deletion or replacement.
- 483 checker errors in unpublished source, being 410 paragraph-length and 73
  rule-of-three. These are cleared per-file inside each REWRITE slot, never in bulk.
- 29 rule-of-three errors in published source, cleared across two FIX slots.

### Weeks 1 to 13

The slot-by-slot table below is historical. Its matching CSV moved to
`planning/research-cache/content-queue-pre-hermes-2026-08-17.csv`; never use it to select or
schedule work. Active selection comes only from the guarded Hermes queue.

**Week 1, Aug 17 to 23. Fix the foundation before adding to it.**

| Date | Type | Piece |
|---|---|---|
| Aug 17 | FIX | Remove the empty `ai-memory` category, add the CTA and glossary plumbing, rebuild, confirm sitemap |
| Aug 18 | FIX | Link triage: rewrite the 14 published-target `/blog/` links, list the other 17 by required action |
| Aug 19 | EXPAND | `technical-documentation-template` absorbs `technical documentation example` |
| Aug 20 | NEW | API documentation anchor, the largest uncovered cluster |
| Aug 21 | GLOSSARY | `docs-as-code` |
| Aug 22 | NEW | Docs as code, working Git workflow |
| Aug 23 | MERGE | Fold homepage article into `how-to-organize-a-documentation-site`, 301 |

**Week 2, Aug 24 to 30. Open the API and AI-ready clusters.**

| Date | Type | Piece |
|---|---|---|
| Aug 24 | NEW | What is API documentation |
| Aug 25 | GLOSSARY | `llms-txt` |
| Aug 26 | NEW | llms.txt anchor, owning the 6,200-volume parent topic |
| Aug 27 | MERGE | Fold headings article into the IA page, 301 |
| Aug 28 | EXPAND | `writing-release-notes` to the `release notes` parent topic |
| Aug 29 | NEW | API documentation example, one complete endpoint |
| Aug 30 | FIX | Add `faqs` frontmatter to the six citability-ready posts |

**Weeks 3 to 5, Aug 31 to Sep 20.** API cluster completed: template, reference vs guides,
authentication, errors, pagination, webhooks, runnable code examples, tools comparison.
Interleaved with glossary terms for `api-reference`, `openapi`, `rag`, `context-window`,
and the first three REWRITE slots.

**Weeks 6 to 8, Sep 21 to Oct 11.** Docs-as-code operating system: tooling comparison,
example repository, CI testing, linting, link checking, preview deployments, versioning,
ownership, migration. Plus the `technical documentation` pillar and the
`software documentation` page.

**Weeks 9 to 11, Oct 12 to Nov 1.** AI-ready documentation: llms.txt implementation guide,
robots.txt for AI crawlers, AI-ready checklist, semantic chunking benchmark, chunking
strategies, metadata for docs RAG, documentation chatbot evaluation. The 53 no-SERP-history
queries become the section structure here.

**Weeks 12 to 13, Nov 2 to Nov 14.** Formats and measurement: code documentation,
requirements document, troubleshooting template, documentation metrics, plus the 45-day
review pass on everything shipped in weeks 1 to 5 and the remaining REWRITE slots.

## What would make this plan wrong

The cadence. Forty-four new researched articles in 90 days assumes the Codex writer works
from complete briefs and that anchor evidence is gathered ahead of its slot. If briefs
arrive thin, the output is 44 thin articles and the plan does active harm, because thin
pages on a small site dilute the topical signal that the 17 good ones have built.

The mitigation is in the brief format, not in the calendar. Every brief carries its
cannibalization boundary and its required evidence, and the publishing gate in the
canonical plan still applies without exception. A slot with no evidence ready is filled by
a glossary term or a fix, never by an article written to fill it.
