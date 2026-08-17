# Tool selection, 2026-08-17

**Question put by Ninad:** pick the highest-value remaining build-a-tool keyword from
`planning/addressable-universe.md` §5a, on this basis in order — volume, then KD, then
whether the checking or calculation job is real enough that a browser tool genuinely
answers it better than an article. With the warning: do not build a tool for a job that
is really an article, and if the best candidate fails that test, say so and take the
next one.

**Answer: the list is exhausted.** Two of the nine are shipped and the remaining six all
fail, three of them on grounds that no amount of build effort would fix. The next viable
opportunity sits just outside the list and is larger on all three criteria, so that is
what got built.

---

## The nine, and what happened to each

| Keyword | Vol/mo | KD | Verdict |
|---|---:|---:|---|
| ai overviews checker | 700 | 0 | **Shipped** — `/ai-overviews-checker/` |
| llms.txt generator | 300 | n/a | **Already existed** — `/llms-txt-generator/` |
| ai documentation generator | 250 | 37 | **Rejected** — cannot be built under the privacy constraint |
| openapi client generator | 150 | 35 | **Rejected** — mature free incumbents, thin by comparison |
| openapi documentation generator | 150 | 23 | **Rejected** — same |
| llms.txt checker | 150 | n/a | **Same job as the validator already shipped** — a copy fix, not a build |
| audit documentation software | 100 | 12 | **Rejected** — off-niche, and misclassified |
| llms.txt validator | 100 | n/a | **Shipped** — `/llms-txt-validator/` |
| audit documentation example | 40 | 0 | **Rejected** — off-niche, and misclassified |

### `ai documentation generator` — 250/mo, KD 37

Highest remaining volume, so it was the first candidate, and it is the one that fails
hardest.

**[VERIFIED]** SERP checked 2026-08-17: JetBrains AI Assistant, Scribe, QuillBot,
aidocmaker.com, Tembo's roundup, and a G2 category page. Every real competitor generates
documentation by calling a language model over the user's source code.

To compete honestly, the tool would have to send the user's code to a model. That
directly violates a non-negotiable constraint — **never transmits what the user pastes** —
and would need a server-side key, a per-use cost, and probably a login. Building a
non-AI tool under the name "AI documentation generator" would be a template dressed up
as a model, which is exactly the thin tool the brief warns against.

**Rejected on constraint-incompatibility, not difficulty.** It is not buildable here at
any effort level. It also carries the highest KD in the list.

### `openapi documentation generator` — 150/mo, KD 23, and `openapi client generator` — 150/mo, KD 35

These pass the tool test in principle: the input is an OpenAPI spec the reader already
has, and the output is something no article provides.

**[VERIFIED]** SERP checked 2026-08-17: `openapi-generator.tech`, the
`OpenAPITools/openapi-generator` GitHub project, Microsoft Learn, Swagger, and
`openapi.tools`. The incumbents are mature, free, and support dozens of target languages
and output formats. Redoc, Swagger UI, and Scalar own the rendering side.

A browser-only version would be visibly worse than what already exists, for a reader who
is one search away from the real thing. That is the definition of a thin tool. Codegen is
also adjacent to the niche rather than inside it.

**Rejected.**

### `audit documentation software` — 100/mo, KD 12, and `audit documentation example` — 40/mo, KD 0

**[VERIFIED]** SERP checked 2026-08-17: ComplianceQuest, Trullion, Healthicity medical
coding audits, Gartner audit-management reviews, Wolters Kluwer "audit software for
accountants", Suralink.

This is the **accounting** sense of "audit documentation" — assurance workpapers, the
ISA 230 term of art — not "audit your developer documentation". The intent is a vendor
listicle for finance and compliance teams.

**Rejected as off-niche.** Worth recording as a correction: **140/mo of the 1,940/mo
"buildable" list is off-niche noise**, and `addressable-universe.md` §5a should drop both
rows. That reduces the genuinely addressable build-a-tool pool to 1,800/mo, of which
1,100/mo is now shipped.

### `llms.txt checker` — 150/mo

This one is a real tool job, and it is already done.

**[VERIFIED]** SERP checked 2026-08-17: indexly.ai, rankability.com, mrs.digital,
rankray.com, radarkit.ai, llmstxtchecker.net, spindorai.com. Notably the whole first page
is small independent tools with no large brands — the barrier is low.

More useful: several of them title their page **"LLMs.txt Checker & Validator"** or
**"Generator & Checker"**. Competitors serve the checker and validator phrasings on **one
page**, because it is one job.

`/llms-txt-validator/` already does that job. A second URL for the same job would
cannibalise it. **So the correct action is a copy change, not a build:** have the
validator's title, H1, and body cover the "checker" phrasing. Handed to Codex in
`TOOL-COPY-BRIEF.md`. That is 150/mo capturable for the price of a title edit.

