# Article Citation-Readiness and AEO Audit

Audit date: 2026-08-13 (Asia/Kolkata)  
Repository: `/Users/ninad/Development/ninadpathak`  
Scope: local Git update followed by a read-only audit of published, review, and draft articles. No articles were edited, committed, pushed, or deployed.

## Executive summary

The checkout was clean and safe to update. It fast-forwarded by one commit from `620bfbcec72aef606beb85f063d465715e3a9d12` to `d59de3ca1c876681ac0473447fe28810b02f285f`; the final local and `origin/main` SHAs matched.

The repository contains 85 Markdown posts: 17 published, 15 in review, 1 draft, and 52 retired. The per-article audit covers the 33 active editorial items (published plus review/draft) and excludes explicitly retired posts from grading.

Overall grades:

- Pass: 17
- Needs improvement: 8
- Poor: 8

The 17 published articles are generally citation-ready and AEO-friendly: each has external sources and frontmatter takeaways, uses direct task-oriented structure, and is emitted through a crawler-readable semantic template. The main risk is the unpublished corpus. All 16 review/draft posts lack explicit update dates and takeaways, seven have no external source links, and all 16 contain internal `/blog/` links. Of the 45 such links, 14 resolve through generated redirects and 31 would hard-404: 19 target review posts and 12 target retired posts. The unpublished checker total is 483 errors: 410 paragraph-length violations plus 73 rule-of-three violations.

**Severity:** live-site risk is **low** because the 17 published posts have clean current routes and the build excludes the review/draft corpus. Release-readiness risk is **medium** because promoting the unpublished material without editorial remediation would expose dead links and unsupported or incorrect claims.

These qualities improve citation-readiness and discoverability, but formatting and schema do **not** guarantee that an LLM will cite a page.

## Git update result

### Pre-update safety inspection

- Working tree: clean
- Current branch: `main`
- Tracking branch: `origin/main`
- Remote: `origin https://github.com/ninadpathak/ninadpathak.git`
- Worktrees: one, at `/Users/ninad/Development/ninadpathak`
- Local SHA before fetch: `620bfbcec72aef606beb85f063d465715e3a9d12`
- Cached `origin/main` SHA before fetch: `620bfbcec72aef606beb85f063d465715e3a9d12`

### Fetch and fast-forward

`git fetch --prune origin` moved `origin/main` to `d59de3ca1c876681ac0473447fe28810b02f285f`. The local branch was behind by one commit, with `HEAD` confirmed as an ancestor of `origin/main` (`0` ahead, `1` behind). `git pull --ff-only origin main` then completed as a clean fast-forward.

### Final state

- Local SHA: `d59de3ca1c876681ac0473447fe28810b02f285f`
- `origin/main` SHA: `d59de3ca1c876681ac0473447fe28810b02f285f`
- Final branch state: `main...origin/main`
- Final working tree after the audit: clean

The only later authorized write is this audit report itself.

## Project instructions and article conventions

The project instructions say that published posts come from `content/posts/`, must use frontmatter, and are included only with `status: published` (`README.md:35-53`). Prose paragraphs are limited to two sentences, with the build stopping on violations (`README.md:55-56`). The voice should be personal where genuine, technically exact, relaxed rather than generic, and should open with a concrete tension and a short promise (`README.md:58-78`). Contrast-formula prose is explicitly discouraged (`README.md:80-82`).

The audit applied the director-supplied framework in addition to these repository rules:

- Answer-first, crawler-readable structure
- Natural user questions and long-tail task phrases in headings
- Clear semantic hierarchy and entities
- Sufficient research depth: why, methodology, tradeoffs, comparisons, examples, and credible sources
- Niche, defensible queries rather than broad unsupported topics
- Small, self-contained passages that can be cited without losing context
- Direct human readability without keyword stuffing
- Evidence, dates, transparent assumptions, and bounded claims
- Constructive treatment of criticism
- Freshness and update signals
- Tables and lists only where they clarify relationships or decisions
- No thin filler or generic AI prose

