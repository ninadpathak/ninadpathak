# ninadpathak.com 90-day organic search campaign

**Campaign window:** 17 August to 15 November 2026
**Target:** 10,000 organic visits per month by day 90
**Baseline, 2026-08-17:** 16 clicks/month (July), of which ~12 are the brand query `ninad pathak`. Non-brand human clicks are approximately zero.
**Measurement source of truth:** Google Search Console, `sc-domain:ninadpathak.com`, read with the workspace service account. First-party, free, no Ahrefs units.
**Governing charter:** `~/.claude/orchestration/ninadpathak-seo/CHARTER.md`. Where this document and the charter disagree, the charter wins and this document gets corrected.

This file is the campaign's durable memory. It lives in the repo, not only in an orchestration folder, so every agent and every future session reads the same source of truth from the checkout. Measurement refreshes are **appended in place with their date**, never rewritten, so the document carries its own history.

---

## 1. Honest position, and what the numbers actually said

The brief handed to this campaign said impressions had roughly 4×'d while clicks stayed flat, and read that as a title-and-snippet problem. It was checked before being acted on, and it was not that.

| Month | Clicks | Impressions | CTR | Avg position |
|---|---|---|---|---|
| 2026-05 | 13 | 825 | 1.58% | 19.6 |
| 2026-06 | 14 | 1,754 | 0.80% | 17.7 |
| 2026-07 | 16 | 2,476 | 0.65% | 13.1 |
| 2026-08 (1–15) | 8 | 971 | 0.82% | 16.0 |

Three findings, all verified on 2026-08-17:

**The impression growth was not human.** *(Refined in the fifth-cycle refresh: the sitewide machine share is a range of 1.8% to 52.9% because Search Console withholds half of all impressions. The per-page concentration below is solid; the sitewide claim was overstated.)* 2,263 of the 5,300 impressions between 1 June and 15 August landed on one URL, `/blog/how-anthropics-contextual-retrieval-changes-rag-architecture/`, at average position 8.3 with zero clicks. The queries reaching it are forty-plus permutations of a single keyword salad: `anthropic contextual retrieval bm25 embeddings reranking official`, `…official contextual embeddings bm25 reranking`, `…bm25 embeddings reranking official 2024`. Position 8–10, zero clicks, every variant. That is machine query fan-out, not people. Optimising titles and snippets against it would have been weeks of wasted work.

**Every non-brand impression the domain had ever earned was pointing at a 404.** Commit `b846597d`, 2026-07-30, "Refocus site for documentation authority," set `status: retired` or `status: review` on 68 posts and six topic hubs. `build.py` deliberately writes no redirect for a removed URL, on the reasonable general principle that a soft 404 is worse than a real one. Applied to a page at position 8.1 carrying 86% of the site's July impressions, it was wrong. Fixed 2026-08-17, see the execution log.

**The documentation pivot had no search footprint.** All 21 live `/articles/` pages combined: 106 impressions, 1 click, average position 49 in August.

**All real clicks are brand.** `ninad pathak`, 12 clicks at position 2.8.

### Why the target is honest but very unlikely

The first research pass priced the documentation niche at 68,870 searches/month across 350 keywords. That figure was later found to be 7.5% overstated by contaminated rows, and the real documentation number is 63,730 — see the 2026-08-17 measurement refresh in section 10. Ten thousand visits would mean capturing 14.5% of every search in the entire niche, from position 49, in ninety days, against Postman and Swagger. That is not a pessimistic reading; it is the ceiling of the measured universe.

The niche was widened on 2026-08-17 (see section 3) precisely because of that arithmetic, so the denominator has changed. The revised band is recorded as a dated refresh in the execution log rather than asserted here. What does not change: the distance to 10,000 is reported every week, plainly, and the trajectory is described as reaching it or not reaching it. Activity is never presented as progress.

---

## 2. Tool-first directive

Build genuinely useful public tools wherever the SERP shows a calculation, checking, validation, or planning job. Tools earn links and citations that articles do not, they win tool-intent SERPs without domain authority, and `static/css/linter.css` is already a complete "input → graded findings" kit, so a new tool costs zero CSS.

A tool must work in the browser with no login and no lead capture, expose its method and assumptions, avoid invented precision, and never transmit what the user pastes into it. Deterministic tests are required.

`/linter/` and `/llms-txt-generator/` already exist. The generator has earned **three impressions in its entire life** — not because it is bad, but because nothing links to it, it carries no schema, and its title and description were never written for search. That is the campaign's clearest example of an asset left on the floor, and it is being fixed first.

**Tools are protected from the thing that is eating everyone else's traffic.** All fifteen highest-value keywords in the seven-cluster niche carry a Google AI Overview. None of the nine build-a-tool keywords do. AI Overviews cost roughly 35% of clicks on the SERPs that have them, and 49.2% of this niche's SERPs have one. That makes tool intent the only traffic profile in the niche that an AI Overview does not tax — a structural advantage, not a temporary one.

Build order, by evidence:

1. **AI Overviews checker** — `ai overviews checker`, 700/month, **KD 0, no AI Overview on the SERP**. The cleanest opportunity in the entire dataset. KD zero at 700/month with no AIO competition does not appear twice.
2. **llms.txt validator** — validation is a different intent from generation and deserves its own URL. The tool-intent subset of the llms.txt family is 550/month. An earlier draft of this document sized it at ~7,000, which was the whole family including a KD-56 head term; that was wrong and the correction is in the 2026-08-17 refresh.
3. **Discoverability for what already exists**, which is where the generator's three lifetime impressions came from.

---

## 3. The niche, and the cluster map

Settled 2026-08-17. The July 30 narrowing to pure documentation was too narrow and the arithmetic proved it. Scope is now the whole of what Ninad actually does — one person's job: getting a technical product understood and adopted. Distribution is not off-topic for a technical writer; it is half the work.

**All-encompassing in scope, strictly clustered in structure.** Breadth without clustering reads as an unfocused personal blog to Google and to a reader, and dilutes every topic.

Volumes are **post-sweep** (`planning/research/CONTAMINATION-SWEEP-2026-08-17.md`), after the
llms.txt reassignment below. **Total 293,800/mo across 940 keywords, not the 336,180 quoted
before the sweep.** Do not quote the old figure again.

| # | Cluster | Vol/mo | Owns | Owner page | Posts |
|---|---|---:|---|---|---:|
| 1 | Technical documentation and docs operations | **54,310** | The commercial cluster, tied to the consulting offer | `/articles/technical-documentation/` | 23 |
| 2 | Developer experience and DevRel for DevTools and B2B SaaS | 6,040 | Content that makes a developer product adoptable | `/articles/developer-experience/` | 8 |
| 3 | AI agent architecture, agent memory, RAG, LLM inference | 149,790 | The revived cluster; the only search equity the domain has earned | `/articles/ai-engineering/` | 57 |
| 4 | Optimising for AI Overviews and AI search citation | **30,980** | The tools cluster: `/linter/`, `/llms-txt-generator/`, the AI Overviews checker, the llms.txt validator | `/articles/ai-search-optimization/` | 3 |
| 5 | Distribution: Reddit, forums, communities, and events | 52,680 *(floor)* | Credibility, first-hand. **Merged 2026-08-17** from three clusters | `/articles/distribution/` | 0 |
| | **Total** | **293,800** | | | **90** |

**Clusters 5, 6 and 7 are floors, not measurements.** They hit the 250-row API cap before the
sweep ran, so their true keyword sets are larger than recorded. Cleaning a floor leaves a floor:
the sweep removed 45%, 34% and 44% of their volume respectively, which makes the recorded number
more accurate without making it complete. Treat them as lower bounds and do not size a calendar
from them. Their intent problem is separate and worse, and is recorded in §10.

**llms.txt moved from cluster 1 to cluster 4 on 2026-08-17.** The sweep found 53 keywords with no
parent topic totalling 8,760/mo, and correctly established that a missing parent is **not**
evidence of contamination: they are all llms.txt terms, legitimate, simply too new for the index
to have assigned parents. By subject they belong to AI-search citation, which owns all four live
tools and both new articles. Leaving them in documentation would put the tools cluster's demand
inside the commercial cluster and leave neither owning it, which is the page-in-two-clusters
failure the isolation rule exists to prevent. Cluster 1 goes 63,070 to 54,310 and cluster 4 goes
22,220 to 30,980, making it the **second-largest cluster** in the niche.

Clusters 5, 6, and 7 are new scope and they matter for a reason beyond volume: they are things Ninad genuinely does, so they pass the falsifiability test in section 4 where invented documentation war stories do not.

**Seven clusters became five on 2026-08-17.** Reddit, forums and events merged into one
Distribution cluster. **No topic was dropped and the scope settled in CHARTER 2c-bis is
unchanged** — only the container changed. The isolation rule's own logic forced it: the rule
requires every cluster to have one owner page covering the whole job, and clusters of 3, 4 and 5
rows cannot each have an owner page that owns anything. Merging makes the rule satisfiable rather
than aspirational, and it **removes** a cross-cluster exception instead of adding one.

The decisive argument was empirical, not arithmetic. A brief for the community owner page needed a
stop instruction, because it opened a cluster with no publishable siblings and could not honestly
meet the two-outbound minimum. That is a structural failure surfacing in the work rather than a
theory about it, and row 49's stop instruction disappearing is the tell that the structure was
wrong rather than the writing.

Verified before applying, not assumed: none of the three old slugs ever rendered. No directory in
`output/`, no sitemap entry, and **zero commits in the entire repository history** placed any of
them in a built sitemap. No post ever declared them. So no redirect was needed and nothing was
indexed.

