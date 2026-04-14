"""Verify-related phases (present-proof 2.0)."""

from __future__ import annotations

import json
import time
from typing import Any

from context import Context
from constants import (
    E2E_PROOF_HOLDER_CRED_MATCH_TIMEOUT_SEC,
    E2E_PROOF_POLL_SEC,
    E2E_PROOF_TIMEOUT_SEC,
    E2E_SCHEMA_ATTR_NAMES,
)
from helpers import LOG, format_json_for_log, log_http_failed, poll_until

# Must match ``requested_attributes`` key in ``presentation_request.anoncreds`` below.
_E2E_PROOF_ATTR_REFERENT = "e2e_attrs"


def _normalize_cred_def_id(cred_def_id: str | None) -> str:
    """Match wallet ``cred_info.cred_def_id`` to harness ``cred_def_id`` (Indy may use ``did:sov:``)."""
    if not cred_def_id:
        return ""
    cred_def_id_str = str(cred_def_id).strip()
    if cred_def_id_str.startswith("did:sov:"):
        return cred_def_id_str[8:]
    return cred_def_id_str


def _thread_thid_from_pres_dict(presentation_exchange: dict[str, Any]) -> str | None:
    """Best-effort thread id for correlating issuer ↔ holder present-proof exchanges."""
    thread_id = presentation_exchange.get("thread_id")
    if isinstance(thread_id, str) and thread_id.strip():
        return thread_id.strip()
    for key in ("pres_request", "pres_proposal", "presentation_request"):
        message = presentation_exchange.get(key)
        if not isinstance(message, dict):
            continue
        thread_block = message.get("~thread") or message.get("thread")
        if isinstance(thread_block, dict):
            thread_hint = thread_block.get("thid") or thread_block.get("pthid")
            if isinstance(thread_hint, str) and thread_hint.strip():
                return thread_hint.strip()
    return None


def _cred_def_id_from_wallet_row(
    wallet_cred_row: dict[str, Any], credential_info: dict[str, Any]
) -> str | None:
    """ACA-Py / wallet payloads vary: pull cred def id from cred_info or top-level row."""
    for source in (credential_info, wallet_cred_row):
        for field_name in ("cred_def_id", "credential_definition_id", "credDefId"):
            raw_value = source.get(field_name)
            if isinstance(raw_value, str) and raw_value.strip():
                return raw_value.strip()
    return None


def _pick_wallet_cred_id_for_proof(
    cred_rows: list[Any],
    want_cred_def_id: str,
) -> str | None:
    """Wallet referent for send-presentation; match cred_def_id when set (avoid stale pres_ex rows)."""
    normalized_target_cred_def_id = _normalize_cred_def_id(want_cred_def_id)
    if not normalized_target_cred_def_id:
        for wallet_cred_row in cred_rows:
            if not isinstance(wallet_cred_row, dict):
                continue
            credential_info = wallet_cred_row.get("cred_info")
            if isinstance(credential_info, dict) and credential_info.get("referent"):
                return str(credential_info["referent"])
        return None
    for wallet_cred_row in cred_rows:
        if not isinstance(wallet_cred_row, dict):
            continue
        credential_info = wallet_cred_row.get("cred_info")
        if not isinstance(credential_info, dict):
            continue
        referent = credential_info.get("referent")
        if not referent:
            continue
        normalized_wallet_cred_def_id = _normalize_cred_def_id(
            _cred_def_id_from_wallet_row(wallet_cred_row, credential_info)
        )
        if (
            not normalized_wallet_cred_def_id
            or normalized_wallet_cred_def_id != normalized_target_cred_def_id
        ):
            continue
        return str(referent)
    return None


def _verified_is_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


def _holder_pres_candidates_request_received(
    records_payload: Any,
    holder_connection_id: str | None,
) -> list[dict[str, Any]]:
    """Filter present-proof rows to ``request-received`` for this holder connection."""
    if not isinstance(records_payload, dict):
        return []
    expected_holder_connection_id = (holder_connection_id or "").strip()
    candidate_pres_exchanges: list[dict[str, Any]] = []
    for pres_ex_row in records_payload.get("results") or []:
        if not isinstance(pres_ex_row, dict):
            continue
        if (pres_ex_row.get("state") or "").lower() != "request-received":
            continue
        row_connection_id = str(pres_ex_row.get("connection_id") or "").strip()
        if expected_holder_connection_id and row_connection_id != expected_holder_connection_id:
            continue
        candidate_pres_exchanges.append(pres_ex_row)
    return candidate_pres_exchanges


