"""Schema/credential-definition phases."""

from __future__ import annotations

import logging

from context import Context

LOG = logging.getLogger("webvh-e2e")


def _placeholder_phase(phase_name: str) -> bool:
    LOG.info("%s phase is not implemented yet.", phase_name)
    return True


def phase_publish_schema(_ctx: Context) -> bool:
    return _placeholder_phase("publish-schema-webvh")


def phase_publish_cred_def(_ctx: Context) -> bool:
    return _placeholder_phase("publish-cred-def-webvh")
