# Three original experiments this site can actually run

**Date:** 2026-08-17 · **Agent:** `seo-currency` · **Paid calls: 0**

**Run candidate 1 first: the code-sample census.** It converts the single most-repeated claim
in technical writing into a number nobody has published, it needs no model API and therefore
no non-determinism, and I have already spiked the extraction and found the confound that
would have sunk it.

**Four candidates died in falsification before these three survived.** Those are in §5,
because which questions are closed is as useful as which are open.

---

## A design constraint I did not expect, and it improves all three

None of the three surviving candidates uses a model API. That is deliberate, and it emerged
from the brief's own requirement.

The campaign has ten articles flagged for citing benchmarks with no reproducible artifact. A
model in the loop makes reproducibility structurally hard: the same prompt returns different
output next month, the model version is deprecated, and a reader cannot re-run your study and
get your number. **Every candidate here produces a number a stranger can reproduce exactly**,
because the inputs are public files and the analysis is deterministic code.

That also drops API spend to roughly zero across all three, so the real cost is hours.

---

## Candidate 1 — Do the code samples in developer documentation actually run?

### The exact question

**Of the Python code samples published in the documentation of the N most-used Python
packages, what fraction is not valid Python?** Secondary: of the fraction that is invalid, how
much is deliberate (illustrating an error) versus broken.

### Why this one

"Test your code samples" is the most repeated instruction in technical writing. It is an
article of faith with no published number attached to it. Putting a number on a belief the
field already holds is the cheapest citation there is: nobody has to be persuaded the question
matters.

### Method, and the three confounds I found by spiking it

I ran the extractor against live docs before proposing this, which changed the design three
times.

**Confound 1 — extraction is generator-specific, not universal.** My first extractor found
36 `<pre>` blocks on the `requests` quickstart and classified **zero** as Python. Sphinx puts
the language class on an ancestor `<div class="highlight-python">`, not on the `<pre>`.
Docusaurus, MkDocs-Material and Mintlify each differ again. **Design:** one extractor per
documentation generator, generator detected from the page's own markup, and the census
reports results per generator so a parsing failure cannot masquerade as a documentation
failure. Sites whose generator has no extractor are excluded and *counted as excluded*.

**Confound 2 — JavaScript-rendered docs return no code at all.** Stripe's API reference gave
6 `<pre>` blocks and no Python. **Design:** record fetch-mode per site and publish the
excluded list. This biases the sample toward statically-rendered docs and the write-up must
say so rather than imply full coverage.

**Confound 3, the one that would have sunk it — documentation deliberately publishes invalid
code.** Pydantic's docs gave 39 Python blocks with exactly one syntax failure, and that
failure looks like an intentional example of a mistake. A naive census reports that as a
broken sample. **Design:** the confound only touches the numerator, and the numerator is
small. At the ~2.6% failure rate the spike suggests, a 3,000-block corpus yields roughly 80
failures — few enough to **hand-classify every single one** as deliberate, broken, or
extraction artifact, and to publish that classification per block. The headline number is
then the hand-audited one, not the raw one.

**Fourth design choice: language tag as selection rule.** Only blocks the site itself labels
Python are tested. That makes inclusion mechanical rather than a judgement I could be accused
of tuning.

**Tiered result, because "broken" has degrees:**

1. Does it parse? (`ast.parse`, unambiguous, no execution)
2. Do its imports resolve against the package's current release?
3. *Optional, only if time allows:* does it execute in a sandbox with no credentials?

Tier 1 is the headline. Tiers 2 and 3 are extensions, and the study is publishable at tier 1
alone — which matters, because it means the piece cannot fail to exist.

**Sample frame:** the top N Python packages by PyPI download count, which is public and
reproducible, with the frame's snapshot date recorded. Not a hand-picked list.

### The artifact

A repo containing the extractor, the per-generator adapters, the frozen HTML snapshots of
every page crawled, a CSV of every block with its URL, generator, tier-1 result and
hand-classification, and the analysis script. **Anyone can re-run it and get the same number,
or point the frame at 500 packages instead of 100.**

### Cost

**API spend: zero.** Hours: roughly 12–18. Most of it is the per-generator extractors and the
hand-audit of failures, not the analysis.

### Interesting whichever way it comes out

