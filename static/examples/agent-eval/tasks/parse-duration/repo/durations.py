"""Duration helpers."""


def format_duration(seconds):
    """Format a number of seconds as '1h30m15s', leaving out zero parts."""
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    parts = [(hours, "h"), (minutes, "m"), (secs, "s")]
    return "".join(f"{value}{unit}" for value, unit in parts if value) or "0s"
