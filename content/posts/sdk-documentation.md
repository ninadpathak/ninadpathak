---
category: technical-documentation
primary_query: sdk documentation
siblings:
- api-documentation
- quickstart-guide
- code-documentation
date: 2026-11-23
description: "Renaming one keyword argument broke the examples on four docs pages. A small Python SDK shows how to test its quickstart, reference, and error guide."
slug: sdk-documentation
status: published
takeaways:
- "Show how a developer installs the library and makes their first successful call."
- "Run the samples against the service and compare the reference with the SDK signatures."
- "Explain what happens when a call fails and when a retry can safely reuse the same key."
title: "SDK Documentation: What It Covers and How to Test Every Sample"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write the quickstarts and reference pages for your client library. [Ask me about yours](/services/developer-documentation/)."
---

A developer following my Python SDK quickstart would hit a `TypeError` before their request reached the API. I’d renamed one keyword argument, and the old name was still in examples on four pages.

The example below lets you see what breaks when the library and the docs move at different speeds. The same setup lets you check the first call a reader copies and the details they'll look up when it fails.

## Document what the caller sees in this language

A quickstart is the first part of the [technical documentation](/articles/technical-documentation/) a developer needs for one version of a client library.

The API describes requests and responses over HTTP. The SDK describes the methods, return values, and exceptions someone sees in their code.

Here’s the same export operation at both levels.

| | API documentation | SDK documentation |
|---|---|---|
| Unit of reference | An endpoint, such as `POST /exports` | A method, such as `WritingLab.create_export(format, *, idempotency_key=None)` |
| A failed request | A status and a body, `409` with `{"error":"key_conflict"}` | An exception class, `KeyConflictError` |
| A lost response | No row, because the service sent nothing | `APIConnectionError`, raised after the client's retries |

The Python client builds the JSON body. The person using it doesn't need an error entry for malformed JSON in the request.

They do need to know which Python exception an API error becomes and what they can do about it. [The export API reference](/articles/api-documentation/)

## Give the developer a first call they can verify

I use the same order in a [quickstart](/articles/quickstart-guide/) for any tool. Get one result on screen before explaining optional settings.

My example uses `writinglab`, a small Python client for a local export service. It takes a base URL and the fixture needs no API key.

The example zip includes the docs and the checker.

- [Python client](/static/examples/sdk-docs/writinglab.py)
- [Getting started](/static/examples/sdk-docs/docs/getting-started.md), [reference](/static/examples/sdk-docs/docs/reference.md), [errors](/static/examples/sdk-docs/docs/errors.md), and [changelog](/static/examples/sdk-docs/docs/changelog.md)
- [Checker](/static/examples/sdk-docs/check_sdk_docs.py) and [complete example zip](/static/examples/sdk-docs.zip)

Start a quickstart with the install command and the supported runtime. Show where the endpoint and credentials come from.

Then make one call and print what success looks like.

```python
export = client.create_export("csv", idempotency_key="report-a")
print(export)
```

```text
Export(id='exp_1', format='csv', status='accepted', replayed=False)
```

The reference can go deeper. For each method, list the actual parameters and defaults, the return type, and the exceptions the caller can handle.

```markdown
### `WritingLab.create_export(format, *, idempotency_key=None)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `idempotency_key` | `str \| None` | `None` | From 1 to 64 letters, digits or hyphens. When it is `None`, the client generates a key and uses it for every attempt of this call. |

**Returns:** `Export`
```

## Show the failure a signature can't explain

What happens if the server stores an export and the response never arrives? The sample makes the service drop the response to check what the SDK does next.

```python
flaky = WritingLab(
    os.environ["WRITINGLAB_URL"],
    default_headers={"X-Fixture-Drop-Response": "yes"},
)
export = flaky.create_export("json", idempotency_key="report-d")
print(export.id, export.replayed)
print(client.get_state().exports)
```

```text
exp_2 True
2
```

The client retried with the same key and got the saved export back. The total is two because an earlier sample created one export before this one.

The service keeps those keys in one process. With the same key sent to separate instances, each stored its own record.

That's a limit I'd put beside the retry example.

## Make every release run the docs

The checker starts a fresh service for each page, runs the Python blocks in page order, and compares the output with the text underneath. It also checks method signatures, parameter tables, the error mapping, and the version in the changelog against code.

```bash
python3 sdk-docs/check_sdk_docs.py
```

```text
ok   changelog.md samples       2 python blocks ran, 2 outputs matched
ok   errors.md samples          5 python blocks ran, 5 outputs matched
ok   getting-started.md samples 4 python blocks ran, 3 outputs matched
ok   reference.md samples       3 python blocks ran, 3 outputs matched
ok   reference.md entries       3 signatures, 6 parameters, 6 return fields matched the code
ok   errors.md table            7 exceptions, 4 error mappings matched the code
ok   changelog.md version       newest entry 2.0.0, code 2.0.0
PASS
```

When the sample used the old keyword, the reference check showed both sides of the mismatch.

```text
...
FAIL reference.md entries       2 signatures, 5 parameters, 6 return fields matched the code
     reference.md: WritingLab.create_export is documented as (format, *, idempotency_key=None) and the code has (format, *, key=None)
     reference.md: WritingLab.create_export omits parameter key, which the code has
     reference.md: WritingLab.create_export documents parameter idempotency_key, which the code does not have
...
FAIL: 8 problems
```

For a client in another language, I'd run that language's examples against the same test service. In the release notes, point to the API version the SDK uses and show what the caller has to change if a method breaks.

A working call beside the old call is more useful to me than “updated the export client.” [Release notes template](/articles/release-notes-template/)

I'd keep the reference close to the signatures it describes, so a method rename is one change to review. [Where to put code documentation](/articles/code-documentation/)