- **High failure rate:** "X% of published Python samples in major docs do not parse" is a
  finding every docs team acts on.
- **Low failure rate** — the spike hints at this — is the *better* piece: "the most repeated
  advice in technical writing is solving a problem that is already largely solved; here is
  what the remaining failures actually are, and they are not what you would guess." That is
  contrarian, it is defensible, and it is more surprising than the alarming version.

Either way the number is new.

### Falsification

**Adjacent academic work exists and must be cited.** DOCREF (Zhong & Su, OOPSLA 2013,
"Detecting API documentation errors") detects broken code names and obsolete samples and
reported over 1,000 new documentation errors. There is a body of work on API-documentation
smells and evolution.

**But the specific census is open.** DOCREF targets javadoc corpora with a static analyser,
not live documentation sites, and it is thirteen years old. Repeated searching for a published
percentage across a modern live-docs corpus returned none — the literature establishes that
broken samples are *a problem*, not *how big a problem*. Ours must be positioned as
measurement-in-the-wild that stands on that literature, not as a novel discovery.

**Neither failure mode applies.** Not owned: no current census exists. Not ignored: the field
already believes the question matters.

---

## Candidate 2 — Are published llms.txt files even valid?

### The exact question

**Of the sites that publish an llms.txt, what fraction conforms to the llms.txt v2
specification, and which rules do they break?**

### Why this one

Ahrefs' 137,210-domain study is the definitive work on llms.txt, and its authors named this
exact gap in their own limitations: **they did not assess whether the files were well-formed
against the specification.** A study that fills a gap the field leader publicly left is the
cheapest citation path available, because the citation already has a natural anchor: anyone
citing Ahrefs on adoption needs someone on validity.

### Method

Take a public sample frame of sites known to publish llms.txt — the llmstxt.org directory plus
the documentation platforms that auto-generate it — fetch each `/llms.txt`, and run the
already-built, already-tested validator over it. Report conformance by rule, not just a pass
rate: which specific rule fails most, how many files are HTML served as text, how many are
empty.

**Confound 1 — auto-generated files dominate.** Mintlify and GitBook generate llms.txt
automatically, so a large share of the corpus is machine-produced and will conform or fail
uniformly. **Design:** classify each file as auto-generated (by fingerprinting the generator's
output shape) or hand-written, and report the two populations separately. A blended number
would describe neither.

**Confound 2 — the spec is permissive.** Only the H1 is required, so a naive "conformance
rate" would be near 100% and meaningless. **Design:** report against the spec's ordered
structure rule by rule, exactly as the validator already does, separating requirements from
conventions. The validator was built with that separation and 40 tests pin it.

**Confound 3 — served content varies by requester**, as established when Stack Overflow
returned HTTP 418 to an unknown client. **Design:** record status code and content-type per
fetch, publish them, and state that the census describes what a neutral fetcher is served.

### The artifact

The frozen corpus of fetched files, the per-file validator output as JSON, and the analysis
script. The validator itself is already public, tested, and shipped.

### Cost

**API spend: zero.** Hours: roughly 4–6, because the instrument already exists.

### Interesting whichever way it comes out

High conformance says the tooling is doing its job and hand-written files are the risk. Low
conformance says a large share of the llms.txt corpus is malformed, which — set against
Ahrefs' finding that almost nobody reads these files — sharpens the existing evidence rather
than duplicating it.

### Falsification

**Ahrefs owns adoption and readership.** Ours would be a replication if it measured either.
It does not — it measures conformance, which they explicitly excluded. **Open, and narrowly
so:** the moment anyone else runs it, this candidate is worthless, and the llms.txt topic is
cooling. It has a shelf life measured in weeks.

---

## Candidate 3 — Can a reader tell whether a documentation page is current?

### The exact question

**Of N developer documentation sites, what fraction lets a reader determine whether the page
they are reading is current?** Measured as three mechanical signals: a visible last-updated or
published date, a version selector, and whether the default served version matches the
project's latest release.

### Method

Crawl a sample frame of docs sites, detect a date via `<time>` elements and common
last-updated patterns, detect a version selector via generator-specific markup, and compare
the default version string against the latest release from the package registry or the GitHub
releases API.

