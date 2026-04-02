"""Revoke-related phases."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from context import Context

LOG = logging.getLogger("webvh-e2e")


def _revocation_ids_from_cred_ex_detail(detail: dict[str, Any]) -> tuple[str | None, str | None]:
    """
    ``GET /issue-credential-2.0/records/{id}`` returns ``V20CredExRecordDetail``:
    ``rev_reg_id`` / ``cred_rev_id`` sit under ``anoncreds`` or ``indy`` (not on ``cred_ex_id`` alone).
    """
    for key in ("anoncreds", "indy"):
        block = detail.get(key)
        if not isinstance(block, dict):
            continue
        rev_reg_id = block.get("rev_reg_id")
        cred_rev_id = block.get("cred_rev_id")
        if rev_reg_id is None or cred_rev_id is None or cred_rev_id == "":
            continue
        return str(rev_reg_id), str(cred_rev_id)
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

    rev_reg_id, cred_rev_id = _revocation_ids_from_cred_ex_detail(detail)
    publish = os.environ.get("WEBVH_E2E_REVOKE_PUBLISH", "true").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )

    # Agents started with --notify-revocation default notify=true; that requires connection_id +
    # thread_id. E2E revokes locally without DIDComm revocation notification unless opted in.
    notify = os.environ.get("WEBVH_E2E_REVOKE_NOTIFY", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )

    def _cred_ex_core(d: dict[str, Any]) -> dict[str, Any]:
        cr = d.get("cred_ex_record")
        return cr if isinstance(cr, dict) else {}

    body: dict[str, Any] = {"publish": publish, "notify": notify}

    if notify:
        core = _cred_ex_core(detail)
        conn = core.get("connection_id") or ctx.issuer_connection_id
        tid = core.get("thread_id") or core.get("parent_thread_id")
        if not conn or not tid:
            LOG.error(
                "WEBVH_E2E_REVOKE_NOTIFY enabled but missing connection_id or thread_id "
                "(need them on the cred exchange or issuer_connection_id + thread on record)"
            )
            return False
        body["connection_id"] = str(conn)
        body["thread_id"] = str(tid)

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
