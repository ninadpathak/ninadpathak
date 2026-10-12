# Website improvement priorities — October 12, 2026

The next investment should help a prospective client understand what they can hire Ninad to do, then measure whether that visit becomes a qualified enquiry. The site already has articles and working booking links; its search audience remains small, its commercial offer lacks a dedicated page, and its lead event counts calendar opens.

I would start with confirmed-booking measurement and one focused software documentation service page. I would then improve the route from existing documentation articles into that offer, while measuring renamed URLs together. A larger batch of general AI articles has weaker evidence for producing client work.

## Search performance and its limits

Search Console was queried read-only for `sc-domain:ninadpathak.com`, Web search, finalized data. The latest returned date was October 10, 2026. GSC reporting dates follow Pacific Time; the audit date uses Asia/Kolkata.

| Metric | September 13–October 10 | August 16–September 12 |
|---|---:|---:|
| Property clicks | 7 | 4 |
| Property impressions | 1,173 | 1,809 |
| Property CTR | 0.60% | 0.22% |
| Property average position | 24.39 | 57.94 |

Clicks rose by three and impressions fell by 35.2%. This sample cannot establish recovery, content quality improvements, or enquiry growth. Over July 13–October 10, the property recorded 23 clicks and 4,864 impressions.

The aggregate position shift is particularly misleading as a headline. For the same seven named nonbrand queries with at least five impressions in each window, fixed weights based on the smaller period's impression count produce positions of 52.32 previously and 50.81 currently. That is a modest shift within this selected cohort, not the apparent sitewide jump; the cohort still cannot hold country, device, or result presentation constant. `pglite vs sqlite` moved from 8.69 to 8.90, while `code documentation` moved from 59.04 to 63.81.

