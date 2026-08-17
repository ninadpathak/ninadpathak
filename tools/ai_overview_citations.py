#!/usr/bin/env python3
"""Report whether an AI Overview cites the pages that rank beneath it.

WHY THIS EXISTS

The campaign bet on tool-intent keywords being safe from AI Overviews. That was
falsified on 2026-08-17: three of six readable build-a-tool keywords carry an Overview
and the flagship, `ai overviews checker`, carries one reproducibly. The bet came from
keyword-tool feature flags, which were wrong on three of four rows in both directions.

So the open question is not "is there an Overview" any more. It is **does the Overview
cite the pages ranking under it, or different ones**. If it cites the same pages, ranking
still buys the citation. If it cites different ones, ranking and being cited are separate
games and the whole content plan is aimed at the wrong target.

Nobody in this niche can currently answer that, and it is answerable with automation
rather than opinion. This tool answers it for one keyword at a time and refuses to
pretend when it cannot.

THE FAILURE IT CATCHES

Publishing against a keyword whose Overview cites nobody who ranks for it. That page can
reach position 3 and still never be seen, and no existing gate on this site detects it.

ACQUISITION, settled 2026-08-17

  Semrush          presence only, SERP feature code 52. Already paid for, but MCP-only
                   in-session, so a standalone script cannot reach it. No citations.
  DataForSEO       presence AND citations AND the classic results, one request.
                   `ai_overview.references[]` gives domain, url, title, text.
                   ~$0.004 per keyword per check.
  Scraping Google  REFUSED. It would get the box blocked, and the box runs six other
                   businesses. Not implemented, and must not be.

DataForSEO is the only route that answers the question. It needs an account, which is a
purchase and therefore Ninad's to make. Until `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD`
exist this tool runs in --dry-run and reports exactly what it would cost.

USAGE

    python3 tools/ai_overview_citations.py --keyword "docs as code" \
        --decision "whether row 31 targets a keyword whose Overview cites its rankers"

    python3 tools/ai_overview_citations.py --file planning/aio-watchlist.txt --strict

`--decision` is required and free text. A paid call is not spent until the caller can name
the decision it changes; "interesting to know" is not a decision. That rule was standing
policy and is enforced here rather than remembered.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "planning" / "research-cache" / "aio"
CALL_LOG = ROOT / "planning" / "research-cache" / "CALL-LOG.md"
ENDPOINT = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
COST_PER_CALL_USD = 0.004


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def credentials() -> tuple[str, str] | None:
    login = os.environ.get("DATAFORSEO_LOGIN")
    password = os.environ.get("DATAFORSEO_PASSWORD")
    return (login, password) if login and password else None


def cache_path(keyword: str, location: str) -> Path:
    def slug(value: str) -> str:
        return re.sub(r"-+", "-", "".join(
            c if c.isalnum() else "-" for c in value.lower()
        )).strip("-") or "empty"

    # The readable slug is not an identity: ``llms.txt`` and ``llms txt`` both
    # collapse to ``llms-txt``. Keep a short digest so one keyword can never read
    # another keyword's paid response from cache.
    identity = f"{keyword}\0{location}".encode("utf-8")
    digest = hashlib.sha256(identity).hexdigest()[:10]
    return CACHE / f"{slug(keyword)}--{slug(location)}--{digest}.json"


def normalized_page(url: str | None) -> str | None:
    """Return a scheme/query/fragment-independent page identity.

    DataForSEO can return a tracking query on a citation while the organic result
    uses the clean URL. Those are the same page. Two different paths on the same
    host are not the same page, which is the distinction this instrument exists to
    measure.
    """
    if not url or not isinstance(url, str):
        return None
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if not host:
        return None
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return f"{host}{path}"


def fetch(keyword: str, location: str, creds: tuple[str, str]) -> dict:
    """One paid request. Returns the raw payload; the caller caches and logs it."""
    body = json.dumps([{
        "keyword": keyword,
        "location_name": location,
        "language_code": "en",
        "device": "desktop",
        "load_async_ai_overview": True,
    }]).encode()
    token = base64.b64encode(f"{creds[0]}:{creds[1]}".encode()).decode()
    request = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read())


def parse(payload: dict) -> dict:
    """Pull the three things the question needs out of a SERP payload.

    Returns organic rankers, Overview citations, and whether an Overview was present at
    all. An empty citation list with an Overview present is a real finding, not an error:
    it means the Overview cited nothing the API could attribute.
    """
    items = []
    for task in payload.get("tasks") or []:
        for result in task.get("result") or []:
            items.extend(result.get("items") or [])

    organic, citations, present = [], [], False
    for item in items:
        kind = item.get("type")
        if kind == "organic":
            url = item.get("url")
            if url:
                organic.append({"rank": item.get("rank_absolute"), "url": url,
                                "domain": item.get("domain")})
        elif kind == "ai_overview":
            present = True
            for ref in item.get("references") or []:
                if ref.get("url"):
                    citations.append({"domain": ref.get("domain"), "url": ref.get("url"),
                                      "title": ref.get("title")})
            # Some payloads nest references inside the element list instead.
            for element in item.get("items") or []:
                for ref in element.get("references") or []:
                    if ref.get("url"):
                        citations.append({"domain": ref.get("domain"), "url": ref.get("url"),
                                          "title": ref.get("title")})
    seen, deduped = set(), []
    for c in citations:
        if c["url"] not in seen:
            seen.add(c["url"])
            deduped.append(c)
    return {"overview_present": present, "organic": organic, "citations": deduped}


def overlap(parsed: dict, top_n: int = 10) -> dict:
    """Compare cited pages with top-N organic pages; domains are secondary context.

    The campaign decision is page-level. A host whose ``/tool`` ranks while its
    ``/research`` page is cited has won two different surfaces, not one overlapping
    result. Domain overlap is retained only to expose that near miss.
    """
    def is_top(result: dict) -> bool:
        try:
            rank = float(result.get("rank"))
        except (TypeError, ValueError):
            return False
        return 1 <= rank <= top_n

    top = [o for o in parsed["organic"] if is_top(o)]
    ranked_pages = {page for o in top if (page := normalized_page(o.get("url")))}
    cited_pages = {
        page for citation in parsed["citations"]
        if (page := normalized_page(citation.get("url")))
    }
    pages_in_both = ranked_pages & cited_pages
    cited_pages_only = cited_pages - ranked_pages

    ranked_domains = {o["domain"] for o in top if o.get("domain")}
    cited_domains = {c["domain"] for c in parsed["citations"] if c.get("domain")}
    domains_in_both = ranked_domains & cited_domains
    return {
        "ranked_top_n_pages": len(ranked_pages),
        "cited_pages": len(cited_pages),
        "pages_in_both": sorted(pages_in_both),
        "cited_pages_not_ranking": sorted(cited_pages_only),
        "page_overlap_pct": (
            round(100 * len(pages_in_both) / len(cited_pages), 1)
            if cited_pages else None
        ),
        "ranked_top_n_domains": len(ranked_domains),
        "cited_domains": len(cited_domains),
        "domains_in_both": sorted(domains_in_both),
        "domain_overlap_pct": (
            round(100 * len(domains_in_both) / len(cited_domains), 1)
            if cited_domains else None
        ),
    }


def log_call(keyword: str, decision: str, outcome: str, cost: float) -> None:
    CALL_LOG.parent.mkdir(parents=True, exist_ok=True)
    with CALL_LOG.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n| — | {utc_now()} | dataforseo serp/organic/live/advanced | "
            f"keyword `{keyword}` | {outcome} | ${cost:.3f} | decision: {decision} |\n"
        )


def report(keyword: str, parsed: dict, ov: dict) -> str:
    lines = [f"## {keyword}"]
    if not parsed["overview_present"]:
        lines.append("  No AI Overview. Ranking is the whole game for this keyword.")
        return "\n".join(lines)
    if not parsed["citations"]:
        lines.append("  AI Overview present, but no attributable citations returned.")
        lines.append("  That is a finding, not a failure: the Overview took the answer and "
                     "credited nobody the API could name.")
        return "\n".join(lines)
    lines.append(f"  AI Overview present. {ov['cited_pages']} cited page(s), "
                 f"{ov['ranked_top_n_pages']} organic page(s) in the top 10.")
    lines.append(f"  Page overlap: {ov['page_overlap_pct']}% of cited pages also rank.")
    if ov["pages_in_both"]:
        lines.append("  Pages ranking AND cited: " + ", ".join(ov["pages_in_both"]))
    if ov["cited_pages_not_ranking"]:
        lines.append("  Pages cited WITHOUT ranking top 10: " +
                     ", ".join(ov["cited_pages_not_ranking"]))
        lines.append("  Those are the pages winning the citation without winning the ranking. "
                     "If this pattern holds across keywords, ranking and being cited are "
                     "separate games.")
    if ov["domain_overlap_pct"] != ov["page_overlap_pct"]:
        lines.append(
            f"  Same-domain overlap is {ov['domain_overlap_pct']}%. A domain can rank one "
            "page and have a different page cited; that does not count as page overlap."
        )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keyword")
    ap.add_argument("--file", help="one keyword per line")
    ap.add_argument("--decision", help="the decision this call changes. Required to spend.")
    ap.add_argument("--location", default="United States")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any keyword could not be resolved")
    ap.add_argument("--dry-run", action="store_true",
                    help="cost the run and touch no paid endpoint")
    args = ap.parse_args()

    # Refuse on missing inputs rather than reporting on nothing.
    keywords: list[str] = []
    if args.keyword:
        keywords.append(args.keyword.strip())
    if args.file:
        path = Path(args.file)
        if not path.is_file():
            print(f"REFUSING: --file {args.file} does not exist.")
            return 1
        keywords += [l.strip() for l in path.read_text(encoding="utf-8").splitlines()
                     if l.strip() and not l.startswith("#")]
    keywords = list(dict.fromkeys(keywords))
    if not keywords:
        print("REFUSING: no keywords. Pass --keyword or --file.")
        return 1

    creds = credentials()
    uncached = [k for k in keywords if not cache_path(k, args.location).is_file()]
    estimate = len(uncached) * COST_PER_CALL_USD

    if args.dry_run or not creds:
        if not creds:
            print("NO CREDENTIALS: DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD are not set.")
            print("  DataForSEO is the only route that returns AI Overview citations.")
            print("  Semrush gives presence only (SERP feature code 52) and is MCP-only here.")
            print("  Scraping Google is refused: it would get the box blocked.")
            print("  Creating the account is a purchase, so it is Ninad's to make.\n")
        print(f"WOULD CHECK {len(keywords)} keyword(s); {len(uncached)} uncached at "
              f"${COST_PER_CALL_USD:.3f} each = ${estimate:.3f}")
        for k in keywords:
            cached = cache_path(k, args.location)
            print(f"  {'cached' if cached.is_file() else 'would fetch'}  {k}")
        return 0

    if uncached and not args.decision:
        print("REFUSING: --decision is required before spending. Name the decision this "
              "call changes. 'Interesting to know' is not a decision.")
        return 1

    CACHE.mkdir(parents=True, exist_ok=True)
    failures = 0
    for keyword in keywords:
        cached = cache_path(keyword, args.location)
        if cached.is_file():
            payload = json.loads(cached.read_text(encoding="utf-8"))
            spent = 0.0
            outcome = "cache hit, no spend"
        else:
            try:
                payload = fetch(keyword, args.location, creds)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                print(f"## {keyword}\n  REQUEST FAILED: {exc}")
                log_call(keyword, args.decision, f"FAILED: {exc}", COST_PER_CALL_USD)
                failures += 1
                continue
            cached.write_text(json.dumps(payload, indent=1), encoding="utf-8")
            spent = COST_PER_CALL_USD
            parsed_preview = parse(payload)
            outcome = ("empty response" if not parsed_preview["organic"]
                       else f"{len(parsed_preview['citations'])} citation(s)")
            log_call(keyword, args.decision, outcome, spent)

        parsed = parse(payload)
        if not parsed["organic"] and not parsed["overview_present"]:
            print(f"## {keyword}\n  EMPTY: no organic results and no Overview. "
                  "Logged so an empty response is never mistaken for an absent Overview.")
            failures += 1
            continue
        print(report(keyword, parsed, overlap(parsed)))

    if failures and args.strict:
        print(f"\nFAILED: {failures} keyword(s) unresolved.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
