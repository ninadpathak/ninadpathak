#!/usr/bin/env python3
"""Guard against silently 404ing a URL that Search Console still sends traffic to.

WHY THIS EXISTS

The March 2026 rebuild dropped the entire previous site with no redirects. In mid-2025
this domain earned roughly 6,000 impressions and 26 clicks a month across about 30 URLs —
more real clicks than it earns today — and every one of those URLs 404s now. The top page,
/guides/css-grid-layouts-webflow-table/, took 65 clicks and 5,374 impressions in four
months at position 21.

That traffic is gone and is not coming back: those URLs have had zero impressions for
twelve weeks, so Google has dropped them. It is written off in the allowlist, with the
evidence, rather than pretended away.

The loss is not the finding. The finding is that nothing prevented it, and it nearly
happened twice more in one month: the July refocus 404ed 68 pages carrying 86% of
impressions, and the glossary sat dead for weeks with 24 indexed URLs behind one line of
config. Each time the only thing that caught it was somebody happening to look.

This is the thing that looks.

    tools/url_inventory.py                  # check, offline, no credentials
    tools/url_inventory.py --refresh        # pull Search Console, rewrite the inventory
    tools/url_inventory.py --json           # machine-readable result

HOW IT DECIDES, AND WHAT EACH STATE MEANS

The inventory is committed as data so the check runs in CI with no credentials. Refreshing
it needs Search Console; checking never does.

A URL in the inventory that the build no longer produces is classified, not simply failed:

  ALARM      Dead, and still earned impressions in the last 28 days. An active leak:
             Google is still serving it and users are still landing on a 404. This is the
             expensive case and the only one that fails the build.
  WATCH      Dead, nothing in 28 days, but impressions inside 84 days. Google is dropping
             it. Reported, never fails. Recovery may still be worth it; that is a judgment
             call and this tool does not make judgment calls.
  WRITE-OFF  Dead, zero impressions in 84 days. Google has dropped it. Reported once as a
             candidate for the allowlist so the decision gets recorded, then silent.
  REDIRECTED A redirect rule covers it. Sub-classified below.
  RETIRED    On the allowlist with a stated reason. Silent.

WHY 28 AND 84 DAYS

28 days is the ALARM window because it is the window the rest of this toolchain already
uses (tools/daily_cycle.py, tools/gsc_report.py), and because Google normally stops
serving a 404 within a few weeks. Impressions after 28 days of 404 mean it is still
ranking and still leaking.

84 days is the write-off threshold because that is the evidence standard already applied
to the 2025 legacy set: zero impressions in twelve weeks was the basis for writing it off.
Using a different number here would make the allowlist's own reasoning unquotable.

Both windows end GSC_LAG_DAYS back. Search Console lags about three days; anchoring on
yesterday returns zeros and reads as a collapse.

WHAT THIS TOOL CANNOT DO

It cannot tell whether a redirect goes somewhere equivalent. `/guides/foo/` -> `/articles/`
is a soft 404 that Google treats as a redirect to an unrelated page, and
`/guides/foo/` -> `/articles/foo/` is a genuine move, and nothing mechanical separates
them. So redirects are reported with their target and a flag when the target looks like a
bare listing page, and the reader decides. Reporting beats blocking wherever the tool
would have to guess.

It also cannot see traffic Search Console withholds. Low-volume queries and pages are
suppressed, so every impression count here is a floor, never a total.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "sc-domain:ninadpathak.com"
ORIGIN = "https://ninadpathak.com"
CRED_DEFAULT = pathlib.Path(
    "/Users/ninad/Development/.google-service-account/google-workspace-service-account.json"
)

INVENTORY = ROOT / "planning" / "url-inventory.json"
ALLOWLIST = ROOT / "planning" / "url-inventory-allowlist.yaml"
OUTPUT = ROOT / "output"
# Cloudflare serves the BUILT redirects file, not the source one. build.py generates the
# /blog/ -> /articles/ rules at build time, so static/_redirects holds 25 hand-written
# rules while output/_redirects holds 208. Reading the source file reported 65 live leaks
# that were all correctly redirected. Always check the artifact that ships.
REDIRECTS_BUILT = ROOT / "output" / "_redirects"
REDIRECTS_SOURCE = ROOT / "static" / "_redirects"

# Inherited from tools/daily_cycle.py, and load-bearing for the same reason.
GSC_LAG_DAYS = 3
ALARM_DAYS = 28
WATCH_DAYS = 84
# Search Console retains 16 months. Asking for more returns the same data with a
# misleading span, so the span is recorded as what was requested AND what came back.
MAX_HISTORY_DAYS = 16 * 30

# An inventory nobody refreshes is the failure mode this tool exists to prevent, so its
# own staleness is a reported condition rather than something to notice later.
STALE_WARN_DAYS = 14
STALE_FAIL_DAYS = 45

# Redirect targets that are almost never a genuine equivalent for a specific article.
# Google treats a redirect to an unrelated page as a soft 404.
LISTING_TARGETS = {"/", "/articles/", "/blog/", "/guides/", "/glossary/", "/work/",
                   "/projects/", "/portfolio/"}


def _norm(path: str) -> str:
    """Strip origin, query and fragment. Deliberately does NOT touch the trailing slash.

    An earlier version appended one to every extension-less path, which stopped
    /static/visuals/agent-taxonomy matching the agent-taxonomy.html the build produces and
    reported twelve live pages as leaks. Slash variants are handled at match time by
    _variants instead, because Cloudflare treats them as the same resource and this tool
    should too.
    """
    if path.startswith("http://") or path.startswith("https://"):
        path = urllib.parse.urlsplit(path).path
    path = path.split("?", 1)[0].split("#", 1)[0]
    if not path.startswith("/"):
        path = "/" + path
    return path or "/"


def _variants(path: str) -> set:
    """Every form under which Cloudflare Pages will serve the same resource.

    Verified against production 2026-08-17: /static/visuals/agent-taxonomy returns 200,
    and both /static/visuals/agent-taxonomy/ and .../agent-taxonomy.html return 308 to it.
    A 308 to a live page is not a leak, so all three forms count as alive.
    """
    path = _norm(path)
    out = {path}
    if path != "/":
        out.add(path.rstrip("/"))
        out.add(path.rstrip("/") + "/")
    if path.endswith(".html"):
        stem = path[: -len(".html")]
        out.update({stem, stem + "/"})
    return {v for v in out if v}


# ---------------------------------------------------------------------------
# Refresh: the only part that needs credentials
# ---------------------------------------------------------------------------

def _service():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        return None
    cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or str(CRED_DEFAULT)
    if not pathlib.Path(cred).exists():
        return None
    creds = service_account.Credentials.from_service_account_file(
        cred, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def _pages(svc, start: str, end: str) -> dict:
    """All pages with impressions in a window, paginated. Returns path -> row."""
    out = {}
    start_row = 0
    while True:
        body = {"startDate": start, "endDate": end, "dimensions": ["page"],
                "rowLimit": 25000, "startRow": start_row}
        rows = svc.searchanalytics().query(siteUrl=SITE, body=body).execute().get("rows", [])
        if not rows:
            break
        for row in rows:
            path = _norm(row["keys"][0])
            slot = out.setdefault(path, {"clicks": 0, "impressions": 0})
            slot["clicks"] += row.get("clicks", 0)
            slot["impressions"] += row.get("impressions", 0)
        if len(rows) < 25000:
            break
        start_row += len(rows)
    return out


def _earliest_date(svc, end: str) -> str:
    """The first date Search Console actually holds data for.

    Recorded so the inventory's span is a measurement rather than an assumption. The
    request span and the returned span are both written to the file; when they differ,
    the difference is the honest answer about how far back the record goes.
    """
    start = (dt.date.fromisoformat(end) - dt.timedelta(days=MAX_HISTORY_DAYS)).isoformat()
    body = {"startDate": start, "endDate": end, "dimensions": ["date"], "rowLimit": 1}
    rows = svc.searchanalytics().query(siteUrl=SITE, body=body).execute().get("rows", [])
    return rows[0]["keys"][0] if rows else end


def refresh() -> int:
    svc = _service()
    if svc is None:
        print("REFRESH FAILED: no Search Console credential or google-api-python-client.",
              file=sys.stderr)
        print("The committed inventory is unchanged. Checking still works offline.",
              file=sys.stderr)
        return 2

    end = (dt.date.today() - dt.timedelta(days=GSC_LAG_DAYS))
    requested_start = end - dt.timedelta(days=MAX_HISTORY_DAYS)
    earliest = _earliest_date(svc, end.isoformat())

    total = _pages(svc, earliest, end.isoformat())
    watch = _pages(svc, (end - dt.timedelta(days=WATCH_DAYS - 1)).isoformat(), end.isoformat())
    alarm = _pages(svc, (end - dt.timedelta(days=ALARM_DAYS - 1)).isoformat(), end.isoformat())

    urls = []
    for path in sorted(total):
        urls.append({
            "path": path,
            "clicks_total": total[path]["clicks"],
            "impressions_total": total[path]["impressions"],
            "impressions_watch": watch.get(path, {}).get("impressions", 0),
            "impressions_alarm": alarm.get(path, {}).get("impressions", 0),
            "clicks_alarm": alarm.get(path, {}).get("clicks", 0),
        })

    payload = {
        "refreshed": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "site": SITE,
        "span": {
            "requested_start": requested_start.isoformat(),
            "earliest_with_data": earliest,
            "end": end.isoformat(),
            "note": "end is GSC_LAG_DAYS back; Search Console lags about three days.",
        },
        "windows": {
            "gsc_lag_days": GSC_LAG_DAYS,
            "alarm_days": ALARM_DAYS,
            "watch_days": WATCH_DAYS,
        },
        "caveat": ("Impression and click counts are floors, not totals. Search Console "
                   "withholds low-volume pages and queries."),
        "url_count": len(urls),
        "urls": urls,
    }
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    INVENTORY.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"inventory refreshed: {len(urls)} URLs, {earliest} to {end.isoformat()}")
    print(f"wrote {INVENTORY.relative_to(ROOT)}")
    return 0


# ---------------------------------------------------------------------------
# Check: offline, no credentials
# ---------------------------------------------------------------------------

def load_inventory(path: pathlib.Path = None) -> dict:
    path = path or INVENTORY
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_allowlist(path: pathlib.Path = None) -> dict:
    """Recorded retirements and human-approved equivalent redirects.

    A retired URL is a recorded decision, not a silent omission, so an entry with no
    `reason` is rejected rather than honoured. Failing loudly on a reasonless write-off is
    the whole point of the file.
    """
    path = path or ALLOWLIST
    empty = {"exact": {}, "prefixes": [], "redirects": {}, "problems": []}
    if not path.exists():
        return empty
    import yaml
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    exact, prefixes, problems = {}, [], []
    for entry in data.get("retired", []) or []:
        if not isinstance(entry, dict):
            continue
        if not str(entry.get("reason", "")).strip():
            problems.append(f"allowlist entry {entry.get('path') or entry.get('prefix')} "
                            f"has no reason")
            continue
        if entry.get("path"):
            exact[_norm(entry["path"])] = entry
        elif entry.get("prefix"):
            prefixes.append((_norm(entry["prefix"]), entry))
    equivalent_redirects = {}
    for entry in data.get("equivalent_redirects", []) or []:
        if not isinstance(entry, dict):
            continue
        source = entry.get("path")
        target = entry.get("target")
        reason = str(entry.get("reason", "")).strip()
        if not source or not target or not reason:
            problems.append(
                f"equivalent redirect {source or '?'} needs path, target, and reason"
            )
            continue
        equivalent_redirects[_norm(source)] = {**entry, "target": _norm(target)}
    return {"exact": exact, "prefixes": prefixes,
            "redirects": equivalent_redirects, "problems": problems}


def _allowed_entry(path: str, allowed: dict):
    """The allowlist entry covering `path`, or None.

    A prefix matches only strictly below itself: the `/glossary/` prefix retires the
    previous site's glossary children without retiring the current /glossary/ index, which
    is live and built.
    """
    for variant in _variants(path):
        if variant in allowed.get("exact", {}):
            return allowed["exact"][variant]
    for prefix, entry in allowed.get("prefixes", []):
        base = prefix.rstrip("/") + "/"
        if path.startswith(base) and path.rstrip("/") + "/" != base:
            return entry
    return None


def load_redirects(path: pathlib.Path = None) -> dict:
    """source path -> target, from Cloudflare's _redirects. Exact sources only.

    Reads the built file by default, because that is what Cloudflare serves and because
    build.py generates most of the rules. Falls back to the source file only when there is
    no build to read, and says so, since checking the wrong file silently reports leaks
    that do not exist.

    Splat and placeholder rules are recorded separately: matching them properly means
    reimplementing Cloudflare's matcher, and a half-implementation would quietly pass
    URLs it had not actually checked.
    """
    if path is None:
        path = REDIRECTS_BUILT if REDIRECTS_BUILT.exists() else REDIRECTS_SOURCE
    exact, wildcard = {}, []
    if not path.exists():
        return {"exact": exact, "wildcard": wildcard}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2 or not parts[0].startswith("/"):
            continue
        source, target = parts[0], parts[1]
        if "*" in source or ":" in source:
            wildcard.append((source, target))
        else:
            exact[_norm(source)] = target
    return {"exact": exact, "wildcard": wildcard}


def built_paths(output: pathlib.Path = None) -> set:
    """Every form under which the current build's files are reachable."""
    output = output or OUTPUT
    paths = set()
    if not output.exists():
        return paths
    for html in output.rglob("index.html"):
        rel = html.relative_to(output).parent.as_posix()
        paths |= _variants("/" if rel == "." else "/" + rel + "/")
    # Non-index files are real URLs too: /llms.txt, /feed.xml, and the 120 standalone
    # visual pages Cloudflare serves extension-less.
    for other in output.rglob("*"):
        if other.is_file() and other.name != "index.html":
            paths |= _variants("/" + other.relative_to(output).as_posix())
    return paths


