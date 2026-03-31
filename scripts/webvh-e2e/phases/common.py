"""Shared phase helpers."""

from __future__ import annotations

from context import Context
from harness_log import LOG


def phase_upgrade_anoncreds_wallet(_ctx: Context) -> bool:
    LOG.info("upgrade-anoncreds-wallet phase is not implemented yet.")
    return True

