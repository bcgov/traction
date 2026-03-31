"""Shared phase helpers."""

from __future__ import annotations

import logging

from context import Context

LOG = logging.getLogger("webvh-e2e")


def phase_upgrade_anoncreds_wallet(_ctx: Context) -> bool:
    LOG.info("upgrade-anoncreds-wallet phase is not implemented yet.")
    return True

