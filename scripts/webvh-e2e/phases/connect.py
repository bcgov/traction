"""Connection/configuration related phases."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from typing import Any

import requests

from context import Context, env_flag, get_plugin_webvh, holder_tenant_token, issuer_tenant_token
from harness_log import LOG, bold, detail_field_line, dim, headline_request, party_headline, wrap_dim_block
from helpers import build_witness_invitation, did_from_webvh_create_body
import records as rec

from .common import _ensure_wallet_anoncreds_session, _oob_invitation_issuer_did, fetch_server_config

def phase_oob_didexchange_webvh_didcomm(ctx: Context) -> bool:
    """OOB + DID Exchange **active**; issuer invitation uses ``use_did`` = WebVH DID (not did:peer / implicit peer)."""
    try:
        htok = holder_tenant_token()
    except RuntimeError as e:
        LOG.error("%s", e)
        return False
    if htok == issuer_tenant_token():
        LOG.error("TRACTION_HOLDER_TENANT_TOKEN must differ from TRACTION_ISSUER_TENANT_TOKEN.")
        return False

    holder_session = requests.Session()
    holder_session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {htok}",
        }
    )
    ctx.holder_session = holder_session
    issuer = ctx.issuer_client()
    holder = ctx.holder_client()

    if not _ensure_wallet_anoncreds_session(holder, party="holder"):
        return False

    issuer_alias = (os.environ.get("WEBVH_OOB_ISSUER_ALIAS") or "webvh-e2e-issuer").strip()
    holder_alias = (os.environ.get("WEBVH_OOB_HOLDER_ALIAS") or "webvh-e2e-holder").strip()
    multi_use = env_flag("WEBVH_OOB_MULTI_USE")
    my_label = (os.environ.get("WEBVH_OOB_ISSUER_LABEL") or "webvh-e2e-issuer").strip()
    goal = (os.environ.get("WEBVH_OOB_GOAL") or "WebVH E2E issuer–holder").strip()
    goal_code = (os.environ.get("WEBVH_OOB_GOAL_CODE") or "issue-vc").strip()

    issuer_invite_did = _oob_invitation_issuer_did(ctx)
    if not issuer_invite_did:
        LOG.error(
            "OOB invitation needs an issuer DID — run webvh-create in this profile first, "
            "or set WEBVH_OOB_USE_DID to an existing did:webvh in the issuer wallet."
        )
        return False

    # ACA-Py: ``use_did`` pins the inviter to this DID (did:webvh with DIDComm service),
    # instead of ``use_public_did: false`` which yields a did:peer-style invitation.
    create_body: dict[str, Any] = {
        "accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"],
        "alias": issuer_alias,
        "goal": goal,
        "goal_code": goal_code,
        "handshake_protocols": ["https://didcomm.org/didexchange/1.1"],
        "my_label": my_label,
        "protocol_version": "1.1",
        "use_did": issuer_invite_did,
    }
    LOG.info(
        "%s\n%s\n%s",
        headline_request("POST", "/out-of-band/create-invitation", role="issuer"),
        wrap_dim_block("alias", issuer_alias),
        wrap_dim_block("use_did", issuer_invite_did),
    )
    cr = issuer.post_out_of_band_create_invitation(create_body, multi_use=multi_use)
    if not cr.ok:
        LOG.error(
            "POST /out-of-band/create-invitation failed  HTTP %s  %s",
            cr.status_code,
            cr.text[:800],
        )
        return False
    try:
        created = cr.json()
    except json.JSONDecodeError:
        LOG.error("create-invitation response was not JSON")
        return False
    invitation = created.get("invitation") if isinstance(created, dict) else None
    if not isinstance(invitation, dict):
        LOG.error(
            "create-invitation missing invitation object (keys=%r)",
            list(created.keys()) if isinstance(created, dict) else type(created),
        )
        return False

    LOG.info(
        "%s\n%s",
        headline_request("POST", "/out-of-band/receive-invitation", role="holder"),
        wrap_dim_block("alias", holder_alias),
    )
    rr = holder.post_out_of_band_receive_invitation(invitation, alias=holder_alias)
    if not rr.ok:
        LOG.error(
            "POST /out-of-band/receive-invitation failed  HTTP %s  %s",
            rr.status_code,
            rr.text[:800],
        )
        return False
    try:
        received = rr.json()
    except json.JSONDecodeError:
        received = {}

    holder_cid: str | None = None
    if isinstance(received, dict):
        for key in ("connection_id", "connection_ids"):
            v = received.get(key)
            if isinstance(v, str) and v:
                holder_cid = v
                break
            if isinstance(v, list) and v and isinstance(v[0], str):
                holder_cid = v[0]
                break
        if not holder_cid:
            oob = received.get("oob_record")
            if isinstance(oob, dict):
                oc = oob.get("connection_id")
                if isinstance(oc, str) and oc:
                    holder_cid = oc
    if not holder_cid:
        time.sleep(1.0)
        holder_cid = rec.find_active_connection_id_by_alias(holder, holder_alias)
    if not holder_cid:
        LOG.error(
            "Could not determine holder connection_id after receive-invitation  %s",
            json.dumps(received, default=str)[:600],
        )
        return False

    if not rec.wait_connection_active(holder, holder_cid, party="holder"):
        return False
    ctx.oob_holder_connection_id = holder_cid

    try:
        poll_s = max(0.25, float((os.environ.get("WEBVH_CONNECT_POLL_SEC") or "1").strip()))
    except ValueError:
        poll_s = 1.0
    try:
        timeout_s = max(10.0, float((os.environ.get("WEBVH_CONNECT_TIMEOUT_SEC") or "120").strip()))
    except ValueError:
        timeout_s = 120.0
    deadline = time.time() + timeout_s
    issuer_cid: str | None = None
    while time.time() < deadline:
        issuer_cid = rec.find_active_connection_id_by_alias(issuer, issuer_alias)
        if issuer_cid:
            break
        time.sleep(poll_s)
    if not issuer_cid:
        LOG.error(
            "Could not find active issuer connection with alias %r before timeout",
            issuer_alias,
        )
        return False
    if not rec.wait_connection_active(issuer, issuer_cid, party="issuer"):
        return False
    ctx.oob_issuer_connection_id = issuer_cid

    LOG.info(
        "%s\n%s\n%s",
        f"{bold('DID Exchange')} {dim('active — issuer ↔ holder')}",
        wrap_dim_block("issuer_conn", issuer_cid),
        wrap_dim_block("holder_conn", holder_cid),
    )
    return True


def phase_smoke(ctx: Context) -> bool:
    live = ctx.issuer_client().get_status_live()
    if not live.ok:
        LOG.error(
            "GET /status/live failed  HTTP %s  %s",
            live.status_code,
            live.text[:500],
        )
        return False
    try:
        keys = list(fetch_server_config(ctx).keys())[:12]
    except requests.HTTPError as e:
        LOG.error("GET /tenant/server/status/config failed  %s", e)
        return False
    keys_s = ", ".join(repr(k) for k in keys) if keys else "—"
    LOG.info(
        "%s\n%s",
        headline_request("GET", "/status/live", subtitle="smoke check"),
        wrap_dim_block("response keys", keys_s),
    )
    return True


def phase_webvh_plugin(ctx: Context) -> bool:
    try:
        data = fetch_server_config(ctx)
    except requests.HTTPError as e:
        LOG.error("GET /tenant/server/status/config failed  %s", e)
        return False

    entry = get_plugin_webvh(data)
    server_url = (entry or {}).get("server_url")
    if not entry or not server_url:
        LOG.error("plugin_config has no webvh / did-webvh block or server_url")
        return False

    ctx.plugin_webvh = entry
    ctx.webvh_server_url = os.environ.get("WEBVH_SERVER_URL") or server_url
    w = entry.get("witnesses")
    if isinstance(w, list) and w:
        ctx.webvh_witnesses = [str(x) for x in w]
    elif entry.get("witness_id"):
        ctx.webvh_witnesses = [str(entry["witness_id"])]
    wit = (
        ", ".join(ctx.webvh_witnesses)
        if ctx.webvh_witnesses
        else "(none)"
    )
    LOG.info(
        "%s\n%s\n%s",
        headline_request("GET", "/tenant/server/status/config", subtitle="WebVH plugin"),
        wrap_dim_block("server_url", str(ctx.webvh_server_url)),
        wrap_dim_block("witnesses", wit),
    )
    return True


def _webvh_configure_controller_payload(
    ctx: Context, witness_invitation: str
) -> dict[str, Any]:
    """Plugin ``configure()``: witness false + invitation; ``endorsement`` follows ``--witness``."""
    return {
        "server_url": str(ctx.webvh_server_url),
        "witness": False,
        "endorsement": ctx.use_witness,
        "witness_invitation": witness_invitation.strip(),
    }


def phase_webvh_configure(ctx: Context) -> bool:
    if not ctx.plugin_webvh and not phase_webvh_plugin(ctx):
        return False

    override = (os.environ.get("WEBVH_WITNESS_INVITATION") or "").strip()
    if override:
        invitation = override
        source = "WEBVH_WITNESS_INVITATION"
    elif not ctx.webvh_witnesses:
        LOG.error(
            "plugin_config has no witnesses / witness_id; set WEBVH_WITNESS_INVITATION "
            "or fix server WebVH defaults."
        )
        return False
    else:
        try:
            invitation = build_witness_invitation(
                str(ctx.webvh_server_url),
                ctx.webvh_witnesses[0],
            )
        except (requests.RequestException, ValueError) as e:
            LOG.error(
                "Witness invitation fetch from %s failed: %s",
                ctx.webvh_server_url,
                e,
            )
            return False
        source = "WebVH server"

    LOG.info(
        "%s\n%s\n%s",
        headline_request("POST", "/did/webvh/configuration"),
        wrap_dim_block("invitation", source),
        detail_field_line(
            "endorsement",
            "on" if ctx.use_witness else "off",
            emphasis=ctx.use_witness,
        ),
    )
    payload = _webvh_configure_controller_payload(ctx, invitation)

    r = ctx.issuer_client().post_did_webvh_configuration(payload)
    if r.status_code not in (200, 201):
        LOG.error(
            "Configure failed  HTTP %s  %s",
            r.status_code,
            r.text[:800],
        )
        return False
    LOG.info(
        "%s\n%s",
        party_headline("issuer", "WebVH wallet configured"),
        wrap_dim_block("HTTP", str(r.status_code)),
    )
    return True


def phase_configure_webvh_plugin(ctx: Context) -> bool:
    """Read WebVH plugin defaults from tenant config, then configure the wallet (POST /did/webvh/configuration)."""
    if not phase_webvh_plugin(ctx):
        return False
    return phase_webvh_configure(ctx)

def phase_webvh_create(ctx: Context) -> bool:
    if not ctx.webvh_server_url and not phase_webvh_plugin(ctx):
        return False
    server_url = os.environ.get("WEBVH_SERVER_URL") or ctx.webvh_server_url
    alias = (os.environ.get("WEBVH_DID_ALIAS") or "").strip() or uuid.uuid4().hex[:8]
    namespace = (os.environ.get("WEBVH_NAMESPACE") or "webvh-e2e").strip()

    options: dict[str, Any] = {
        "identifier": alias,
        "namespace": namespace,
        "server_url": server_url,
    }
    if ctx.use_witness and ctx.webvh_witnesses:
        options["witnesses"] = ctx.webvh_witnesses
        options["witness"] = {"threshold": 1}

    # WebVH plugin: add DIDComm service to the DID doc so OOB / DID Exchange can use it.
    _didcomm_raw = (os.environ.get("WEBVH_CREATE_DIDCOMM") or "1").strip().lower()
    didcomm_on = _didcomm_raw not in ("0", "false", "no", "off")
    if didcomm_on:
        options["didcomm"] = True

    body = {"options": options}
    LOG.info(
        "%s\n%s\n%s\n%s\n%s",
        headline_request("POST", "/did/webvh/create", role="issuer"),
        detail_field_line("alias", alias, emphasis=True),
        detail_field_line("namespace", namespace),
        detail_field_line(
            "witness",
            "on" if ctx.use_witness else "off",
            emphasis=ctx.use_witness,
        ),
        detail_field_line("didcomm", "on" if didcomm_on else "off", emphasis=didcomm_on),
    )
    r = ctx.issuer_client().post_did_webvh_create(body)
    if r.status_code not in (200, 201):
        LOG.error(
            "Create DID failed  HTTP %s  %s",
            r.status_code,
            r.text[:800],
        )
        return False
    try:
        data = r.json()
    except json.JSONDecodeError:
        data = {}
    did = did_from_webvh_create_body(data)
    status = data.get("status") if isinstance(data, dict) else None
    message = data.get("message") if isinstance(data, dict) else None
    if did:
        ctx.webvh_issuer_did = did
        LOG.info(
            "%s\n%s",
            party_headline("issuer", "DID ready"),
            wrap_dim_block("did", did),
        )
    elif status == "pending" or message == "The witness is pending.":
        LOG.info(
            "%s  ·  %s",
            party_headline("issuer", "Create accepted"),
            dim("witness attestation pending — check Identifiers UI or /did/webvh/requests/…"),
        )
    elif status == "unknown":
        LOG.info(
            "%s  ·  %s",
            party_headline("issuer", "Create accepted"),
            dim("no immediate witness response — check witness queue or Identifiers UI"),
        )
    elif ctx.use_witness:
        LOG.info(
            "%s  ·  %s",
            party_headline("issuer", "Create accepted"),
            dim("DID not in body yet — witness may still attest"),
        )
    else:
        LOG.info(
            "%s  ·  %s",
            party_headline("issuer", "Create accepted"),
            dim("DID not in expected JSON fields — try -v for response keys"),
        )
    if not did and LOG.isEnabledFor(logging.DEBUG):
        LOG.debug(
            "create response JSON keys: %s",
            list(data) if isinstance(data, dict) else type(data),
        )
        if isinstance(data, dict):
            snippet = json.dumps(data, default=str)[:2000]
            LOG.debug("create response body (truncated): %s", snippet)
    return True
