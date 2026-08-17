#!/usr/bin/env python3
"""Deterministic daily campaign check for ninadpathak.com.

The campaign's judgment work belongs to an agent session. This does not attempt any
of it. It runs the parts that are mechanical, cannot be wrong, and are the parts most
likely to be skipped: pull Search Console, confirm the day's publish landed, run the
publish gate, and append a dated row to a log that survives the session.

Written because the director's daily cycle was a session-only cron that auto-expires
after seven days, so a 90-day campaign had no durable measurement at all. See
campaign-90d.md.

    tools/daily_cycle.py                 # check and append to planning/daily-cycle.md
    tools/daily_cycle.py --dry-run       # print, write nothing

Needs GOOGLE_APPLICATION_CREDENTIALS or the workspace service-account file, plus
google-api-python-client and google-auth.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "sc-domain:ninadpathak.com"
CRED_DEFAULT = pathlib.Path(
    "/Users/ninad/Development/.google-service-account/google-workspace-service-account.json"
)
LOG = ROOT / "planning" / "daily-cycle.md"
# Search Console lags roughly three days; asking for yesterday returns zeros and
# reads as a collapse. Anchor the window on a date that actually has data.
GSC_LAG_DAYS = 3


def run(*cmd: str, cwd: pathlib.Path = ROOT) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)


def gsc_totals(start: str, end: str) -> dict | None:
    """Sitewide clicks/impressions/position, and the non-brand split.

    Brand traffic is the whole of this site's current click volume, so a total that
    does not separate it hides whether the campaign is working.
    """
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
    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    def query(dimensions):
        body = {"startDate": start, "endDate": end, "dimensions": dimensions, "rowLimit": 2000}
        return svc.searchanalytics().query(siteUrl=SITE, body=body).execute().get("rows", [])

    total = query([])
    if not total:
        return {"clicks": 0, "impressions": 0, "position": 0.0,
                "nonbrand_clicks": 0, "nonbrand_impressions": 0,
                "human_clicks": 0, "human_impressions": 0,
                "machine_clicks": 0, "machine_impressions": 0, "named_impressions": 0}
    t = total[0]

    # Search Console withholds low-volume queries, so the query dimension does not sum
    # to the sitewide total. These two figures are therefore floors taken from named
    # queries only, never a full non-brand total. Labelled as such where they print.
    brand = re.compile(r"ninad|pathak", re.IGNORECASE)
    rows = query(["query"])
    nb_clicks = nb_impr = 0
    for row in rows:
        if not brand.search(row["keys"][0]):
            nb_clicks += row["clicks"]
            nb_impr += row["impressions"]

    # Non-brand still includes machine query fan-out, which is not a person. Over
    # 2025-04 to 2026-08 that fan-out was only 3.6% of named impressions sitewide, but
    # it was 57% of them in August 2026 and 66% of the site's entire impression growth
    # came from one page whose every identifiable query was fan-out with zero clicks.
    # A non-brand number alone therefore cannot tell whether anything shipped works.
    # See planning/gsc-human-baseline.md and gsc_report.py for the separator.
    human = machine = machine_clicks = human_clicks = 0
    named_impr = int(sum(r["impressions"] for r in rows))
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import gsc_report
        parts = gsc_report.partition_queries(rows)
        human = int(sum(r["impressions"] for r in parts["human"]))
        human_clicks = int(sum(r["clicks"] for r in parts["human"]))
        machine = int(sum(r["impressions"] for r in parts["machine"]))
        machine_clicks = int(sum(r["clicks"] for r in parts["machine"]))
    except ImportError:
        human = human_clicks = machine = machine_clicks = -1

    return {"clicks": t["clicks"], "impressions": t["impressions"], "position": t["position"],
            "nonbrand_clicks": nb_clicks, "nonbrand_impressions": nb_impr,
            "human_clicks": human_clicks, "human_impressions": human,
            "machine_clicks": machine_clicks, "machine_impressions": machine,
            "named_impressions": named_impr}


# Standing order 1 is to grow the site in Google *and* in AI search, and robots.txt here
# is Cloudflare-managed, so it can change without anyone touching the repo. The posture
# that serves a traffic goal is: block training crawlers, allow the crawlers that produce
# citations. Training ingestion earns no traffic and no attribution; citation does. These
# are the agents that must stay allowed.
CITATION_CRAWLERS = ("Googlebot", "OAI-SearchBot", "PerplexityBot",
                     "Claude-SearchBot", "Claude-User")


def robots_check() -> list[str]:
    """Confirm no citation crawler has been blocked, and that the sitemap is declared."""
    # Cloudflare varies robots.txt by User-Agent. The default `Python-urllib/x.y` UA is
    # treated as an unwanted bot and served only the managed block, without the site's
    # own `Sitemap:` line, which reads as a missing sitemap when nothing is wrong.
    # Googlebot and ordinary browsers get the full file. Identify honestly instead.
    request = urllib.request.Request(
        "https://ninadpathak.com/robots.txt",
        headers={"User-Agent": "ninadpathak-daily-cycle/1.0 (+https://ninadpathak.com)"})
    try:
        with urllib.request.urlopen(request, timeout=20) as r:
            robots = r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as exc:
        return [f"robots.txt unreachable: {exc}"]

    problems = []
    if "Sitemap:" not in robots:
        problems.append("robots.txt declares no Sitemap")

    for agent in CITATION_CRAWLERS:
        block = re.search(rf"^User-agent:\s*{re.escape(agent)}\s*$(.*?)(?=^User-agent:|\Z)",
                          robots, re.M | re.S)
        if block and re.search(r"^Disallow:\s*/\s*$", block.group(1), re.M):
            problems.append(f"{agent} is BLOCKED — this is a citation crawler")
    return problems


def foreign_urls(start: str, end: str) -> list[str]:
    """Flag URLs on this domain that belong to no version of this site.

    In September 2025 something served 398 `/products/<numeric-id>` pages plus `/shop/`,
    `/cart/` and `/jukyuban/` on ninadpathak.com, ranking for Japanese counterfeit-goods
    queries. In the same week the legitimate corpus fell from 791 impressions to 262 and
    then to 14, and it never recovered — 119 non-brand queries became one. That episode
    was only found ten months later by reading history.

    It is checked daily now because the cost of noticing late is the entire non-brand
    corpus, and because Search Console is the only place it is visible: the pages return
    404 to a direct request today, so a crawl of the live site would not have caught it.
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        return []
    cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or str(CRED_DEFAULT)
    if not pathlib.Path(cred).exists():
        return []
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import gsc_collapse_forensics as forensics
    except ImportError:
        return []

    creds = service_account.Credentials.from_service_account_file(
        cred, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    body = {"startDate": start, "endDate": end, "dimensions": ["page"], "rowLimit": 25000}
    rows = svc.searchanalytics().query(siteUrl=SITE, body=body).execute().get("rows", [])

    bad = [r for r in rows if forensics.is_foreign(r["keys"][0])]
    if not bad:
        return []
    bad.sort(key=lambda r: -r["impressions"])
    sections = sorted({forensics.section(r["keys"][0]) for r in bad})
    total = int(sum(r["impressions"] for r in bad))
    return [f"FOREIGN URLs in Search Console: {len(bad)} page(s), {total} impressions, "
            f"section(s) {', '.join(sections)} — e.g. "
            f"{urllib.parse.urlsplit(bad[0]['keys'][0]).path}. This is how the "
            f"September 2025 injection looked. Check Security Issues in the Search "
            f"Console UI."]


def shadowing_redirects() -> list[str]:
    """A redirect must never point away from a page that actually exists.

    Cloudflare's _redirects takes precedence over a static file, so a rule added while a
    URL was dead keeps firing after the page comes back and sends every visitor and
    crawler away from it. That happened to /glossary/ on 2026-08-17: it was redirected
    while 404ing at position 8.6, then republished, and the redirect would have shadowed
    it. Every recovery of a dead URL can reintroduce this, so it is checked, not
    remembered.
    """
    redirects = ROOT / "static" / "_redirects"
    output = ROOT / "output"
    if not redirects.exists() or not output.exists():
        return []

    problems = []
    for line in redirects.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        source = line.split()[0]
        if not source.startswith("/"):
            continue
        candidate = output / source.strip("/") / "index.html"
        if source != "/" and candidate.is_file():
            problems.append(f"redirect {source} shadows a real page at {candidate.relative_to(ROOT)}")
    return problems


# A commit is not a deploy, and a deploy is not a working page. On 2026-08-17 eight
# commits sat on origin/main while production kept serving an older build, and the only
# reason it was noticed was a manual spot check. These are URLs that must serve 200 for
# the site to be in the state the repo claims. Anything the repo builds but production
# does not serve is a stalled or failed deploy, which is silent by default: Cloudflare
# Pages keeps the previous deploy live when a build fails.
LIVE_URLS = (
    "/",
    "/articles/",
    "/glossary/",
    "/linter/",
    "/llms-txt-generator/",
    "/llms-txt-validator/",
    "/ai-overviews-checker/",
    "/ai-crawler-checker/",
    "/articles/ai-search-optimization/",
    "/articles/ai-engineering/",
    "/articles/technical-documentation/",
    # Added with the Distribution merge, 2026-08-17. The loop below skips any URL the
    # build does not produce, so this is inert until the first Distribution piece ships.
    "/articles/distribution/",
)


# Cloudflare Pages serialises builds, so production legitimately trails main for a few
# minutes after a push. A check that alarms instantly is worse than no check: it cried
# wolf on 2026-08-17 while a deploy was mid-flight, and the false alarm cost more time
# than the real problem would have. So the check distinguishes two states — "not deployed
# yet", which is normal and reported as WAITING, and "deployed wrong", which is an alarm.
#
# The discriminator is the age of the newest commit that changed anything the build
# renders. Inside the window a mismatch is expected; past it, production has had ample
# time and something is wrong.
DEPLOY_GRACE_SECONDS = 15 * 60


def deploy_lag_seconds() -> int | None:
    """Seconds since the newest commit that could have changed the built output.

    Documentation-only commits are excluded: a change to campaign-90d.md or a file under
    planning/ does not alter a single rendered page, so it must not start a deploy clock
    that then reports a phantom lag.
    """
    code, out = run("git", "log", "-60", "--format=%H %ct", "--name-only")
    if code != 0:
        return None

    # git prints "<sha> <unix-ts>", a blank line, then the file list, and the next
    # commit's header follows with no separating blank line. Splitting on blank lines
    # therefore runs commits together, so walk the lines and track the current commit.
    import re as _re
    import time
    header = _re.compile(r"^[0-9a-f]{40} (\d+)$")
    RENDERS_PREFIX = ("content/", "templates/", "static/", "functions/")
    RENDERS_FILE = {"build.py", "config.toml", "rule_checker.py"}

    current_ts = None
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        match = header.match(line)
        if match:
            current_ts = int(match.group(1))
            continue
        if current_ts is None:
            continue
        if line.startswith(RENDERS_PREFIX) or line in RENDERS_FILE:
            return int(time.time()) - current_ts
    return None


def deploy_check() -> list[str]:
    """Compare what the local build produces against what production actually serves.

    Returns alarms only. A mismatch inside the grace window is returned as a WAITING
    note by the caller, not as a failure, so a mid-flight deploy never reads as broken.
    """
    problems = []
    local_sitemap = ROOT / "output" / "sitemap.xml"
    local_count = None
    if local_sitemap.exists():
        local_count = local_sitemap.read_text(encoding="utf-8", errors="replace").count("<loc>")

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        """Do not follow redirects.

        Following them is what would have hidden the /glossary/ near-miss: a page the
        build produces, shadowed by a stale redirect, resolves to 200 at the redirect
        target and looks healthy. For a URL this build generates, a 3xx is a failure.
        """

        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(NoRedirect)

    def fetch(path):
        request = urllib.request.Request(
            "https://ninadpathak.com" + path,
            headers={"User-Agent": "ninadpathak-daily-cycle/1.0 (+https://ninadpathak.com)"})
        try:
            with opener.open(request, timeout=25) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as exc:
            return exc.code, b""
        except (urllib.error.URLError, OSError) as exc:
            return None, str(exc).encode()

    status, body = fetch("/sitemap.xml")
    if status != 200:
        problems.append(f"live /sitemap.xml returned {status}")
    elif local_count is not None:
        live_count = body.decode("utf-8", "replace").count("<loc>")
        if live_count != local_count:
            problems.append(
                f"DEPLOY STALE: live sitemap has {live_count} URLs, local build has "
                f"{local_count}. Production is not serving what main builds.")

    for path in LIVE_URLS:
        # Only assert on URLs this build actually produces, so the check does not fail
        # on a page that was legitimately removed.
        built = ROOT / "output" / path.strip("/") / "index.html"
        if path != "/" and not built.is_file():
            continue
        status, _ = fetch(path)
        if status != 200:
            detail = " (a redirect is shadowing a page the build generates)" if status and 300 <= status < 400 else ""
            problems.append(f"live {path} returned {status} but the build produces it{detail}")

    return problems


# Each tool page is static and will render whatever happens to the Pages Function behind
# it, so a Function that 404s is invisible from the page. That combination nearly shipped.
# The repo-side half is asserted in tests/test_tool_e2e.py; this is the production half,
# which only a live probe can answer.
TOOL_FUNCTIONS = (
    ("/llms-txt-generator/", "/api/discover-site"),
    ("/llms-txt-validator/", "/api/fetch-llms-txt"),
    ("/ai-overviews-checker/", "/api/fetch-page"),
    ("/ai-crawler-checker/", "/api/fetch-robots"),
)


def functions_check() -> list[str]:
    """Confirm every Pages Function a tool depends on still answers in production.

    A 400 or 422 is a pass: the endpoint is alive and validating its input. Only 404, 5xx
    or an unreachable host mean the tool is broken behind a page that still looks fine.
    """
    problems = []
    for page, endpoint in TOOL_FUNCTIONS:
        request = urllib.request.Request(
            "https://ninadpathak.com" + endpoint,
            data=b'{"url":"example.com"}',
            headers={"content-type": "application/json",
                     "user-agent": "ninadpathak-daily-cycle/1.0 (+https://ninadpathak.com)"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
        except urllib.error.HTTPError as exc:
            status = exc.code
        except (urllib.error.URLError, OSError) as exc:
            problems.append(f"{endpoint} unreachable ({exc}) — {page} renders without it")
            continue
        if status == 404:
            problems.append(f"{endpoint} returns 404 but {page} still renders")
        elif status >= 500:
            problems.append(f"{endpoint} returns {status} but {page} still renders")
    return problems


def url_inventory_check() -> tuple[list[str], str]:
    """Fail when the build stops producing a URL Search Console still sends traffic to.

    Returns (failures, one-line summary). The split draws the same distinction
    deploy_check draws between something to act on now and something merely worth seeing:
    a dead URL still earning impressions in the last 28 days is an active leak and fails,
    while a URL Google has already dropped is a write-off and must never fail the build
    forever, or the guard becomes another alarm people learn to ignore.

    Written because the March 2026 rebuild 404ed the entire previous site with no redirects
    and nobody noticed for five months. tools/url_inventory.py carries the full account and
    the defence of the two windows.
    """
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import url_inventory
    except ImportError as exc:
        return [f"url_inventory unavailable: {exc}"], f"unavailable: {exc}"

    outcome = url_inventory.check()
    return outcome["failures"], url_inventory.summary_line(outcome)


def publish_gate() -> list[str]:
    """The mechanical half of the publish gate in campaign-90d.md section 8."""
    failures = []
    failures += shadowing_redirects()

    python = str(ROOT / ".venv" / "bin" / "python")
    if not pathlib.Path(python).exists():
        python = sys.executable

    code, out = run(python, "build.py")
    if code != 0:
        failures.append(f"build.py exits {code}")
    broken = out.count("broken internal link")
    if broken:
        failures.append(f"{broken} broken internal link(s)")
    if "SEO audit passed" not in out:
        failures.append("SEO audit did not pass")

    # Standing order 4: no new CSS, ever.
    code, css = run("git", "diff", "--stat", "origin/main", "--", "static/css/")
    if css.strip():
        failures.append(f"CSS changed against origin/main: {css.strip().splitlines()[-1].strip()}")

    # Runs after build.py so it reads the build this gate just produced, including the
    # generated output/_redirects rather than the 25 hand-written source rules.
    url_failures, _ = url_inventory_check()
    failures += url_failures

    return failures


def todays_publish() -> str:
    run("git", "fetch", "origin", "main", "--quiet")
    _, log = run("git", "log", "origin/main", "--format=%h|%ad|%s", "--date=short", "-20")
    today = dt.date.today().isoformat()
    for line in log.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3 and parts[1] == today and "content: publish" in parts[2]:
            return f"shipped {parts[0]} {parts[2]}"
    return "NO PUBLISH FOUND on origin/main for today"


def _deploy_line(problems, waiting, lag) -> str:
    if not problems:
        return "LIVE, matches the build"
    age = "unknown age" if lag is None else f"{lag // 60}m since the last rendering commit"
    if waiting:
        return (f"WAITING, not an alarm — {age}, inside the "
                f"{DEPLOY_GRACE_SECONDS // 60}m grace window: " + "; ".join(problems))
    return f"ALARM, past the grace window — {age}: " + "; ".join(problems)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    end = dt.date.today() - dt.timedelta(days=GSC_LAG_DAYS)
    start_28 = end - dt.timedelta(days=27)

    gsc = gsc_totals(start_28.isoformat(), end.isoformat())
    gate = publish_gate()
    gate += robots_check()
    gate += foreign_urls(start_28.isoformat(), end.isoformat())
    functions = functions_check()
    deploy = deploy_check()
    _, url_summary = url_inventory_check()
    lag = deploy_lag_seconds()
    # A mismatch is only an alarm once production has had the grace window to catch up.
    deploy_waiting = bool(deploy) and lag is not None and lag < DEPLOY_GRACE_SECONDS
    publish = todays_publish()

    if gsc is None:
        gsc_lines = ["Search Console UNAVAILABLE (missing credential or "
                     "google-api-python-client)"]
        distance = "unknown"
    else:
        gsc_lines = [
            f"28d to {end}: {gsc['clicks']} clicks / {gsc['impressions']} impressions, "
            f"avg pos {gsc['position']:.1f}",
            f"Non-brand floor (named queries only, Search Console withholds the long "
            f"tail): {gsc['nonbrand_clicks']} clicks / "
            f"{gsc['nonbrand_impressions']} impressions",
        ]
        if gsc["human_impressions"] < 0:
            gsc_lines.append("Human-only UNAVAILABLE (gsc_report.py not importable)")
        else:
            gsc_lines.append(
                f"Human-only estimate (non-brand minus machine query fan-out): "
                f"{gsc['human_clicks']} clicks / {gsc['human_impressions']} impressions. "
                f"Fan-out removed: {gsc['machine_clicks']} clicks / "
                f"{gsc['machine_impressions']} impressions of "
                f"{gsc['named_impressions']} named")
            # Say exactly what this number is, in both directions, every single time.
            # A cleaner figure that loses its qualifiers becomes a worse figure than the
            # one it replaced.
            gsc_lines.append(
                "Human-only is an **estimate, not a bound**: it undercounts because the "
                "withheld long tail is excluded entirely, and overcounts because fan-out "
                "is only detected within this 28d window, so a family with fewer than "
                "three variants here still counts as human")

        # The target is 10,000/month. Report the multiple still needed, never a percentage
        # of a percentage, and report it against human because neither brand nor a bot is
        # the campaign.
        hc = gsc["human_clicks"]
        nb = gsc["nonbrand_clicks"]
        if hc > 0:
            distance = f"{10000 / hc:.0f}x away on human clicks"
        elif nb > 0:
            distance = (f"no human clicks in any named query; {nb} non-brand click(s) "
                        f"exist but are fan-out or undetected")
        else:
            distance = "no non-brand clicks in any named query"

    row = (f"\n## {dt.date.today().isoformat()}\n\n"
           f"- Publish: {publish}\n"
           + "".join(f"- {line}\n" for line in gsc_lines)
           + f"- Distance to 10,000/month: **{distance}**\n"
           f"- Publish gate: {'PASS' if not gate else 'FAIL — ' + '; '.join(gate)}\n"
           f"- Deploy: {_deploy_line(deploy, deploy_waiting, lag)}\n"
           f"- URL inventory: {url_summary}\n"
           f"- Tool Functions: {'all answering' if not functions else 'BROKEN — ' + '; '.join(functions)}\n")

    print(row)
    if args.dry_run:
        return 0

    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text(
            "# Daily cycle log\n\n"
            "Appended by `tools/daily_cycle.py`. Deterministic checks only — no judgment,\n"
            "no interpretation. This exists so the campaign keeps a measurement record even\n"
            "when no agent session is running. Search Console lags about three days, so each\n"
            "row's window ends three days before its date.\n\n"
            "Three click figures appear per row and they are not interchangeable. Sitewide\n"
            "includes brand and machine traffic. Non-brand is a floor from named queries and\n"
            "still contains machine query fan-out. Human-only removes that fan-out and is an\n"
            "estimate bounded in neither direction — it undercounts by excluding the withheld\n"
            "tail and overcounts by detecting fan-out only within each 28-day window.\n",
            encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(row)

    # Waiting is not a failure. Only alarm once the grace window has passed. A broken
    # tool Function is always a failure: it has no grace window, because the page it sits
    # behind renders regardless and gives no sign anything is wrong.
    return 1 if (gate or functions or (deploy and not deploy_waiting)
                 or "NO PUBLISH" in publish) else 0


if __name__ == "__main__":
    sys.exit(main())
