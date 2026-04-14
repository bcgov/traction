"""Issue-related phases."""

from __future__ import annotations

import json
import time
from typing import Any

from context import Context
from constants import (
    E2E_CREDENTIAL_PREVIEW_ATTRIBUTES,
    E2E_ISSUE_POLL_SEC,
    E2E_ISSUE_TIMEOUT_SEC,
)
from helpers import LOG, format_json_for_log, log_http_failed, poll_until, v20_cred_ex_record_core


def _issuer_manual_issue_poll_once(
    issuer: Any,
    issuer_cred_ex_id: str,
    issuer_terminal: frozenset[str],
) -> str | None:
    """Poll step for Indy manual issue: ``request-received``, ``terminal``, or still waiting."""
    issuer_record_response = issuer.get_issue_credential_v2_record(issuer_cred_ex_id)
    if not issuer_record_response.ok:
        return None
    try:
        issuer_cred_ex_core = v20_cred_ex_record_core(issuer_record_response.json())
    except json.JSONDecodeError:
        return None
    issuer_exchange_state = (issuer_cred_ex_core.get("state") or "").lower()
    if issuer_exchange_state == "request-received":
        return "request-received"
    if issuer_exchange_state in issuer_terminal:
        return "terminal"
    return None


def _issuer_thread_id(offer_record: dict[str, Any]) -> str | None:
    """Thread id to correlate issuer ↔ holder credential exchange records."""
    thread_identifier = offer_record.get("thread_id") or offer_record.get("parent_thread_id")
    return str(thread_identifier) if thread_identifier else None


def _holder_rows_match_thread(rows: list[dict[str, Any]], thread_id: str | None) -> list[dict[str, Any]]:
    if not thread_id:
        return list(rows)
    matching_rows: list[dict[str, Any]] = []
    for cred_ex_row in rows:
        cred_ex_core = v20_cred_ex_record_core(cred_ex_row)
        if cred_ex_core.get("thread_id") == thread_id or cred_ex_core.get("parent_thread_id") == thread_id:
            matching_rows.append(cred_ex_row)
    return matching_rows


