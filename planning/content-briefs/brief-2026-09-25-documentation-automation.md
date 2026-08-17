# Brief: Documentation Automation That Is Safe to Trust

**Slot:** 2026-09-25 | Order 58 | **Cluster:** Documentation | **Experience: A**

## Keyword

| Field | Value |
|---|---|
| Primary | `documentation automation` |
| Volume | 170 (Semrush 2026-08-17) |

The highest-volume target left in the docs-operations set.

## Reader task

Automate the mechanical parts of documentation without letting automation invent content.

## Owns

The trust boundary: what may be generated, what must be checked, and what must never be automated.

## Must not repeat

Row 54 owns OpenAPI generation. Row 51 owns AI-written drafts. Row 41 owns link checking. This page
owns the boundary rule that governs all three.

## Evidence — Experience A, and it is the strongest available

**This site is written by an autonomous pipeline and the failures are documented.** That is a
better source than any tutorial, and it is honest because the failures are real:

- a publish prompt that required an evidence artifact every run, which produced checkers validating
  fixtures the same run had authored
- a cleanup gate that claimed to remove workspaces and silently left six behind
- a link requirement satisfied outbound-only, leaving 20 of 88 pages with no inbound link
- gates that were prose assertions until they were replaced by scripts that exit non-zero

The governing rule those failures produce: automate what can be verified mechanically, and never
automate a judgement whose output cannot be checked by something other than the thing that produced
it.

**Do not describe the pipeline as flawless, and do not name it as a product.**

## Internal links

Outbound: row 31, row 41, row 55, all live.

**Inbound retrofit source:** row 55's workflow piece, published three days earlier, same cluster.
