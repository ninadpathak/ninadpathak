# Tool SERP verification — is the tool-first bet supported?

**Date:** 2026-08-17 · **Agent:** `seo-currency` · **Branch:** `seo/currency`
**Question put:** the campaign is betting sixty remaining calendar rows on the claim that tool
intent is the only traffic profile an AI Overview does not tax. That claim came from a
keyword dataset and nobody had verified it on our own target SERPs.

**Verdict, up front: the bet is half wrong, and the wrong half is the half the strategy
rests on.** Working in §4.

---

## 1. Instrument, and one thing I would not do

| Instrument | Used for | Cost |
|---|---|---|
| Live Google SERP reads in a real browser | AI Overview, PAA, video, top-10 composition | free |
| Search Console | where we rank, and our tool pages' whole history | free, first-party |
| Semrush `phrase_these` | volume, difficulty, SERP-feature codes as a cross-check | **1 paid call, 7 lines** |
| WebSearch / WebFetch | the Semrush feature-code mapping | free |

**Google served a bot-detection page on the first attempt** (`/sorry/index`, "unusual traffic
from your computer network"). **I did not attempt to solve or bypass the CAPTCHA.** A plain
query URL on a normal browser session worked on retry, and every read below came from that.
Where it had not, I would have reported the question as unanswerable rather than guessed.

**Two honesty limits on the SERP reads:**

1. **An AI Overview is not deterministic.** It varies by session, personalisation and
   rollout. Each row below is one observation on 2026-08-17, not a guarantee. For the
   flagship keyword I loaded the SERP **twice independently** and the AI Overview block
   rendered both times, so that one is reproducible rather than a one-off. The others are
   single samples and are labelled as such.
2. **Semrush's numeric SERP-feature codes are only partly decodable.** I confirmed
   **52 = AI Overview** from Semrush's own documentation ("FK52 shows the total number of
   the AI Overview SERP feature"). I could not find an authoritative mapping for codes 6, 7,
   9, 14, 15, 20, 21 or 36 anywhere Semrush publishes, so **I have not decoded them.**
   Guessing would have invented findings. Where Semrush and the live SERP disagree, the live
   SERP wins.

**And they do disagree, in both directions**, which is itself worth knowing before anyone
trusts a feature column again:

| Keyword | Ahrefs dataset (pulled ~2026-08-17) | Semrush code 52 | Live SERP |
|---|---|---|---|
| ai overviews checker | no AIO | present | **AIO present** |
| llms.txt validator | no AIO | absent | **AIO present** |
| llms.txt checker | no AIO | absent | **AIO present** |
| llms.txt generator | no AIO | present | no AIO |

Three of four rows have at least one tool wrong. **Feature flags in keyword tools are not a
substitute for reading the SERP.**

---

## 2. One row per keyword

All read 2026-08-17, google.com, en-US, logged-out browser session. "Format" counts the
first ten organic results.

### `ai overviews checker` — the flagship

| | |
|---|---|
| Volume | 700/mo (Ahrefs), 390/mo (Semrush). KD 0 (Ahrefs) vs 37 (Semrush) |
| **AI Overview** | **YES — reproduced on two independent loads.** Cites Growth Natives, SEO.com, SE Ranking, AEO Engine, RankSpark, Keyword.com, Profound AI |
| Featured snippet | none seen |
| People also ask | no PAA block; "People also search for" present |
| Video | **YES, video carousel** — SMA Marketing (11m), SE Ranking (2:57) |
| Paid | **YES, one sponsored result** (Pixis, "Know Your AI Visibility Score") |
| Format of top 10 | **10/10 vendor tool pages.** Sitechecker, **Semrush**, search.google (Google's own), SEO.com, **SE Ranking**, Growth Natives, SiteSpeakAI, LLM Pulse, Rankscale.ai |
| Where we rank | **nowhere.** Zero named-query impressions in 28d |

This is the keyword the whole tool programme was justified on — "700/mo at KD 0, no AI
Overview, the cleanest single opportunity found anywhere in this analysis". Today it carries
an AI Overview, a video carousel, a paid ad, and a top ten made entirely of established SEO
SaaS platforms using a free tool as a lead magnet. Two of them are Semrush and SE Ranking.

### `llms.txt validator`

| | |
|---|---|
| Volume | 100/mo (Ahrefs), 50/mo (Semrush), KD 14 |
| **AI Overview** | **YES.** Cites Rankability, MRS Digital, Radarkit, Techqee, LandKit, AI Rank Lab, Rank Ray, Spindora |
| People also ask | **YES** — "Does LLMs.txt actually work?", "What is LLMs.txt for?", "How to generate an LLMs.txt file?" |
| Video | none |
| Format of top 10 | **9/10 tools.** llmstxtvalidator.org (Hostinger), mrs.digital, rankray.com, rankability.com, indexly.ai, spindorai.com, llmstxtvalidator.dev, plus debugbear.com (article) and a Webflow forum thread |
| Where we rank | **nowhere**, despite `/llms-txt-validator/` being live |

The PAA block is worth noting on its own: **"Does LLMs.txt actually work?" is a question
Google is surfacing on this SERP**, and it is exactly the article `FORMAT-BACKLOG.md` item 6
proposed. That is a demand signal for the evidence piece, independent of the tool.

### `llms.txt checker`

| | |
|---|---|
| Volume | 150/mo (Ahrefs), 110/mo (Semrush), KD 30 |
| **AI Overview** | **YES** — the same AI Overview text as `llms.txt validator`, with an eight-source citation carousel |
| People also ask | none seen; "People also search for" present |
| Video | none |
| Format of top 10 | **9/10 tools.** mrs.digital, rankray.com, rankability.com, llmstxtvalidator.org, spindorai.com, indexly.ai, mxtoolbox.com, a Chrome extension, llmstxt.org (the spec) |
| Where we rank | **nowhere** |

**Google serves substantially the same AI Overview and an overlapping result set for
`checker` and `validator`.** That independently confirms the recommendation already made in
`TOOL-COPY-BRIEF.md`: these are one job, and a second URL would cannibalise. Treat as a
targeting fix on the existing validator page, not a new page.

### `llms.txt generator`

| | |
|---|---|
| Volume | 300/mo (Ahrefs), **2,400/mo (Semrush)** — an 8× disagreement, worth resolving before anyone plans on it |
| **AI Overview** | **no** (Semrush's code 52 claimed one; the live SERP shows none) |
| People also ask | none; "People also search for" present |
| Video | none |
| Format of top 10 | **8/10 tools**, 1 spec page, 1 listicle. llmstxtgenerate.com, sitespeak.ai, gushwork.ai, **writesonic.com**, llmrefs.com, **llmstxt.firecrawl.dev**, github.com/firecrawl, adnabu.com, llmstxt.org, aioseo.com ("7 Best LLMs.txt Generators") |
| Where we rank | **nowhere.** `/llms-txt-generator/` has **zero page-level impressions across Search Console's entire available history**, 2025-04-22 to 2026-08-14 |

The cleanest tool-answered SERP in the set, and the one where our oldest tool has never once
appeared.

### `ai crawler checker`

| | |
|---|---|
| Volume | 20/mo (Semrush), KD 0. The family around it is larger — `oai-searchbot` 720, `claudebot` 3,600 |
| **AI Overview** | **no** |
| People also ask | none; "People also search for" present |
| Video | none |
| Format of top 10 | **9/10 tools.** aicrawlercheck.com, crawlercheck.com, mrs.digital, llmrefs.com, rankability.com, llmpulse.ai, competlab.com, adamigo.ai, tufanerdogan.com, plus cloudflare.com (explainer) |
| Where we rank | **nowhere** |

**The competitive detail matters more than the AIO answer here.** `competlab.com` advertises
"21+ AI bots", `tufanerdogan.com` "Checks 21 different AI crawlers individually" and also
folds in llms.txt presence. My checker covers 17 agents. **The tool I shipped third is
entering a crowded field where incumbents already cover more crawlers than it does**, and two
of them are exact-match domains built for nothing else.

### `technical writing linter`

| | |
|---|---|
| Volume | not returned by Semrush at all — below its reporting floor |
| **AI Overview** | **no** |
| People also ask | **YES** — "What is the purpose of a linter?", "What are the 7 Cs of technical writing?", "What are 5 examples of technical writing?", "What is a linter vs formatter?" |
| Video | none |
| Format of top 10 | **6/10 ARTICLES, 3 tools.** Fern "Docs Linting Guide", techwritertoolkit, tw-docs.com, BrowserStack "What Is a Linter?", JetBrains (Google flags it "Missing: writing"), Medium — against Vale.sh, alphagov/tech-docs-linter, and **ninadpathak.com/linter/** |
| Where we rank | **the only place we appear.** In the live top 10 at roughly position 9; GSC 28-day average position 18.0 on 2 impressions, 11.8 on 9 impressions over the full history, 0 clicks ever |

**This is the one article-answered SERP in the set, and the only one where we rank.** The
PAA block is entirely definitional, which says the query carries heavy informational intent.
Our tool page ranks here despite being a tool, not because the SERP wants one.

### `robots.txt checker` — the variant I judged real

Chosen because it is the crawler checker's actual competitive neighbourhood at 2,400/mo, and
because the tool selection document explicitly declined to position against it.

| | |
|---|---|
| Volume | 2,400/mo (Semrush), KD 48 |
| **AI Overview** | **no** |
| People also ask | **YES** — "How do I check if robots.txt exists?", "How to see a robots.txt file?", "Is robots.txt legal?", "How to fix blocked by robots.txt error?" |
| Video | **YES** — Google Search Central, 5:55, 49.6K views, with six key moments |
| Format of top 10 | **10/10 tools and incumbents.** technicalseo.com (Merkle), seoptimer.com, rankmath.com, a Chrome extension, **seranking.com**, robotstxt.com, seositecheckup.com, robotstxt.org, YouTube (Google), google.com/robots.txt |
| Where we rank | **nowhere** |

The decision to avoid positioning as a generic robots.txt tester was correct and this SERP is
the evidence: no AI Overview, but entrenched incumbents in every slot.

---

## 3. Summary table

| Keyword | AI Overview | PAA | Video | Paid | Top-10 format | We rank |
|---|:---:|:---:|:---:|:---:|---|:---:|
| ai overviews checker | **YES** ×2 | — | **YES** | **YES** | 10/10 vendor tools | no |
| llms.txt validator | **YES** | **YES** | — | — | 9/10 tools | no |
| llms.txt checker | **YES** | — | — | — | 9/10 tools | no |
| llms.txt generator | no | — | — | — | 8/10 tools | no |
| ai crawler checker | no | — | — | — | 9/10 tools | no |
| technical writing linter | no | **YES** | — | — | **6/10 articles** | **~9 live / 11.8 avg** |
| robots.txt checker | no | **YES** | **YES** | — | 10/10 tools | no |

**AI Overview on 3 of 7, including the flagship.** The dataset's claim was "not one of these
nine SERPs shows an AI Overview".

---

## 4. The verdict

### 4a. The claim the strategy rests on is now false

`addressable-universe.md` §5a: *"Not one of these nine SERPs shows an AI Overview. Tool
queries are structurally protected from the thing suppressing clicks everywhere else in this
niche. That is the strongest argument in this document for weighting the campaign toward
tools."*

**Three of the six build-a-tool keywords I could read now carry an AI Overview, and the
flagship carries one reproducibly, plus a video carousel and a paid ad.** I am not going to
soften this: **the structural protection the tool bet was built on has substantially eroded,
and on the single keyword that justified the programme it is gone.**

I cannot prove the SERPs changed rather than the dataset being wrong when pulled — I have no
before-and-after on the same instrument, because Ahrefs is dead. Either reading is bad for
the bet. If the SERPs changed inside a month, tool intent is not structurally protected, it
was temporarily unoccupied. If the dataset was wrong on pull, the premise was never true.

### 4b. The claim about page shape is right, and worth keeping

**Six of seven SERPs are tool-answered.** A tool page is the correct shape for these queries
and our tool pages do not need to become articles. Only `technical writing linter` is
article-answered — and it is the one where we rank.

So the format half of the bet survives. **Do not rewrite the tools as articles.**

### 4c. The premise nobody stated is the one that bites

Neither claim addressed whether a DR-26 personal site can rank for these at all. The SERPs
answer it. Every one is won by one of two things:

1. **SEO SaaS platforms using a free tool as a lead magnet** — Semrush, SE Ranking,
   Sitechecker, SEOptimer, Rank Math, TechnicalSEO/Merkle, Writesonic, Rankability.
2. **Exact-match single-purpose domains** — llmstxtvalidator.org, llmstxtgenerate.com,
   aicrawlercheck.com, crawlercheck.com, llmstxtchecker.net, spindorai.com.

`ninadpathak.com/ai-crawler-checker/` is neither. And our own data is the strongest evidence
available:

- **`/llms-txt-generator/`: zero impressions in Search Console's entire recorded history.**
- **`/linter/`: 9 impressions, ever. Position 11.8. Zero clicks, ever.**

Two tools, live for months, have produced nine impressions and no clicks between them.

**In fairness, three of the five tools are days old** — `/llms-txt-validator/`,
`/ai-overviews-checker/` and `/ai-crawler-checker/` cannot be judged yet and their zeros are
expected, not evidence. The judgement rests only on the two with enough age.

### 4d. Sixty rows on tool intent is not supported

Even taking the dataset's own arithmetic: the entire build-a-tool subset is 1,940/mo, which
my contamination sweep cut to ~1,800/mo after removing the accounting-sense audit pair, of
which ~1,100/mo is already shipped. **There is not sixty rows of tool work in this niche**,
and the remaining candidates were already rejected on constraint grounds in
`TOOL-SELECTION-2026-08-17.md`.

---

## 5. What the evidence says instead

### Keep the tools, change what they are for

My own §4.1 finding still stands: reference infrastructure earns links, and
`keepachangelog.com` holds 2,220 referring domains on **zero** organic traffic. The tools may
be perfectly good assets — as citation targets, as credibility proof for a technical writer
selling documentation work, and as the thing that makes a first-hand article possible. **Judge
them on referring domains and on their use in articles, not on sessions.** That reframes them
rather than killing them, and it is consistent with everything measured.

What it does not support is treating them as the campaign's traffic channel.

### Put the calendar where the site already ranks

Search Console, 28 days to 2026-08-14:

- **`/blog/how-anthropics-contextual-retrieval-changes-rag-architecture/` — 755 impressions
  at position 8.3.** That is 68% of the site's entire 28-day impressions from one page.
- Also ranking: `/blog/fine-tuning-vs-rag-for-agent-memory/` at 12.0,
  `/blog/embedding-models-compared/` at 31.3, a glossary HNSW page.
- **The only two genuinely human long-tail queries we hold** are
  *"how do you handle errors when ai agents make mistakes in production"* at **10.6** and
  *"how do companies debug ai agents that fail in production"* at **10.2**.

That is cluster 3 — AI agents, memory, RAG, inference. The charter already called it "the only
search equity this domain has ever earned", the contamination sweep found it **clean** where
four other clusters lost 24–45%, and it is 149,790/mo after cleaning.

**Two caveats I will not leave out.** The 755 impressions are largely machine query fan-out
with zero clicks, which I established in the earlier GSC work — so cluster 3's apparent
strength is inflated by phantom impressions too. And those two human queries are
conversational, question-shaped and agent-operational: *how do I debug this in production*.
They are not head terms.

### The specific recommendation

1. **Stop counting tool intent as a traffic channel.** Keep the four tools, judge them on
   referring domains and on the articles they make possible.
2. **Do not build tool number five** unless it is a by-product of an article.
3. **Weight the remaining rows toward cluster 3 long-tail operational questions** — the shape
   of the two queries we already hold at position ~10, where a first-hand answer from someone
   who has debugged an agent is exactly the thing an AI Overview cannot fake and a vendor
   will not write.
4. **Write the llms.txt evidence piece.** Google is surfacing *"Does LLMs.txt actually
   work?"* as a People-also-ask question on a SERP we already target. That is measured demand
   for the article, and it needs no tool to rank.
5. **Re-read these seven SERPs monthly.** AI Overview coverage moved enough in a month to
   invalidate a strategy premise. It will move again, and a keyword tool's feature flag was
   wrong on three of four rows.

---

## 6. Paid call log

One paid call. Also appended to `planning/research-cache/CALL-LOG.md`.

| Instrument | Report | Lines | Cost | Why |
|---|---|---|---|---|
| Semrush | `phrase_these` | 7 | 10 units/line = **70 units** | Volume, difficulty and SERP-feature codes as a cross-check on the live reads. Justified: Ahrefs is dead and the dataset's volumes needed a second opinion, which found an 8× disagreement on `llms.txt generator`. |

Everything else — seven live SERP reads, Search Console, the feature-code documentation
hunt — was free.
