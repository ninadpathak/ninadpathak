# Brief: AI Code Documentation: What to Automate and What to Verify

**Slot:** 2026-09-18 | Order 51 | **Cluster:** Documentation | **Experience: B**

## Keyword

| Field | Value |
|---|---|
| Primary | `ai code documentation` |
| Volume / Difficulty | 200 / KD 7 (Ahrefs cached, parent `code documentation ai`) |
| AI Overview | yes |

## Reader task

Use AI for code documentation without shipping invented behaviour.

## Owns

The automate-versus-verify boundary for AI-generated code documentation.

## Must not repeat

Row 20 owns the comment/reference/guide decision. Row 29 owns the worked example. Row 30 owns
tooling. This page owns only what changes when a model writes the first draft.

## Evidence — Experience B

Run a model over a real module from this repository and record what it got wrong. The interesting
class is confident-and-wrong: a described parameter that does not exist, an inferred behaviour the
code does not have.

That is a genuine information test. What could surprise you is which kind of function it fails on.

**Do not report an error rate without showing the runs.**

## Internal links

Outbound:
- row 20 `code-documentation`, row 29's example, both live
- `/articles/technical-writing-for-ai-products-the-new-rules/` only if the sentence is genuinely
  about AI-product documentation. It is cluster 2, so this is cross-cluster and needs the
  connection to be its subject.

**Inbound retrofit source:** row 20's `code-documentation`, same cluster, and the natural parent.
