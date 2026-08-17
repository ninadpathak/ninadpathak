# Brief: Documentation Workflow From Issue to Published Page

**Slot:** 2026-09-22 | Order 55 | **Cluster:** Documentation | **Experience: A**

## Keyword

`documentation workflow` measures 70/mo. Modest. Completes the docs-operations set.

## Reader task

Define who does what between a reported gap and a published page.

## Owns

The handoffs: intake, triage, drafting, review, publish.

## Must not repeat

The technical pipeline (row 31). The tooling (row 34). Ownership (row 44). Maintenance cadence
(row 33). This page owns the sequence of hands, not the machinery.

## Evidence — Experience A

This site runs an unusually literal version of this workflow: a queue with an explicit state
machine, a lease, and a guard script that refuses invalid transitions. Planned to In Progress to
Done to Published, with Skipped as a terminal state carrying a written reason.

The honest and useful part is why the states exist. Skipped carries a reason because a row removed
without one is indistinguishable from a row forgotten, and the guard refuses hand-edits because
hand-editing corrupted the lease and stalled a morning publish.

That is a real workflow with real failure modes, which beats a generic issue-to-page diagram.

## Internal links

Outbound: row 31, row 33, both live.

**Inbound retrofit source:** row 33's maintenance piece, same cluster.
