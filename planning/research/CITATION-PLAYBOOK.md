# Citation Playbook

**For:** the writer (`codex-writer`), applied to **every** piece before it ships.
**Derived from:** `seo-state-of-play-2026-08.md` (2026-08-17). Section refs below point there.
**Goal:** maximise the chance that (a) an AI assistant quotes the page, and (b) a human finishes it.

Two things make this playbook different from generic SEO advice, and both are measured, not assumed:

- **Link authority does not predict AI citation.** A DR-92 site with 42,624 referring domains gets *fewer*
  citations than a DR-73 solo blog in this niche (§2.3). We cannot win head-term rankings, but the citation
  game is not decided by the metric we are worst at.
- **Our reader has already been failed by an AI answer.** 74% of developers research solutions through AI
  but only 59% find it effective; 66% name "almost right, but not quite" as their top frustration; **75.3%
  then go ask a human** (§3.3, Sonar 2026 n=1,149; Stack Overflow 2025 n=33,662). They arrive looking for
  evidence a person did this.

Everything below follows from those two facts.

---

## Section 0 — The gate: one first-hand artefact, or do not ship

**This is not a style preference. It is the campaign's main risk control.**

Google's Quality Rater Guidelines (live edition, 182pp, 2025-09-10) name as a **Low-quality** criterion,
verbatim: *"Lacks adequate effort and first-hand experience from the content creator"* — illustrated by
content *"paraphrased or summarized from other sources, with minimal signs of effort or original content
added by the content creator."* A daily LLM-assisted publishing programme is, on its face, that shape
(§1.5).

**Every piece must contain at least one of these, and it must be specific enough that it could not have
been paraphrased from the existing top 10:**

| Artefact | What it looks like concretely |
|---|---|
| A command actually run | The invocation, the real output, the version, the date |
| A number measured | "Of the 30 docs sites I checked on 2026-08-14, 11 had no version selector" |
| A named real example | A specific docs page, with what it does and what it omits |
| A decision with a cost | "We chose X; it cost us Y; here is what I would do differently" |
| A failure reproduced | The exact error string, the conditions, the fix |

**If a day's piece has none of these, skip or merge it. Do not ship it.** Volume is not the spam test —
primary purpose is (spam policies, updated 2026-05-15) — but a piece with no first-hand artefact carries
risk and earns nothing.

**Write this test into the draft:** before submitting, quote the artefact to yourself. If the sentence
you'd quote is a generality, there is no artefact.

---

## Section 1 — The opening (first 50 words)

The opening does one job: **prove a human did this, and state the conclusion.** Nothing else.

### Rules

1. **Sentence 1 states the claim or the answer.** Not the topic, not why the topic matters, not history.
   NN/g's inverted-pyramid principle: *"The most important information (or what might even be considered
   the conclusion) is presented first."* The low-authority page Google cited in its AI Overview for
   `docs as code` opens: *"AI changes the game when it comes to having all your docs in your repository:
   it's never been that easy to keep them up to date!"* — position first (§2.5).
2. **Sentence 2 or 3 carries the first-hand marker.** That cited page's second sentence: *"I've always
   been a fan of having documentation living alongside the code."* First person, by sentence two.
3. **Zero preamble.** Delete any opening that establishes importance before delivering content.

### Banned openings

Delete these on sight. Each one spends the reader's attention establishing that a topic exists.

- "In today's fast-paced development landscape…"
- "Documentation is a critical part of any software product."
- "Whether you're a seasoned technical writer or just starting out…"
- "Before we dive in, let's understand what X is."
- "X has become increasingly important in recent years."
- Any sentence whose removal loses no information.

### Rewrite examples

> **Bad:** "API documentation is one of the most important assets a developer product has. In this guide,
> we'll explore best practices for writing documentation that developers love."
>
> **Good:** "Most API reference pages fail at the same point: they describe the endpoint but never show a
> request that works. I checked 20 developer portals in August 2026; 13 had no copy-pasteable request with
> a real credential flow."

> **Bad:** "Choosing a documentation tool can be overwhelming, with many options available."
>
> **Good:** "I moved a 400-page docs site from GitBook to Docusaurus in March 2026. The migration took
> nine days, and seven of those went to redirects — not content."

---

## Section 2 — Headings (the highest-leverage rule in this playbook)

**The F-pattern is a failure mode, not a target.** NN/g (Pernice, 2019-08-25), verbatim: *"In the absence
of subheadings and bullets, users tend to fixate on the words toward the beginning of lines."* The
**layer-cake pattern** — reading headings only — is *"by far the most effective way in which users can
scan pages"* (§3.1).

