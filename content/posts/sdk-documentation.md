---
category: technical-documentation
primary_query: sdk documentation
siblings:
- api-documentation
- quickstart-guide
- code-documentation
date: 2026-11-23
description: "SDK documentation covers install, client setup, each method, errors and upgrades. See a Python SDK whose docs a script runs against the running service."
slug: sdk-documentation
status: published
takeaways:
- SDK documentation describes one library in one language, so its reference lists method signatures and exception classes where API documentation lists endpoints and status codes.
- A checker ran the 14 Python samples in four pages of SDK docs against the running service and compared each documented signature with the imported SDK.
- A generator can copy a signature into a reference page, and a writer still has to say when a retry is safe.
title: "SDK Documentation: What It Covers and How to Test Every Sample"
work_note: "Does your client library ship faster than the pages that explain it? I'm Ninad Pathak, a freelance technical writer, and I write quickstarts and reference pages after running each sample against the product. [Ask me about yours](/services/developer-documentation/)."
---

SDK documentation is the set of pages that takes a developer from installing your client library to calling it from their own code and handling the exceptions it raises. API documentation describes HTTP requests and responses, while SDK documentation describes one library in one language, down to its method signatures and exception classes.

I wrote a small Python SDK for a local export service and documented it. A script then runs every Python sample in those docs against the running service, and when I renamed one parameter in the SDK without touching the docs, it reported 8 problems.

## What is SDK documentation?

SDK documentation is the written material that ships with a software development kit, and it explains how to install the kit and call what's in it. For a web API, the kit is a client library in each supported language, such as `stripe` for Python or `@aws-sdk/client-dynamodb` for JavaScript.

SDK docs are a part of [technical documentation](/articles/technical-documentation/) that describes one package version, so any release can make a sample on the page wrong.

## SDK documentation vs API documentation

API documentation describes the HTTP contract, and SDK documentation describes what one library does with that contract. The rows below use the export service from my [API documentation guide](/articles/api-documentation/) and the Python client I wrote for it:

| | API documentation | SDK documentation |
|---|---|---|
| Unit of reference | An endpoint, such as `POST /exports` | A method, such as `WritingLab.create_export(format, *, idempotency_key=None)` |
| A failed request | A status and a body, `409` with `{"error":"key_conflict"}` | An exception class, `KeyConflictError` |
| A lost response | No row, because the service sent nothing | `APIConnectionError`, raised after the client's retries |

The API documentation guide lists seven responses for `POST /exports`. The Python client returns an `Export` object for two of them and raises its own exception class for four.

The client can't cause the seventh, `invalid_json`, because it builds the JSON body itself. So I'd write an SDK's error page from the SDK's code, since the API's error table has a row the caller can't hit and no row for a lost response.

## What SDK documentation should include

SDK documentation should include these eight parts, in the order a developer meets them:

1. **Install:** the command and the supported language versions.
2. **Client setup:** the line that creates a client, and where the credential comes from.
3. **First call:** one method call with its output.
4. **Method reference:** each parameter's type and default, plus the return type.
5. **Errors:** each exception class and what to do about it.
6. **Retries and timeouts:** what the client retries, and how long a call waits.
7. **Pagination:** the helper that walks a list across pages.
8. **Changelog:** each breaking change with a migration note.

<!-- evidence-three: the table's SDK columns -->

The parts up to the first call make a quickstart, which my [quick start guide template](/articles/quickstart-guide/) covers. To see the parts in practice, I read the current docs of three SDKs on November 23, 2026:

