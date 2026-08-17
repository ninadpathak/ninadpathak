# Brief: Docs as Code, a working Git-based documentation workflow

**Slot:** 2026-08-22 | **Type:** NEW (anchor) | **Proposed slug:** `docs-as-code`

## Keyword data

| Field | Value |
|---|---|
| Primary keyword | docs as code |
| Volume / Difficulty | 300 / 5 |
| Combined family volume | 690 across 4 keywords |
| Parent topic | docs as code |
| Intent | Informational |
| AI Overview | Yes |

The docs-as-code and tooling cluster has the second-highest AI Overview rate in the
universe at 54%, so this page has to be quotable, not only rankable.

## Reader task

Run documentation through branches, review, automated checks, and a deploy, and know which
part catches which kind of defect.

## Owns

The end-to-end workflow, and it absorbs `documentation as code`, `docs-as-code`, and
`what is docs as code`. Those get no separate URL.

## Must not repeat

Platform and tool selection, which the documentation-software comparison owns. Review
criteria, which `/articles/documentation-review-checklist-before-you-publish/` owns. Style
rules, which `/articles/documentation-style-guide-template/` owns.

## Evidence required

This site is itself a docs-as-code implementation and is the strongest available artifact.
It has a Python generator, a writing linter that gates publication, a build-time SEO audit,
a test suite, and Cloudflare Pages deployment.

Use it as the worked example, including what it does badly. Real, inspectable material
available today:

- `rule_checker.py` enforces house style and exits non-zero, so a violating post cannot ship
- `build.py` runs an SEO audit at build time and fails the build on paragraph-length violations
- `tests/` currently passes 28 of 29, with one failure caused by a missing system binary
- `python build.py` regenerates `sitemap.xml` and `llms.txt` from source

Do not invent CI stages the repository does not have. If a stage is recommended but not
implemented here, say so plainly and show the config that would add it.

## Internal links, all verified in the built sitemap

- `/articles/documentation-review-checklist-before-you-publish/` for the human review pass
- `/articles/documentation-style-guide-template/` for what the linter should enforce
- `/articles/technical-documentation-template/` for the source structure being versioned
- `/articles/seo-for-technical-documentation/` for what the build-time audit checks

## Links blocked until published

- The `docs-as-code` glossary term, which ships 2026-08-21. Safe to link if that slot lands first.
