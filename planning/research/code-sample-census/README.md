# Code-sample validity census: execution protocol

**Status:** pilot instrument in progress
**Protocol frozen:** 2026-08-17
**Study owner:** `seo-currency`
**Paid calls:** 0

This directory turns candidate 1 in
`../EXPERIMENT-CANDIDATES-2026-08-17.md` into a runnable study. It is a
research artifact, not article copy.

## Question and estimands

The preregistered question is narrower than the original candidate wording:

> Across a deterministic page sample from the documentation sites of the 100
> most-downloaded PyPI projects, what fraction of code samples that the site
> identifies as Python source or Python-console input fail syntax parsing under
> the pinned parser?

PyPI explicitly warns that download counts are not a measure of project quality
or usage. The sample frame is therefore described as **most-downloaded**, never
"most-used".

The study reports two estimands, neither substituted for the other:

1. **Block-weighted:** failing blocks / all included blocks.
2. **Package-weighted:** the median package-level failure fraction, with packages
   that yield no included block reported separately rather than treated as zero.

The raw syntax-failure rate is not the headline. Every failing block is later
hand-classified as `broken`, `deliberate-invalid-example`, `context-fragment`, or
`extraction-artifact`. The audited `broken` fraction is the headline.

## Frozen sample frame

- Source mirror: ClickPy's public ClickHouse service, which the Python Packaging
  User Guide names as a free interface to the PyPI download data.
- Underlying source: PyPI Linehaul download logs.
- Window: 2026-07-18 through 2026-08-16 inclusive, the latest 30 complete dates
  visible when the frame was frozen.
- Ranking: `sum(count)` descending, project name ascending as a stable tie-break.
- Installer treatment: all installers. The aggregate daily table cannot remove
  mirrors; this limitation travels with every result.
- Size: 100 projects. Exclusion from the documentation census never causes the
  next-ranked project to be substituted.

`freeze_sample_frame.py` records the exact SQL, response hash, endpoint, fetch
time, and validation facts next to the CSV. The fixed SQL is also stored in
`sample-frame.sql`.

`resolve_docs_urls.py` applies the documentation-label rule below to every
project in that frame and preserves the relevant PyPI metadata plus the hash of
each full API response.

## Documentation-site resolution

For each frozen project, fetch and preserve `https://pypi.org/pypi/<name>/json`.
The first pilot chose a documentation root mechanically from
`info.project_urls` after label normalization:

1. exact label `documentation`;
2. exact label `docs`;
3. labels ending in `documentation` or `docs`.

That rule resolved only 57/100 and systematically excluded projects with real
docs under `Homepage` or `Docs: RTD`; see `RESOLUTION-2026-08-17.md`. It is
falsified as the final primary rule. No search-engine lookup or hand-picked
replacement is allowed. The replacement must mechanically test qualified docs
labels and supported-generator homepages, preserve resolution strata, and pass
inspection before any code crawl. The replacement resolves 80/100 in three
strata (63 label, 5 declared homepage, 12 repository homepage). All 80 roots must
still pass live redirect/generator inspection before page sampling starts.

## Page sampling

The full run must freeze this stage before parsing any result:

1. Fetch `robots.txt` and obey it. A denied site is `robots-denied`.
2. Discover XML sitemaps from `robots.txt` and the conventional `/sitemap.xml`.
3. Keep HTML pages on the resolved documentation host and path. Remove fragments,
   query strings, duplicate canonicals, non-200 responses, and obvious asset
   extensions mechanically.
4. Sort eligible URLs by
   `sha256("ninadpathak-code-census-v1\0" + canonical_url)` and take 50 per
   project. Hash ordering is the fixed random sample; alphabetical order would
   over-sample API-reference prefixes.
5. If no sitemap is available, breadth-first crawl the documentation root with
   sorted links and cap at 50 pages. Report sitemap and crawl populations
   separately because their selection mechanisms differ.
6. Freeze response bytes, final URL, status, content type, fetch time, and SHA-256.

The cap makes the result a page sample, not a census of every block on every
documentation site. The publication must use that wording.

## Inclusion and parsing

The extractor is generator-aware. Unknown generators are excluded and counted;
they are not passed through a permissive generic selector.

An included sample needs site-owned language evidence:

- explicit classes or attributes such as `language-python`,
  `highlight-python`, `language-pycon`, or `data-language=python`; or
- a Python-console prompt (`>>>`) inside a Sphinx or MkDocs code block. This
  second rule is necessary because the live Requests and HTTPX quickstarts label
  their Python transcripts `highlight-default` / generic `highlight`, not
  `python`.

Shell transcripts, output-only blocks, JSON, and unlabeled source are excluded.
The extractor records the selector and evidence for every included block.

- `python` blocks: parse with `ast.parse` under the pinned CPython image.
- `pycon` blocks: use `doctest.DocTestParser` and parse every extracted input;
  console output is never parsed as Python.
- Parse failure means only syntax failure. Imports are not installed or executed
  in tier 1.
- The full run must pin the CPython container by version and image digest before
  result generation. The current local Python 3.9 interpreter is acceptable for
  extractor tests, not for the final number.

## Pilot falsification gates

Do not run the 100-project crawl until all are true:

- generator adapters recover the expected samples from frozen Sphinx, MkDocs,
  and Starlight fixtures;
- a console transcript with output parses only its `>>>` inputs;
- an unknown generator is excluded even when it contains a plausible Python
  block;
- duplicate selectors cannot emit the same `<pre>` twice;
- every record has a stable content hash and block identifier;
- rerunning the frozen sample-frame query reproduces the same ordered project
  list, or the difference is recorded rather than overwritten.

## Current pilot result

The live feasibility read on 2026-08-17 corrected two predecessor assumptions:

- Requests currently has 36 `<pre>` blocks, but 34 sit under
  `highlight-default`; the ancestor is not `highlight-python`. Prompt detection
  is required for its console examples.
- Stripe's current server response does contain Python code, but custom token
  spans collapse whitespace under naive text extraction. It is an unsupported
  generator in v1, not evidence that the page has no code.

These corrections reduce false claims before the paid-in-time crawl begins.