| Part | stripe-python 17.1.0 | AWS SDK for JavaScript 3.1175.0 | openai-python 3.58.0 |
|---|---|---|---|
| Install and versions | [README](https://github.com/stripe/stripe-python/blob/2bbff430470360a501c2054221036e8dee5977d7/README.md): `pip install --upgrade stripe`, Python 3.9+; a [versioning page](https://docs.stripe.com/sdks/versioning?lang=python) gives the month support ends for each Python version | [README](https://github.com/aws/aws-sdk-js-v3/blob/b9c18c5fe1c5bbc104d01f2790aa24f51fee8f5d/README.md): one npm package per service; 3.968.0 or later needs Node.js 20 | [README](https://github.com/openai/openai-python/blob/7596fb8b75bd5b95dbc618d148fb8b0f96ca2aea/README.md): `pip install openai`, Python 3.10+; a [policy file](https://github.com/openai/openai-python/blob/7596fb8b75bd5b95dbc618d148fb8b0f96ca2aea/PYTHON_VERSION_POLICY.md) on raising the minimum |
| Client setup | `StripeClient("sk_test_...")`, with per-request `options` for another key or API version | `new DynamoDBClient({ region: "us-west-2" })`; a [credentials page](https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/setting-credentials-node.html) gives the provider chain's search order | `OpenAI()` reads `OPENAI_API_KEY` unless you pass `api_key` |
| Method reference | A [page per method](https://docs.stripe.com/api/customers/create?lang=python) with a Python request and parameters in API types such as `string` | Generated: [ListTablesCommand.ts](https://github.com/aws/aws-sdk-js-v3/blob/b9c18c5fe1c5bbc104d01f2790aa24f51fee8f5d/clients/client-dynamodb/src/commands/ListTablesCommand.ts) opens with `// smithy-typescript generated code` and lists its `@throws` errors | [api.md](https://github.com/openai/openai-python/blob/7596fb8b75bd5b95dbc618d148fb8b0f96ca2aea/api.md): 377 method lines, each with the call and its return type |
| Error classes | [Nine exception classes](https://docs.stripe.com/error-handling?lang=python), each with a section on how to respond | [ERROR_HANDLING.md](https://github.com/aws/aws-sdk-js-v3/blob/b9c18c5fe1c5bbc104d01f2790aa24f51fee8f5d/supplemental-docs/ERROR_HANDLING.md): errors a command lists, and unlisted ones raised as the service's base exception | A README table of eight rows, from `BadRequestError` for `400` to `APIConnectionError` |
| Retries and timeouts | `max_network_retries=2` turns retries on, and the client adds an idempotency key to a request without one | [CLIENTS.md](https://github.com/aws/aws-sdk-js-v3/blob/b9c18c5fe1c5bbc104d01f2790aa24f51fee8f5d/supplemental-docs/CLIENTS.md): `maxAttempts` and `retryStrategy`, plus `requestTimeout` in milliseconds | Two retries by default; a request times out after 10 minutes unless you set `timeout` |
| Pagination | `auto_paging_iter()`, on the [auto-pagination page](https://docs.stripe.com/api/pagination/auto?lang=python) | `paginateListTables` and similar async iterators | Looping over a list call fetches further pages; `get_next_page()` for manual paging |
| Changelog and migration | [CHANGELOG.md](https://github.com/stripe/stripe-python/blob/2bbff430470360a501c2054221036e8dee5977d7/CHANGELOG.md): the 17.1.0 entry of November 18, 2026 names its pinned API version; a [wiki guide for v15](https://github.com/stripe/stripe-python/wiki/Migration-guide-for-v15) with before and after code | [CHANGELOG.md](https://github.com/aws/aws-sdk-js-v3/blob/b9c18c5fe1c5bbc104d01f2790aa24f51fee8f5d/CHANGELOG.md): top entry 3.1175.0, November 21, 2026; [UPGRADING.md](https://github.com/aws/aws-sdk-js-v3/blob/b9c18c5fe1c5bbc104d01f2790aa24f51fee8f5d/UPGRADING.md) for 2.x to 3.x | [CHANGELOG.md](https://github.com/openai/openai-python/blob/7596fb8b75bd5b95dbc618d148fb8b0f96ca2aea/CHANGELOG.md): 3.58.0, November 23, 2026; [httpx2.md](https://github.com/openai/openai-python/blob/7596fb8b75bd5b95dbc618d148fb8b0f96ca2aea/httpx2.md) for the HTTP client change |

Each cell records what the linked page showed on that date. Stripe's error handling page also has scenarios you can run, such as a declined card, each followed by the log line it should print.

## An SDK documentation example you can run

The example is `writinglab`, a one-file Python client for the writing-lab export service, documented in four Markdown pages:

- [writinglab.py](/static/examples/sdk-docs/writinglab.py): a client class with two methods and seven exception classes.
- The docs: [getting-started.md](/static/examples/sdk-docs/docs/getting-started.md), [reference.md](/static/examples/sdk-docs/docs/reference.md), [errors.md](/static/examples/sdk-docs/docs/errors.md) and [changelog.md](/static/examples/sdk-docs/docs/changelog.md).
- [check_sdk_docs.py](/static/examples/sdk-docs/check_sdk_docs.py): the checker, with everything in [sdk-docs.zip](/static/examples/sdk-docs.zip).

Everything below ran on November 23, 2026 with Python 3.12.3 and Node.js 26.13.1, against the service as shipped in this site's repository. The service has no authentication, so the client takes a base URL and no API key.

The getting-started page builds up to a first call and its output:

```python
export = client.create_export("csv", idempotency_key="report-a")
print(export)
```

```text
Export(id='exp_1', format='csv', status='accepted', replayed=False)
```

Each method gets a reference entry in one fixed shape, so a script can read it. Here is the skeleton of one entry, with one parameter row left in:

```markdown
### `WritingLab.create_export(format, *, idempotency_key=None)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `idempotency_key` | `str \| None` | `None` | From 1 to 64 letters, digits or hyphens. When it is `None`, the client generates a key and uses it for every attempt of this call. |

**Returns:** `Export`
```

The errors page carries what a signature can't. A sample there shows a lost response, where a request header makes the service store the record and close the connection without answering:

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

The client got no response to its first attempt and retried with the same key, so the service returned the stored record and `replayed` is `True`. The count is 2 because an earlier sample on that page stored the first record.

The errors page also says where that retry stops being safe. The service keeps its keys in the memory of one process, and when I sent one key to two running instances, each stored its own record.

## Check SDK documentation against the SDK and the service

The checker imports the SDK and makes 12 checks, starting a fresh copy of the service for each docs page. Mintlify's [SDK documentation guide](https://www.mintlify.com/library/sdk-documentation-guide) of October 16, 2026 recommends running code samples in CI, and this script is that job for one small SDK:

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

It makes these checks and no others:

1. **Samples:** each `python` block runs without raising, in page order, in one namespace per page.
2. **Samples:** its printed output equals the `text` block right after it, where there is one.
3. **reference.md:** each method heading names a real method, and its signature equals the real one.
4. **reference.md:** the parameter table has a row per real parameter and no other, with the real type and default.
5. **reference.md:** the Returns line equals the return annotation.
6. **reference.md:** each listed exception is a class in the module or a Python built-in.
7. **reference.md:** the client class and each of its public methods has a heading.
8. **reference.md:** each return type's field table equals its dataclass fields.
9. **errors.md:** the exception table lists each exception class in the module and no other.
10. **errors.md:** each Parent cell equals the real base class.
11. **errors.md:** each status and error-code row equals an entry in the SDK's `ERROR_CLASSES` map, and each entry has a row.
12. **changelog.md:** the newest version heading equals `writinglab.__version__`.

For the first break I renamed `idempotency_key` to `key` in a copy of `writinglab.py` and passed the copy with `--sdk`. All four pages failed their samples with a `TypeError`, and the reference entry failed too (other lines cut):

```text
...
FAIL reference.md entries       2 signatures, 5 parameters, 6 return fields matched the code
     reference.md: WritingLab.create_export is documented as (format, *, idempotency_key=None) and the code has (format, *, key=None)
     reference.md: WritingLab.create_export omits parameter key, which the code has
     reference.md: WritingLab.create_export documents parameter idempotency_key, which the code does not have
...
FAIL: 8 problems
```

For the second break I changed one line of the SDK's error map, so that a `409` with `key_conflict` raises `InvalidKeyError`. A sample and the errors table both caught it (`ok` lines cut):

```text
...
FAIL errors.md samples          0 python blocks ran, 0 outputs matched
     errors.md line 27: the block raised InvalidKeyError: HTTP 409: key_conflict (4 later blocks on this page not run)
...
FAIL errors.md table            7 exceptions, 3 error mappings matched the code
     errors.md: 409 key_conflict is documented as KeyConflictError and the code maps it to InvalidKeyError
...
FAIL: 2 problems
```

A failing run exits with status 1. The script reads headings and tables in the shape these four pages use, so other docs need their own patterns.

It can't check prose, and Python can't tell it which method raises which exception. A claim that a retry is safe is checked only where a sample acts it out.

## What a generated SDK reference can't write

A generator can copy a method's signature and types into a reference page, and it can't write when to call the method or whether a retry is safe. Python's `inspect.signature` returns this for `create_export`:

```text
(self, format: 'str', *, idempotency_key: 'str | None' = None) -> 'Export'
```

Nothing in that line says the service forgets the key when it restarts. The openai-python library is generated from an OpenAPI specification, and its README carries a retry rule in prose, saying a stream isn't retried "because replaying a request could duplicate output already delivered to your application."

The AWS SDK for JavaScript keeps its handwritten guides in a [supplemental-docs folder](https://github.com/aws/aws-sdk-js-v3/blob/b9c18c5fe1c5bbc104d01f2790aa24f51fee8f5d/supplemental-docs/README.md), whose README says they supplement the generated documentation. My guide to [code documentation](/articles/code-documentation/) covers the docstrings a Python generator reads.

## Keeping samples in several languages in step

Run each language's samples with that language's own runner, against one shared test service. The [Markdown version of Stripe's auto-pagination page](https://docs.stripe.com/api/pagination/auto.md?lang=python) shows why one runner can't cover them, since the helper is `auto_paging_iter()` in Python and `autoPagingIterable()` in Java, with five more languages on the same page.

My checker runs Python blocks only, and for a JavaScript client I'd add a step that runs the `javascript` blocks with Node.js against the same service.

## Which SDK version matches which API version

State the matching API version in the changelog entry of each SDK release. The stripe-python entry for 17.1.0 opens with "This release changes the pinned API version to `2026-11-18.endive`", and since the writing-lab service has no version number, my example's 2.0.0 entry names the service file and the date.

That entry's migration note has a sample in which the 1.0.0 call raises `TypeError` and the renamed call returns `exp_1`. My [release notes template](/articles/release-notes-template/) has a filled example of the page that announces a breaking SDK release.

## FAQ

Each answer below is a short version of a section above.

### What is SDK documentation?

SDK documentation is the set of pages that explains one client library in one programming language. It runs from the install command to the method reference and the changelog.

### What is the difference between SDK and API documentation?

API documentation describes HTTP endpoints and the responses they return. SDK documentation describes the methods and exception classes of a library that calls those endpoints for you.

### Can SDK documentation be generated automatically?

A generator can build the method reference from the code or from an OpenAPI file. The guides still need a writer, because no signature says when to use a method or when a retry is safe.
