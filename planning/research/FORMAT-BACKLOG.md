# Format & Tool Backlog

**Compiled:** 2026-08-17 · **Source:** `seo-state-of-play-2026-08.md` · **Constraint:** no new CSS.

## The two rules that produced this ranking

**1. Reference infrastructure earns links; articles do not.** Measured in this niche on 2026-08-17
(§4.1):

| Asset | Type | Ref. domains | Org. traffic |
|---|---|---|---|
| semver.org | spec | 16,900 | 6,993 |
| llmstxt.org | spec | 6,509 | 3,407 |
| diataxis.fr | named framework | 2,240 | 304 |
| keepachangelog.com | named convention | **2,220** | **0** |
| divio.com/blog/documentation/ | **a blog post** about a framework | **203** | 0 |

`keepachangelog.com` holds 2,220 referring domains on **zero** organic traffic. **Judge reference assets on
referring domains, not sessions** — measuring them by traffic will cause us to kill the most valuable
thing we build.

**2. The same idea, published as a named framework instead of a blog post, held ~11× the referring
domains.** Procida's documentation quadrant as `divio.com/blog/documentation/` = 203 referring domains.
Renamed **Diátaxis** with its own canonical home = 2,240. Confounded by time and evangelism, so not a proven
cause (§4.1 Finding B) — but every named, canonically-homed artefact in the table cleared 400, and the
blog-post version capped at 203.

## What we already have, and why it is the right pattern

- `/linter/` — `templates/linter.html` + `linter.css`
- llms.txt generator — `templates/llms_txt_generator.html`
- `functions/api/discover-site.js` — a **264-line, security-hardened** Cloudflare Pages Function with SSRF
  protection (private-IP blocking), fetch timeouts, body-size caps, sitemap parsing and a declared user
  agent.

**That third item is the most under-used asset on the site.** Any new tool that needs to fetch a URL
server-side can reuse its validation and fetch layer, which is the hard and risky part. This materially
lowers the cost of items 1–3 below.

## CSS verdict, checked against the stylesheets (§4.3)

**Free — no new CSS:**
`linter.css` gives a complete **graded-findings** kit: `.lint-grade-a`…`-f`, `.lint-score-bar`,
`.lint-score-number`, `.lint-severity-error/-warning/-info`, `.lint-item` (+ `-message/-rule/-excerpt/-line/-meta`),
`.lint-group-*`, `.highlight-error/-warning/-info`. `main.css` gives `.tool-panel`, `.tool-workspace`,
`.tool-status(-error/-loading/-success)`, `.scan-form`, `.page-list`/`.page-row`, `.stats-band`/`.stat-num`,
`.article-summary`, `.numbered-steps`, `.faq-list`, `.code-block-wrapper`/`.code-output`, and the
`.flowchart-*` diagram set.

**Any tool shaped like "paste something in → get a grade and a list of findings" is free.** That is why the
top of this backlog looks the way it does.

**Needs a decision — flagged, not assumed:**
- **Tables are styled only inside `.post-content`** (`main.css:1551–1580`, responsive rule at `:2162`). A
  results table on a tool page will be unstyled. Workaround: render results as `.lint-item` rows, or wrap
  the results region in `.post-content`.
- **`details`/`summary` styled only inside `.faq-list`**; `select` only inside `.page-row`.
- **No charting CSS and no `input[type="range"]` styling.** Sliders render as browser defaults; charts must
  be hand-authored inline SVG. **Items marked ⚠ below need Ninad's call.**

---

# Ranked backlog

Effort is in solo working days. Ranked by payoff ÷ effort.

## 1. AI Citation Access Checker — *build this first*

**Effort: 1–2 days · Payoff: very high · CSS: free**

Enter a domain; we fetch `robots.txt` and report, per platform, whether the site can be **cited** —
separately from whether it can be **trained on**:

| Platform | Citation agent | Training agent |
|---|---|---|
| ChatGPT | `OAI-SearchBot` | `GPTBot` |
| Claude | `Claude-SearchBot`, `Claude-User` | `ClaudeBot` |
| Perplexity | `PerplexityBot`, `Perplexity-User` | — |
| Google AI Overviews / AI Mode | `Googlebot` | `Google-Extended` |

**Why this is the top item.** This distinction is genuinely confusing and widely misconfigured — I found it
live on our own site, where a block list containing `ClaudeBot`, `GPTBot` and `Google-Extended` looks
alarming but is actually a clean training opt-out that correctly preserves every citation agent (§2.6).
Anyone auditing that file casually would "fix" it wrongly. **The tool encodes a real distinction that
nobody currently has in one place**, and every user-agent claim is backed by the platform's own docs.