> **Distribution is a credibility cluster, not a traffic cluster. Twelve rows is its ceiling, not a
> starting allocation, and it must not grow on the strength of a floor figure.**

That 52,680/mo is three capped, cleaned floors added together. It is exactly the number that would
justify overinvesting, which is why the ceiling is written down here rather than left to memory.

### Cluster isolation — a hard structural rule

1. Every piece belongs to **exactly one** cluster, named in its queue row. A page in two clusters owns neither.
2. Each cluster has one owner page covering the whole job, plus supporting pages owning one sub-job each, linking back to the owner and sideways to genuine siblings.
3. **Clusters do not link across boundaries.** A documentation piece does not link to a Reddit piece or an events piece. The single exception is when the link is the actual subject of the sentence — a documentation piece may link to a blog-writing piece if it is specifically discussing blogs as supporting material for docs. Convenience, "related reading", and keyword proximity never qualify.
4. When a cross-cluster link genuinely earns its place it goes in the body sentence that makes the connection explicit, never in a sidebar or footer list.
5. Audit this map every cycle.

### Depth, heading structure, and the components already built

Added 2026-08-17. Four requirements, all binding on the writer and in all three Hermes skill copies at v1.8.0 plus the publish prompt.

**Nested headings, because this is what an answer engine extracts.** A flat run of `h2`s gives an extractor no way to tell where one idea ends, so boundaries land arbitrarily. Each `h2` is one complete chain of thought — a whole stage of the argument, not a paragraph label. The `h3`s under it are the steps within that chain. The next `h2` starts the next chain. Never skip a level, never head a single short paragraph, and **never leave an `h2` with exactly one `h3`** — if there is only one sub-step, it is not a sub-step. Put a question or decision in the heading and answer it immediately in a passage that names its own subject and conditions; that passage is what gets quoted. Google reads the outline for scope, answer engines lift the passage — flat structure loses both.

**The diagram system has never been used once.** `static/css/flowcharts.css` is a complete 14-class system, and only `.flowchart-image`, its SVG figure wrapper, appears anywhere on the site. That is why the newer documentation articles read flatter than the older AI-cluster posts. Standing order 4 forbids new CSS; it does not forbid using what is built. Where a piece explains a flow, a decision, a hierarchy or a comparison, build the diagram — relationships made explicit are strong AI-search assets, because an extractor can lift a structure it can see.

The DOM in the skill is **verified by rendering it in a browser, not derived from the class list**, and that mattered: `.flowchart-branch` and `.flowchart-outcome` are positioning wrappers only, so each needs a `.flowchart-node` nested inside. Putting `strong` and `small` directly in an outcome renders them run together with no card, because only `.flowchart-node` styles them. Documenting the class list alone would have had every writer producing that.

**Glossary entries earn citation by being the best available answer, not by existing.** A 273-word entry under a fixed "How It Works / Common Use Cases / Related Terms" tree is a template wearing a definition. Each entry needs a self-contained 40-to-80-word opening definition that survives being lifted off the page with no pronoun pointing back at the title, then real depth — origin, what problem it was coined to solve, how it differs from the adjacent terms people confuse it with named explicitly, when it does not apply, the common misuse and why. **At least one concrete worked example, and examples are the priority: a definition plus a real example is worth three definitions.** Headings come from the term, never a template. A term that cannot support depth gets **merged into a related entry rather than shipped as a stub** — twenty-six strong entries beat forty thin ones, and thin entries drag the cluster.

**Important links are destinations, not an inventory.** The footer listed five tools individually, splitting link equity five ways and diluting further with each addition. It now carries one `Tools` link to `/tools/`, which lists and describes each tool and is the tools cluster's owner page. A footer or nav slot holds a top-level destination a reader actually wants; the inventory lives on the page behind it.

### A link profile is a diagnostic for editorial substance

Added 2026-08-17, and it changes what internal linking is for. **If every outbound link on a page fails the subject-of-the-sentence test, the page is telling you it has no natural neighbours.** The cause is almost always that the page holds an abstraction while other pages own each concrete piece of its argument, and an abstraction has no neighbours, so every link has to be manufactured. **Review the page. Do not replace the links.**

It was found the hard way. `technical-content-as-a-moat-the-long-game-for-developer-tools` had three outbound links; all three failed the test, and stripping them left zero. It also had no inbound links, no impressions, no entry in the movement table, and no update since April, in the smallest cluster on the site. Manufactured links were the only thing making it look connected. It is being consolidated into the page that owns the concrete version of its argument, carrying over the two ideas that page does not already have.

The rule is in all three copies of the Hermes `ninadpathak-content` skill at version 1.7.0, so the writer applies it rather than only the reviewer catching it.


**Known structural debt:** the July 30 refocus collapsed all twelve topic pillars into anchors on one page, `/articles/#<slug>`. An anchor cannot own a cluster — no unique URL, no unique title, no unique canonical, so twelve clusters shared one ranking surface and none of them ranked. Five AI hub slugs and `/glossary/` were redirected on 2026-08-17 to stop them 404ing, and every cluster now has a real owner page. The four clusters with no content yet are declared here but render nothing until they have some, so an empty owner page cannot ship.

---

## 3a. Order of operations across the clusters

Added 2026-08-17. The queue is date-sorted, which is a schedule and not a sequence. This section
says what has to exist before the next thing can land, and which rows are therefore blocked on
which. It governs the remaining **60 Planned rows**.

### The constraint that sets the whole order

The domain went through a **spam injection and a full rebuild inside twelve months**: 440 injected
pages, 829 impressions in October 2025, Japanese-language sections. Foreign impressions hit zero
from April 2026 and the last 90 days are clean.

Two consequences bind the sequencing.

**Any historical position improvement on this domain is suspect until the denominator is checked.**
The move from average position 23.1 to 7.2 is a composition artifact: the deep-position tail was
deleted and brand queries were left behind. It is not a gain and must not be cited as one.

**This is neither a fresh domain nor a domain with clean accumulated trust.** It carries a
compromise and a rebuild. New pages should be expected to earn slowly, which means the order should
front-load the things that do not depend on accumulated domain trust: **tools, which rank on
utility and links rather than history, and pages built to be cited rather than ranked.** That
single fact is why cluster 4 goes first.

---

### Cluster 4, AI search — the priority lever, and it goes first

**Why first.** No build-a-tool keyword in this niche carries an AI Overview, while all 15 top
keywords do. Tool intent is the only demand profile an AI Overview does not tax, and it is also the
profile least dependent on domain trust. Cluster 4 is 30,980/mo and already holds five live tools.

**It is currently a pile, not a cluster.** Five tools, three articles, and no page that covers the
whole job. The clearest evidence: `/llms-txt-generator/` has earned **three impressions in its
entire life**, not because it is bad but because nothing links to it.

**The minimum set that makes it a cluster, in dependency order:**

| # | What it delivers | Row | Blocked on |
|---|---|---|---|
| 1 | **Tool routing.** Gives a live tool its first real inbound link from an article. | **36** (check AI Overviews → `/ai-overviews-checker/`) | nothing. Ship earliest. |
| 2 | **The owner.** One page covering the whole job, that every other page links back to. | **35** (AEO anchor) | nothing |
| 3 | **The definitional spine.** Stops the cluster arguing with itself about terms. | **38** (AEO/GEO/SEO) | 35 |
| 4 | **The standard.** What is actually agreed in llms.txt. | **39** | nothing |
| 5 | **Tool routing, second pair.** Routes the generator and validator. | **57** (llms.txt format guide) | 39 |
| 6 | **Structured-data sub-job.** | **40** (schema markup) | 35 |
| 7 | **Evidence.** | **50** (visibility test) | **time, not content** |

**The blocking relationships that matter:**

- **36 must not wait.** It is the only row that fixes an orphaned tool, it is Experience A, and it
  depends on nothing. It is currently 09-03, one day after the owner. That is acceptable but it
  should never slip behind 35 if the anchor is delayed.
- **57 is blocked on 39**, because a format guide that contradicts the standard page is worse than
  no format guide. 39 is 09-06 and 57 is 09-24, so this holds.
- **50 is blocked on an observation window, not on a page.** Its brief already authorises publishing
  the pre-registration instead of a conclusion. That is the correct outcome, not a fallback.
- **40 is blocked on 35** only for its framing, and can move if the anchor slips.

**What "behaves like a cluster" means concretely here:** every one of the five tools has at least
one inbound link from an article that explains when to use it, and every article links back to the
owner. Rows 36 and 57 deliver four of the five. `/linter/` and `/ai-crawler-checker/` are not yet
routed by any planned row, and that is the gap this sequence leaves open. **Flagged rather than
filled:** it needs either a row or a retrofit, and a retrofit is cheaper.

---

### Cluster 3, AI engineering — consolidate, do not add

**The honest answer is that addition is wrong here, and the evidence is not close.**

57 live posts. 149,790/mo, the largest cluster by volume. **65% AI Overview saturation, the worst
of any cluster, and only 40% of its volume at KD≤20, also the worst.** High volume, high friction,
and the highest tax on any new page.

The GSC picture is decisive. 44 cluster-3 pages sit at average position 11.5 on 1,191 impressions,
which reads like a goldmine and is not: those impressions are the `anthropic contextual retrieval`
28-variant fan-out and its relatives. **No human is behind them.** Meanwhile the site's three real
striking-distance queries are all cluster 3, and all three map to pages that already exist.

Adding 12 posts to 57 that are not earning does not fix a cluster that is not earning. It makes it
larger.

**What the 12 planned rows actually contain:**