def _pick_holder_pres_ex_id_from_candidates(
    candidate_pres_exchanges: list[dict[str, Any]],
    issuer_proof_thread_id_hint: str | None,
) -> str | None:
    """Pick holder ``pres_ex_id``: match issuer thread id if possible, else newest row."""
    if not candidate_pres_exchanges:
        return None
    if issuer_proof_thread_id_hint:
        for pres_ex_row in candidate_pres_exchanges:
            if _thread_thid_from_pres_dict(pres_ex_row) != issuer_proof_thread_id_hint:
                continue
            pres_ex_id_value = pres_ex_row.get("pres_ex_id")
            if pres_ex_id_value:
                return str(pres_ex_id_value)
    candidate_pres_exchanges.sort(
        key=lambda pres_ex_row: str(
            pres_ex_row.get("updated_at") or pres_ex_row.get("created_at") or ""
        ),
        reverse=True,
    )
    pres_ex_id_value = candidate_pres_exchanges[0].get("pres_ex_id")
    return str(pres_ex_id_value) if pres_ex_id_value else None


def _present_proof_round(
    context: Context,
    *,
    cred_def_id: str,
    proof_name: str,
    expect_verified: bool,
    log_label: str,
) -> bool:
    if not cred_def_id or not context.issuer_connection_id or not context.holder_connection_id:
        LOG.error("[%s] Missing cred_def or connection IDs for proof", log_label)
        return False

    issuer = context.issuer_client()
    holder = context.holder_client()
    attr_names = E2E_SCHEMA_ATTR_NAMES

    now = int(time.time())
    proof_body = {
        "connection_id": context.issuer_connection_id,
        "presentation_request": {
            "anoncreds": {
                "name": proof_name,
                "version": "1.0",
                "requested_attributes": {
                    _E2E_PROOF_ATTR_REFERENT: {
                        "names": attr_names,
                        "restrictions": [{"cred_def_id": cred_def_id}],
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
        log_http_failed("POST /present-proof-2.0/send-request failed", send_response)
        return False

    try:
        send_request_payload = send_response.json()
    except json.JSONDecodeError:
        LOG.error("send-request returned non-JSON")
        return False
    verifier_pres_ex_id = send_request_payload.get("pres_ex_id")
    if not verifier_pres_ex_id:
        LOG.error("send-request response missing pres_ex_id")
        LOG.debug("send-request body:\n%s", format_json_for_log(send_request_payload))
        return False
    verifier_pres_ex_id = str(verifier_pres_ex_id)
    issuer_proof_thread_id_hint = (
        _thread_thid_from_pres_dict(send_request_payload)
        if isinstance(send_request_payload, dict)
        else None
    )

    poll_interval_sec = E2E_PROOF_POLL_SEC
    proof_poll_timeout_sec = E2E_PROOF_TIMEOUT_SEC

    def poll_holder_pres_ex_id() -> str | None:
        """Resolve holder pres_ex_id: correlate by issuer thread id else newest request-received row."""
        records_response = holder.get_present_proof_v2_records(
            params={
                "role": "prover",
                "state": "request-received",
                "connection_id": context.holder_connection_id,
            }
        )
        if not records_response.ok:
            return None
        try:
            records_payload = records_response.json()
        except json.JSONDecodeError:
            return None
        candidates = _holder_pres_candidates_request_received(
            records_payload, context.holder_connection_id
        )
        return _pick_holder_pres_ex_id_from_candidates(candidates, issuer_proof_thread_id_hint)

    holder_pres_exchange_id = poll_until(
        poll_holder_pres_ex_id,
        timeout_sec=proof_poll_timeout_sec,
        interval_sec=poll_interval_sec,
        description="holder presentation exchange (request-received)",
    )
    if not holder_pres_exchange_id:
        return False

    target_cred_def_id = (cred_def_id or "").strip()
    wallet_cred_id: str | None = None
    cred_deadline = time.monotonic() + E2E_PROOF_HOLDER_CRED_MATCH_TIMEOUT_SEC
    while time.monotonic() < cred_deadline:
        credentials_http_response = holder.get_present_proof_v2_credentials(
            holder_pres_exchange_id,
            params={"referent": _E2E_PROOF_ATTR_REFERENT, "limit": 20},
        )
        if not credentials_http_response.ok:
            if credentials_http_response.status_code in (502, 503, 504):
                LOG.warning(
                    "Holder GET …/credentials HTTP %s; retrying (proxy/upstream)",
                    credentials_http_response.status_code,
                )
                time.sleep(E2E_PROOF_POLL_SEC)
                continue
            log_http_failed(
                "Holder GET /present-proof-2.0/records/…/credentials failed",
                credentials_http_response,
            )
            return False
        try:
            cred_rows = credentials_http_response.json()
        except json.JSONDecodeError:
            LOG.error("Holder credentials lookup returned non-JSON")
            return False
        if not isinstance(cred_rows, list) or not cred_rows:
            LOG.info(
                "[%s] No credentials listed yet for referent %r pres_ex_id=%s; "
                "waiting for wallet / cred_def_id=%s",
                log_label,
                _E2E_PROOF_ATTR_REFERENT,
                holder_pres_exchange_id,
                target_cred_def_id or "(any)",
            )
            time.sleep(E2E_PROOF_POLL_SEC)
            continue
        wallet_cred_id = _pick_wallet_cred_id_for_proof(cred_rows, target_cred_def_id)
        if wallet_cred_id:
            break
        LOG.info(
            "[%s] Credentials for referent %r present but none match cred_def_id=%s; retrying",
            log_label,
            _E2E_PROOF_ATTR_REFERENT,
            target_cred_def_id or "(any)",
        )
        time.sleep(E2E_PROOF_POLL_SEC)

    if not wallet_cred_id:
        LOG.error(
            "[%s] No wallet credential matching cred_def_id=%s for referent %r pres_ex_id=%s "
            "within %.0fs (wrong/stale holder pres_ex is common if multiple request-received rows; "
            "or holder has no credential for this cred_def_id)",
            log_label,
            target_cred_def_id or "(unset)",
            _E2E_PROOF_ATTR_REFERENT,
            holder_pres_exchange_id,
            E2E_PROOF_HOLDER_CRED_MATCH_TIMEOUT_SEC,
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
    send_presentation_response = holder.post_present_proof_v2_send_presentation(
        holder_pres_exchange_id, pres_body
    )
    if not send_presentation_response.ok:
        log_http_failed("Holder send-presentation failed", send_presentation_response)
        return False

    def verifier_outcome() -> str | None:
        verifier_record_response = issuer.get_present_proof_v2_record(verifier_pres_ex_id)
        if not verifier_record_response.ok:
            return None
        try:
            verifier_exchange_payload = verifier_record_response.json()
        except json.JSONDecodeError:
            return None
        exchange_state = (verifier_exchange_payload.get("state") or "").lower()
        if exchange_state == "done":
            verified = _verified_is_true(verifier_exchange_payload.get("verified"))
            return "verified" if verified else "not_verified"
        if exchange_state == "abandoned":
            return "abandoned"
        return None

    presentation_outcome = poll_until(
        verifier_outcome,
        timeout_sec=proof_poll_timeout_sec,
        interval_sec=poll_interval_sec,
        description="verifier presentation exchange completed",
    )
    if presentation_outcome is None:
        return False

    if expect_verified and presentation_outcome != "verified":
        LOG.error("Expected verified proof, got outcome=%s", presentation_outcome)
        return False
    if expect_verified:
        LOG.info("Presentation verified as expected")
        return True

    if presentation_outcome not in ("not_verified", "abandoned"):
        LOG.error(
            "Expected unverifiable proof after revocation, got outcome=%s",
            presentation_outcome,
        )
        return False
    LOG.info("Presentation not verified after revocation (outcome=%s)", presentation_outcome)
    return True


def _verify_phase(
    context: Context,
    *,
    cred_def_attr: str,
    proof_name: str,
    expect_verified: bool,
    log_label: str,
) -> bool:
    cred_def_id = (getattr(context, cred_def_attr, None) or "").strip()
    if not cred_def_id:
        LOG.error("Missing %s", cred_def_attr)
        return False
    return _present_proof_round(
        context,
        cred_def_id=cred_def_id,
        proof_name=proof_name,
        expect_verified=expect_verified,
        log_label=log_label,
    )


def phase_verify_webvh(context: Context) -> bool:
    """WebVH: present-proof, expect verified."""
    return _verify_phase(
        context,
        cred_def_attr="webvh_cred_def_id",
        proof_name="WebVH E2E proof",
        expect_verified=True,
        log_label="webvh",
    )


def phase_verify_webvh_post_revoke(context: Context) -> bool:
    """WebVH: present-proof after revoke, expect not verified."""
    return _verify_phase(
        context,
        cred_def_attr="webvh_cred_def_id",
        proof_name="WebVH E2E proof",
        expect_verified=False,
        log_label="webvh",
    )


def phase_verify_indy(context: Context) -> bool:
    """Indy: present-proof, expect verified."""
    return _verify_phase(
        context,
        cred_def_attr="indy_cred_def_id",
        proof_name="Indy E2E proof",
        expect_verified=True,
        log_label="indy",
    )


def phase_verify_indy_post_revoke(context: Context) -> bool:
    """Indy: present-proof after revoke, expect not verified."""
    return _verify_phase(
        context,
        cred_def_attr="indy_cred_def_id",
        proof_name="Indy E2E proof",
        expect_verified=False,
        log_label="indy",
    )