A scanning reader sees **only your headings**. So headings must carry content, not labels.

### Rules

1. **Every heading states a conclusion, not a topic.**
2. **The heading stack alone must read as a useful summary of the piece.**
3. **Prefer statement headings over question headings.** The cited AI-Overview page used statement headings
   throughout (§2.5). Use a question heading only where it matches a real query verbatim.
4. **No heading may be a single abstract noun.** "Versioning", "Structure", "Best Practices", "Overview",
   "Considerations" — all banned alone.

### The heading test — run this on every draft

**Strip everything but the headings. Read what remains.** If it is not a coherent, useful summary, the
headings are labels and must be rewritten. This is a pass/fail check, and the reviewer runs it too.

### Rewrite examples

| Bad (topic label) | Good (carries the point) |
|---|---|
| Versioning | Keep one URL per version and canonicalise to the current one |
| Error handling | Document the error string, not the error code |
| Getting started | A new developer needs a working request in under five minutes |
| Best practices | Every reference page needs a request a reader can paste |
| Tooling | Pick the tool that matches your review path, not your feature list |

**Why this rule pays twice:** headings that assert extractable claims serve the scanning human *and* give
a retrieval system a self-contained passage to quote. One piece of work, both audiences (§3.1).

---

## Section 3 — The citable unit

**What gets quoted is a self-contained claim plus its support, in one place.** A claim whose evidence sits
three paragraphs away cannot be lifted, so it will not be.

### Rules

1. **One claim per paragraph, supported inside that paragraph.** If the support is elsewhere, the paragraph
   is not quotable.
2. **A quotable paragraph survives removal from the page.** Test: cut a paragraph, paste it into a blank
   document. Does it still assert something true and complete, without needing the sentence before it?
   If not, it needs its subject and its evidence restated inside itself.
3. **Avoid opening a paragraph with an unresolved pronoun or "This means that…".** These bind the paragraph
   to its neighbour and make it unquotable.
4. **Put the number in the same sentence as the claim.** "Adoption is low" is unquotable. "97% of llms.txt
   files received zero fetches in May 2026 across 137,210 domains" is quotable.
5. **Date every factual claim inline.** Not in the frontmatter — in the sentence. "As of August 2026…",
   "measured 2026-08-14…". An undated claim is unusable to a retrieval system deciding freshness, and
   unusable to us in three months.

### The "answer to objections" pattern — use it

The single most copyable structural feature of the low-authority page Google cited was **a section
answering eight specific counterarguments** (§2.5). It manufactures eight discrete, self-contained,
quotable claim-and-response units — and it doubles as the first-hand position-taking that Section 0
requires.

**Recommended: include an objections or "when this is wrong" section in most pieces.** Format:

> **"But our docs are too large to move into the repo."** — Then move one section. I moved 40 pages
> first and left 360 in place for six weeks. [specific outcome]

Each bolded objection plus its response is independently quotable. This is cheap to write and hard for a
vendor blog to imitate, because it requires having actually hit the objection.

---

## Section 4 — Cover the failure modes

**This is our value proposition, not an appendix.** 66% of developers' top frustration with AI answers is
*"almost right, but not quite"* (Stack Overflow 2025). The reader left the assistant precisely because the
happy path was covered and the edge was not (§3.3).

### Rules

1. **Every how-to includes what breaks.** The version incompatibility, the error string, the ordering
   constraint, the thing that silently does nothing.
2. **Quote error messages verbatim, in a code block.** Exact strings are what people search and what
   assistants match. Paraphrased errors are worthless.
3. **State version and date for anything that can drift.** "Tested with Redocly CLI 1.34 on 2026-08-14."
4. **Say what you could not make work.** This is the strongest possible first-hand signal, and no
   AI summary and no vendor blog will ever contain it.
5. **Never write the generic middle.** If an assistant already answers it adequately, the reader never
   arrives. Content whose whole value is a competent summary of consensus has no audience.

---

## Section 5 — Depth and shape

Set length by the number of claims that need support, then stop.

1. **One page, one question.** The best-cited independent site in the niche uses one page per narrow
   sub-question, ranking on near-zero page-level links (§2.3). Prefer several narrow pages to one omnibus
   guide. This also cuts cannibalisation risk.
2. **~1,800 words is a real, working length.** The page Google cited in its AI Overview was ~1,800 words,
   not 3,000 (§2.5). **There is no evidence that longer wins** (§3.4).
3. **Padding actively imports risk.** Length chased for its own sake produces exactly the "minimal signs
   of effort" the QRG penalises (§1.5). Stop when you would begin padding.
