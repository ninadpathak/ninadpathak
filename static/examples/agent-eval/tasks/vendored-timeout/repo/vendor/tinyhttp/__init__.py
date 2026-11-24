# Vendored from tinyhttp 2.1.0. Do not edit: tests/test_vendor.py checks every file here against vendor/CHECKSUMS.
from vendor.tinyhttp import defaults


def get(url, timeout=None, user_agent=None):
    """Return the request that would be sent. The real library opens a socket here."""
    return {"url": url, "timeout": timeout or defaults.REQUEST_TIMEOUT, "user_agent": user_agent or defaults.USER_AGENT}
