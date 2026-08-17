# Brief: Merge the task-based headings article into the IA page

**Slot:** 2026-08-27 | **Type:** MERGE
**Absorbing URL:** `/articles/how-to-organize-a-documentation-site/`
**Retiring URL:** `/articles/how-to-write-task-based-documentation-headings/` (301 to the absorbing URL)

## Why

Second half of the three-way IA merge started on 2026-08-23. Ahrefs US volume for
`task based documentation` is 0. The heading-construction method is genuinely useful and
belongs inside the IA page, where labels and navigation are already the subject.

## What to keep

The rule connecting a heading to the job its section does, in full. It is the most
reusable idea in the article and it supports the retrieval argument: a heading that names
its section's job is also the heading that survives being retrieved without the page.

## Owns after the merge

Documentation information architecture: structure, homepage routing, and heading and label
construction. The merge is then complete.

## Must not repeat

Style and terminology rules, which `/articles/documentation-style-guide-template/` owns.
Review criteria, which `/articles/documentation-review-checklist-before-you-publish/` owns.

## Mechanics, same as the 2026-08-23 merge

1. Move the sections in under their own H2s.
2. Set `status: retired` on `how-to-write-task-based-documentation-headings.md`.
3. Confirm the 301 emits into `output/_redirects`.
4. Run `python build.py`, confirm the retiring URL leaves `sitemap.xml`.
5. Grep for internal links to the retiring slug and repoint them. Note that
   `/articles/what-a-documentation-homepage-must-help-users-do/` links to it in body text,
   and that content is now inside the absorbing page, so the link becomes a self-link and
   must be removed.
6. Update `content/data/glossary.yaml`: both `information-architecture` and
   `semantic-chunking` list this slug under `related_articles`. Remove it from both or the
   build will warn.

## After this slot

The IA page carries three articles' worth of research. Re-verify every external source in
the combined page before setting `updated`, rather than inheriting three separate
verification dates.