4. **Tables: use for lookup and comparison only.** Where the reader's question is "which one?" or "what is
   the value for X?", a table beats prose. **Do not add tables believing they drive AI citation — the page
   Google actually cited had no tables and no code blocks** (§3.5). Never convert a genuine argument into
   a matrix; a table strips causality.

---

## Section 6 — What NOT to do (measured dead ends)

Do not spend a sentence, a brief, or a build hour on these. Each is contradicted by a primary source.

| Do not | Because |
|---|---|
| Claim llms.txt improves AI visibility | Google (2026-07-10), verbatim: *"Google Search itself doesn't use them"* and *"will neither harm nor help."* 97% of files got zero fetches across 137,210 domains in May 2026. The cats.txt experiment (2026-08-07) reproduced all four standard "proofs" with a fake standard about office cats (§2.2). |
| Add schema markup "for AI" | Google (2026-07-10): *"Structured data isn't required for generative AI search, and there's no special schema.org markup you need to add."* Keep existing schema for rich results; do not build new schema on an AI rationale (§2.1). |
| Build per-article backlinks to win rankings | In this niche a Medium post with **URL Rating 0 and zero referring domains** ranks 8th for a commercial head term; Mintlify ranks 5th on 4 referring domains. Nobody won on page-level links (§1.3). |
| Target head terms like `api documentation best practices` | The top 10 is DR-84-to-94 vendors plus UGC. A DR-26 site does not win it with a better article. Go long-tail and specific (§1.3). |
| Write "definitive guide to X" omnibus pages | Loses on both counts: no head-term chance, and it dilutes the one-page-one-question granularity that correlates with citation (§2.3, §5.1). |
| Cite CWV thresholds of 2.0s LCP or a "composite performance score" | False. Google's own doc still says LCP 2.5s, INP 200ms, CLS 0.1, per-page at the 75th percentile (§1.2). |
| Reference a "June 2026 Quality Rater Guidelines update" | It does not exist. The live PDF is 182pp, dated 2025-09-10 (§1.2). |
| Source any statistic from a "statistics 2026" roundup post | These misattribute and inflate. One claimed "92.6%" for a Stack Overflow figure that is actually 84% (§3.3). Always go to the primary survey. |

---

## Section 7 — Freshness and attribution

1. **Show a visible updated date.** `.post-meta-updated` **already exists in `main.css`** — this costs
   nothing to display. The AI-Overview-cited page carried both a publish date and a visible revision date
   two days later (§2.5).
2. **Name the author on every piece.** 75.3% of developers go looking for a human when they distrust an AI
   answer (§3.3). Attribution is the product, not a formality.
3. **Be honest about method where AI assisted.** Google's helpful-content doc asks, verbatim: *"Is the use
   of automation, including AI-generation, self-evident to visitors through disclosures?"* (§1.5). A plain
   note on how a piece was researched and written is a trust asset. It is also the honest position.
4. **Never fabricate specificity.** The failure mode we documented in other people's work — confident,
   precise, invented detail (§1.2) — is the one thing that would destroy this site's value. If a number,
   date, version or quote is not verified, do not write it. Write "I did not verify this" instead.

---

## Pre-publish checklist

Run every item. Any **No** in the first five blocks it from shipping.

**Blocking:**

- [ ] Contains at least one first-hand artefact, specific enough not to be paraphrasable (§0)
- [ ] Opening sentence states the claim or answer — no preamble (§1)
- [ ] First-hand marker appears by sentence three (§1)
- [ ] Heading test passes: headings alone read as a useful summary (§2)
- [ ] No factual claim is undated; no fabricated number, version, date or quote (§3.5, §7.4)

**Quality:**

- [ ] Every heading states a conclusion, not a topic (§2)
- [ ] Every paragraph survives being cut and pasted into a blank document (§3.2)
- [ ] Numbers sit in the same sentence as the claim they support (§3.4)
- [ ] An objections / "when this is wrong" section is present, or its absence is deliberate (§3)
- [ ] Failure modes covered: what breaks, exact error strings, versions tested (§4)
- [ ] Nothing in the piece is a competent summary of consensus and nothing else (§4.5)
- [ ] Length is set by claims needing support; no padding (§5)
- [ ] Tables used only for lookup/comparison, and dated (§5.4)
- [ ] Nothing from the Section 6 dead-end list appears
- [ ] Visible author and updated date (§7)

**Build constraint:**

- [ ] No new CSS. Composed from `main.css`, `visuals.css`, `flowcharts.css`, `linter.css` only.
      Note: **tables are styled only inside `.post-content`**, and `details`/`summary` only inside
      `.faq-list`. If the piece needs styling that does not exist, **escalate to Ninad — do not add a
      stylesheet.**
