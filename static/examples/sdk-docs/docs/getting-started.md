# Get started with writinglab

`writinglab` is a Python client for the writing-lab example service. This page installs version 2.0.0, creates a client and stores a first export record.

## Requirements

- Python 3.9 or later. The module was run on Python 3.9.25, 3.12.3 and 3.13.18, and it imports nothing outside the standard library.
- Node.js, to run the service. The service was run on Node.js 26.13.1.
- The `writing-lab` folder, which holds the service.

## Install

`writinglab` is one file and it is not published on PyPI. Copy `writinglab.py` into the directory you run Python from, then check the version:

```python
import writinglab

print(writinglab.__version__)
```

```text
2.0.0
```

## Start the service

Run the service in one terminal. It prints the URL it listens on, with a port the operating system picks:

```bash
node writing-lab/service.mjs
```

```text
http://127.0.0.1:49152
```

In a second terminal, put the URL your service printed into `WRITINGLAB_URL`:

```bash
export WRITINGLAB_URL=http://127.0.0.1:49152
```

## Create a client

The client needs the base URL and nothing else. The service has no authentication, so there is no API key to pass.

```python
import os

from writinglab import WritingLab

client = WritingLab(os.environ["WRITINGLAB_URL"])
```

## Store a first export record

Call `create_export` with a format and an idempotency key. The key names this request, so a repeat of the same call can't store a second record.

```python
export = client.create_export("csv", idempotency_key="report-a")
print(export)
```

```text
Export(id='exp_1', format='csv', status='accepted', replayed=False)
```

The service stored a record. It generates no file.

Send the same call again and the service returns the stored record. `replayed` is `True`, and the record count is still 1:

```python
again = client.create_export("csv", idempotency_key="report-a")
print(again.id, again.replayed)
print(client.get_state())
```

```text
exp_1 True
State(exports=1, events=0)
```

## Next

- [Reference](reference.md): every parameter, return field and exception.
- [Errors, retries and timeouts](errors.md): what each exception means and when the client retries.
- [Changelog](changelog.md): what changed in 2.0.0 and how to update a 1.0.0 call.