def inventory_age_days(inventory: dict, today: dt.date = None) -> int:
    stamp = (inventory.get("refreshed") or "").rstrip("Z")
    if not stamp:
        return 10 ** 6
    try:
        when = dt.datetime.fromisoformat(stamp).date()
    except ValueError:
        return 10 ** 6
    return ((today or dt.date.today()) - when).days


def classify(inventory: dict, built: set, redirects: dict, allowed: dict) -> dict:
    """Sort every inventoried URL into a state. Pure; no I/O, no clock."""
    alarm, watch, writeoff, redirected, soft404, retired = [], [], [], [], [], []

    for row in inventory.get("urls", []):
        path = _norm(row["path"])
        if _variants(path) & built:
            continue

        entry = _allowed_entry(path, allowed)
        if entry is not None:
            retired.append({**row, "reason": entry.get("reason", "")})
            continue

        hit = next((v for v in _variants(path) if v in redirects["exact"]), None)
        if hit:
            target = redirects["exact"][hit]
            target_norm = _norm(target) if target.startswith("/") else target
            approved = next(
                (allowed.get("redirects", {}).get(v) for v in _variants(path)
                 if allowed.get("redirects", {}).get(v)),
                None,
            )
            approved_equivalent = bool(
                approved and target.startswith("/")
                and approved.get("target") == target_norm
            )
            record = {**row, "target": target,
                      "target_is_built": bool(_variants(target_norm) & built)
                      if target.startswith("/") else True,
                      "target_is_listing": target_norm.rstrip("/") + "/" in LISTING_TARGETS,
                      "equivalence_approved": approved_equivalent}
            # A redirect to a bare listing is what Google calls a soft 404. Equivalence
            # cannot be judged mechanically, so this is reported, not failed.
            if ((record["target_is_listing"] and not approved_equivalent)
                    or not record["target_is_built"]):
                soft404.append(record)
            else:
                redirected.append(record)
            continue

        if row.get("impressions_alarm", 0) > 0:
            alarm.append(row)
        elif row.get("impressions_watch", 0) > 0:
            watch.append(row)
        else:
            writeoff.append(row)

    key = lambda r: -(r.get("impressions_total") or 0)
    return {
        "alarm": sorted(alarm, key=key),
        "watch": sorted(watch, key=key),
        "writeoff": sorted(writeoff, key=key),
        "redirected": sorted(redirected, key=key),
        "soft404": sorted(soft404, key=key),
        "retired": sorted(retired, key=key),
    }