- **Five chunking and retrieval variants** — rows 63, 68, 69, 70, 71. This is precisely the
  "keyword variations that belong on the same page" failure. Only 63 carries an artifact.
  **Collapse into 63 and skip 68, 70, 71.** Keep 69 only if heading-aware chunking survives its own
  parent-topic check against 63.
- **Two documentation-chatbot rows** — 74 and 75, both `C`, overlapping each other.
  **Collapse into one or skip both.**
- **Five genuine gaps** — rows 72, 73, 76, 77, 78: tool schema design, agent evals, observability,
  prompt injection, circuit breakers. All five are listed in `planning/content-roadmap.md` as posts
  that existing published articles already link toward and that were never written. They are
  demand-backed by the corpus itself rather than by a keyword tool. Keep all five.

**Net: cluster 3 goes from 12 planned rows to about 6**, and the freed slots do not get refilled
with more cluster-3 content.

**What replaces the addition:** a consolidation pass over the existing 57. Nothing in the plan
currently schedules one, and it is the highest-value work available in the largest cluster. It is
not briefed here because it needs a page-level audit first, of the kind that produced the
`technical-content-as-a-moat` verdict. **That audit is the next structural job after this section.**

---

### Cluster 1, Documentation — order serves the offer, not the volume

**Yes. Its order must serve the consulting offer, and that changes the sequence.**

26 planned rows, the largest remaining block, and the only cluster tied to money. A buyer evaluating
a documentation consultant does not read a definitional explainer. They look for evidence that the
person has done the work: a template they can open, an audit with a method, a tested comparison, a
worked example with its failures visible.

**So the ordering rule for cluster 1 is: artifacts before explainers.**

- **Front:** the docs-as-code trio (31, 32, 33) and the artifact rows around it — 34, 41, 42, 45,
  47, 48, 52. These are Experience A, they point at this site's own tooling and its own migration,
  and they are what a buyer inspects. **Already front-loaded, which is correct.**
- **Middle:** the format and operations rows that show range — 43, 51, 54, 55, 58.
- **Back:** the definitional and `C`-tier rows — 26 (what is software documentation) and its
  relatives. They serve volume, not the offer, and moving them later costs nothing because nothing
  is blocked on them.

**Blocking inside cluster 1 is mostly one-directional and already respected:** 29 (worked example)
and 30 (tooling) are blocked on 20 (the decision rule), because an example of a rule not yet stated
is just code. 52 (repository tour) is blocked on 31 (the workflow it tours). 47's troubleshooting
template is blocked on nothing and can move freely.

**One ordering defect to fix:** row 26 is a `C`-tier definitional page scheduled for 08-24, ahead of
most of the artifact rows. It should trade places with a later artifact row. Not urgent enough to
churn the queue for, but it should not be repeated in the next fortnight's planning.

---

### Clusters 5, 6 and 7 — not viable as clusters. Merge them into one.

**The honest answer is that at 4, 5 and 3 rows they cannot function as clusters, and pretending
otherwise will produce three owner pages that own nothing.**

A cluster needs an owner page covering a whole job, supporting pages each owning a sub-job, and
enough mass for the supporting pages to link to each other. Three to five near-zero-volume pieces
deliver none of that. The evidence is already in the briefs: **row 49's brief had to carry a stop
instruction** because it opens a cluster with no published siblings and may not be able to meet the
two-outbound minimum honestly. That is a structural failure, not a writing problem.

Their content is still worth publishing. All twelve rows are Experience A or B on ground Ninad
genuinely has, and they pass the falsifiability standard where invented documentation war stories
do not. The problem is the container, not the pieces.

**Decision: merge 5, 6 and 7 into a single cluster, Distribution.**

| | Before | After |
|---|---|---|
| Clusters | 3 | **1** |
| Rows | 4 + 5 + 3 | **12** |
| Volume (all floors) | 18,300 + 15,910 + 18,470 | **52,680/mo** |
| Owner pages needed | 3, none earnable | **1, earnable at 12 pieces** |

The job is coherent and states in one sentence: **getting a technical product in front of the
developers who would use it.** Reddit, forums and events are three venues for one job, which is
exactly what a cluster is, and splitting them was an artifact of how the niche was first written
down rather than a real boundary.

**What this fixes immediately:** twelve pieces can interlink without a cross-cluster exception, so
row 49's stop instruction becomes unnecessary. An owner page becomes earnable. And the isolation
rule stops forcing three-page clusters to link only inward to two siblings.

**What it does not fix:** the volume is still floors from a capped pull, and the head terms of all
three were contaminated. Distribution is a **credibility cluster, not a traffic cluster.** Size it
that way. Twelve rows is the ceiling, not a starting allocation, and it should not grow on the
strength of a floor figure.

**Applied 2026-08-17.** Seven clusters became five, in `config.toml`, in the queue's twelve rows,
and in §3 above. The venue survives as `Subcluster` (Reddit 4, communities and forums 5, events 3)
so planning granularity is not lost. `tools/daily_cycle.py` now asserts `/articles/distribution/`
alongside the other owner pages; its check skips URLs the build does not produce, so the assertion
is inert until the first Distribution piece ships and becomes live the moment it does.

---

### The resulting order, in one table

| Priority | Cluster | Rows | Why here |
|---:|---|---:|---|
| 1 | AI search | 7 | Tool intent is untaxed by AI Overviews and least dependent on the damaged domain trust. Fixes five orphaned tools. |
| 2 | Documentation | 26 | The commercial cluster. Artifacts first, explainers last. |
| 3 | AI engineering | ~6, down from 12 | Consolidation beats addition at 57 posts and 65% AIO. Freed slots are not refilled. |
| 4 | Distribution (5+6+7 merged, applied) | 12 | Credibility, not traffic. Viable as one cluster, not as three. Ceiling, not a starting allocation. |
| 5 | DevEx and DevRel | 3 | Smallest at 6,040/mo. Search Console reports 4 of its pages, carrying 1 click on 32 impressions. Kept, not grown. |

**Rows freed by the cluster-3 collapse: about 6.** They should stay empty or be spent on the
cluster-3 consolidation audit, not refilled with new cluster-3 posts. An empty slot is a scheduling
problem; a thin article in a saturated cluster is a permanent one.

## 4. The voice standard

Ninad is a former engineer who became a technical writer. He has shipped documentation for developer products and built this site's tooling. Judgment earned from that work is fair game. Events and measurements he did not make are not.

**The test every first-person claim must pass: could a reader who knows the subject point at this sentence and say "that is bullshit"?** If yes, it does not ship. Not softened, not hedged — removed.

**Unfalsifiable-safe is not the goal.** "I have reviewed a lot of API docs" is safe and worthless. The goal is claims that are both specific and true.

| | Example | Why |
|---|---|---|
| **PASSES** | "A reference page that documents an endpoint's parameters but not its failure modes is the most common gap I look for, because it is the one that generates support tickets." | A stated judgment about what he looks for and why. Specific, useful, and not a claim about an event that can be checked and found absent. |
| **PASSES** | "Anthropic reported contextual retrieval cutting failed retrievals by 49%." | Attributed to its real source. The number is checkable and correctly owned. |
| **FAILS** | "The latency cost runs 30ms to 50ms per turn on Gemini 3.1 Flash Lite for the summarization pass." | A specific measurement presented as his own. If he did not run it, one reader with a stopwatch destroys trust in every other number on the site. |
| **FAILS** | "My current implementation uses a document store keyed by user ID, and SQLite on local NVMe handles 50,000 fact records." | A named implementation and a throughput figure for a system no reader can inspect. Bare numbers with no artifact are the worst case. |
| **FAILS** | "I built a small tool selector." | Technically true and carries no information. The script exists so a first-person sentence has something legal to point at. |

**Silence beats invention.** A researched explainer that makes no personal claim at all is a fully legitimate article and an explicit third path. Say so plainly in the piece rather than manufacturing a story to satisfy a template.

An article's evidence artifact must clear one question: **does it test anything the article did not already assume?** A checker that verifies a fixture the same run authored carries zero information. That question rejected all five articles reviewed on 2026-08-17.

---

## 5. Target classes

Never publish a thin page to hit a calendar slot. Every target query carries a class:

- **A** — top 10 by day 90. Low difficulty, clear intent, an owner page that covers the whole job.
- **B** — top 20 by day 90.
- **C** — top 50 plus sustained non-brand impressions by day 90.
- **G** — must clear an evidence gate before publishing at all. A page with no first-hand ground, no artifact, and nothing to add stays unpublished.

Class assignments live with the keyword universe, not here, so they can be revised without editing this document.

---

## 6. Research credit policy

Before any paid lookup, **search the saved research first**: `planning/research-cache/`, `planning/semrush-opportunity-backlog.csv`, `planning/addressable-universe.md`, `planning/90-day-seo-ai-strategy.md`.

A new paid request requires a **named keyword and the decision it will change**. Do not poll on a content or tool cycle. Do not refresh a frozen historical baseline.

Every call is appended to `planning/research-cache/CALL-LOG.md` with UTC timestamp, tool, query summary, row count, units, and cache filename — **including any empty response**, so the same keyword is never bought twice. Raw JSON is saved beside it.

Ahrefs `keywords-explorer-matching-terms` in terms mode with four or five seeds per call is the efficient shape. Brand Radar is unavailable on this subscription (`Missing addon`), so the AI-search half of the strategy is built on the `serp_features` AI Overview flag plus free SERP and page reads. The strategy says so rather than implying it has citation data.

---

## 7. Internal linking

