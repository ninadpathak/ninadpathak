#!/usr/bin/env bash
# A wrong solution: sums every number-unit pair it finds, so `1m1h` and `1h 30m` are accepted.
cat >> durations.py <<'PY'


def parse_duration(text):
    import re

    pairs = re.findall(r"(\d+)([hms])", text)
    if not pairs:
        raise ValueError(f"not a duration: {text!r}")
    return sum(int(value) * {"h": 3600, "m": 60, "s": 1}[unit] for value, unit in pairs)
PY
