#!/usr/bin/env python3
"""Mechanical checks for Ninad's prose standard. Stdlib only.

Usage: python3 check_prose.py FILE.md [FILE2.md ...] [--first-person-baseline N]

The banned-word lists are read from ../core.md, their single home.

Fails (exit 1) on: banned words anywhere in the file (code, frontmatter and
headings included; the list lines of core.md itself are skipped), a sentence that begins with a number, two headings with no
prose between them. Everything else is reported for judgement: em dashes,
framing openers, sentences with three or more commas, runs of three prose
paragraphs, curly quotes, hard-wrapped paragraphs, first-person token count.

Paragraphs are reflowed before sentence tests, so a hard-wrapped continuation
line that starts with a figure is not a false positive. Verify each hit in
context before changing it: a quotation of someone else's words may be exempt.
"""
import re
import sys

import os

CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core.md")
LIST_LABELS = ("Hard:", "Slop:", "Named sense only:")


def load_lists(path=CORE):
    """The word lists live once, in core.md. Each is one line: 'Label: a, b, c.'"""
    out = {}
    for line in open(path, encoding="utf-8").read().splitlines():
        for label in LIST_LABELS:
            if line.startswith(label):
                items = line[len(label):].strip().rstrip(".").split(",")
                out[label] = [re.sub(r"\s*\(.*?\)", "", i).strip() for i in items if i.strip()]
    missing = [l for l in LIST_LABELS if not out.get(l)]
    if missing:
        sys.exit(f"check_prose: {path} is missing list line(s): {missing}")
    return out


_LISTS = load_lists()
HARD, SLOP, NAMED = (_LISTS[l] for l in LIST_LABELS)
OPENERS = [
    "the useful part of", "the interesting thing about", "the thing to understand about",
    "what matters here is", "the key insight is", "where this gets hard is",
    "but here is the thing", "but here's the thing", "that is where it gets interesting",
    "there is a second reason", "the load-bearing decision", "the step that matters is",
    "here is the thing", "here's the thing", "the real question", "it turns out",
    "note that", "by the end of this", "isn't just", "is not just", "not only",
    "in conclusion", "let's dive", "in this article",
]
NUMBER_WORDS = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|hundreds|thousand|thousands|million|millions|billion|dozens|half)"
NUM_START = re.compile(r"^[\"'(\[]?(?:\d|" + NUMBER_WORDS + r"\b)", re.I)
FIRST_PERSON = re.compile(r"\b(?:I|I'm|I've|I'd|I'll|me|my|mine|myself)\b")
SENT_SPLIT = re.compile(r"(?<=[.!?])[\"')\]]?\s+(?=[\"'(\[]?[A-Z0-9])")


def word_hits(text, terms):
    hits = []
    for term in terms:
        body = r".{1,60}?".join(re.escape(part.strip()) for part in term.split("..."))
        pat = re.compile(r"(?<![\w-])" + body + r"(?![\w-])", re.I)
        n = len(pat.findall(text))
        if n:
            hits.append((term, n))
    return hits


def blocks(lines):
    """Yield (kind, text, lineno). kinds: heading, code, table, quote, list, image, prose."""
    i, n = 0, len(lines)
    if lines and lines[0].strip() == "---":
        j = 1
        while j < n and lines[j].strip() != "---":
            j += 1
        yield ("frontmatter", "\n".join(lines[: j + 1]), 1)
        i = j + 1
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.lstrip().startswith("```"):
            j = i + 1
            while j < n and not lines[j].lstrip().startswith("```"):
                j += 1
            yield ("code", "\n".join(lines[i : j + 1]), i + 1)
            i = j + 1
            continue
        if re.match(r"^#{1,6}\s", line):
            yield ("heading", re.sub(r"^#{1,6}\s+", "", line).strip(), i + 1)
            i += 1
            continue
        if line.lstrip().startswith("|"):
            j = i
            while j < n and lines[j].lstrip().startswith("|"):
                j += 1
            yield ("table", "\n".join(lines[i:j]), i + 1)
            i = j
            continue
        if re.match(r"^!\[", line.strip()):
            yield ("image", line.strip(), i + 1)
            i += 1
            continue
        if line.lstrip().startswith(">"):
            j = i
            while j < n and lines[j].lstrip().startswith(">"):
                j += 1
            yield ("quote", " ".join(re.sub(r"^\s*>\s?", "", x) for x in lines[i:j]), i + 1)
            i = j
            continue
        m = re.match(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.*)$", line)
        if m:
            j, body = i + 1, [m.group(2)]
            while j < n and lines[j].strip() and not re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", lines[j]) and lines[j].startswith(" "):
                body.append(lines[j].strip())
                j += 1
            yield ("list", " ".join(body), i + 1)
            i = j
            continue
        j, body = i, []
        while j < n and lines[j].strip() and not re.match(r"^(#{1,6}\s|\s*```|\s*\||\s*>|\s*(?:[-*+]|\d+[.)])\s|!\[)", lines[j]):
            body.append(lines[j].strip())
            j += 1
        yield ("prose", " ".join(body), i + 1) if len(body) == 1 else ("prose-wrapped", " ".join(body), i + 1)
        i = j


