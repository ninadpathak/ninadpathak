#!/usr/bin/env python3
"""Refetch every source in sources.json and check each quote is on the page.

    python verify_quotes.py            # all sources
    python verify_quotes.py <id> ...   # some

Comparison ignores HTML tags, runs of whitespace and curly versus straight quotes,
and nothing else. Inline tags such as <code> are removed without adding a space. A fetch failure or a missing quote exits non-zero, so a PASS means
every quote was found in a page fetched during this run.
"""
import datetime, gzip, html, json, pathlib, re, subprocess, sys, threading, time, urllib.request

HERE = pathlib.Path(__file__).parent
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")


RETRY_PAUSE_SECONDS = 20
FETCH_DEADLINE_SECONDS = 180
MAX_UNVERIFIED_DAYS = 30


def norm(s):
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?i)</?(?:code|em|strong|a|span|i|b|u|mark|sup|sub)\b[^>]*>", "", s)
    s = re.sub(r"<[^>]+>", " ", s)
    for _ in range(2):
        s = html.unescape(s)
    s = s.replace("\\u003c", "<").replace("\\u003e", ">").replace('\\"', '"')
    # JSON API bodies escape non-ASCII characters, so a curly apostrophe arrives as \\u2019.
    s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), (" ", " ")):
        s = s.replace(a, b)
    # Second pass for markup that was escaped in the source (API JSON). Only strip things
    # shaped like tags: a bare "<" in prose, as in "A <-> B ... x > y", must not swallow text.
    s = re.sub(r"</?[a-zA-Z][^<>]*>", " ", s)
    return re.sub(r"\s+", " ", s)


def fetch(url):
    # Some servers send compressed bytes whether or not they were asked for. Asking for gzip
    # and decompressing it keeps the body readable; any other encoding still fails the
    # quote check, because the text will not be found.
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*",
                                               "Accept-Encoding": "gzip",
                                               # Stripe serves British or American spelling by region.
                                               "Accept-Language": "en-US"})
    for attempt in range(3):
        try:
            data = urllib.request.urlopen(req, timeout=60).read()
            break
        except Exception as error:  # retried, then reported as a failure
            last = error
    else:
        raise last
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    if data[:5] == b"%PDF-":
        # A PDF is converted with pdftotext. If the tool is missing this raises, and the
        # source is reported as a fetch failure rather than passed unread.
        # Reading order suits prose and -layout keeps table rows together, so a quote may
        # match in either rendering.
        plain = subprocess.run(["pdftotext", "-", "-"], input=data, capture_output=True, check=True).stdout
        layout = subprocess.run(["pdftotext", "-layout", "-", "-"], input=data, capture_output=True, check=True).stdout
        return (plain + b"\n" + layout).decode("utf-8", "replace")
    return data.decode("utf-8", "replace")


def fetch_with_deadline(url):
    """Fetch in a worker thread and give up after FETCH_DEADLINE_SECONDS.

    The socket timeout covers each read, so a host that sends a few bytes at a time can
    hold a fetch open for an hour. The deadline turns that into an ordinary fetch failure.
    """
    result = {}

    def work():
        try:
            result["page"] = fetch(url)
        except Exception as error:  # reported by the caller
            result["error"] = error

    worker = threading.Thread(target=work, daemon=True)
    worker.start()
    worker.join(FETCH_DEADLINE_SECONDS)
    if worker.is_alive():
        raise TimeoutError(f"no complete response within {FETCH_DEADLINE_SECONDS} seconds")
    if "error" in result:
        raise result["error"]
    return result["page"]


def check_source(source):
    """Return the problem lines for one source: a fetch failure or each missing quote."""
    try:
        page = norm(fetch_with_deadline(source["url"]))
    except Exception as error:
        return [f"FETCH FAIL {source['id']}: {error}"]
    return [f"MISSING {source['id']}: {quote}" for quote in source["quotes"]
            if norm(quote).strip() not in page]


def main():
    wanted = set(sys.argv[1:])
    failures = 0
    checked = 0
    unverified = 0
    seen = set()
    for source in json.loads((HERE / "sources.json").read_text())["sources"]:
        if wanted and source["id"] not in wanted:
            continue
        seen.add(source["id"])
        # A host that refuses or serves a challenge page on one request often answers the
        # next one, so a source with any problem is fetched once more after a pause, and
        # only the second result is reported.
        problems = check_source(source)
        if problems:
            time.sleep(RETRY_PAUSE_SECONDS)
            problems = check_source(source)
        # A source marked refuses_automated_fetch sits behind a host that answers scripts
        # with an error. A refused fetch for such a source is reported as unverified, with
        # the date its quotes were last confirmed, and fails only once that date is more
        # than MAX_UNVERIFIED_DAYS old. A reachable page with a missing quote still fails.
        if (problems and problems[0].startswith("FETCH FAIL") and source.get("refuses_automated_fetch")
                and source.get("last_confirmed")):
            age = (datetime.date.today() - datetime.date.fromisoformat(source["last_confirmed"])).days
            if age <= MAX_UNVERIFIED_DAYS:
                reason = problems[0].split(": ", 1)[1]
                print(f"UNVERIFIED {source['id']}: fetch failed ({reason}), last confirmed {source['last_confirmed']}")
                unverified += 1
                continue
            problems = [f"STALE {source['id']}: the fetch failed and the last confirmation, "
                        f"{source['last_confirmed']}, is {age} days old"]
        checked += len(source["quotes"])
        for line in problems:
            print(line)
        failures += len(problems)
    for missing in sorted(wanted - seen):
        print(f"UNKNOWN SOURCE {missing}")
        failures += 1
    if not checked and not unverified:
        print("FAIL: 0 quotes checked")
        return 1
    print(f"{'FAIL' if failures else 'PASS'}: {checked} quotes checked, {failures} problems, "
          f"{unverified} sources unverified")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
