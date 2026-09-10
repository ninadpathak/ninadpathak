# Essay rewrite — accepted; publication validation in progress

Title: Before You Ask an Expert
Canonical path: /articles/ai-before-expert-interviews/
Essay: content/posts/writing-with-ai-before-you-know-what-you-think.md
Body: 615 words. Filename retained intentionally; public slug comes from frontmatter.

The opening uses the user's conditional seven-years-ago frame. One explicitly hypothetical documentation assignment connects SEO research to AI preparation, expert disagreement, and evidence. No actual interview, quote, or result is claimed. Tutorial code and mechanical headings were removed.

## Changed files owned by this turn

- content/posts/writing-with-ai-before-you-know-what-you-think.md — complete rewrite, title, description, slug.
- content/posts/documentation-review-checklist-before-you-publish.md — one referring paragraph updated to the new argument and URL.
- templates/index.html — essay link, label, and description.
- static/_redirects — old /articles/ URL with and without trailing slash redirects directly to the new URL with 301.
- planning/research/essay-rewrite-2026-09-10/handoff.md — this handoff.
- planning/research/essay-rewrite-2026-09-10/preserved-files.json — SHA-256 snapshot of 54 initially dirty/untracked files, all unchanged after validation.

## Validation

Called SiteBuilder.build() using the repository virtual environment, with output redirected to a fresh temporary directory to preserve existing output/. Ran seo_audit.main() against that directory: PASS, 141 HTML pages, 140 sitemap URLs, 140 unique canonicals.

Additional assertions passed: exactly one direct 301 per legacy /articles/ and /blog/ route, with and without trailing slash; new self-canonical and title; no old generated article; no old article URLs in generated HTML; new URL and no old slug in sitemap, feed, and llms.txt. Existing build.py automatically preserves legacy /blog/ routes from the retained filename. git diff --check passed. Essay banned-word scan passed. The first draft overused conditional narration; the revised draft keeps the conditional opening and develops the hypothetical in direct present. No formatter used.

The given live page was fetched with curl after web fetch failed; its title and opening matched the local baseline. No new technical factual claims requiring external citations were added.

## Review and publication

Root and independent reviewer accepted the final 615-word essay in the preceding turn (user confirms acceptance). The user subsequently rejected the short slug before any commit or push. The authorized canonical is now /articles/ai-before-expert-interviews/; title and accepted prose are unchanged. The unused ai-better-questions URL was never published and needs no alias.

Push to main and established Cloudflare deployment are authorized. Exact staged-tree validation is in progress, excluding all unrelated article refreshes, static/examples, and dirty planning/video work. Publication status will be recorded only after exact-SHA deployment and live checks succeed.

The old run-owned preview /var/folders/8m/mzbx3_8d5xx9bfq8lqn7kpr00000gn/T/essay-rewrite-build-n8i8f1k7/site can be removed after delivery.

## Exact publication-tree validation

Validated an isolated export from a temporary Git index based on d83ac73f039dc14f9824f00287c719f29bf8be88 containing only this turn's four source files and evidence. No unrelated working-tree content was copied into the build. Python compilation, build including SEO audit, and all 666 regression tests passed (4 environment-dependent skips). All four CI strict audits passed: clusters, stylesheets, structural diversity, inert CSS. Changed-post writing errors remain 4 → 4; claim candidates remain 0 → 0. Canonical, title, first paragraph, homepage link, feeds, and four direct 301 routes passed assertions for ai-before-expert-interviews.

All 54 excluded dirty/untracked files were copied to a run-owned temporary backup and SHA-256 checked unchanged; publish-preserved-files.json records the snapshot. No unrelated refresh, static/examples, or planning/video change is staged.