def sentences(text):
    return [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]


def check(path, baseline=None):
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    fails, notes = [], []

    scan = "\n".join(l for l in lines if not l.startswith(LIST_LABELS))
    # A file that teaches the replacements has to name the words; it opts out with a marker.
    words = notes if "check_prose: word-mentions-allowed" in text else fails  # also softens number-start hits
    for term, n in word_hits(scan, HARD):
        words.append(f"banned word '{term}' x{n}")
    for term, n in word_hits(scan, SLOP):
        words.append(f"slop word '{term}' x{n}")
    for term, n in word_hits(scan, NAMED):
        notes.append(f"'{term}' x{n}: banned in its named sense, check each use")

    prev_kind, wall, wrapped = None, 0, 0
    for kind, body, ln in blocks(lines):
        if kind == "heading" and prev_kind == "heading":
            fails.append(f"line {ln}: heading directly after a heading")
        if kind in ("prose", "prose-wrapped", "list"):
            wall = wall + 1 if kind != "list" else 0
            if wall == 3:
                notes.append(f"line {ln}: third consecutive prose paragraph")
        elif kind not in ("image",):
            wall = 0
        if kind == "prose-wrapped":
            wrapped += 1
        if kind in ("prose", "prose-wrapped", "list", "heading", "quote"):
            units = [body] if kind == "heading" else sentences(body)
            for s in units:
                if NUM_START.match(s):
                    soft = kind == "quote" or words is notes
                    tag = "quote, verify" if soft else "FAIL"
                    (notes if soft else fails).append(f"line {ln}: starts with a number ({tag}): {s[:70]}")
                if s.count(",") >= 3:
                    notes.append(f"line {ln}: 3+ commas, check for a list of 3+ values: {s[:70]}")
        prev_kind = kind

    lowered = text.lower()
    for op in OPENERS:
        n = lowered.count(op)
        if n:
            notes.append(f"framing/tell phrase '{op}' x{n}")
    dashes = text.count("—") + text.count("–")
    if dashes:
        notes.append(f"em/en dashes: {dashes}")
    curly = len(re.findall(r"[“”‘’]", text))
    if curly:
        notes.append(f"curly quotes: {curly}")
    if wrapped:
        notes.append(f"hard-wrapped paragraphs: {wrapped}")
    fp = len(FIRST_PERSON.findall(text))
    msg = f"first-person tokens: {fp}"
    if baseline is not None:
        msg += f" (baseline {baseline}, {'DROPPED' if fp < baseline else 'held'})"
        if fp < baseline:
            notes.append("first-person count dropped; a judgement was probably sanded off")
    notes.append(msg)

    print(f"== {path}")
    for f in fails:
        print("FAIL", f)
    for w in notes:
        print("note", w)
    print("result:", "FAIL" if fails else "pass", f"({len(fails)} failures, {len(notes)} notes)")
    return not fails


def main(argv):
    baseline = None
    if "--first-person-baseline" in argv:
        k = argv.index("--first-person-baseline")
        baseline = int(argv[k + 1])
        del argv[k : k + 2]
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print(__doc__)
        return 2
    ok = all([check(f, baseline) for f in files])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
