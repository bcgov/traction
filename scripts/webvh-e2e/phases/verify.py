"""Verify-related phases."""

from __future__ import annotations

import logging

from context import Context

LOG = logging.getLogger("webvh-e2e")


def _placeholder_phase(phase_name: str) -> bool:
    LOG.info("%s phase is not implemented yet.", phase_name)
    return True


def phase_verify_webvh(_ctx: Context) -> bool:
    return _placeholder_phase("verify-webvh")


def phase_verify_webvh_post_revoke(_ctx: Context) -> bool:
    return _placeholder_phase("verify-webvh-post-revoke")

