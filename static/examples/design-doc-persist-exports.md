# Keep export records when the writing-lab service restarts

<!-- Filled example of design-doc-template.md for a hypothetical change to the writing-lab fixture. -->

Status: Accepted
Author: Service owner (example)
Reviewers: Docs lead, on-call engineer (example)
Date: 2026-10-20

## Problem

`POST /exports` stores records in a `Map` inside the process, so a restart loses every record and every idempotency key. A client that retries with the key it used before the restart gets a new `exp_1` instead of its original record, which breaks the retry promise in the reference.

## Goals

- A record created before a restart is returned with status `200` when the same key and body are sent after it.
- The reference entry for `POST /exports` stays accurate with no edits to its response table.

## Non-goals

- Generating export files. The service still only records the request.
- Running more than one service instance against the same records.

## Proposal

Append each new record to `exports.jsonl` next to the service, one JSON object per line with its key, and load the file into the `Map` at startup. Write the line before sending `202`, so a record the client was told about is always on disk.

## Alternatives considered

### Do nothing

What happens: records and keys disappear on each restart, and retries after a restart create duplicates.
Rejected because: the reference promises that a retry with the same key is safe, and a restart silently breaks that.

### SQLite database

What happens: records go into a table with a unique index on the key.
Rejected because: it adds a native dependency to a fixture that has none, for a single table that a line-per-record file handles.

## Risks and rollout

- Risk: a crash between writing the line and sending `202`. Mitigation: the client retries with the same key and gets `200` with the stored record.
- Rollout: ship behind the existing tests, then add a restart case to `check.mjs`.
- Rollback: delete the loader; `exports.jsonl` can stay on disk because nothing reads it.

## Open questions

- None

## Decision

Accepted on 2026-10-21 by the service owner and the docs lead, with the restart case added to `check.mjs` before release.