Named queries expose only 504 current impressions and two of the seven clicks. Both visible clicks are for `ninad pathak`; the queries behind the other five clicks are withheld. This does **not** prove that all clicks are branded, that buyer demand is absent, or that the site received no enquiries. Page rows sum to 1,412 impressions because page aggregation differs from property aggregation; that sum must not replace the property total. See [Google's API aggregation and completeness rules](https://developers.google.com/webmaster-tools/v1/searchanalytics/query).

The US accounted for 589 property impressions and one click; India had 153 and three clicks. Desktop had 965 impressions and four clicks, versus mobile's 201 and three. These samples support checking both devices and US buyer language; they do not justify a country-specific strategy or a desktop conversion diagnosis.

## Recommended order

Effort and impact below are qualitative judgments, not traffic or revenue forecasts. Every action requires a separate implementation decision; this audit changed no website content or configuration.

| Priority | Action and affected surface | Evidence | Expected value / effort | Success check |
|---|---|---|---|---|
| P1 | Measure completed, qualified enquiries across booking buttons and `/contact/` | Live JavaScript fires `generate_lead` when a booking trigger is clicked, before the modal opens | High decision value / medium effort | Modal opens and completed bookings are separate; confirmed meetings reconcile with calendar records; each enquiry has an entry page and qualification outcome |
| P1 | Create one software documentation service destination, linked from homepage and Work | Homepage describes three services but its service rows have no destinations; live sitemap has no service route. Commercial SERPs contain service pages | Potentially high buyer relevance / medium effort | Page is indexable and linked; offer is understandable without a call; track qualified enquiries and relevant service-query impressions |
| P2 | Normalize renamed URLs in reporting and settle the existing SEO loop target | The loop still points to `/articles/internal-vs-external-documentation/`; it now redirects to `/articles/internal-vs-external-docs/` | High measurement reliability / low effort | Baseline includes both aliases; loop watches the current canonical; next report distinguishes migration from an editorial experiment |
| P2 | Improve the client path from `/articles/internal-vs-external-docs/` | Old/new rows have 92 page impressions and one click; page relevance is directly aligned with documentation work | Potential client relevance / low to medium effort | A contextual route explains a documentation engagement and shows relevant proof; measure clicks through to service and confirmed enquiries |
| P3 | Test two existing AI pages selectively: `/articles/browser-vector-search/` and `/articles/vector-embeddings/` | Observed query positions are within reach, but volumes and buyer fit constrain value | Modest traffic potential / medium effort | Track the same named queries and canonical pages; preserve versioned evidence and measure downstream enquiries |
| P3 | Add topic navigation to `/articles/`, and control standalone visual indexing | Article index has no links to the three populated archives. Sample visual pages are indexable standalone assets with no booking context | Navigation and indexing hygiene / low effort | Archives can be reached from the article index; selected visual URLs leave standalone results while parent article embeds remain usable |

### Count an actual enquiry

The live script records `generate_lead` immediately after a user clicks a booking trigger. It therefore measures intent to open a calendar, including users who close it without booking. The source behavior is at `static/js/main.js:120`; a live extract is saved alongside this report.

Use a separate diagnostic event for opening the calendar. Count a lead only after a confirmed booking or an actual enquiry; use the calendar's verified confirmation signal if available, or reconcile bookings manually until an integration is established. Record qualification separately so an irrelevant meeting does not look like a successful client acquisition. Keep personal contact details out of analytics event parameters.

This audit did not query GA4 or booking records, so it cannot report session conversion rates or lead counts. A prior weekly digest reported unavailable conversion access; that historical access state was not retested here. The current event's meaning was verified directly from live JavaScript.

### Give a buyer a service page

A proposed destination such as `/technical-documentation-services/` should explain the software audience and the engagement before asking for a call. Its outline should contain:

- The developer problem the engagement addresses, with an example of the documentation work required.
- Actual deliverables Ninad offers, plus the product access and engineering review needed to produce them.
- Relevant published samples, with a case study that explains Ninad's contribution and the observable result.
- The engagement process, followed by an enquiry route asking about the product and its reader.

Only include terms Ninad can actually honor; this audit does not invent prices or turnaround times. Start with one page and preserve the distinctive homepage voice. Link the homepage's Documentation row to the service destination, and add a contextual link from Work and the documentation archive.

Semrush's US keyword snapshot provides commercial research leads: `technical writing services` has estimated monthly volume 880 and difficulty 25; `technical documentation services` has volume 390 and difficulty 17. These are estimates for queries, not obtainable traffic. The sampled search results contain dedicated service pages from [MadCap](https://www.madcapsoftware.com/services/technical-writing/) and [TimelyText](https://www.timelytext.com/services/documentation-services/). Several results cover industrial or regulated documentation, so Ninad's page should state its software/API audience rather than pursuing every meaning of the broad query.

### Measure URL moves together

The internal/external article's old route makes one 301 hop to a 200 destination with a self canonical. GSC inspection records the destination as indexed and self canonical after its October 10 crawl. The old inspection still reflects an October 1 crawl and a legacy Google canonical. This is migration settling, not evidence that another redirect needs adding.

The same pattern appears for `local-wasm-vector-benchmarks` → `browser-vector-search`; the new destination is indexed with a self canonical. The old embedding page is explicitly recorded as a redirected page whose Google canonical is now `/articles/vector-embeddings/`.

Combine old and new aliases for historical evaluation, retaining the raw rows. Current page-row impressions on renamed source slugs total 690 out of 1,412 page-row impressions; that is a measurement continuity issue, not a property-level percentage or proof of harmful duplication. Pause additional cosmetic slug moves while these settle. Preserve the working redirects and update the SEO loop's canonical target at `planning/seo-loop/config.json:4` together with its brief and baseline.

### Improve pages with actual evidence

| Current canonical page | Observed opportunity | What to change or test | Limitation |
|---|---|---|---|
| [Internal/external documentation](https://ninadpathak.com/articles/internal-vs-external-docs/) | Old route: 84 impressions, one click, page position 10.42; current alias: eight impressions. `external documentation`: four named impressions at 26.5 | Keep its useful definition and placement audit. Add a specific invitation to a documentation engagement with a relevant work sample, then link the service page when it exists | Page position is not the main query's position; buyer intent and conversion remain unmeasured |
| [Browser vector search](https://ninadpathak.com/articles/browser-vector-search/) | `pglite vs sqlite`: 80 named impressions, zero clicks, position 8.90; reverse phrasing: 14 at 6.71 | The title already says PGlite vs. SQLite-vec. Test whether the description and early comparison explain the browser/vector use case clearly; keep benchmark versions and measurement limits visible | Semrush US volume is only 20. Old/new rows reflect a URL move, not demonstrated cannibalization; this is a secondary credibility/traffic opportunity |
| [Vector embeddings](https://ninadpathak.com/articles/vector-embeddings/) | `vector embedding models`: six named impressions at 5.33; `ai vector embedding`: seven at 6.14 | Review the model comparison against current primary documentation before refreshing it. Link a relevant example of Ninad's developer education work at the decision point | Tiny samples; current comparisons contain time-sensitive model claims. Do not promise a material traffic increase |

The internal/external page already opens with a direct definition and already contains comparison material. Recommending a generic answer-first rewrite would repeat work that is visible live. The pending weekly draft concerns specific replacements, so reconcile it with the deployed text before applying anything.

`code documentation` has 63 impressions at position 63.81, while `llm inference optimization` has 61 at 71.69. They are deeper editorial projects, not immediate snippet wins. Semrush sees 26 US ranking keyword rows with estimated zero traffic; the recorded positions run from 44 to 88. That third-party estimate must not override measured GSC clicks, and the keyword rows include older URLs and different observation timestamps.

The tools currently have sparse GSC evidence: `/linter/` has three page impressions and `/tools/` four; the other tool routes have no returned current page rows. This is insufficient evidence to build another tool as the first improvement. Semrush's checker and validator query volumes suggest possible demand, but page-query fit and distribution need validation before investment.

### Improve navigation and visual indexing

[The article index](https://ninadpathak.com/articles/) offers a chronological list without links to the populated Technical Documentation, Developer Experience, or AI Engineering archives. Homepage topic chips already exist. Reuse those destinations on the article index so readers can find an area of interest without paging through unrelated posts; do not create a new category system.

Standalone `/static/visuals/chunking` and `/static/visuals/context-memory` return 200 with neither a canonical nor a noindex directive. Semrush reports rankings for both; GSC records 16 current page impressions across static assets, including knowledge-silo and attention-heatmap queries. These are small numbers, so treat this as hygiene rather than a principal growth lever.

For visuals whose sole purpose is embedding in articles, consider `noindex, indexifembedded` while leaving them crawlable. Verify that the parent article still renders the visual and remains indexable before rollout. Google's [robots rule documentation](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag) supports embedded indexing with that combination and explains why robots.txt blocking prevents the noindex rule from being read. Keep intentionally standalone tools or useful downloadable pages outside this rule.

## What is already healthy, and what remains unknown

Selected live pages return 200 with self canonicals and indexable robots metadata. The documentation article's renamed destination is indexed. Booking triggers are present, and the code-documentation page is live, indexed, and returns 200.

The earlier local output audit's broken `/articles/code-documentation/` link is a **local deployment risk only**: the working copy marks that post draft, while the live site retains the published article. A build from the current dirty checkout could remove that live page and fail its SEO audit. Resolve that source/live discrepancy before any future deployment; no live link repair is warranted from this observation. The live sitemap has 117 URLs; existing local generated output has 116.

This audit does not include a full live crawl, backlink audit, or current field performance data. The previous weekly report's Lighthouse measurement is historical lab data and should not become a current performance claim. No Ahrefs tools are exposed in this session; its absence from the callable tool inventory does not establish whether Ninad has an account or another configuration elsewhere. Semrush domain-competitor discovery and the PGlite SERP report returned `NOTHING FOUND`; commercial SERP reports and keyword summaries succeeded.

## Evidence and implementation boundary

The read-only audit created only this report and nonsecret evidence in its dated audit directory. It did not publish, alter credentials, create a paid project, or change the site's source/configuration. Existing dirty work was preserved.

| Evidence file | Contents |
|---|---|
| `gsc-raw.json` | Current/prior totals and page/query rows; device and country dimensions; 90-day context; finalized-data requests |
| `analysis.json` | Fixed-weight query cohort, explicit coverage counts, and retained old/new page rows for priority URLs |
| `gsc-inspections.json` | Google's recorded indexing and canonical state for seven selected URLs |
| `semrush.json` | US keyword snapshots, domain visibility, commercial SERP competitors, report URLs and usage metadata |
| `live-pages.json` | Direct HTTP observations for selected live pages, including redirect chains and indexing metadata |
| `live-js-tracking-extract.txt` | Live booking-trigger event behavior |

Use confirmed qualified enquiries as the business measure. Use query clicks and canonical consolidation to assess the selected search changes, with a dated change log and preserved baselines. If the next window still has a handful of clicks, report the observations without declaring a winning variant.
