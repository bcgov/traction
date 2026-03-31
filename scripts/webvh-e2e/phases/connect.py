"""Connection/configuration related phases."""

from __future__ import annotations

import logging

import requests

from context import Context

LOG = logging.getLogger("webvh-e2e")


def _smoke_status_live(client_label: str, live: requests.Response) -> None:
    if not live.ok:
        LOG.warning(
            "[%s] GET /status/live returned HTTP %s; continuing (response snippet: %s)",
            client_label,
            live.status_code,
            live.text[:160].replace("\n", " "),
        )
    else:
        LOG.info("[%s] GET /status/live ok", client_label)


def _smoke_tenant_wallet(client_label: str, resp: requests.Response) -> None:
    if not resp.ok:
        LOG.warning(
            "[%s] GET /tenant/wallet returned HTTP %s; continuing (response snippet: %s)",
            client_label,
            resp.status_code,
            resp.text[:160].replace("\n", " "),
        )
    else:
        LOG.info("[%s] GET /tenant/wallet ok", client_label)


def phase_smoke(ctx: Context) -> bool:
    """Smoke check: unauthenticated liveness plus authenticated tenant wallet for both tenants."""
    issuer = ctx.issuer_client()
    holder = ctx.holder_client()
    _smoke_status_live("issuer", issuer.get_status_live())
    _smoke_status_live("holder", holder.get_status_live())
    _smoke_tenant_wallet("issuer", issuer.get_tenant_wallet())
    _smoke_tenant_wallet("holder", holder.get_tenant_wallet())
    return True


def _placeholder_phase(phase_name: str) -> bool:
    LOG.info("%s phase is not implemented yet.", phase_name)
    return True


def phase_configure_webvh_plugin(_ctx: Context) -> bool:
    return _placeholder_phase("configure-webvh-plugin")


def phase_webvh_create(_ctx: Context) -> bool:
    return _placeholder_phase("webvh-create")


def phase_oob_didexchange_webvh_didcomm(_ctx: Context) -> bool:
    return _placeholder_phase("oob-didexchange-webvh-didcomm")
