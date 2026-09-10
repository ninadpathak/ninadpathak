# Semrush research record

Retrieved 10 September 2026 for the technical-writing strategy. Reports use `database=us`, meaning United States desktop search; no India or global extrapolation is made.

`display_date` was omitted to request the latest available snapshot. The provider did not return a dated observation field in these reports, so the retrieval date must not be described as the underlying measurement date.

## Reproducing the requests

Each JSON file preserves the report name, parameters, and unedited tool response. Discover the appropriate Semrush toolkit, read `get_report_schema`, and pass the saved report and parameters to `execute_report` to refresh a report.

| File | Purpose | Result and caveat |
|---|---|---|
| `baseline.json` | Domain totals | Rank 16,883,973; organic keywords 14; estimated traffic 0 |
| `rankings.json` | Domain ranking URLs | Returned 14 rows within a limit of 50, including duplicate keyword/URL observations |
| `competitors.json` | Automatic domain competitors | `ERROR 50 :: NOTHING FOUND`; no organic competitors inferred from this failed report |
| `keywords.json` | Batch of 28 relevant terms | Volume, CPC, KD, and raw intent codes |
| `discovery.json` | Broad documentation exploration | Returned 40 rows, with substantial unrelated demand; excluded from market sizing |
| `serp-docs.json` | Docs-as-code SERP | Top ten returned organic results |
| `serp-writing.json` | Writing-examples SERP | Top ten returned organic results |
| `serp-template.json` | Documentation-template SERP | Top ten returned organic results |
| `gap.json` | Filtered keyword comparison | Failed because the endpoint rejected the schema-advertised keyword filter |
| `gap-retry.json` | Unfiltered competitive comparison | Successful union of Tom Johnson and Write the Docs, minus Ninad's domain, capped at 30 rows |
| `competitor-wtd.json` | Write the Docs keyword sample | Documentation-filtered report, capped at 30 rows |
| `competitor-tom.json` | Tom Johnson keyword sample | Documentation-filtered report, capped at 30 rows |

The comparison's zeros denote absence from that report's ranking set, not absence from the web. The filtered domain samples supplement the volume-sorted comparison because the latter includes unrelated book and vendor queries.

## Baseline and limitations

The domain overview reports 14 organic keywords, while the detailed report contains repeated observations for `anthropic contextual retrieval` and `best llm for system design`. Preserve the provider total and avoid silently relabeling the row count as a deduplicated query count.

The current template URL ranks at position 65 for `code documentation template` with volume 90. The list also includes a `/blog/` URL and `/static/visuals/context-memory`; those are URL-inspection leads, not authority to delete or migrate anything.

Semrush traffic is modeled. The saved local `planning/leading-indicators.md` entry for 10 September supplies first-party context but was not refreshed by this task, and its query classification does not establish whether a particular request came from a human.

The `technical documentation` volume of 1,830,000 is anomalous relative to adjacent queries. Its trend and broad-match contamination make it unsuitable for demand sizing without further validation; no summed market estimate or traffic projection uses it here.

KD values differ between keyword and domain reports, for example `api documentation` is 47 in the batch and 52 in the competitive comparison. Use a named report consistently, retain both raw values, and refresh priority keywords before production.

CPC is an advertising metric. It does not establish consulting revenue, buyer quality, or organic conversion probability; intent codes are retained raw and reader intent in the strategy is an editorial interpretation of query wording and sampled SERPs.

## Competitor interpretation

Write the Docs and Tom Johnson were selected after the docs-as-code SERP returned both. They are relevant teaching benchmarks, not automatically discovered competitors for Ninad's small current search footprint.

| Observed query | Competitor result | Ninad observation | Editorial consequence |
|---|---|---|---|
| docs as code | Write the Docs first in sampled SERP; Tom Johnson seventh | No row in returned domain rankings | A tested change workflow can add a distinct practical artifact |
| documentation as code | Write the Docs first, volume 320 | No row in returned domain rankings | Treat as a synonym cluster with docs as code, not another page |
| how to write api documentation | Tom Johnson third, volume 140 | No row in returned domain rankings | Refresh the existing API owners before creating broad instruction |
| technical documentation best practices | Write the Docs second, volume 170 | No row in returned domain rankings | Broad institutional guidance is established; show a tested decision |
| documentation portfolio | Tom Johnson positions 7 and 8, volume 50 | No row in returned domain rankings | Annotated attributable work belongs in the existing portfolio |
| api documentation | Write the Docs 32 in comparison, volume 2,900 | Zero in comparison | A broad term is a later ambition, not a quarter-one traffic commitment |

The template SERP includes Microsoft and Atlassian alongside template providers. The examples SERP includes Reddit and general career-oriented pages; a developer-product examples page must make its scope plain and provide the examples near the top.

The strategy's differentiation is an inference from these result types. No full content audit of those ten-result SERPs was performed, and no claim is made that a competitor lacks the proposed material.

## Primary writing references

- Paul Graham, [How to Write Usefully](https://paulgraham.com/useful.html), accessed 10 September 2026: precise claims with scope that remains true.
- Paul Graham, [Putting Ideas into Words](https://paulgraham.com/words.html), accessed 10 September 2026: writing as an aid to working out a thought.
- Paul Graham, [Writing, Briefly](https://paulgraham.com/writing44.html), accessed 10 September 2026: revision and reading aloud.
- Simon Willison, [What to Blog About](https://simonwillison.net/2022/Nov/6/what-to-blog-about/), accessed 10 September 2026: preserve things learned and built, with visible artifacts.

These sources guide editorial practice, not an imitation of an author's voice. The proposed experiments remain unrun, and no personal experience has been invented to fill a brief.
