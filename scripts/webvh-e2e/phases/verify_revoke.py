"""Proof verification and revoke phases for WebVH."""

from __future__ import annotations

import json
import os
import time
from typing import Any

from context import Context, env_flag
from harness_log import LOG, detail_field_line, dim, headline_request, party_headline, wrap_dim_block
import records as rec

from .common import (
    _attach_holder_session,
    _build_anoncreds_proof_request_for_webvh,
    _issuer_holder_connection_ids,
)

def _run_webvh_present_proof_round(
    ctx: Context,
    *,
    expect_verified: bool,
    proof_name: str,
    comment: str,
    include_non_revoked: bool,
) -> bool:
    """One present-proof **2.0** round; ``expect_verified`` False = assert verifier finishes **unverified** (revoked cred)."""
    issuer_conn, holder_conn = _issuer_holder_connection_ids(ctx)
    if not issuer_conn or not holder_conn:
        LOG.error(
            "Missing connection ids — run oob-didexchange-webvh-didcomm first or set "
            "WEBVH_ISSUE_ISSUER_CONNECTION_ID / WEBVH_ISSUE_HOLDER_CONNECTION_ID."
        )
        return False
    if not ctx.anoncreds_cred_def_id:
        LOG.error("Missing anoncreds_cred_def_id — run publish-cred-def-webvh (and issue-webvh) first.")
        return False
    if not _attach_holder_session(ctx) or ctx.holder_session is None:
        return False
    issuer = ctx.issuer_client()
    holder = ctx.holder_client()

    built = _build_anoncreds_proof_request_for_webvh(
        ctx,
        proof_name=proof_name,
        include_non_revoked=include_non_revoked,
    )
    if not built:
        return False
    anoncreds_req, referent_keys = built

    try:
        poll_s = max(0.25, float((os.environ.get("WEBVH_VERIFY_POLL_SEC") or "1").strip()))
    except ValueError:
        poll_s = 1.0
    try:
        timeout_s = max(30.0, float((os.environ.get("WEBVH_VERIFY_TIMEOUT_SEC") or "180").strip()))
    except ValueError:
        timeout_s = 180.0

    auto_verify = True
    _av = (os.environ.get("WEBVH_VERIFY_AUTO_VERIFY") or "").strip().lower()
    if _av in ("0", "false", "no", "off"):
        auto_verify = False

    cred_ref = rec.holder_wallet_cred_referent_for_cred_def(holder, ctx.anoncreds_cred_def_id)
    if not cred_ref:
        LOG.error(
            "Holder wallet has no credential for cred_def_id %r — run issue-webvh first.",
            ctx.anoncreds_cred_def_id[:80] + "…"
            if len(ctx.anoncreds_cred_def_id) > 80
            else ctx.anoncreds_cred_def_id,
        )
        return False

    subtitle = "verifier / issuer tenant"
    if include_non_revoked:
        subtitle += "  (non_revoked interval)"
    send_body: dict[str, Any] = {
        "connection_id": issuer_conn,
        "auto_verify": auto_verify,
        "comment": comment,
        "trace": False,
        "presentation_request": {"anoncreds": anoncreds_req},
    }
    LOG.info(
        "%s\n%s\n%s",
        headline_request(
            "POST",
            "/present-proof-2.0/send-request",
            role="issuer",
            subtitle=subtitle,
        ),
        wrap_dim_block("connection", issuer_conn),
        wrap_dim_block("proof_name", proof_name),
    )
    pr = issuer.post_present_proof_v20_send_request(send_body)
    if not pr.ok:
        LOG.error(
            "POST /present-proof-2.0/send-request failed  HTTP %s  %s",
            pr.status_code,
            pr.text[:800],
        )
        return False
    try:
        pres_resp = pr.json()
    except json.JSONDecodeError:
        LOG.error("send-request response was not JSON")
        return False
    item = pres_resp.get("item") if isinstance(pres_resp, dict) else None
    issuer_pres = rec.pres_ex_id_from_send_request_item(
        item if isinstance(item, dict) else pres_resp
    )
    if not issuer_pres:
        LOG.error(
            "send-request missing pres_ex_id  %s",
            json.dumps(pres_resp, default=str)[:800],
        )
        return False
    ctx.issuer_pres_ex_id = issuer_pres

    thread_id: str | None = None
    if isinstance(item, dict):
        inner_sr = rec.inner_pres_ex_record(item) or item
        tid = inner_sr.get("thread_id")
        if isinstance(tid, str) and tid.strip():
            thread_id = tid.strip()
    if not thread_id:
        thread_id = rec.issuer_pres_thread_after_send(issuer, issuer_pres)

    LOG.info(
        "%s\n%s\n%s",
        party_headline("issuer", "Waiting for prover request-received"),
        wrap_dim_block("connection", holder_conn),
        wrap_dim_block("thread_id", thread_id or "—"),
    )
    deadline = time.time() + timeout_s
    holder_pres: str | None = None
    skip_holder_send_presentation = False
    last_progress = 0.0
    while time.time() < deadline:
        rows = rec.holder_prover_pres_ex_inner_records(holder)
        for prow in rows:
            cid_ok = prow.get("connection_id") == holder_conn
            thread_ok = bool(thread_id and prow.get("thread_id") == thread_id)
            if not cid_ok and not thread_ok:
                continue
            st = rec.norm_cred_ex_state(prow.get("state"))
            pxid = prow.get("pres_ex_id")
            if not isinstance(pxid, str) or not pxid:
                continue
            if st == "request-received":
                holder_pres = pxid
                if not cid_ok and thread_ok:
                    LOG.info(
                        "%s",
                        dim(
                            "Matched prover presentation exchange by thread_id "
                            "(connection_id differed)"
                        ),
                    )
                break
            if st in (
                "presentation-sent",
                "presentation-received",
                "done",
            ):
                holder_pres = pxid
                skip_holder_send_presentation = True
                LOG.info(
                    "%s  ·  %s",
                    dim(f"Prover presentation exchange already {st}"),
                    dim("skipping send-presentation"),
                )
                break
        if holder_pres:
            break
        now = time.time()
        if now - last_progress >= 12.0:
            last_progress = now
            samples = [
                (
                    str(r.get("pres_ex_id") or "")[:8] + "…",
                    rec.norm_cred_ex_state(r.get("state")),
                )
                for r in rows[:6]
            ]
            vr = rec.get_v20_pres_ex_inner(issuer, issuer_pres)
            vs = rec.norm_cred_ex_state(vr.get("state")) if vr else "?"
            LOG.info(
                "%s\n%s\n%s",
                dim("Still waiting — presentation exchange poll"),
                detail_field_line("verifier state", vs),
                detail_field_line("prover sample", repr(samples) if samples else "(none)"),
            )
        time.sleep(poll_s)
    if not holder_pres:
        LOG.error(
            "Timed out waiting for prover request-received  thread_id=%r  holder_conn=%r",
            thread_id,
            holder_conn,
        )
        return False
    ctx.holder_pres_ex_id = holder_pres

    if not skip_holder_send_presentation:
        pres_spec: dict[str, Any] = {
            "anoncreds": {
                "requested_attributes": {
                    k: {"cred_id": cred_ref, "revealed": True} for k in referent_keys
                },
                "requested_predicates": {},
                "self_attested_attributes": {},
            }
        }
        LOG.info(
            "%s\n%s",
            headline_request(
                "POST",
                "/present-proof-2.0/records/{id}/send-presentation",
                role="holder",
            ),
            wrap_dim_block("holder_pres_ex", holder_pres),
        )
        sp = holder.post_present_proof_v20_send_presentation(holder_pres, pres_spec)
        if not sp.ok:
            LOG.error(
                "POST holder send-presentation failed  HTTP %s  %s",
                sp.status_code,
                sp.text[:800],
            )
            return False

    outcome = "verified + done" if expect_verified else "done (expect not verified)"
    LOG.info("%s", dim(f"Waiting — verifier presentation → {outcome}"))
    deadline = time.time() + timeout_s
    verify_called = False
    last_vst: str | None = None
    while time.time() < deadline:
        vrec = rec.get_v20_pres_ex_inner(issuer, issuer_pres)
        if vrec:
            last_vst = vrec.get("state")
            vst = rec.norm_cred_ex_state(last_vst)
            if vst == "abandoned":
                LOG.error(
                    "Presentation exchange abandoned  error_msg=%r",
                    vrec.get("error_msg"),
                )
                return False
            if not auto_verify and vst == "presentation-received" and not verify_called:
                LOG.info(
                    "%s",
                    headline_request(
                        "POST",
                        "/present-proof-2.0/records/{id}/verify-presentation",
                        role="issuer",
                    ),
                )
                vp = issuer.post_present_proof_v20_verify_presentation(issuer_pres)
                verify_called = True
                if not vp.ok:
                    LOG.error(
                        "POST verify-presentation failed  HTTP %s  %s",
                        vp.status_code,
                        vp.text[:800],
                    )
                    return False
                time.sleep(poll_s)
                continue
            if vst == "done":
                ok_ver = rec.presentation_record_verified(vrec)
                if expect_verified and ok_ver:
                    LOG.info(
                        "%s\n%s\n%s",
                        party_headline("issuer", "Presentation verified"),
                        wrap_dim_block("verifier_pres_ex", issuer_pres),
                        wrap_dim_block("prover_pres_ex", holder_pres),
                    )
                    return True
                if expect_verified and not ok_ver:
                    LOG.error(
                        "Expected verified presentation but verifier reported verified=%r",
                        vrec.get("verified"),
                    )
                    return False
                if not expect_verified and not ok_ver:
                    LOG.info(
                        "%s\n%s\n%s\n%s",
                        party_headline(
                            "issuer",
                            "Presentation not verified (expected after revoke)",
                        ),
                        wrap_dim_block("verifier_pres_ex", issuer_pres),
                        wrap_dim_block("prover_pres_ex", holder_pres),
                        wrap_dim_block("verified", str(vrec.get("verified"))),
                    )
                    return True
                if not expect_verified and ok_ver:
                    LOG.error(
                        "After revoke, expected verification to fail but verified=%r",
                        vrec.get("verified"),
                    )
                    return False
        time.sleep(poll_s)

    LOG.error(
        "Timed out waiting for presentation outcome  verifier_state=%r  auto_verify=%s  expect_verified=%s",
        last_vst,
        auto_verify,
        expect_verified,
    )
    return False