## Article inventory

| Status | Count | Included in per-article grading |
|---|---:|---|
| Published | 17 | Yes |
| Review | 15 | Yes |
| Draft | 1 | Yes |
| Retired | 52 | No |
| **Total** | **85** | **33 active items graded** |

## Per-article grades

### Published articles

| Grade | Article | Concise assessment and exact example |
|---|---|---|
| Pass | `content/posts/developer-onboarding-docs-what-works-what-doesnt.md` | Starts with the reader's safe first change (`:23`), then covers success checks, nearby recovery, ownership, a worked API example, and primary-source support such as Microsoft guidance (`:78`). |
| Pass | `content/posts/documentation-accessibility-checklist.md` | Release-oriented checklist with a sound automation/manual-testing boundary; Google accessibility guidance grounds the semantic-structure advice (`:38`) and WCAG is linked for exact criteria (`:89`). |
| Pass | `content/posts/documentation-review-checklist-before-you-publish.md` | Thick, staged methodology spanning page purpose, technical accuracy (`:44`), execution, accessibility, rendered output, ownership, automation, and a detailed worked example. |
| Pass | `content/posts/documentation-style-guide-template-for-developer-teams.md` | Answers a narrow template query directly (`:18`), ties rules to evidence and owners, and uses credible Google, GitLab, and Microsoft references (`:30`, `:76`). |
| Pass | `content/posts/how-to-document-multiple-product-versions.md` | Defensible niche topic with explicit supported/retired/historical distinctions, canonicalization tradeoffs grounded in Google guidance (`:36`), and a reproducible route-audit artifact. |
| Pass | `content/posts/how-to-organize-a-documentation-site.md` | Presents an answer-first recovery method (`:22`), reader routes, URL and navigation decisions, a worked migration, and semantic page-structure evidence (`:229`). |
| Pass | `content/posts/how-to-write-a-changelog-developers-actually-read.md` | Centers the upgrade decision (`:23`), connects entries to consequences and migration details, and grounds the structure in Keep a Changelog and Semantic Versioning (`:53`, `:90`). |
| Pass | `content/posts/how-to-write-a-technical-tutorial-that-actually-teaches.md` | Defines the reader and finish line (`:52`), builds a runnable path, includes failure and verification steps, and uses Diátaxis and Google audience guidance (`:31`, `:56`). |
| Pass | `content/posts/how-to-write-task-based-documentation-headings.md` | Focused long-tail query with a clear rule for matching headings to section jobs (`:29`), plus source-backed task/concept distinctions and semantic hierarchy (`:56`, `:72`). |
| Pass | `content/posts/internal-vs-external-documentation.md` | Answers the placement decision by reader task (`:19`), supplies a comparison, split cases, an audit template, ownership, and credible audience guidance (`:21`). |
| Pass | `content/posts/seo-for-technical-documentation.md` | Uses a dependency-ordered audit checklist (`:23`) and separates intent, discovery, crawling, indexing, canonicalization, page quality, performance, and measurement with primary Google sources (`:57`). |
| Pass | `content/posts/technical-documentation-best-practices-tested-real-developer-docs.md` | Short but evidence-dense: it identifies and checks FastAPI, Stripe, and GitHub source pages (`:17`), then organizes conclusions around task completion, recovery, limits, and ownership (`:21`). |
| Pass | `content/posts/technical-documentation-template.md` | Provides a downloadable template first (`:21`), explains page jobs and evidence requirements, validates the generated structure, and distinguishes source files from deployed output. |
| Pass | `content/posts/types-of-technical-documentation.md` | Establishes clear user, team, and agent audiences (`:18`), defines eight document types with concrete public examples, and treats agent instructions as an additional audience rather than a replacement. |
| Pass | `content/posts/what-a-documentation-homepage-must-help-users-do.md` | Narrow scope and strong information density: the opening states the homepage's job and identifies five inspected documentation homepages (`:15`), followed by four distinct reader routes (`:19`). |
| Pass | `content/posts/what-is-technical-documentation-and-what-should-it-include.md` | Direct definition followed by a minimum viable documentation package (`:19`, `:37`), clear document boundaries, a coverage audit, ownership, and update triggers. |
| Pass | `content/posts/writing-release-notes-that-developers-trust.md` | Separates release notes from changelogs (`:23`), puts upgrade risk first, explains tradeoffs and rollback limits, and includes a full breaking-SDK worked example with source support (`:36`). |

