#!/usr/bin/env python3
"""Check that every double-quoted phrase in a post traces to sources.json.

    python check_post_quotes.py content/posts/<slug>.md ...

A phrase of three or more words inside straight double quotes must be a substring of a
quote recorded in sources.json, or be listed under own_phrases for that slug (the post's
own illustrative wording, which is not attributed to anyone). Anything else fails.
Pair it with verify_quotes.py, which checks the recorded quotes against the live pages.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).parent


def norm(s):
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"')):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def main():
    data = json.loads((HERE / "sources.json").read_text())
    recorded = [norm(q) for s in data["sources"] for q in s["quotes"]]
    failures = 0
    total = 0
    for name in sys.argv[1:]:
        path = pathlib.Path(name)
        own = [norm(p) for p in data.get("own_phrases", {}).get(path.stem, [])]
        body = path.read_text().split("---", 2)[2]
        body = re.sub(r"```.*?```", " ", body, flags=re.S)
        body = re.sub(r"<[^>]+>", " ", body)
        body = re.sub(r"\]\([^)]*\)", "]", body)
        found = 0
        for line in body.splitlines():
            if line.lstrip().startswith(">"):
                phrases = [line.lstrip("> ").strip()] if len(line.split()) > 3 else []
            else:
                phrases = re.findall(r'"([^"\n]+)"', line)
            for phrase in phrases:
                phrase = norm(phrase)
                if len(phrase.split()) < 3:
                    continue
                found += 1
                nested = phrase.replace('"', "")
                if any(phrase in q or nested in q.replace('"', "") for q in recorded):
                    continue
                if phrase in own:
                    continue
                print(f"UNTRACED {path.stem}: {phrase}")
                failures += 1
        print(f"{path.stem}: {found} quoted phrases checked")
        total += 1
    if not total:
        print("FAIL: no post was given, so nothing was checked")
        return 1
    print("FAIL" if failures else "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
