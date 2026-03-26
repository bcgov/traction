"""Issue-related WebVH phases."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from context import Context
from harness_log import LOG, detail_field_line, dim, headline_request, party_headline, wrap_dim_block
import records as rec

from .common import (
    _attach_holder_session,
    _issue_credential_attributes,
    _issuer_holder_connection_ids,
)

def phase_issue_webvh(ctx: Context) -> bool:
    """AnonCreds **issue-credential 2.0** (WebVH ``cred_def_id``): issuer ``send-offer``, holder ``send-request``, poll **done**."""
    issuer_conn, holder_conn = _issuer_holder_connection_ids(ctx)
    if not issuer_conn or not holder_conn:
        LOG.error(
            "Missing connection ids — run oob-didexchange-webvh-didcomm in the same session, or set "
            "WEBVH_ISSUE_ISSUER_CONNECTION_ID and WEBVH_ISSUE_HOLDER_CONNECTION_ID."
        )
        return False
    if not ctx.anoncreds_cred_def_id:
        LOG.error("Missing anoncreds_cred_def_id — run publish-cred-def-webvh first.")
        return False
    if not _attach_holder_session(ctx) or ctx.holder_session is None:
        return False
    issuer = ctx.issuer_client()
    holder = ctx.holder_client()

    attrs, err = _issue_credential_attributes()
    if err:
        LOG.error("%s", err)
        return False
    assert attrs is not None

    try:
        poll_s = max(0.25, float((os.environ.get("WEBVH_ISSUE_POLL_SEC") or "1").strip()))
    except ValueError:
        poll_s = 1.0
    try:
        timeout_s = max(30.0, float((os.environ.get("WEBVH_ISSUE_TIMEOUT_SEC") or "180").strip()))
    except ValueError:
        timeout_s = 180.0

    auto_issue = True
    _ai = (os.environ.get("WEBVH_ISSUE_AUTO_ISSUE") or "").strip().lower()
    if _ai in ("0", "false", "no", "off"):
        auto_issue = False

    anon_filter: dict[str, Any] = {"cred_def_id": ctx.anoncreds_cred_def_id}
    if ctx.anoncreds_schema_id:
        anon_filter["schema_id"] = ctx.anoncreds_schema_id

    offer_body: dict[str, Any] = {
        "auto_issue": auto_issue,
        "auto_remove": False,
        "connection_id": issuer_conn,
        "credential_preview": {
            "@type": "issue-credential/2.0/credential-preview",
            "attributes": attrs,
        },
        "filter": {"anoncreds": anon_filter},
        "trace": False,
    }

    LOG.info(
        "%s\n%s\n%s",
        headline_request(
            "POST",
            "/issue-credential-2.0/send-offer",
            role="issuer",
            subtitle="AnonCreds",
        ),
        wrap_dim_block("connection", issuer_conn),
        wrap_dim_block("cred_def_id", ctx.anoncreds_cred_def_id),
    )
    so = issuer.post_issue_credential_v20_send_offer(offer_body)
    if not so.ok:
        LOG.error(
            "POST /issue-credential-2.0/send-offer failed  HTTP %s  %s",
            so.status_code,
            so.text[:800],
        )
        return False
    try:
        offer_resp = so.json()
    except json.JSONDecodeError:
        LOG.error("send-offer response was not JSON")
        return False
    item = offer_resp.get("item") if isinstance(offer_resp, dict) else None
    issuer_cex = rec.cred_ex_id_from_send_offer_item(item if isinstance(item, dict) else offer_resp)
    if not issuer_cex:
        LOG.error(
            "send-offer response missing cred_ex_id  %s",
            json.dumps(offer_resp, default=str)[:800],
        )
        return False
    ctx.issuer_cred_ex_id = issuer_cex

    thread_id: str | None = None
    if isinstance(item, dict):
        inner_offer = rec.inner_cred_ex_record(item) or item
        tid = inner_offer.get("thread_id")
        if isinstance(tid, str) and tid.strip():
            thread_id = tid.strip()
    if not thread_id:
        thread_id = rec.issuer_thread_id_after_offer(issuer, issuer_cex)
    if thread_id and LOG.isEnabledFor(logging.DEBUG):
        LOG.debug("Issuer cred exchange thread_id=%s", thread_id)

    LOG.info(
        "%s\n%s\n%s",
        party_headline("issuer", "Waiting for holder offer-received"),
        wrap_dim_block("connection", holder_conn),
        wrap_dim_block("thread_id", thread_id or "—"),
    )
    deadline = time.time() + timeout_s
    holder_cex: str | None = None
    skip_holder_send_request = False
    last_progress = 0.0
    while time.time() < deadline:
        rows = rec.holder_cred_ex_inner_records(holder)
        for hrow in rows:
            cid_ok = hrow.get("connection_id") == holder_conn
            thread_ok = bool(thread_id and hrow.get("thread_id") == thread_id)
            if not cid_ok and not thread_ok:
                continue
            st = rec.norm_cred_ex_state(hrow.get("state"))
            hc = hrow.get("cred_ex_id")
            if not isinstance(hc, str) or not hc:
                continue
            if st == "offer-received":
                holder_cex = hc
                if not cid_ok and thread_ok:
                    LOG.info(
                        "%s",
                        dim("Matched holder cred exchange by thread_id (connection_id differed)"),
                    )
                break
            if st in ("request-sent", "request-received", "credential-issued", "done"):
                holder_cex = hc
                skip_holder_send_request = True
                LOG.info(
                    "%s  ·  %s",
                    dim(f"Holder cred exchange already {st}"),
                    dim("skipping send-request"),
                )
                if not cid_ok and thread_ok:
                    LOG.info(
                        "%s",
                        dim("Matched holder cred exchange by thread_id (connection_id differed)"),
                    )
                break
        if holder_cex:
            break
        now = time.time()
        if now - last_progress >= 12.0:
            last_progress = now
            samples = [
                (
                    str(r.get("cred_ex_id") or "")[:8] + "…",
                    rec.norm_cred_ex_state(r.get("state")),
                    str(r.get("connection_id") or "")[:8] + "…" if r.get("connection_id") else "—",
                )
                for r in rows[:6]
            ]
            ir = rec.get_v20_cred_ex_inner(issuer, issuer_cex)
            iss_st = rec.norm_cred_ex_state(ir.get("state")) if ir else "?"
            LOG.info(
                "%s\n%s\n%s",
                dim("Still waiting — cred exchange poll"),
                detail_field_line("issuer state", iss_st),
                detail_field_line("holder sample", repr(samples) if samples else "(none)"),
            )
        time.sleep(poll_s)
    if not holder_cex:
        rows = rec.holder_cred_ex_inner_records(holder)
        LOG.error(
            "Timed out waiting for holder offer-received. "
            "Issuer thread_id=%r  holder_conn=%r  holder rows=%s",
            thread_id,
            holder_conn,
            [
                {
                    "cred_ex_id": r.get("cred_ex_id"),
                    "state": r.get("state"),
                    "connection_id": r.get("connection_id"),
                    "thread_id": r.get("thread_id"),
                }
                for r in rows
            ],
        )
        return False
    ctx.holder_cred_ex_id = holder_cex

    if not skip_holder_send_request:
        LOG.info(
            "%s\n%s",
            headline_request(
                "POST",
                "/issue-credential-2.0/records/{id}/send-request",
                role="holder",
            ),
            wrap_dim_block("holder_cred_ex", holder_cex),
        )
        sr = holder.post_issue_credential_v20_send_request(holder_cex)
        if not sr.ok:
            LOG.error(
                "POST holder send-request failed  HTTP %s  %s",
                sr.status_code,
                sr.text[:800],
            )
            return False

    LOG.info(
        "%s",
        dim("Waiting — issuer + holder cred_ex → done"),
    )
    deadline = time.time() + timeout_s
    issuer_done = holder_done = False
    last_issuer_st = last_holder_st = None
    while time.time() < deadline:
        if not issuer_done:
            ir = rec.get_v20_cred_ex_inner(issuer, issuer_cex)
            if ir:
                last_issuer_st = ir.get("state")
                if (last_issuer_st or "").lower() == "done":
                    issuer_done = True
                elif (last_issuer_st or "").lower() == "abandoned":
                    LOG.error("Issuer cred exchange abandoned")
                    return False
        if not holder_done:
            hr = rec.get_v20_cred_ex_inner(holder, holder_cex)
            if hr:
                last_holder_st = hr.get("state")
                if (last_holder_st or "").lower() == "done":
                    holder_done = True
                elif (last_holder_st or "").lower() == "abandoned":
                    LOG.error("Holder cred exchange abandoned")
                    return False
        if issuer_done and holder_done:
            LOG.info(
                "%s\n%s\n%s",
                party_headline("issuer", "Credential issued (v2)"),
                wrap_dim_block("issuer_cred_ex", issuer_cex),
                wrap_dim_block("holder_cred_ex", holder_cex),
            )
            return True
        time.sleep(poll_s)

    LOG.error(
        "Timed out waiting for done  issuer_state=%r holder_state=%r",
        last_issuer_st,
        last_holder_st,
    )
    return False


def phase_issue_indy(_ctx: Context) -> bool:
    LOG.warning(
        "issue-indy (non-WebVH Indy path) not implemented — use issue-webvh; Indy E2E TBD (DITP#136)"
    )
    return True