### Review and draft articles

| Grade | Article | Concise assessment and exact example |
|---|---|---|
| Poor | `content/posts/developer-trust-hierarchy.md` | The broad five-tier hierarchy and academic attributions have no source links (`:37`); absolute claims such as “Source code is the only source that cannot lie” are not defensible (`:50`). The “nonsense detector”/“marketing fluff” framing is more combative than constructive (`:26-28`). |
| Poor | `content/posts/embedding-models-compared.md` | Zero external sources despite numerous provider, benchmark, model, latency, and accuracy claims. The identifier is factually wrong in two places: `text-embedding-3d-small` at `:34` and `:132` must be `text-embedding-3-small`, the identifier used elsewhere in the repository and in official OpenAI documentation. Provider rankings and “industry standard” claims are also uncited (`:130-152`). This is the highest-priority factual correction. |
| Poor | `content/posts/engineering-velocity-documentation.md` | Stacks large causal percentages against broad publication links without claim-level evidence or methodology (`:9`). Further 19%, 70%, and 1500% claims are not transparently derived (`:18`, `:53`). |
| Needs improvement | `content/posts/from-engineer-to-technical-writer-what-i-kept-and-what-i-left-behind.md` | Useful first-person structure and several credible sources, but some references such as the Write the Docs survey are named without a link (`:78`), internal routes are stale (`:23`, `:50`, `:86`), and current paragraph rules block publication. |
| Needs improvement | `content/posts/how-anthropics-contextual-retrieval-changes-rag-architecture.md` | Strong niche analysis, direct benchmark framing, official source, appendix, tradeoffs, and implementation judgment (`:75`, `:97`). Publication is blocked by long paragraphs and obsolete `/blog/` links such as `:69`; the fast-moving claim set also lacks an update field. |
| Poor | `content/posts/how-stripes-technical-blog-became-a-competitive-moat.md` | Zero external source links despite relying on specific Stripe landing pages, articles, tooling, and a two-year rollout claim (`:21`, `:43-47`). Several causal “moat” conclusions remain assertions (`:117-119`). |
| Needs improvement | `content/posts/hybrid-search-bm25-vector-search.md` | Good formula, benchmark comparison, system differences, tuning tradeoffs, and nine external sources (`:35-58`). Legacy internal links such as `:98`, long paragraphs, and reliance on mixed-quality secondary material keep it from passing. |
| Poor | `content/posts/rag-evaluation-metrics-what-actually-matters.md` | Zero external sources for metric definitions, RAGAS behavior, or recommended ranges. Claimed production score ranges (`:59`) and operational thresholds (`:192-201`) need explicit methodology, sample context, and evidence. |
| Poor | `content/posts/reranking-in-rag-why-your-top-k-results-are-probably-wrong.md` | Zero external sources for architecture, provider, model, latency, and quality claims. Provider recommendations (`:122-128`) and categorical “Two stages, every time” advice (`:173`) require evidence and narrower assumptions. |
| Needs improvement | `content/posts/structured-outputs-llms-json-mode-function-calling.md` | Strong answer-first mechanism comparison and ten source links. However, exact provider/model claims need a dated freshness check, and a weak secondary source supports precise tool-use rankings (`:50`); benchmark methodology at `:24` is not documented. |
| Needs improvement | `content/posts/technical-content-as-a-moat-the-long-game-for-developer-tools.md` | Useful sourced examples and constructive strategy, but broad causal framing needs tighter qualification. Obsolete internal routes begin at `:33`, and current paragraph rules block publication. |
| Needs improvement | `content/posts/technical-writing-examples.md` | Thick, concrete inventory of 12 formats with real examples and a useful quality rubric. All six contextual article links use obsolete `/blog/` paths, including `:92`, `:128`, `:228`, and `:245`; it also lacks explicit freshness metadata and takeaways. |
| Needs improvement | `content/posts/technical-writing-for-ai-products-the-new-rules.md` | Well sourced, entity-rich, and clear about prompts, schemas, evals, versions, retrieval, and agent readers. Fast-moving provider guidance needs dated verification, four internal routes are stale (for example `:56`), and the draft does not meet paragraph conventions. |
| Poor | `content/posts/technical-writing-for-engineers.md` | Broad generic topic with zero external sources. The 80/20 framing is unsupported (`:13`), as are sweeping statements about why “most technical writing fails” and how readers behave (`:22-34`). |
| Poor | `content/posts/the-case-for-shorter-technical-documentation.md` | Research, study windows, NASA-TLX comparisons, and quantitative outcomes are described without source links, dates, samples, or methods (`:19-38`). The argument has useful tradeoffs but cannot support its empirical claims as written. |
| Needs improvement | `content/posts/why-devtools-startups-lose-deals-over-bad-docs.md` | Credible product examples and a defensible commercial query, but causal purchase/deal-loss claims need tighter qualification. Internal routes are obsolete at `:91` and `:104`, and current paragraph rules block publication. |

