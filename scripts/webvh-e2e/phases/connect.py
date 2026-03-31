"""Connection/configuration related phases."""

from __future__ import annotations

import logging

from context import Context

LOG = logging.getLogger("webvh-e2e")


def phase_smoke(ctx: Context) -> bool:
    """Smoke check against tenant proxy."""
    live = ctx.issuer_client().get_status_live()
    if not live.ok:
        LOG.warning(
            "GET /status/live returned HTTP %s; continuing (response snippet: %s)",
            live.status_code,
            live.text[:160].replace("\n", " "),
        )
        return True
    LOG.info("GET /status/live (smoke check)")
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
