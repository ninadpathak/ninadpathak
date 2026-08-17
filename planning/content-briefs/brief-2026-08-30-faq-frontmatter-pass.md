# Brief: Add FAQ frontmatter to the six citability-ready posts

**Slot:** 2026-08-30 | **Type:** FIX

## Why this is a scheduled slot

`templates/post.html` already emits FAQPage schema, but only when a post carries `faqs`
frontmatter. Almost no post does, so the capability sits unused.

Of the clean keyword universe, 145 of 350 keywords return an AI Overview. Documentation
foundations trigger at 60%. FAQ schema is the cheapest structured signal available on
pages that already rank, and this is a frontmatter edit rather than a rewrite.

## The six posts, chosen because they are already closest to citable

| Post | Why it qualifies |
|---|---|
| `technical-documentation-best-practices-tested-real-developer-docs` | Named sources checked live with status codes |
| `how-to-document-multiple-product-versions` | Decision table, canonical rules, downloadable audit |
| `seo-for-technical-documentation` | Dependency-ordered checklist, primary Google sources |
| `types-of-technical-documentation` | Eight types with public examples |
| `what-is-technical-documentation-and-what-should-it-include` | Direct definition, minimum viable set |
| `how-to-organize-a-documentation-site` | Will hold three articles' research after the merges |

## How to write the questions

Draw them from question-shaped keywords that already resolve to that page's topic, in
`planning/research-cache/A6-matching-terms-questions-documentation.json`. Examples with
measured volume: `what is technical documentation` 250, `how to create technical
documentation` 150, `how to write technical documentation` 100.

Each answer must be self-contained and true on its own. An answer that only makes sense
after reading the article defeats the purpose.

## Also in this slot

`documentation-review-checklist-before-you-publish` and `how-to-organize-a-documentation-site`
have no explicit `updated` value, the only two published posts missing it. Verify their
claims first, then set it. Do not set a freshness date without doing the check, because
`build.py` already substitutes the publication date and a false `updated` is worse than none.

## Done when

- Six posts carry `faqs` and the FAQPage schema appears in their built HTML.
- Both missing `updated` values are set, after verification.
- `python build.py` passes and `rule_checker.py` shows no new errors.