## Verified corpus counts and patterns

### Published corpus

- 17 articles
- 17/17 have at least one external source link
- 17/17 have frontmatter takeaways
- 15/17 have an explicit `updated` value
- 2/17 omit explicit `updated`: `documentation-review-checklist-before-you-publish.md` and `how-to-organize-a-documentation-site.md`

Published headings generally use natural task phrases rather than stuffing exact keywords. Literal question marks are uncommon, but the headings still map cleanly to natural user questions such as how to organize documentation, how to review a release, how to document versions, and where internal versus external documentation belongs. Tables and lists mostly encode comparisons, checklists, route inventories, or decision criteria rather than padding word count.

### Review/draft corpus

- 16 articles
- 7/16 have zero external source links
- 16/16 lack explicit `updated`
- 16/16 lack frontmatter takeaways
- 16/16 contain at least one obsolete `/blog/` internal link
- 45 obsolete `/blog/` links total
- 14/45 target published posts and resolve through generated legacy redirects
- 19/45 target review posts and have no generated redirect
- 12/45 target retired posts and have no generated redirect
- 31/45 therefore hard-404 under the current generated routes
- 483 checker errors across the unpublished set: 410 paragraph-length plus 73 rule-of-three
- 15/16 lack explicit slugs; the filename fallback is valid but less deliberate

The largest writing-quality gap is not literal heading syntax. It is claim discipline: broad theses, provider rankings, productivity percentages, benchmark thresholds, and behavioral claims frequently lack direct evidence, dated methodology, bounded applicability, or credible primary sources. Several openings also use generic or sweeping formulations such as “Every interaction…”, “Most technical writing fails…”, and “Technical documentation often…” rather than the repository's newer concrete-tension convention.

### Independent cross-review additions

#### Verified facts

