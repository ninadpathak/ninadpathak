# Article-specific work notes

Baseline: `60909b2c`. Scope: the 67 remaining published articles, one short contextual work note per article; original body, title, description, dates, canonical, code and assets stay unchanged. Drafts and the 20 archived sources are outside this change.

## Reference and editorial choices

User request: "push. Also for all articles, I want to add a short paragraph right before the intro related to my work. If you read Fly.io blogs, you'll see they have this tiny paragraph for what fly.io does. It's unique for every article, never the same. It only serves to build the context or as a little bit of custom advertisement per article."

Read Fly's [WireGuard article](https://fly.io/blog/our-user-mode-wireguard-year/), [Postgres article](https://fly.io/blog/how-we-built-fly-postgres/), and [agent customers article](https://fly.io/blog/fuckin-robots/). Their introductory product paragraphs name what Fly offers through the subject of that article and give a direct invitation before the body begins. WireGuard's source uses a separate `div.lead`. No wording is copied. The implementation here uses a modest paragraph, not a large CTA card.

The technical-writing skill and the site's editorial constitution guided the work: name the mechanism, remove sentences announcing their own importance, and preserve a specific reason to read. This is advertising for strategy, documentation, and developer education, not an offer to implement or operate customers' AI infrastructure. No claim of guaranteed business results or client metrics is added.

All 67 openings and heading paths were read, plus relevant body sections and the homepage/portfolio offerings. `note-review-map.json` maps each note to its article decision and writing-service purpose. This is a review of the added notes, not factual clearance of the inherited article bodies.

The first draft had too uniform a two-sentence situation/service pattern. Independent review flagged that corpus-level rhythm. The revision changes 45 notes, including direct service offers, product questions, launch situations and concrete deliverables. Overlapping memory articles now distinguish a coding integration, record-version restoration, and search-led customer education. Length and uniqueness checks are only guardrails; they do not certify semantic variety.

The Mem0 and Firecrawl relationships are user-confirmed in this conversation and recorded in `planning/editorial/constitution.md`. A draft reference to specific authorship was replaced with the confirmed relationship plus an offer: public bylines can differ from portfolio attribution, so the note does not use the artifact as proof of authorship.

## Implementation

Each published source owns a `work_note` frontmatter field. The renderer accepts one plain paragraph and one Markdown link to `/portfolio/` or `/contact/`; it escapes text and labels and rejects other destinations or multiple links. Absent fields remain supported for drafts and legacy fixtures. Notes are outside article body/TOC/reading-time metadata, immediately before `.post-content`, after the existing summary and contents. The original first-paragraph styling remains intact.

The shared main stylesheet adds only scoped `.article-work-note` rules. Its URL is cache-busted so an existing browser cache cannot hide the new styling. Homepage layout, image rules, matrix animation and logo reel are untouched.

## Verification and review

`checks.json` and `check-00.log` through `check-08.log` record the final current-tree commands. Regression logs remove trailing spaces from printed excerpts so committed evidence passes diff whitespace checks; findings and exit codes are unchanged. The full suite ran 677 tests: 673 passed, four skipped, no failures. This adds seven work-note tests to the 670-test baseline. The build passes SEO checks across 120 HTML pages, 117 sitemap URLs and 117 unique indexable canonicals. Strict inventory, cluster, stylesheet, diagram structure and inert-CSS gates pass, as does `git diff --check`.

`verification.json` proves 67 unique notes and byte-identical original bodies/metadata after removing only the new field. All draft sources, 20 archives and ten protected dirty files remain unchanged. The notes range from 20 to 36 words after link markup is removed; this is an observed range, not a writing target. Regression scans remain at 151 existing writing-rule findings and 103 existing claim candidates before and after. Those inherited findings are not cleared by this work.

`visual/manifest.json` records 22 current viewport artifacts: eight representative articles at desktop/mobile in dark mode, two of those articles at both sizes in light mode, and the unchanged homepage at both sizes. The article captures center the added note and original opening instead of attempting long-page stitches. Browser assertions cover placement immediately before original content, a single underlined/focusable internal link, actual paragraph font size of 15px, note bounds, and no note overflow. Visible article images decode before capture. All 22 artifacts were visually inspected. Capture uses reduced motion: the existing homepage logo reel therefore wraps and the matrix is still, rather than asserting their animation changed. The HyperAgents animated illustration remains its existing clipped orbital composition; its image/iframe rules were not changed.

Initial focused tests exposed a Python 3.9 annotation incompatibility; removing that unsupported annotation fixed it before the build. Initial renders exposed the global paragraph size overriding the note's intended smaller size; scoped paragraph inheritance fixed it, and the browser check now measures the paragraph itself. All current captures were regenerated after those fixes and the final relationship-copy tightening. The final capture process exited zero and recorded browser disconnection; the local HTTP server was stopped afterward. Independent reviewer `zero_impression_review` accepted the final 67-note corpus and current 15px renders with no blockers; root accepted and authorized publication. Acceptance applies to the exact added notes in `note-review-map.json` and source hashes in `verification.json`, not to the pre-existing article claims.

## Rollback and cleanup

Before commit, `validate-staged.py` exported the exact Git index into a disposable directory and reran the build, all 677 tests and five strict gates without the user-owned dirty planning files. All passed. `staged-validation.json` records that tree and the exact commands; `staged-00.log` through `staged-06.log` contain the results. The exported tree was removed afterward. These generated evidence files and the updated allowlist were staged after validation; no public source or test code changed afterward.

Remove only the new work-note fields and renderer/template/styles/tests from this change, or reverse its eventual commit. Do not reset the checkout. The previous removal commit remains intact, and the archived sources stay recoverable there. No publication until root relays independent acceptance. Temporary browser/server processes are stopped at handoff; existing Playwright dependencies remain untouched.
