# Phase B review evidence

Status: independent review accepted Phase B with no blockers; approved for this bounded publish.

Date: 2026-09-11. Base commit: `832808392d466da3981e291a37a682ef673bc2c8` on `main`.

## Scope and dispositions

Only these four articles were rewritten:

- `content/posts/developer-onboarding-docs-what-works-what-doesnt.md`
- `content/posts/documentation-review-checklist-before-you-publish.md`
- `content/posts/documentation-style-guide-template-for-developer-teams.md`
- `content/posts/how-to-organize-a-documentation-site.md`

The second-review visual correction also changes `static/css/main.css` and `static/css/visuals.css`. Global images now retain intrinsic aspect ratio, while only `.visual-container` elements that directly contain static images switch from the iframe height contract to content height.

Their four rows in `page-pov-audit.md` are `PROVISIONAL_REVIEW`, not editorially cleared. The page-level theses, opposing defaults, source use, removed claims, and exact claim dispositions are recorded in `source-and-claim-audit.md`.

No slug, canonical, or redirect changed. The title changes are recorded in the source audit. The built H1 and canonical for each article match its intended title and existing URL.

## Claim and voice checks

- Focused claim scan: 0 candidates across all 4 posts. Public style-guide prose ends naturally with "The downloadable template records those decisions." Authorship handling remains in this internal evidence record only.
- No invented first-person experience, client incident, metric, quote, internal result, role, or product-use claim was added.
- Every illustrative service, host, route, command, recovery branch, role, and response is labeled as illustrative or fictional before the reader encounters it. `example.com` and Orbit remain example material, not claimed live systems.
- The onboarding dependency contract reads the selected manager from `packageManager`, checks it with the matching manager command, and confines `corepack enable pnpm` / `corepack install` to a Corepack-managed example. The maintained Corepack README is the primary source.
- Repeated "passes when / fails when" verdict scaffolding, duplicate failure H3s, the style-guide mismatch restatement, and repetitive FAQ/checklist tails were removed. Organization now calls Guides, API reference, SDKs, release notes, and support "content routes," not product areas.
- First-person marker counts are 1 onboarding, 2 review, 2 style guide, and 5 organization. The rewrite did not erase judgment to satisfy a detector.
- Focused technical-writing rule check: 0 errors, 0 warnings, 2 informational results. The information results note the absence of an embedded visual in the review and style-guide articles; neither page needs a decorative fixture to carry its method.
- Banned-word and punctuation sweep: no hit for the selected deferral/slop terms, em dashes, or curly quotation marks.
- Heading audit: 0 issues across 4 published posts.

## Sources and links

Sixteen distinct Markdown-linked public sources returned HTTP 200 on the final check. They are primary product, project, or standards sources from Microsoft, GitLab, Google, W3C, Diataxis, AWS, and the maintained Corepack repository. The source audit maps each source to the claim it supports.

The fictional `api.orbit.example` and `example.com/checkout-api.git` strings occur only inside worked code samples. They are not citations or claimed live endpoints.

## Final validation

Run against the final intended tree:

- `python3 -m compileall -q build.py seo_audit.py tools tests`: passed.
- `python3 build.py`: passed; built 87 posts, 12 article focus areas, 5 case studies, 6 projects, and 23 glossary terms.
- Build-integrated SEO audit: passed; 141 HTML pages, 140 sitemap URLs, 140 unique canonicals.
- `python3 -m unittest discover -s tests -v`: 666 tests passed, 4 skipped, in 12.136 seconds.
- `python3 tools/audit_clusters.py --strict`: passed; 87 posts across 5 declared clusters, 0 undeclared, 0 without inbound links. It reports one pre-existing low-outbound page and 21 cross-cluster links for human judgment.
- `python3 tools/audit_stylesheets.py --strict`: passed.
- `python3 tools/audit_structure.py --strict`: passed with 0 structural problems.
- `python3 tools/audit_inert_css.py --strict`: passed with no inert declaration found.
- `python3 tools/content_inventory_gate.py --strict`: passed; 87 published articles and 87 audit rows. This gate checks inventory and mechanically interchangeable openings, not editorial truth.
- `python3 rule_checker.py --summary` on the four files: 0 errors, 0 warnings, 2 information results.
- `python3 tools/audit_headings.py --paths ...` on the four files: 0 issues across 4 posts.
- `python3 tools/audit_claims.py --paths ...` on the four files: 0 candidates across 0 of 4 posts.
- `python3 seo_audit.py`: passed; 141 HTML pages, 140 sitemap URLs, 140 unique canonicals.
- Sixteen linked-source requests: 16 HTTP 200, 0 failures.
- Playwright visual QA: 10/10 cases passed, split as 5/5 desktop and 5/5 mobile. The suite covers the four Phase B pages plus representative unaffected flowchart and iframe imagery.
- All 3 affected images reported `complete=true`. Microsoft and GitLab render at 670 x 376.875 desktop and 340 x 191.25 mobile from 1280 x 720 sources. AWS renders at 670 x 523.4375 desktop and 340 x 265.625 mobile from its 1280 x 1000 source. Rendered and natural ratios match within `0.01`; each full image bounding box fits its container, and container height matches image height within one pixel.
- Unaffected rendering checks: the responsive flowchart preserves its desktop and mobile source ratios and fits its `<picture>`; the iframe still fills a 670 x 400 desktop container and 340 x 500 mobile container.
- Mobile table assertions: 9 overflowing wrappers moved from `scrollLeft=0` to their measured maximums (3, 7, 32, 32, 73, 78, 123, 175, and 340 pixels); 7 other tables fit at 342 pixels and did not claim scrollability.
- `git diff --check`: passed.

The full-corpus claim scanner still reports 113 candidate claims across 49 of 87 published posts. Phase B does not certify the factual or editorial quality of the archive.

## Current renders

Thirty-three PNGs are under `visual/`: 4 full-page desktop renders, 4 clean mobile top viewports, 3 corrected decoded-image viewports, 18 before/after table viewports, and 4 representative unaffected-image viewports. Their dimensions, SHA-256 hashes, exact DOM assertions, capture method, and implementation-side inspection notes are in `visual/README.md`. All artifacts were inspected. The local server is stopped. Independent visual and public-content review remains required.

## Preservation and rollback

The staging area is empty. No commit, push, deployment, redirect, or publication occurred.

Pre-existing dirty planning, essay, URL-inventory, and video files were not edited by Phase B. Rollback should target only the four article files, their four audit-row changes, `static/css/main.css`, `static/css/visuals.css`, and `planning/research/opinionated-site-2026-09-11/phase-b/`; do not reset, stash, clean, or blanket-restore the checkout.
