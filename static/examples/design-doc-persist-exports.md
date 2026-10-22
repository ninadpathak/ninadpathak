# Keep export records when the writing-lab service restarts

<!-- Filled example of design-doc-template.md for a hypothetical change to the writing-lab fixture. -->

Status: Accepted
Author: Service owner (example)
Reviewers: Docs lead, on-call engineer (example)
Date: 2026-10-20

## Problem

The current contract limits safe retries to one running instance: `POST /exports` keeps records and idempotency keys in a `Map`, so a restart erases them. A client whose retry lands after a restart gets a new `exp_1` instead of its original record, and the reference has to warn about that boundary.

## Goals

- A record created before a restart is returned with status `200` when the same key and body are sent after it.
- The retention paragraph in `docs/reference.md` says records survive a restart, and the response table needs no other change.

## Non-goals

- Generating export files. The service still only records the request.
- Running more than one service instance against the same records.

## Proposal

Append each new record to `exports.jsonl` next to the service, one JSON object per line with its key, and load the file into the `Map` at startup. Write the line before sending `202`, so a record the client was told about is on disk, and revise the retention paragraph in `docs/reference.md` to match.

## Alternatives considered

### Do nothing

What happens: records and keys disappear on each restart, and a retry that lands after a restart creates a duplicate.
Rejected because: clients can't retry safely across a restart, so every integration has to handle a boundary the service could remove.

### SQLite database

What happens: records go into a table with a unique index on the key, through `node:sqlite`, which ships with Node.js 24 as a release candidate.
Rejected because: the fixture exists to be read, and a line-per-record file can be inspected with `cat` while someone follows the docs. SQLite's transactions add little for one append per request.

## Risks and rollout

- Risk: a crash between writing the line and sending `202`. Mitigation: the client retries with the same key and gets `200` with the stored record.
- Rollout: ship behind the existing tests, then add a restart case to `check.mjs`.
- Rollback: delete the loader; `exports.jsonl` can stay on disk because nothing reads it.

## Open questions

- None

## Decision

Decided by: Service owner and docs lead (example)
Decided on: 2026-10-21
Outcome: Accepted, with a restart case added to `check.mjs` before release.
