#!/usr/bin/env python3
"""Refetch every source in sources.json and check each quote is on the page.

    python verify_quotes.py            # all sources
    python verify_quotes.py <id> ...   # some

Comparison ignores HTML tags, runs of whitespace and curly versus straight quotes,
and nothing else. Inline tags such as <code> are removed without adding a space. A fetch failure or a missing quote exits non-zero, so a PASS means
every quote was found in a page fetched during this run.
"""
import html, json, pathlib, re, subprocess, sys, urllib.request

HERE = pathlib.Path(__file__).parent
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")


def norm(s):
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?i)</?(?:code|em|strong|a|span|i|b|u|mark|sup|sub)\b[^>]*>", "", s)
    s = re.sub(r"<[^>]+>", " ", s)
    for _ in range(2):
        s = html.unescape(s)
    s = s.replace("\\u003c", "<").replace("\\u003e", ">").replace('\\"', '"')
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), (" ", " ")):
        s = s.replace(a, b)
    # Second pass for markup that was escaped in the source (API JSON). Only strip things
    # shaped like tags: a bare "<" in prose, as in "A <-> B ... x > y", must not swallow text.
    s = re.sub(r"</?[a-zA-Z][^<>]*>", " ", s)
    return re.sub(r"\s+", " ", s)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    for attempt in range(3):
        try:
            data = urllib.request.urlopen(req, timeout=60).read()
            break
        except Exception as error:  # retried, then reported as a failure
            last = error
    else:
        raise last
    if data[:5] == b"%PDF-":
        # A PDF is converted with pdftotext. If the tool is missing this raises, and the
        # source is reported as a fetch failure rather than passed unread.
        # Reading order suits prose and -layout keeps table rows together, so a quote may
        # match in either rendering.
        plain = subprocess.run(["pdftotext", "-", "-"], input=data, capture_output=True, check=True).stdout
        layout = subprocess.run(["pdftotext", "-layout", "-", "-"], input=data, capture_output=True, check=True).stdout
        return (plain + b"\n" + layout).decode("utf-8", "replace")
    return data.decode("utf-8", "replace")


def main():
    wanted = set(sys.argv[1:])
    failures = 0
    checked = 0
    for source in json.loads((HERE / "sources.json").read_text())["sources"]:
        if wanted and source["id"] not in wanted:
            continue
        try:
            page = norm(fetch(source["url"]))
        except Exception as error:
            print(f"FETCH FAIL {source['id']}: {error}")
            failures += 1
            continue
        for quote in source["quotes"]:
            checked += 1
            if norm(quote).strip() not in page:
                print(f"MISSING {source['id']}: {quote}")
                failures += 1
    print(f"{'FAIL' if failures else 'PASS'}: {checked} quotes checked, {failures} problems")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