def report(inventory: dict, result: dict, age: int) -> list:
    """Human-readable lines. Returns the lines; the caller decides the exit code."""
    lines = []
    if not inventory:
        lines.append("NO INVENTORY: planning/url-inventory.json is missing. "
                     "Run tools/url_inventory.py --refresh. Nothing is being guarded.")
        return lines

    span = inventory.get("span", {})
    lines.append(
        f"inventory: {inventory.get('url_count', 0)} URLs, "
        f"{span.get('earliest_with_data', '?')} to {span.get('end', '?')}, "
        f"refreshed {age}d ago")

    if age >= STALE_FAIL_DAYS:
        lines.append(f"INVENTORY STALE: {age}d since refresh (fail threshold "
                     f"{STALE_FAIL_DAYS}d). A guard nobody refreshes is the failure mode "
                     f"this tool exists to prevent.")
    elif age >= STALE_WARN_DAYS:
        lines.append(f"inventory ageing: {age}d since refresh (warn at {STALE_WARN_DAYS}d)")

    for problem in result.get("allowlist_problems", []):
        lines.append(f"ALLOWLIST: {problem}")

    if result["alarm"]:
        lines.append(f"ALARM: {len(result['alarm'])} dead URL(s) still earning impressions "
                     f"in the last {inventory.get('windows', {}).get('alarm_days', ALARM_DAYS)} days")
        for row in result["alarm"]:
            lines.append(f"    {row['path']} — {row['impressions_alarm']} impressions, "
                         f"{row.get('clicks_alarm', 0)} clicks in window; "
                         f"{row['impressions_total']} impressions all time")
    else:
        lines.append("no dead URL is still earning impressions")

    if result["soft404"]:
        lines.append(f"REVIEW: {len(result['soft404'])} redirect(s) may be soft 404s "
                     f"(target is a bare listing, or does not exist)")
        for row in result["soft404"]:
            why = "target not built" if not row["target_is_built"] else "target is a listing page"
            lines.append(f"    {row['path']} -> {row['target']} ({why}); "
                         f"{row['impressions_watch']} impressions in 84d")

    if result["watch"]:
        lines.append(f"watch: {len(result['watch'])} dead URL(s) with impressions in 84d "
                     f"but none in 28d — Google is dropping them")
        for row in result["watch"][:10]:
            lines.append(f"    {row['path']} — {row['impressions_watch']} impressions in 84d")

    if result["writeoff"]:
        total = sum(r["impressions_total"] for r in result["writeoff"])
        lines.append(f"write-off candidates: {len(result['writeoff'])} dead URL(s), zero "
                     f"impressions in 84d, {total} impressions all time. Google has dropped "
                     f"them. Add to planning/url-inventory-allowlist.yaml with a reason.")
        for row in result["writeoff"][:10]:
            lines.append(f"    {row['path']} — {row['impressions_total']} impressions, "
                         f"{row['clicks_total']} clicks all time")

    if result["redirected"]:
        approved = sum(1 for row in result["redirected"]
                       if row.get("equivalence_approved"))
        unreviewed = len(result["redirected"]) - approved
        lines.append(f"redirected: {len(result['redirected'])} URL(s) point at a page that "
                     f"exists; {approved} listing redirect(s) were human-approved as "
                     f"equivalent and {unreviewed} specific-page redirect(s) remain "
                     f"mechanically valid but editorially unverified.")
    if result["retired"]:
        lines.append(f"retired by decision: {len(result['retired'])} URL(s) on the allowlist")
        # An allowlist is where leaks would go to hide. A retired URL still earning
        # impressions is a deliberate 404 for live traffic, which is a legitimate choice
        # and still worth naming every time rather than absorbing into a count.
        leaking = [r for r in result["retired"] if r.get("impressions_alarm", 0) > 0]
        if leaking:
            lines.append(f"    of those, {len(leaking)} still earned impressions in the last "
                         f"{inventory.get('windows', {}).get('alarm_days', ALARM_DAYS)} days. "
                         f"Retired on purpose, so this does not fail, and it is still traffic "
                         f"landing on a 404 by choice:")
            for row in leaking:
                lines.append(f"        {row['path']} — {row['impressions_alarm']} impressions, "
                             f"{row.get('clicks_alarm', 0)} clicks in window")

    lines.append("Counts are floors. Search Console withholds low-volume pages.")
    return lines


