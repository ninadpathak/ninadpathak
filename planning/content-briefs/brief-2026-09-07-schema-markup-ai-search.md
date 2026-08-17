# Brief: Schema Markup for AI Search

**Slot:** 2026-09-07 | Order 40 | **Cluster:** AI Overviews and AI-search citation | **Experience: B**

## Keyword

| Field | Value |
|---|---|
| Primary | `schema markup for ai search` |
| Difficulty | KD 35 (Semrush 2026-08-17) |
| AI Overview | yes |

## Reader task

Choose the structured data that answer engines actually consume, and skip what they do not.

## Owns

Structured data specifically. Which types are documented as used, which are speculative.

## Must not repeat

The live `what-makes-a-page-extractable-by-answer-engines` owns passage structure, headings, and
the nine checks, and it explicitly refuses to claim schema earns citations. **This page must hold
the same line.** It owns which markup to emit and why; it does not own page structure, and it must
not promise that markup produces citations.

## Evidence — Experience B

The site emits `TechArticle`, `BreadcrumbList`, `FAQPage`, `DefinedTerm` and `CollectionPage`
already, from `templates/`. Inspect what is actually emitted, validate it, and report which types
are documented by Google as consumed versus which are folklore.

What could surprise you: a type the site emits that no documentation supports. That is the finding
worth having and it is a real possibility.

**Do not claim a ranking or citation effect from adding markup.** Google's own guidance is the
source of record for what a type does.

## Internal links

Outbound:
- `/articles/what-makes-a-page-extractable-by-answer-engines/`
- `/articles/seo-for-technical-documentation/` — same-cluster question is worth checking before
  linking, since that page is in Documentation. If it is, this is a cross-cluster link and needs
  the connection to be the subject of its sentence, or drop it and use row 35 instead.

**Inbound retrofit source:** `/articles/what-makes-a-page-extractable-by-answer-engines/`, whose
"Evidence should travel with the claim" section is the natural place.
