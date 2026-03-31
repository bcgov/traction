"""Schema/credential-definition phases."""

from __future__ import annotations

from context import Context
from harness_log import LOG


def _placeholder_phase(phase_name: str) -> bool:
    LOG.info("%s phase is not implemented yet.", phase_name)
    return True


def phase_publish_schema(_ctx: Context) -> bool:
    return _placeholder_phase("publish-schema-webvh")


def phase_publish_cred_def(_ctx: Context) -> bool:
    return _placeholder_phase("publish-cred-def-webvh")
