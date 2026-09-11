# Zero recorded impressions: review-ready removal

Baseline: `309db0f9` on `main`. No commit, push, or deployment performed.

## Selection and limitations

The user asked to remove non-ranking articles, then selected the cohort Google recorded zero impressions for. A fresh read-only Search Console request to `sc-domain:ninadpathak.com`, web search, final data, page dimension, covers June 11 through September 8, 2026 inclusive (90 days). The API returned 203 page rows, below its requested 25,000-row limit, so no additional page was available. Raw requests and unmodified responses are in `gsc-page-raw.json`.

`cohort.json` records all 87 originally published sources, canonical slugs, source hashes, matching page rows, impressions, and dispositions. Matching combines canonical `/articles/` routes with legacy `/blog/` filename and slug forms, root forms, trailing-slash variants, and static redirect aliases. Query strings and hosts do not create false missing matches because comparison uses URL paths within the domain property. Independent root and reviewer checks reproduced the 20/67 split.

The selection means **zero recorded impressions in this window**, not that these pages never ranked, failed editorial review, or could never attract readers. Search Console reports observed data, not a quality verdict. Source publication dates bound possible observation; the two September 7 essays have only two eligible calendar days in this window, and that is not evidence of a failed content strategy. Recent article refreshes occurred after the reporting cutoff. They are included because the user selected this cohort, not because their refreshes were measured and rejected.

`collect.py` refuses to overwrite the baseline evidence. It must not be rerun to derive the original cohort from the now-reduced public folder. `verify.py` can be rerun and validates the current implementation against that immutable cohort.

## Dispositions

All 20 sources are moved byte-for-byte to `archived-posts/`, outside the generator's content search path. Their prior editorial notes are in `previous-editorial-dispositions.md`. The other 67 articles remain published at their existing URLs.

| Archived slug | Source publication date | Eligible calendar days through September 8 |
| --- | --- | --- |
| `ai-crawlers-robots-txt-training-vs-citation` | 2026-08-17 | 23 |
| `api-documentation-best-practices-reference-guides-and-working-requests` | 2026-08-14 | 26 |
| `api-documentation-examples-what-the-best-developer-portals-get-right` | 2026-08-15 | 25 |
| `api-documentation-template-the-pages-every-api-needs` | 2026-08-17 | 23 |
| `api-documentation-tools-hands-on-comparison-small-teams` | 2026-08-16 | 24 |
| `coding-agent-setup-that-works` | 2026-06-13 | 88 |
| `developer-trust-hierarchy` | 2026-04-10 | 90 |
| `documentation-style-guide-template` | 2026-08-07 | 33 |
| `how-to-document-multiple-product-versions` | 2026-08-12 | 28 |
| `how-to-find-the-right-subreddit-for-a-developer-product` | 2026-08-19 | 21 |
| `llms-txt-examples-real-files-audited` | 2026-08-17 | 23 |
| `mcp-server-setup-guide` | 2026-06-12 | 89 |
| `prompt-caching-what-it-is-and-when-the-math-works` | 2026-03-13 | 90 |
| `reddit-self-promotion-rules-read-properly` | 2026-08-20 | 20 |
| `technical-writing-examples` | 2026-07-29 | 42 |
| `technical-writing-is-deciding-what-the-reader-can-assume` | 2026-09-07 | 2 |
| `token-counting-isnt-optional-a-practical-guide-to-llm-cost-control` | 2026-03-22 | 90 |
| `what-a-documentation-homepage-must-help-users-do` | 2026-08-11 | 29 |
| `what-makes-a-page-extractable-by-answer-engines` | 2026-08-17 | 23 |
| `writing-ai-first-content` | 2026-09-07 | 2 |

## Implementation boundaries