def _phase_issue_anoncreds_cred_def(
    context: Context,
    cred_def_id: str,
    *,
    log_label: str,
    explicit_issue_fallback: bool = False,
) -> bool:
    """
    Issuer: POST /issue-credential-2.0/send-offer (anoncreds).

    WebVH uses ``auto_issue: true``. Indy uses ``auto_issue: false`` and a single
    ``POST …/issue`` after the holder’s ``send-request`` — Traction/BCovrin often leaves
    ``auto_issue`` stuck in ``request-received``, and a manual issue while ``auto_issue`` is
    true returns **400** and abandons the exchange.
    """
    if not cred_def_id or not context.issuer_connection_id:
        LOG.error("[%s] Missing cred_def_id or issuer connection; run prior phases", log_label)
        return False

    issuer = context.issuer_client()
    holder = context.holder_client()

    offer_body = {
        "auto_issue": not explicit_issue_fallback,
        "auto_remove": False,
        "connection_id": context.issuer_connection_id,
        "credential_preview": {
            "@type": "issue-credential/2.0/credential-preview",
            "attributes": E2E_CREDENTIAL_PREVIEW_ATTRIBUTES,
        },
        "filter": {"anoncreds": {"cred_def_id": cred_def_id}},
        "trace": False,
    }
    offer_response = issuer.post_issue_credential_v2_send_offer(offer_body)
    if not offer_response.ok:
        log_http_failed("POST /issue-credential-2.0/send-offer failed", offer_response)
        return False

    try:
        offer_record = offer_response.json()
    except json.JSONDecodeError:
        LOG.error("send-offer returned non-JSON")
        return False
    LOG.debug("POST /issue-credential-2.0/send-offer response:\n%s", format_json_for_log(offer_record))

    offer_core = v20_cred_ex_record_core(offer_record)
    raw_cred_ex_id = offer_record.get("cred_ex_id") or offer_core.get("cred_ex_id")
    if not raw_cred_ex_id:
        LOG.error("send-offer response missing cred_ex_id")
        LOG.debug("send-offer body:\n%s", format_json_for_log(offer_record))
        return False
    issuer_cred_ex_id = str(raw_cred_ex_id)
    thread_id = _issuer_thread_id(offer_record) or _issuer_thread_id(offer_core)
    if thread_id:
        LOG.info("Credential exchange thread_id=%s (for holder correlation)", thread_id)

    poll_sec = E2E_ISSUE_POLL_SEC
    timeout_sec = E2E_ISSUE_TIMEOUT_SEC
    diag_interval = 30.0
    last_diag = time.monotonic()

    issuer_terminal = frozenset(
        {
            "done",
            "credential-issued",
            "credential-acked",
            "credential-received",
        }
    )

    # Do not filter GET by state=offer-received — some agents omit rows or move state quickly.
    def holder_exchange_status() -> str | None:
        nonlocal last_diag
        records = holder.get_issue_credential_v2_records(
            params={
                "role": "holder",
                "connection_id": context.holder_connection_id,
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
            for cred_ex_row in candidates[:8]:
                cred_ex_core = v20_cred_ex_record_core(cred_ex_row)
                summary.append(
                    (
                        cred_ex_core.get("cred_ex_id"),
                        (cred_ex_core.get("state") or "").lower(),
                        cred_ex_core.get("thread_id"),
                    )
                )
            LOG.info(
                "Waiting for holder credential exchange (connection_id=%s); "
                "matching rows (up to 8): %s",
                context.holder_connection_id,
                summary,
            )

        for cred_ex_row in candidates:
            cred_ex_core = v20_cred_ex_record_core(cred_ex_row)
            holder_state = (cred_ex_core.get("state") or "").lower()
            holder_cred_ex_id = cred_ex_core.get("cred_ex_id")
            if not holder_cred_ex_id:
                continue
            if holder_state == "offer-received":
                return f"send:{holder_cred_ex_id}"
            if holder_state in ("done", "credential-received"):
                return f"done:{holder_cred_ex_id}"

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
            log_http_failed(
                "Holder POST /issue-credential-2.0/records/…/send-request failed", send_req
            )
            return False
        LOG.info(
            "Holder send-request accepted (HTTP %s); polling issuer until terminal state",
            send_req.status_code,
        )
        if explicit_issue_fallback:
            manual_phase = poll_until(
                lambda: _issuer_manual_issue_poll_once(
                    issuer, issuer_cred_ex_id, issuer_terminal
                ),
                timeout_sec=timeout_sec,
                interval_sec=poll_sec,
                description="issuer request-received for Indy manual issue",
            )
            if manual_phase == "request-received":
                issue_resp = issuer.post_issue_credential_v2_issue(issuer_cred_ex_id)
                if not issue_resp.ok:
                    log_http_failed(
                        f"[{log_label}] Issuer POST …/issue failed", issue_resp
                    )
                    return False
                LOG.info("[%s] Issuer POST …/issue accepted after holder send-request", log_label)
            elif manual_phase != "terminal":
                LOG.error(
                    "[%s] Issuer did not reach request-received for manual issue (got %s)",
                    log_label,
                    manual_phase,
                )
                return False

        try:
            LOG.debug("Holder send-request response:\n%s", format_json_for_log(send_req.json()))
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

    def issuer_cred_ex_done() -> bool | None:
        nonlocal last_diag
        issuer_record_response = issuer.get_issue_credential_v2_record(issuer_cred_ex_id)
        if not issuer_record_response.ok:
            if time.monotonic() - last_diag >= diag_interval:
                last_diag = time.monotonic()
                LOG.warning(
                    "Issuer GET /issue-credential-2.0/records/%s failed: %s",
                    issuer_cred_ex_id,
                    issuer_record_response.status_code,
                )
            return None
        try:
            issuer_record = issuer_record_response.json()
        except json.JSONDecodeError:
            return None
        issuer_cred_ex_core = v20_cred_ex_record_core(issuer_record)
        issuer_exchange_state = (issuer_cred_ex_core.get("state") or "").lower()

        if issuer_exchange_state in issuer_terminal:
            LOG.info(
                "Issuer cred_ex_id=%s state=%s (terminal)",
                issuer_cred_ex_id,
                issuer_exchange_state,
            )
            return True
        if issuer_exchange_state in ("abandoned", "credential-revoked", "deleted"):
            LOG.error("Issuer cred exchange entered failure state: %s", issuer_exchange_state)
            return False
        if time.monotonic() - last_diag >= diag_interval:
            last_diag = time.monotonic()
            LOG.info(
                "Waiting for issuer credential exchange (cred_ex_id=%s state=%s)",
                issuer_cred_ex_id,
                issuer_exchange_state or "?",
            )
        return None

    last_diag = time.monotonic()
    issuer_exchange_poll_result = poll_until(
        lambda: issuer_cred_ex_done(),
        timeout_sec=timeout_sec,
        interval_sec=poll_sec,
        description="issuer credential exchange completed",
    )
    if issuer_exchange_poll_result is not True:
        # Final snapshot for debugging
        final_issuer_record_response = issuer.get_issue_credential_v2_record(issuer_cred_ex_id)
        if final_issuer_record_response.ok:
            try:
                final_issuer_record = final_issuer_record_response.json()
                final_issuer_core = v20_cred_ex_record_core(final_issuer_record)
                final_issuer_state = (final_issuer_core.get("state") or "") if final_issuer_core else ""
                LOG.error(
                    "Issuer exchange still not terminal (cred_ex_id=%s state=%s)",
                    issuer_cred_ex_id,
                    final_issuer_state or "?",
                )
                LOG.debug("Issuer last record:\n%s", format_json_for_log(final_issuer_record))
            except json.JSONDecodeError:
                pass
        return False

    context.issuer_cred_ex_id = issuer_cred_ex_id
    LOG.info("[%s] Issued credential; issuer cred_ex_id=%s", log_label, issuer_cred_ex_id)
    return True


def _issue_phase(
    context: Context,
    *,
    cred_def_attr: str,
    publish_phase_hint: str,
    log_label: str,
    explicit_issue_fallback: bool,
) -> bool:
    cred_def_id = (getattr(context, cred_def_attr, None) or "").strip()
    if not cred_def_id:
        LOG.error("Missing %s; run %s first", cred_def_attr, publish_phase_hint)
        return False
    return _phase_issue_anoncreds_cred_def(
        context, cred_def_id, log_label=log_label, explicit_issue_fallback=explicit_issue_fallback
    )


def phase_issue_webvh(context: Context) -> bool:
    """AnonCreds issue using WebVH issuer cred def."""
    return _issue_phase(
        context,
        cred_def_attr="webvh_cred_def_id",
        publish_phase_hint="publish-cred-def-webvh",
        log_label="webvh",
        explicit_issue_fallback=False,
    )


def phase_issue_indy(context: Context) -> bool:
    """AnonCreds issue using Indy (BCovrin) issuer cred def."""
    return _issue_phase(
        context,
        cred_def_attr="indy_cred_def_id",
        publish_phase_hint="publish-cred-def-indy",
        log_label="indy",
        explicit_issue_fallback=True,
    )
