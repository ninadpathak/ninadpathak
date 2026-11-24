#!/usr/bin/env bash
# Pass when parse_duration() returns the right seconds for every accepted form the prompt lists,
# raises ValueError for every rejected form it lists, and the existing suite still passes.
# These assertions are held out: the agent sees the prompt, never this file.
work=$1
cd "$work" || exit 1
out=$(python3 - <<'PY' 2>&1
from durations import parse_duration

accepted = {"90s": 90, "15m": 900, "2h": 7200, "1h30m": 5400, "1h30m15s": 5415, " 5m ": 300}
for text, seconds in accepted.items():
    got = parse_duration(text)
    assert got == seconds and isinstance(got, int), f"{text!r} returned {got!r}"
for text in ["", "30", "1m1h", "1h1h", "1.5h", "-5m", "1h 30m"]:
    try:
        got = parse_duration(text)
    except ValueError:
        continue
    raise AssertionError(f"{text!r} returned {got!r}, expected ValueError")
PY
)
if [ $? -ne 0 ]; then
  echo "FAIL: held-out assertion: $(echo "$out" | tail -1)"; exit 1
fi
if ! python3 -m unittest -q >/dev/null 2>&1; then
  echo "FAIL: python3 -m unittest does not pass"; exit 1
fi
echo "PASS"
