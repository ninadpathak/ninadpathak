# Brief: Expand the release notes article to its parent topic

**Slot:** 2026-08-28 | **Type:** EXPAND
**Target URL:** `/articles/writing-release-notes-that-developers-trust/` (published, keep the URL)

## Why

The published article targets `release notes best practices` at **50** volume, KD 4. Its
parent topic is `release notes` at **5,500** volume, KD 18.

The page is aimed at a term worth a fraction of the topic it already covers. The audit
graded it Pass, with a full breaking-SDK worked example and sourced support. The content
is strong and the targeting is narrow.

| Keyword | Volume | KD | Parent topic |
|---|---:|---:|---|
| release notes | 5,500 | 18 | release notes |
| release notes best practices | 50 | 4 | release notes |

AI Overview present on both.

## Reader task

Write release notes that let a developer decide whether to upgrade, and when not to.

## What to add

Broaden the entry point to the general query without diluting the specificity that made
the page good. The reader arriving on `release notes` needs the definition and the
structure before the upgrade-risk depth the page already has.

Do not rewrite the existing worked example. Add above and around it.

## Owns

Release notes end to end: what they are, structure, upgrade risk, breaking changes, and
migration guidance.

## Must not repeat

The chronological record and Keep a Changelog structure, which
`/articles/how-to-write-a-changelog-developers-actually-read/` owns. That boundary already
exists in the published text and must survive the expansion.

Version state and URL routing, which `/articles/how-to-document-multiple-product-versions/` owns.

## Evidence required

Re-verify the existing external sources and record the date. Any new claim about a real
product's release notes needs a live-checked link.

## Internal links, all verified in the built sitemap

- `/articles/how-to-write-a-changelog-developers-actually-read/`
- `/articles/how-to-document-multiple-product-versions/`
- `/articles/technical-documentation-best-practices-tested-real-developer-docs/`

## On publish

Set `updated`. Add `faqs` frontmatter. Consider whether the title should carry the broader
term, but do not change the slug: the URL is published and has equity.