Report the training opt-out as **neutral information, not an error** — it is a legitimate choice. Flag only
genuine citation blocks.

- **Build:** reuse `discover-site.js` validation + fetch; add a robots.txt parser with correct
  longest-match user-agent precedence. Render with `.lint-item` + `.lint-severity-*`.
- **Link ceiling:** high. This is reference infrastructure of the `keepachangelog` kind — a thing people
  link to while making their own point.
- **Bonus artefact:** run it across 50 developer-docs domains and publish the distribution. That is a
  small-scale original research piece (item 8) generated for free by the tool.
- **Caveat to state in the UI:** robots.txt is not the whole story. Cloudflare and other WAFs can block AI
  crawlers at the edge regardless of robots.txt (§2.6). Say so, or the tool will mislead.

## 2. A named framework of our own — *the best effort-to-payoff ratio on this list*

**Effort: 2–3 days (thinking, not building) · Payoff: very high · CSS: free**

Publish one **named, canonically-homed rubric** — not an article. Candidate: a **Documentation Citability
Scorecard**, a short numbered rubric scoring a docs page on the criteria this research actually established:
opening states a claim; headings pass the layer-cake test; claims dated; failure modes covered; first-hand
artefact present; snippet-eligible; citation agents allowed.

**Why:** highest link ceiling measured (§4.1 Finding B), and it costs no engineering. It also becomes the
spine for items 1, 3 and 7 — the tool scores against it, the teardowns apply it, and each links back to it.

- Give it a name, a stable URL, a version number and a visible changelog. `keepachangelog.com` and
  `semver.org` are the shape to copy: one page, versioned, quotable.
- **Risk, stated honestly:** most self-declared frameworks are ignored. The measured 11× is one confounded
  case. Treat this as a cheap, high-ceiling bet, not a sure thing. It is cheap *because* it is only writing.

## 3. Heading-stack / layer-cake test

**Effort: 1 day · Payoff: high · CSS: free**

Paste a URL or Markdown; return the heading tree alone, and flag headings that are bare topic labels rather
than conclusions ("Versioning", "Overview", "Best Practices" — a stoplist plus a "no verb, no claim"
heuristic gets most of the way).

**Why:** it operationalises the single highest-leverage writing rule we found — NN/g's finding that the
layer-cake pattern is *"by far the most effective way in which users can scan pages"* and that the F-pattern
is what happens *"in the absence of subheadings"* (§3.1). It is also the exact check the playbook asks the
writer to run manually, so it dogfoods our own process.

Cheapest genuinely novel tool on the list. Could ship as a mode inside item 1 rather than standalone, but
standalone is sharper and more linkable.

## 4. Diátaxis type classifier / mixed-mode detector

**Effort: 2–3 days · Payoff: medium-high · CSS: free**

Paste a docs page; classify it as tutorial / how-to / reference / explanation and flag where it mixes modes.
Mode-mixing is the most common structural docs failure.

**Why:** rides an established named framework with 2,240 referring domains, which is a distribution channel
in itself. Heuristics (imperative density, second person, presence of parameter tables, "why"-framing) get a
useful first pass.

**Caveat:** classification will be visibly wrong sometimes. Present it as a prompt for judgement, not a
verdict, or it damages trust. Lower confidence than items 1 and 3 for that reason.

## 5. Docs migration redirect-map builder

**Effort: 2 days · Payoff: medium · CSS: free**

Paste old and new URL lists (or two sitemaps); get a proposed redirect map plus flags for orphans,
collisions and chains. Uses the `.page-list`/`.page-row` kit the llms.txt generator already established.

**Why:** solves a real, painful, recurring job. Practical utility, moderate link ceiling — more likely to be
bookmarked than cited.

## 6. The llms.txt evidence piece — *highest-value single article on the list*

**Effort: 1–2 days · Payoff: high · CSS: free**

"We ship an llms.txt generator. Here is the evidence that llms.txt does almost nothing."

**Why this is strong:** it is genuine information gain (§1.5) with real receipts, all of them dated —
Google's own sentence that *"Google Search itself doesn't use them"* (2026-07-10); the 137,210-domain
server-log study finding 97% of files never fetched (May 2026 data, published 2026-06-15); the **cats.txt**
falsification that reproduced all four standard "proofs" with a fake standard about office cats
(2026-08-07); and Chrome Lighthouse's audit, which treats the file as optional and pointedly does not claim
any AI system consumes it (2026-05-05).

