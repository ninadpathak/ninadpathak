# Reference

This page describes `writinglab` 2.0.0. Each entry gives the signature, the parameters, the return type and the exceptions.

## Client

The module has one client class, `WritingLab`, with two methods.

### `WritingLab(base_url, *, timeout=5.0, max_retries=2, default_headers=None)`

Creates a client for one running service. Creating a client sends no request.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `base_url` | `str` | Required | The URL the service printed at startup, such as `http://127.0.0.1:49152`. |
| `timeout` | `float` | `5.0` | Seconds to wait for the connection, and for each read from it, on one attempt. |
| `max_retries` | `int` | `2` | How many more attempts to make after an attempt that got no response. `0` turns retries off. |
| `default_headers` | `dict[str, str] \| None` | `None` | Headers added to every request this client sends. |

| Exception | When |
|---|---|
| `ValueError` | `base_url` does not start with `http://` or has no host. The service listens on plain HTTP only. |

### `WritingLab.create_export(format, *, idempotency_key=None)`

Stores an export record and returns it. The service keeps the record in memory and generates no file.

Pass your own `idempotency_key` when your code may call this method again for the same piece of work, for example after a crash. The service returns the stored record for a key it has seen with the same format, so the second call stores nothing new.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `format` | `str` | Required | `"csv"` or `"json"`. The client sends the value as given and the service validates it. |
| `idempotency_key` | `str \| None` | `None` | From 1 to 64 letters, digits or hyphens. When it is `None`, the client generates a key and uses it for every attempt of this call. |

**Returns:** `Export`

| Exception | When |
|---|---|
| `InvalidFormatError` | The service rejected `format`. |
| `InvalidKeyError` | The service rejected `idempotency_key`. |
| `KeyConflictError` | The key was used before on this service instance with a different format. |
| `PayloadTooLargeError` | The request body was over 4,096 bytes, which takes a `format` string longer than 4,082 ASCII characters. |
| `APIConnectionError` | No attempt got a response. The service may still have stored the record. |
| `APIStatusError` | The service returned an error this client has no class for. |
| `ValueError` | The key can't be written as an HTTP header, for example because it has a line break. No request is sent. |

Retry safety: every attempt of one call carries the same key and body. The guarantee holds while one service instance keeps running, because a restart erases every stored key.

```python
import os

from writinglab import WritingLab

client = WritingLab(os.environ["WRITINGLAB_URL"])
export = client.create_export("json", idempotency_key="invoice-2026-11")
print(export.id, export.format, export.status, export.replayed)
```

```text
exp_1 json accepted False
```

A call with no key still stores one record. The key the client generated is not returned, so pass your own when you need to repeat the call later:

```python
unkeyed = client.create_export("csv")
print(unkeyed.id, unkeyed.replayed)
```

```text
exp_2 False
```

### `WritingLab.get_state()`

Returns how many export records and webhook events the running service instance holds. Use it to confirm that a retry stored no second record.

This method takes no parameters.

**Returns:** `State`

| Exception | When |
|---|---|
| `APIConnectionError` | No attempt got a response. |
| `APIStatusError` | The service returned an error status. |

```python
state = client.get_state()
print(state.exports, state.events)
```

```text
2 0
```

## Return types

Both return types are frozen dataclasses, so their fields can be read and not assigned.

### `Export`

| Field | Type | Description |
|---|---|---|
| `id` | `str` | The record's identifier, such as `exp_1`. Identifiers count up from 1 within one service instance. |
| `format` | `str` | The format the record was stored with. |
| `status` | `str` | Always `accepted`. No worker changes it. |
| `replayed` | `bool` | `False` when this response created the record. `True` when the service already held a record for the key and returned it. |

### `State`

| Field | Type | Description |
|---|---|---|
| `exports` | `int` | Export records held by this service instance. |
| `events` | `int` | Webhook events held by this service instance. This client sends none. |
