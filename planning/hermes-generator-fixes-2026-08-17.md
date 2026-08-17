# Hermes generator fixes, 2026-08-17

Driven by `planning/slop-review-2026-08-17.md` (PASS 0, REJECT 5) and Charter sections 2, 2b,
2c, 2c-bis, 2d, 2e. Edits are config and prompts on Phantom. No prose was written.

Backup stamp for every file touched: **`.bak.20260817T130105Z`**

## What was edited, and where

| Artefact | Paths |
|---|---|
| Daily publish prompt | `/root/.hermes/cron/prompts/ninadpathak-every-two-days-publish.md` |
| `ninadpathak-content` skill | canonical `/root/.hermes/skills/marketing/`, plus `profiles/research-desk/skills/marketing/` and `profiles/client-ops/skills/marketing/` |
| `devtools-blog-craft` skill | same three locations |
| Queue | `/root/.hermes/knowledge/ninadpathak/content-queue.csv` |
| Queue state guard | `/root/.hermes/scripts/ninadpathak_queue_state.py` |
| Structure log, new file | `/root/.hermes/knowledge/ninadpathak/published-structure-log.md` |

### Mirror drift, found and closed

The two mirrors were **two versions behind canonical**: `ninadpathak-content` was 1.4.2 against
canonical 1.4.4, and `devtools-blog-craft` differed by 11 lines. The mirrors were missing the
daily-cadence override, the `Skipped` state machine, and the DEV syndication section.

Editing three drifted copies independently would have preserved the drift. Canonical was edited,
then copied over both mirrors, so all three are now byte-identical. Verified by `md5sum`: two
distinct hashes, three files each.

### Schema change required a script change

`load_rows()` raises if the CSV header does not equal its `HEADERS` constant, and `save_rows()`
writes with `fieldnames=HEADERS`, dropping unknown columns. Adding `Experience` to the CSV alone
would have hard-failed the guard and stalled the next morning's publish. `HEADERS` was updated in
the same pass, with a comment explaining that the two must move together.

Verified end to end against a throwaway copy at `/tmp/qtest/q.csv`, never the live file: claim →
`save_rows` → 90 rows, 16 columns, `Experience` preserved through the write. The live queue is
still 15 Published, 4 Skipped, 71 Planned, and no lease was created.

## How the `Experience` column was judged

A **new** column, because `Tier` already means article weight (Anchor / Practical / Focused) and
repurposing it would have destroyed that signal. Populated for the 71 `Planned` rows only.
`Published` and `Skipped` rows are left blank deliberately: a retrospective value would imply a
judgement that was never applied when those pieces were written.

The rule used, in order of precedence:

**`A` — he has actually done it.** The ground is inspectable in his own work: this site's
repository and tooling, `/linter/`, the llms.txt generator, the build / lint / deploy pipeline,
its own `/blog/` to `/articles/` migration, its Search Console data. Or the writing craft that is
literally his profession, since a working technical writer has written tutorials, release notes,
changelogs, READMEs, briefs, and error copy. First person is required and points at that ground.

**`B` — he can genuinely do it in this run, and the result would carry information.** He does not
have the thing yet, but a template tested against a real target, a generator run on a real spec,
or a benchmark with published data would tell a reader something the article could not have
assumed. Artifact required, and it must pass the information test.

**`C` — it needs an event, product, organisation, or dataset he does not have.** Another company's
API internals, team ownership models, a production documentation chatbot, vendor tooling he does
not run. First person banned, researched explainer, no artifact.

Result of this first pass: **25 A, 24 B, 22 C** across the 71 Planned rows. The reweight in the
second half of this document revised it to **33 A, 22 B, 16 C**, and superseded several of the
row-level calls named below. Where the two disagree, the reweight section is current.

The deliberate calls worth naming:

- **Rows 22 to 25** (API authentication, errors, pagination, webhooks) are `C`, not `B`. He could
  build a sample API with auth and webhooks, but that artifact would be a toy testing values the
  same run chose. Charter 2b flags these four rows as dated and imminent, and under the old prompt
  each would have got a fixture-checker and a PASS screenshot. `C` defuses them at the source.
