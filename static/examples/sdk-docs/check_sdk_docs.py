#!/usr/bin/env python3
"""Check the writinglab docs against the SDK and the running service.

What it checks:

Code samples (every .md file in the docs folder)
  1. Each fenced python block runs without raising. The blocks of one page run
     in order in one namespace, against a fresh copy of the service that the
     script starts for that page and stops afterwards.
  2. When a fenced text block follows a python block with only blank lines
     between them, the python block's printed output equals it.

Reference (reference.md)
  3. Each "### `Name(...)`" heading names a class or method the module has, and
     the signature in the heading equals the real one: parameter names, order,
     the keyword-only marker and defaults.
  4. The Parameter table under the heading has one row per real parameter, and
     no row for a parameter the code lacks. Type and Default cells equal the
     annotation and the default in the code.
  5. The "**Returns:**" line of a method equals its return annotation.
  6. Each name in an Exception table is an exception class in the module or a
     Python built-in exception.
  7. Each public class in __all__ and each of its public methods has a heading.
  8. Each dataclass in __all__ has a "### `Name`" heading whose Field table
     equals the dataclass fields and their types.

Errors (errors.md)
  9. The Exception table lists each exception class the module defines, and no
     other name.
 10. Each row's Parent cell equals the class's real base class.
 11. Each row with an HTTP status and a service error equals an entry of
     ERROR_CLASSES, and each entry of ERROR_CLASSES has a row.

Changelog (changelog.md)
 12. The newest "## X.Y.Z" heading equals the module's __version__.

What it does not check: prose, bash blocks, and which method raises which
exception (Python can't report that by inspection; a sample has to trigger it).

Usage (Python 3.9 or later, Node.js on PATH):
  python3 check_sdk_docs.py
  python3 check_sdk_docs.py --sdk path/to/writinglab.py
  python3 check_sdk_docs.py --docs path/to/docs --service path/to/service.mjs
Exit status: 0 when every check passes, 1 when any check fails.
"""
import argparse
import builtins
import contextlib
import dataclasses
import importlib.util
import inspect
import io
import os
import re
import subprocess
import sys
from pathlib import Path

# Importing the SDK should leave no __pycache__ folder beside it.
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
FENCE = re.compile(r"^```(\w*)\s*$")
HEADING = re.compile(r"^(#{2,3})\s+(.*?)\s*$")
ENTRY = re.compile(r"^`([A-Za-z_][\w.]*)(?:\((.*)\))?`$")


def count(number, noun):
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def load_sdk(path):
    spec = importlib.util.spec_from_file_location("writinglab", path)
    module = importlib.util.module_from_spec(spec)
    # Registered under its real name so `import writinglab` in a sample gets this file.
    sys.modules["writinglab"] = module
    spec.loader.exec_module(module)
    return module


def fenced_blocks(lines):
    """Return [(language, first line number, text, last line index)] for a page."""
    blocks, start, language, body = [], None, None, []
    for index, line in enumerate(lines):
        match = FENCE.match(line)
        if match and start is None:
            start, language, body = index, match.group(1), []
        elif match and start is not None:
            blocks.append((language, start + 1, "\n".join(body), index))
            start = None
        elif start is not None:
            body.append(line)
    return blocks


def start_service(service_path):
    # Resolved first: the service only starts when its real path is the one node was given.
    process = subprocess.Popen(["node", str(Path(service_path).resolve())], stdout=subprocess.PIPE, text=True)
    url = process.stdout.readline().strip()
    if not url.startswith("http://"):
        process.terminate()
        raise SystemExit(f"the service at {service_path} did not print a URL")
    return process, url


def check_samples(page, service_path, failures):
    lines = page.read_text(encoding="utf-8").splitlines()
    blocks = fenced_blocks(lines)
    python_blocks = [b for b in blocks if b[0] == "python"]
    if not python_blocks:
        return 0, 0
    ran = matched = 0
    process, url = start_service(service_path)
    os.environ["WRITINGLAB_URL"] = url
    namespace = {"__name__": "__main__"}
    try:
        for position, (language, line_number, code, end) in enumerate(blocks):
            if language != "python":
                continue
            printed = io.StringIO()
            try:
                with contextlib.redirect_stdout(printed):
                    exec(compile(code, f"{page.name}:{line_number}", "exec"), namespace)
            except Exception as error:
                left = len([b for b in python_blocks if b[1] > line_number])
                failures.append(
                    f"{page.name} line {line_number}: the block raised "
                    f"{type(error).__name__}: {error} ({count(left, 'later block')} on this page not run)"
                )
                break
            ran += 1
            following = blocks[position + 1] if position + 1 < len(blocks) else None
            if not following or following[0] != "text":
                continue
            between = lines[end + 1 : following[1] - 1]
            if any(text.strip() for text in between):
                continue
            expected = following[2].rstrip()
            got = printed.getvalue().rstrip()
            if got == expected:
                matched += 1
            else:
                failures.append(
                    f"{page.name} line {line_number}: the output differs\n"
                    f"       documented: {expected!r}\n"
                    f"       printed:    {got!r}"
                )
    finally:
        process.terminate()
        process.wait()
    return ran, matched


