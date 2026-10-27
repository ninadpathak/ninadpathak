#!/usr/bin/env python3
"""Write static/videos/<slug>/captions.vtt from a film's word timings.

Usage: python tools/build_video_captions.py <slug> [--check]

Inputs live in content/videos/<slug>/: words.json (per-line word timings from the
voice render, times relative to the start of each line) and video.yaml (line_offsets,
the second each line starts in the finished film). Each line is split into cues at
commas and full stops, and a fragment of fewer than three words joins the next one,
so a cue is a clause the viewer can read in one glance. A cue ends when its last word
ends, plus a short hold that never runs into the next cue.

Word timings carry what the voice said, which can differ from the written script: a
file name such as CLAUDE.md is voiced as "Claude dot MD". When a line has a "text"
field, the captions show that written text, and each written word takes the timing of
the spoken words it aligns with.

--check exits 1 if the committed captions.vtt differs from what the inputs produce.
"""
import difflib
import json
import re
import sys
from pathlib import Path

import yaml

HOLD = 0.4
MIN_WORDS = 3


def stamp(seconds: float) -> str:
    millis = round(seconds * 1000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"00:{minutes:02d}:{secs:02d}.{millis:03d}"


def norm(word: str) -> str:
    return re.sub(r"[^\w@.']", "", word.lower()).rstrip(".")


def written_words(line: dict) -> list[dict]:
    """The line's written words, each timed by the spoken words it replaces."""
    spoken = line["words"]
    text = line.get("text")
    if not text or text == " ".join(w["w"] for w in spoken):
        return spoken
    written = text.split()
    matcher = difflib.SequenceMatcher(None, [norm(w) for w in written], [norm(w["w"]) for w in spoken],
                                      autojunk=False)
    timed = []
    for op, w1, w2, s1, s2 in matcher.get_opcodes():
        if op == "equal":
            timed += [{"w": written[w1 + i], "start": spoken[s1 + i]["start"], "end": spoken[s1 + i]["end"]}
                      for i in range(w2 - w1)]
        elif op == "replace":
            # Spread the spoken span evenly across the written words that replace it.
            start, end, count = spoken[s1]["start"], spoken[s2 - 1]["end"], w2 - w1
            step = (end - start) / count
            timed += [{"w": written[w1 + i], "start": round(start + i * step, 3),
                       "end": round(start + (i + 1) * step, 3)} for i in range(count)]
        elif op == "delete":
            raise ValueError(f"written text has words the voice did not say: {written[w1:w2]}")
        # "insert": spoken filler with no written word; its time stays inside the cue.
    return timed


def clauses(words: list[dict]) -> list[list[dict]]:
    groups, current = [], []
    for word in words:
        current.append(word)
        if word["w"].endswith((",", ".")):
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    merged = []
    for group in groups:
        if merged and len(merged[-1]) < MIN_WORDS:
            merged[-1] = merged[-1] + group
        else:
            merged.append(group)
    if len(merged) > 1 and len(merged[-1]) < MIN_WORDS:
        merged[-2] = merged[-2] + merged.pop()
    return merged


def build(slug: str) -> str:
    source = Path("content/videos") / slug
    meta = yaml.safe_load((source / "video.yaml").read_text(encoding="utf-8"))
    lines = json.loads((source / "words.json").read_text(encoding="utf-8"))
    cues = []
    for line_id, offset in meta["line_offsets"].items():
        for group in clauses(written_words(lines[line_id])):
            cues.append([offset + group[0]["start"], offset + group[-1]["end"], " ".join(w["w"] for w in group)])
    for index, cue in enumerate(cues):
        limit = cues[index + 1][0] if index + 1 < len(cues) else meta["duration_seconds"]
        cue[1] = min(cue[1] + HOLD, limit)
    body = "\n\n".join(f"{n}\n{stamp(start)} --> {stamp(end)}\n{text}" for n, (start, end, text) in enumerate(cues, 1))
    return f"WEBVTT\n\n{body}\n"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    slug = sys.argv[1]
    vtt = build(slug)
    meta = yaml.safe_load((Path("content/videos") / slug / "video.yaml").read_text(encoding="utf-8"))
    target = Path("static/videos") / slug / meta["captions"]
    if "--check" in sys.argv[2:]:
        if not target.is_file() or target.read_text(encoding="utf-8") != vtt:
            print(f"{target} is out of date; run python tools/build_video_captions.py {slug}", file=sys.stderr)
            return 1
        return 0
    target.write_text(vtt, encoding="utf-8")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
