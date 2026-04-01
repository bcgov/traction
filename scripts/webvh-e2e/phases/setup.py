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
    s = wallet.get("settings")
    return s if isinstance(s, dict) else {}


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
    t = wallet.get("type")
    if isinstance(t, str) and t:
        return t
    wt = _wallet_settings_blob(wallet).get("wallet.type")
    return wt if isinstance(wt, str) else None


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

    r2 = client.get_tenant_wallet()
    if not r2.ok:
        LOG.error("GET /tenant/wallet failed: %s %s", r2.status_code, r2.text[:500])
        return False
    try:
        wallet = r2.json()
    except json.JSONDecodeError:
        LOG.error("GET /tenant/wallet returned non-JSON")
        return False

    wallet_name = _wallet_name_from_response(wallet)
    if not wallet_name:
        LOG.error(
            "GET /tenant/wallet missing settings.wallet.name; cannot upgrade wallet"
        )
        return False

    wtype = _wallet_type_from_response(wallet)
    if wtype == "askar-anoncreds":
        LOG.info("Issuer wallet already askar-anoncreds; skipping upgrade")
        return True

    LOG.info("Upgrading issuer wallet to askar-anoncreds (current type=%s)", wtype)
    r3 = client.post_anoncreds_wallet_upgrade(wallet_name)
    if not r3.ok:
        LOG.error(
            "POST /anoncreds/wallet/upgrade failed: %s %s",
            r3.status_code,
            r3.text[:500],
        )
        return False

    deadline = time.monotonic() + _wallet_upgrade_timeout_sec()
    poll = _wallet_upgrade_poll_sec()
    while time.monotonic() < deadline:
        r4 = client.get_tenant_wallet()
        if not r4.ok:
            LOG.warning("GET /tenant/wallet during poll failed: %s", r4.status_code)
            time.sleep(poll)
            continue
        try:
            w = r4.json()
        except json.JSONDecodeError:
            time.sleep(poll)
            continue
        if _wallet_type_from_response(w) == "askar-anoncreds":
            LOG.info("Issuer wallet upgraded to askar-anoncreds")
            return True
        time.sleep(poll)

    LOG.error("Timed out waiting for wallet type askar-anoncreds")
    return False


def _placeholder_phase(phase_name: str) -> bool:
    LOG.info("%s phase is not implemented yet.", phase_name)
    return True


def phase_publish_schema(_ctx: Context) -> bool:
    return _placeholder_phase("publish-schema-webvh")


def phase_publish_cred_def(_ctx: Context) -> bool:
    return _placeholder_phase("publish-cred-def-webvh")