def summary_line(outcome: dict) -> str:
    """One compact line for the daily log. The detail lives in this tool's own output.

    Deliberately leads with the only number that means act-now, and states the floor
    caveat, because a count of impressions from Search Console is never a total.
    """
    inv = outcome["inventory"]
    if not inv:
        return "NO INVENTORY committed — nothing is guarded"
    r = outcome["result"]
    parts = [f"{inv.get('url_count', 0)} URLs tracked since "
             f"{inv.get('span', {}).get('earliest_with_data', '?')}",
             f"refreshed {outcome['age_days']}d ago"]
    if r["alarm"]:
        worst = r["alarm"][0]
        parts.append(f"ALARM {len(r['alarm'])} dead and still earning "
                     f"(worst {worst['path']}, {worst['impressions_alarm']} impressions/28d)")
    else:
        parts.append("no dead URL still earning")
    if r["soft404"]:
        parts.append(f"{len(r['soft404'])} possible soft 404 redirect(s) to review")
    if r["watch"]:
        parts.append(f"{len(r['watch'])} being dropped by Google")
    if r["writeoff"]:
        parts.append(f"{len(r['writeoff'])} write-off candidate(s) awaiting a reason")
    leaking = [x for x in r["retired"] if x.get("impressions_alarm", 0) > 0]
    if leaking:
        parts.append(f"{len(leaking)} retired-on-purpose still earning")
    parts.append("impressions are floors")
    return "; ".join(parts)


