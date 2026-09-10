---
category: technical-documentation
date: 2026-07-29
description: Compare concrete technical writing examples, from quickstarts to release notes, with annotated edits and checks for each reader task.
slug: technical-writing-examples
status: published
tags:
- technical-writing
- documentation
- developer-experience
- devtools
title: 'Technical Writing Examples: Formats, Annotated Edits, and Reader Tasks'
updated: 2026-09-10
---

Technical writing examples are usually displayed like dead butterflies: polished snippets, pinned to a category, cut away from the product behavior that made the wording right or wrong. "Your export is ready" looks lovely in that display and sends the reader searching for a file the local fixture never creates.

Change the sentence to "Your export request was accepted" and the reader knows to inspect the stored record. That tiny edit carries my whole argument: an example is useful only when you can see the product fact behind the prose and the decision it changes for the reader.

I use one hypothetical service below so every format has to answer to the same implementation.

## Choose the format from the reader's task

[Download the writing lab](/static/examples/writing-lab.zip) to inspect the service and its filled Markdown pages. It runs locally with Node.js 24.18.0 and has no npm dependencies.

From the extracted `writing-lab` directory, run `node check.mjs`; it must end with `PASS`. If an assertion fails, investigate before using the affected example as evidence.

| Format | Reader's task | Example artifact |
| --- | --- | --- |
| Quickstart | Store a first export request | Startup and request commands |
| Tutorial | Learn why signed bytes matter | A valid event followed by an altered body |
| How-to guide | Recover one lost response | A request repeated with its original identity |
| Reference | Check accepted input | Format and body-size contracts |
| Explanation | Understand a design boundary | Why process restart clears retained requests |
| Troubleshooting | Choose an action from a symptom | Connection and HTTP-error decision table |
| Runbook | Stop a local test deliberately | Preconditions and shutdown verification |
| Release note | Decide whether a feature meets a need | Scope of the fixture's accepted-record endpoint |

The [documentation types guide](/articles/types-of-technical-documentation/) covers the broader classification. These examples stay with one service so differences in wording come from the reader's task, rather than from switching products.

## Write a quickstart that reaches a visible result

A new reader needs an installed runtime and a running service before an API request means anything. The filled [quickstart](/static/examples/writing-lab/docs/getting-started.md) provides both.

| Draft instruction | Revised instruction | Consequence |
| --- | --- | --- |
| "Start the service and send an export." | "Run `node service.mjs`. Copy its printed URL into `LAB_URL` in another terminal." | The reader can address the server actually running |
| "Your export is ready." | "HTTP 202 means the request record was stored. The fixture does not generate a file." | The reader stops at a result the implementation supports |

These are constructed editing examples, not little client war stories invented to make the page sound lived-in. On a fresh server, the first accepted request returns:

```json
{"id":"exp_1","format":"csv","status":"accepted"}
```

If the response differs, compare its status with the reference before declaring success. A quickstart can select `csv` for this path; it need not teach every accepted format before the first request.

## Use a tutorial to teach a consequential variation

A tutorial gives the learner a result they can modify and explain. The webhook fixture's variation is a single trailing space added after signing:

```js
const raw = '{"type":"order.created","id":"evt_local"}';
const signature = sign(raw);
const changed = raw + ' ';
```

The signature accepts `raw` and rejects `changed`. Both parse to the same JSON value, but their bytes differ.

The [technical tutorial method](/articles/how-to-write-a-technical-tutorial-that-actually-teaches/) supplies the complete fixture and checkpoints.

| Draft instruction | Revised instruction | Check |
| --- | --- | --- |
| "Validate the JSON signature." | "Verify the signature over the received bytes before parsing JSON." | The altered-body request returns HTTP 401 |

The tutorial teaches why the order matters. The reference would instead specify the signature encoding.

If altered bytes are accepted, hold the example and repair the verification path. The synthetic protocol has no replay protection and is not a vendor webhook SDK.

## Keep a how-to focused on one known operation

The [request guide](/static/examples/writing-lab/docs/send-a-request.md) assumes the local service is already running. It deliberately loses one response after storing the request, then repeats the request.

| Draft instruction | Revised instruction | Consequence |
| --- | --- | --- |
| "Retry with a fresh request key." | "Repeat the saved key and format only within the same running instance." | The retained record is returned instead of creating another |

