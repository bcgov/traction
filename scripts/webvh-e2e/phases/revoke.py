"""Revoke-related phases."""

from __future__ import annotations

import json
import time
from typing import Any

from context import Context
from constants import (
    E2E_REVOKE_LEDGER_LOG_INTERVAL_SEC,
    E2E_REVOKE_LEDGER_POLL_SEC,
    E2E_REVOKE_LEDGER_TIMEOUT_SEC,
    E2E_REVOKE_NOTIFY,
    E2E_REVOKE_PUBLISH,
)
from helpers import LOG, log_http_failed, poll_until, v20_cred_ex_record_core


def _revocation_ids_from_flat_cred_ex(cred_ex_dict: dict[str, Any]) -> tuple[str | None, str | None]:
    """``rev_reg_id`` / ``cred_rev_id`` under ``anoncreds`` or ``indy`` on one record object."""
    for key in ("anoncreds", "indy"):
        block = cred_ex_dict.get(key)
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
    seen_object_ids: set[int] = set()
    for candidate in (detail, v20_cred_ex_record_core(detail)):
        candidate_id = id(candidate)
        if candidate_id in seen_object_ids:
            continue
        seen_object_ids.add(candidate_id)
        rev_reg_id, cred_rev_id = _revocation_ids_from_flat_cred_ex(candidate)
        if rev_reg_id and cred_rev_id:
            return rev_reg_id, cred_rev_id
    return None, None


def _ledger_revoked_cred_indices(payload: dict[str, Any]) -> set[int]:
    """Indices from ``GET …/issued/indy_recs`` ``rev_reg_delta.value.revoked``."""
    delta = payload.get("rev_reg_delta")
    if not isinstance(delta, dict):
        return set()
    value = delta.get("value")
    if not isinstance(value, dict):
        return set()
    raw = value.get("revoked")
    if not isinstance(raw, (list, tuple)):
        return set()
    revoked_indices: set[int] = set()
    for raw_index in raw:
        try:
            revoked_indices.add(int(raw_index))
        except (TypeError, ValueError):
            continue
    return revoked_indices


def _wait_for_revocation_on_ledger(
    client: Any,
    *,
    rev_reg_id: str,
    cred_rev_id: str,
    log_label: str,
) -> bool:
    """
    Poll ledger until ``cred_rev_id`` appears in the revocation registry delta.

    With ``publish: true`` the admin revoke call can still return before an endorser finishes
    writing the registry entry; verifiers read the ledger, so post-revoke proofs need this.
    """
    try:
        expected_cred_rev_index = int(str(cred_rev_id).strip())
    except ValueError:
        LOG.error("[%s] Invalid cred_rev_id for ledger wait: %r", log_label, cred_rev_id)
        return False

    last_progress_log = 0.0

    def maybe_progress(msg: str) -> None:
        nonlocal last_progress_log
        now = time.monotonic()
        if now - last_progress_log >= E2E_REVOKE_LEDGER_LOG_INTERVAL_SEC:
            last_progress_log = now
            LOG.info("[%s] %s", log_label, msg)

    LOG.info(
        "[%s] Waiting for cred_rev_id=%s on ledger (rev_reg_id=%s, timeout=%.0fs)",
        log_label,
        expected_cred_rev_index,
        rev_reg_id,
        E2E_REVOKE_LEDGER_TIMEOUT_SEC,
    )

    def fetch() -> bool | None:
        indy_recs_response = client.get_anoncreds_revocation_registry_issued_indy_recs(rev_reg_id)
        if not indy_recs_response.ok:
            maybe_progress(
                f"indy_recs HTTP {indy_recs_response.status_code} rev_reg_id={rev_reg_id} — still waiting"
            )
            return None
        try:
            indy_recs_payload = indy_recs_response.json()
        except json.JSONDecodeError:
            maybe_progress("indy_recs non-JSON — still waiting")
            return None
        if not isinstance(indy_recs_payload, dict):
            return None
        ledger_revoked = _ledger_revoked_cred_indices(indy_recs_payload)
        if expected_cred_rev_index in ledger_revoked:
            LOG.info(
                "[%s] Ledger shows cred_rev_id=%s revoked (rev_reg_id=%s)",
                log_label,
                expected_cred_rev_index,
                rev_reg_id,
            )
            return True
        maybe_progress(
            f"cred_rev_id={expected_cred_rev_index} not in ledger revoked set "
            f"{sorted(ledger_revoked)!r} (rev_reg_id={rev_reg_id})"
        )
        return None

    poll_result = poll_until(
        fetch,
        timeout_sec=E2E_REVOKE_LEDGER_TIMEOUT_SEC,
        interval_sec=E2E_REVOKE_LEDGER_POLL_SEC,
        description=(
            f"{log_label} revocation on ledger (rev_reg_id={rev_reg_id} "
            f"cred_rev_id={expected_cred_rev_index})"
        ),
    )
    if poll_result is True:
        return True
    LOG.error(
        "[%s] Timed out waiting for cred_rev_id=%s on ledger (rev_reg_id=%s)",
        log_label,
        expected_cred_rev_index,
        rev_reg_id,
    )
    return False


