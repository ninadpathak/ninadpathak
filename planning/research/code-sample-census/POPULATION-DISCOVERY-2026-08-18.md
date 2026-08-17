# Robots and sitemap population discovery — 2026-08-18

**Decision:** sitemap presence is not accepted as page-population coverage. The
landing-page challenge falsified 52 of 58 apparent sitemap populations. The
next acquisition split is six sitemap samples, 69 breadth-first crawl fallbacks,
and one robots-denied exclusion.

## First pass

`discover_page_populations.py` fetched each final origin's robots resource once,
then followed declared and conventional sitemap resources within fixed limits.
It parsed no code samples.

```text
eligible roots                 76
unique origins                 73
robots reads                   73
sitemap reads                 276
top-level request attempts    349
redirect hops                   2
initial sitemap populations    58
initial crawl fallbacks        17
robots-denied                   1
```

The raw population artifact SHA-256 is
`fe12e1a2370e1ecfa0f8252777d856e3c91944774b7cb4f9224b70e087a7286a`.
Jmespath is the single robots-denied project and remains excluded.

AWS exposes a 10,692-child sitemap index. The preregistered safety cap stopped
after 200 reachable sitemap documents, leaving 10,494 index-referenced documents
unfetched across the two seed routes. Boto3 had no eligible URL in the bounded
result and is therefore routed to the crawl fallback; a partial AWS sitemap is
not treated as its population.

## Coverage falsification

The first pass classified 48 projects as one-page sitemap populations. Current
Read the Docs and several Sphinx-family sitemaps commonly list a version landing
URL, not the documentation pages beneath it. Treating those files as exhaustive
would have reduced Requests, pytest, Pillow, pip, Rich, and many others to one
page each.

`validate_sitemap_coverage.py` therefore fetched the landing page for all 58
apparent sitemap populations and compared its normalized, in-scope links with
the sitemap population. A single eligible landing link absent from the sitemap
falsifies page-level coverage; the missing link is evidence, not an augmentation
chosen after looking at results.

```text
sitemap roots challenged       58
coverage failed                52
coverage not falsified          6
landing-page requests          58
```

The six populations not falsified at this gate are typing-extensions (1 URL),
pydantic-core (8), Uvicorn (14), HTTPX (23), Starlette (24), and Textual (301).
"Not falsified" is deliberately narrower than "proven complete". Their page
samples still use the frozen sitemap populations and the same response/canonical
checks as crawl-fallback pages.

The v2 challenge artifact corrects one reporting bug without new network work:
an unfetched conventional sitemap seed after robots denial is not a truncated
index. Only children explicitly named by a fetched sitemap index count as
truncation. It reuses the 58-response snapshot and has SHA-256
`9c3591d2367229a9a6a246914e322e7c7fd6a6799669245029696d5a33b54258`.

## Frozen acquisition split

- **6 sitemap projects:** hash-sort the preserved population and take up to 50.
- **69 crawl-fallback projects:** breadth-first traversal from the frozen root,
  sorted links at every page, maximum 50 eligible pages, with robots applied.
- **1 robots-denied project:** no page request and no replacement.

Global canonical-page deduplication still applies after the independent project
samples are selected. Syntax parsing remains locked until the selected page
manifest and response receipts are frozen.
