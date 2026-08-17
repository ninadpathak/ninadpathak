# Brief: Glossary term, Docs as Code

**Slot:** 2026-08-21 | **Type:** GLOSSARY
**Target:** `content/data/glossary.yaml`, term `docs-as-code`. Do not create a Markdown post.

## What to write

Fill three fields on the existing term entry. The plumbing, categories, and article links
are already in place and validated.

| Field | Requirement |
|---|---|
| `short_definition` | One or two sentences. Must be a complete answer to "what is docs as code" for a reader who arrives with no surrounding page. Becomes the DefinedTerm schema description, the index blurb, and the llms.txt line. |
| `long_definition` | The mechanism: source control, review, CI checks, and deploy. |
| `description` | Meta description, under 160 characters. |

## Why the standalone quality matters

Extractability is the entire reason these pages exist. A definition that only makes sense
after reading the paragraph above it cannot be quoted by an assistant or an AI Overview.
Write the answer, never a teaser.

## Keyword data

`docs as code` 300 vol KD 5, `documentation as code` 250 KD 12, `docs-as-code` 100 KD 8,
`what is docs as code` 40 KD 9. Combined 690. Parent topic for all four is `docs as code`.
AI Overview present.

## Owns

The definition of the practice, at glossary depth.

## Must not repeat

The working implementation, which the 2026-08-22 article owns. Tooling selection, which
the documentation-software comparison owns. Keep this to what the term means, not how to
run it.

## Article links, already wired and verified

- `/articles/technical-documentation-template/`
- `/articles/documentation-review-checklist-before-you-publish/`

## Links blocked until published

- `docs-as-code`, the article, unblocked by the 2026-08-22 slot. Already recorded under
  `pending_articles` in the YAML. Move it into `related_articles` once that piece ships.

## Publishing

The term goes live automatically once the TODO markers are gone. There is no flag to flip.
