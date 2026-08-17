# Brief: Code Documentation: Comments, Generated Reference, and External Guides

**Slot:** 2026-08-18 | Order 20 | **Type:** NEW anchor | **Cluster:** Documentation
**Experience: A** — first person required, and it points at his own repository.

## Keyword

| Field | Value |
|---|---|
| Primary | `code documentation` |
| Volume / Difficulty | 600 / KD 20 (Ahrefs, cached 2026-08-17) |
| Intent | Informational |
| Parent topic | itself. Verified by SERP on 2026-08-17: IBM, GitHub, Heretto, Codacy and a r/webdev thread all rank with pages dedicated to the term, not sections of something broader. |
| AI Overview | not returned on this SERP |

Secondary terms that belong here and get no separate URL: `code documentation best practices`,
`documenting code`. Row 29 owns the worked example, row 30 owns tooling.

## Reader task

Decide what belongs in a comment, what belongs in generated reference, and what belongs in a
written guide.

## Owns

The boundary between the three. The rule for deciding which one a given piece of knowledge goes in.

## Must not repeat

The worked module example (row 29, 2026-08-27). Tool selection (row 30, 2026-08-28). General
documentation structure, owned by the live `technical-documentation-template`. Writing craft for
engineers, owned by live `technical-writing-for-engineers`.

## Evidence — Experience A, no new artifact

Do **not** build a demo repository. The ground already exists and is inspectable: this site's own
Python codebase. `build.py`, `rule_checker.py`, `seo_audit.py` and `tools/` carry real docstrings,
real inline comments, and a README, and the decisions about what went where were made for real
reasons.

Point at that. Say what he puts in a docstring versus what he moved out into a written page, and
why. An opinion honestly held about his own code is not falsifiable in the damaging sense.

Do not claim a client codebase, a team convention, or a measurement he did not take.

## Internal links, verified in the built sitemap 2026-08-17

Outbound, at least two:
- `/articles/technical-documentation-template/` — where the written-guide half lives
- `/articles/types-of-technical-documentation/` — reference versus explanation as document types

Inbound retrofit, required, and `tools/check_link_retrofit.py` blocks the publish without it:
- Edit `/articles/technical-writing-for-engineers/`. It is the same cluster and its reader is an
  engineer being asked to write. A sentence about what belongs in code rather than prose is the
  natural place.

## Gate

`.venv/bin/python tools/check_link_retrofit.py --slug code-documentation` must exit 0.