Contrarian, evidenced, and almost impossible for a vendor to publish — every docs vendor in the SERP is
selling llms.txt support.

**Handle with care:** it must not read as a bait-and-switch against our own tool. The honest framing is that
the tool serves real search demand for a file people want, and the file is not an AI-visibility lever.
Say both plainly.

## 7. Docs teardown series, scored against our rubric

**Effort: 1 day each, repeatable · Payoff: medium-high, compounding · CSS: free**

Teardowns of real developer docs sites, scored with item 2's rubric, with reproducible receipts.

**Why sustainable:** raw material is free and effectively infinite, and each teardown *automatically*
produces the first-hand artefact the playbook's Section 0 gate requires (§1.5). It is the most reliable way
to hit a daily cadence without drifting into paraphrase.

**Discipline required:** critique real named products fairly and factually. Be specific about what is good.
A teardown series that reads as dunking on people will cost more in reputation than it earns in links.

## 8. Small-scale original research

**Effort: 2–3 days each · Payoff: high per piece · CSS: free (⚠ if charts wanted)**

"I checked N developer docs sites for one variable; here is the table and the method." N = 30–50, one
variable, method published.

**Why scoped down:** the large-scale version (the 137K-domain genre) needs a data asset we do not have and
is explicitly **not sustainable for one person** (§4.2). The scoped version keeps nearly all the citation
benefit. Item 1 generates the data for the first one at no extra cost.

**⚠ CSS:** results tables are fine **inside an article** (`.post-content table` is styled and responsive).
A chart is **not** free — no charting CSS exists. Either hand-author inline SVG or publish the table only.
**Recommend: table only, at least at first.**

## 9. Benchmark posts with published methodology

**Effort: 3–5 days each · Payoff: high per piece · CSS: free (⚠ if charts wanted)**

Strong information gain and very citable, but each is a real project. **Budget one per fortnight at most —
these are not calendar filler** (§4.2). Same charting caveat as item 8.

## 10. Comparison matrices

**Effort: 1 day · Payoff: low-medium, decaying · CSS: free in articles**

Cheap, but be clear-eyed: **I found no evidence that comparison tables drive AI citation**, and the one
low-authority page Google actually cited in an AI Overview for a niche head term had **no tables and no code
blocks at all** (§3.5). They are also maintenance liabilities with a visible wrong-answer risk.

Ship only where a reader genuinely needs lookup, date them visibly, and do not build a content strategy on
them.

---

# Explicitly not recommended

| Idea | Why not |
|---|---|
| A calculator with sliders (e.g. "docs ROI calculator") | ⚠ No `input[type="range"]` styling exists; controls would be off-brand. Worse, the output would be invented numbers — the opposite of §7.4's no-fabricated-specificity rule. **Recommend against on substance, not just CSS.** |
| Embedded live demos of third-party products | Ongoing breakage, external dependencies, and no styling support. Poor fit for a solo maintainer (§4.2). |
| Anything justified as "helps AI find us" via files or markup | Google, 2026-07-10: no machine-readable files, no special schema needed; llms.txt is *"ignored"* (§2.1, §2.2). Build tools that are useful to people; the citation benefit comes from being worth quoting. |
| A "definitive guide" omnibus page | Loses twice: no head-term chance at DR 26, and it dilutes the one-page-one-question granularity that correlates with citation (§1.3, §2.3). |
| Large-scale crawl research | Needs a data asset we do not have; not sustainable solo (§4.2). Use item 8 instead. |

---

# Suggested sequence

1. **Item 2** (named rubric) — pure writing, and items 1, 3, 7 all hang off it.
2. **Item 1** (AI Citation Access Checker) — highest-value build; reuses `discover-site.js`.
3. **Item 6** (llms.txt evidence piece) — receipts already gathered in this research pass.
4. **Item 3** (heading-stack test) — one day, dogfoods the playbook.
5. **Item 8** (first small-scale study) — data comes free from item 1.
6. **Item 7** (teardowns) — the repeatable daily-cadence engine from here on.

**One measurement note.** ninadpathak.com currently has **0 AI citations across all six platforms, 0
organic keywords and 0 organic traffic** (DR 26, 597 referring domains, measured 2026-08-17). That is the
baseline. **Perplexity is the surface to watch** — it is the only platform where the comparable solo site
beats both DR-90 vendors (27 vs 14 vs 12), and it is where writethedocs.org, with 4,909 referring domains,
scores zero (§2.3, §2.4).
