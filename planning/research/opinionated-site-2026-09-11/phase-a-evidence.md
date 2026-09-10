# Phase A implementation evidence

Status: Phase A is review-ready. Current desktop/mobile Chromium artifacts are available for independent visual review; independent acceptance remains pending. No commit, push, deployment, or external publication occurred.

Root content check applied: the homepage hero preserves Ninad's two governing sentences with spelling and plural grammar edits. The constitution holds the raw quote exactly, and About now carries the raw conviction with only the spelling correction.

The exact current tree passed the full build, SEO audit, all 666 tests, four strict audits, the structural content-inventory gate, refreshed-article checks, fixture validation, and diff hygiene.

## Repository and ownership

- Checkout: `/Users/ninad/Development/ninadpathak`
- Base: `main` at `6ff1f4d7cf700dbe03a177b4b7324bae36248a3d`
- Staging area remained empty.
- One writer owned the checkout for this phase.
- No reset, stash, checkout, clean, blanket add, commit, push, or deploy ran.

## Delivered surfaces

- Editorial constitution: `planning/editorial/constitution.md`
- Complete POV register: `page-pov-audit.md`, covering 87 published articles, 23 glossary terms, five work pages, five categories, five standalone tools, legal pages, shared listings, and core pages
- Evidence/interview queue: `interview-backlog.md`
- Title and slug recommendation register: `title-slug-register.md`
- Structural inventory/opening-reuse guard: `tools/content_inventory_gate.py`, wired into `.github/workflows/quality.yml`. It cannot approve semantics.
- Core copy: homepage, About, Work, Portfolio, Projects, Contact, Articles, glossary index, footer, category archives, and site metadata
- Technical-documentation batch: tutorial, documentation template, and examples refreshes
- Work pages: removed eleven anonymous or role-only quotations pending provenance; retained the named Roman Hresko quotation. Removal does not establish that a quotation was fabricated.

## Corpus disposition

- `PHASE_A_EDITED`: 3 articles awaiting independent review
- `EVIDENCE_REQUIRED`: 50 articles containing 114 automated provenance candidates
- `PROVISIONAL_REVIEW`: 33 articles with no automated candidate and no human clearance
- `REWRITE_BATCH`: 1 article with a recorded structural/voice problem and no automated provenance candidate
- Total: 87 of 87 published articles

The register does not pretend the backlog was rewritten. It names the next action for each page and keeps evidence-dependent stories out of public edits.

## Verification

The current worktree passed:

```text
python3 -m compileall -q build.py check_rules.py rule_checker.py seo_audit.py tools/content_inventory_gate.py tests
python3 build.py
  87 blog posts
  12 article focus areas
  5 work pages
  6 projects
  23 glossary terms
SEO audit passed: 141 HTML pages, 140 sitemap URLs, 140 unique canonicals

python3 -m unittest discover -s tests -v
Ran 666 tests in 12.096s
OK (skipped=4)

python3 tools/audit_clusters.py --strict
python3 tools/audit_stylesheets.py --strict
python3 tools/audit_structure.py --strict
python3 tools/audit_inert_css.py --strict
All four strict audits passed.

python3 tools/content_inventory_gate.py --strict
Content inventory: 87 published articles, 87 audit rows
Human editorial review remains separate; this command does not approve thesis, evidence, or point of view
PASS: inventory is complete and no mechanically interchangeable opening was found

python3 rule_checker.py --summary <three refreshed articles>
TOTAL: 0 errors, 8 warnings, 3 info

python3 tools/audit_claims.py --paths <three refreshed articles>
0 candidate claims across 0 of 3 published posts

node static/examples/writing-lab/check.mjs
PASS

git diff --check
PASS
```

The fixture check reconfirmed signature success and rejection paths, dropped-response recovery, body limits, replay behavior, and clean new-instance state.

## Preservation

The following protected files matched their pre-work SHA-256 values after implementation:

