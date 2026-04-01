"""Setup phases: issuer wallet upgrade and AnonCreds publish placeholders."""

from __future__ import annotations

import json
import logging
import os
import time

from typing import Any

from context import Context

LOG = logging.getLogger(__name__)


def _wallet_settings_blob(wallet: dict[str, Any]) -> dict[str, Any]:
    settings_value = wallet.get("settings")
    return settings_value if isinstance(settings_value, dict) else {}


def _wallet_name_from_response(wallet: dict[str, Any]) -> str | None:
    """
    Multitenant wallet name for ``POST /anoncreds/wallet/upgrade``.

    ACA-Py ``GET /settings`` does not return ``wallet.name`` (filtered dict); use
    ``GET /tenant/wallet`` → ``settings['wallet.name']``.
    """
    name = _wallet_settings_blob(wallet).get("wallet.name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return None


def _wallet_type_from_response(wallet: dict[str, Any]) -> str | None:
    """Wallet storage type (e.g. askar / askar-anoncreds) from tenant wallet payload."""
    top_level = wallet.get("type")
    if isinstance(top_level, str) and top_level:
        return top_level
    from_settings = _wallet_settings_blob(wallet).get("wallet.type")
    return from_settings if isinstance(from_settings, str) else None


def _wallet_upgrade_poll_sec() -> float:
    return float(os.environ.get("WEBVH_WALLET_UPGRADE_POLL_SEC", "2"))


def _wallet_upgrade_timeout_sec() -> float:
    return float(os.environ.get("WEBVH_WALLET_UPGRADE_TIMEOUT_SEC", "120"))


def phase_upgrade_anoncreds_wallet(ctx: Context) -> bool:
    """
    Ensure issuer wallet is upgraded to askar-anoncreds (POST /anoncreds/wallet/upgrade, poll GET /tenant/wallet).

    Requires issuer bearer token. Skips if already askar-anoncreds.
    """
    client = ctx.issuer_client()

    initial_wallet_response = client.get_tenant_wallet()
    if not initial_wallet_response.ok:
        LOG.error(
            "GET /tenant/wallet failed: %s %s",
            initial_wallet_response.status_code,
            initial_wallet_response.text[:500],
        )
        return False
    try:
        wallet = initial_wallet_response.json()
    except json.JSONDecodeError:
        LOG.error("GET /tenant/wallet returned non-JSON")
        return False

    wallet_name = _wallet_name_from_response(wallet)
    if not wallet_name:
        LOG.error(
            "GET /tenant/wallet missing settings.wallet.name; cannot upgrade wallet"
        )
        return False

    wallet_storage_type = _wallet_type_from_response(wallet)
    if wallet_storage_type == "askar-anoncreds":
        LOG.info("Issuer wallet already askar-anoncreds; skipping upgrade")
        return True

    LOG.info(
        "Upgrading issuer wallet to askar-anoncreds (current type=%s)",
        wallet_storage_type,
    )
    upgrade_response = client.post_anoncreds_wallet_upgrade(wallet_name)
    if not upgrade_response.ok:
        LOG.error(
            "POST /anoncreds/wallet/upgrade failed: %s %s",
            upgrade_response.status_code,
            upgrade_response.text[:500],
        )
        return False

    deadline = time.monotonic() + _wallet_upgrade_timeout_sec()
    poll_interval_sec = _wallet_upgrade_poll_sec()
    while time.monotonic() < deadline:
        poll_wallet_response = client.get_tenant_wallet()
        if not poll_wallet_response.ok:
            LOG.warning(
                "GET /tenant/wallet during poll failed: %s",
                poll_wallet_response.status_code,
            )
            time.sleep(poll_interval_sec)
            continue
        try:
            polled_wallet = poll_wallet_response.json()
        except json.JSONDecodeError:
            time.sleep(poll_interval_sec)
            continue
        if _wallet_type_from_response(polled_wallet) == "askar-anoncreds":
            LOG.info("Issuer wallet upgraded to askar-anoncreds")
            return True
        time.sleep(poll_interval_sec)

    LOG.error("Timed out waiting for wallet type askar-anoncreds")
    return False


def _placeholder_phase(phase_name: str) -> bool:
    LOG.info("%s phase is not implemented yet.", phase_name)
    return True


def phase_publish_schema(_ctx: Context) -> bool:
    return _placeholder_phase("publish-schema-webvh")


def phase_publish_cred_def(_ctx: Context) -> bool:
    return _placeholder_phase("publish-cred-def-webvh")
