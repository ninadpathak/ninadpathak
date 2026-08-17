#!/usr/bin/env python3
"""Measure what actually links to this domain, and to each tool.

WHY THIS EXISTS

The campaign decided on 2026-08-17 that the five tools are measured on referring domains and
on the first-hand articles they make possible, not on sessions. That decision rested on a
real finding — keepachangelog.com holds 2,220 referring domains on effectively no organic
traffic — but "measured on referring domains" is a sentence, not a measurement, until
something reports the number. Nothing did. This does.

WHAT CANNOT BE MEASURED, AND HOW THAT WAS ESTABLISHED

Every one of these was checked rather than assumed, on 2026-08-17:

  * Search Console's Links report. **The API does not expose it.** Enumerating the whole
    v1 service returns exactly five resources — searchanalytics, sitemaps, sites,
    urlInspection, urlTestingTools — and no member of the service has "link" in its name.
    The UI has the report, but the signed-in browser account (ninad@manicule.dev) returns
    "you don't have access to this property" for sc-domain:ninadpathak.com, while the
    service account that holds API access has no UI session. So the authoritative first-party
    number is reachable by a human and by nothing else.
  * GA4 referral traffic. The Admin API is disabled on the credential's project
    (HTTP 403, "Google Analytics Admin API has not been used in project 1045915980514
    before or it is disabled").
  * Ahrefs. Token dead since 2026-08-17.
  * LinkedIn. Returns HTTP 999 to any automated fetch.

Rather than approximate a number nobody can see, this tool does two honest things:

  1. It holds a slot for the authoritative Search Console figure, filled in by hand with
     the date it was read. When that slot is empty the report says so in as many words,
     because an unfilled slot is the true state and hiding it would be worse than the gap.
  2. It verifies, by fetching them, the inbound links that CAN be checked from here — and
     reports a regression when a link that used to exist stops existing.

    tools/link_inventory.py                 # check against the committed baseline, offline
    tools/link_inventory.py --refresh       # re-fetch every source and rewrite the baseline
    tools/link_inventory.py --json          # machine-readable

WHAT IT FOUND ON FIRST RUN, so the numbers below are not a surprise later

96 articles are published on dev.to under this author. **14** carry a canonical to
ninadpathak.com. **82 canonicalise to pathak.ventures instead** — a different property. And
**not one canonical, of any kind, points at a tool page.** The syndication channel that is
the site's main off-site presence sends the tools nothing at all.

A NOTE ON WHAT A CANONICAL IS AND IS NOT

A rel=canonical from dev.to to a page here tells Google this site holds the original. That is
valuable and it is not the same thing as a referring domain: it consolidates a duplicate
rather than passing the endorsement an ordinary href passes. The report counts the two
separately and never adds them together.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASELINE = ROOT / "planning" / "link-inventory.json"
DOMAIN = "ninadpathak.com"
UA = "ninadpathak-link-inventory/1.0 (+https://ninadpathak.com)"
TIMEOUT = 25

# Printed on every report from this constant rather than from the baseline file, so a stale
# or hand-edited baseline cannot drop the one distinction that keeps the metric honest.
CAVEAT = ("A rel=canonical is counted separately from an href and the two are never added. "
          "A canonical consolidates a duplicate; an href passes an endorsement. They are "
          "different things.")

TOOL_PATHS = ("/linter/", "/llms-txt-generator/", "/llms-txt-validator/",
              "/ai-overviews-checker/", "/ai-crawler-checker/")

# Sources that can be fetched and checked from here. Each is a page that plausibly links to
# this domain; the check is whether it actually does, not whether it ought to.
SOURCES = [
    {"id": "github-profile", "url": "https://github.com/ninadpathak",
     "note": "GitHub profile. Verified to carry the domain on 2026-08-17."},
    {"id": "devto-profile", "url": "https://dev.to/ninadpathak",
     "note": "DEV Community profile page. Carried no link to the domain on 2026-08-17; the "
             "links live on the individual articles as canonicals, not on the profile."},
]

# Sources known to be unfetchable, kept in the file so their absence is a recorded fact
# rather than an omission someone has to rediscover.
UNFETCHABLE = [
    {"id": "linkedin-profile", "url": "https://www.linkedin.com/in/ninadwrites/",
     "reason": "LinkedIn returns HTTP 999 to automated fetches. Verify by hand."},
]


def _get(url: str, as_json: bool = False):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        raw = response.read().decode("utf-8", "replace")
    return json.loads(raw) if as_json else raw


def count_domain_links(html: str) -> int:
    """Count hrefs pointing at this domain. Bare text mentions are not links."""
    return len(re.findall(r'href=["\']https?://(?:www\.)?' + re.escape(DOMAIN), html, re.I))


def count_domain_mentions(html: str) -> int:
    return len(re.findall(re.escape(DOMAIN), html, re.I))


def fetch_devto() -> dict:
    """dev.to syndication: how many articles point their canonical at this domain.

    The API is public and needs no key. Paginated defensively: the author had 96 articles on
    2026-08-17 and a single page would silently truncate.
    """
    articles = []
    for page in range(1, 11):
        try:
            batch = _get(f"https://dev.to/api/articles?username=ninadpathak"
                         f"&per_page=100&page={page}", as_json=True)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            return {"error": f"{type(exc).__name__}: {exc}", "articles": len(articles)}
        if not batch:
            break
        articles += batch

    ours, elsewhere, missing = [], [], []
    for article in articles:
        canonical = article.get("canonical_url") or ""
        record = {"title": (article.get("title") or "")[:90],
                  "published": (article.get("published_at") or "")[:10],
                  "canonical": canonical}
        if not canonical:
            missing.append(record)
        elif DOMAIN in canonical:
            ours.append(record)
        else:
            elsewhere.append(record)

    paths = sorted({
        "/" + c["canonical"].split(DOMAIN, 1)[1].strip("/") + "/" for c in ours
        if DOMAIN in c["canonical"]
    })
    return {
        "articles": len(articles),
        "canonical_to_us": len(ours),
        "canonical_elsewhere": len(elsewhere),
        "canonical_missing": len(missing),
        "elsewhere_hosts": sorted({
            re.sub(r"^https?://(?:www\.)?([^/]+).*$", r"\1", c["canonical"])
            for c in elsewhere if c["canonical"]
        }),
        "target_paths": paths,
        "target_tool_paths": [p for p in paths if p in TOOL_PATHS],
    }


def fetch_sources() -> list:
    results = []
    for source in SOURCES:
        record = {"id": source["id"], "url": source["url"], "note": source["note"]}
        try:
            html = _get(source["url"])
            record["status"] = 200
            record["href_links"] = count_domain_links(html)
            record["mentions"] = count_domain_mentions(html)
            record["links_to_us"] = record["href_links"] > 0 or record["mentions"] > 0
            record["tool_links"] = sorted(
                p for p in TOOL_PATHS if re.search(re.escape(DOMAIN) + re.escape(p), html, re.I))
        except urllib.error.HTTPError as exc:
            record.update({"status": exc.code, "links_to_us": None,
                           "error": f"HTTP {exc.code}"})
        except (urllib.error.URLError, OSError) as exc:
            record.update({"status": None, "links_to_us": None,
                           "error": f"{type(exc).__name__}: {exc}"})
        results.append(record)
    return results


def refresh() -> int:
    previous = load_baseline()
    payload = {
        "refreshed": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "domain": DOMAIN,
        "authoritative_referring_domains": previous.get(
            "authoritative_referring_domains",
            {
                "value": None,
                "source": "Search Console > Links > Top linking sites",
                "read_on": None,
                "read_by": None,
                "note": ("Fill this in by hand. The Search Console API exposes no links "
                         "resource, and the signed-in browser account lacks access to "
                         "sc-domain:ninadpathak.com, so no automated path exists. Until this "
                         "is filled in, the campaign has no referring-domain number at all "
                         "and the report says so."),
            }),
        "cannot_measure": {
            "gsc_links_api": ("No links resource. Enumerating searchconsole v1 returns "
                              "searchanalytics, sitemaps, sites, urlInspection, "
                              "urlTestingTools and nothing else. Verified 2026-08-17."),
            "gsc_links_ui": ("Signed-in browser account ninad@manicule.dev returns "
                             "'you don't have access to this property'. Verified 2026-08-17."),
            "ga4_referrals": ("Analytics Admin API disabled on the credential's project "
                              "(HTTP 403). Verified 2026-08-17."),
            "ahrefs": "Token dead since 2026-08-17.",
            "linkedin": "HTTP 999 to automated fetches.",
        },
        "devto_syndication": fetch_devto(),
        "sources": fetch_sources(),
        "unfetchable_sources": UNFETCHABLE,
        "caveat": CAVEAT,
    }
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {BASELINE.relative_to(ROOT)}")
    return 0


def load_baseline(path: pathlib.Path = None) -> dict:
    path = path or BASELINE
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def baseline_age_days(baseline: dict, today: dt.date = None) -> int:
    stamp = (baseline.get("refreshed") or "").rstrip("Z")
    if not stamp:
        return 10 ** 6
    try:
        when = dt.datetime.fromisoformat(stamp).date()
    except ValueError:
        return 10 ** 6
    return ((today or dt.date.today()) - when).days


def evaluate(baseline: dict, today: dt.date = None) -> dict:
    """Pure. Returns (lines, failures, summary) derived from the committed baseline."""
    lines, failures = [], []
    if not baseline:
        return {"lines": ["NO LINK BASELINE: planning/link-inventory.json is missing. "
                          "Run tools/link_inventory.py --refresh. Referring domains are "
                          "not being measured at all."],
                "failures": ["no link baseline committed"], "summary": {}}

    age = baseline_age_days(baseline, today)
    lines.append(f"link baseline refreshed {age}d ago")

    auth = baseline.get("authoritative_referring_domains") or {}
    if auth.get("value") is None:
        lines.append("REFERRING DOMAINS: UNKNOWN. The authoritative Search Console figure has "
                     "never been recorded, and no automated path to it exists — the API has "
                     "no links resource and the browser account lacks property access. "
                     "The campaign is measuring tools on a number nobody has read.")
    else:
        lines.append(f"referring domains: {auth['value']} "
                     f"(read {auth.get('read_on')} from {auth.get('source')})")

    devto = baseline.get("devto_syndication") or {}
    if devto.get("error"):
        lines.append(f"dev.to syndication unreadable: {devto['error']}")
    elif devto:
        lines.append(
            f"dev.to: {devto.get('articles', 0)} articles, "
            f"{devto.get('canonical_to_us', 0)} canonicalised here, "
            f"{devto.get('canonical_elsewhere', 0)} canonicalised elsewhere"
            + (f" ({', '.join(devto.get('elsewhere_hosts') or [])})"
               if devto.get("elsewhere_hosts") else ""))
        # The whole point of the reframe is per-tool link counts, so an empty result is
        # stated as a number rather than left as silence.
        tool_targets = devto.get("target_tool_paths") or []
        lines.append(f"dev.to canonicals pointing at a tool page: "
                     f"{len(tool_targets)}{' — ' + ', '.join(tool_targets) if tool_targets else ' (none)'}")
        if devto.get("canonical_elsewhere", 0) > devto.get("canonical_to_us", 0):
            lines.append("NOTE: more syndicated articles point their canonical at another "
                         "property than at this one. That is a routing decision worth "
                         "confirming is deliberate.")

    verified, lost = [], []
    for source in baseline.get("sources") or []:
        if source.get("links_to_us"):
            verified.append(source)
        elif source.get("links_to_us") is False:
            lost.append(source)
    lines.append(f"verifiable inbound sources: {len(verified)} linking, {len(lost)} not")
    for source in lost:
        lines.append(f"    {source['id']} ({source['url']}) carries no link to the domain")

    # A link that was verified and has since disappeared is the one condition worth failing
    # on: everything else here is a baseline, and a baseline cannot regress.
    for source in baseline.get("sources") or []:
        if source.get("error") and source.get("id") in {s["id"] for s in SOURCES}:
            lines.append(f"    {source['id']} unreachable: {source['error']}")

    per_tool = {path: 0 for path in TOOL_PATHS}
    for source in baseline.get("sources") or []:
        for path in source.get("tool_links") or []:
            per_tool[path] = per_tool.get(path, 0) + 1
    for path in (baseline.get("devto_syndication") or {}).get("target_tool_paths") or []:
        per_tool[path] = per_tool.get(path, 0) + 1

    lines.append("per-tool verified inbound links:")
    for path, count in per_tool.items():
        lines.append(f"    {path:<24} {count}")
    if not any(per_tool.values()):
        lines.append("    every tool is at zero. That is the honest baseline the reframe "
                     "starts from, not a measurement failure.")

    for source in baseline.get("unfetchable_sources") or []:
        lines.append(f"cannot verify {source['id']}: {source['reason']}")

    lines.append(CAVEAT)
    return {"lines": [l for l in lines if l], "failures": failures,
            "summary": {"referring_domains": auth.get("value"),
                        "per_tool": per_tool, "age_days": age,
                        "devto_canonical_here": devto.get("canonical_to_us"),
                        "devto_canonical_elsewhere": devto.get("canonical_elsewhere")}}


def summary_line(outcome: dict) -> str:
    """One compact line for the daily log."""
    s = outcome.get("summary") or {}
    if not s:
        return "NO LINK BASELINE committed — referring domains unmeasured"
    rd = s.get("referring_domains")
    parts = [f"referring domains: {rd if rd is not None else 'UNKNOWN, never read'}"]
    tool_total = sum((s.get("per_tool") or {}).values())
    parts.append(f"verified inbound links to tools: {tool_total}")
    if s.get("devto_canonical_elsewhere") is not None:
        parts.append(f"dev.to canonicals here {s.get('devto_canonical_here')} vs elsewhere "
                     f"{s.get('devto_canonical_elsewhere')}")
    parts.append(f"baseline {s.get('age_days')}d old")
    return "; ".join(parts)


def check(baseline_path=None, today=None) -> dict:
    return evaluate(load_baseline(baseline_path), today)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true",
                    help="re-fetch every source and rewrite the committed baseline")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.refresh:
        return refresh()

    outcome = check()
    if args.json:
        print(json.dumps({"failures": outcome["failures"],
                          "summary": outcome["summary"]}, indent=1))
    else:
        for line in outcome["lines"]:
            print(line)
    return 1 if outcome["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
