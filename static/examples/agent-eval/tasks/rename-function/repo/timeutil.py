"""Timestamp helpers."""
from datetime import datetime, timezone


def parse_ts(text):
    """Parse an ISO 8601 timestamp and return an aware datetime in UTC."""
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
