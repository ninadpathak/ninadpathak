#!/usr/bin/env python3
"""Flag first-person claims and bare measurements across every published post.

CHARTER 2c: a first-person claim ships only if a reader who knows the subject could not
point at it and say "that is bullshit". The dangerous ones are specific events and
measurements Ninad did not make — a named client, a benchmark not run, a number with no
source. An honestly held opinion is never falsifiable in the damaging sense.

Two repair passes have run, each against a hand-picked list: the top ten by Search
Console value, then eight benchmark articles. Both were productive and both were
incomplete, because a list assembled by hand cannot cover 89 posts. Claims kept turning
up outside whatever list was current — `context-windows-vs-memory` states a cost
measured on a named RTX 4090, `time-to-first-token-ttft` describes an assistant built
with a two-model handoff, `best-llms-for-coding` cites a benchmark that a later audit
found has no reproducible artifact.

This replaces the list with a sweep. It decides nothing: every hit is a candidate for a
reviewer to classify KEEP, REWRITE or CUT, and the reviewer is Codex because Claude
commissioned the content.

    tools/audit_claims.py                    # full report
    tools/audit_claims.py --slug <slug>      # one post
    tools/audit_claims.py --count            # per-post totals, highest first
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import frontmatter

POSTS = pathlib.Path("content/posts")

# A first-person verb that asserts an action taken. "I think" and "I look for" are
# judgment and deliberately absent.
FIRST_PERSON_ACTION = re.compile(
    r"\b(?:I|we)\s+(?:"
    r"ran|run|measured|tested|benchmarked|timed|profiled|audited|built|shipped|"
    r"deployed|instrumented|traced|logged|reproduced|verified|counted|surveyed|"
    r"interviewed|migrated|rewrote|debugged|hit|saw|found"
    r")\b", re.IGNORECASE)

# A measurement with a unit, or a proportion. These are only a problem when the article
# claims them as its own, so proximity to first person is what promotes them.
MEASUREMENT = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:ms|s|sec|seconds?|us|µs|ns|MB|KB|GB|TB|TFLOPS|FLOPs|"
    r"tokens?/s|req/s|qps|%|USD|\$)\b"
    r"|\b\d+\s+(?:of|out of)\s+\d+\b"
    r"|\bp\d{2}\b", re.IGNORECASE)

# Named hardware or a named model with a version is where an unbacked benchmark hides.
NAMED_KIT = re.compile(
    r"\b(?:RTX|GTX|A100|H100|H200|M1|M2|M3|M4|EPYC|Xeon|Ryzen)\b"
    r"|\b(?:Llama|Mistral|Gemini|GPT|Claude|Qwen|DeepSeek)[\s-]?\d", re.IGNORECASE)

# Articles a later audit found to have no reproducible artifact. A live article that
# cites one of these as its own evidence inherits the problem.
UNBACKED = (
    "agentic-cli-benchmarks", "beam-memory-benchmark", "local-wasm-vector-benchmarks",
    "lambda-calculus-ai-reasoning-benchmark", "rag-evaluation-metrics-what-actually-matters",
    "state-of-ai-agent-memory-2026", "state-of-open-source-memory-2026",
    "embedding-models-compared", "voice-ai-latency-gemini-benchmark",
    "kv-cache-eviction-accuracy",
)
UNBACKED_LINK = re.compile(r"\[([^\]]+)\]\(/articles/(" + "|".join(UNBACKED) + r")/?\)")


# Inline code is quoted, not asserted. `I ran the checker` inside backticks is a command
# a reader types, not a claim Ninad makes about having run it. Stripping code spans before
# first-person detection was one of two refinements the reviewer identified after
# classifying 118 candidates by hand.
INLINE_CODE = re.compile(r"`[^`]*`")


def classify(line: str) -> list[str]:
    """Why this line was flagged. Multiple reasons are common and useful."""
    line = INLINE_CODE.sub(" ", line)
    reasons = []
    person = bool(FIRST_PERSON_ACTION.search(line))
    measured = bool(MEASUREMENT.search(line))
    kit = bool(NAMED_KIT.search(line))

    if person and measured:
        reasons.append("first-person measurement")
    elif person and kit:
        reasons.append("first-person on named hardware or model")
    elif person:
        reasons.append("first-person action")
    if measured and kit and not person:
        reasons.append("bare measurement on named kit")
    if UNBACKED_LINK.search(line):
        reasons.append("cites an article with no reproducible artifact")
    return reasons


def _is_navigation(line: str) -> bool:
    """Lines that match syntactically but assert nothing.

    A reviewer classified 36 of 118 candidates as false positives, and they clustered into
    three shapes. Markdown headings like "What I Found Works" are editorial navigation, not
    evidence of a test event. FAQ questions like "Can I run this locally?" are questions,
    not claims. And a bullet in a reading list points at further reading rather than
    offering it as proof.
    """
    stripped = line.strip()
    if stripped.startswith("#"):
        return True
    if stripped.endswith("?"):
        return True
    # A bold-only line ending in a question mark is an FAQ heading in this house style.
    # Its ANSWER is a separate line and still gets scanned, which is the point: the
    # question asserts nothing, the answer might.
    if re.match(r"^\*\*[^*]+\?\*\*:?$", stripped):
        return True
    # A list item whose whole content is a link and a short gloss is a reading pointer.
    if re.match(r"^[-*+]\s*\[[^\]]+\]\([^)]+\)\s*[:\u2014-]?\s*.{0,90}$", stripped):
        return True
    return False


def scan(path: pathlib.Path):
    data = frontmatter.load(path)
    if data.get("status") != "published":
        return None
    hits = []
    in_fence = False
    for number, line in enumerate(data.content.splitlines(), start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _is_navigation(line):
            continue
        reasons = classify(line)
        if reasons:
            hits.append((number, reasons, re.sub(r"\s+", " ", line).strip()))
    return {
        "slug": data.get("slug") or path.stem,
        "cluster": data.get("category") or "(none)",
        "hits": hits,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slug")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--paths", nargs="*", default=None,
                    help="restrict to these post files, for a CI regression check")
    args = ap.parse_args()

    # `--paths` with no values means "no posts", not "every post". Falling through to a
    # full scan there would make a CI regression check silently compare the whole site
    # against one file and report a number that means nothing.
    if args.paths is not None:
        candidates = [pathlib.Path(x) for x in args.paths if x.endswith(".md")]
    else:
        candidates = sorted(POSTS.glob("*.md"))
    reports = [r for r in (scan(p) for p in candidates if p.exists()) if r]
    if args.slug:
        reports = [r for r in reports if r["slug"] == args.slug]

    flagged = [r for r in reports if r["hits"]]
    total = sum(len(r["hits"]) for r in flagged)

    if args.count:
        print(f"{'hits':>5}  {'cluster':<26} slug")
        for r in sorted(flagged, key=lambda r: -len(r["hits"])):
            print(f"{len(r['hits']):>5}  {r['cluster']:<26} {r['slug']}")
        print(f"\n{total} candidate claim(s) across {len(flagged)} of {len(reports)} published posts")
        return 0

    for r in sorted(flagged, key=lambda r: -len(r["hits"])):
        print(f"\n## [{r['cluster']}] {r['slug']}  ({len(r['hits'])})")
        for number, reasons, line in r["hits"]:
            print(f"  L{number} [{', '.join(reasons)}]")
            print(f"      {line[:160]}")
    print(f"\n{total} candidate claim(s) across {len(flagged)} of {len(reports)} published posts")
    print("Every hit is a candidate, not a verdict. A reviewer classifies each one")
    print("KEEP (earned judgment), REWRITE (sound point, wrong attribution) or CUT.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