def _phase_revoke_issued_cred_ex(context: Context, *, log_label: str) -> bool:
    """POST /anoncreds/revocation/revoke for the last issued credential (publish)."""
    cred_ex_id = context.issuer_cred_ex_id
    if not cred_ex_id:
        LOG.error("[%s] No issuer cred_ex_id; run issue phase first", log_label)
        return False

    client = context.issuer_client()
    cred_ex_response = client.get_issue_credential_v2_record(cred_ex_id)
    if not cred_ex_response.ok:
        log_http_failed(
            f"GET /issue-credential-2.0/records/{cred_ex_id} failed; cannot revoke",
            cred_ex_response,
            max_body=2000,
        )
        return False
    try:
        detail = cred_ex_response.json()
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
        log_http_failed("POST /anoncreds/revocation/revoke failed", response)
        return False
    try:
        payload = response.json()
    except json.JSONDecodeError:
        payload = {}
    LOG.info("[%s] Revoked credential cred_ex_id=%s", log_label, cred_ex_id)
    LOG.debug("revoke response: %s", payload)

    wait_rev_reg, wait_cred_rev = rev_reg_id, cred_rev_id
    if (not wait_rev_reg or not wait_cred_rev) and E2E_REVOKE_PUBLISH:
        cred_ex_refresh_response = client.get_issue_credential_v2_record(cred_ex_id)
        if cred_ex_refresh_response.ok:
            try:
                refreshed_detail = cred_ex_refresh_response.json()
            except json.JSONDecodeError:
                refreshed_detail = None
            if isinstance(refreshed_detail, dict):
                wait_rev_reg, wait_cred_rev = _revocation_ids_from_cred_ex_payload(refreshed_detail)

    # Indy BCovrin: endorser can return from revoke before the delta is readable on-ledger; WebVH paths
    # use a different registry — ``indy_recs`` is not applicable there.
    if (
        log_label == "indy"
        and E2E_REVOKE_PUBLISH
        and wait_rev_reg
        and wait_cred_rev
    ):
        if not _wait_for_revocation_on_ledger(
            client,
            rev_reg_id=wait_rev_reg,
            cred_rev_id=wait_cred_rev,
            log_label=log_label,
        ):
            return False

    return True


def phase_revoke_webvh(context: Context) -> bool:
    """Revoke credential from WebVH issue flow."""
    return _phase_revoke_issued_cred_ex(context, log_label="webvh")


def phase_revoke_indy(context: Context) -> bool:
    """Revoke credential from Indy issue flow."""
    return _phase_revoke_issued_cred_ex(context, log_label="indy")