def sections(lines):
    """Split a page into (heading text, body lines) for each ## or ### heading."""
    found, current, in_fence = [], None, False
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
        match = None if in_fence else HEADING.match(line)
        if match:
            current = (match.group(2), [])
            found.append(current)
        elif current:
            current[1].append(line)
    return found


def cell_text(cell):
    return cell.strip().replace("\\|", "|").strip("`").strip()


def tables(body):
    """Return each Markdown table in body as (header cells, [row cells])."""
    found, rows = [], []
    for line in list(body) + [""]:
        if line.startswith("|"):
            cells = re.split(r"(?<!\\)\|", line.strip())[1:-1]
            rows.append([cell_text(cell) for cell in cells])
        elif rows:
            if len(rows) >= 2:
                found.append((rows[0], rows[2:]))
            rows = []
    return found


def table_with(body, *columns):
    for header, rows in tables(body):
        if all(column in header for column in columns):
            return header, rows
    return None


def annotation_text(annotation):
    if annotation is inspect.Signature.empty:
        return ""
    return annotation if isinstance(annotation, str) else getattr(annotation, "__name__", str(annotation))


def real_signature(parameters):
    parts, starred = [], False
    for parameter in parameters:
        if parameter.kind is parameter.KEYWORD_ONLY and not starred:
            parts.append("*")
            starred = True
        if parameter.kind is parameter.VAR_POSITIONAL:
            parts.append("*" + parameter.name)
            starred = True
            continue
        if parameter.kind is parameter.VAR_KEYWORD:
            parts.append("**" + parameter.name)
            continue
        default = "" if parameter.default is parameter.empty else f"={parameter.default!r}"
        parts.append(parameter.name + default)
    return ", ".join(parts)


def exception_classes(sdk):
    return {
        name: value
        for name, value in vars(sdk).items()
        if inspect.isclass(value) and issubclass(value, Exception) and value.__module__ == sdk.__name__
    }


def check_reference(page, sdk, failures):
    counts = {"signatures": 0, "parameters": 0, "fields": 0}
    documented = {}
    for heading, body in sections(page.read_text(encoding="utf-8").splitlines()):
        entry = ENTRY.match(heading)
        if entry:
            documented[entry.group(1)] = (entry.group(2), body)

    public = [name for name in getattr(sdk, "__all__", []) if inspect.isclass(getattr(sdk, name, None))]
    clients = [n for n in public if not issubclass(getattr(sdk, n), Exception) and not dataclasses.is_dataclass(getattr(sdk, n))]
    records = [n for n in public if dataclasses.is_dataclass(getattr(sdk, n))]

    expected = {}
    for name in clients:
        cls = getattr(sdk, name)
        expected[name] = cls.__init__
        for method, value in vars(cls).items():
            if inspect.isfunction(value) and not method.startswith("_"):
                expected[f"{name}.{method}"] = value

    for name in expected:
        if name not in documented:
            failures.append(f"{page.name}: the code has {name}() and the page has no heading for it")
    for name, (signature, _) in documented.items():
        if signature is not None and name not in expected:
            failures.append(f"{page.name}: the page documents {name}(), which the code does not have")

    names = exception_classes(sdk)
    for name, function in expected.items():
        if name not in documented:
            continue
        signature, body = documented[name]
        real = inspect.signature(function)
        parameters = [p for p in real.parameters.values() if p.name != "self"]
        written = re.sub(r"\s+", " ", signature or "").strip()
        if written == real_signature(parameters):
            counts["signatures"] += 1
        else:
            failures.append(
                f"{page.name}: {name} is documented as ({written}) and the code has ({real_signature(parameters)})"
            )
        table = table_with(body, "Parameter")
        rows = {row[0]: row for row in table[1]} if table else {}
        header = table[0] if table else []
        for parameter in parameters:
            if parameter.name not in rows:
                failures.append(f"{page.name}: {name} omits parameter {parameter.name}, which the code has")
                continue
            row = dict(zip(header, rows[parameter.name]))
            default = "Required" if parameter.default is parameter.empty else repr(parameter.default)
            if row.get("Type") != annotation_text(parameter.annotation):
                failures.append(
                    f"{page.name}: {name} documents {parameter.name} as {row.get('Type')} "
                    f"and the code annotates it {annotation_text(parameter.annotation)}"
                )
            elif row.get("Default") != default:
                failures.append(
                    f"{page.name}: {name} documents the default of {parameter.name} as "
                    f"{row.get('Default')} and the code has {default}"
                )
            else:
                counts["parameters"] += 1
        for row_name in rows:
            if row_name not in real.parameters:
                failures.append(f"{page.name}: {name} documents parameter {row_name}, which the code does not have")
        if "." in name:
            returns = [re.match(r"^\*\*Returns:\*\*\s+`(.+?)`", line) for line in body]
            returns = [match.group(1) for match in returns if match]
            if returns != [annotation_text(real.return_annotation)]:
                failures.append(
                    f"{page.name}: {name} documents its return type as {returns or 'nothing'} "
                    f"and the code annotates it {annotation_text(real.return_annotation)}"
                )
        raised = table_with(body, "Exception", "When")
        for row in raised[1] if raised else []:
            builtin = getattr(builtins, row[0], None)
            if row[0] not in names and not (inspect.isclass(builtin) and issubclass(builtin, Exception)):
                failures.append(f"{page.name}: {name} lists exception {row[0]}, which the code does not have")

    for name in records:
        if name not in documented:
            failures.append(f"{page.name}: the code has the return type {name} and the page has no heading for it")
            continue
        table = table_with(documented[name][1], "Field", "Type")
        rows = {row[0]: row[1] for row in table[1]} if table else {}
        fields = {field.name: annotation_text(field.type) for field in dataclasses.fields(getattr(sdk, name))}
        for field, kind in fields.items():
            if field not in rows:
                failures.append(f"{page.name}: {name} omits field {field}, which the code has")
            elif rows[field] != kind:
                failures.append(f"{page.name}: {name} documents {field} as {rows[field]} and the code annotates it {kind}")
            else:
                counts["fields"] += 1
        for field in rows:
            if field not in fields:
                failures.append(f"{page.name}: {name} documents field {field}, which the code does not have")
    return counts