- **Rows 31 to 37, 39, 41, 42, 45** are `A` because this site *is* a docs-as-code implementation
  with real linting, a build gate, CI checks, a migration history, and a deploy. Hermes itself is
  the honest evidence for row 37, documentation automation, including its failures.
- **Row 61** (llms.txt generator) is `A`: he built it. **Row 64** ("What Is llms.txt, and What Is
  It Not?") is `C`, so the definitional page stays clean of first person and row 61 keeps the
  first-person ground.
- **Row 40** (Vale and Markdownlint) is `B`, not `A`. He built his own linter, not Vale, so the
  honest path is to run Vale in-run rather than imply prior use.
- **Row 60** (documenting error messages) is `A` because `rule_checker.py` emits graded error
  messages, which is a real artifact he owns.

## Cluster discipline per Charter 2c-bis

`Cluster` now holds one of the seven top-level niche clusters. The previous six documentation
groupings moved to a new `Subcluster` column so nothing was lost and the within-documentation
structure survives for planning.

Intermediate state, before the reweight below replaced it. Kept because the zero rows are the
finding that justified the reweight:

| Cluster | Rows, first pass | Rows, after reweight |
|---|---:|---:|
| Documentation | 60 | 18 |
| DevRel & DX | 15 | 3 |
| AI Engineering | 9 | 12 |
| AI Search | 6 | 6 |
| Reddit Marketing | 0 | 11 |
| Community Building | 0 | 10 |
| Events | 0 | 11 |

Rows 63 and 68 to 75 moved out of "AI-ready documentation" into **AI Engineering**, because
chunking, hybrid search, reranking, and chatbot architecture are retrieval engineering rather
than AI-search optimisation. The six llms.txt and AI-crawler rows stayed in **AI Search**.

**Finding that drove the reweight: three of the seven clusters had zero rows.** The queue could not grow Reddit marketing,
community building, or events because it contains nothing about them. The queue is fixed at 90
rows, so rather than adding rows, 32 existing Planned rows were repurposed into those clusters. See
the reweight section below.

Link scope is now `Cluster`, not `Subcluster`. A cross-cluster link is permitted only when the
connection is the subject of the sentence.

## Gate verification, replacing trust

Charter 2b: a gate that fails silently means others do too. Every gate that matters now prints
its result, and the prompt states that **a gate whose result is not in the run output is treated
as failed.**

The workspace cleanup gate was the known failure: six workspaces under
`/root/.cache/ninadpathak-article-runs/` survived a prompt that claimed to delete them. The
rewritten gate removes only the current run's workspace by lease attempt ID, prints the path and
verification result, prints `WORKSPACE CLEANUP FAILED` with a reason on failure, carries that line
into Delivery, and **reports pre-existing stale workspaces without deleting them**. Nothing was
deleted on the box; all six are still present and are evidence of the past failure.

Step 16 of the prompt is a printed self-audit checklist, one line per defect G1 to G6 plus the
title honesty result, and any `FAIL` blocks publication.

---

# Queue reweight, same session

Driven by `planning/addressable-universe.md` (branch `seo/analytics`, commit `506d4173`), which
prices the full niche at 336,180/mo across 1,129 keywords, 55% at KD<=20.

Weighted by **volume times winnability**, using each cluster's KD<=20 volume rather than its raw
volume, then adjusted for the four constraints given. All 71 `Planned` rows now carry one of the
seven cluster names and an honest `Experience` value. `Published` and `Skipped` rows were not
touched, and `Status` was never hand-edited.

## Allocation

| # | Cluster | KD<=20 vol/mo | Even split | Pure arithmetic | **Allocated** | Move |
|---:|---|---:|---:|---:|---:|---|
| 1 | Technical documentation & docs ops | 31,730 | 10 | 12 | **18** | up |
| 2 | Developer experience & DevRel | 7,190 | 10 | 3 | **3** | down hard |
| 3 | AI agents, memory, RAG, inference | 60,650 | 10 | 23 | **12** | down hard |
| 4 | AI Overviews & AI-search citation | 11,890 | 10 | 5 | **6** | flat |
| 5 | Reddit marketing | 28,970 | 10 | 11 | **11** | up vs even |
| 6 | Forums & community building | 18,440 | 10 | 7 | **10** | up |
| 7 | Technical & community events | 25,290 | 10 | 10 | **11** | up |
| | **Total** | **184,160** | 71 | 71 | **71** | |

Clusters 5, 6 and 7 take **32 of 71 rows, 45% of the calendar**.

## What moved and why

**Cluster 2 cut to 3 rows.** It is 3.9% of winnable volume and has nothing in the niche top 15.
It stays because it is real, but an even seventh would have been ten rows spent on the smallest
cluster in the universe. Rows 59, 60 and 79 keep their existing titles because README quality,
error-message copy, and writing a technical blog post for developers genuinely are developer
experience.

**Cluster 3 cut from 23 to 12, the largest single correction.** Pure arithmetic says 23 because it
is 33% of winnable volume, but three facts argue it down. Only 40% of its volume is KD<=20, the
worst of any cluster. 65% of its SERPs carry an AI Overview, the worst of any cluster. And the
freshly recovered corpus already ships **about 50 live AI-engineering articles**, so the cluster
has depth to build on rather than needing volume. Twelve rows spent on genuine gaps beats
twenty-three spent re-covering agent memory.

Rows 72 and 73 were rewritten because their planned titles duplicated live articles:
"Hybrid Search for Documentation" against live `hybrid-search-bm25-vector-search`, and "Reranking
Documentation Search Results" against live `reranking-in-rag-why-your-top-k-results-are-probably-wrong`.
They now carry tool-schema design and agent evals. Rows 76 to 78 became agent observability,
prompt injection, and circuit breakers. All five were requested by existing published posts and
never written, so they are demand-backed rather than invented.

**Clusters 5, 6 and 7 weighted up to 32 rows, from 30 empty ones.** Two reasons beyond volume.
Winnability: 87%, 76% and 77% of their keywords sit at KD<=20, against 50% for documentation and
40% for AI engineering. And they hit the 250-row API cap, so their recorded volumes are floors.

The decisive reason is `Experience`. **Sixteen of the 32 rows in these clusters are tier A**, where
first person is real and required. That is the point of widening the niche: an invented
documentation war story fails the falsifiability test, and his actual distribution work does not.
Rows where the piece needs a specific event he has not evidenced stayed `C`: the Reddit AMA, the
first meetup, the virtual event, hackathon documentation.

**Cluster 1 raised to 18 despite arithmetic saying 12**, because it is the commercial cluster tied
to the consulting offer. Rows 31 to 45 kept their titles unchanged: the docs-as-code block is
almost entirely tier A, since this site is itself a docs-as-code implementation. Row 46 was
rewritten because "Technical Documentation Examples" duplicated two already-published pieces.

## The whole API block was repurposed

Rows 20 to 30, eleven rows, became cluster 5. Four API articles shipped on `main` on 2026-08-17
and took the anchor, template, tools comparison, and examples teardown. Rows 22 to 25 were the
`C`-tier authentication, errors, pagination, and webhooks pieces that Charter 2b flagged as
imminent fixture-checker risks. Repurposing them removes that risk at the source and converts the
site's weakest planned block into its most winnable one.

Tomorrow's row 20 is now "How to Promote a Developer Tool on Reddit Without Getting Banned",
cluster 5, `Experience: A`, Anchor.

## Resulting Experience distribution

33 A, 22 B, 16 C across 71 Planned rows, against 25 A, 24 B, 22 C before the reweight. The rise in
A is not generosity: it is the direct consequence of moving 32 rows into clusters where he has
first-hand ground.

No new title collides with any of the 88 live article slugs. Checked exactly, and by shared-stem
near-miss; the two flagged pairs share only generic words.