def phase_verify_webvh(ctx: Context) -> bool:
    """Present-proof **2.0** with **non_revoked** on requested attributes (revocation-aware verify)."""
    _nr = (os.environ.get("WEBVH_VERIFY_NON_REVOKED") or "1").strip().lower()
    include_nr = _nr not in ("0", "false", "no", "off")
    proof_name = (os.environ.get("WEBVH_VERIFY_PROOF_NAME") or "webvh-e2e-proof").strip()
    comment = (os.environ.get("WEBVH_VERIFY_COMMENT") or "webvh-e2e verify-webvh").strip()
    return _run_webvh_present_proof_round(
        ctx,
        expect_verified=True,
        proof_name=proof_name,
        comment=comment,
        include_non_revoked=include_nr,
    )


def phase_revoke_webvh(ctx: Context) -> bool:
    """``POST /anoncreds/revocation/revoke`` for the issued cred (by issuer ``cred_ex_id``); publishes by default."""
    cred_ex = (os.environ.get("WEBVH_REVOKE_CRED_EX_ID") or "").strip() or (ctx.issuer_cred_ex_id or "")
    if not cred_ex:
        LOG.error(
            "revoke-webvh needs issuer cred_ex_id — run issue-webvh first or set WEBVH_REVOKE_CRED_EX_ID."
        )
        return False
    issuer = ctx.issuer_client()
    try:
        poll_s = max(0.25, float((os.environ.get("WEBVH_REVOKE_RECORD_POLL_SEC") or "1").strip()))
    except ValueError:
        poll_s = 1.0
    try:
        timeout_s = max(15.0, float((os.environ.get("WEBVH_REVOKE_RECORD_TIMEOUT_SEC") or "90").strip()))
    except ValueError:
        timeout_s = 90.0
    rr_id, cr_id = rec.issuer_cred_rev_ids_from_cred_ex(
        issuer, cred_ex, poll_s=poll_s, timeout_s=timeout_s
    )
    if not rr_id or not cr_id:
        LOG.error(
            "Could not read revocation ids for cred_ex_id=%r via GET /anoncreds/revocation/credential-record",
            cred_ex,
        )
        return False

    publish = True
    _pub = (os.environ.get("WEBVH_REVOKE_PUBLISH") or "1").strip().lower()
    if _pub in ("0", "false", "no", "off"):
        publish = False

    # ACA-Py applies ``revocation.notify`` from agent settings when ``notify`` is omitted,
    # which then requires ``connection_id`` — always send an explicit boolean.
    body: dict[str, Any] = {
        "cred_ex_id": cred_ex,
        "publish": publish,
        "notify": False,
    }
    if env_flag("WEBVH_REVOKE_NOTIFY"):
        conn, _hc = _issuer_holder_connection_ids(ctx)
        ir = rec.get_v20_cred_ex_inner(issuer, cred_ex)
        tid = ir.get("thread_id") if ir else None
        if isinstance(conn, str) and conn and isinstance(tid, str) and tid.strip():
            body["notify"] = True
            body["connection_id"] = conn
            body["thread_id"] = tid.strip()
            body["notify_version"] = (os.environ.get("WEBVH_REVOKE_NOTIFY_VERSION") or "v2_0").strip()
        else:
            LOG.warning(
                "WEBVH_REVOKE_NOTIFY set but missing connection_id or thread_id — "
                "sending notify=false (override agent default)"
            )

    LOG.info(
        "%s\n%s\n%s\n%s\n%s\n%s",
        headline_request("POST", "/anoncreds/revocation/revoke", role="issuer"),
        wrap_dim_block("cred_ex_id", cred_ex),
        wrap_dim_block("rev_reg_id", rr_id),
        wrap_dim_block("cred_rev_id", cr_id),
        detail_field_line("publish", "true" if publish else "false", emphasis=publish),
        detail_field_line("notify", "true" if body.get("notify") else "false", emphasis=bool(body.get("notify"))),
    )
    rv = issuer.post_anoncreds_revocation_revoke(body)
    if not rv.ok:
        LOG.error(
            "POST /anoncreds/revocation/revoke failed  HTTP %s  %s",
            rv.status_code,
            rv.text[:800],
        )
        return False
    LOG.info("%s", party_headline("issuer", "Credential revoked (AnonCreds)"))
    return True


def phase_verify_webvh_post_revoke(ctx: Context) -> bool:
    """Second present-proof round: same **non_revoked** request; verifier must finish **unverified** (revoked)."""
    proof_name = (os.environ.get("WEBVH_VERIFY_POST_REVOKE_PROOF_NAME") or "webvh-e2e-proof-post-revoke").strip()
    comment = (
        os.environ.get("WEBVH_VERIFY_POST_REVOKE_COMMENT") or "webvh-e2e expect unverifiable (revoked)"
    ).strip()
    return _run_webvh_present_proof_round(
        ctx,
        expect_verified=False,
        proof_name=proof_name,
        comment=comment,
        include_non_revoked=True,
    )
