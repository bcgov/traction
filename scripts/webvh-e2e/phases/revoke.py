"""Revoke-related phases."""

from __future__ import annotations

import json
import logging

from context import Context

LOG = logging.getLogger("webvh-e2e")


def phase_revoke_webvh(ctx: Context) -> bool:
    """POST /anoncreds/revocation/revoke for the issuer credential exchange (publish)."""
    cred_ex_id = ctx.issuer_cred_ex_id
    if not cred_ex_id:
        LOG.error("No issuer cred_ex_id; run issue-webvh first")
        return False

    body = {
        "cred_ex_id": cred_ex_id,
        "publish": True,
    }
    response = ctx.issuer_client().post_anoncreds_revocation_revoke(body)
    if not response.ok:
        LOG.error(
            "POST /anoncreds/revocation/revoke failed: %s %s",
            response.status_code,
            (response.text or "")[:600],
        )
        return False
    try:
        payload = response.json()
    except json.JSONDecodeError:
        payload = {}
    LOG.info("Revoked credential cred_ex_id=%s response=%s", cred_ex_id, payload)
    return True