1. **Links come from the freshly built sitemap, never from memory.** Run `python build.py`, then read `output/llms.txt` and `output/sitemap.xml`. `llms.txt` is the better instrument: every live article grouped by topic with its canonical URL and a one-line description, which is what lets a writer pick a link that genuinely belongs in the sentence.
2. Every piece has at least one **inbound** link from an existing page and at least two outbound.
3. **Retrofit as you go.** When a piece publishes, update the existing pages that should now point at it. A link added in one direction only is half a link. This is a per-cycle job, not a cleanup.
4. Links go inside sentences where they help a reader go deeper. Never a "Related posts" dump. Never "click here", "this article", or a bare keyword as anchor text.
5. Respect cluster isolation, section 3.

---

## 8. Publish gate

Every piece clears all of these, and each is **verified rather than trusted** — a gate that fails silently is worse than no gate:

1. `python build.py` passes.
2. `rule_checker.py` adds no new errors.
3. Every internal link resolves to a URL present in the built `output/sitemap.xml`.
4. `git diff --stat main -- static/css/` is **empty**. No new CSS, ever.
5. The topic appears nowhere in `output/llms.txt` or the queue's Published rows.
6. Reviewed by the **opposite model** from the one that wrote it. Hermes writes with `gpt-5.6-terra`; the slop review is Codex `gpt-5.6-sol`; strategy and code are Claude. A model never grades its own family's output.
7. The piece has its inbound retrofit, not just outbound links.
8. Its cluster is named and it belongs to exactly one.

---

## 9. Explicit limits

Stated plainly, because a campaign that hides its uncertainty cannot be corrected:

- **No honest campaign can guarantee 10,000 visits/month by 2026-11-15.** The measured universe, the domain's near-zero authority, and an average position of 49 on the current content all argue against it. The target is not abandoned and distance to it is reported weekly, but it is not promised.
- **Publication is not a ranking.** Nothing in the execution log counts as a result until Search Console shows impressions and positions for it.
- **AI-search citation cannot be measured on this subscription.** Brand Radar is not entitled. Claims about AI Overview presence rest on the `serp_features` flag and manual SERP reads, and are labelled as such.
- **A revived page is not yet a repaired page.** The AI cluster was restored from 404 on 2026-08-17 because a page at position 8 can be repaired in place while a 404 earns nothing and decays. It carries 349 `rule_checker` errors and several first-person claims that fail section 4. Repair is in flight, in Search Console value order, and the debt is stated rather than quietly carried.
- Ranking movement depends on recrawl and indexation, neither of which is controllable. Timelines assume Google behaves as it did during the campaign's baseline period.

---

## 10. Execution log

Dated entries, appended in place. Each says what changed, what it is expected to do, and how it will be judged.

### 2026-08-17 — 404 recovery, and the diagnosis that redirected the campaign

Commit `4862c2d5` on `main`.

- Verified the handed-down framing before acting on it. "Impressions 4×'d with flat clicks, so fix titles and snippets" was wrong: the impression growth is machine query fan-out against a dead URL, forty-plus permutations of one keyword salad at position 8–10 with zero clicks across every variant. Chasing CTR there would have cost weeks.
- Found that 68 pages and six topic hubs were returning hard 404s, and that those dead URLs carried 86% of July's impressions.
- Restored 67 posts and six hubs to `status: published`. Only `uv-package-manager-benchmark` stays retired, because no cluster owns Python packaging. `/blog/<slug>/` now 301s to `/articles/<slug>/` for all of them. Verified live: the position-8.1 URL returns 301 → 200.
- Redirected the five AI hub slugs and `/glossary/` instead of 404ing them.
- Built `tools/reflow_paragraphs.py`. `build.py` hard-fails any post whose paragraphs exceed two sentences, a rule added after these articles were written, and all 67 failed it with 700+ violations. That mechanical failure, not an editorial judgment, is why the set sat retired. The tool wraps the formatter already in `rule_checker.py`; it regroups existing sentences and rewrites no prose.
- Built `tools/fix_internal_links.py`. Repointed 294 legacy `/blog/` body links across 68 files, taking the build's broken-internal-link count from 292 to 0 and clearing the 31-hard-404 debt from the August audit.
- Corrected `text-embedding-3d-small` to `text-embedding-3-small`, the wrong OpenAI identifier flagged as highest priority in the August audit, on a page that was about to go live at position 28.
- Sitemap 39 → 109 URLs. Build green, SEO audit passes, no CSS touched.

Expected first-order impact: recovery of already-earned positions rather than new demand. The flagship's impressions are machine traffic and will not convert to human clicks, so the honest expectation is hundreds of visits, not thousands — the human value is in the pages at positions 20–28 on real queries (`embedding models compared`, `hybrid search bm25 vector search`, `kv cache eviction`) and in restoring the domain's topical association. Judge it on non-brand clicks in Search Console from week commencing 2026-08-24, not on the sitemap count.

### 2026-08-17 — slop review: 0 of 5 Hermes articles pass

`planning/slop-review-2026-08-17.md`, produced by Codex `gpt-5.6-sol` because Claude commissioned the work and a model must never grade its own family's output.

Every one of the last five published articles was rejected. Six named generator defects, each traced to a specific instruction:

- **G1 unconditional artifact** — "build, run, or audit a real evidence artifact" every run produces a toy checker even when the subject needs research or judgment.
- **G2 mandatory first person** — turns pipeline activity into claims in Ninad's voice.
- **G3 mandatory evidence ceremony** — forces exact commands, exact PASS strings, and pixel-specified screenshots into prose.
- **G4 fixed cold-run structure, no rolling structure log** — all five converge on an identical skeleton: generic failure mode, "I built", framework table, authored fixture, PASS, terminal screenshot at the same `2560/1664` dimensions, two-link conclusion.
- **G5 objection slot** — "The strongest objection is that…" appears in four of five, in the same position. A prompt slot showing through the prose.
- **G6 link quota without retrofit** — the internal-link rule is being satisfied outbound-only. Nothing updates an existing page to give the new article its inbound link, so every piece ships half-linked. This defect was found by the reviewer, not briefed to it.

The single question that killed all five artifacts: does the artifact test anything the article did not already assume? In every case the script checked fields the same run chose, against a fixture the same run authored.

Fixes are being made in the generator — the publish prompt and all three copies of the `ninadpathak-content` and `devtools-blog-craft` skills — not in the five outputs. Judge it on whether the defects recur in pieces published after the edits land.

### 2026-08-17 — measurement refresh: the full-niche universe, and the revised band

`planning/addressable-universe.md` on branch `seo/analytics`. Seven paid Ahrefs calls, 25,540 units, one under budget. Cluster 1 was reused from the bank, not re-bought.

| # | Cluster | Keywords | Volume/mo | KD≤20 kws | KD≤20 vol | KD≤20 share | SERPs with AI Overview |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Technical documentation and docs ops | 322 | 63,730 | 220 | 31,730 | 50% | 111 |
| 2 | Developer experience and DevRel | 56 | 7,930 | 54 | 7,190 | 91% | 26 |
| 3 | AI agents, memory, RAG, inference | 347 | 150,140 | 217 | 60,650 | 40% | 226 |
| 4 | AI Overviews and AI-search citation | 58 | 23,880 | 42 | 11,890 | 50% | 40 |
| 5 | Reddit marketing | 78 | 33,360 | 70 | 28,970 | 87% | 38 |
| 6 | Forums and community building | 94 | 24,140 | 82 | 18,440 | 76% | 51 |
| 7 | Technical and community events | 174 | 33,000 | 133 | 25,290 | 77% | 64 |
| | **Total** | **1,129** | **336,180** | **818** | **184,160** | **55%** | **556** |

Clusters 5, 6, and 7 hit the API's 250-row cap. Those three are floors, not measurements.

**The earlier documentation figure was itself wrong.** `DERIVED-clean-universe.json` carried about 28 nursing-charting keywords (`picc line documentation example`, `perrla documentation example`) plus a junk `test.com` term at 3,000/month. Documentation is 63,730, not 68,870 — the number this campaign was reoriented on was 7.5% overstated. Recorded because a research bank that is trusted without being checked is worse than no bank.

**Revised day-90 band: 350 to 1,350 clicks/month, central estimate ~710.** *(Corrected later the same day to 306–1,176 after the contamination sweep cut the universe 12.6%. See the fourth-cycle refresh.)* Down from the documentation-only 700–2,400, despite a 4.9× larger universe. The reason matters more than the number: **volume was never the constraint.** Seventy-one planned pages inside ninety days buys only 22.2 mature-equivalent pages once cohort maturity is applied (0.55 / 0.30 / 0.08). At DR 26 — the site is not zero-authority, as previously assumed — with P(top 3) at 0.15 and P(4–10) at 0.30, and an AI Overview haircut of 49.2% of SERPs losing about 35% of clicks (×0.828), the campaign contributes 334 / 685 / 1,295 and the recovered legacy set adds 15 / 25 / 40.

**Against the 10,000 target, the central estimate is 7%.** Reaching 10,000 by publishing would need about 450 clicks per page across 22.2 mature-equivalent pages, which is roughly 25,000 addressable searches per page. The best 150 keywords in the entire niche average 740. **That is a 34× throughput gap, not a volume gap, and no choice of niche closes it.** Widening the niche bought winnability, not reach.

Three decisions taken on this evidence:

