# Brief: Documentation Migration Checklist

**Slot:** 2026-09-12 | Order 45 | **Cluster:** Documentation | **Experience: A**

## Keyword

`documentation migration` measures 20/mo. Near zero, and the piece earns its slot on evidence
rather than demand.

## Reader task

Move documentation between platforms or URL structures without losing search equity.

## Owns

The migration checklist and the failure modes that appear afterwards rather than during.

## Must not repeat

Version routing, owned by the live `how-to-document-multiple-product-versions`. Platform choice,
owned by row 32.

## Evidence — Experience A, and this is the strongest A row in the fortnight

**This site did the migration and got it wrong in a measurable way.** It moved from `/blog/` to
`/articles/`, and the consequences are documented rather than remembered:

- inherited hard-404 internal links from pages that linked to the old prefix
- 68 pages returning hard 404s, recovered later in a dedicated commit
- Search Console still showing **94% of post impressions on the legacy `/blog/` path**, which is
  the clearest possible evidence that a migration is not finished when the redirects ship

That last number is the article. A checklist written by someone whose own migration is still
visible in the data is worth more than a clean one.

Cite the GSC path split with its date. Do not claim a recovery figure that has not been measured.

## Internal links

Outbound:
- `/articles/how-to-document-multiple-product-versions/`
- `/articles/seo-for-technical-documentation/`

**Inbound retrofit source:** `/articles/seo-for-technical-documentation/`, whose canonicalization
and redirect sections are exactly where a migration checklist belongs.
