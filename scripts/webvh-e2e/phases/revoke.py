"""Revoke-related phases."""

from __future__ import annotations

import logging

from context import Context

LOG = logging.getLogger("webvh-e2e")


def phase_revoke_webvh(_ctx: Context) -> bool:
    LOG.info("revoke-webvh phase is not implemented yet.")
    return True

