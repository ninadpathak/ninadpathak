# Documentation-root inspection — 2026-08-17

**Decision:** the mechanically resolved population contracts from 80 roots to
76 crawl-eligible roots. Do not replace the four exclusions with searched or
hand-picked URLs. Page discovery may begin only with the 76 preserved roots and
the overlap rule below.

## Reproducible batch

`inspect_docs_roots.py` read the frozen v3 resolution artifact and made one
bounded HTML request per selected root, retrying only transient failures. It
records every redirect, final URL, status, content type, byte count, response
SHA-256, cache validators, canonical URL, and detected generator.

```text
selected roots                 80
successful root responses      78
hard root errors                2
supported generator roots      76
unsupported successful roots    2
HTTP request attempts          82
redirect hops                  45
```

Generator distribution among successful responses: 61 Sphinx, 12 MkDocs, two
Starlight, one Docusaurus, and two unknown. The output artifact SHA-256 is
`db225a4c9a4076994a0189b10a820842f60890a57ab881b4691ccf3103ad6639`.

## Exclusions, not backfill invitations

| Rank | Project | Outcome | Reason |
|---:|---|---|---|
| 15 | PyYAML | unsupported | The declared wiki returns HTML, but no supported generator. |
| 72 | aiosignal | dead root | `docs.aiosignal.org` failed DNS resolution on all three bounded attempts. |
| 82 | annotated-doc | unsupported | Its declared Documentation URL is a GitHub repository page, not a supported docs site. |
| 89 | pydantic-settings | stale root | The declared URL redirects to `pydantic.dev` and returns 404. |

These are observable metadata/deployment failures in the frozen frame. Searching
for alternatives after seeing the failures would make inclusion depend on
researcher intervention and undo the resolver's selection control.

One supported root, `python-multipart`, redirects from HTTPS to HTTP. The full
report preserves that transport downgrade. It is not silently rewritten or
treated as a generator failure; robots and page acquisition still apply.

## Shared-corpus rule

Three final hosts are attached to two sampled projects each:

- `pyasn1.readthedocs.io`: `pyasn1` and `pyasn1-modules` resolve to the exact
  same canonical root.
- `grpc.github.io`: the `grpcio-status` root is a page inside the broader
  `grpcio` Python documentation tree.
- `pydantic.dev`: the `pydantic-core` root is a nested section of the broader
  Pydantic documentation tree.

The page sampler must therefore use **global canonical-page deduplication**:

1. build each project's eligible population and deterministic 50-page sample
   from its own resolved root;
2. take the union of those selected canonical URLs and fetch each canonical
   page once;
3. attach the fetched page and its blocks to every project sample that selected
   it;
4. count each canonical page/block once for the block-weighted estimate;
5. retain project attachment for the preregistered package-weighted estimate,
   and report a unique-documentation-corpus sensitivity result so the three
   related package pairs cannot be mistaken for independent sites.

This preserves the fixed top-100 project frame while preventing identical pages
from inflating the pooled block numerator or denominator.

## Remaining gate

The crawler is still locked. The next stage is robots/sitemap discovery for only
the 76 eligible roots, followed by a frozen URL-population artifact. Parsing
results must not influence which pages enter the sample.
