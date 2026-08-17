# Tool copy brief — for Codex

**Raised by:** `seo-currency` · **Date:** 2026-08-17 · **Branch:** `seo/currency`

Two tools are built, tested, wired, and shipping with placeholder prose. Every
placeholder is marked `TODO(copy)` in the template. Nothing below is written yet —
per charter 2d the director does not write publishable prose.

**Cluster: 4, `ai-search-optimization` ("Optimising for AI Overviews and AI search
citation").** Both tools belong to it. Cluster isolation applies: no links to
documentation pieces unless the link is the literal subject of the sentence.

---

## Non-negotiable factual constraints

These are not stylistic preferences. Each is a primary source, dated, and any copy
contradicting one has to be rejected.

1. **Never promise AI Overview placement.** Google, `developers.google.com/search/docs/appearance/ai-features`,
   last updated 2025-12-10, verbatim: *"There are no additional requirements to
   appear in AI Overviews or AI Mode, nor other special optimizations necessary."*
2. **Never claim schema helps AI Overviews.** Google's generative-AI guide, last
   updated 2026-07-10, verbatim: *"Structured data isn't required for generative AI
   search, and there's no special schema.org markup you need to add."*
3. **Never claim llms.txt improves AI visibility.** Same guide, verbatim: *"You
   don't need to create new machine readable files, AI text files, markup, or
   Markdown to appear in Google Search (including its generative AI capabilities),
   as Google Search itself doesn't use them"* and *"will neither harm nor help."*
   Supporting evidence in `seo-state-of-play-2026-08.md` §2.2: 97% of llms.txt files
   across 137,210 domains got zero fetches in May 2026, and the cats.txt
   falsification of 2026-08-07 reproduced every standard "proof" with a fake standard.
4. **The one thing that genuinely gates AI features is snippet eligibility.** Same
   guide, verbatim: *"a page must be indexed and eligible to be shown in Google
   Search with a snippet."* This is the only hard requirement either tool asserts.
5. **No invented precision.** Neither tool has a weighted score, and copy must not
   imply one. The checker counts checks; it does not grade a probability.
6. **Falsifiability test (charter 2c).** No first-person claim that a reader who
   knows the subject could call bullshit on. Ninad built these tools, so
   "I built this because…" is fair. A measurement he did not take is not.

---

## Tool A — AI Overviews Checker (priority)

**URL:** `/ai-overviews-checker/` · **Template:** `templates/ai_overviews_checker.html`
**Primary keyword:** `ai overviews checker` — 700/mo, KD 0, **no AI Overview on its
own SERP** as of the 2026-08-17 recompute.

Secondary intent worth covering in body copy, not in the title: checking whether a
page is *eligible* for AI features, and what actually blocks it.

| # | Slot | Spec |
|---|---|---|
| 1 | `<title>` | 50–60 chars. Must contain "AI Overviews Checker". Suffix ` | Ninad Pathak` is already in the pattern. |
| 2 | `meta description` | 140–155 chars. Say what it checks and that it runs in the browser. Must not promise placement. |
| 3 | `og:title` | Under 60 chars. |
| 4 | `og:description` | 110–130 chars. |
| 5 | `twitter:title` | Under 60 chars. |
| 6 | `twitter:description` | Under 120 chars. |
| 7 | `<h1>` | Must contain "AI Overviews Checker". |
| 8 | Lead paragraph | 2 sentences. Sentence one: what it does. Sentence two: it measures extractability and does not predict placement. |
| 9 | Domain-field hint | 1 sentence. Must say that fetching a URL is the only way to check snippet eligibility, and that pasting keeps content in the browser. |
| 10 | Empty-state line | Under 12 words. |
| 11 | Method section `<h2>` | Currently "What each check is based on". |
| 12 | Rule descriptions | Review for voice only. **The claims are load-bearing and each is sourced — do not soften them, and add nothing implying schema or llms.txt affects placement.** |
| 13 | Reference section | 300–450 words. Cover: what extractability means; why snippet eligibility is the only hard gate; why a scored prediction would be dishonest. Source: `seo-state-of-play-2026-08.md` §2.1 and §2.2. |

**Tone note.** The tool's differentiator is that it refuses to fake precision while
every competitor sells a score. Copy should make that a feature, plainly, without
attacking anyone by name.

---

## Tool B — llms.txt Validator

**URL:** `/llms-txt-validator/` · **Template:** `templates/llms_txt_validator.html`
**Tool-intent subset:** 550/mo across generator, checker, and validator phrasings
(corrected figure — the ~7,000/mo llms.txt family includes the KD-56 head term,
which is not tool intent and is not what this page targets).

| # | Slot | Spec |
|---|---|---|
| 1 | `<title>` | 50–60 chars. Must contain "llms.txt validator". |
| 2 | `meta description` | 140–155 chars. |
| 3 | `og:title` | Under 60 chars. |
| 4 | `og:description` | 110–130 chars. |
| 5 | `twitter:title` | Under 60 chars. |
| 6 | `twitter:description` | Under 120 chars. |
| 7 | `<h1>` | Must contain "llms.txt validator". |
| 8 | Lead paragraph | 2 sentences. Mention that findings are marked as spec requirement or convention. |
| 9 | Domain-field hint | 1 sentence. |
| 10 | Empty-state line | Under 12 words. |
| 11 | Rules section `<h2>` | Currently "What gets checked". |
| 12 | Rule descriptions | Review for voice. **Rule names must not change — `tests/test_llms_txt_validator.py` asserts them.** |
| 13 | Reference section | 250–400 words. Must state that only the H1 is required by the spec. Must not claim llms.txt improves AI visibility. |

---

## Structured-data descriptions (both tools)

`content/projects.yaml` carries three `TODO(copy)` markers:

- **A — generator description.** The old text claimed the generator worked
  *"without sending site data to a server"*. **That is false and I removed it**
  under charter 2c: scanning POSTs the domain and the discovered page URLs to
  `/api/discover-site`, which devtools makes obvious. Needs a replacement clause
  that is accurate about what is and is not transmitted. Also decide whether the
  `Local-only` tech tag stays, since it carries the same false implication — I
  changed it to `Cloudflare Pages Function`.
- **B — validator description.** One sentence, sibling register.
- **C — checker description.** One sentence, sibling register. Must not imply
  placement prediction.

---

## The in-sentence linking problem, and why I did not fake it

Charter 2e requires inbound links from existing pages inside real sentences, never
a related-posts dump, never bare-keyword or "click here" anchors.

**What I shipped (structural, no prose required):** footer links for all tools,
`projects.yaml` entries, sitemap entries, a new `## Tools` section in the site's own
`llms.txt` covering all four tools (`/linter/` was missing from it entirely), and
`SoftwareApplication` schema on each tool cross-referencing its siblings via
`isRelatedTo`.

**What I could not honestly ship.** I checked the freshly built output rather than
working from memory, as 2e requires. **No live article mentions llms.txt or AI
Overviews anywhere** — `grep` over `content/posts/*.md` returns zero hits. So there
is no existing sentence on the site where a link to either tool would be its
subject, and manufacturing one inside a documentation article would breach cluster
isolation (2c-bis rule 3). Two links added in one direction, from tool to nowhere,
would be half a link.

**This is the actual reason `/llms-txt-generator/` earned three lifetime
impressions.** It was never only a linking problem. The tools have no supporting
content cluster at all.

**And cluster 4 is one tagged post away from existing.** `config.toml` already
declares it — `slug = "ai-search-optimization"`, title "AI Search and Citation",
with `llms-txt`, `ai-overviews`, `ai-search`, and `answer-engines` in its
`tag_matches`. `build.py` renders `/articles/<slug>/` for any category that has at
least one post. The category is empty only because the single tag-matching live post,
`seo-for-technical-documentation.md`, carries an explicit `category:
technical-documentation` in its frontmatter, and an explicit category overrides tag
matching. **I did not reassign it** — moving a live post between clusters changes its
ranking surface and that is the strategy agent's call, not mine.

So the unblock is one of:

1. **Commission one article tagged into cluster 4.** The moment it publishes,
   `/articles/ai-search-optimization/` renders as the cluster owner page, and both
   tools have a same-cluster home to be linked from in real sentences.
2. **Or reassign `seo-for-technical-documentation` to cluster 4**, which brings the
   owner page to life immediately with no new writing. Its tags already match. This
   is a cluster-map decision.

**The article I would commission first**, already argued in
`FORMAT-BACKLOG.md` item 6: *"We ship an llms.txt generator, and here is the
evidence llms.txt does almost nothing."* The receipts are gathered and dated
(§2.2). It is contrarian, it is genuinely information-gain, no docs vendor can
publish it, and it belongs in cluster 4 by subject. It would carry in-sentence
links to both llms.txt tools where the link is unambiguously the subject.

A second, for the checker: an article on what actually makes a page eligible for AI
features, whose subject is snippet eligibility. That one hosts the checker link
naturally.

---

## Verification already done, so copy review need not redo it

- `python build.py` passes: 114 HTML pages, 113 sitemap URLs, 113 unique canonicals.
- `git diff --stat main -- static/css/` is **empty**. No CSS added; both tools compose
  `linter.css` and `main.css` only. A test asserts no tool template contains `<style`.
- 49 deterministic tests for the checker, 40 for the validator, driving the shipped
  JavaScript engines through node so there is no second implementation.
- Privacy asserted by test: each tool's wiring script contains exactly one `fetch`
  call, to its own endpoint, and no `sendBeacon`, `localStorage`, `sessionStorage`,
  or `WebSocket`. Paste paths never transmit.
- Both engines dogfooded against real pages. The site's own `llms.txt` validates at
  100/A. The checker was run against four of the site's own article pages and scores
  3–6 of 9, which is discriminating rather than flattering.
