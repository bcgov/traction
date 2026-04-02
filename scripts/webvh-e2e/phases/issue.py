"""Issue-related phases."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from context import Context
from polling import poll_until

LOG = logging.getLogger("webvh-e2e")


def _format_json_log(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def _issuer_thread_id(offer_record: dict[str, Any]) -> str | None:
    """Thread id to correlate issuer ↔ holder credential exchange records."""
    tid = offer_record.get("thread_id") or offer_record.get("parent_thread_id")
    return str(tid) if tid else None


def _v20_cred_ex_record_core(row: Any) -> dict[str, Any]:
    """
    ACA-Py often wraps the v2.0 credential exchange in ``cred_ex_record`` (``V20CredExRecordDetail``):
    applies to **list** ``GET /issue-credential-2.0/records`` and **single-record** GET by id.
    """
    if not isinstance(row, dict):
        return {}
    inner = row.get("cred_ex_record")
    if isinstance(inner, dict):
        return inner
    return row


def _holder_rows_match_thread(rows: list[dict[str, Any]], thread_id: str | None) -> list[dict[str, Any]]:
    if not thread_id:
        return list(rows)
    out: list[dict[str, Any]] = []
    for row in rows:
        core = _v20_cred_ex_record_core(row)
        if core.get("thread_id") == thread_id or core.get("parent_thread_id") == thread_id:
            out.append(row)
    return out


def _placeholder_phase(phase_name: str) -> bool:
    LOG.info("%s phase is not implemented yet.", phase_name)
    return True


def _credential_preview_attributes() -> list[dict[str, str]]:
    raw = (os.environ.get("WEBVH_E2E_CRED_VALUES") or "").strip()
    if raw:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            LOG.error("WEBVH_E2E_CRED_VALUES must be JSON object of attr -> value")
            return []
        if not isinstance(data, dict):
            return []
        return [{"name": str(k), "value": str(v)} for k, v in data.items()]
    return [
        {"name": "name", "value": "WebVH E2E"},
        {"name": "score", "value": "42"},
    ]


def phase_issue_webvh(ctx: Context) -> bool:
    """
    Issuer: POST /issue-credential-2.0/send-offer (anoncreds, auto_issue).

    Holder: POST …/send-request when offer is received.
    Poll until issuer exchange reaches a terminal issued state.
    """
    if not ctx.webvh_cred_def_id or not ctx.issuer_connection_id:
        LOG.error("Missing cred_def_id or issuer connection; run prior phases")
        return False

    issuer = ctx.issuer_client()
    holder = ctx.holder_client()
    attrs = _credential_preview_attributes()
    if not attrs:
        return False

    offer_body = {
        "auto_issue": True,
        "auto_remove": False,
        "connection_id": ctx.issuer_connection_id,
        "credential_preview": {
            "@type": "issue-credential/2.0/credential-preview",
            "attributes": attrs,
        },
        "filter": {"anoncreds": {"cred_def_id": ctx.webvh_cred_def_id}},
        "trace": False,
    }
    offer_response = issuer.post_issue_credential_v2_send_offer(offer_body)
    if not offer_response.ok:
        LOG.error(
            "POST /issue-credential-2.0/send-offer failed (HTTP %s)",
            offer_response.status_code,
        )
        LOG.debug(
            "send-offer error body:\n%s",
            (offer_response.text or "")[:4000],
        )
        return False

    try:
        offer_record = offer_response.json()
    except json.JSONDecodeError:
        LOG.error("send-offer returned non-JSON")
        return False
    LOG.debug(
        "POST /issue-credential-2.0/send-offer response:\n%s",
        _format_json_log(offer_record),
    )

    offer_core = _v20_cred_ex_record_core(offer_record)
    raw_cred_ex_id = offer_record.get("cred_ex_id") or offer_core.get("cred_ex_id")
    if not raw_cred_ex_id:
        LOG.error("send-offer response missing cred_ex_id")
        LOG.debug("send-offer body:\n%s", _format_json_log(offer_record))
        return False
    issuer_cred_ex_id = str(raw_cred_ex_id)
    thread_id = _issuer_thread_id(offer_record) or _issuer_thread_id(offer_core)
    if thread_id:
        LOG.info("Credential exchange thread_id=%s (for holder correlation)", thread_id)

    poll_sec = float(os.environ.get("WEBVH_E2E_ISSUE_POLL_SEC", "2"))
    timeout_sec = float(os.environ.get("WEBVH_E2E_ISSUE_TIMEOUT_SEC", "300"))
    diag_interval = 30.0
    last_diag = time.monotonic()

    # Do not filter GET by state=offer-received — some agents omit rows or move state quickly.
    def holder_exchange_status() -> str | None:
        nonlocal last_diag
        records = holder.get_issue_credential_v2_records(
            params={
                "role": "holder",
                "connection_id": ctx.holder_connection_id,
            }
        )
        if not records.ok:
            if time.monotonic() - last_diag >= diag_interval:
                last_diag = time.monotonic()
                LOG.warning(
                    "Holder GET /issue-credential-2.0/records failed: %s %s",
                    records.status_code,
                    (records.text or "")[:500],
                )
            return None
        try:
            payload = records.json()
        except json.JSONDecodeError:
            return None
        rows = payload.get("results") or []
        candidates = _holder_rows_match_thread(rows, thread_id)
        if not candidates and rows:
            candidates = rows

        if time.monotonic() - last_diag >= diag_interval:
            last_diag = time.monotonic()
            summary = []
            for r in candidates[:8]:
                c = _v20_cred_ex_record_core(r)
                summary.append(
                    (c.get("cred_ex_id"), (c.get("state") or "").lower(), c.get("thread_id"))
                )
            LOG.info(
                "Waiting for holder credential exchange (connection_id=%s); "
                "matching rows (up to 8): %s",
                ctx.holder_connection_id,
                summary,
            )

        for row in candidates:
            core = _v20_cred_ex_record_core(row)
            state = (core.get("state") or "").lower()
            cid = core.get("cred_ex_id")
            if not cid:
                continue
            if state == "offer-received":
                return f"send:{cid}"
            if state in ("done", "credential-received"):
                return f"done:{cid}"

        return None

    holder_outcome = poll_until(
        holder_exchange_status,
        timeout_sec=timeout_sec,
        interval_sec=poll_sec,
        description="holder credential exchange (offer-received or already done)",
    )
    if not holder_outcome:
        LOG.error(
            "Timed out waiting for holder exchange. Check DIDComm delivery and that "
            "holder_connection_id matches the connection used after OOB receive."
        )
        return False

    if holder_outcome.startswith("send:"):
        holder_cred_ex_id = holder_outcome.split(":", 1)[1]
        LOG.info("Holder cred_ex_id=%s state=offer-received; POST send-request", holder_cred_ex_id)
        send_req = holder.post_issue_credential_v2_send_request(holder_cred_ex_id)
        if not send_req.ok:
            LOG.error(
                "Holder POST /issue-credential-2.0/records/…/send-request failed (HTTP %s)",
                send_req.status_code,
            )
            LOG.debug(
                "send-request error body:\n%s",
                (send_req.text or "")[:4000],
            )
            return False
        LOG.info(
            "Holder send-request accepted (HTTP %s); polling issuer until terminal state",
            send_req.status_code,
        )
        try:
            LOG.debug(
                "Holder send-request response:\n%s",
                _format_json_log(send_req.json()),
            )
        except json.JSONDecodeError:
            pass
    elif holder_outcome.startswith("done:"):
        LOG.info(
            "Holder exchange already terminal before send-request (auto-handled or fast path); "
            "cred_ex_id=%s",
            holder_outcome.split(":", 1)[1],
        )
    else:
        LOG.error("Unexpected holder outcome: %s", holder_outcome)
        return False

    issuer_terminal = frozenset(
        {
            "done",
            "credential-issued",
            "credential-acked",
            "credential-received",
        }
    )

    def issuer_cred_ex_done() -> bool | None:
        nonlocal last_diag
        response = issuer.get_issue_credential_v2_record(issuer_cred_ex_id)
        if not response.ok:
            if time.monotonic() - last_diag >= diag_interval:
                last_diag = time.monotonic()
                LOG.warning(
                    "Issuer GET /issue-credential-2.0/records/%s failed: %s",
                    issuer_cred_ex_id,
                    response.status_code,
                )
            return None
        try:
            row = response.json()
        except json.JSONDecodeError:
            return None
        core = _v20_cred_ex_record_core(row)
        state = (core.get("state") or "").lower()
        if state in issuer_terminal:
            LOG.info("Issuer cred_ex_id=%s state=%s (terminal)", issuer_cred_ex_id, state)
            return True
        if state in ("abandoned", "credential-revoked", "deleted"):
            LOG.error("Issuer cred exchange entered failure state: %s", state)
            return False
        if time.monotonic() - last_diag >= diag_interval:
            last_diag = time.monotonic()
            LOG.info(
                "Waiting for issuer credential exchange (cred_ex_id=%s state=%s)",
                issuer_cred_ex_id,
                state or "?",
            )
        return None

    last_diag = time.monotonic()
    done = poll_until(
        lambda: issuer_cred_ex_done(),
        timeout_sec=timeout_sec,
        interval_sec=poll_sec,
        description="issuer credential exchange completed",
    )
    if done is not True:
        # Final snapshot for debugging
        snap = issuer.get_issue_credential_v2_record(issuer_cred_ex_id)
        if snap.ok:
            try:
                snap_row = snap.json()
                snap_core = _v20_cred_ex_record_core(snap_row)
                st = (snap_core.get("state") or "") if snap_core else ""
                LOG.error(
                    "Issuer exchange still not terminal (cred_ex_id=%s state=%s)",
                    issuer_cred_ex_id,
                    st or "?",
                )
                LOG.debug(
                    "Issuer last record:\n%s",
                    _format_json_log(snap_row),
                )
            except json.JSONDecodeError:
                pass
        return False

    ctx.issuer_cred_ex_id = issuer_cred_ex_id
    LOG.info("Issued credential; issuer cred_ex_id=%s", issuer_cred_ex_id)
    return True


def phase_issue_indy(_ctx: Context) -> bool:
    return _placeholder_phase("issue-indy")