- `planning/attribution.md`: `d402e87c69461808be0e10b9c35615f27ca95628450957b1129594396a8c13b7`
- `planning/daily-cycle.md`: `6f7abc81a7089a974b03d44abfe0226b1c9695ca2b685e7d2e0e673df1f4e992`
- `planning/leading-indicators.md`: `d6ac7442bad392d256f079e93102674b2dc35981228ed70ba728d7e52f9426f3`
- `planning/position.md`: `74e58180decc0f62fd2f1ca96fa819bb036bac890b7b3ff22e7a8ca2e00164f6`
- `planning/scoreboard.md`: `293c87cb524427f2d539548e3c1e8ea3a65b3a0373d56e3c67210535fc711879`
- `planning/url-inventory.json`: `db2f73bdfbd0357d66f07cf7a59098533f6cf99be34e704e76958fd327f6fc0a`
- `planning/video/brief-001.md`: `2950375a3786b808f6d99972d593cfc381b2532768d90d955bc0b14e0dc858a4`
- `planning/video/review-001.md`: `4dc865a971f037ab055e09bfa56df058e81b66381d946facfe6693b363329467`
- `planning/research/essay-rewrite-2026-09-10/handoff.md`: `847eb7ea89adeb2747eb595bf25af7592505a68d3a182d64496abb46e0ac91bf`
- `planning/research/essay-rewrite-2026-09-10/publication.json`: `ba1eb95b16c34ecd23c79e2f846dee52b668e8ad25033204ab3344033f2cae2c`

The reviewed writing-lab fixture also matched its pre-work hashes, including:

- archive: `b0def6b4e253d69e6f041294460af05bdd4fc8d8287de41d8221b96d001201e1`
- validation record: `e06862a863b1550a82c2ca4f74a6ce188ed0e8200b52e4e8b43fd59912ae9f4d`
- checks: `fe1fff7b3a66ddb9a55b84161ec2be0ed7d505fba4edda70c5d209b110502e21`
- service: `2828372f3b598dccb543f1cccc43709ebf610b95575c0a852a508b1cc5d374ef`
- webhook: `bd658bc3395002a75221af551577ea786be6271b4159bc1be6d759d306ae2d85`

## Canonicals and redirects

- No slug or canonical changed.
- `writing-ai-first-content` remains the canonical slug for "Before You Ask an Expert."
- Existing direct redirects to that canonical remain byte-unchanged.
- No redirect was added, removed, or edited.

## Current render artifacts

The screenshots under `writing-refresh-2026-09-10` predate this Phase A copy pass and remain excluded from current-render acceptance evidence.

Fresh full-page renders of `/`, `/about/`, `/work/`, `/articles/`, and the three refreshed articles are under `visual/`. Each route has a 1440-pixel desktop capture and a 390-pixel mobile capture, for fourteen PNGs total. The artifacts were captured from the exact current build served on localhost with a fresh headless Playwright/Chromium session. The server was stopped afterward.

Implementation-side inspection found no clipping, overlap, broken navigation, collapsed tables, or unreadable code blocks in the fourteen renders. This is a render QA result, not independent visual acceptance. File dimensions and SHA-256 hashes are recorded in `visual/README.md` so the reviewer can identify the exact artifacts.

## Review focus

The reviewer should inspect:

1. Whether the homepage and About preserve the heat of `crack`, `suck`, `smell`, and `running` instead of turning the belief into consultant copy.
2. Whether the public profanity in the tutorial is natural or draws attention away from the technical boundary.
3. Whether removing anonymous work-page quotations is the right handling; the interview backlog asks which existing quotes have provenance.
4. Whether core-page line lengths and the About sidebar survive the supplied desktop and mobile renders.
5. Whether the inventory/opening-reuse gate catches interchangeable openings without being mistaken for editorial clearance.

## Rollback and cleanup

No generated output is tracked. Rollback is the selective reversal of the Phase A files after preserving the three pre-existing article refreshes and their fixture/evidence; never reset the checkout because unrelated dirty work is present.

The temporary localhost server was stopped after capture. No Playwright or server process remains. `output/` is ignored build output and can be regenerated with `python3 build.py`.
