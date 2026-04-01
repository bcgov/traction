"""Small polling helpers for async ACA-Py / DIDComm transitions."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

LOG = logging.getLogger("webvh-e2e")

T = TypeVar("T")


def poll_until(
    fetch: Callable[[], T | None],
    *,
    timeout_sec: float,
    interval_sec: float,
    description: str,
) -> T | None:
    """
    Call ``fetch()`` until it returns a non-None value or timeout.

    ``fetch`` should return None while waiting.
    """
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        result = fetch()
        if result is not None:
            return result
        time.sleep(interval_sec)
    LOG.error("Timeout waiting for: %s", description)
    return None
