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
real inline comments, and a README. Those present-tense placements are the evidence.

Point at that. Explain the boundary he uses now: what belongs in a docstring, what the generated
reference can derive, and what needs a written guide. A current first-person judgment about his
own code is supportable. A historical claim such as "I moved this out" or a claim about why a
past decision was made needs a cited file revision, commit, issue, or other inspectable record.
If the history does not record the reason, describe the current choice and rationale without
inventing an event or past motivation.

Do not claim a client codebase, a team convention, a measurement he did not take, or a development
history that the repository does not show.

## Internal links, verified in the built sitemap 2026-08-17

Outbound, at least two:
- `/articles/technical-documentation-template/` — where the written-guide half lives
- `/articles/types-of-technical-documentation/` — reference versus explanation as document types

Inbound retrofit, required, and `tools/check_link_retrofit.py` blocks the publish without it:
- Edit `/articles/technical-writing-for-engineers/`. It is the same cluster and its reader is an
  engineer being asked to write. A sentence about what belongs in code rather than prose is the
  natural place. Keep the retrofit sentence factual and about the boundary; do not inherit or rely
  on any unsupported first-person anecdote already present on that page.

## Gate

`.venv/bin/python tools/check_link_retrofit.py --slug code-documentation` must exit 0.

Pre-grade this article before it can ship:

- **G1 — artifact:** no artifact is required. If research uncovers a genuinely useful one, it must
  test an external fact or reader input; a checker that merely accepts a fixture written to satisfy
  the same checker is a failure.
- **G2 — first person:** every first-person sentence must be either a present-tense, inspectable
  judgment about this repository or supported by a cited revision. Pipeline activity, client work,
  team conventions, durations, measurements, and unrecorded past motives are failures.
- **G3 — evidence ceremony:** do not add a command transcript, PASS string, screenshot, or receipt
  unless it helps the reader decide where documentation belongs. Research receipts stay private.
- **G4/G5 — shape:** compare the outline to the five-entry structure log. Do not reuse its opening
  move or skeleton, and do not add a stock objection section when the decision has no real objection.
- **G6 — linking:** keep the two subject-earned outbound destinations above and ship the required
  inbound retrofit in the same commit. A quota link or outbound-only result fails.
- **Heading and render:** use h3s only where they form real children of one h2 idea. After the build,
  pass the strict cluster, stylesheet, and structure audits, inspect relevant computed styles on the
  rendered page, and inspect a screenshot for layout. Add no CSS.
- **Claims and prose:** changed-page claim and rule-checker counts may not regress. The repository
  evidence must support the final wording, not merely the topic.
