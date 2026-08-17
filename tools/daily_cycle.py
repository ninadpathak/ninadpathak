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
                "nonbrand_clicks": 0, "nonbrand_impressions": 0}
    t = total[0]

    # Search Console withholds low-volume queries, so the query dimension does not sum
    # to the sitewide total. These two figures are therefore floors taken from named
    # queries only, never a full non-brand total. Labelled as such where they print.
    brand = re.compile(r"ninad|pathak", re.IGNORECASE)
    nb_clicks = nb_impr = 0
    for row in query(["query"]):
        if not brand.search(row["keys"][0]):
            nb_clicks += row["clicks"]
            nb_impr += row["impressions"]

    return {"clicks": t["clicks"], "impressions": t["impressions"], "position": t["position"],
            "nonbrand_clicks": nb_clicks, "nonbrand_impressions": nb_impr}


def publish_gate() -> list[str]:
    """The mechanical half of the publish gate in campaign-90d.md section 8."""
    failures = []

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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    end = dt.date.today() - dt.timedelta(days=GSC_LAG_DAYS)
    start_28 = end - dt.timedelta(days=27)

    gsc = gsc_totals(start_28.isoformat(), end.isoformat())
    gate = publish_gate()
    publish = todays_publish()

    if gsc is None:
        gsc_line = "Search Console UNAVAILABLE (missing credential or google-api-python-client)"
        distance = "unknown"
    else:
        gsc_line = (f"28d to {end}: {gsc['clicks']} clicks / {gsc['impressions']} impressions, "
                    f"avg pos {gsc['position']:.1f}. Non-brand floor (named queries only, "
                    f"Search Console withholds the long tail): "
                    f"{gsc['nonbrand_clicks']} clicks / {gsc['nonbrand_impressions']} impressions")
        # The target is 10,000/month. Report the multiple still needed, never a percentage
        # of a percentage, and report it against non-brand because brand is not the campaign.
        nb = gsc["nonbrand_clicks"]
        distance = f"{10000 / nb:.0f}x away" if nb else "no non-brand clicks in any named query"

    row = (f"\n## {dt.date.today().isoformat()}\n\n"
           f"- Publish: {publish}\n"
           f"- {gsc_line}\n"
           f"- Distance to 10,000/month on non-brand clicks: **{distance}**\n"
           f"- Publish gate: {'PASS' if not gate else 'FAIL — ' + '; '.join(gate)}\n")

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
            "row's window ends three days before its date.\n",
            encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(row)

    return 1 if gate or "NO PUBLISH" in publish else 0


if __name__ == "__main__":
    sys.exit(main())