def check(inventory_path=None, output_path=None, redirects_path=None,
          allowlist_path=None, today=None) -> dict:
    inventory = load_inventory(inventory_path)
    built = built_paths(output_path)
    redirects = load_redirects(redirects_path)
    allowed = load_allowlist(allowlist_path)
    result = classify(inventory, built, redirects, allowed)
    result["allowlist_problems"] = allowed.get("problems", [])
    age = inventory_age_days(inventory, today)
    failures = []
    if not inventory:
        failures.append("no URL inventory committed")
    if result["alarm"]:
        failures.append(f"{len(result['alarm'])} dead URL(s) still earning impressions")
    if result.get("allowlist_problems"):
        failures.append(f"{len(result['allowlist_problems'])} allowlist entry/entries with no reason")
    if inventory and age >= STALE_FAIL_DAYS:
        failures.append(f"URL inventory {age}d stale")
    return {"inventory": inventory, "result": result, "age_days": age,
            "failures": failures, "lines": report(inventory, result, age)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true",
                    help="pull Search Console and rewrite the committed inventory")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if args.refresh:
        return refresh()

    outcome = check()
    if args.json:
        print(json.dumps({"failures": outcome["failures"], "age_days": outcome["age_days"],
                          "counts": {k: len(v) for k, v in outcome["result"].items()}},
                         indent=1))
    else:
        for line in outcome["lines"]:
            print(line)
    return 1 if outcome["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