**Confound 1 — absence of a date is not absence of currency.** A page can be current and
undated. **Design:** the claim is strictly about *what a reader can determine*, not about
whether the docs are accurate. The framing has to hold that line in every sentence or the
study overclaims.

**Confound 2 — the third signal is the only objective one.** Date and selector presence are
detection problems with false negatives; default-version-versus-latest-release is a factual
comparison. **Design:** lead on the third, report the first two as detection-limited with the
detector published.

### The artifact

Crawl snapshots, per-site signal table, detector source, and the release-version comparison
with its data source and date.

### Cost

**API spend: zero.** Hours: roughly 8–10.

### Interesting whichever way it comes out

Weakly. "Most docs sites do show a version selector" is a shrug. This is the candidate whose
result is least likely to be quoted, and I am ranking it accordingly.

### Falsification

Searching for a published census of documentation currency signals returned nothing relevant —
the query collides badly with US Census results, and nothing in the docs-ops literature
surfaced. **Open, but this is the failure mode to watch: it may be open because nobody cares.**
Unlike candidate 1, there is no pre-existing article of faith creating demand for the number.
I would not run it without a reason candidate 1 was blocked.

---

## The four candidates that died, and how

Reported because a closed question is worth as much as an open one.

| Candidate | Killed by |
|---|---|
| **Crawler-access census with citation-vs-training split** | Already run, including the exact differentiator. Inspeccia checked 1,567 robots.txt files; another analysis reports "of the 108 sites that fully block GPTBot, 91 — 84 percent — never mention OAI-SearchBot on any line." That was going to be our headline. Cloudflare also publishes network-wide crawler data we cannot match. |
| **Position-controlled AI Overview citation predictors** | Comprehensively run. Anthony Lee, SSRN, April 2026, *"I Rank on Page 1 — What Gets Me Cited by AI?"*: 250 queries, 10,293 pages, 66 features, position-band matching — the exact design I would have used. Reports AUCs and effect sizes. |
| **What sources do AI assistants cite** | Occupied commercially and editorially. glotier measured 40 buying questions and 292 citations; LLM Pulse, Profound and others sell this as a product. |
| **Can an LLM complete a task from docs alone** | Occupied academically, with better rigour than a blog can bring: NovelAPIBench, TaskBench, and *Benchmarking LLMs in Web API Integration Tasks*, which already include with-docs versus without-docs controls. |

**One finding worth extracting from the falsification**, independent of any experiment. Lee's
position-controlled study reports that **absence of first-person language** is among the top
predictors of AI citation, alongside comparison structure, query-term coverage and subheading
depth. This campaign's voice standard mandates first-person experience. **Those two are in
tension and somebody should look at it** — it is not my call, but it came out of this work and
should not be lost in it.

---

## Ranking, and what I would run first

| | Candidate | Citation ceiling | Completion risk | Hours | Shelf life |
|---|---|---|---|---|---|
| **1** | Code-sample census | **High** | Medium — extractors are fiddly | 12–18 | Years |
| **2** | llms.txt validity census | Moderate | **Very low** — instrument exists | 4–6 | **Weeks** |
| **3** | Currency signals census | Low | Low | 8–10 | Years |

**Run candidate 1 first.** It has the highest ceiling, and the ceiling is what matters given
90 published posts have produced zero human clicks. It is the only one of the three that
converts a belief the whole field already holds into a number, which is the property that made
cats.txt travel. Its method risk is real but I have already spent the spike that found the
three confounds, so the unknown is smaller than it looks.

**Run candidate 2 alongside, not instead.** At four to six hours on an instrument that already
exists and has 40 tests, it is not competing for the same slot, and it de-risks candidate 1 by
proving the publish-a-study pipeline end to end on something small. Its shelf life is the
argument for doing it soon or not at all.

**Do not run candidate 3** unless candidate 1 turns out to be blocked. It is open, and it may
be open for the wrong reason.

### One expectation to set against the measured baseline

The comparable is cats.txt: 85 referring domains, independent author, zero domain authority.
That author had an existing SEO audience this domain does not have, so **a first attempt
should be planned at single digits, not 85.** The number to watch is whether the code-sample
census earns *any* referring domains within ninety days. Under ten and the second route is
closed too, which is the test already recorded in the reference-infrastructure verdict.