- The 45-link breakdown was reproduced by parsing only relative Markdown links beginning `/blog/` in the 16 review/draft files and joining each target slug to its repository frontmatter status. It excludes legitimate external URLs containing `/blog/`. Representative evidence: a published target at `content/posts/technical-writing-examples.md:92`, a review target at `content/posts/developer-trust-hierarchy.md:74`, and a retired target at `content/posts/from-engineer-to-technical-writer-what-i-kept-and-what-i-left-behind.md:50`.
- `build.py:796-811` generates legacy `/blog/` redirects only for the posts passed to the published build. Its own comment at `build.py:799-801` explicitly permits removed URLs to return the real 404. Consequently, the 14 links to published targets redirect, while the 19 review-target and 12 retired-target links do not.
- The 31 hard-404 links are a release-readiness defect in unpublished source, not a current live-site defect: their source pages are not emitted by the normal published build.
- The unpublished checker count is 483, comprising exactly 410 `paragraph-length` errors and 73 `rule-of-three` errors. The paragraph rule is the build gate at `build.py:267-275`; fixing those 410 violations can unblock `build.py --drafts`, but it leaves the 73 standalone checker errors to resolve.
- `content/posts/embedding-models-compared.md:34` and `:132` both say `text-embedding-3d-small`. The repository uses `text-embedding-3-small` elsewhere, including `content/posts/how-memory-works-in-hyperagents.md:212` and `content/posts/rag-vs-memory.md:94`; [official OpenAI documentation](https://developers.openai.com/api/docs/models/text-embedding-3-small) also names the model `text-embedding-3-small`.

#### Editorial recommendations

- Do not bulk-rewrite all 45 links from `/blog/` to `/articles/`. Rewriting the 14 published-target links is mechanical. The 19 review-target links need the target published or the link removed/replaced. The 12 retired-target links require deletion, replacement with a live authoritative page, or an explicit decision to restore the retired content; rewriting their path would merely point to a missing `/articles/` page.
- Treat the two wrong embedding identifiers as the cheapest and highest-priority factual fix before broader prose work.
- Batch paragraph and rule-of-three remediation by file when revising unpublished prose, while retaining separate acceptance checks: the paragraph fixes govern draft buildability; both classes govern the standalone writing checker.

## Site/template audit

These findings are separate from article-writing findings.

### Checks that pass

- Article pages use semantic `<article>` and `<header>` elements (`templates/post.html:115-142`).
- Author identity is visible and linked with `rel="author"` (`templates/post.html:120`).
- Publication date is exposed in a semantic `<time>` element (`templates/post.html:122`).
- A distinct update date is visibly displayed when it differs from publication (`templates/post.html:123-126`).
- Article title and description are rendered as H1 and lead text (`templates/post.html:130-133`).
- Frontmatter takeaways become a self-contained “The short version” summary (`templates/post.html:146-155`).
- Markdown headings become a semantic table of contents (`templates/post.html:156-161`).
- Breadcrumb navigation and related article links are present (`templates/post.html:102-113`, `:169-180`).
- `TechArticle` JSON-LD exposes headline, description, word count, keywords, article section, author, publication date, modification date, publisher, and main entity (`templates/post.html:17-51`).
- FAQ and breadcrumb schema are generated where applicable (`templates/post.html:52-97`).
- Pages expose title, description, index/follow robots directives, Open Graph metadata, Twitter metadata, canonical URL, and RSS (`templates/base.html:20-55`).
- The SEO audit checks title, description, one canonical, one H1, canonical/OG agreement, JSON-LD validity, internal links, static assets, sitemap coverage, indexability, robots, and `llms.txt` (`seo_audit.py:100-180`).
- The isolated published build passed with 36 HTML pages, 35 sitemap URLs, and 35 unique indexable canonicals.

### Template/site improvements

- Every article uses the site favicon as its schema image (`templates/post.html:24`) and social preview image (`templates/base.html:32`, `:42`). Article-specific descriptive images would provide better page/entity context.
- Related articles are chosen by any shared tag and truncated to the first three matches (`build.py:525-530`). This is valid internal linking but can be less relevant than deliberate contextual recommendations.
- The builder substitutes publication date for modification date when `updated` is missing (`build.py:285`). This is technically valid but not evidence that content received a freshness review.
- Source links are present in body HTML, but the template has no dedicated references/provenance component. This is not mandatory; claim-level inline links are generally preferable, especially for small citation-friendly passages.

## Five highest-impact fixes

1. **Correct the wrong embedding model identifier first.** Replace `text-embedding-3d-small` with `text-embedding-3-small` at `content/posts/embedding-models-compared.md:34` and `:132`, then add an official source. This is a concrete factual defect in an otherwise unsourced article.

2. **Triage the 31 dead links by target status before any route rewrite.** The 19 review-target links need the target published or the link removed/replaced. The 12 retired-target links require an editorial deletion, replacement, or restoration decision. Only the 14 published-target links are safe mechanical `/blog/` to `/articles/` rewrites.

3. **Rework the eight Poor drafts around narrower, evidence-bearing claims.** Prioritize Developer Trust Hierarchy, Vector Embeddings, Engineering Velocity, Stripe's Blog Moat, RAG Evaluation Metrics, RAG Reranking, Technical Writing for Engineers, and Shorter Documentation. Replace universal rankings and causal claims with bounded questions, primary sources, explicit limitations, and claim-level methodology.

4. **Clear both unpublished checker classes, not only the draft-build gate.** Fix the 410 paragraph-length errors to unblock `build.py --drafts`, then clear the remaining 73 rule-of-three errors. Run both the standalone checker and the draft build before changing any status to published.

5. **Make freshness and contextual discovery deliberate.** Recheck fast-moving provider/model/API claims before adding `updated`; add article-specific social/schema images and replace tag-only related-post selection with intentional links. Separately clear the published writing checker's 29 rule-of-three errors and four warnings.

## Commands and validations run

### Git safety and update

```text
pwd
git status --short --branch
git branch --show-current
git remote -v
git branch -vv
git worktree list --porcelain
git rev-parse HEAD
git rev-parse --abbrev-ref --symbolic-full-name @{upstream}
git rev-parse @{upstream}
git fetch --prune origin
git merge-base --is-ancestor HEAD origin/main
git rev-list --left-right --count HEAD...origin/main
git pull --ff-only origin main
```

### Repository and content inspection

```text
rg --files (project instructions, content, templates, tests, configuration)
rg -n (metadata, schema, canonical, robots, author, dates, internal links)
frontmatter-based inventory and status counts
heading, word, source-link, internal-link, takeaways, and update-field counts
obsolete /blog/ route scan
```

### Validation results

- `.venv/bin/python rule_checker.py --summary`
  - Failed on the published set: 29 errors, 4 warnings, 9 informational findings.
  - All 29 published errors were the project's `rule-of-three` evidence rule.
  - Warnings: four banned sentence starters across two posts.
- Active-corpus rule aggregation
  - 33 active posts checked.
  - 512 errors, 19 warnings, 9 informational findings.
  - 410 paragraph-length errors across the 16 unpublished posts.
  - 102 rule-of-three errors across 24 active posts.
  - Unpublished-only total: 483 errors = 410 paragraph-length + 73 rule-of-three.
- Internal `/blog/` target-status classification
  - 45 relative internal links across all 16 unpublished posts.
  - 14 target published posts and resolve through generated redirects.
  - 19 target review posts and 12 target retired posts; these 31 have no generated redirect and hard-404.
- Isolated `python -m unittest discover -s tests -v`
  - 28 of 29 tests passed.
  - One failure was environment-only: `rsvg-convert` was not installed for deterministic PNG rendering in `test_cli_writes_svg_png_and_geometry_receipt`.
- Isolated `python build.py`
  - Passed.
  - Built 17 blog posts, six article focus areas, five case studies, and three projects.
  - SEO audit passed: 36 HTML pages, 35 sitemap URLs, 35 unique canonicals.
- Isolated `python build.py --drafts`
  - Failed immediately because `developer-trust-hierarchy.md` violates the two-sentence paragraph rule, confirming the review/draft corpus is not publication-ready under current project conventions.
- Final Git verification before this report was created
  - Working tree clean.
  - Local and `origin/main` both `d59de3ca1c876681ac0473447fe28810b02f285f`.

## Audit boundary

This was a local repository audit. It inspected the source links, source types, claim placement, dates, routes, generated output, templates, schema, and validation behavior. It did not independently reproduce every external benchmark or re-verify every linked web page's current content. High-risk claims identified above should receive that claim-level verification before publication.
