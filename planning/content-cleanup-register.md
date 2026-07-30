# Content Cleanup Register

**Started:** 2026-07-30  
**Scope:** Source content only. Generated HTML in `output/` remains disposable build output.

## Decision rules

- **Published:** Relevant to the documentation authority position and usable while a verified rewrite is prepared.
- **Review:** Potentially useful as source material, but excluded from builds until its claims, examples, intent, and internal links are audited.
- **Retired:** Outside the documentation and technical-content position. The Markdown remains in the repository, but the generator excludes it.
- **Draft:** New work that has not passed the publishing gate.

No retired URL has been redirected to an unrelated hub. The generated site now includes
a real `404.html` so removed URLs do not fall through to the homepage.

## Voice requirement

Every article is part of a personal blog. It must use first person, explain what Ninad
noticed or did, take a clear position, and prefer simple conversational language.
Search intent determines the problem being answered; it does not flatten the prose into
anonymous SEO copy. Prose paragraphs never exceed two sentences.

## Published pending rewrite

| Source | Planned destination |
|---|---|
| `developer-onboarding-docs-what-works-what-doesnt.md` | Developer onboarding checklist and timed test |
| `how-to-write-a-changelog-developers-actually-read.md` | Changelog best practices |
| `how-to-write-a-technical-tutorial-that-actually-teaches.md` | Tested technical tutorial workflow |
| `writing-release-notes-that-developers-trust.md` | Release notes best practices |

## In review

- `developer-trust-hierarchy.md`
- `embedding-models-compared.md`
- `engineering-velocity-documentation.md`
- `from-engineer-to-technical-writer-what-i-kept-and-what-i-left-behind.md`
- `how-anthropics-contextual-retrieval-changes-rag-architecture.md`
- `how-stripes-technical-blog-became-a-competitive-moat.md`
- `hybrid-search-bm25-vector-search.md`
- `rag-evaluation-metrics-what-actually-matters.md`
- `reranking-in-rag-why-your-top-k-results-are-probably-wrong.md`
- `structured-outputs-llms-json-mode-function-calling.md`
- `technical-content-as-a-moat-the-long-game-for-developer-tools.md`
- `technical-writing-for-ai-products-the-new-rules.md`
- `technical-writing-for-engineers.md`
- `the-case-for-shorter-technical-documentation.md`
- `why-devtools-startups-lose-deals-over-bad-docs.md`

## Retired

The remaining 52 published articles are marked `retired`. They are predominantly agent
architecture, agent memory, inference, model, and generic RAG topics that do not help
the documentation ICP complete a documentation task.

The AI glossary and the six previous AI topic hubs are also retired from generated
output. Their source remains available for selective reuse after verification.
