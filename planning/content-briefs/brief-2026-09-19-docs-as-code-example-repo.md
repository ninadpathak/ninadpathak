# Brief: Docs-as-Code Example Repository, Explained File by File

**Slot:** 2026-09-19 | Order 52 | **Cluster:** Documentation | **Experience: A**

## Keyword

Near zero. This exists as the artifact companion to row 31's docs-as-code anchor, not as a search
target. Keep it short and concrete; do not pad.

## Reader task

Understand a working repository without copying it blindly.

## Owns

The file-by-file walkthrough.

## Must not repeat

The workflow (row 31), the stack (row 34), the CI link check (row 41), preview deploys (row 42).
This page is the tour, those pages are the arguments.

## Evidence — Experience A, and it is this repository

Walk the real thing: `build.py`, `rule_checker.py`, `tools/check_link_retrofit.py`,
`tools/audit_clusters.py`, `content/posts/`, `static/_redirects`, `tests/`.

Say what each file is for and, more usefully, **what each one exists because of**. Several were
added after something broke, and that history is the honest part of the tour. The link-retrofit
gate exists because 20 of 88 pages had no inbound link. The cluster audit runs after the build
because it reads generated output.

**Do not invent a cleaner example repository.** The real one, with its scars, is the artifact.

## Internal links

Outbound: row 31 `docs-as-code`, row 34, row 41.

**Inbound retrofit source:** row 31's anchor. It is the parent and should delegate the tour.
