"""Smoke / liveness phases (tenant proxy and wallets)."""

from __future__ import annotations

import json
import time
from typing import Any

import requests

from constants import (
    E2E_SMOKE_WALLET_POST_READY_SETTLE_SEC,
    E2E_SMOKE_WALLET_READY_POLL_SEC,
    E2E_SMOKE_WALLET_READY_TIMEOUT_SEC,
)
from context import Context
from helpers import LOG, tenant_wallet_storage_type


def _smoke_status_live(client_label: str, live_response: requests.Response) -> None:
    if not live_response.ok:
        LOG.warning(
            "[%s] GET /status/live returned HTTP %s; continuing (response snippet: %s)",
            client_label,
            live_response.status_code,
            live_response.text[:160].replace("\n", " "),
        )
    else:
        LOG.info("[%s] GET /status/live ok", client_label)


def _wait_tenant_wallet_ready(
    client_label: str, client: object
) -> tuple[bool, dict[str, Any] | None]:
    """
    Poll GET /tenant/wallet until OK or timeout (handles 503 during wallet upgrade).

    Returns ``(True, body)`` on success with parsed JSON object, else ``(False, None)``.
    """
    deadline = time.monotonic() + E2E_SMOKE_WALLET_READY_TIMEOUT_SEC
    poll_interval_sec = E2E_SMOKE_WALLET_READY_POLL_SEC
    fetch_tenant_wallet = getattr(client, "get_tenant_wallet")
    while time.monotonic() < deadline:
        wallet_response = fetch_tenant_wallet()
        if wallet_response.ok:
            LOG.info("[%s] GET /tenant/wallet ok", client_label)
            try:
                wallet_payload = wallet_response.json()
            except json.JSONDecodeError:
                LOG.error("[%s] GET /tenant/wallet returned non-JSON", client_label)
                return False, None
            if not isinstance(wallet_payload, dict):
                LOG.error("[%s] GET /tenant/wallet JSON is not an object", client_label)
                return False, None
            return True, wallet_payload
        LOG.warning(
            "[%s] GET /tenant/wallet HTTP %s; retrying in %.0fs (wallet upgrade / platform load)",
            client_label,
            wallet_response.status_code,
            poll_interval_sec,
        )
        time.sleep(poll_interval_sec)
    LOG.error(
        "[%s] GET /tenant/wallet still failing after %.0fs",
        client_label,
        E2E_SMOKE_WALLET_READY_TIMEOUT_SEC,
    )
    return False, None


def phase_smoke(context: Context) -> bool:
    """Smoke check: liveness plus tenant wallet ready for both tenants (polls through upgrade 503)."""
    issuer = context.issuer_client()
    holder = context.holder_client()
    _smoke_status_live("issuer", issuer.get_status_live())
    _smoke_status_live("holder", holder.get_status_live())
    issuer_wallet_ok, issuer_wallet_payload = _wait_tenant_wallet_ready("issuer", issuer)
    holder_wallet_ok, holder_wallet_payload = _wait_tenant_wallet_ready("holder", holder)
    if not issuer_wallet_ok or not holder_wallet_ok:
        return False

    post_ready_settle_sec = E2E_SMOKE_WALLET_POST_READY_SETTLE_SEC
    if post_ready_settle_sec > 0:
        issuer_storage_type = tenant_wallet_storage_type(issuer_wallet_payload or {})
        holder_storage_type = tenant_wallet_storage_type(holder_wallet_payload or {})
        if issuer_storage_type == "askar-anoncreds" and holder_storage_type == "askar-anoncreds":
            LOG.info(
                "Smoke: skipping %.0fs post-ready settle (issuer and holder already askar-anoncreds)",
                post_ready_settle_sec,
            )
        else:
            LOG.info(
                "Smoke: waiting %.0fs after wallets ready (post-upgrade settle)",
                post_ready_settle_sec,
            )
            time.sleep(post_ready_settle_sec)
    return True
