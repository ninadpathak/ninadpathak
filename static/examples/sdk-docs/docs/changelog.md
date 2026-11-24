# Changelog

Versions of `writinglab`, newest first. Both versions were written on the same day, as the example for one article.

## 2.0.0 (2026-11-23)

Works with the writing-lab service as shipped in `writing-lab/service.mjs` on 2026-11-23. The service has no version number of its own.

### Breaking

- `create_export`: the `key` parameter is now `idempotency_key`, and it is keyword-only.

A 1.0.0 call that passes the key by position, or as `key=`, raises `TypeError` in 2.0.0 before any request is sent:

```python
import os

from writinglab import WritingLab

client = WritingLab(os.environ["WRITINGLAB_URL"])

for arguments, keywords in [(("csv", "report-a"), {}), (("csv",), {"key": "report-a"})]:
    try:
        client.create_export(*arguments, **keywords)
    except TypeError as error:
        print(type(error).__name__)
print(client.get_state().exports)
```

```text
TypeError
TypeError
0
```

Migration: pass the key as `idempotency_key=`.

```python
export = client.create_export("csv", idempotency_key="report-a")
print(export.id)
```

```text
exp_1
```

### Added

- `create_export` generates a key when `idempotency_key` is left out.
- The client retries an attempt that got no response, up to `max_retries` times, with the same key.
- `Export.replayed` says whether the service returned a record it already held.
- `get_state()` returns the service's record counts.
- `InvalidKeyError`, `InvalidFormatError`, `KeyConflictError` and `PayloadTooLargeError` replace a bare `APIStatusError` for four error responses, and `APIConnectionError` reports a call that got no response.
- `default_headers` and `max_retries` on the client.

## 1.0.0 (2026-11-23)

- First version: `WritingLab(base_url, *, timeout=5.0)` and `create_export(format, key)`.
