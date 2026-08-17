#!/bin/bash
# Daily campaign job, run by launchd via tools/launchd/com.ninadpathak.daily-cycle.plist.
#
# Order matters. The URL inventory is refreshed FIRST because the guard that reads it
# needs credentials to refresh but not to check, so it cannot refresh itself in CI. Left
# unrefreshed it goes stale and then fails its own freshness gate — the guard rotting is
# the exact failure mode it exists to prevent.
#
# Then build, because tools/audit_clusters.py reads output/ for template inbound links and
# reports every page as an orphan without it. Then the cycle checks, which compare the
# fresh build against production.
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1
PY="./.venv/bin/python"
[ -x "$PY" ] || PY="python3"

echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) daily cycle ==="

# A refresh failure must not stop the checks: a stale inventory is still worth checking,
# and the guard reports its own staleness.
"$PY" tools/url_inventory.py --refresh || echo "WARN: inventory refresh failed, continuing with the committed copy"

"$PY" build.py >/dev/null 2>&1 || echo "WARN: build failed"

"$PY" tools/url_inventory.py || echo "NOTE: url_inventory reported findings"
"$PY" tools/daily_cycle.py

# The scoreboard is weekly, not daily. It is called every run with --weekly and writes
# only on its configured weekday, so the cadence lives in one place instead of being
# split between launchd and the script. A failure here must not affect the exit status of
# the daily checks above — the scoreboard reports, it does not gate.
"$PY" tools/gsc_scoreboard.py --weekly || echo "NOTE: scoreboard did not run"
