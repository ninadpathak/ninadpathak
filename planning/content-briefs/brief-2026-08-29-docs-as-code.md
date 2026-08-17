# Brief: Docs as Code: A Working Git-Based Documentation Workflow

**Slot:** 2026-08-29 | Order 31 | **Type:** NEW anchor | **Cluster:** Documentation
**Experience: A** — the strongest A row in the fortnight.

## Keyword

| Field | Value |
|---|---|
| Primary | `docs as code` |
| Volume / Difficulty | 300 / KD 5 |
| Parent topic | itself |
| AI Overview | yes |

Absorbs `documentation as code` (250 / KD 12), `docs-as-code` (100 / KD 8), `what is docs as code`
(40 / KD 9). All four share the parent topic, so they get no separate URLs. Combined 690.

The docs-as-code and tooling cluster carries the second-highest AI Overview rate measured, at 54%.
This page has to be quotable, not only rankable.

## Reader task

Run documentation through branches, review, automated checks, and a deploy, and know which stage
catches which kind of defect.

## Owns

The end-to-end workflow.

## Must not repeat

Platform selection (row 32, next day). Maintenance cadence (row 33, the day after). Review criteria,
owned by live `documentation-review-checklist-before-you-publish`.

## Evidence — Experience A, and it is unusually strong here

**This site is a docs-as-code implementation.** Every stage exists and is inspectable:

- `rule_checker.py` enforces house style and exits non-zero, so a violating post cannot ship
- `build.py` runs an SEO audit at build time and fails the build on paragraph-length violations
- `tools/check_link_retrofit.py` blocks a publish whose internal links are one-directional
- CI runs the repository test suite after the build; report the publish run's actual pass/skip
  counts rather than copying a count from this brief
- `python build.py` regenerates `sitemap.xml` and `llms.txt` from source
- Cloudflare Pages deploys on push to `main`

Use it as the worked example **including what it does badly**. The honest material includes gates
that failed silently until they were made to print, which is a better story than a clean pipeline
and is recorded in repository history. Cite the workflow or commit that establishes any past
failure; do not reconstruct a historical incident from the current code alone.

Do not invent CI stages this repository does not have. Where a stage is recommended but absent
here, say so and show the config that would add it.

## Internal links

- `/articles/documentation-review-checklist-before-you-publish/`
- `/articles/technical-documentation-template/`
- `/articles/seo-for-technical-documentation/` for what the build-time audit checks

Inbound retrofit: `/articles/documentation-review-checklist-before-you-publish/`, same cluster,
and its reader is standing exactly where the automated half begins.
