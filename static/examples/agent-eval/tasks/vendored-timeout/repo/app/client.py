"""Fetch a URL with our defaults."""
from app import config
from vendor.tinyhttp import defaults, get


def fetch(url, timeout=None):
    return get(url, timeout=timeout or config.REQUEST_TIMEOUT, user_agent=defaults.USER_AGENT)
