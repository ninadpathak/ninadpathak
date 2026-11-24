"""Summaries over events."""
import timeutil


def seconds_between(first, second):
    delta = timeutil.parse_ts(second) - timeutil.parse_ts(first)
    return int(delta.total_seconds())
