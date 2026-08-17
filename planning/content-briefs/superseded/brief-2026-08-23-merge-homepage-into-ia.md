# Brief: Merge the documentation homepage article into the IA page

**Slot:** 2026-08-23 | **Type:** MERGE
**Absorbing URL:** `/articles/how-to-organize-a-documentation-site/`
**Retiring URL:** `/articles/what-a-documentation-homepage-must-help-users-do/` (301 to the absorbing URL)

## Why

Three published articles answer the same underlying question, which is how documentation
should be structured so a reader finds the right page:

| URL | Ahrefs US volume |
|---|---:|
| `/articles/how-to-organize-a-documentation-site/` | 0 |
| `/articles/what-a-documentation-homepage-must-help-users-do/` | 0 |
| `/articles/how-to-write-task-based-documentation-headings/` | 0 |

All three measure at or near zero, and they split one weak signal three ways. Merging
gives one page three times the depth and stops the internal competition. The headings
article merges on 2026-08-27.

## What to keep

The homepage article is good and its research is real. It names five documentation
homepages that were inspected and derives four reader routes from them. Carry that in
whole, as a section, not a summary. Nothing about that research gets thrown away.

## Owns after the merge

Documentation information architecture end to end: site structure, homepage routing, and
the labels that let a reader predict a destination.

## Must not repeat

Version routing, which `/articles/how-to-document-multiple-product-versions/` owns.
Crawl and canonical mechanics, which `/articles/seo-for-technical-documentation/` owns.

## Mechanics, do not skip

1. Move the homepage sections into the absorbing article under their own H2s.
2. Set `status: retired` on `what-a-documentation-homepage-must-help-users-do.md`.
3. Add the 301 so the retiring URL resolves. Check how `build_redirects` emits
   `output/_redirects` before assuming the redirect exists.
4. Run `python build.py` and confirm the retiring URL is gone from `sitemap.xml` and the
   absorbing URL is still present.
5. Grep the corpus for links to the retiring slug and repoint them. This merge must not
   create the exact defect the 2026-08-18 slot is cleaning up.
6. Update `content/data/glossary.yaml`: the `information-architecture` term lists the
   retiring slug in `related_articles` and it must be removed, or the build will warn.

## Internal links on the combined page

- `/articles/types-of-technical-documentation/`
- `/articles/what-is-technical-documentation-and-what-should-it-include/`
- `/articles/how-to-document-multiple-product-versions/`

## Set on publish

`updated`, and add `faqs` frontmatter so the merged page emits FAQPage schema.
