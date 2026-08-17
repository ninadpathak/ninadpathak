# Token-match contamination sweep — the seven-cluster universe

**Date:** 2026-08-17 · **Agent:** `seo-currency` · **Branch:** `seo/currency`
**Input:** `planning/research-cache/DERIVED-full-universe.json` (1,129 kws, 336,180/mo)
**Reproducible sweep:** `planning/research-cache/_contamination_sweep.py`
**Full audit with every removed keyword and its parent topic:** `planning/research-cache/DERIVED-contamination-sweep.json`
**Paid calls: 0.** Parent topics were already banked; every SERP read used free WebSearch.

---

## The answer, first

| | Prior | Swept | Change |
|---|---:|---:|---:|
| Keywords | 1,129 | **940** | −189 |
| Volume/month | 336,180 | **293,800** | **−42,380 (−12.6%)** |
| KD≤20 keywords | 656 | **556** | −100 |
| KD≤20 volume/month | 158,950 | **133,790** | −25,160 (−15.8%) |
| Share of SERPs with an AI Overview | 49.2% | **52.6%** | **+3.4pp, worse** |

**The day-90 band of 350–1,350 does not hold. Restated: 306–1,176, central ~629.**
Working in §3. It is not a large restatement, and I am not going to dress it up as one —
but it moves in the wrong direction on two independent counts, and the previous number
should not be quoted again.

**The conclusion the band supports is unchanged.** The 10,000/month target is still
unreachable inside 90 days, and the binding constraint is still publishing throughput —
22.2 mature-equivalent pages by day 90 — not addressable volume. Contamination inflated the
denominator and modestly inflated the band. It did not change the structural finding.

---

## 1. Per cluster

| # | Cluster | Before | | Removed | | After | | Cut |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| | | kws | vol/mo | kws | vol/mo | kws | vol/mo | |
| 1 | Technical documentation & docs ops | 322 | 63,730 | 7 | 660 | 315 | 63,070 | 1% |
| 2 | Developer experience & DevRel | 56 | 7,930 | 22 | 1,890 | 34 | 6,040 | **24%** |
| 3 | AI agents, memory, RAG, inference | 347 | 150,140 | 1 | 350 | 346 | 149,790 | 0% |
| 4 | AI Overviews & AI-search citation | 58 | 23,880 | 13 | 1,660 | 45 | 22,220 | 7% |
| 5 | Reddit marketing | 78 | 33,360 | 33 | 15,060 | 45 | 18,300 | **45%** |
| 6 | Forums & community building | 94 | 24,140 | 31 | 8,230 | 63 | 15,910 | **34%** |
| 7 | Technical & community events | 174 | 33,000 | 82 | 14,530 | 92 | 18,470 | **44%** |
| | **Total** | **1,129** | **336,180** | **189** | **42,380** | **940** | **293,800** | **12.6%** |

**The shape of the damage matters more than the total.** Cluster 3 — 45% of the universe by
volume — is essentially clean, one keyword out. Clusters 1 and 4 are close to clean. The
contamination is concentrated in **clusters 2, 5, 6 and 7**, which lost 24% to 45% each.
Those are precisely the four clusters the prior document called "the winnable ones" on the
strength of their KD≤20 share. Their winnability was real; their size was not.

### Cluster 1 — documentation, 660/mo out (1%)

The nursing-charting vein was already gone. What survived:

| Removed | Vol | Why |
|---|---:|---|
| `hospital documentation software` | 200 | parent `medical document management software` — clinical records |
| `loan documentation software` | 150 | parent `loan document software` — lending |
| `audit documentation software` | 100 | parent `auditing software for accountants` — names the industry outright |
| `employee behavior documentation template` | 60 | HR disciplinary paperwork |
| `employee conversation documentation template` | 60 | same |
| `employee documentation template` | 50 | same |
| `audit documentation example` | 40 | SERP: PCAOB AS 1215, "work papers", depreciation |

`audit documentation software` and `audit documentation example` are the pair from the tool
shortlist. Both confirmed. Together 140/mo, which was 7% of the 1,940/mo "build-an-actual-tool"
subset in §5a.

### Cluster 2 — DevEx/DevRel, 1,890/mo out (24%)

The worst proportional damage relative to how small it already was. Everything here is a
token match on *developer*, *development*, *experience* or *marketing*:

