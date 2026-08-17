# Crawl-fallback storage pilot — 2026-08-18

**Decision:** the fallback is feasible with content-addressed gzip snapshots.
Proceed in verified batches and reuse page records; do not repeat successful
reads. Syntax parsing remains locked until all batches and the selected manifest
are frozen.

## Pilot frame

The pilot used the first five fallback projects by frozen PyPI rank: Boto3,
Pygments, NumPy, grpcio-status, and typing-inspection. This was fixed before page
responses were inspected and spans large Sphinx corpora, a small documentation
site, an exact-file root, and a small MkDocs tree.

`crawl_fallback_pages.py` applies robots rules, performs sorted breadth-first
traversal within the frozen host/path scope, caps each project at 50 attempted
eligible URLs, records redirects/status/content type/hashes/canonicals/link
frontiers, and stores each successful response once as deterministic gzip under
its SHA-256.

## Result

```text
projects                              5
unique page records                 130
selected page attachments           127
complete project traversals           3
capped project traversals             2
successful content blobs            126
uncompressed successful bytes 10,365,300
compressed snapshot bytes      1,478,948
```

Boto3 selected 48 pages from 50 attempts and retained 519 queued URLs; NumPy
selected 50/50 with 4,931 queued. Pygments exhausted at 24 selected pages,
grpcio-status at one, and typing-inspection at four. The small totals are
observed crawl populations, not zero-filled 50-page samples.

Three page-level exceptions remain explicit: the Boto3 general index exceeded
the fixed 5 MB response limit, one Boto3 migration page reset the connection,
and one Pygments link returned 404. None was replaced by an extra page after the
50-attempt ceiling.

The first result exposed and then fixed two accounting defects: Boto3 was
incorrectly labelled complete because it had fewer than 50 successful pages
despite a non-empty queue, and exceptions were absent from the request-attempt
counter. The v2 artifact reuses all 130 page records, makes zero new page reads,
and correctly reports Boto3 and NumPy as capped. Its SHA-256 is
`9a9720a3da8760c369a5c4aa202d9a747c6d8a06db0943bb675102314358df5d`.

## Cost gate

The original pilot used 130 page attempts and two robots reads. The v2
accounting rerun reused every page and made two robots reads because parsed rules
were not stored in the page snapshot: **134 free HTTP attempts total, paid calls
0**. Successful HTML compressed to 14.3% of its raw byte size. At the deliberately
conservative 3,450-page maximum, this pilot implies roughly 40 MB compressed;
actual volume should be lower because many project traversals exhaust before 50
and shared page records are reused.