def check_errors(page, sdk, failures):
    counts = {"exceptions": 0, "mappings": 0}
    table = table_with(page.read_text(encoding="utf-8").splitlines(), "Exception", "Parent")
    if not table:
        failures.append(f"{page.name}: no table with Exception and Parent columns")
        return counts
    header, rows = table
    names = exception_classes(sdk)
    mapping = {pair: cls.__name__ for pair, cls in sdk.ERROR_CLASSES.items()}
    documented_pairs = {}
    for cells in rows:
        row = dict(zip(header, cells))
        name = row["Exception"]
        if name not in names:
            failures.append(f"{page.name}: the page lists exception {name}, which the code does not have")
            continue
        parent = names[name].__bases__[0].__name__
        if row["Parent"] == parent:
            counts["exceptions"] += 1
        else:
            failures.append(f"{page.name}: {name} is documented under {row['Parent']} and the code derives it from {parent}")
        if row.get("HTTP status") and row.get("Service error"):
            documented_pairs[(int(row["HTTP status"]), row["Service error"])] = name
    for name in names:
        if name not in [cells[0] for cells in rows]:
            failures.append(f"{page.name}: the code has exception {name} and the page does not list it")
    for pair, name in documented_pairs.items():
        if mapping.get(pair) == name:
            counts["mappings"] += 1
        else:
            failures.append(
                f"{page.name}: {pair[0]} {pair[1]} is documented as {name} "
                f"and the code maps it to {mapping.get(pair, 'APIStatusError')}"
            )
    for pair, name in mapping.items():
        if pair not in documented_pairs:
            failures.append(f"{page.name}: the code maps {pair[0]} {pair[1]} to {name} and the page has no row for it")
    return counts


def check_changelog(page, sdk, failures):
    for line in page.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^## (\d+\.\d+\.\d+)", line)
        if match:
            if match.group(1) != sdk.__version__:
                failures.append(
                    f"{page.name}: the newest entry is {match.group(1)} and the code is version {sdk.__version__}"
                )
            return match.group(1)
    failures.append(f"{page.name}: no '## X.Y.Z' heading")
    return None


def report(label, detail, failures, before):
    verdict = "ok  " if len(failures) == before else "FAIL"
    print(f"{verdict} {label:<27}{detail}")
    for failure in failures[before:]:
        print(f"     {failure}")


def main():
    parser = argparse.ArgumentParser(description="Check the writinglab docs against the SDK and the running service.")
    parser.add_argument("--sdk", default=HERE / "writinglab.py", type=Path)
    parser.add_argument("--docs", default=HERE / "docs", type=Path)
    parser.add_argument("--service", default=HERE.parent / "writing-lab" / "service.mjs", type=Path)
    arguments = parser.parse_args()

    sdk = load_sdk(arguments.sdk)
    failures = []
    for page in sorted(arguments.docs.glob("*.md")):
        before = len(failures)
        ran, matched = check_samples(page, arguments.service, failures)
        report(f"{page.name} samples", f"{count(ran, 'python block')} ran, {count(matched, 'output')} matched", failures, before)

    before = len(failures)
    counts = check_reference(arguments.docs / "reference.md", sdk, failures)
    report(
        "reference.md entries",
        f"{count(counts['signatures'], 'signature')}, {count(counts['parameters'], 'parameter')}, {count(counts['fields'], 'return field')} matched the code",
        failures,
        before,
    )
    before = len(failures)
    counts = check_errors(arguments.docs / "errors.md", sdk, failures)
    report(
        "errors.md table",
        f"{count(counts['exceptions'], 'exception')}, {count(counts['mappings'], 'error mapping')} matched the code",
        failures,
        before,
    )
    before = len(failures)
    version = check_changelog(arguments.docs / "changelog.md", sdk, failures)
    report("changelog.md version", f"newest entry {version}, code {sdk.__version__}", failures, before)

    print(f"FAIL: {count(len(failures), 'problem')}" if failures else "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
