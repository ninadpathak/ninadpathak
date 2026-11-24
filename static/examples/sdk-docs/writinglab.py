"""writinglab: a small Python client for the writing-lab example service.

The service is the local fixture in ../writing-lab/. It keeps export records in
the memory of one server process, has no authentication and listens on plain
HTTP on loopback. This module needs only the Python standard library.
"""
from __future__ import annotations

import http.client
import json
import time
import uuid
from dataclasses import dataclass
from urllib.parse import urlsplit

__version__ = "2.0.0"

__all__ = [
    "WritingLab",
    "Export",
    "State",
    "WritingLabError",
    "APIConnectionError",
    "APIStatusError",
    "InvalidKeyError",
    "InvalidFormatError",
    "KeyConflictError",
    "PayloadTooLargeError",
    "ERROR_CLASSES",
]

# Seconds to wait before the first retry. Each later retry waits twice as long.
RETRY_DELAY = 0.1


class WritingLabError(Exception):
    """Base class for every error this client raises."""


class APIConnectionError(WritingLabError):
    """No attempt received a response from the service.

    `attempts` is how many requests were sent. `idempotency_key` is the key
    those requests carried, or None for a call that sends no key.
    """

    def __init__(self, message: str, *, attempts: int, idempotency_key: str | None) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.idempotency_key = idempotency_key


class APIStatusError(WritingLabError):
    """The service answered with an error status.

    `status` is the HTTP status and `code` is the `error` field of the
    response body. Responses with no entry in ERROR_CLASSES raise this class.
    """

    def __init__(self, status: int, code: str | None) -> None:
        super().__init__(f"HTTP {status}: {code}")
        self.status = status
        self.code = code


class InvalidKeyError(APIStatusError):
    """The idempotency key is empty, over 64 characters, or has other characters."""


class InvalidFormatError(APIStatusError):
    """The format is not one the service supports."""


class KeyConflictError(APIStatusError):
    """The idempotency key was already used with a different format."""


class PayloadTooLargeError(APIStatusError):
    """The request body is over the service's 4,096-byte limit."""


# The (HTTP status, service error code) pairs this client maps to a class.
ERROR_CLASSES = {
    (400, "invalid_key"): InvalidKeyError,
    (400, "invalid_format"): InvalidFormatError,
    (409, "key_conflict"): KeyConflictError,
    (413, "body_too_large"): PayloadTooLargeError,
}


@dataclass(frozen=True)
class Export:
    """An export record stored by the service."""

    id: str
    format: str
    status: str
    replayed: bool


@dataclass(frozen=True)
class State:
    """How many records the running service instance holds."""

    exports: int
    events: int


class WritingLab:
    """A client for one running writing-lab service."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 5.0,
        max_retries: int = 2,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        parts = urlsplit(base_url)
        if parts.scheme != "http" or not parts.hostname:
            raise ValueError(f"base_url must be an http:// URL, got {base_url!r}")
        self._host = parts.hostname
        self._port = parts.port or 80
        self.timeout = timeout
        self.max_retries = max_retries
        self.default_headers = dict(default_headers or {})

    def create_export(self, format: str, *, idempotency_key: str | None = None) -> Export:
        """Store an export record and return it.

        Every attempt of one call sends the same key and the same body, so a
        retry after a lost response returns the stored record.
        """
        key = uuid.uuid4().hex if idempotency_key is None else idempotency_key
        status, data = self._request(
            "POST",
            "/exports",
            body=json.dumps({"format": format}),
            headers={"Content-Type": "application/json", "Idempotency-Key": key},
            idempotency_key=key,
        )
        return Export(
            id=data["id"],
            format=data["format"],
            status=data["status"],
            replayed=status == 200,
        )

    def get_state(self) -> State:
        """Return the record counts of the running service instance."""
        _, data = self._request("GET", "/state")
        return State(exports=data["exports"], events=data["events"])

    def _request(self, method, path, *, body=None, headers=None, idempotency_key=None):
        merged = dict(self.default_headers)
        merged.update(headers or {})
        attempts = self.max_retries + 1
        last_error = None
        for attempt in range(1, attempts + 1):
            connection = http.client.HTTPConnection(self._host, self._port, timeout=self.timeout)
            try:
                connection.request(method, path, body=body, headers=merged)
                response = connection.getresponse()
                status = response.status
                raw = response.read()
            except (OSError, http.client.HTTPException) as error:
                # No response arrived: refused, reset, closed early or timed out.
                last_error = error
                if attempt < attempts:
                    time.sleep(RETRY_DELAY * 2 ** (attempt - 1))
                continue
            finally:
                connection.close()
            try:
                data = json.loads(raw)
            except ValueError:
                data = None
            if status in (200, 202) and isinstance(data, dict):
                return status, data
            # An error response is never retried: the same request gets the same answer.
            code = data.get("error") if isinstance(data, dict) else None
            raise ERROR_CLASSES.get((status, code), APIStatusError)(status, code)
        raise APIConnectionError(
            f"no response from {self._host}:{self._port} after {attempts} attempt(s): {last_error!r}",
            attempts=attempts,
            idempotency_key=idempotency_key,
        )