| Group | Vol | Examples |
|---|---:|---|
| Adobe Experience Manager | 600 | `adobe experience manager developer guide|certification|training` |
| Real estate & construction | 450 | `home developer marketing agency`, `real estate developer marketing` |
| Web/email marketing developer roles | 360 | `email marketing developer`, `digital marketing web developer` |
| Salesforce Marketing Cloud cert | 280 | incl. `marketing-cloud-developer dumps` — exam dumps |
| Vendor navigational | 140 | `apple worldwide developer relations certification authority` (a TLS certificate) |
| Job-seeker "no experience" | 60 | `software developer no experience` |

**Cluster 2 is now 6,040/mo across 34 keywords.** It was already the smallest cluster and
placed nothing in the top 15. At this size it cannot carry a cluster of its own on search
volume; keep it for positioning, not for traffic.

### Cluster 3 — AI agents/RAG, 350/mo out (0%)

One removal: `ai insurance agent` (350) — insurance sales agents, token match on *agent*.

I scanned this cluster twice, because at 45% of the universe a false clean would be the
most expensive error available. The second scan flagged 54 parent topics with no AI
vocabulary and 17,350/mo — and on inspection nearly all were real ML terms my regex simply
did not cover: `chromadb`, `pgvector`, `word embeddings`, `bert embeddings`, `faiss`,
`cosine similarity`, `clip`, `fasttext`, `rope embeddings`. `linkedin mcp server`
(parent `linkedinjobs`), `tavily mcp server`, `context7 mcp server` and
`ai customer support agent` (parent `fin`, Intercom's agent) all have misleading parent
topics and are genuine. **Cluster 3 is clean, and that is a real finding rather than an
unexamined one.**

### Cluster 4 — AI Overviews, 1,660/mo out (7%)

| Group | Vol | Why |
|---|---:|---|
| `chatgpt … prompts …` family, 11 kws | 870 | Prompt templates for using ChatGPT to *do* SEO copywriting. This cluster is about being cited **by** assistants, not using one to write meta descriptions. Inverted job, same tokens. |
| `hide google ai overviews` | 700 | Consumers wanting AI Overviews switched **off**. Browser-extension market. |
| `chatgpt para seo` | 90 | Spanish-language query in a US English universe |

The `chatgpt seo` head terms survive: SERP for `chatgpt seo` returns Semrush "How to Show
Up in ChatGPT Responses" and SEO Sherpa "Optimize Your Content for AI Search", which is the
right sense. Only the explicit prompt sub-family is the wrong job.

### Cluster 5 — Reddit, 15,060/mo out (45%)

| Group | Vol | Why |
|---|---:|---|
| Consumer subreddit discovery, 15 kws | 11,120 | `subreddit` (4,700), `what is a subreddit` (1,400), `subreddit list`, `finder`, `search`, `viewer`, `meaning`. SERP for `subreddit`: Reddit Help, Wikipedia, Dictionary.com slang. Zero marketing intent, and Reddit itself owns them. |
| `progressivegrowth2` junk token, 3 kws | 1,570 | A Reddit username, not a topic |
| Reddit as a source for other topics, 6 kws | 1,150 | `youtube ads reddit`, `facebook ads reddit`, `twitch ads reddit`, `squarespace seo reddit` — parent topics point at the *other* platform |
| Reddit ad product navigation, 5 kws | 1,000 | `reddit ads login|logo|account|help|help center` |
| Ad blocking, 4 kws | 220 | People blocking Reddit ads. Opposite intent. |

The prior pass removed `<topic> subreddit` navigation and kept the generic `subreddit` head
terms, which are the same intent at higher volume. **`subreddit` at 4,700/mo was the second
largest keyword in the cluster and is consumer navigation.**

Kept deliberately: `reddit seo` and its family (SERP-verified on-niche), `subreddit stats`
and `subreddit growth` (marketer tooling), the `how to make/create/start a subreddit` family
(a real Reddit-marketing action).

### Cluster 6 — community, 8,230/mo out (34%)

| Group | Vol | Why |
|---|---:|---|
| HOA / property management, 4 kws | 3,350 | **`community management` at 2,600/mo has parent topic `hoa`.** SERP is entirely HOA and condo association managers, and one definition result reads "community management (also called property management)". `community management services` (500) same. `residential community management software` parent `hoa management software`. `community management service` parent `cms hoa`. |
| Discord navigational, 4 kws | 1,330 | `discord community guidelines` (parent `discord rules`), `discord community server(s)` (parent `discord login`), `discord community manager` (parent `discord jobs`) |
| Off-niche vertical communities, 10 kws | 1,330 | `aarp online community`, `online artistic|learning|gaming|writing|health|fitness|trading community` — consumers looking for a community to join |
| Corporate team building, 3 kws | 1,100 | `community building activities|games|questions`, all parented to `team building activities` |
| Civic community engagement, 7 kws | 790 | Public-consultation software. SERP: Granicus, Local Housing Solutions, Simply Stakeholders. One parent topic is `publicinput`, a civic-tech vendor. |
| Classroom & dictionary, 2 kws | 240 | `community building examples` parent `building community in the classroom`; `community building synonym` |
| Job queries, 1 kw | 90 | `online community manager` parent `online community manager jobs` |

**This is the surviving-head case.** The prior pass stripped 59% of cluster 6 as HOA and
still left the HOA industry sitting on the cluster's single largest keyword under a
different phrase. Volume-ranked cleaning catches veins; it does not catch heads.

Kept after SERP check: the `community management software|platform|tools` family — Glue Up,
Sprinklr, Bevy and G2's "Online Community Management" category dominate, with PayHOA a
minority. Partially contaminated, majority on-niche.

### Cluster 7 — events, 14,530/mo out (44%) — **provisional, `seo-90day` owns the row level**

You told me `seo-90day` is probing this cluster for the same defect, so this is a magnitude
estimate to correct the total, not a settled row-level pass. **Reconcile before either
number is used.**

The split I get:

| Slice | kws | vol/mo |
|---|---:|---:|
| Clearly community/technical (hackathon, meetup, community event, dev conference) | 41 | 12,280 |
| Clearly commercial event industry | 50 | 9,150 |
| Ambiguous, resolved by SERP as commercial | 83 | 11,570 |

SERP for `how to host a virtual event`, the head of the ambiguous slice: Zoom Webinars,
Lucidspark, Whova, ON24, wiz-team, Wharton IT — "speaker fees, attendee gifts, video and
audio equipment", "attendee acquisition and marketing". Corporate webinar industry.

The ambiguous slice is dominated by corporate event *operations*: `virtual event branding`
(parent `event branding services`), `virtual event landing page` (parent `landing page for
event`), `virtual event feedback survey` (parent `event survey questions`), `run of show
template for virtual event`, `virtual event attendee engagement`. A DevRel running a
community meetup does not search `virtual event branding`.

My rule removes 82 keywords / 14,530/mo. **Two caveats I want on the record:**

1. **One false positive found and fixed:** `community event planning` (90/mo) was caught by
   the `event planning` token and is genuinely the job. Restored.
2. **My rule under-removes.** `virtual event guide`, `virtual event metrics`,
   `virtual event themes` and `virtual event hosting platforms` survive it and probably
   should not. So 14,530/mo is a **floor** on cluster 7's contamination.

---

## 2. Two removals the parent topic would have made wrongly

Recorded because they are the argument for why the SERP step is not optional, and the
reason I did not simply trust the parent-topic field:

- **`developer portal` (1,600/mo, cluster 1)** — parent topic `discord developer portal`,
  which reads as navigational to Discord's own product. SERP: OpsLevel, Zuplo, Pronovix,
  Port.io, Azure API Management, getDX. A genuine docs-ops and platform-engineering concept
  and one of cluster 1's larger terms. **Kept.**
- **`reddit seo` (1,300/mo, cluster 5)** — parent topic `latest seo`, which reads generic.
  SERP: Search Engine Land, Siege Media, SEO Sherpa, Sprout Social, Semrush, all on
  optimising brand presence on Reddit for search. **Kept.**

Parent topic is the cheap first filter. It is not sufficient on its own, in either
direction.

## 3. The restated band

The band's derivation touches the universe in exactly two places, so only those two inputs
change. Maturity (22.2 mature-equivalent pages), position probabilities, CTR assumptions
and legacy clicks are all held at the prior values deliberately.

**Input 1 — mean head volume of the best KD≤20 keywords.** Contamination was concentrated
in the winnable slice: **62 of the best-400 KD≤20 keywords were contaminated, 22,150/mo**,
including `subreddit` (4,700, KD 14) and `community management` (2,600, KD 13).

| Scenario | Selection | Head vol before | after | change |
|---|---|---:|---:|---:|
| Low | best 400 KD≤20 | 354 | 313 | −11.5% |
| Mid | best 250 KD≤20 | 491 | 439 | −10.7% |
| High | best 150 KD≤20 | 702 | 625 | −11.0% |

**Input 2 — the AI Overview haircut gets worse.** Contaminated SERPs carried *fewer* AI
Overviews than the real niche does — HOA directories and corporate event vendors are less
AIO-heavy than technical queries. Removing them raises the share from 49.2% to **52.6%**,
so at 35% click loss the multiplier moves from ×0.8278 to **×0.8159**.

| | Low | Mid | High |
|---|---:|---:|---:|
| Prior total | 349 | 710 | 1,335 |
| Campaign raw × head ratio | 357 | 740 | 1,392 |
| × new AIO multiplier (0.816) | 291 | 604 | 1,136 |
| Plus legacy | +15 | +25 | +40 |
| **Restated clicks/month** | **306** | **629** | **1,176** |
| Change | −12.2% | −11.4% | −11.9% |

### **Restated day-90 band: 306–1,176 clicks/month, central ~629.**

Against the 10,000 target the central estimate falls from 7.1% to **6.3%**.

**What did not change, and it is the part that matters.** Reaching 10,000 across 22.2
mature-equivalent pages still requires ~450 clicks/page/month. The best 150 keywords in the
cleaned universe average 625/mo of head volume. The gap is still ~34× and it is still a
throughput gap, not a volume gap. **A 12.6% smaller universe does not change the strategic
conclusion, because the universe was never the constraint.** What it changes is that the
band was quoted 12% too high, and three of the four clusters called "winnable" are between
a quarter and a half smaller than recorded.

### Two things that keep this a floor, not a measurement

1. **Clusters 5, 6 and 7 hit the 250-row API limit** in the original pull, so their true
   volumes were always floors. Cleaning a floor leaves a floor.
2. **My cluster 7 rule under-removes** (§1), and cluster 7 is `seo-90day`'s to settle.

Both push the same way: the corrected total of 293,800/mo is more likely to fall further
than to recover.

## 4. Cluster misassignment, separate from contamination

Not inflation — it does not change the total — but it misstates the per-cluster split and
affects which cluster gets seeded:

- **All 53 no-parent keywords in cluster 1 are llms.txt terms** (`llms.txt standard`,
  `websites using llms.txt`, `llms.txt checker`, `llms.txt validator` …), 8,760/mo. They
  have no parent topic because the term is too new for Ahrefs to have assigned one — **a
  missing parent topic is not evidence of contamination**, which is worth stating since the
  sweep method leans on that field. By subject these belong to **cluster 4**
  (`ai-search-optimization`), where the tools live, not cluster 1.
- `best ai agent projects from 2025 hackathons` (800/mo, cluster 3) has parent topic
  `hackathon agency`. Kept in 3, flagged as a possible cluster-7 assignment.

Moving the llms.txt block would take cluster 1 to ~54,310/mo and cluster 4 to ~30,980/mo.
**I have not moved it** — the cluster map is `seo-90day`'s to own, and the llms.txt seed
article is already being written into cluster 4, which may settle it anyway.

## 5. The `llms.txt checker` targeting fix

Folding in the correction from my own selection document, as asked.

`llms.txt checker` (150/mo Ahrefs, 110/mo Semrush) is **the same job** as the shipped
`/llms-txt-validator/`. Competitors serve both phrasings on one page — `mrs.digital` titles
its page "LLMs.txt Checker & Validator", `rankability.com` uses "Generator & Checker".
**Do not create a synonym page.** A second URL for one job cannibalises the first.

What the existing validator page needs, for Codex, in the template's `TODO(copy)` slots:

- **`<title>` (slot 1)** must carry both phrasings naturally in 50–60 chars. It currently
  reads `llms.txt Validator | Ninad Pathak` and carries only one.
- **`<h1>` (slot 7)** must contain "validator" and should reach "checker" in the same line
  or the immediately following lead sentence.
- **Lead paragraph (slot 8)** should use "check" as the verb at least once, so the page
  answers the checker phrasing in its own words rather than by keyword insertion.
- **Reference section (slot 13)** should state plainly that checking and validating an
  llms.txt file are the same operation, which is true, useful, and disposes of the synonym
  question for a reader as well as for a crawler.

`llms.txt validator` (100/mo Ahrefs, 70/mo Semrush) and `llms.txt checker` together are
~250/mo on Ahrefs figures. Both are inside the cluster-1 no-parent block in §4 and would
move to cluster 4 with it.

## 6. Blocker

**Ahrefs is dead and confirmed dead.** `Access denied: MCP token is invalid` on every
endpoint including the free `subscription-info` one, reproduced independently. It is the
token, not a quota. Raised to Ninad.

**It did not block this sweep and would not have improved it.** The question here is what a
SERP actually shows, and free WebSearch answers that directly. Parent topics were already
banked in the JSON from the original paid pull. **Zero paid calls were made.** Semrush was
available but unnecessary: volume figures were not in question, meaning was.