---

## What got built instead, and why it clears the bar

**AI Crawler Access Checker** — `/ai-crawler-checker/`, cluster 4
(`ai-search-optimization`).

Enter a domain or paste a robots.txt; get a per-platform verdict on whether the file
permits **citation** in AI answers, separately from whether it permits **training**.

### It beats every remaining candidate on volume

**[VERIFIED]** Semrush US, pulled 2026-08-17 (`phrase_these`). Ahrefs was unavailable —
see the note at the end.

| Keyword | Vol/mo | CPC |
|---|---:|---:|
| claudebot | 3,600 | $6.41 |
| robots.txt checker | 2,400 | $4.27 |
| robots.txt validator | 1,600 | $5.09 |
| robots txt tester | 880 | $3.58 |
| **oai-searchbot** | **720** | **$10.81** |
| gptbot | 390 | $1.66 |
| google-extended | 260 | $1.69 |
| ai crawlers | 170 | $6.27 |
| llms.txt checker | 110 | $5.18 |
| perplexitybot | 70 | $8.13 |
| claude-searchbot | 20 | $12.89 |
| ai crawler checker | 20 | $8.46 |
| gptbot robots.txt / block ai crawlers / ai bot blocker / how to block ai crawlers | 20 each | — |

**Honest caveats on these numbers, because the headline is easy to overstate:**

- **The bot-name queries are partly informational.** Someone searching `claudebot` may
  only want to know what it is. I am not claiming we capture 3,600/mo. The tool-intent
  core is the checker/validator/tester family at **4,880/mo**, with the bot-name queries
  as a natural follow-on once someone knows the agent exists.
- **`robots.txt checker`, `validator`, and `tester` are owned by incumbents** — Google's
  tester, TechnicalSEO, Merkle. A generic robots.txt syntax checker would be a thin
  me-too, which is the trap again. **The tool is positioned on the AI citation-versus-
  training matrix**, which no generic tester does, and it happens to do correct RFC 9309
  matching underneath.
- **The two sources disagree on volume.** Semrush puts `ai overviews checker` at 390/mo;
  the Ahrefs-derived figure in `addressable-universe.md` is 700. Both are estimates.
  Where they conflict, treat the order of magnitude as the signal and the exact figure as
  noise.

Even on the conservative read, the addressable family is several times the 250/mo of the
best remaining list entry.

### It clears the "is this really a tool" test, which is the part that matters

**Input the reader has:** their domain, or a robots.txt they are about to ship.

**An answer they cannot get by reading:** yes, and this is the crux. robots.txt matching
is genuinely counter-intuitive. Under RFC 9309 **only the single most specific matching
user-agent group applies** — naming a crawler *replaces* the `*` group for it rather than
adding to it. An article can state that rule; it cannot tell a reader what their own file
does with it. Add per-platform agents that change over time, path-specific rules, and the
longest-match precedence rule, and the answer is a computation, not a fact to look up.

**Evidence the confusion is real, from this campaign:** ninadpathak.com's own robots.txt
blocks `ClaudeBot`, `GPTBot`, `Google-Extended`, `CCBot` and more. It looks hostile to AI.
It is in fact a clean training opt-out that preserves **every** citation crawler, and
anyone auditing it casually would "fix" it wrongly. The tool exists to prevent that
mistake in both directions.

**In-niche:** cluster 4 exactly, alongside `/ai-overviews-checker/`. Per the campaign
doc, cluster 4 is "the tools cluster".

**Constraint-clean:** paste path is fully local; the domain path transmits a domain and
nothing else; zero new CSS; no login; no lead capture.

**Structurally protected:** tool-intent queries in this space carry no AI Overview, which
is the finding that made tools the campaign's priority lever.

### What it refuses to claim

- **No score.** The headline is a count of citation crawlers allowed. There is no correct
  number of permitted crawlers, so weighting one would invent a judgement.
- **A training opt-out is not a defect.** It is reported separately and never counted
  against the headline.
- **robots.txt is not enforcement.** Every report says a CDN or WAF can block a crawler
  at the edge regardless, and that a crawler can ignore the file. The tool reports what
  the file permits, which is a different statement from what reaches the site.

---

## Blocker to record

**Ahrefs MCP returned `Access denied: MCP token is invalid` on 2026-08-17.** Every
endpoint. Per the charter this is the one class of thing to raise: an authentication
failure I cannot resolve. I did not block on it — Semrush covered the volume question and
WebSearch covered SERP intent, both free — but the Ahrefs-only capabilities are
unavailable until the token is refreshed. Brand Radar remains separately unavailable as a
missing add-on.
