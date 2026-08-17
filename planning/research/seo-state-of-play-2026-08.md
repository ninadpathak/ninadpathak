# SEO & AI-Discovery State of Play — August 2026

**Compiled:** 2026-08-17
**Author:** `seo-currency` research agent
**Scope:** technical documentation & docs-ops, developer experience, DevRel content for DevTools/B2B SaaS, AI-ready documentation, AI agent architecture. Ecommerce and local-SEO findings are deliberately excluded.
**Re-check cadence:** see [Monthly re-check list](#monthly-re-check-list) at the end.

## How to read this document

Every claim carries a date and a source. Claims are tagged:

- **[VERIFIED]** — I checked the primary artefact myself (Google doc, PDF metadata, live SERP data pulled from Ahrefs, file I fetched).
- **[ASSERTED]** — a source claims it; I could not independently confirm. Treat as a hypothesis, not a fact.
- **[KILLED]** — a widely repeated claim I checked and found false or unsupported. Do not use it.

If a source would not state when it was published or measured, it was dropped and is listed in [Sources I dropped](#sources-i-dropped).

---

# Question 1 — What actually ranks in Google now

## 1.1 The confirmed update record (the only reliable spine)

**[VERIFIED]** Pulled from Google's official Search Status Dashboard ranking-update history on 2026-08-17
(`status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history`, which is where
`developers.google.com/search/updates/ranking` now 301-redirects):

| Update | Launched | Completed | Duration |
|---|---|---|---|
| June 2026 spam update | 2026-06-24 | 2026-06-26 | 2d 1h |
| May 2026 core update | 2026-05-21 | 2026-06-02 | 11d 21h |
| March 2026 core update | 2026-03-27 | 2026-04-08 | 12d 4h |
| March 2026 spam update | 2026-03-24 | 2026-03-25 | 19h 30m |
| February 2026 Discover update | 2026-02-05 | 2026-02-27 | 21d 17h |
| December 2025 core update | 2025-12-11 | 2025-12-29 | 18d 2h |
| August 2025 spam update | 2025-08-26 | 2025-09-22 | 26d 15h |
| June 2025 core update | 2025-06-30 | 2025-07-17 | 16d 18h |
| March 2025 core update | 2025-03-13 | 2025-03-27 | 13d 21h |

**What this means for us:** as of 2026-08-17 we are **~11 weeks clear of the last core update** (ended
2026-06-02) and ~7 weeks past the June spam update. Historically Google has shipped 2–4 core updates a
year, so **a core update landing inside our 90-day window (to ~2026-11-15) is likely.** Plan for it: the
campaign should not be structured so that one volatility event invalidates the whole quarter.

## 1.2 What I could NOT confirm, and what is outright false

This matters more than the confirmations, because the false claims are circulating widely and an agent
searching casually will find them first.

**[KILLED] "Core Web Vitals moved from per-page to site-wide aggregate scoring in March 2026."**
**[KILLED] "Google tightened the LCP threshold from 2.5s to 2.0s."**
**[KILLED] "LCP/INP/CLS were replaced by a single composite performance score."**

I fetched Google's own Core Web Vitals reference (`web.dev/articles/vitals`) on 2026-08-17. It states LCP
**2.5 seconds**, INP **200 milliseconds**, CLS **0.1**, assessed at the **75th percentile of page loads,
segmented by mobile and desktop** — i.e. still per-page, still three separate metrics, still the same
thresholds. Page's own last-updated stamp: **2024-10-31**. There is no composite score and no site-wide
aggregation in Google's documentation. These three claims trace to a cluster of undated agency blog posts
that cite each other and no primary source. **Do not let any of this drive a performance work item.**

**[KILLED] "Google shipped a June 2026 Search Quality Rater Guidelines update that added a Section 5.2 on
unattributed AI content and a Section 5.4 on 'Verifiable Real World Expertise'."**

I downloaded the live QRG PDF on 2026-08-17 from Google's canonical URL
(`static.googleusercontent.com/media/guidelines.raterhub.com/en//searchqualityevaluatorguidelines.pdf`)
and read its embedded metadata: **182 pages, CreationDate 2025-09-10**. The current guidelines are the
**September 2025** edition. There is no June 2026 revision, and the cited section numbers and phrases do
not appear in the document. This claim appears to be fabricated detail in AI-written SEO posts. Several of
those posts contradicted each other in the same search-results page (one asserting "first update since
November 2024", another correctly stating "182 pages, last updated September 11, 2025"), which is the tell.

**Standing rule this implies:** for anything about Google's own systems, the primary artefact is cheap to
check (a doc's last-updated stamp, a PDF's CreationDate, the status dashboard). Check it. The SEO blog
layer in 2026 is substantially AI-generated and inserts confident, specific, false detail.

## 1.3 Site-level vs page-level signals — measured, not theorised

**[VERIFIED]** I pulled live SERP data from Ahrefs for niche head terms on 2026-08-17 (Ahrefs' own SERP
snapshots dated 2026-08-16 and 2026-07-22). The page-level authority of winning results is strikingly low:

`api documentation best practices` (SERP crawled 2026-08-16):

| Pos | URL | DR | UR | Ref. domains | Est. traffic |
|---|---|---|---|---|---|
| 1 | postman.com/api-platform/api-documentation/ | 90 | 8 | 72 | 2,468 |
| 2 | stoplight.io/api-documentation-guide | 84 | 4 | 457 | 401 |
| 3 | buildwithfern.com/post/api-documentation-best-practices-guide | 76 | 4 | 11 | 18 |
| 5 | mintlify.com/library/our-recommendations-for-creating-api-documentation… | 90 | 4 | **4** | 89 |
| 6 | swagger.io/blog/what-is-api-documentation-and-why-it-matters/ | 90 | 5 | 15 | 339 |
| 7 | theneo.io/blog/api-documentation-best-practices-guide-2025 | 67 | 6 | 9 | 7 |
| 8 | robertdelwood.medium.com/getting-to-great-documentation… | 94 | **0** | **0** | 21 |
| 9 | zoho.com/learn/focalpoint/api-documentation-guide.html | 92 | 6 | **3** | 33 |

`docs as code` (SERP crawled 2026-07-22):

| Pos | URL | DR | UR | Ref. domains |
|---|---|---|---|---|
| 2 | writethedocs.org/guide/docs-as-code/ | 76 | 7 | 416 |
| 3 | **reddit.com**/r/technicalwriting/…/what_exactly_is_the_docsascode_process/ | 95 | 0 | 2 |
| 4 | gitbook.com/blog/what-is-docs-as-code | 92 | 4 | 15 |
| 5 | konghq.com/blog/learning-center/what-is-docs-as-code | 79 | 4 | 13 |
| 6 | medium.com/@arastoo/what-is-docs-as-code… | 94 | 0 | 1 |
| 7 | dev.to/dumebii/docs-as-code-the-best-guide-for-technical-writers-97c | 91 | 4 | 10 |
| 8 | **reddit.com**/r/technicalwriting/…/just_use_docsascode/ | 95 | 0 | 1 |
| 10 | medium.com/@EjiroOnose/understanding-docs-as-code… | 94 | 4 | 4 |

**Finding: in this niche, page-level link equity is close to irrelevant, and host-level authority plus
topical fit is doing nearly all the work.** A Medium post with URL Rating 0 and zero referring domains
ranks 8th for a commercial-intent head term. Mintlify ranks 5th on 4 referring domains. Only two pages in
either top 10 have a meaningful page-level link profile (stoplight 457, writethedocs 416), and they sit at
positions 2 and 2 respectively — not 1.

**Therefore, do differently:**
- **Stop treating per-article link building as the lever.** It is not what separates position 3 from
  position 8 here. Nobody in these SERPs won on page links.
- **The lever is site-level.** For a solo domain the practical implication is that every thin or
  off-topic page on ninadpathak.com is a liability against the whole domain, and topical density in a
  narrow area is the asset. This is consistent with Google's own documented position (§1.5) that the
  helpful-content assessment is site-wide.
- **A low-DR independent domain cannot out-rank Postman and Mintlify on head terms by writing a better
  version of the same article.** Head terms like `api documentation best practices` are effectively
  closed. The winnable surfaces are (a) long-tail and specific-intent queries, and (b) AI-assistant
  citation, where the authority barrier is demonstrably much lower — see Question 2.

## 1.4 Forums and UGC — a structural placement, not a fad

**[VERIFIED, first-party]** In the `docs as code` top 10 (crawled 2026-07-22), **two of the ten organic
results are Reddit threads** from r/technicalwriting, at positions 3 and 8. For `llms.txt` (crawled
2026-08-10), Reddit holds position 5 with three additional Reddit sitelinks stacked under it, plus two
more Reddit threads inside a `news`-type block. Medium and dev.to occupy three further slots in the
`docs as code` top 10.

**[VERIFIED]** This is backed by Google's rater specification, not just observation. From the live
September 2025 QRG (p. ~ "High Level of E-E-A-T"), quoted verbatim:

> "Experience is valuable for almost any topic. Social media posts and forum discussions are often High
> quality when they involve people sharing their experience. From writing symphonies to reviewing home
> appliances, first-hand experience can make a social media post or discussion page High quality."

**Therefore, do differently:**
- **Do not target head terms whose SERP is half UGC and half DR-90 vendors.** We lose both halves.
- **Reddit threads rank because they contain a named person recounting what happened to them.** That is a
  format instruction, not a platform advantage we cannot copy. The transferable move is first-person,
  specific, dated, outcome-bearing accounts — the thing a vendor blog structurally cannot write.
- **The r/technicalwriting threads ranking for our terms are a keyword mine.** The exact phrasings people
  use there ("what exactly is the docs-as-code process", "just use docs-as-code") are the long-tail
  intents worth owning. Recommend the strategy agent read those threads for query phrasing.

## 1.5 Thin and programmatic content — the rule is intent, not volume

**[VERIFIED]** Google's spam policies page, fetched 2026-08-17, **last updated 2026-05-15** (i.e. current,
revised six days before the May 2026 core update launched). Verbatim:

> "Scaled content abuse is when many pages are generated for the primary purpose of manipulating search
> rankings and not helping users."

Note what this definition does **not** say: it does not set a volume threshold, and it does not say
"automatically generated". The test is **primary purpose**. Examples Google gives include generating pages
with AI tools without adding user value, scraping feeds with minimal additions, and stitching content
together from multiple sources.

**[VERIFIED]** Google's "Creating helpful, reliable, people-first content", fetched 2026-08-17,
**last updated 2025-12-10**. Verbatim on automation disclosure:

> "Is the use of automation, including AI-generation, self-evident to visitors through disclosures?"

and it warns that using "automation, including AI-generation, to produce content for the primary purpose
of manipulating search rankings" violates the spam policies.

**[VERIFIED]** The Low-quality criteria in the September 2025 QRG include, verbatim, the failure mode
**"Lacks adequate effort and first-hand experience from the content creator"**, illustrated by content
"paraphrased or summarized from other sources, with minimal signs of effort or original content added by
the content creator."

**Therefore, do differently — and this one is a direct risk to this campaign:**

A 90-pieces-in-90-days programme written substantially by an LLM is, on its face, the exact silhouette
Google describes. It is not automatically a violation — volume is not the test — but the campaign only
stays on the right side of the line if **each piece carries something that could not have been
paraphrased from the existing top 10.** Concretely, this argues for:

1. **Every piece needs at least one first-hand artefact**: a command Ninad actually ran with its real
   output, a screenshot of a real docs site, a number he measured, a decision he made on a real project
   and what it cost. This is the single highest-leverage constraint in this document, and it maps
   directly to a documented Low-quality criterion.
2. **Author attribution and an "how this was made" posture.** Google explicitly asks whether automation is
   self-evident through disclosure. A visible, honest note about method is a trust asset, not a confession.
3. **Rate is a risk multiplier, so front-load originality, not volume.** If a day's piece has no
   first-hand artefact, it is better skipped or merged than shipped. Recommend the calendar carry slack
   days rather than 90 hard commitments.

## 1.6 How first-hand experience is actually assessed

**[VERIFIED]** From the September 2025 QRG, verbatim:

> "Experience: Consider the extent to which the content creator has the necessary first-hand or life
> experience for the topic. Many types of pages are trustworthy and achieve their purpose well when
> created by people with a wealth of personal experience. For example, which would you trust: a product
> review from someone who has personally used the product or a 'review' by someone who has not?"

**[VERIFIED]** Google's helpful-content self-assessment questions, quoted verbatim from the 2025-12-10
version, that bear on our work:

> "Does the content provide original information, reporting, research, or analysis?"
> "Is this content written or reviewed by an expert or enthusiast who demonstrably knows the topic well?"
> "If someone researched the site producing the content, would they come away with an impression that it
> is well-trusted?"
> "Would you expect to see this content in or referenced by a printed magazine, encyclopedia, or book?"

**[VERIFIED]** Also from the helpful-content doc: E-E-A-T is described as a mix of factors and **"trust is
most important"**, with extra weight where content could significantly affect health, financial stability,
or safety. Our niche is **not** YMYL, which is genuinely good news: the trust bar is real but not the
elevated one, and informal/demonstrated expertise counts. The QRG explicitly allows that "there are many
types of informal expertise that may be visible in the MC itself" — i.e. showing the work in the article
body itself is a recognised way to demonstrate expertise, without credentials.

**Therefore, do differently:** the operational form of "experience" is *demonstrated in the body of the
page*, not claimed in an author bio. A sentence like "I've worked on developer docs for years" is worth
nothing. "Here is the `redocly lint` output on this spec, and here is the one rule that produced 60% of
the errors" is the thing. This is turned into sentence-level rules in `CITATION-PLAYBOOK.md`.

---

# Question 2 — How AI assistants pick what to cite

## 2.0 A note on what I could and could not use

**Ahrefs Brand Radar is not available on this subscription.** Every Brand Radar endpoint returns
`Missing addon: Brand Radar ["Chatgpt"]` / `["GoogleAIOverviews"]`. The account is a **Standard, billed
monthly** plan (checked 2026-08-17: 38,520 of 400,000 units used, resets 2026-09-07). Brand Radar is a
paid add-on that is not attached.

So I substituted two data sources that are available and, for this question, arguably better because they
are measurements rather than a vendor's aggregation:

1. **`site-explorer-ai-responses-count`** — per-domain citation counts across ChatGPT, Perplexity, Gemini,
   Google AI Overviews, Google AI Mode and Copilot. This works.
2. **`serp-overview` filtered to `ai_overview` / `ai_overview_sitelink` types** — returns the actual URLs
   Google cited inside an AI Overview for a given query. This works and is real citation data.

The per-page AI columns on `site-explorer-top-pages` (`ai_responses_perplexity` etc.) are also addon-gated
and returned "column not found". **If Ninad wants page-level citation attribution and prompt-level share
of voice, Brand Radar needs to be added to the plan.** That is a purchasing decision, not something I can
work around. Everything below is from the two endpoints that do work.

## 2.1 Google's own position, from the newest primary doc

**[VERIFIED]** `developers.google.com/search/docs/fundamentals/ai-optimization-guide` — "Google's Guide to
Optimizing for Generative AI Features on Google Search", **last updated 2026-07-10**. This is the freshest
primary artefact on the question and it is unusually direct. Verbatim:

> "Creating content that people find unique, compelling, and useful will likely influence your website's
> presence in generative AI search in the long run more than any of the other suggestions in this guide."

> "Structured data isn't required for generative AI search, and there's no special schema.org markup you
> need to add. However, it's a good idea to continue using it as part of your overall SEO strategy, as it
> helps with being eligible for rich results on Google Search."

> "You don't need to create new machine readable files, AI text files, markup, or Markdown to appear in
> Google Search (including its generative AI capabilities), as Google Search itself doesn't use them."

> "Doing so will neither harm nor help your site's visibility or rankings in Google Search, as Google
> Search ignores them."

> "People generally appreciate it when web pages are organized by paragraphs and sections, along with
> headings that provide a clear structure to navigate content."

> "To be eligible to be shown in generative AI features on Google Search, a page must be indexed and
> eligible to be shown in Google Search **with a snippet**, fulfilling the Search technical requirements."

**[VERIFIED]** Corroborated by `developers.google.com/search/docs/appearance/ai-features` (last updated
2025-12-10): *"There are no additional requirements to appear in AI Overviews or AI Mode, nor other special
optimizations necessary."*

**Two things to take from this, and one caution:**

- **The snippet-eligibility requirement is the one real technical gate.** A page carrying `nosnippet`, or a
  restrictive `max-snippet`, is by Google's own wording not eligible for AI Overviews or AI Mode. Worth a
  one-time check across our templates. (I could not find a Google doc that states the `nosnippet` → AI
  exclusion link explicitly — the "Search generative AI control" help page does not mention snippet meta
  tags at all — so I am inferring this from the eligibility sentence above. **[ASSERTED, my inference]**,
  flagged as such.)
- **Schema is not an AI-citation lever.** Keep it for rich results if it is already there; do not build new
  schema work justified as "for AI".
- **Caution: Google speaks only for Google.** These statements bind AI Overviews and AI Mode. They say
  nothing about ChatGPT, Perplexity or Claude, which are separate retrieval systems. Do not generalise.

## 2.2 llms.txt — the evidence, and it is not good

This is the claim Ninad specifically asked not to be theorised about. Here is the measured record.

**[VERIFIED]** **Google ignores it.** Quoted above from the 2026-07-10 guide: *"Google Search itself doesn't
use them… will neither harm nor help."*

**[VERIFIED]** **Chrome's Lighthouse treats it as optional and non-diagnostic.**
`developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt`, last updated **2026-05-05**, describes
llms.txt as an *"emerging convention"*, states *"providing the file is optional at the moment"*, and the
audit only *"flags the pages if a server error occurs when attempting to retrieve the llms.txt file"* — a
404 is marked Not Applicable. Notably the page **does not claim any AI system consumes it**; it offers only
a theoretical benefit ("agents may spend more time crawling the site").

**[ASSERTED — strong methodology, vendor-published]** **97% of llms.txt files were never fetched.** Ahrefs
study, published **2026-06-15**, authors Louise Linehan and Xibeijia Guan, measuring **May 2026** across
**137,210 domains** using Ahrefs Web Analytics and Bot Analytics server-log data. Verbatim findings:

- *"28% of the 137K domains using Ahrefs Web Analytics publish an llms.txt file"*
- *"97% of those files received zero traffic in May 2026. Nothing fetched them"*
- *"96% of the requests that did reach llms.txt files came from bots"*
- *"19.5% of fetches came from named AI tools"*
- *"77% of the bots reading llms.txt aren't from AI tools at all"* — SEO audit tools 21.7%, unidentified
  bots 14.9%, general crawlers 13.1%, tech-profiling tools 11.6%

The authors state their own limitation: *"Ahrefs Web Analytics customers skew more technical and SEO-aware
than the web at large, so treat the 28% adoption figure as an upper bound."* They also did not check whether
files were well-formed.

**Why I kept a vendor study:** it is dated, the sample and measurement window are stated, the method is
server logs rather than opinion, and the finding runs *against* the vendor's commercial interest — Ahrefs
sells AI-visibility tooling, and this result deflates a popular AI-visibility tactic. That is the opposite
of the content-marketing pattern we were told to discount. It is tagged ASSERTED rather than VERIFIED only
because I cannot independently re-run their log analysis.

**[VERIFIED]** **The standard "proofs" that llms.txt works are non-diagnostic.** Mark Williams-Cook
(director, Candour) published a falsification experiment on **2026-08-07**: he invented `cats.txt`, a
fictitious standard listing office cats with names, job titles, breeds and a "PurrLevel" affection metric,
published a serious-looking spec, and announced it as "the missing standard for SEO and GEO". Result:
PerplexityBot, GPTBot, ClaudeBot and Googlebot all downloaded it, Google indexed it, ChatGPT cited details
from the fake file as fact, and the model volunteered that cats.txt "can potentially help you rank in both
search engines and LLM-driven systems".

That is the decisive point. All four observations normally offered as evidence that llms.txt works —
crawlers fetch it, Google indexes it, models cite it, models endorse it — were reproduced by a file about
office cats. **These observations cannot distinguish a working standard from a fictional one.** Any future
argument for llms.txt has to clear a higher bar than "look, GPTBot fetched it".

**Therefore, do differently:**
- **Do not write, or let any brief imply, that adding llms.txt improves AI visibility.** It is not
  supported, and for Google it is explicitly contradicted by Google.
- **Keep `/llms-txt-generator/` — but reposition why.** The tool is justified as a *utility with real
  search demand*, not as a ranking tactic. `llms.txt` as a query has a live SERP with an AI Overview and
  substantial interest (llmstxt.org alone: 6,504 referring domains, ~4,391 est. monthly traffic, measured
  2026-08-10). Serving that demand is legitimate. Claiming the file earns citations is not.
- **There is a genuinely strong article here, and we are unusually well placed to write it.** "We ship an
  llms.txt generator, and here is the evidence that llms.txt does almost nothing" is a credible,
  first-hand, contrarian piece with real receipts (the 137K-domain study, the cats.txt experiment, Google's
  own sentence, the Lighthouse audit's silence). It is also exactly the kind of "information gain" content
  §1.5 says we need. **Recommended for the calendar.** Note the honesty requirement: it must not read as
  a bait-and-switch against our own tool.

## 2.3 Citation is decoupled from link authority — measured

**[VERIFIED]** I pulled per-domain AI citation counts and authority metrics for the niche's competitive
set on **2026-08-17** (`site-explorer-ai-responses-count` and `batch-analysis`, country US). Citations are
counts of citation links in each platform's generated answers.

| Domain | DR | Ref. domains | Org. traffic | Org. keywords | ChatGPT | Perplexity | Gemini | AI Overviews | AI Mode | Copilot | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mintlify.com | 90 | 18,690 | 31,712 | 448 | **193** | 12 | 11 | 9 | 8 | 6 | **239** |
| idratherbewriting.com | 73 | 3,784 | 1,558 | **590** | 5 | **27** | 10 | 14 | 15 | 2 | **73** |
| gitbook.com | 92 | **42,624** | 21,415 | 390 | 15 | 14 | 9 | 6 | 5 | 4 | **53** |
| writethedocs.org | 76 | 4,909 | 2,001 | 332 | 7 | 0 | 0 | 0 | 1 | 0 | **8** |
| diataxis.fr | 77 | 2,682 | 334 | 16 | 0 | 0 | 2 | 0 | 0 | 0 | **2** |
| passo.uno | 44 | 953 | 81 | 34 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| **ninadpathak.com** | **26** | **597** | **0** | **0** | 0 | 0 | 0 | 0 | 0 | 0 | **0** |

**The robust finding — and it is a negative one, which makes it reliable: link authority does not predict
AI citation.**

- **gitbook.com has 11× the referring domains of idratherbewriting.com and gets fewer citations** (53 vs
  73). DR 92 vs DR 73.
- **writethedocs.org and idratherbewriting.com are near-twins on classic metrics** — DR 76 vs 73, 4,909 vs
  3,784 referring domains, 2,001 vs 1,558 organic traffic — and differ **9×** in citations (8 vs 73).
  writethedocs is *zero* on Perplexity, Gemini and AI Overviews despite ranking **#2 organically** for
  `docs as code` with 416 referring domains on that single page.

Whatever drives citation, it is not DR, referring domains, or organic traffic. **This is the single most
strategically important finding in this document for a DR-26 site:** the ranking game is closed to us on
head terms (§1.3), but the citation game demonstrably is not decided by the metric we are worst at.

**The likely driver, stated honestly as a hypothesis.** The strongest correlate in this sample is
**`org_keywords` — the count of distinct queries a domain ranks for at all.** idratherbewriting has the
most in the set (590) despite the third-lowest DR. **[ASSERTED, n=7]** — and it is not clean:
writethedocs has 332 keywords and only 8 citations, which breaks a simple relationship. With seven domains
I can confidently rule authority *out*; I cannot isolate what is *in*. Do not let anyone quote the
query-breadth idea as established.

**Supporting structural observation [VERIFIED].** idratherbewriting.com's top pages (pulled 2026-08-17)
show a distinctive shape: **many pages, low traffic each, high keyword count per page, near-zero page-level
links.**

| Page | Est. traffic | Keywords | Ref. domains |
|---|---|---|---|
| /quickreferenceguides/ | 137 | 33 | 7 |
| /learnapidoc/ | 132 | 29 | 831 |
| /2018/10/15/ideal-number-of-slides-for-an-hour-long-presentations/ | 102 | 57 | 4 |
| /learnapidoc/pubapis_swagger.html | 37 | 10 | 19 |
| /learnapidoc/docendpoints.html | 32 | 4 | 1 |

The `learnapidoc` course is **one page per narrowly-scoped sub-question** (`pubapis_swagger.html`,
`docendpoints.html`), each ranking for a handful of very specific queries on essentially no links. That
granularity — a page whose entire content answers exactly one extractable question — is the format that
maps most naturally onto how a retrieval system selects a passage to quote.

**One honest complication:** idratherbewriting is *not* narrowly topical. Its top pages include standing
desks, balance boards, Java access modifiers and book reviews. So "tight topical focus" is **not** what
distinguishes it from writethedocs, and I should not claim it is. Breadth of specific, granular,
first-person pages is a better description of the site than topical purity.

## 2.4 Platform differences that change where we should aim

**[VERIFIED, from the table above]**

- **Perplexity is the most accessible platform for an independent practitioner site.** It is the *only*
  platform where the solo blog beats both vendors: idratherbewriting 27, gitbook 14, mintlify 12. And
  Perplexity is where writethedocs scores zero. If we pick one AI surface to optimise for and measure,
  **it should be Perplexity.**
- **ChatGPT's numbers are brand-driven and are not a content lesson.** mintlify's 193 ChatGPT citations
  across 184 distinct pages is an outlier of a different kind: those are product-documentation pages being
  cited in answers to "how do I do X in Mintlify". That is demand for a product we do not have. **Do not
  read mintlify's ChatGPT score as evidence that a content tactic works.** It is evidence that owning a
  product generates documentation citations.
- **Google's AI Overviews cite small sites freely.** For `docs as code` (AI Overview captured 2026-07-22)
  Google cited roughly 25 sources, and among them were `dein.fr` (a personal blog), `arundo.com`,
  `doc-e.ai`, `techwritertoolkit.wordpress.com` and seven separate Medium posts — sitting alongside
  github.blog and techtarget.com. The AI Overview citation set is markedly more open to small sites than
  the blue-link top 10 for the same query.

## 2.5 What a cited low-authority page actually looks like

Rather than theorise about "claim extractability", I fetched one. `dein.fr/posts/2026-03-13-its-time-to-move-your-docs-in-the-repo`
is a personal blog cited inside Google's AI Overview for `docs as code`, alongside Google's own blog.
**[VERIFIED]** its structure, fetched 2026-08-17:

- **~1,800 words.** Not 3,000. Not a "definitive guide".
- **Opens with a claim, zero preamble.** Verbatim first sentence: *"AI changes the game when it comes to
  having all your docs in your repository: it's never been that easy to keep them up to date!"* The
  position is stated before anything else.
- **Dated byline with a visible revision date** — published 2026-03-13, updated 2026-03-15.
- **First person throughout**, from sentence two: *"I've always been a fan of having documentation living
  alongside the code."*
- **Statement-form headings, not questions** — "It's time to move your docs in the repo", "We will be
  spending more time writing docs", "Why AI makes it even more meaningful to move docs into your repo".
- **An "Answer to objections" section handling eight specific counterarguments.** This is the most
  copyable structural feature on the page: it manufactures eight discrete, self-contained
  claim-and-response units, each quotable without surrounding context.
- **No tables and no code blocks.** Worth noting because it contradicts the common assertion that tables
  and structured comparisons are required for citation. Heavy bulleted lists instead.

**Therefore, do differently:** the citable unit is a **self-contained claim plus its support, in one
place**. The "answer to objections" pattern is a cheap, repeatable way to generate several of those per
article, and it doubles as the thing §1.5 requires — a first-hand position, defended.

## 2.6 Crawler access — the actual gate, and a live audit of our own site

Access is the one place where a wrong setting silently zeroes out citations regardless of content quality.
The controls are **per-platform and split between search and training**, which is where sites get it wrong.

**[VERIFIED]** From each platform's own documentation:

| Platform | Governs citation in search | Governs model training | Source |
|---|---|---|---|
| OpenAI / ChatGPT | **`OAI-SearchBot`** — *"surface websites in search results in ChatGPT's search features"*. Sites blocking it *"will not be shown in ChatGPT search answers, though can still appear as navigational links."* | `GPTBot` — *"crawl content that may be used in training our generative AI foundation models"* | `developers.openai.com/api/docs/bots` |
| OpenAI (user-initiated) | `ChatGPT-User` — *"certain user actions in ChatGPT and Custom GPTs"* | — | same |
| Anthropic / Claude | **`Claude-SearchBot`** — *"navigates the web to improve search result quality for users"*; `Claude-User` for user-initiated fetches | `ClaudeBot` — *"collecting web content that could potentially contribute to their training"* | `support.claude.com` art. 8896518 |
| Perplexity | **`PerplexityBot`** — *"designed to surface and link websites in search results on Perplexity. It is not used to crawl content for AI foundation models."*; `Perplexity-User` for user-initiated | — (Perplexity states PerplexityBot is not used for foundation-model training) | `docs.perplexity.ai/guides/bots` |
| Google Search + AI Overviews + AI Mode | `Googlebot` | `Google-Extended` (Gemini apps, Vertex AI grounding/training — **not** Search) | Google crawler docs, last updated 2026-06-12 |

**[VERIFIED] Live audit of `https://ninadpathak.com/robots.txt`, fetched 2026-08-17.** The file is
Cloudflare-managed ("BEGIN Cloudflare Managed content") and contains:

```
User-agent: *
Content-Signal: search=yes,ai-train=no,use=reference
Allow: /

Disallow: /  for: Amazonbot, Applebot-Extended, Bytespider, CCBot, ClaudeBot,
                   CloudflareBrowserRenderingCrawler, Google-Extended, GPTBot,
                   meta-externalagent
```

Assessed against the table above:

- **Good news — the citation-critical bots are all allowed.** `OAI-SearchBot`, `Claude-SearchBot`,
  `Claude-User`, `PerplexityBot`, `Perplexity-User` and `Googlebot` are **not** in the block list, so they
  fall under `User-agent: *` → `Allow: /`. **ChatGPT, Claude and Perplexity citation are not blocked.**
  This is the outcome we want and it is worth stating plainly, because the block list looks alarming at
  first glance and it would be easy to "fix" it wrongly.
- **The blocks are training opt-outs, which is a coherent, deliberate position.** `GPTBot`,
  `ClaudeBot`, `Applebot-Extended`, `CCBot`, `Google-Extended` and `meta-externalagent` are all
  training/grounding agents. Anthropic's doc explicitly confirms that blocking `ClaudeBot` alone leaves
  `Claude-SearchBot` and `Claude-User` *"unaffected, meaning the site could still be accessed for search
  results and user queries while being excluded from future model training."* Same shape for GPTBot vs
  OAI-SearchBot.
- **One real cost, and it is Ninad's call, not mine.** `Google-Extended: Disallow` opts out of **Gemini
  apps and Vertex AI grounding**. It does **not** affect Google Search, AI Overviews or AI Mode. But our
  competitor data shows Gemini citations are a live channel in this niche (idratherbewriting 10, mintlify
  11, gitbook 9). So this setting plausibly forecloses the Gemini surface while correctly preserving AI
  Overviews and AI Mode. **Decision for Ninad:** keep the training opt-out and accept ~0 Gemini
  citations, or allow `Google-Extended` to compete there. I am not changing it.
- **One thing I could not verify from outside, and it matters.** The `Content-Signal` block and the
  "Cloudflare Managed content" marker mean Cloudflare's managed-robots feature is enabled. Cloudflare also
  ships **edge-level AI bot blocking**, which returns 403 to known AI crawlers **regardless of what
  robots.txt says**. If that is switched on, `OAI-SearchBot` and `PerplexityBot` could be blocked at the
  edge while robots.txt appears to allow them — and the robots.txt above would be actively misleading.
  I did not test this by spoofing user agents. **Action for Ninad: check the Cloudflare dashboard for
  AI-crawler blocking / "Block AI bots" and confirm it is off for these agents.** This is the highest-value
  five-minute check on the list, because it can silently zero every finding in §2.4.
- **Note the `Content-Signal: ai-input` gap.** The header declares `search=yes,ai-train=no,use=reference`
  and **omits `ai-input`**. Per the file's own preamble, omitting a signal "neither grants nor restricts
  permission". Since `ai-input` is the signal covering RAG/grounding for generative answers — i.e. exactly
  the citation behaviour we want — leaving it unstated is ambiguous rather than permissive. Content
  Signals are a Cloudflare-led convention, not an enforced standard, so the practical risk is low today,
  but **setting `ai-input=yes` explicitly would state our intent unambiguously.** Recommended, low cost.

## 2.7 Measurement — there is now a real report, and it is impressions-only

**[VERIFIED]** Google launched **Generative AI performance reports in Search Console** in **June 2026**
(Search Central blog, `2026/06/gen-ai-performance-reports`; help pages
`support.google.com/webmasters/answer/16984139` for Search and `16983858` for Discover). The 2026-07-10
optimization guide directs site owners to it verbatim: *"To measure how your content is performing in
generative AI features on Google Search and Discover, use the Generative AI performance report in Search
Console."*

**[ASSERTED]** Per Google's help documentation the report shows **impressions** — how often URLs from the
site appeared in generative AI features in Search and Discover — broken down over time and by page, device
and country, and this data is also folded into the overall performance report. Rollout is to **a subset of
properties**, so access is not guaranteed.

**Therefore, do differently — this is a direct handoff to `seo-analytics`:**
1. **Check whether ninadpathak.com's Search Console property has the Generative AI performance report
   yet.** If it does, it is our only first-party AI-visibility measurement and should be in the weekly
   read from day one.
2. **Set expectations correctly: it is impressions, not clicks.** Do not build a KPI that implies AI
   Overviews send traffic. Treat it as a visibility signal.
3. **There is also now a separate "Search generative AI control"** in Search Console
   (`support.google.com/webmasters/answer/16908024`) governing inclusion in Search generative AI features,
   distinct from `Google-Extended`. Verbatim: it *"doesn't override publishers' other choices"*, and
   changes take *"a few days"*. Worth confirming we have not inadvertently opted out there.

---

# Question 3 — What makes people read and finish

## 3.0 An honesty problem with this question, stated up front

Ninad's brief says: no work built on what used to rank ten years ago. The strongest reading-behaviour
evidence **is** old, and I am not going to disguise that.

- The famous **"users read at most 28% of the words; 20% is more likely"** figure comes from an NN/g
  article published **2008-05-05**, analysing Weinreich et al., *"Not Quite the Average: An Empirical Study
  of Web Use"*, ACM Transactions on the Web 2(1), **February 2008** — browser instrumentation over 45,237
  analysed page views. That is **18-year-old data**, gathered before mobile, infinite scroll, and AI
  summaries. **Do not quote the 28% number as a current fact.** I am recording it for provenance, not for
  use.
- NN/g's eyetracking corpus (**published 2020-04-05**, studies run **2006, 2009, 2013, 2016–17, 2019**,
  500+ participants, 750+ hours) is the best-methodology source available, but its most recent data is
  **2019**.

What justifies still using the *mechanism*: it is the one finding NN/g reports as stable across the whole
23-year span, and it is corroborated by independent eyetracking work. Reading behaviour is a much slower-
moving thing than a ranking algorithm. So I use the **direction** of these findings and discard their
**precise numbers**. Where I have fresh, well-powered data (§3.3) I lead with that instead.

## 3.1 Scanning is the default, and headings are the mechanism

**[VERIFIED]** NN/g, *How People Read Online: The Eyetracking Evidence* (published 2020-04-05). Verbatim:

> "People rarely read online — they're far more likely to scan than read word for word."
> "Scanning all of the text on a page, or even a majority, is still extremely rare."
> "People are not likely to read your content completely or linearly."

**[VERIFIED]** Kara Pernice, *Text Scanning Patterns: Eyetracking Evidence* (NN/g, published
**2019-08-25**) names the patterns and — critically — ranks them. Verbatim:

- **Layer-cake pattern** (fixations on headings and subheadings, with gaps between): *"by far the most
  effective way in which users can scan pages"*, second only to reading every word.
- **Commitment pattern** (reading most content words): *"usually leads to the best comprehension, even
  though it is the most time consuming."*
- **F-pattern** — and here is the causal statement that matters: *"In the absence of subheadings and
  bullets, users tend to fixate on the words toward the beginning of lines and toward the top of the
  page."* The F-pattern is what happens **when structure is missing**. It is a symptom, not a target.
- **Spotted pattern**: users fixate on words that *"visually stand out"* or that *"resemble a word that
  the user looks for to accomplish the current task."*

And the summary claim: *"text comprehension is improved when the content is chunked and calls out its main
points in subheadings."*

**Therefore, do differently — this is the highest-value writing rule in this document:**

The F-pattern is usually presented as a law of nature to design around. Per NN/g's own wording it is a
**failure mode caused by absent subheadings.** The fix is not clever formatting; it is **headings that
carry the point**. A reader in layer-cake mode sees *only the headings*. This means:

- **A heading must state a conclusion, not name a topic.** "Versioning" tells a layer-cake reader nothing.
  "Keep one URL per version and canonicalise to the current one" transfers the whole point.
- **The heading stack alone must be a readable summary of the article.** Testable: strip everything but
  the headings. If what remains is not a coherent, useful summary, the headings are labels, not content.
  This is a concrete check the writer and reviewer can both run.
- **This same property is what makes a page citable** (§2.5). Headings that assert extractable claims serve
  the layer-cake human and the retrieval system with one piece of work. That convergence is the most
  useful structural fact in this whole report.

**[VERIFIED]** On preamble: NN/g, *Inverted Pyramid: Writing for Comprehension* (Amy Schade, published
**2018-02-11**) — *"The most important information (or what might even be considered the conclusion) is
presented first"*, so that a reader who reads only one paragraph still gets the essence. Note honestly:
**this article contains no measured numbers.** It is a well-grounded editorial principle from a research
organisation, not itself a study. Tagged accordingly.

## 3.2 How developers specifically read — one fresh study, and it is humbling

**[VERIFIED]** Flint, Dyer & Sharif, *"Do Developers Read Type Information? An Eye-Tracking Study on
TypeScript"*, **ICPC '26** (34th IEEE/ACM International Conference on Program Comprehension), Rio de
Janeiro, 12–13 April 2026; preprint dated **2026-02-05**; DOI 10.1145/3794763.3794800. Method: eye-tracking
study, **26 undergraduate students**, code-summarisation and bug-localisation tasks. Verbatim finding:

> "We found that developers do not look directly at lines containing type annotations or type declarations
> more often when they are present, in either code summarization or bug localization tasks."

**Limitations I will not paper over:** n=26, undergraduates, one language, lab tasks. This does **not**
generalise to professional developers reading prose documentation, and I am not going to pretend it does.

**What it is legitimately good for:** it is a clean, recent, measured counterexample to the assumption that
because information is present and relevant, developers read it. The authors' own framing — that type
annotations were *hypothesised* to function as in-code documentation and empirically are not consulted —
is a useful caution for anyone writing reference material. **[ASSERTED]** as a general lesson; **[VERIFIED]**
only as a finding about TypeScript type annotations in a 26-person lab study.

## 3.3 The real shift: developers now arrive via an AI assistant, and are often let down

This is the freshest, best-powered evidence I found, and it changes the reading model more than any
scanning research does.

**[VERIFIED]** **Sonar, *2026 State of Code Developer Survey***. Fieldwork ran **throughout October 2025**;
final sample **n=1,149** professional developers, distributed globally, all 18+, employed full-time or
self-employed in a technology role, writing code or managing developers, **and having used AI as part of
their job in the past year** (note this last screen — the sample is AI-users by construction, so these are
not general-population adoption rates). From the use-case table, verbatim pairs of adoption and
"% rated extremely / very effective":

| Use case | Adoption | Rated effective |
|---|---|---|
| Writing documentation | 74% | **74%** |
| Explaining or understanding existing code | 78% | 66% |
| Generating tests | 75% | 59% |
| **Researching technical solutions or exploring APIs/libraries** | **74%** | **59%** |
| Assisting development of new code | 90% | 55% |
| Refactoring or optimizing existing code | 72% | 43% |

**[VERIFIED]** **Stack Overflow Developer Survey 2025** — 33,662 total respondents, 26,004 professional
developers. Verbatim:

> "84% of respondents are using or planning to use AI tools in their development process"
> "51% of professional developers use AI tools daily"
> Only **"3.1% highly trust"** AI accuracy, while **"46% actively distrust"** it.
> Top frustration: **"AI solutions that are almost right, but not quite"** — cited by **66%**.
> **"75.3%"** would ask humans when they **"don't trust AI's answer."**

**[KILLED]** An aggregator blog attributed *"92.6% of developers use an AI coding assistant at least once a
month"* to this same Stack Overflow 2025 survey. The primary source says **84% are using or planning to
use**. The aggregator inflated and restated it. Same genre of error as §1.2 — do not source survey numbers
from statistics-roundup posts.

**Therefore, do differently — this is the strategic spine for the writing agent:**

Put the three verified numbers together and a specific reader emerges:

1. **74% of developers research technical solutions and explore APIs through AI**, so a large share of our
   audience meets our material as a quoted fragment inside an assistant, not as a page they chose.
2. **Only 59% find that effective**, and **66% name "almost right, but not quite"** as their top
   frustration. So the modal experience is an answer that looks plausible and fails on contact.
3. **75.3% then go ask a human.**

That is the arrival state of our best reader: they have already been failed by a confident summary, and
they are specifically looking for a person who has actually done the thing. This yields writing rules that
are the opposite of generic SEO advice:

- **The opening must prove a human did this, fast.** Not a personality flourish — evidence. A version
  number, a real error string, the thing that broke, the date it was tried. This is what an AI summary
  structurally cannot supply, and it is what the arriving reader is checking for.
- **Cover the failure modes, because that is where the AI answer broke.** The "almost right, but not
  quite" gap is our whole value proposition. Documenting the edge case, the version incompatibility, the
  error message and the recovery step is not padding — it is the reason the reader left the assistant.
- **Never write the generic middle.** Content an assistant can already synthesise adequately has no
  reader, because the 74% never leave the assistant for it.
- **Be unmistakably attributed.** 75.3% are looking for a human. A named author with visible, specific,
  dated experience is the product.

## 3.4 Depth by intent — where I do not have good evidence, and say so

**[No reliable evidence found.]** I looked for defensible data on ideal content length by intent and did
not find any I would stake a recommendation on. What exists is mostly vendor correlation studies of word
count against ranking position, which are confounded in an obvious way: comprehensive coverage causes both
length and ranking, so length is a proxy, not a lever. Undated or methodology-free versions of these
studies were dropped (see [Sources I dropped](#sources-i-dropped)).

So the following is **explicitly my judgement**, labelled as such rather than dressed up as a finding,
grounded in the two things I *did* verify — that the citable unit is a self-contained claim (§2.5) and
that a cited low-authority page in our niche ran ~1,800 words with no tables:

- **One page, one question.** The strongest structural signal I measured is idratherbewriting's
  one-page-per-sub-question granularity (§2.3) — `pubapis_swagger.html`, `docendpoints.html` — ranking on
  near-zero links. Prefer several narrow pages over one omnibus guide. This also directly reduces the
  cannibalisation risk the strategy agent is already tracking.
- **Length should be set by the number of claims that need support, then stopped.** The verified cited
  example (§2.5) is ~1,800 words, not 3,000. There is no evidence that longer wins.
- **Stop at the point where you would be padding.** Padding is precisely the "minimal signs of effort…
  paraphrased or summarized from other sources" that the QRG names as a Low-quality marker (§1.5). Length
  chased for its own sake actively imports risk.

## 3.5 When a table or diagram beats prose

**[VERIFIED, but note the counter-evidence.]** NN/g's spotted pattern — users fixate on words that
*"visually stand out"* or match their task — supports tables for **comparison and lookup**, where the
reader has a specific cell in mind and prose forces linear search.

**The honest counterweight:** the low-authority page Google cited in its AI Overview for `docs as code`
(§2.5) has **no tables and no code blocks** at all. So I cannot claim tables are required for citation, and
the widely-repeated advice that comparison tables drive AI citation is **not supported by the one case I
actually examined**. Tables earn their place on reader-utility grounds — lookup and comparison — not as a
citation tactic.

Practical rule, my judgement: use a table when the reader's question is *"which one / what is the value
for X"* and prose would make them scan linearly for one fact. Use prose when the answer is a chain of
reasoning, because a table strips causality. Never convert a genuine argument into a matrix.

**Hard constraint check:** tables, headings and lists all render from existing `main.css`. Nothing in §3
requires new CSS.

---

# Question 4 — Formats that work now

## 4.1 The measured pattern: reference infrastructure earns links, articles do not

**[VERIFIED]** Pulled 2026-08-17 via `batch-analysis`, exact-URL mode, country US. These are the
best-linked assets in this exact niche:

| Asset | What it is | Ref. domains | Org. traffic | Org. keywords |
|---|---|---|---|---|
| semver.org | a versioned **spec** | **16,900** | 6,993 | 152 |
| llmstxt.org | a **spec** | **6,509** | 3,407 | **4** |
| developers.google.com/style | a **style guide** | 4,204 | 2,944 | 819 |
| diataxis.fr | a **named framework** | **2,240** | 304 | 15 |
| keepachangelog.com | a **named convention** | **2,220** | **0** | **0** |
| idratherbewriting.com/learnapidoc/ | a **free course** | 860 | 124 | 29 |
| writethedocs.org/guide/docs-as-code/ | a **community definition** | 416 | 364 | 31 |
| divio.com/blog/documentation/ | **a blog post** explaining a framework | 203 | 0 | 0 |

**Two findings jump out of this table, and both are actionable.**

### Finding A: links and traffic are different games, and reference assets win the link game outright

**keepachangelog.com has 2,220 referring domains, zero organic traffic and zero ranking keywords.**
llmstxt.org has 6,509 referring domains on **four** keywords. diataxis.fr has 2,240 referring domains on
15 keywords.

These pages are not competing for search traffic at all. They accumulate links because **other people need
to link to them to make their own point.** That is a fundamentally different acquisition mechanism from
ranking, and per §1.3 it is also the mechanism that builds the site-level authority that *does* matter.

**Therefore, do differently:** a solo site should build a small number of assets whose job is to be
*cited by other writers*, and judge them on referring domains, not sessions. Judging a
reference asset by its traffic will cause us to kill the most valuable thing we build.

### Finding B: naming a framework and giving it its own home multiplied links ~11× for the same idea

This is the cleanest natural experiment I found in this niche, and it is worth stating carefully.

Daniele Procida's documentation quadrant (tutorials / how-to / reference / explanation) was first published
as a **blog post on a company site**: `divio.com/blog/documentation/` — **203 referring domains, 0 organic
traffic**. The same body of thinking, renamed **Diátaxis** and given its own dedicated site, is
`diataxis.fr` — **2,240 referring domains**. Same author, same core idea, **~11× the referring domains.**

**[ASSERTED — causal claim, not verified.]** I want to be precise about what this does and does not show.
The confounds are real: diataxis.fr came later and had years to accumulate links; Procida actively
evangelised it through talks and community work; and adoption momentum compounds. I cannot isolate "gave it
a name and its own domain" as *the* cause from this data alone.

What I will claim, and think is well supported: **the format in which an idea is published materially
changes its link ceiling, and "named framework on its own canonical page" is the highest-ceiling format
observed in this niche.** A blog post explaining a framework capped at 203. Every named,
canonically-homed artefact in the table cleared 400, and three cleared 2,000.

**Therefore, do differently:** when we have a genuinely reusable idea — a checklist, a maturity model, a
review rubric, a taxonomy — **do not publish it as an article.** Give it a name, a stable canonical URL,
and a page that exists to be linked. That is a strategy-level recommendation for `seo-90day`.

## 4.2 Which formats a solo writer can actually sustain

Ninad asked for concreteness about sustainability, and this is where most format advice fails. Assessing
each against the evidence above and against a one-person, one-piece-per-day cadence:

**Sustainable and evidence-backed:**

- **Interactive single-purpose tools.** Already the site's proven pattern (`/linter/`, the llms.txt
  generator). Crucially, §4.3 shows these are now near-zero marginal cost in CSS terms. High link ceiling
  (they are reference infrastructure), and they generate the first-hand artefacts §1.5 demands as a
  by-product.
- **Named frameworks / rubrics / checklists on their own canonical page.** Highest link ceiling measured
  (§4.1 Finding B). Very low production cost — this is thinking, not tooling. **The single best
  effort-to-payoff ratio in this document.**
- **Teardowns with reproducible receipts.** Directly satisfies the QRG's first-hand-experience criterion
  (§1.5), the "answer to objections" citability pattern (§2.5), and the failure-mode gap that sends
  developers away from AI answers (§3.3). Sustainable because the raw material is real docs sites, which
  are free and infinite.

**Sustainable with discipline:**

- **Comparison matrices.** Cheap to produce, but note §3.5: I found **no evidence** they drive AI citation,
  and the one cited page I examined had no tables. They also decay — a matrix is a maintenance liability
  with a visible wrong-answer risk. Ship them only where a reader genuinely needs lookup, and date them
  visibly.
- **Benchmark posts with published methodology.** Strong information-gain (§1.5) and highly citable. But
  each one is a real project, not a day's writing. **Budget these as multi-day efforts, not calendar
  filler.** Realistic rate for one person: perhaps one per fortnight, not one per week.

**Not sustainable for one person — recommend against:**

- **Original large-scale research** (the Ahrefs 137K-domain study genre). It requires a data asset we do
  not have. The *small*-scale version — "I checked 30 developer docs sites for X, here is the table and
  the method" — is sustainable and carries most of the citation benefit. **Scope down, do not drop.**
- **Embedded live demos of third-party products.** Ongoing breakage risk, external dependencies, and per
  §4.3 the styling is not free.

## 4.3 The no-new-CSS constraint, checked precisely

I inventoried all four stylesheets (2,891 lines total: `main.css` 2,221, `linter.css` 380, `flowcharts.css`
239, `visuals.css` 51) rather than assuming. **[VERIFIED]** by reading the files.

**Buildable today with zero new CSS:**

- **Any "input → process → itemised graded results" tool.** `main.css` carries a complete generic tool kit:
  `.tool-panel` (+ `-header/-body/-footer/-actions`), `.tool-workspace`, `.tool-section`, `.tool-actions`,
  `.tool-hint`, `.tool-status` (+ `-error/-loading/-success`), `.scan-form`, `.scan-submit`.
  `linter.css` adds a full **scored-findings** vocabulary: `.lint-grade-a` … `.lint-grade-f`,
  `.lint-score-bar`, `.lint-score-number`, `.lint-severity-error/-warning/-info`, `.lint-item` (+
  `-excerpt/-line/-message/-meta/-rule`), `.lint-group-*`, `.highlight-error/-warning/-info`.
  **This is the single most important build fact in this document: any new tool shaped like "paste
  something in, get a grade and a list of findings" is free.** That covers a large share of the ideas in
  `FORMAT-BACKLOG.md`.
- **Row-based editors / list builders** — `.page-list`, `.page-row`, `.page-row-fields`, `.page-row-controls`,
  `.form-grid`, `.form-field`, `.check-field` (the llms.txt generator's kit).
- **Stat/metric displays** — `.stats-band`, `.stats-grid`, `.stat-cell`, `.stat-num`, `.stat-desc`.
- **Progress bars** — `.tasks-progress-bar-wrap` (styled `progress` element, incl. WebKit and Moz pseudos).
- **Diagrams** — `.visual-container`, `.visual-title`, `.visual-caption`, and the full `.flowchart-*` set
  (`-node`, `-branch`, `-branches`, `-edge-label`, `-outcome`, `-outcomes`, `-note`, `-caption`).
  Inline SVG is viable because SVG carries its own presentation attributes.
- **Code with output** — `.code-block-wrapper`, `.code-output`, `.copy-code-btn`.
- **Article summary box** — `.article-summary` + `.article-summary-label` + styled `ul`/`li`. Purpose-built
  for the key-takeaways block the playbook recommends.
- **A visible updated-date** — `.post-meta-updated` **already exists.** Freshness display costs nothing.
- **Numbered procedures, task lists, TOC, FAQ** — `.numbered-steps`, `.task-list`/`.task-item`, `.toc`,
  `.faq-list`.

**Three constraints that need Ninad's decision — flagging rather than assuming:**

1. **Tables are scoped to `.post-content`.** Table styling lives at `main.css:1551–1580` as
   `.post-content table` / `thead` / `th` / `td`, with the mobile responsive rule
   `.post-content table { display: block; overflow-x: auto; }` at `main.css:2162`. **A table on a tool page
   outside `.post-content` will be completely unstyled.** Workarounds without new CSS: wrap the tool's
   results region in `.post-content`, or render results with `.lint-item` / `.page-row` instead of a
   table. **If we want first-class tables on tool pages, that needs a CSS decision.**
2. **`details`/`summary` are styled only inside `.faq-list`** (`main.css:1231–1234`). Collapsible sections
   work if wrapped in `.faq-list`; anywhere else they fall back to browser defaults. Same for `select`,
   which is styled only within `.page-row`.
3. **There is no charting or data-visualisation CSS, and no `input[type="range"]` styling.** A calculator
   with sliders would render with browser-default controls (functional, but visually off-brand), and any
   chart must be hand-authored inline SVG with hardcoded presentation attributes. **Any format needing a
   real chart or a styled slider requires either a CSS decision or an inline-SVG-only approach.** I have
   ranked `FORMAT-BACKLOG.md` on the assumption that no CSS will be added, and marked the items this
   affects.

---

# Sources I dropped

Recording these so the decision is auditable and nobody re-imports them later.

| Source / genre | Why dropped |
|---|---|
| A cluster of agency posts on "Google Core Update 2026" (monstermegs, numediagroup, almcorp, orangemonke, lasso-up, launchcodex, clickcatcher, digitalapplied) | Undated or vaguely dated; no primary citations; mutually contradictory; collectively the origin of the three [KILLED] CWV claims in §1.2. Several read as AI-generated. |
| Posts asserting a "June 2026 Quality Rater Guidelines update" with section numbers (stanventures, theguidex, pravinkumar.co, hmdigitalsolution, johnelincoln, broworks) | Falsified directly against the live QRG PDF (182 pages, CreationDate 2025-09-10). Fabricated specificity. |
| "AI coding statistics 2026" roundup posts (axis-intelligence, digitalapplied, uvik, netcorp, secondtalent, getpanto) | Statistics-aggregator genre; misattributed and inflated at least one figure (§3.3 [KILLED]). Where they named a primary survey I went to the primary instead. |
| `medium.com/@beeos-ai` restatement of the Ahrefs llms.txt study | Second-hand restatement of a source I read directly. No added method. |
| Word-count-vs-ranking correlation studies | Confounded by construction (coverage causes both length and ranking); the undated ones also fail the dating rule. Basis for declining to answer §3.4 with a number. |
| `baselinelabs.ai/blog/llms-txt-google-search` | **Partially kept.** It correctly pointed me to Google's AI-optimization guide and the Gary Illyes/John Mueller statements, but it **would not state its own publication date**, so I used it only as a lead and cite Google's doc directly instead. Its unverified attributions (a Mueller Reddit comment with "date unspecified") are not used. |
| `searchengineland.com` core-update coverage | Not dropped for quality — SEL is reliable and dates its work — but it returns **HTTP 403** to WebFetch, so I could not read the primary text. Update dates were taken from Google's own status dashboard instead. Worth noting for future passes: SEL cannot be fetched by this agent. |

---

# Monthly re-check list

This is a standing role. Ranked by how fast the thing moves and how much it would change our plan.

**Check every month:**

1. **Google's ranking-update history** — `status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history`.
   A core update inside the 90-day window is likely (§1.1). Cheap, authoritative, 30 seconds.
2. **The `Last updated` stamp on three primary docs.** If a date moves, re-read; otherwise skip.
   - `developers.google.com/search/docs/fundamentals/ai-optimization-guide` (now 2026-07-10) — the most
     load-bearing doc in this report.
   - `developers.google.com/search/docs/essentials/spam-policies` (now 2026-05-15).
   - `developers.google.com/search/docs/fundamentals/creating-helpful-content` (now 2025-12-10).
3. **The QRG PDF's CreationDate** — one `curl` + `pdfinfo`. Currently 182 pages / 2025-09-10. A genuine
   revision here would be the most substantive change possible to §1.6.
4. **Our AI citation counts vs the competitive set** — re-run the §2.3 table
   (`site-explorer-ai-responses-count` + `batch-analysis`). This is our actual scoreboard, and
   ninadpathak.com's row is currently all zeros. **First non-zero citation is the leading indicator to
   watch.**
5. **Whether the Search Console Generative AI performance report has reached our property** (§2.7). Rollout
   is partial; the day it appears, it becomes our best first-party measurement.

**Check every quarter, or on a trigger:**

6. **SERP composition for our head terms** — re-pull `serp-overview` for `docs as code`,
   `api documentation best practices`, `llms.txt`. Watch the UGC share and whether an AI Overview has
   appeared or disappeared. Trigger: any core update completing.
7. **Crawler documentation for the four platforms** (OpenAI, Anthropic, Perplexity, Google). New user
   agents appear regularly, and a new citation-governing agent that our Cloudflare-managed robots.txt does
   not anticipate is a silent-failure risk (§2.6).
8. **Whether llms.txt evidence has changed.** Current position is well-evidenced (§2.2), but it is the
   claim most likely to be revisited. Re-check if any platform documents actually consuming it.

**One-off items not yet closed:**

- **Cloudflare edge AI-bot blocking** — needs a dashboard check by Ninad (§2.6). Highest-value open item.
- **`Content-Signal: ai-input`** — currently omitted; recommend setting it explicitly to `yes` (§2.6).
- **Brand Radar** — not on the plan (§2.0). Needed for page-level citation attribution and prompt-level
  share of voice.
- **Snippet-eligibility audit** — confirm no template emits `nosnippet` or a restrictive `max-snippet`
  (§2.1); this is the one hard technical gate on AI-feature eligibility.