1. **Tools are the only lever with a defensible traffic profile, and the reason is structural.** All fifteen highest-value keywords in the niche carry an AI Overview. None of the nine build-a-tool keywords do. Tool intent is protected from the single largest threat to every article the campaign could publish. `ai overviews checker` — 700/month, KD 0, no AI Overview — is now the top build target, ahead of the llms.txt validator. A correction to an earlier claim in this document: the llms.txt family was sized at ~7,000/month, but that included the KD-56 head term; the tool-intent subset is 550/month. Still worth owning, no longer the headline.
2. **The calendar is reweighted by volume × winnability, not evenly across seven clusters.** Cluster 2 does not get a seventh of it: 2.4% of the universe and nothing in the niche top 15. Clusters 5, 6, and 7 are weighted up — 76–87% of their keywords are KD≤20 against documentation's 50% and AI engineering's 40%, and they are the clusters where Ninad has genuine first-hand ground, which makes Experience tier A actually available. Cluster 3 holds 45% of all volume but is the hardest and 65% AI-Overview-saturated, so its 217 KD≤20 keywords are the target and its head terms are not. Cluster 1 keeps a real allocation regardless of the arithmetic because it is tied to the consulting offer.
3. **`traffic_potential` is not used in any estimate.** Ahrefs reports the #1 ranking page's total traffic, so `nfl streams subreddit` scored 481,000 because that page is reddit.com. Using it would have inflated the band roughly tenfold. Recorded so nobody reintroduces it.

Brand Radar remains unentitled — confirmed again, `Missing addon`. The management endpoint listing a report is misleading. No AI-citation data is claimed anywhere in this campaign; AI exposure means the `serp_features` flag, which says a SERP has an AI Overview, never who is cited in it.

### 2026-08-17 — cluster owner pages, and the homepage retrofit

Commits `fbdcddef` and `1fa28ac2` on `main`.

Cluster isolation could not be enforced, because no cluster had a page to own. The July 30 refocus collapsed all twelve topic pillars into anchors on one URL, `/articles/#<slug>` — no unique URL, title, or canonical, so twelve clusters shared one ranking surface. The category mechanism that already existed for exactly one category now covers all seven clusters, rendering `/articles/<slug>/` with its own title, description, canonical, and `CollectionPage` schema. No template work and no new CSS.

Assignment is explicit, not inferred: tag matching put 85 of 88 posts in the wrong cluster, because `developer-experience` and `infrastructure` straddle boundaries and the builder takes the first match. Every published post now declares `category:` in frontmatter. Current distribution is 57 ai-engineering, 23 technical-documentation, 8 developer-experience; the other four clusters are declared ahead of their content and render nothing until they have some.

Two generator fixes so declaring a cluster early cannot ship an empty page — that failure is exactly how an empty `/articles/ai-memory/` shipped and had to be removed by hand. Empty categories are now skipped in the build, excluded from the sitemap, and filtered out of the `/articles/` nav, which had been emitting four broken internal links on every paginated page.

The homepage then got the retrofit that 2e requires. It carries 310 impressions, 28 clicks, and 9% CTR at position 6.8 — more clicks than the rest of the site combined — and it linked to no cluster owner at all, so the owner pages inherited their only inbound links from paginated lists. It now links every non-empty cluster. `/linter/` went into the footer, which is part of why the linter had no inbound link anywhere on the site.

Judge all of this on whether the cluster owner pages accumulate non-brand impressions of their own, not on the fact that they exist.

### 2026-08-17 (second cycle) — the pipeline is fixed, and the liability is wider than the AI cluster

**Voice repair deployed.** 16 articles, **1,349 deletions against 675 insertions** — the right ratio when the finding is invented evidence rather than bad writing. `rule_checker` 349 → 284 errors. The audit covered 235 claim units at 54 keep / 115 rewrite / 66 cut.

**Every benchmark article checked has no reproducible artifact.** The extension pass asked one question of eight more articles — does an artifact exist, in this repo or at a linked public location, that produces the numbers the article states — and the answer was **no, eight times out of eight**: BEAM, local WASM, agentic CLI, lambda calculus, RAG evaluation metrics, state of AI agent memory, state of open-source memory, embedding models. Benchmark framing removed from all of them rather than unpublishing, because they hold real positions and a 404 earns nothing. Two now point at genuinely reproducible public work instead: NVIDIA RULER and LongMemEval.

**The two tools are live and verified working.** `/ai-overviews-checker/` and `/llms-txt-validator/`, 89 unit tests between them, 133 of 134 in the suite passing (the failure is a missing local `rsvg-convert` binary, unrelated). The checker was smoke-tested in a real browser: loads clean, no console errors, and its sample run reports "8 checks applied, 2 not applicable" — it says which checks it could not apply instead of padding a score. That honesty is why the page is trustworthy and it is a standing requirement for every tool.

**New finding, and it widens the problem: the voice liability is not confined to the revived AI cluster.** A scan of the non-AI clusters found **ten documentation-cluster articles carrying the identical defect** — "I ran the checker against a fixture containing…" — which is the fixture-verifies-its-own-fixture pattern that carries zero information. The slop review found it in five articles; it is in at least fifteen. It is the Hermes generator's signature, so the generator fix matters more than the cleanup, but the cleanup now extends to cluster 1.

**Cluster isolation is now auditable, and it is failing.** `tools/audit_clusters.py`, first run over 88 posts:

- **20 posts have no inbound link at all — 23% of the site.** Five were published by Hermes in the last week, which is generator defect G6 appearing in the data rather than in a review.
- 9 posts have fewer than two outbound links, 5 of them zero.
- 22 cross-cluster links need the subject-of-the-sentence test, which cannot be decided mechanically, so the tool reports each with its sentence and never auto-fixes one.

**Generator fixes verified independently, not taken on report.** Checked on Phantom directly: backups exist, the artifact conditional is in the prompt, the "does the artifact test anything the article did not already assume" question is present in **all three** skill copies, and the queue carries new `Subcluster` and `Experience` columns without repurposing `Tier`. Nothing was deleted on the box — 6 stale workspaces, 9 backups, 37 cron jobs all intact.

**Calendar reweighted by volume x winnability.** Out of 71 Planned rows: documentation 18, AI engineering 12, Reddit 11, events 11, community 10, AI search 6, DevEx 3. Clusters 5-7 take 32 rows, 45% of the calendar, and 16 of those are Experience A. The whole API block at rows 20-30 moved out, because rows 22-25 were precisely the fixture-checker risks and that block was simultaneously the weakest and the most dangerous content on the schedule. Experience distribution moved to 33 A / 22 B / 16 C, which is a consequence of moving rows to where Ninad has real ground rather than of generosity.

**A sitewide cosmetic defect, fixed.** `.label::before` in `main.css` emits `//` and 21 template labels hardcoded another, so every page on the site rendered `// // About`, `// // Tool`, `// // Portfolio`. The fix had existed on a branch for hours and never reached `main`. Fixed at the template layer, no CSS touched.

**Search Console.** Nothing has moved and nothing could have — the recovery is hours old. Striking distance is the useful read, and it is thin: only **three genuinely human queries** sit within reach — `stripe tech blog` at position 17.7, `single agent vs multi agent` at 26.7, and `engineer to technical writer` at 16.2. Everything else in the top 20 is the machine keyword-salad fan-out or the brand query. That is a direct confirmation of the day-90 band and of why tools, not articles, are the lever.

Three decisions taken:

1. **`seo-for-technical-documentation` stays in cluster 1.** It was the cheap way to bring cluster 4's owner page to life, and it is the wrong one: the piece is a traditional technical SEO checklist for docs sites, it genuinely belongs to documentation, and moving a live post between clusters to make a page appear is gaming the structure rather than building it. Cluster 4 gets a real seed article instead — the llms.txt evidence piece, which is also the only legitimate home for in-sentence links to both llms.txt tools. The tool agent was right to refuse to invent those links: zero live articles mention llms.txt or AI Overviews anywhere, and *that*, not the linking, is why the generator earned three impressions in its life.
2. **Commit `7e875cda` is dropped, not merged.** Every file it touched already exists on `main` through later commits; its only unique contribution was 103 lines of unused glossary CSS against standing order 4. Superseded rather than lost.
3. **The director works in a separate `main` worktree from now on.** Agents own the shared checkout, and an agent mid-rebase left conflict markers in `config.toml` that made `build.py` fail for everyone in that tree. Separating the deploy checkout removes the collision entirely.

### 2026-08-17 (third cycle) — the glossary recovery, and the finding that killed a twelve-article plan

**The glossary was one line away from live the whole time.** `content/data/glossary.yaml` line 1 read `status: retired`, and `load_glossary` returns an empty list on that, so all 25 terms were unreachable. The terms are complete — real short and long definitions, a how-it-works section, use cases, related terms, and **zero TODO placeholders**. Meanwhile Google had **24 of those URLs indexed and ranking**, at positions from 7.4 to 76, drawing roughly 380 impressions over three and a half months, every one of them landing on a 404.

Checked the thing that would have made the recovery worthless: every one of the 24 indexed slugs is present in the rebuilt set, so this is recovery rather than 25 new pages competing with 24 dead ones. The terms make no first-person claims at all, which clears the voice standard by the third path it explicitly allows. Publishing immediately failed the SEO audit on two `related_terms` pointing at terms that do not exist; both removed, and `tests/test_glossary_integrity.py` now fails on a dangling related term, a duplicate slug, or a placeholder definition.

**A near-miss worth recording, because it is a whole class of defect.** `/glossary/` had been redirected to `/articles/` earlier the same day to stop it 404ing. Cloudflare's `_redirects` takes precedence over a static file, so once the glossary republished, that redirect would have sent every visitor and crawler away from the page it was meant to protect — including the `/glossary/` URL sitting at position 8.6. **A redirect added to cover a dead page has to come out when the page comes back.** Every future dead-URL recovery can reintroduce this, so `daily_cycle.py` now fails the gate on any redirect whose source resolves to a real built page. Verified by reintroducing the bug and watching the gate catch it.

