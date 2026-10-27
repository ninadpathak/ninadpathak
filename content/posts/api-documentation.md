---
category: technical-documentation
date: 2026-10-22
description: What API documentation includes, page by page, and a complete reference entry for one endpoint that a script checks against the running service.
slug: api-documentation
status: published
takeaways:
- API documentation is a set of pages with one reader job each, from the homepage and quickstart to reference, errors and version changes.
- A reference entry documents each response the endpoint returns, with the fix for each error.
- Check the reference against the running service, so a changed status code fails before a developer hits it.
title: 'API Documentation: What to Include, With a Tested Reference Example'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for APIs, checking each documented request and response against the service it describes.'
video: api-documentation
---

The [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) describes an HTTP API's paths, operations, parameters, request bodies and responses, so a generator can turn one OpenAPI file into a reference page for each endpoint. Those pages still leave two jobs to a writer: choosing the request a new developer should send first, and explaining what to do after a 409.

I treat API documentation as a set of pages with one job each. For the worked example I use `POST /exports` from the local writing-lab service, with a checker for its documented request cases.

## What API documentation includes

API documentation is the set of pages that takes a developer from choosing your API to sending requests and recovering when one fails. Each page owns one reader moment:

| Reader moment | Page that owns it | Done when |
|---|---|---|
| Where do I begin? | Documentation homepage | The reader can pick a first task and its starting page |
| Does this work for me? | Quickstart | One safe request returns a result the reader recognizes |
| How do I get and send a credential? | Authentication guide | The credential format, scope and failure response are explicit |
| What exactly does this endpoint accept and return? | API reference | Parameters, body, every response and the limits are written down |
| My request failed | Error and troubleshooting guide | Each error names its cause, what to inspect and the fix |
| My system receives an event | Webhooks guide | Signature checks, duplicates and failed deliveries are covered |
| The API changed | Version and change guide | Affected versions, required action and the deadline are named |

The [API documentation page outline](/static/templates/api-documentation-page-outline.md) has a section for each of these pages, with the facts each one needs before it can be published.

## A complete reference entry for one endpoint

The endpoint is `POST /exports` from the writing-lab service that ships with the [technical documentation template](/articles/documentation-template/). It is a small Node.js server you can run locally, and its reference entry reads like this:

### POST /exports

Creates an export record in the server's memory. The server generates no file, and repeating a request with the same key and body returns the stored record without creating another.

Records and keys live only as long as this server instance runs. A restart clears them and separate instances share nothing, so a retry with the same key is safe only against the same running instance.

**Headers**

| Header | Required | Value |
|---|---|---|
| `Content-Type` | Recommended | `application/json`. The service parses the body as JSON whatever this header says. |
| `Idempotency-Key` | Yes | Up to 64 letters, digits or hyphens, and not empty. Reuse the key to retry the same request safely. |

**Body**

| Field | Type | Required | Value |
|---|---|---|---|
| `format` | string | Yes | `csv` or `json`. No other fields are accepted, and the body must be 4,096 bytes or smaller. |

**Example request**

```bash
curl -i "$LAB_URL/exports" \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: report-a' \
  --data '{"format":"csv"}'
```

**Responses**

| Status | Body | When | What to do |
|---|---|---|---|
| `202` | `{"id":"exp_1","format":"csv","status":"accepted"}` | A new key created a record | Store the `id` |
| `200` | The same record as the `202` | The key and body match an earlier request on this instance | No action. The retry was safe and created no duplicate |
| `409` | `{"error":"key_conflict"}` | The key was used before with a different body | Send a new key for a different request |
| `400` | `{"error":"invalid_key"}` | `Idempotency-Key` is missing or has other characters | Send a key that matches the rule above |
| `400` | `{"error":"invalid_format"}` | `format` is not `csv` or `json`, or the body has another field | Send only `format` with a supported value |
| `400` | `{"error":"invalid_json"}` | The body is not valid JSON | Fix the JSON; this check runs before the key check |
| `413` | `{"error":"body_too_large"}` | The body is over 4,096 bytes | Send the documented body only |

The service parses the body before it validates the key, so a request with broken JSON and no key gets `invalid_json`.

## Check the reference against the running service

The [check script](/static/examples/api-reference-check.mjs) holds nine documented cases: the seven response rows, a second `invalid_format` case with an extra field, and a request with no `Content-Type` header. It starts its own copy of the service on a random local port, sends the rows in order, compares each response with the page, and stops the server:

```bash
node api-reference-check.mjs
```

```text
ok   202 new key
ok   200 same key, same body
ok   409 same key, different body
ok   400 missing key
ok   400 unsupported format
ok   400 extra field
ok   400 malformed JSON
ok   413 body over 4 KB
ok   202 no Content-Type header
PASS: 9 of 9 documented responses match
```

Change the service to return `201` for a new key, pass that copy's path, and both `202` rows fail:

```text
DIFF 202 new key   got 201 {"id":"exp_1","format":"csv","status":"accepted"}
...
DIFF 202 no Content-Type header   got 201 {"id":"exp_2","format":"json","status":"accepted"}
FAIL: 2 of 9 documented responses differ
```

A FAIL exits with status 1, so the check can run in CI next to the service's own tests. When a row shows DIFF, decide whether the service or the page is wrong, fix that one, and rerun until it prints PASS.

## Where reference ends and guides begin

The quickstart owns first success, so it links to this entry once the reader has a request to inspect. The reference owns exact behavior, the error guide owns recovery across endpoints, and a status change like `202` to `201` belongs in the [changelog](/articles/writing-changelogs/) as well as the reference.

A generated reference keeps up with endpoints as they change. I write the recovery guidance explicitly, whether it lives in the OpenAPI response description or on the page, and I check the generated reference against the service.

## FAQ

### What is API documentation?

API documentation is the set of pages that helps a developer choose an API, send a first request, look up exact behavior and recover from errors. It includes a quickstart, an authentication guide, the API reference, an error guide and a version or change guide.

### What is the difference between API reference and API documentation?

The API reference is one part of API documentation: the exact contract for each endpoint, with its parameters, body, responses and limits. The rest of the documentation covers tasks, such as the first request, authentication and recovering from errors.

### How should I document API errors?

Give each error its status, response body, the state that causes it and the action that fixes it. Put that in the endpoint's reference entry, and link to an error guide when the same error can come from several endpoints.

### Is an OpenAPI file enough for API documentation?

An OpenAPI file can generate a reference for each endpoint, and that reference is accurate only once you check it against the running service. You still need a quickstart that picks the first request, an authentication guide, and a recovery step for each error.
