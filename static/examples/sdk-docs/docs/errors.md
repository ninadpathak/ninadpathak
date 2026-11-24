# Errors, retries and timeouts

Every error `writinglab` 2.0.0 raises for a failed request is a subclass of `WritingLabError`. This page lists each class, then says when the client retries and how long it waits.

## Exception classes

The client turns four of the service's error responses into their own classes. Any other error response raises `APIStatusError`.

| Exception | Parent | HTTP status | Service error | Raised when | What to do |
|---|---|---|---|---|---|
| `WritingLabError` | `Exception` | | | Never raised itself | Catch it to handle every error below in one place |
| `APIConnectionError` | `WritingLabError` | | | No attempt got a response: the connection was refused, closed early or timed out | Call again with the same key, which is on the exception as `idempotency_key` |
| `APIStatusError` | `WritingLabError` | | | The service returned an error with no class of its own | Read `status` and `code` |
| `InvalidKeyError` | `APIStatusError` | 400 | `invalid_key` | The key is empty, longer than 64 characters, or has a character other than a letter, digit or hyphen | Send a key that fits the rule |
| `InvalidFormatError` | `APIStatusError` | 400 | `invalid_format` | `format` is not `csv` or `json` | Send `csv` or `json` |
| `KeyConflictError` | `APIStatusError` | 409 | `key_conflict` | The key was used before on this service instance with a different format | Send the original format to get the stored record, or a new key for a new record |
| `PayloadTooLargeError` | `APIStatusError` | 413 | `body_too_large` | The request body is over 4,096 bytes | Send `csv` or `json` |

`APIStatusError` and its subclasses carry `status`, the HTTP status as an `int`, and `code`, the service's `error` string.

The service has two error responses this client gives no class, because neither method can cause them. `invalid_json` needs a broken JSON body, and the client builds the body itself. `not_found` is the service's answer for a path it doesn't serve, and the client calls only `/exports` and `/state`.

## Catch one error

Reuse a key with a different format and the service refuses the request:

```python
import os

from writinglab import KeyConflictError, WritingLab

client = WritingLab(os.environ["WRITINGLAB_URL"])
client.create_export("csv", idempotency_key="report-a")

try:
    client.create_export("json", idempotency_key="report-a")
except KeyConflictError as error:
    print(type(error).__name__, error.status, error.code)
```

```text
KeyConflictError 409 key_conflict
```

## Catch every error

Catch `WritingLabError` when the handling is the same for each failure. The three calls below fail for three reasons, and none stores a record:

```python
from writinglab import WritingLabError

calls = [
    {"format": "pdf", "idempotency_key": "report-b"},
    {"format": "csv", "idempotency_key": "report b"},
    {"format": "x" * 5000, "idempotency_key": "report-c"},
]
for call in calls:
    try:
        client.create_export(call["format"], idempotency_key=call["idempotency_key"])
    except WritingLabError as error:
        print(type(error).__name__, error.status, error.code)
print(client.get_state().exports)
```

```text
InvalidFormatError 400 invalid_format
InvalidKeyError 400 invalid_key
PayloadTooLargeError 413 body_too_large
1
```

## Retries

The client retries an attempt only when no response arrived. It makes up to `max_retries` more attempts, waits 0.1 seconds before the first retry and twice as long before each later one, and sends the same key and body every time.

An error response is never retried, because the same request would get the same answer.

The service can show a lost response on purpose. A request with the header `X-Fixture-Drop-Response: yes` and a new key is stored, and then the connection is closed with no response. The client below sends that header on every request, so its first attempt is lost and its retry gets the stored record:

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

Two requests reached the service and it holds one new record. `replayed` is `True` because the response that came back was the service's answer to the retry.

With retries off, the same lost response raises `APIConnectionError`. The record was stored anyway, so the count goes up by one:

```python
from writinglab import APIConnectionError

no_retry = WritingLab(
    os.environ["WRITINGLAB_URL"],
    max_retries=0,
    default_headers={"X-Fixture-Drop-Response": "yes"},
)
try:
    no_retry.create_export("csv", idempotency_key="report-e")
except APIConnectionError as error:
    print(type(error).__name__, error.attempts, error.idempotency_key)
print(client.get_state().exports)
```

```text
APIConnectionError 1 report-e
3
```

So after an `APIConnectionError`, call `create_export` again with the key from the exception and the same format. A new key would store a second record:

```python
recovered = client.create_export("csv", idempotency_key="report-e")
print(recovered.id, recovered.replayed)
print(client.get_state().exports)
```

```text
exp_3 True
3
```

## What a retry does not guarantee

The service keeps its keys in the memory of one process, and two running instances share none. The same key sent to a second instance stores a new record there, and `replayed` is `False`.

A restart clears the keys the same way, so a retry that arrives after a restart also stores a new record.

## Timeouts

`timeout` is the number of seconds one attempt waits for the connection and for each read. The default is `5.0`.

A timeout counts as no response, so the client retries it under the rule above. With `timeout=0.5` and `max_retries=1`, a call to a server that accepts the connection and never answers raises `APIConnectionError` after about 1.1 seconds: two attempts of 0.5 seconds and one wait of 0.1 seconds.
