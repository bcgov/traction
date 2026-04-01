"""Issue-related phases."""

from __future__ import annotations

import json
import logging
import os

from context import Context
from polling import poll_until

LOG = logging.getLogger("webvh-e2e")


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
            "POST /issue-credential-2.0/send-offer failed: %s %s",
            offer_response.status_code,
            (offer_response.text or "")[:800],
        )
        return False

    try:
        offer_record = offer_response.json()
    except json.JSONDecodeError:
        LOG.error("send-offer returned non-JSON")
        return False
    issuer_cred_ex_id = offer_record.get("cred_ex_id")
    if not issuer_cred_ex_id:
        LOG.error("send-offer response missing cred_ex_id: %s", offer_record)
        return False
    issuer_cred_ex_id = str(issuer_cred_ex_id)

    poll_sec = float(os.environ.get("WEBVH_E2E_ISSUE_POLL_SEC", "2"))
    timeout_sec = float(os.environ.get("WEBVH_E2E_ISSUE_TIMEOUT_SEC", "180"))

    def holder_offer_cred_ex_id() -> str | None:
        records = holder.get_issue_credential_v2_records(
            params={
                "role": "holder",
                "state": "offer-received",
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
            cid = row.get("cred_ex_id")
            if cid:
                return str(cid)
        return None

    holder_cred_ex_id = poll_until(
        holder_offer_cred_ex_id,
        timeout_sec=timeout_sec,
        interval_sec=poll_sec,
        description="holder credential exchange (offer-received)",
    )
    if not holder_cred_ex_id:
        return False

    send_req = holder.post_issue_credential_v2_send_request(holder_cred_ex_id)
    if not send_req.ok:
        LOG.error(
            "Holder send-request failed: %s %s",
            send_req.status_code,
            (send_req.text or "")[:600],
        )
        return False

    def issuer_cred_ex_done() -> bool | None:
        response = issuer.get_issue_credential_v2_record(issuer_cred_ex_id)
        if not response.ok:
            return None
        try:
            row = response.json()
        except json.JSONDecodeError:
            return None
        state = (row.get("state") or "").lower()
        if state in ("done", "credential-issued", "credential-acked"):
            return True
        if state in ("abandoned", "credential-revoked"):
            LOG.error("Issuer cred exchange entered failure state: %s", state)
            return False
        return None

    done = poll_until(
        lambda: issuer_cred_ex_done(),
        timeout_sec=timeout_sec,
        interval_sec=poll_sec,
        description="issuer credential exchange completed",
    )
    if done is not True:
        return False

    ctx.issuer_cred_ex_id = issuer_cred_ex_id
    LOG.info("Issued credential; issuer cred_ex_id=%s", issuer_cred_ex_id)
    return True


def phase_issue_indy(_ctx: Context) -> bool:
    return _placeholder_phase("issue-indy")
