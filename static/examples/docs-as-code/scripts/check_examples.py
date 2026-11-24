#!/usr/bin/env python3
"""Run the commands in a docs page's console blocks and compare the output.

usage: python3 scripts/check_examples.py docs [more files or folders]

A console block is a fenced code block tagged `console` whose fence starts at
the left margin. A line that starts with "$ " is a command. The lines under
it, up to the next "$ " line or the end of the block, are the output the page
promises. Each command runs in bash from the directory you call this script
in, and what it prints (stdout and stderr together) has to equal the promised
lines. Spaces at the end of a line and blank lines at the end of the output
are ignored.

Put <!-- check_examples: skip --> on the line above a block to leave it out.
Skipped blocks are listed on every run. A run with no examples at all fails.
The commands run as you, with no sandbox, so point this at pages you trust.
"""
import argparse
import difflib
import pathlib
import subprocess
import sys

SKIP = "<!-- check_examples: skip -->"


def closes(line, ticks):
    """True when the line is a closing fence of at least `ticks` backticks."""
    line = line.strip()
    return len(line) >= ticks and set(line) == {"`"}


def console_blocks(lines):
    """Yield (line number of the opening fence, skipped, body lines)."""
    index = 0
    while index < len(lines):
        ticks = len(lines[index]) - len(lines[index].lstrip("`"))
        if ticks < 3:
            index += 1
            continue
        start, tag = index, lines[index][ticks:].strip()
        index += 1
        while index < len(lines) and not closes(lines[index], ticks):
            index += 1
        if tag == "console":
            above = [line.strip() for line in lines[:start] if line.strip()]
            yield start + 1, bool(above) and above[-1] == SKIP, lines[start + 1:index]
        index += 1


def examples(fence_line, body):
    """Split one block into [line number, command, promised output lines]."""
    found = []
    for offset, line in enumerate(body, start=1):
        if line.startswith("$ "):
            found.append([fence_line + offset, line[2:], []])
        elif found:
            found[-1][2].append(line.rstrip())
    for example in found:
        while example[2] and not example[2][-1]:
            example[2].pop()
    return found


def printed_by(command, timeout):
    try:
        done = subprocess.run(["bash", "-c", command], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return [f"(no result after {timeout} seconds)"]
    printed = [line.rstrip() for line in done.stdout.splitlines()]
    while printed and not printed[-1]:
        printed.pop()
    return printed


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the console examples in Markdown pages.")
    parser.add_argument("paths", nargs="+", help="Markdown files, or folders to search for .md files")
    parser.add_argument("--timeout", type=int, default=60, help="seconds allowed per command")
    args = parser.parse_args(argv)

    pages = []
    for path in map(pathlib.Path, args.paths):
        pages.extend(sorted(path.rglob("*.md")) if path.is_dir() else [path])

    ran = differed = 0
    for page in pages:
        page_ran, skipped = 0, []
        for fence_line, skip, body in console_blocks(page.read_text(encoding="utf-8").splitlines()):
            if skip:
                skipped.append(str(fence_line))
                continue
            for line_number, command, promised in examples(fence_line, body):
                page_ran += 1
                printed = printed_by(command, args.timeout)
                if printed == promised:
                    continue
                differed += 1
                print(f"{page}:{line_number}: the command does not print what the page shows")
                print(f"  $ {command}")
                for row in difflib.unified_diff(promised, printed, "the page", "the command", lineterm=""):
                    print(f"  {row}")
        where = f" (line {', '.join(skipped)})" if skipped else ""
        print(f"{page}: {page_ran} run, {len(skipped)} skipped{where}")
        ran += page_ran

    if ran == 0:
        print("FAIL: no console examples found, so nothing was checked")
        return 1
    if differed:
        print(f"FAIL: examples that differ from the page: {differed} of {ran}")
        return 1
    print(f"PASS: examples that print what the page shows: {ran} of {ran}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
