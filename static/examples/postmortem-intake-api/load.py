#!/usr/bin/env python3
"""Send steady traffic to intake and log what each request got back.

Four threads send about ten requests a second in total: four writes for every read.
One line per request goes to stdout: time, method, path, status, latency, detail.
"""
from datetime import datetime, timezone
import json
import os
import random
import string
import threading
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:" + os.environ.get("INTAKE_PORT", "8471")
THREADS = 4
PAUSE = 0.4          # seconds between requests in each thread
LOCK = threading.Lock()


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def one_request(rng, worker):
    if rng.random() < 0.8:
        method, path = "POST", "/events"
        payload = "".join(rng.choices(string.ascii_letters + " ", k=900))
        body = json.dumps({"source": f"worker-{worker}", "payload": payload}).encode()
        request = urllib.request.Request(BASE + path, data=body, method="POST",
                                         headers={"Content-Type": "application/json"})
    else:
        method, path, request = "GET", "/events/latest", urllib.request.Request(BASE + "/events/latest")
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            status, detail = response.status, ""
            response.read()
    except urllib.error.HTTPError as exc:
        status, detail = exc.code, exc.read().decode(errors="replace").strip()
    except Exception as exc:  # connection refused, reset, timeout
        status, detail = "ERR", f"{type(exc).__name__}: {exc}"
    took = int((time.monotonic() - started) * 1000)
    with LOCK:
        print(f"{utc_now()} {method} {path} {status} {took}ms {detail}".rstrip(), flush=True)


def worker(number):
    rng = random.Random(number)
    while True:
        one_request(rng, number)
        time.sleep(PAUSE)


for n in range(THREADS):
    threading.Thread(target=worker, args=(n,), daemon=True).start()
while True:
    time.sleep(1)
