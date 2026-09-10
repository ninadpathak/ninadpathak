# Export request reference

The local fixture accepts `POST /exports`. It has no authentication and binds only to loopback. It accepts a JSON object containing exactly one field.

| Field or header | Contract |
| --- | --- |
| `format` | Required string: `csv` or `json` |
| `Idempotency-Key` | Required; 1 to 64 ASCII letters, digits, or hyphens |
| `X-Fixture-Drop-Response` | Optional test control; `yes` closes the connection after storing a new key |
| Body size | Limit: 4096 bytes |

| Response | Meaning |
| --- | --- |
| HTTP 202 | A new key created a record |
| HTTP 200 | The key and format matched a retained record |
| HTTP 400 | Invalid JSON, key, or format; no record created |
| HTTP 409 | A retained key was reused with a different format; no new record created |
| HTTP 413 | The body exceeded the fixture's size limit |

A successful response contains `id`, `format`, and `status`. The identifier is sequential within one fixture instance; status is `accepted`. No worker generates a file.

Retention lasts only while this server instance runs. There is no expiration timer within the instance. Restarting erases the map, so the service cannot recognize an earlier key afterward. It cannot provide a guarantee about duplicate work across restart or across multiple servers.

Check these boundaries with `node check.mjs`. A failed assertion blocks use of the affected instruction until the implementation and documentation agree.
