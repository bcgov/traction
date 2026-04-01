"""DIDComm connection phases (holder ↔ issuer over DIDComm)."""

from __future__ import annotations

import logging

from context import Context

LOG = logging.getLogger("webvh-e2e")


def phase_oob_didexchange_webvh_didcomm(_ctx: Context) -> bool:
    """Out-of-band DID Exchange using the WebVH issuer DID and DIDComm (not implemented yet)."""
    LOG.info("oob-didexchange-webvh-didcomm phase is not implemented yet.")
    return True