The recorded fixture check returns HTTP 200 with `exp_1` for the same key. A new key with the same format returns HTTP 202 with `exp_2`.

If the process restarted, the guide's recovery promise no longer applies; the map was erased. That condition belongs beside the instruction, even though it lengthens the sentence.

## Make reference precise enough to implement against

Reference lets an experienced reader look up a fact without following the quickstart again. The [filled reference](/static/examples/writing-lab/docs/reference.md) gives the accepted values and their failure responses.

| Draft entry | Revised entry | Check |
| --- | --- | --- |
| `format`: export format | `format`: required string, `csv` or `json`; other values return HTTP 400 | The invalid-format request is rejected |
| Request bodies should be small | Body limit: 4096 bytes; oversized requests return HTTP 413 | Valid JSON padded to 4096 bytes is accepted; 4097 bytes are rejected |

The reference needs both permitted values even when the quickstart uses only one. If the boundary test fails, change the implementation or contract before publishing the table.

Passing one boundary case does not establish every possible input combination. Technical writers get into trouble when one green check makes them feel licensed to describe an entire system.

## Explain the boundary behind a rule

An explanation answers why the product behaves this way. It can use a small piece of the actual implementation:

```js
const exportsByKey = new Map();
```

A new fixture server instance creates a new map, so a key from a previous instance has no retained record. The instruction to reuse a key therefore needs a process-lifetime condition that persistent storage would require us to reconsider.

The restart assertion in `check.mjs` observes zero stored exports in a new instance. If retained state appears there, update the explanation and the recovery instruction it supports.

## Start troubleshooting with what the reader observes

An error message gives the reader a starting point. The [troubleshooting page](/static/examples/writing-lab/docs/troubleshooting.md) connects that symptom to a check before proposing a repair.

| Symptom | Diagnostic check | Action |
| --- | --- | --- |
| Connection refused | Compare `LAB_URL` with the server's printed URL | Correct the URL or restart deliberately, knowing state will be cleared |
| HTTP 409 | Compare the format with the original request using that key | Recover with the original format; use a new key only for a separate operation |
| HTTP 400 | Read the response's `error` field | Fix the named invalid input before repeating |

"Restart and try again" would erase information this fixture needs for recovery. If the page cannot distinguish a stopped server from the wrong URL, record that uncertainty before promising to restore the original result.

## Give a runbook a stop condition

A runbook carries a repeatable operational procedure. The procedure applies only to the local fixture.

1. Confirm the terminal is running your `node service.mjs` instance and no test still needs its records. If ownership is unclear, stop the procedure.
2. Record that instance's printed URL, then press Ctrl-C in its terminal.
3. Run `curl --max-time 2 "$LAB_URL/health"` using the recorded URL. Connection refusal confirms the listener stopped. If a response arrives, identify the listener before taking another action.

State loss is intentional in this procedure. A production runbook would need the actual service's drain and recovery contracts before the same steps could be recommended.

## Write a release note that defines available behavior

A release note should let a reader determine whether a feature serves their task. For the initial fixture, the difference is between accepting a record and generating a file.

> **Initial fixture release:** `POST /exports` accepts a `csv` or `json` request and returns a stored identifier. Records last for the current server instance. File generation is not implemented.

The note describes the downloadable fixture. Replacing "accepts a request" with "exports your data" would introduce a capability the implementation lacks.

If file generation is later added, test that behavior before extending the note. The [release notes guide](/articles/writing-release-notes-that-developers-trust/) covers changes that require migration decisions.

## Annotate a portfolio sample with ownership and evidence

I would rather assess a small sample with its decisions visible than infer someone's contribution from a company logo. A sample annotation can identify the reader and state what was tested without claiming an outcome that was never measured.

| Annotation | Example for this fixture |
| --- | --- |
| Intended reader | A writer documenting a developer product |
| Artifact | Filled quickstart with a separate reference |
| Material edit | Defined "accepted" as a stored record |
| Evidence | Runnable fixture and request assertions |
| Provenance | Synthetic example with [recorded local checks](/static/examples/writing-lab/validation.txt); no client incident |
| Unmeasured | Human completion time and usability improvement |

For attributable published work, use the [portfolio](/portfolio/). To build a sample with these page responsibilities, start with the [filled documentation template](/articles/technical-documentation-template/).

A reviewer should be able to point from each annotation to the instruction or check that supports it; if they cannot, narrow the annotation before using it as proof.
