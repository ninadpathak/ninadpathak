#!/usr/bin/env python3
"""Watch intake: a health probe, a 5xx-rate alert and a database-size alert.

Every 5 seconds it calls GET /health and counts the access-log lines the service
wrote since the last poll. It prints one line per poll. It prints ALERT when 5% or
more of requests returned a 5xx status in two polls in a row, or when the health
probe failed twice in a row, and RECOVERED after two clean polls. It prints
ALERT IntakeDbNearLimit once when /health reports a database file at 80% or more
of its file-size limit.
"""
from datetime import datetime, timezone
import json
import os
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:" + os.environ.get("INTAKE_PORT", "8471")
ACCESS_LOG = sys.argv[1] if len(sys.argv) > 1 else "logs/service.log"
INTERVAL = 5
THRESHOLD = 0.05
NEAR_LIMIT = 0.80


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def health():
    try:
        with urllib.request.urlopen(BASE + "/health", timeout=2) as response:
            return str(response.status), json.loads(response.read())
    except Exception as exc:
        return type(exc).__name__, {}


offset = os.path.getsize(ACCESS_LOG) if os.path.exists(ACCESS_LOG) else 0
bad_polls = down_polls = clean_polls = 0
firing = near_limit = False
while True:
    time.sleep(INTERVAL)
    probe, state = health()
    total = errors = 0
    if os.path.exists(ACCESS_LOG):
        with open(ACCESS_LOG, encoding="utf-8", errors="replace") as log:
            log.seek(offset)
            for line in log:
                parts = line.split()
                if len(parts) >= 4 and parts[1] in ("GET", "POST") and parts[2] != "/health":
                    total += 1
                    errors += parts[3].startswith("5")
            offset = log.tell()
    rate = errors / total if total else 0.0
    size, limit = state.get("db_bytes"), state.get("limit_bytes")
    used = f" db={size / limit:.0%} of limit" if size is not None and limit else ""
    print(f"{utc_now()} health={probe} requests={total} 5xx={errors} rate={rate:.0%}{used}", flush=True)
    if used and not near_limit and size / limit >= NEAR_LIMIT:
        near_limit = True
        print(f"{utc_now()} ALERT IntakeDbNearLimit: database file is {size} of {limit} bytes", flush=True)
    bad_polls = bad_polls + 1 if rate >= THRESHOLD else 0
    down_polls = down_polls + 1 if probe != "200" else 0
    unhealthy = bad_polls > 0 or down_polls > 0
    clean_polls = 0 if unhealthy else clean_polls + 1
    if not firing and bad_polls >= 2:
        firing = True
        print(f"{utc_now()} ALERT Intake5xxRate: {rate:.0%} of requests returned 5xx for two polls", flush=True)
    elif not firing and down_polls >= 2:
        firing = True
        print(f"{utc_now()} ALERT IntakeHealthDown: /health gave {probe} for two polls", flush=True)
    elif firing and clean_polls >= 2:
        firing = False
        print(f"{utc_now()} RECOVERED: two clean polls", flush=True)
