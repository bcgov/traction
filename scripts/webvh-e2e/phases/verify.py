"""Verify-related phases (present-proof 2.0)."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from context import Context
from helpers import poll_until

LOG = logging.getLogger("webvh-e2e")

# Must match ``requested_attributes`` key in ``presentation_request.anoncreds`` below.
_E2E_PROOF_ATTR_REFERENT = "e2e_attrs"


def _schema_attr_names() -> list[str]:
    raw = os.environ.get("WEBVH_E2E_SCHEMA_ATTRS", "name,score")
    return [part.strip() for part in raw.split(",") if part.strip()]


def _verified_is_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


def _present_proof_round(ctx: Context, *, expect_verified: bool) -> bool:
    if not ctx.webvh_cred_def_id or not ctx.issuer_connection_id or not ctx.holder_connection_id:
        LOG.error("Missing cred_def or connection IDs for proof")
        return False

    issuer = ctx.issuer_client()
    holder = ctx.holder_client()
    attr_names = _schema_attr_names()
    if not attr_names:
        LOG.error("No schema attribute names for proof request")
        return False

    now = int(time.time())
    proof_body = {
        "connection_id": ctx.issuer_connection_id,
        "presentation_request": {
            "anoncreds": {
                "name": "WebVH E2E proof",
                "version": "1.0",
                "requested_attributes": {
                    _E2E_PROOF_ATTR_REFERENT: {
                        "names": attr_names,
                        "restrictions": [{"cred_def_id": ctx.webvh_cred_def_id}],
                        "non_revoked": {"from": now - 86_400, "to": now},
                    }
                },
                "requested_predicates": {},
            }
        },
        "auto_verify": True,
        "trace": False,
    }

    send_response = issuer.post_present_proof_v2_send_request(proof_body)
    if not send_response.ok:
        LOG.error(
            "POST /present-proof-2.0/send-request failed (HTTP %s)",
            send_response.status_code,
        )
        LOG.debug(
            "send-request error body:\n%s",
            (send_response.text or "")[:4000],
        )
        return False

    try:
        sent = send_response.json()
    except json.JSONDecodeError:
        LOG.error("send-request returned non-JSON")
        return False
    pres_ex_id_verifier = sent.get("pres_ex_id")
    if not pres_ex_id_verifier:
        LOG.error("send-request response missing pres_ex_id")
        LOG.debug("send-request body:\n%s", json.dumps(sent, indent=2, default=str))
        return False
    pres_ex_id_verifier = str(pres_ex_id_verifier)

    poll_sec = float(os.environ.get("WEBVH_E2E_PROOF_POLL_SEC", "2"))
    timeout_sec = float(os.environ.get("WEBVH_E2E_PROOF_TIMEOUT_SEC", "180"))

    def holder_pres_ex_id() -> str | None:
        records = holder.get_present_proof_v2_records(
            params={
                "role": "prover",
                "state": "request-received",
                "connection_id": ctx.holder_connection_id,
            }
        )
        if not records.ok:
            return None
        try:
            payload = records.json()
        except json.JSONDecodeError:
            return None
        for row in payload.get("results") or []:
            pid = row.get("pres_ex_id")
            if pid:
                return str(pid)
        return None

    holder_pres_ex = poll_until(
        holder_pres_ex_id,
        timeout_sec=timeout_sec,
        interval_sec=poll_sec,
        description="holder presentation exchange (request-received)",
    )
    if not holder_pres_ex:
        return False

    creds_resp = holder.get_present_proof_v2_credentials(
        holder_pres_ex,
        params={"referent": _E2E_PROOF_ATTR_REFERENT, "limit": 20},
    )
    if not creds_resp.ok:
        LOG.error(
            "Holder GET /present-proof-2.0/records/…/credentials failed (HTTP %s)",
            creds_resp.status_code,
        )
        LOG.debug(
            "credentials error body:\n%s",
            (creds_resp.text or "")[:4000],
        )
        return False
    try:
        cred_rows = creds_resp.json()
    except json.JSONDecodeError:
        LOG.error("Holder credentials lookup returned non-JSON")
        return False
    if not isinstance(cred_rows, list) or not cred_rows:
        LOG.error(
            "No wallet credentials match proof referent %r for pres_ex_id=%s; "
            "ensure issue-webvh completed on this holder",
            _E2E_PROOF_ATTR_REFERENT,
            holder_pres_ex,
        )
        return False

    wallet_cred_id: str | None = None
    want_cd = (ctx.webvh_cred_def_id or "").strip()
    for row in cred_rows:
        if not isinstance(row, dict):
            continue
        ci = row.get("cred_info")
        if not isinstance(ci, dict):
            continue
        ref = ci.get("referent")
        if not ref:
            continue
        cdid = (ci.get("cred_def_id") or "").strip()
        if want_cd and cdid and cdid != want_cd:
            continue
        wallet_cred_id = str(ref)
        break
    if not wallet_cred_id:
        for row in cred_rows:
            if not isinstance(row, dict):
                continue
            ci = row.get("cred_info")
            if isinstance(ci, dict) and ci.get("referent"):
                wallet_cred_id = str(ci["referent"])
                LOG.warning(
                    "Using first matching credential referent without cred_def_id filter "
                    "(wanted cred_def_id=%s)",
                    want_cd or "(unset)",
                )
                break
    if not wallet_cred_id:
        LOG.error(
            "Could not resolve wallet credential id for referent %r (cred_def_id=%s)",
            _E2E_PROOF_ATTR_REFERENT,
            want_cd or "(any)",
        )
        return False

    pres_body: dict[str, Any] = {
        "anoncreds": {
            "requested_attributes": {
                _E2E_PROOF_ATTR_REFERENT: {
                    "cred_id": wallet_cred_id,
                    "revealed": True,
                }
            },
            "requested_predicates": {},
            "self_attested_attributes": {},
        }
    }
    LOG.info(
        "Holder send-presentation (wallet cred_id=%s referent=%s)",
        wallet_cred_id,
        _E2E_PROOF_ATTR_REFERENT,
    )
    pres = holder.post_present_proof_v2_send_presentation(holder_pres_ex, pres_body)
    if not pres.ok:
        LOG.error(
            "Holder send-presentation failed (HTTP %s)",
            pres.status_code,
        )
        LOG.debug(
            "send-presentation error body:\n%s",
            (pres.text or "")[:4000],
        )
        return False

    def verifier_outcome() -> str | None:
        check = issuer.get_present_proof_v2_record(pres_ex_id_verifier)
        if not check.ok:
            return None
        try:
            row = check.json()
        except json.JSONDecodeError:
            return None
        state = (row.get("state") or "").lower()
        if state == "done":
            verified = _verified_is_true(row.get("verified"))
            return "verified" if verified else "not_verified"
        if state == "abandoned":
            return "abandoned"
        return None

    outcome = poll_until(
        verifier_outcome,
        timeout_sec=timeout_sec,
        interval_sec=poll_sec,
        description="verifier presentation exchange completed",
    )
    if outcome is None:
        return False

    if expect_verified:
        if outcome == "verified":
            LOG.info("Presentation verified as expected")
            return True
        LOG.error("Expected verified proof, got outcome=%s", outcome)
        return False

    if outcome in ("not_verified", "abandoned"):
        LOG.info("Presentation not verified after revocation (outcome=%s)", outcome)
        return True
    LOG.error("Expected unverifiable proof after revocation, got outcome=%s", outcome)
    return False


def phase_verify_webvh(ctx: Context) -> bool:
    """Request anoncreds proof with non-revocation interval; expect verification success."""
    return _present_proof_round(ctx, expect_verified=True)


def phase_verify_webvh_post_revoke(ctx: Context) -> bool:
    """Same proof request after revocation; expect verification to fail."""
    return _present_proof_round(ctx, expect_verified=False)
