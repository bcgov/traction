"""Revoke-related phases."""

from __future__ import annotations

import json
import logging
from typing import Any

from context import Context
from constants import E2E_REVOKE_NOTIFY, E2E_REVOKE_PUBLISH
from helpers import v20_cred_ex_record_core

LOG = logging.getLogger("webvh-e2e")


def _revocation_ids_from_flat_cred_ex(d: dict[str, Any]) -> tuple[str | None, str | None]:
    """``rev_reg_id`` / ``cred_rev_id`` under ``anoncreds`` or ``indy`` on one record object."""
    for key in ("anoncreds", "indy"):
        block = d.get(key)
        if not isinstance(block, dict):
            continue
        rev_reg_id = block.get("rev_reg_id")
        cred_rev_id = block.get("cred_rev_id")
        if rev_reg_id is None or cred_rev_id is None or cred_rev_id == "":
            continue
        return str(rev_reg_id), str(cred_rev_id)
    return None, None


def _revocation_ids_from_cred_ex_payload(detail: dict[str, Any]) -> tuple[str | None, str | None]:
    """
    Same unwrapping as issue phase: try outer ``V20CredExRecordDetail``, then ``cred_ex_record`` core.
    Revocation fields may live only on the inner object.
    """
    seen: set[int] = set()
    for cand in (detail, v20_cred_ex_record_core(detail)):
        cid = id(cand)
        if cid in seen:
            continue
        seen.add(cid)
        rev_reg_id, cred_rev_id = _revocation_ids_from_flat_cred_ex(cand)
        if rev_reg_id and cred_rev_id:
            return rev_reg_id, cred_rev_id
    return None, None


def phase_revoke_webvh(ctx: Context) -> bool:
    """POST /anoncreds/revocation/revoke for the issued credential (publish)."""
    cred_ex_id = ctx.issuer_cred_ex_id
    if not cred_ex_id:
        LOG.error("No issuer cred_ex_id; run issue-webvh first")
        return False

    client = ctx.issuer_client()
    rec = client.get_issue_credential_v2_record(cred_ex_id)
    if not rec.ok:
        LOG.error(
            "GET /issue-credential-2.0/records/%s failed (HTTP %s); cannot revoke",
            cred_ex_id,
            rec.status_code,
        )
        LOG.debug("GET cred ex error:\n%s", (rec.text or "")[:2000])
        return False
    try:
        detail = rec.json()
    except json.JSONDecodeError:
        LOG.error("Issuer credential exchange record returned non-JSON")
        return False
    if not isinstance(detail, dict):
        LOG.error("Issuer credential exchange record is not an object")
        return False

    rev_reg_id, cred_rev_id = _revocation_ids_from_cred_ex_payload(detail)

    body: dict[str, Any] = {
        "publish": E2E_REVOKE_PUBLISH,
        "notify": E2E_REVOKE_NOTIFY,
    }

    if rev_reg_id and cred_rev_id:
        body["rev_reg_id"] = rev_reg_id
        body["cred_rev_id"] = cred_rev_id
    else:
        body["cred_ex_id"] = cred_ex_id
        LOG.warning(
            "No rev_reg_id/cred_rev_id on exchange detail; falling back to cred_ex_id-only revoke "
            "(may fail on some agents)"
        )

    response = client.post_anoncreds_revocation_revoke(body)
    if not response.ok:
        err = (response.text or "").strip()
        LOG.error(
            "POST /anoncreds/revocation/revoke failed (HTTP %s)%s",
            response.status_code,
            f": {err[:500]}" if err else "",
        )
        LOG.debug(
            "revoke error body:\n%s",
            (response.text or "")[:4000],
        )
        return False
    try:
        payload = response.json()
    except json.JSONDecodeError:
        payload = {}
    LOG.info("Revoked credential cred_ex_id=%s", cred_ex_id)
    LOG.debug("revoke response: %s", payload)
    return True
