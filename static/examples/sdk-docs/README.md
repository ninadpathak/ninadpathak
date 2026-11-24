# writinglab SDK docs example

A small Python SDK for the writing-lab example service, its documentation, and a script that checks the documentation against the SDK and the running service. It is the worked example for the article at https://ninadpathak.com/articles/sdk-documentation/.

This is a teaching example. The service is a local fixture with no authentication and no persistence, so do not deploy either part.

## Files

| File | What it is |
|---|---|
| `writinglab.py` | The SDK, version 2.0.0: one client class, two methods, seven exception classes. Standard library only. |
| `docs/getting-started.md` | Install, client setup and a first call with its output. |
| `docs/reference.md` | One entry per method, plus the two return types. |
| `docs/errors.md` | Each exception class, the retry rule and timeouts. |
| `docs/changelog.md` | Versions 1.0.0 and 2.0.0, with one breaking change and its migration note. |
| `check_sdk_docs.py` | The checker. |

## Run the checker

You need Python 3.9 or later and Node.js on your `PATH`. The checker starts the service itself, so the `writing-lab` folder has to sit next to this one:

```text
some-directory/
  sdk-docs/       this folder
  writing-lab/    from https://ninadpathak.com/static/examples/writing-lab.zip
```

```bash
python3 sdk-docs/check_sdk_docs.py
```

A run that finds no problem ends with `PASS` and exits 0. Any problem prints a `FAIL` line with the page, the line number where it has one, and what differs, and the script exits 1.

Pass other locations with `--sdk`, `--docs` and `--service`:

```bash
python3 sdk-docs/check_sdk_docs.py --sdk path/to/writinglab.py --service path/to/service.mjs
```

## What the checker checks

Code samples, in each `.md` file in `docs/`:

1. Each fenced `python` block runs without raising. The blocks of one page run in order in one namespace, against a fresh copy of the service that the script starts for that page and stops afterwards.
2. When a fenced `text` block follows a `python` block with only blank lines between them, the printed output of the `python` block equals it.

Reference, in `docs/reference.md`:

3. Each `` ### `Name(...)` `` heading names a class or method the module has, and the signature in the heading equals the real one: parameter names, order, the keyword-only marker and defaults.
4. The Parameter table under the heading has one row per real parameter and no row for a parameter the code lacks. Type and Default cells equal the annotation and the default in the code.
5. The `**Returns:**` line of a method equals its return annotation.
6. Each name in an Exception table is an exception class in the module or a Python built-in exception.
7. Each public class in `__all__` and each of its public methods has a heading.
8. Each dataclass in `__all__` has a heading whose Field table equals the dataclass fields and their types.

Errors, in `docs/errors.md`:

9. The Exception table lists each exception class the module defines, and no other name.
10. Each row's Parent cell equals the class's real base class.
11. Each row with an HTTP status and a service error equals an entry of `ERROR_CLASSES`, and each entry of `ERROR_CLASSES` has a row.

Changelog, in `docs/changelog.md`:

12. The newest `## X.Y.Z` heading equals the module's `__version__`.

## What it does not check

- Prose. A sentence that says a retry is safe is checked only where a sample shows it.
- `bash` blocks, and `text` blocks that follow them.
- Which method raises which exception. Python can't report that by inspection, so a sample has to trigger the exception.

## Versions

Run on 2026-11-23 with Python 3.12.3 and Node.js 26.13.1. The checker also passed on Python 3.9.25 and 3.13.18. The service's own README records Node.js 24.18.0.
