#!/usr/bin/env bash
# Reference solution.
cat >> durations.py <<'PY'


def parse_duration(text):
    """Parse '1h30m15s' into seconds. Raises ValueError for anything else."""
    import re

    match = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", text.strip())
    if not match or not any(match.groups()):
        raise ValueError(f"not a duration: {text!r}")
    hours, minutes, seconds = (int(part or 0) for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds
PY
