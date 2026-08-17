# Content briefs

One brief per calendar slot in `planning/90-day-seo-ai-strategy.md`. The Codex writer
works only from these, so a vague brief produces a vague article.

Named `brief-YYYY-MM-DD-<slug>.md` by publication date. The four 2026-07 briefs in this
folder predate the documentation-only decision and use an older format. Follow the
2026-08 briefs, not those.

## Every brief carries

| Field | Why it is mandatory |
|---|---|
| Slot type | NEW, EXPAND, REWRITE, MERGE, GLOSSARY, or FIX. Sets the amount of work. |
| Primary keyword | One per URL. Never two. |
| Volume / Difficulty / Intent | From Ahrefs US, 2026-08-17, cached in `planning/research-cache/`. |
| Parent topic | Ahrefs' statement about which page Google already rewards. If the parent is another page, this is a section, not an article. |
| AI Overview | Whether the SERP returns an `ai_overview` feature. If yes, the page has to be written to be quoted, not only to rank. |
| Reader task | The single job the reader completes. |
| **Owns** | What this URL is the answer to. |
| **Must not repeat** | The cannibalization boundary, taken from the map in the strategy document. Non-negotiable. |
| Evidence required | What has to be gathered or built before writing. The publishing gate rejects the piece without it. |
| Internal links | Exact URLs, each verified present in the built sitemap. |

## The internal-link rule

The site already carries 31 hard-404 internal links because pieces linked to pages that
did not exist. That does not happen again.

Every internal link in a brief is copied from the built output, never invented:

```
python build.py
# output/llms.txt      grouped by topic, with a description per URL. Use this to choose.
# output/sitemap.xml   the authority on what exists. Confirm here.
```

A brief may name a target that is not published yet. When it does, it goes under
**Links blocked until published** with the slot that unblocks it, and the writer leaves
the link out until then. It never goes in the live list.

The 17 live article URLs as of 2026-08-17 are listed in `output/llms.txt`. Re-read that
file rather than trusting this one after any publish.

## House rules that apply to every piece

Enforced by `rule_checker.py`, which must pass before publish:

- No em dashes. No semicolons in prose. No horizontal rules in the body.
- No paragraph over two sentences.
- No sentence starting with a number, numeral or spelled out.
- No banned sentence starters: in, this, by, finally, most, ever.
- No forbidden words: leverage, synergy, unlock.
- No contrastive parallelism: unlike X, whereas, on the other hand, "not X but Y".
- Any factual count needs an evidence receipt comment or it trips `rule-of-three`.
- At most two comma-separated values in a sentence. Split, or use a list.
- First person where there is a real opinion, decision, or thing he did. Not as scaffolding.
- Every claim inspectable. No invented experience, clients, benchmarks, or anecdotes.
  A hypothetical is labelled as one.
