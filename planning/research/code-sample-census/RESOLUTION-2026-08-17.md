# Documentation-resolution gate — 2026-08-17

**Decision:** do not start the 100-project crawl  
**Paid calls:** 0  
**PyPI JSON records fetched:** 100/100, zero errors

## The preregistered rule failed

The exact `Documentation` / `Docs` label rule resolves 57 of the frozen top 100
projects and excludes 43. That is not a tolerable primary frame for a claim about
the top 100: the missing group contains projects with known documentation, so the
exclusion is driven partly by metadata-label conventions rather than absence of
docs.

Observed false exclusions include:

- pytest: docs are its `Homepage` URL;
- Uvicorn: docs are its `Homepage` URL;
- aiohttp, yarl, multidict, propcache, frozenlist, and aiosignal: docs use labels
  such as `Docs: RTD`, which the exact/suffix rule does not admit;
- Hatchling: docs are its `Homepage` URL.

The full result is frozen in `data/docs-resolution-2026-08-17.json`, including
all project URL mappings, chosen URLs, full-response hashes, versions, and PyPI
serials. Summary:

| State | Projects |
|---|---:|
| Declared docs under the preregistered rule | 57 |
| No match | 43 |
| Metadata fetch error | 0 |

## What is falsified

The experiment is not falsified. The first resolution rule is. Proceeding with
57 would bias the corpus toward projects that maintain conventional PyPI
metadata, plausibly the same projects that maintain code samples more carefully.
The direction of that bias is exactly the result the study wants to measure.

## Replacement rule to test before crawling

The next batch must remain mechanical and report each stage separately:

1. Admit labels whose first token is `docs` or `documentation`, excluding labels
   containing `changelog`, `history`, `release`, `contact`, or `funding`. This
   captures `Docs: RTD` without selecting `Docs: Changelog`.
2. For still-unresolved projects, test only the declared `Homepage`. Reject code
   hosts and package indexes mechanically. Accept it only when the fetched page
   identifies a supported documentation generator or redirects to a host/path
   already declared as documentation by another package in the frame.
3. Keep `label-resolved`, `homepage-resolved`, and `unresolved` as separate
   strata. Never blend them without publishing the per-stratum estimates.
4. Inspect every rule-produced URL list before crawling code. A deterministic
   rule can still be systematically wrong.

No search-engine discovery and no hand-picked replacement enters the primary
sample. A manual sensitivity appendix remains permissible if separately labelled.

## Replacement-rule result

The replacement was run against the frozen metadata without re-fetching PyPI:

| Resolution stratum | Projects |
|---|---:|
| Qualified documentation labels | 63 |
| Generator-verified declared homepages | 5 |
| Generator-verified GitHub repository homepages | 12 |
| Unresolved | 20 |

This reaches 80/100 without search discovery or hand selection. The repository
route uses only a PyPI-declared GitHub repository, that repository's own public
`homepage` field, and the same supported-generator check. The 20 unresolved are
preserved, not backfilled.

The result is materially less selective, but it does **not** unlock page crawling
yet. Label-resolved URLs have not all been fetched through the generator gate,
and three documentation hosts cover related package pairs (Pydantic,
grpcio/grpcio-status, and pyasn1/pyasn1-modules). The next gate must fetch all 80
roots, record redirects and generator distribution, and define whether related
packages share or partition a documentation corpus before sampling pages.

Artifacts: `data/docs-resolution-v2-2026-08-17.json` (68-project intermediate)
and `data/docs-resolution-v3-2026-08-17.json` (80-project result).
