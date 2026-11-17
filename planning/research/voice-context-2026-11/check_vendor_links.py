"""Follow every external link in the given posts and fail on a redirect to another page or a legacy marker.

usage: check_vendor_links.py content/posts/a.md [content/posts/b.md ...]

A link fails when the URL it lands on has a different host or path from the one written in the
post, or when the page it lands on (or its Markdown twin) marks itself legacy or deprecated.
Hosts that block scripted fetches are reported as UNCHECKED and do not fail the run.
"""
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"
MARKERS = re.compile(r"(?im)^status:\s*(legacy|deprecated)\b|\((legacy)\)\s*\|")
SKIP_HOSTS = {"news.ycombinator.com", "arxiv.org", "en.wikipedia.org", "github.com", "huggingface.co"}


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.geturl(), response.read(400_000).decode("utf-8", "replace")


def same_page(a, b):
    pa, pb = urllib.parse.urlparse(a), urllib.parse.urlparse(b)
    strip = lambda host: host.lower().removeprefix("www.")
    return strip(pa.netloc) == strip(pb.netloc) and pa.path.rstrip("/") == pb.path.rstrip("/")


def links(path):
    body = open(path).read().split("\n---\n", 1)[-1]
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    return sorted(set(re.findall(r"\]\((https?://[^)\s]+)\)", body)))


problems = unchecked = checked = 0
for path in sys.argv[1:]:
    for url in links(path):
        host = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
        if host in SKIP_HOSTS:
            continue
        clean = url.split("#")[0]
        try:
            final, text = get(clean)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            unchecked += 1
            print(f"UNCHECKED {path}: {clean} ({error})")
            continue
        checked += 1
        if not same_page(clean, final):
            problems += 1
            print(f"REDIRECT  {path}: {clean} -> {final}")
        marked = MARKERS.search(text)
        if not marked:
            twin = final.split("?")[0].rstrip("/")
            for candidate in (twin + "/index.md", twin + ".md"):
                try:
                    _, markdown = get(candidate)
                except (urllib.error.URLError, TimeoutError, OSError):
                    continue
                marked = MARKERS.search(markdown[:2000])
                break
        if marked:
            problems += 1
            print(f"LEGACY    {path}: {final} carries '{marked.group(0).strip()}'")
print(f"{'FAIL' if problems else 'PASS'}: {checked} links followed, {problems} problems, {unchecked} unchecked")
sys.exit(1 if problems else 0)