- Removed incoming links to archived articles and dangling static aliases. Where a sentence only advertised the removed guide, removed that sentence; otherwise retained its substantive wording without the link.
- Restored contextual inbound links to four surviving articles whose only referring article was removed. Cluster checks still reject orphans; no gate was weakened.
- Kept downloads, tested fixtures, research, images, glossary terms, tools, work, projects, homepage design and copy unchanged except the necessary tool/glossary link cleanup. Latest-post listings naturally change with the source corpus.
- Preserved the existing AI Search and Citation and Reaching Developers category routes. They now show a truthful empty state, `noindex, follow`, and no sitemap entry. Only categories explicitly configured with `preserve_empty_route` do this; new empty categories still do not render. No unrelated blanket redirect was added.
- Updated the public POV register to 67 current rows and counts. The inventory gate is unmodified and is not editorial clearance.
- The historical GSC merge guard now recognizes only manifest-listed archived sources after verifying their source path, byte hash, and slug. It calls them `archived`, not `published`, while still requiring merge targets to be published. Digest tampering fails a regression test.
- CI writing/claim diffs exclude deleted paths using `--diff-filter=ACMR`; deleted files must not be passed to a parser as though they still exist. All surviving changed articles still receive the existing regression checks.

## Verification

`verification.json` and `check-00.log` onward record exact commands and outputs. The final suite ran 670 tests: 666 passed, 4 skipped, zero failures. This is the pre-existing 666-test suite plus four new category/archive tests, not a claim that all tests executed without skips.

Build: 67 articles; 120 generated HTML pages; 117 sitemap entries and unique indexable canonicals. The build's SEO audit checks rendered internal links, local static asset existence, canonical consistency, metadata, JSON-LD, and sitemap coverage. It passes with no broken internal links. All generated redirect destinations exist.

Strict inventory, cluster, stylesheet coverage, diagram structure, and inert CSS audits pass. The cluster audit has zero undeclared articles and zero orphans; five articles still have fewer than two body outbound links after removal, reported as advisory by the unchanged gate. Existing cross-cluster links remain human-review items, not automatic errors.

Changed-survivor writing regressions: 41 existing writing-rule errors before and after; 39 claim candidates before and after. Full surviving-corpus claim scan: 103 candidates across 41 of 67 articles. These are inherited review debt, not newly verified factual claims. This cleanup does not factually certify the remaining corpus.

`visual/manifest.json` records localhost HTTP checks: all 20 removed canonical routes return 404, all 67 retained routes return 200. It records eight desktop/mobile artifacts for the homepage, articles listing, and retained empty categories. Homepage/listing captures are top viewports; category captures are full page. All images were decoded before screenshots, with recorded natural dimensions. No horizontal page overflow. All eight artifacts were visually inspected. Capture uses reduced motion; it does not assert animation behavior changed or was tested.

Local HTTP checks use Python's static server; production's existing Cloudflare 404 page is not live-tested because nothing has been published. Generated removal routes and legacy aliases have no redirect to missing/unrelated destinations.

## Preservation, rollback, and cleanup

`protected-sha256.json` records the ten pre-existing dirty planning/video/essay files. Verification confirms they remain byte-identical. `intended-files.json` lists task-owned changes (plus this README and that manifest itself); no `output/`, dependency folder, or unrelated dirty file belongs in staging.

Rollback before publication: move any selected archived source back to its recorded `content/posts/` path using `apply_patch`, restore its prior POV row, restore only relevant links/aliases from the baseline diff, and rebuild. The original source hash in `cohort.json` proves recovery. Do not reset the checkout or overwrite protected dirty work. After a future commit, a scoped reverse commit can restore the whole batch without discarding unrelated changes.

The temporary headless browser closes itself in `finally`; the localhost server is stopped at handoff. Existing `/tmp/ninad-phase-b-playwright` dependencies are reused read-only and retained because they predated this task. No new dependency installation, tab, worktree, or permanent background process was created.

Independent reviewer `zero_impression_review` accepted this bounded diff with no blockers. Commit/push and publication remain pending explicit direction.