Sitemap 116 → 142 URLs.

### The premise in charter section 4 is dead, and this is where it is recorded

Section 4 says *fixing what already ranks may beat anything else on the board*. That was written before the machine query fan-out was identified, and once `tools/gsc_report.py` shipped it became measurable. The scoreboard:

**46 queries sit in positions 4–30 carrying 204 impressions. Of those, 28 are machine fan-out variants of a single keyword salad (149 impressions), 3 are brand, 1 is a pasted blob, and 9 fall below a 3-impression floor. Human queries in reach: five — and two of those are junk** (`roman hresko` is a different person's name, `technical tutorial` has 3 impressions).

So the site has roughly **three real striking-distance queries**. The 44 AI-cluster pages sitting at average position 11.5 on 1,191 impressions look like a goldmine and are not: those impressions are the `anthropic contextual retrieval` fan-out. Expanding them would be optimising for a crawler that does not click.

That correction cancelled twelve queue rows mid-plan. They had been reassigned to "expansion slots on pages already ranking at GSC positions 8–28" — a reasonable idea under section 4, resting on a scoreboard that did not exist yet. When the scoreboard arrived it showed almost nothing there. The twelve rows are repointed at cluster 4, which is the priority lever on evidence, has verified volume (23,880/mo, 42 keywords at KD≤20), holds one post, and already contains four live tools for articles to point at.

### The methodological finding, which cost twelve articles before it was caught

**Cluster-level volume × winnability is the right instrument for sizing a niche and the wrong one for choosing articles.** The morning's reweight sent 45% of the calendar to Reddit, community and events on the strength of 76–91% KD≤20 winnability. Checking individual keywords against their parent topic before writing briefs showed why those shares were so high:

- Reddit marketing's head is `buy reddit account` (3,600) and `readvertising` (4,400). Actual content intent in that space totals about 100/mo, and the row scheduled to publish the next morning targeted a 20/mo keyword whose long tail is OnlyFans and music promotion.
- `developer community` returns community development block grants and departments of housing. 59% of that cluster had already been stripped as HOA and property management, and the contamination survived at the head under a different phrase.
- Independently, and within the same hour, the tool-selection pass found that `audit documentation software` and `audit documentation example` are the **accounting** sense — ISA 230 assurance workpapers — not developer documentation.

Both cluster totals were accurate. Both were misleading. **High winnability can mean nobody in this niche contests those keywords because they are not this niche.** Parent topic is the per-keyword check that catches it, and it is cheap. Allocation corrected: Reddit 11 → 4, community 10 → 5. Cluster 7 probed on the same basis. Row 20 repointed before it could publish.

Because two independent agents hit contamination inside one hour, a full sweep of the banked universe is in flight. The 336,180/mo total and everything resting on it are treated as provisional until it lands.

### Also this cycle

- **Third tool live**: `/ai-crawler-checker/`. The build-a-tool shortlist is now exhausted — the remaining six candidates were rejected with dated SERP evidence, three of them on constraint-incompatibility rather than difficulty, including `ai documentation generator` which cannot be built at any effort level without transmitting the user's code.
- **All four tools verified working, not assumed.** The AI Overviews checker runs 8/8 in a browser with no console errors and honestly reports "2 not applicable". The llms.txt validator was tested end to end against a live domain: it fetched a real 28,458-byte file through the Cloudflare function, parsed 8 sections and 102 links, and graded it A with zero findings.
- **Documentation-cluster voice repair**: 55 claim units at 23 keep / 21 rewrite / 11 cut, `rule_checker` 284 → 280. The Cloudflare Workers SEO audit was **kept** after the script was rerun and reproduced 12 passes — the standard removes what cannot be evidenced, not everything first-person. The reviewer also caught that a cut 30-site measurement had survived inside the AI Overviews checker's sample data.
- **Six illegitimate cross-cluster links removed**, 22 → 16. The tell is now stated in all three skill copies as a test rather than a phrase list: *delete the link and the sentence should break*. Stripping them revealed that `technical-content-as-a-moat-the-long-game-for-developer-tools` has **zero** outbound links — all three of its links were convenience links. The page was never connected to the site, it only looked connected, and it is queued for review as a page.
- **`rsvg-convert` installed.** The suite had carried one permanently red test from a missing binary, which is how a real failure hides behind a known one. 234 passing, zero failures.
- **Cluster audit corrected twice**, both times because the instrument overstated the problem: it now counts inbound links from the built site rather than article bodies only, and counts links to tools as outbound. Orphans 21 → 18, thin outbound 10 → 8. Cluster 4 has one post and therefore no article siblings, so an audit that demanded article-to-article links would have forced the exact cluster-isolation breach the rule forbids.

### Ahrefs is dead, and it changed nothing

The MCP token is invalid — reproduced on the free `subscription-info-limits-and-usage` endpoint, so it is the token and not a quota. Escalated; credentials are out of the director's scope. Semrush is confirmed working and standing order 8 covers the split.

The pattern worth keeping: the blocked call was a re-pull of clusters 5–7 past a 250-row cap. Rather than treating it as a blocker, the argument was checked — the cap ordered by volume descending, so truncation only ever removed keywords **below** the target-set cut-offs. The band stands at 350–1,350, central ~710. Cluster totals stay labelled as floors rather than quietly restated as facts, and the correction was appended as an appendix rather than rewritten into the original section. **When something is unavailable, establish whether it changes the answer before treating it as a blocker.**

### 2026-08-17 (fourth cycle) — corrected universe, corrected band, and the site's first zero-orphan state

**The keyword universe was contaminated by 12.6%, and the band moves with it.** A full sweep by parent topic plus free SERP reads cut the seven-cluster total from 336,180/mo to **293,800/mo**, and the day-90 band from 350–1,350 to **306–1,176 clicks/month**. Same order of magnitude, so the strategy does not change; the number is corrected because a band resting on an inflated denominator is worse than no band. Clusters 5–7 were floors before the sweep and remain floors after, so 293,800 is more likely to fall again than recover.

The sweep cost **zero paid calls** — ten free SERP reads plus parent topics already banked from the original paid pull. Two of the ten reads *reversed* a removal that the parent-topic field alone would have made wrongly, which is the argument for keeping the SERP step rather than trusting parent topic on its own. It is a reproducible script, so the next pass re-runs it rather than re-deriving it.

**A missing parent topic is not evidence of contamination.** Worth stating because the method leans on that field: all 53 no-parent cluster-1 keywords are llms.txt terms totalling 8,760/mo. They are legitimate, just too new for the index to have assigned parents. By subject they belong to cluster 4 rather than cluster 1, which would make cluster 1 ~54,310 and **cluster 4 ~30,980** — the second-largest cluster, and the one holding the four live tools.

**Cluster 7 is contaminated too.** `developer conference` is navigational brand traffic — WWDC 5,400, GDC 2,400, NVIDIA, Roblox — and every variant of `conference talk proposal` returns 0/mo. There is no how-to intent under it. Eight rows were skipped rather than filled, taking Planned from 71 to 63. An empty slot is a scheduling problem; a thin article is a permanent one.

**Zero orphans, for the first time.** The retrofit landed: 18 posts with no inbound link and 8 with fewer than two outbound are both now at **0**, across 91 published posts. `tools/audit_clusters.py --strict` therefore went into CI as a gate, having been deliberately kept out while it would have failed on arrival. It still does not block a cross-cluster link, because the legitimate exception — the link being the subject of the sentence — cannot be judged mechanically; those are reported for a reviewer. 21 remain.

**Two cluster-4 articles shipped**, and their job was structural as much as editorial: the AI Overviews checker and the AI crawler checker were both orphans, and the campaign's own evidence says tools are the only lever an AI Overview does not tax. Reviewed as Claude, since Codex wrote them. Each carries exactly one first-person claim and both are true and checkable by any reader — that the live robots.txt was read on a stated date, and that the checker on this site was built.

### The claim sweep, and why hand-picked lists were the wrong instrument

Two voice-repair passes ran against lists assembled by hand: the top ten by Search Console value, then eight benchmark articles. Both were productive. Both were incomplete, and reviewing an unrelated commit turned up claims outside either list — a cost measured on a named RTX 4090, an assistant described as built with a two-model handoff, and an article citing a benchmark that a later audit had already found unbacked.

`tools/audit_claims.py` replaces the list with a sweep, and the result is the honest scale of the problem: **116 candidate claims across 54 of 89 published posts.** The two hand-picked passes had covered 26. It flags first-person actions, first-person measurements, bare measurements beside named hardware or models, and any link to one of the ten articles established to have no reproducible artifact. It decides nothing — every hit is a candidate for a reviewer to classify KEEP, REWRITE or CUT, and the reviewer is Codex because Claude commissioned the content.

### Production was behind main, and that is now detected rather than noticed

Ten commits sat on `origin/main` while production served an older build. Cloudflare Pages keeps the previous deploy live when a build fails, so a stalled deploy is silent by default and the repo looks correct while the site is not.

Ruled out, in order, before concluding: the build is fine (a pristine clone of `main` builds on Python 3.9 with only `requirements.txt` — 144 URLs, audit passes); CI was green on the affected commits; it is not a dashboard redirect rule (`/glossary/` returned a 301 with `content-type: text/plain`, which is Pages `_redirects` behaviour, from a rule that exists only in the previously deployed build); and all four Pages Functions parse and execute cleanly. What remains needs the Cloudflare Pages build log, which is outside the director's access.

`tools/daily_cycle.py` now compares the local build's sitemap count against production and asserts a list of URLs serve 200, **without following redirects** — following them is what would have hidden the `/glossary/` shadowing, because a shadowed page resolves 200 at the redirect target and looks healthy.

One operational change taken from it: **commits get batched into one push per cycle.** Fifteen deploys in an afternoon is wasteful regardless of whether a build cap caused this, and it makes each deploy verifiable instead of a blur.

### CI could not go green, which is the same failure class as a silent gate

Two bugs, both structural. The rule-of-three check offered two ways to pass in its error message — an evidence receipt or an explicit factual trio — and only implemented the receipt, so it fired on sentences that named all three of their items. Fixing that removed 29 false positives, 280 → 251, with nine tests pinning both directions. Then the CI step itself failed on **inherited** debt rather than regressions, so touching any older post turned CI red while ~250 pre-existing errors sit across the archive. Hermes edits a post daily, so red was the default state, and a gate that cannot go green stops being read. CI now compares changed files against their previous versions and fails only if the count rises, which is what the publish gate in section 8 always said.

Also removed a "verify generated output is committed" step: `output/` is untracked and generated at build time, so it diffed nothing and passed unconditionally. A check that cannot fail reads as coverage and is worse than no check.

### 2026-08-17 (fifth cycle) — the real baseline, and a write-off

**This is the honest baseline, and it is worse than anything reported before it.** `tools/gsc_human_baseline.py` separated machine query fan-out from people across the full Search Console span:

| Month | Site impressions | Human impressions | Human clicks | Human position | Machine % of named |
|---|---:|---:|---:|---:|---:|
| 2025-04 | 3,822 | 2,532 | 3 | 44.2 | 1.7% |
| 2025-06 | 6,499 | 3,362 | 1 | 38.6 | 3.8% |
| 2025-10 | 904 | 221 | 6 | 15.9 | 0.0% | *(the apparent position gain is a composition artifact — see the seventh-cycle refresh)* |
| 2026-03 | 652 | 437 | 0 | 77.4 | 0.8% |
| 2026-07 | 2,476 | 152 | 0 | 41.1 | 34.5% |
| 2026-08 | 946 | 46 | 0 | 56.7 | 57.1% |

**Human impressions fell from 3,362 in June 2025 to 46 in August 2026 — a 98.6% collapse.** Twenty human clicks in the entire span, all of them in 2025. **No human click on a named non-brand query since October 2025**, ten months. 49 of 72 named clicks are the brand query.

So the framing this campaign inherited — impressions 4×'d — is not growth. Human visibility collapsed and machine fan-out partially refilled the hole. One page, `/blog/how-anthropics-contextual-retrieval-changes-rag-architecture/`, went from zero impressions before May 2026 to 49% of all site impressions in July and 59% in August; its 69 identifiable queries are one family permuting `anthropic contextual retrieval` at a uniform position 8.7 with **zero clicks across all 69**.

**A correction to an earlier entry in this document.** The third-cycle refresh said the impression growth "is machine query fan-out". That overstated what is provable. Within named queries fan-out is only 3.6% of impressions across the span; human is 93%. Search Console withholds 51% of impressions, so **the sitewide machine share is a range of 1.8% to 52.9%** — the lower bound assumes every withheld impression is human, the upper assumes every one is machine, and the midpoint is not an estimate. What *is* solid is the per-page concentration and the ten-month absence of non-brand human clicks. The range is now reported as a range.

### The 2025 site is gone, and it is written off

The repo history begins in March 2026. Search Console goes back to April 2025, and the site that earned the 2025 traffic no longer exists in it. Mid-2025 the domain pulled roughly 6,000 impressions and **26 clicks a month across about 30 URLs — more real clicks than it earns today.** The top page, `/guides/css-grid-layouts-webflow-table/`, took 65 clicks on 5,374 impressions at position 21.

Every one of those URLs is a hard 404. The March 2026 rebuild dropped the previous site with no redirects.

**Written off, deliberately, and the reasoning is recorded so nobody re-runs this investigation.** Checked whether it was recoverable: **zero impressions on any legacy URL in the last twelve weeks.** Google has dropped them, so restoring a URL now starts from zero rather than recovering a position. And the content does not warrant rewriting: the volume was productivity-app comparisons — `ticktick vs todoist`, `todoist vs trello`, fifteen variants — sitting at positions 30 to 45 with **0% CTR**. They were never converting. The only genuine click-earner was an off-niche CSS guide at ~16 clicks/month, and building on it would mean an eighth cluster of one page, which is the unfocused-personal-blog failure the isolation rule exists to prevent.

Three URL sets earned on-niche: the Stripe documentation case study at position 7.7, a Stripe documentation lead-generation essay at 10.8, and a Notion API documentation case study at 19.8. Those *topics* are validated demand and belong in the queue as new work. The pages themselves are unrecoverable.

**The finding that matters is not the lost traffic — it is that nothing prevented it.** The same failure nearly recurred twice more this month: the July refocus 404'd 68 pages carrying 86% of impressions, and the glossary sat dead with 24 indexed URLs behind one line of config. In every case the window closed quietly because nothing was watching. A committed inventory of every URL that has ever earned an impression, checked against the build, is in flight.

### Deploy verification now distinguishes waiting from broken

The post-deploy check added earlier this day cried wolf: a mismatch read while a deploy was mid-flight was treated as a build failure, and two stale reads agreeing with each other were mistaken for confirmation. The false alarm cost more time than a real failure would have.

It now reports three states. **LIVE** when production matches the build. **WAITING** for a mismatch inside a fifteen-minute grace window measured from the newest commit that changed something the build actually renders — documentation-only commits do not start that clock, so editing this file cannot produce a phantom lag. **ALARM** only past the window. Seven tests pin the distinction.

The general lesson, since it will recur: **when a check disagrees with what you believe you shipped, establish whether the check is sound before acting on it.** The same discipline that was applied correctly to the Ahrefs failure — proving the missing data could not change the conclusion before treating it as a blocker — was not applied here, and it cost a detour.

### 2026-08-17 (seventh cycle) — the autumn 2025 collapse was a spam injection

**Cause found.** `tools/gsc_collapse_forensics.py` traced it: the largest weekly fall was the week of 2025-09-05, legitimate impressions 517 → 77, a loss of 440 in one week. Same-week onset of foreign-language URLs, four clean weeks before, inverse trajectories for four weeks after. At its October peak the injection ran to **440 pages and 829 impressions** across sections `contents`, `hg`, `home`, `jukyuban`, `products`, `pw`, `shop` — Japanese-language shopping spam.

**It is gone.** Foreign impressions ran 826 in October 2025, 155 in November, 32 in January 2026, 26 in March, and **zero from April 2026 onward.** Sampled injected URLs return 404. The last 90 days contain no foreign path segment at all.

**The vector was almost certainly the WordPress installation, and the rebuild eliminated it.** The 2025 URL set carries unmistakable WordPress fingerprints — `/category/` taxonomy paths, `/2022/` and `/2023/` date permalinks, a `/wordpress-6-3-update/` post — and 417 of the injected pages sat under a single fabricated `/products/` section, which is the standard shape of a compromised-CMS shopping-spam hack. Every WordPress endpoint now 404s: `/wp-login.php`, `/wp-admin/`, `/xmlrpc.php`, `/wp-content/uploads/`, `/wp-json/wp/v2/users`. The site serves as static files from Cloudflare Pages with no PHP, no database, no admin login and no plugins, so content can only change through the git repository. That is a different and far harder threat model, and it carries an audit trail. **Recorded as a closed risk of a known class rather than an unknown vector that might recur.**

**Two corrections this produces, both to readings recorded earlier in this document.**

First, and it matters because it appears in an earlier refresh: **"human position improved from 44.2 to 15.9 over 2025" is a composition artifact, not a gain.** The deep-position tail was wiped out and brand queries were left behind, so the average improved while the site lost everything that made it. Any historical position improvement on this domain has to be checked against whether the denominator changed.

Second, the October 2025 rebound visible in the sitewide series **was the spam peaking, not the site recovering.** Legitimate impressions in those two weeks were 11 and 35. The real corpus never recovered; it fell monotonically.

**What the evidence cannot settle, stated rather than smoothed over.** Co-timing is not causation: the pattern is consistent with the spam triggering a demotion, or with one compromise both injecting spam and breaking the real pages. Neither is asserted. And Search Analytics reports impressions, clicks and position only, so it cannot see a manual action or security issue — the Manual Actions and Security Issues reports in the Search Console UI are the only way to rule out a penalty still in force, and that needs an interactive login rather than the service account. It is a 30-second check, it is the last open question on "is anything still suppressing this domain", and the evidence already answers no.

**Guarded against a repeat.** `daily_cycle.py` now flags foreign URLs on every run. Verified rather than assumed: silent on the clean 28-day window, and against October 2025 it correctly reports 440 pages and 829 impressions with the section list. This went unnoticed for ten months precisely because the injected pages 404 to a direct request — only Search Console could ever have revealed them, and nothing was reading it.

### Also this cycle

- **Fortnight three briefed**: 41 consecutive days from 08-18 to 09-29, no gaps, all 79 link targets verified. Two rows killed on verification. Order 61 was "Free llms.txt Generator and Checker" — **already delivered as software**, so an article restating it would compete with the tool it should route to. Order 64 duplicated an already-briefed row.
- **Two briefs carry a stop instruction rather than a workaround.** Row 49 opens a cluster with no published siblings and may not meet the two-outbound minimum honestly. Row 50's controlled test cannot be manufactured in one run, so it may publish a **pre-registration instead of a conclusion** — honest, where a conclusion would be fabrication. Offering the honest alternative inside the brief means the writer does not have to invent one under deadline.
- **Two redirect leaks recovered.** Seven hub redirects pointed at the bare `/articles/` listing, a soft 404, carrying 87 impressions; 17 rules repointed at the cluster owner pages that now exist. And nine date-prefixed posts had a second legacy URL with no redirect at all — one taking 41 impressions into a 404 — fixed in `build_redirects` so future filename/slug divergence is covered.
- **The URL inventory guard** tracks 1,047 URLs since 2025-04-21, checkable without credentials, and `tools/daily.sh` refreshes it before building and checking. It needs credentials to refresh but not to check, and unrefreshed it fails its own freshness gate, which is the failure it exists to prevent.

### 2026-08-17 — no-new-CSS violation, held out of the deploy

Commit `7e875cda` on `seo/90day-strategy` added 103 lines and nine classes to `static/css/main.css` for glossary and post-terms display, against standing order 4. The glossary is not shipping — all 16 terms are held back on TODO placeholder prose — so the CSS is currently dead weight on every page load.

Decision: that commit was kept off `main` and only the recovery was cherry-picked, so production carries no unused CSS. The glossary revival must reduce those nine classes to existing utilities or justify each one before it ships. Recorded rather than silently carried.

### 2026-08-17 — the impression growth that framed this campaign was not human growth

Every impression figure the campaign had reported was contaminated by query traffic with
no person behind it, and the contamination rate was only known inside positions 4–30.
It has now been measured across the full history by `tools/gsc_human_baseline.py`, which
shares its classifier with `tools/gsc_report.py`.

**Read the denominator before the finding.** Search Console withholds low-volume queries,
so the query dimension covers only **48.9%** of sitewide impressions. Machine share can
only be measured inside that named subset. The sitewide share is a range —
**1.8% to 52.9%** of all impressions — where the lower bound assumes every withheld
impression is human and the upper assumes every one is machine. There is no point
estimate and the midpoint is not one.

**Machine fan-out is 3.6% of named impressions across the whole span** — 599 of 16,416,
in 123 queries. Sitewide that is small. The concentration is what matters: it is **57% of
named impressions in August 2026** and 34.5% in July, against 1–4% in every month of 2025.

**The 4× growth story does not survive.** Site impressions did rise 652 → 2,476 from
March to July 2026, which is real. Underneath it:

| March → July 2026 | Change |
|---|---|
| Site impressions | 652 → 2,476 (**×3.8**) |
| Named impressions | 473 → 330 (**×0.70**) |
| **Human impressions** | 437 → **152** (**×0.35, down 65%**) |
| Machine fan-out impressions | 4 → 114 (×28.5) |
| Withheld by Search Console | 179 → 2,146 (×12) |

One page accounts for it. `/blog/how-anthropics-contextual-retrieval-changed…` recorded
zero impressions before May 2026, then 157, 495, 1,210, 558 — reaching **49% of all site
impressions in July and 59% in August**. Its 69 identifiable queries are one fan-out
family permuting `anthropic contextual retrieval`, at a uniform position 8.7, with **zero
clicks across all 69**. Because that page's named queries are entirely fan-out while most
of its impressions are withheld, the withheld surge is very likely more of the same
family, each variant too small to be named. That is an inference from page-level
concentration, not a query-level proof, and Search Console withholding makes the proof
impossible.

**The click record is the blunt version.** Across the full span there were 20 human clicks
on named queries, all of them in 2025. **Since October 2025 there has not been a single
human click on a named non-brand query — ten consecutive months.** Of 72 named clicks in
the span, 49 are brand. The homepage alone carries 9 of the site's 11 clicks in the current
28-day window.

**What follows.** Charter section 4 said fixing what already ranks may beat anything else,
written before anyone knew the impressions were machine. It is now stronger than that:
there is no human ranking demand to fix on the page carrying half the site's impressions.
The twelve expansion slots repointed at cluster 4 were repointed correctly. Impressions are
retired as a campaign metric — human clicks and human impressions are the series, and
`tools/daily_cycle.py` now logs them beside the sitewide and non-brand figures with their
qualifiers attached.

**The measurement's own limits, because they are not small.** The first version of this
analysis reported 64% of named impressions as machine and was wrong. It clustered queries
by transitive similarity, which chained unrelated queries into groups with no shared core
and filed real human comparison queries — `notion vs todoist`, `ticktick vs todoist`,
`grid table css` — as bot traffic. Families are now anchored on an explicit shared core and
accepted only when their decoration vocabulary is narrow, and a regression test asserts no
family can have an empty core. Residual false positives remain in the small families
(`top content marketing books` is a person, and one Todoist family even has a click), which
means 3.6% is an upper estimate rather than a floor. The human series is itself a floor,
because the withheld tail is excluded entirely and some of it is certainly human.

### 2026-08-17 — the autumn 2025 collapse: a spam injection on the domain, closed

The human collapse did not begin with the March 2026 rebuild. It began in the **week of
2025-09-08**, five months earlier, and it coincides with several hundred URLs appearing on
ninadpathak.com that belong to no version of this site. Method and re-run instructions:
`tools/gsc_collapse_forensics.py`, output in `planning/gsc-collapse-forensics.md`.

**It is a step, not a slope.** Daily impressions ran 100–120 through 2025-09-05, then 63,
72, 70, 59, 56 on 09-06 to 09-10, then 30, 19, 9, 10 on 09-11 to 09-14. Legitimate
impressions by week: 791 → **260** → 56 → 10. The largest single-week loss is
2025-09-01 → 2025-09-08, down 531 impressions (67%).

**What appeared in that exact week.** Foreign URLs recorded **zero** impressions in every
week through 2025-09-01, then 18 impressions on 16 pages in the week of 2025-09-08, rising
to 233 pages and 381 impressions per week by 2025-09-29. At peak, 398 distinct
`/products/<numeric-id>` pages, plus `/shop/`, `/cart/`, `/contents/`, `/hg/`, `/pw/` and
`/jukyuban/`. The queries they ranked for name it: `ルイヴィトン スカーフ` (Louis Vuitton
scarf), `ノーザリー 黒色`, `ネイルズ ストーリア`, `nettspend mowalola`. Japanese
counterfeit-goods and streetwear spam. Japan appeared as a new country in the same period.

**The legitimate corpus was not demoted — it stopped appearing.** Comparing 28 days before
(2025-08-09) with 28 days after (2025-10-13):

| | Before | After |
|---|---:|---:|
| Pages with impressions | 22 | 3 of those 22 survived |
| Non-brand queries | 119 | 15, and **only one** in common |
| Impressions on queries that vanished | 1,569 | — |

The one query present in both windows is `ninad pathak`. 75% of the vanished impressions
sat at positions 21–50; every surviving impression sat at positions 1–10. **Average
position "improving" from 23.1 to 7.2 is a composition artifact**, not a gain: the
deep-position long tail disappeared and left brand behind. `/guides/css-grid-layouts-webflow-table/`
(962 impressions), `/marketing-research/stripe-documentation-case-study/` (762) and
`/marketing-research/asana-marketing-case-study/` (713) all went to zero.

**Not device-specific and not geographic.** Desktop fell 2,974 → 175 (−94%), mobile
318 → 120 (−62%); usa 2,172 → 100, gbr 177 → 0. A rendering or mobile break would hit one
and not the other. This hit everything.

**And the apparent recovery was not one.** The sitewide series shows a rebound to ~80–100
impressions/day around 2025-10-03. That was the spam peaking, not the site returning.
Legitimate impressions over the same fortnight were 11 and 35. Reading the sitewide number
alone would have suggested the site healed and then relapsed; it never healed.

**The domain is clean now.** Foreign impressions: 826 in October 2025, 155 in November, 32
in January 2026, 26 in March, and **zero from April 2026 onward**. Sampled injected URLs
return 404. In the last 90 days every path segment receiving impressions is legitimate and
exactly one query contains CJK characters — the pasted-blob artifact already classified as
a blob, not spam. A daily guard now flags foreign URLs in `tools/daily_cycle.py`, because
this was found ten months late and the pages 404 to a direct request, so only Search
Console could have shown it.

**Named as inferences, not findings.** Search Analytics reports impressions, clicks and
position and nothing else, so:

1. **It cannot see a manual action, a security issue, or an algorithm update.** The
   Manual Actions and Security Issues reports in the Search Console UI are the only thing
   that settles whether a penalty was applied, and whether one is still in force. **That
   is the one check worth doing by hand** — it is the only way to rule out lingering
   suppression, and this analysis cannot.
2. **Co-timing is not causation.** The injection first registers in the same week the
   corpus collapses, with four clean weeks before it and inverse trajectories for four
   weeks after. That is strong. It is still consistent with either the spam triggering a
   demotion, or a single compromise both injecting spam and breaking the real pages.
   The data does not separate those two, and neither should be asserted.
3. **The injection vector is unknown.** Hacked hosting, a compromised CMS, an abused
   proxy or redirect, a DNS interlude — Search Console shows the symptom, never the entry
   point.

**What this closes and what it does not.** The autumn 2025 collapse is explained and the
condition that caused it is gone, so it is not suppressing the campaign today; the March
2026 rebuild is a separate, later event that killed roughly 30 legacy URLs and is already
written off. What it does not close is whether a penalty from that episode still applies,
and that is a UI check rather than an API one. One correction to a claim made earlier in
this document: legitimate-URL impressions have recovered well past the 2025 nadir — 164 in
October 2025 to 2,737 in July 2026 — but that recovery is the machine fan-out documented
above, not people. Human impressions went 3,362 in June 2025 to 46 in August 2026.
