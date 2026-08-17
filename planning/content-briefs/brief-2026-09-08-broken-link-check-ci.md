# Brief: How to Add a Broken-Link Check to Documentation CI

**Slot:** 2026-09-08 | Order 41 | **Cluster:** Documentation | **Experience: A**

## Keyword, and a finding worth acting on separately

| Field | Value |
|---|---|
| Primary | `documentation ci` / broken-link-check-in-CI family |
| Volume | near zero for the CI phrasing |
| **Adjacent finding** | **`broken link checker` is 8,100/mo** (Semrush 2026-08-17) |

That 8,100 is **tool intent, not article intent**. People want a checker to run, not a guide to
CI configuration. This article should not chase it.

**It is a tool opportunity and it has been recorded as one.** The site already ships five tools
and the tool-first directive in campaign §2 exists for exactly this shape. Flagged to the director
separately; this brief does not try to serve it with prose.

## Reader task

Catch dead internal and external links before release rather than after.

## Owns

The CI configuration and the failure policy: what blocks a build and what only warns.

## Must not repeat

The workflow (row 31), the stack (row 34), documentation testing generally. This is one check.

## Evidence — Experience A, and it is strong

The site carries real history here. It inherited hard-404 internal links from a `/blog/` to
`/articles/` migration, and it now runs `tools/check_link_retrofit.py` as a publish gate plus an
SEO audit at build time. The honest arc is: the links broke, nothing caught it, and a gate was
added afterwards.

The most useful part is the failure policy. A link check that fails a build on any external 404
becomes noise the team routes around, and saying so is more valuable than the config snippet.

## Internal links

Outbound:
- row 31 `docs-as-code`, row 34
- `/articles/seo-for-technical-documentation/`

**Inbound retrofit source:** row 34's docs-as-code tools piece, published a week earlier, same
cluster.
