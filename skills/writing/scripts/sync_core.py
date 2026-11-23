#!/usr/bin/env python3
"""Keep generated copies of the writing core in step with core.md. Stdlib only.

Claude Code imports core.md from ~/.claude/CLAUDE.md, so it needs no copy.
Codex has no import syntax in AGENTS.md, so the core is written into a marked
block there. core.md stays the only file anyone edits.

Usage: sync_core.py           write the block into every target
       sync_core.py --check   exit 1 if any target has drifted or lacks the block
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, "..", "core.md")
TARGETS = [os.path.expanduser("~/.codex/AGENTS.md")]
BEGIN = "<!-- writing-core:begin (generated from ~/.agents/skills/writing/core.md by scripts/sync_core.py; edit core.md, not this block) -->"
END = "<!-- writing-core:end -->"


def block():
    return BEGIN + "\n" + open(CORE, encoding="utf-8").read().strip() + "\n" + END


def current(text):
    # Match by prefix, so a reworded marker replaces the old block instead of appending a second one.
    a = text.find("<!-- writing-core:begin")
    b = text.find(END, a)
    if a != -1 and b != -1:
        return a, b + len(END)
    return None


def main(argv):
    check = "--check" in argv
    want, ok = block(), True
    for path in TARGETS:
        if not os.path.exists(path):
            print(f"MISSING {path}")
            ok = False
            continue
        text = open(path, encoding="utf-8").read()
        span = current(text)
        if span and text[span[0]:span[1]] == want:
            print(f"OK {path}")
            continue
        if check:
            print(f"DRIFT {path}")
            ok = False
            continue
        new = text[:span[0]] + want + text[span[1]:] if span else text.rstrip("\n") + "\n\n" + want + "\n"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
        print(f"WROTE {path}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
