#!/usr/bin/env python3
"""
Traction WebVH E2E harness — HTTP checks against the tenant proxy.

See README.md for environment variables, phases, and profiles.

Default run: ``--profile all`` (every registered phase, including the Indy placeholder).
Use ``--profile new-issuer-webvh`` for the new-issuer WebVH path only.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import secrets
import time
import uuid
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from context import (
    Context,
    build_context,
    env_flag,
    get_plugin_webvh,
    holder_tenant_token,
    issuer_tenant_token,
)
from harness_log import (
    LOG,
    bold,
    detail_field_line,
    dim,
    headline_request,
    party_headline,
    phase_banner,
    run_summary_standout,
    setup_logging,
    wrap_dim_block,
)
from helpers import build_witness_invitation, did_from_webvh_create_body, parse_schema_attr_names
from traction_client import TractionClient, encode_anoncreds_path_segment

import records as rec


def _settings_wallet_type(settings: dict[str, Any]) -> str | None:
    """``wallet.type`` from ``GET /settings`` (top-level dotted key or nested ``wallet.type``)."""
    v = settings.get("wallet.type")
    if v is not None:
        return str(v)
    nested = (settings.get("wallet") or {}) if isinstance(settings.get("wallet"), dict) else {}
    t = nested.get("type")
    return str(t) if t is not None else None


def fetch_server_config(ctx: Context) -> dict[str, Any]:
    r = ctx.issuer_client().get_tenant_server_status_config()
    r.raise_for_status()
    return r.json()


def _ensure_wallet_anoncreds_session(c: TractionClient, *, party: str) -> bool:
    """Ensure wallet is ``askar-anoncreds`` for the given tenant session."""
    r = c.get_settings()
    if not r.ok:
        LOG.error(
            "GET /settings failed  HTTP %s  %s",
            r.status_code,
            r.text[:500],
        )
        return False
    try:
        settings = r.json()
    except json.JSONDecodeError:
        LOG.error("GET /settings response was not JSON")
        return False
    if not isinstance(settings, dict):
        LOG.error("GET /settings expected a JSON object")
        return False

    wt = _settings_wallet_type(settings)
    if wt == "askar-anoncreds":
        LOG.info(
            "%s\n%s",
            party_headline(party, "Wallet already askar-anoncreds"),
            wrap_dim_block("wallet.type", wt),
        )
        return True

    LOG.info(
        "%s\n%s",
        party_headline(party, "Starting AnonCreds wallet upgrade"),
        detail_field_line("wallet.type", repr(wt)),
    )
    tw = c.get_tenant_wallet()
    if not tw.ok:
        LOG.error(
            "GET /tenant/wallet failed  HTTP %s  %s",
            tw.status_code,
            tw.text[:500],
        )
        return False
    try:
        tw_body = tw.json()
    except json.JSONDecodeError:
        LOG.error("GET /tenant/wallet response was not JSON")
        return False
    wname = ((tw_body.get("settings") or {}) if isinstance(tw_body, dict) else {}).get(
        "wallet.name"
    )
    if not wname or not str(wname).strip():
        LOG.error("GET /tenant/wallet missing settings.wallet.name; cannot upgrade")
        return False
    wname = str(wname).strip()
    up = c.post_anoncreds_wallet_upgrade(wname)
    if not up.ok:
        low = (up.text or "").lower()
        if "already" not in low:
            LOG.error(
                "POST /anoncreds/wallet/upgrade failed  HTTP %s  %s",
                up.status_code,
                up.text[:500],
            )
            return False
        LOG.debug("upgrade endpoint reported already in progress or done: %s", up.text[:300])

    try:
        poll_s = max(0.25, float((os.environ.get("WEBVH_WALLET_UPGRADE_POLL_SEC") or "1").strip()))
    except ValueError:
        poll_s = 1.0
    try:
        timeout_s = max(5.0, float((os.environ.get("WEBVH_WALLET_UPGRADE_TIMEOUT_SEC") or "180").strip()))
    except ValueError:
        timeout_s = 180.0
    deadline = time.time() + timeout_s
    last_seen: str | None = wt
    while time.time() < deadline:
        time.sleep(poll_s)
        pr = c.get_settings()
        if not pr.ok:
            LOG.debug("poll GET /settings HTTP %s", pr.status_code)
            continue
        try:
            ps = pr.json()
        except json.JSONDecodeError:
            continue
        if not isinstance(ps, dict):
            continue
        last_seen = _settings_wallet_type(ps)
        if last_seen == "askar-anoncreds":
            LOG.info(
                "%s\n%s",
                party_headline(party, "Wallet upgraded to askar-anoncreds"),
                wrap_dim_block("wallet.type", last_seen),
            )
            return True

    LOG.error(
        "%s",
        party_headline(
            party,
            f"Wallet still not askar-anoncreds after {int(timeout_s)}s (last wallet.type={last_seen!r})",
            bold_message=False,
        ),
    )
    return False


def phase_upgrade_anoncreds_wallet(ctx: Context) -> bool:
    """Ensure issuer wallet is ``askar-anoncreds`` (``GET /settings``, upgrade + poll if needed)."""
    return _ensure_wallet_anoncreds_session(ctx.issuer_client(), party="issuer")


def _anoncreds_non_revoked_interval() -> dict[str, int]:
    """Interval for ``non_revoked`` on proof attributes (ledger revocation checks)."""
    now = int(time.time())
    return {"from": 0, "to": now + 300}


def _build_anoncreds_proof_request_for_webvh(
    ctx: Context,
    *,
    proof_name: str | None = None,
    include_non_revoked: bool = True,
) -> tuple[dict[str, Any], tuple[str, ...]] | None:
    """AnonCreds presentation request body + ordered attribute referent keys."""
    if not ctx.anoncreds_cred_def_id:
        return None
    names = parse_schema_attr_names(os.environ.get("WEBVH_SCHEMA_ATTRS"))
    restriction: dict[str, str] = {"cred_def_id": ctx.anoncreds_cred_def_id}
    if ctx.anoncreds_schema_id:
        restriction["schema_id"] = ctx.anoncreds_schema_id
    req_attrs: dict[str, Any] = {}
    keys: list[str] = []
    nr = _anoncreds_non_revoked_interval() if include_non_revoked else None
    for i, attr in enumerate(names):
        ref = f"webvh_req_{i}_{attr}"
        keys.append(ref)
        spec: dict[str, Any] = {"names": [attr], "restrictions": [dict(restriction)]}
        if nr is not None:
            spec["non_revoked"] = dict(nr)
        req_attrs[ref] = spec
    pn = (proof_name or (os.environ.get("WEBVH_VERIFY_PROOF_NAME") or "webvh-e2e-proof")).strip()
    nonce = str(secrets.randbelow(10**18) + 1)
    anoncreds: dict[str, Any] = {
        "name": pn,
        "version": "1.0",
        "nonce": nonce,
        "requested_attributes": req_attrs,
        "requested_predicates": {},
    }
    return anoncreds, tuple(keys)


def _issue_credential_attributes() -> tuple[list[dict[str, str]] | None, str | None]:
    """Build ``credential_preview.attributes`` aligned with ``WEBVH_SCHEMA_ATTRS``."""
    names = parse_schema_attr_names(os.environ.get("WEBVH_SCHEMA_ATTRS"))
    jraw = (os.environ.get("WEBVH_ISSUE_VALUES_JSON") or "").strip()
    if jraw:
        try:
            obj = json.loads(jraw)
        except json.JSONDecodeError as e:
            return None, f"WEBVH_ISSUE_VALUES_JSON is not valid JSON ({e})"
        if not isinstance(obj, dict):
            return None, "WEBVH_ISSUE_VALUES_JSON must be a JSON object"
        attrs: list[dict[str, str]] = []
        for n in names:
            if n not in obj:
                return None, f"WEBVH_ISSUE_VALUES_JSON missing key {n!r}"
            attrs.append({"name": n, "value": str(obj[n])})
        return attrs, None
    raw_vals = (os.environ.get("WEBVH_ISSUE_VALUES") or "").strip()
    if raw_vals:
        parts = [p.strip() for p in raw_vals.split(",")]
        if len(parts) != len(names):
            return (
                None,
                f"WEBVH_ISSUE_VALUES has {len(parts)} comma-separated parts "
                f"but schema has {len(names)} attributes",
            )
        return [{"name": n, "value": v} for n, v in zip(names, parts)], None
    defaults: dict[str, str] = {"name": "WebVH E2E Holder", "score": "95"}
    return [{"name": n, "value": defaults.get(n, "n/a")} for n in names], None


def _attach_holder_session(ctx: Context) -> bool:
    if ctx.holder_session is not None:
        return True
    try:
        htok = holder_tenant_token()
    except RuntimeError as e:
        LOG.error("%s", e)
        return False
    hs = requests.Session()
    hs.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {htok}",
        }
    )
    ctx.holder_session = hs
    return True


def _issuer_holder_connection_ids(ctx: Context) -> tuple[str | None, str | None]:
    ic = (
        ctx.oob_issuer_connection_id
        or (os.environ.get("WEBVH_ISSUE_ISSUER_CONNECTION_ID") or "").strip()
    )
    hc = (
        ctx.oob_holder_connection_id
        or (os.environ.get("WEBVH_ISSUE_HOLDER_CONNECTION_ID") or "").strip()
    )
    return (ic or None, hc or None)


def _oob_invitation_issuer_did(ctx: Context) -> str | None:
    """DID embedded in the issuer OOB invitation: created WebVH DID, or ``WEBVH_OOB_USE_DID`` override."""
    override = (os.environ.get("WEBVH_OOB_USE_DID") or "").strip()
    if override:
        return override
    return ctx.webvh_issuer_did


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


def _anoncreds_issuer_id(ctx: Context) -> str | None:
    """Schema and cred-def ``issuerId``: WebVH DID from create, or ``WEBVH_SCHEMA_ISSUER_ID``."""
    v = (os.environ.get("WEBVH_SCHEMA_ISSUER_ID") or "").strip() or ctx.webvh_issuer_did
    return v or None


def _revocation_ids_from_issuer_record(rec: dict[str, Any]) -> tuple[str | None, str | None]:
    """``revoc_reg_def.id`` (definition) and ``revoc_reg_id`` (issuer registry / entry handle)."""
    rdef = rec.get("revoc_reg_def")
    def_id = rdef.get("id") if isinstance(rdef, dict) else None
    if def_id is not None:
        def_id = str(def_id)
    reg_id = rec.get("revoc_reg_id")
    if reg_id is not None:
        reg_id = str(reg_id)
    return def_id, reg_id


# IssuerRevRegRecord uses ``active``; some AnonCreds / resolver paths report ``finished`` when published.
_REV_REG_LEDGER_READY_STATES = frozenset({"active", "finished"})


def _active_registry_http_retryable(status: int) -> bool:
    """Treat rate-limit and server errors like \"not ready\" and keep polling."""
    return status == 429 or 500 <= status <= 599


def _issuer_rev_reg_record_like(d: dict[str, Any]) -> bool:
    """True if ``d`` looks like an ACA-Py IssuerRevRegRecord (not a random nested dict)."""
    rdef = d.get("revoc_reg_def")
    if isinstance(rdef, dict) and rdef.get("id"):
        return True
    def_id, reg_id = _revocation_ids_from_issuer_record(d)
    return bool(def_id and reg_id)


def _deep_find_issuer_rev_reg_record(obj: Any, depth: int = 0) -> dict[str, Any] | None:
    if depth > 12 or not isinstance(obj, (dict, list)):
        return None
    if isinstance(obj, dict):
        if _issuer_rev_reg_record_like(obj):
            return obj
        for v in obj.values():
            found = _deep_find_issuer_rev_reg_record(v, depth + 1)
            if found:
                return found
        return None
    for item in obj:
        found = _deep_find_issuer_rev_reg_record(item, depth + 1)
        if found:
            return found
    return None


def _try_revocation_record_via_cred_def_get(
    ctx: Context, cred_def_id: str
) -> dict[str, Any] | None:
    """If ``active-registry`` fails, try ``GET /anoncreds/credential-definition/...`` for embedded rev-reg data."""
    try:
        r = ctx.issuer_client().get_anoncreds_credential_definition(cred_def_id)
    except requests.RequestException as exc:
        LOG.debug("cred-def GET (rev fallback): %s", exc)
        return None
    if r.status_code != 200:
        LOG.debug("cred-def GET (rev fallback) HTTP %s", r.status_code)
        return None
    try:
        body = r.json()
    except json.JSONDecodeError:
        return None
    rec = _deep_find_issuer_rev_reg_record(body)
    if rec:
        st = rec.get("state")
        if st in _REV_REG_LEDGER_READY_STATES or st is None:
            return rec
        def_id, reg_id = _revocation_ids_from_issuer_record(rec)
        if def_id and reg_id:
            LOG.debug(
                "cred-def GET (rev fallback) accepting state=%r (have rev def + reg ids)",
                st,
            )
            return rec
        LOG.debug("cred-def GET (rev fallback) record state=%r (not ledger-ready)", st)
    return None


def _wait_active_revocation_registry(
    ctx: Context, cred_def_id: str
) -> dict[str, Any] | None:
    """Poll active-registry until revocation is ledger-ready (``active`` or ``finished``)."""
    try:
        attempts = max(1, int((os.environ.get("WEBVH_REV_ACTIVE_WAIT_ATTEMPTS") or "30").strip()))
    except ValueError:
        attempts = 30
    try:
        delay = max(0.1, float((os.environ.get("WEBVH_REV_ACTIVE_WAIT_SEC") or "1").strip()))
    except ValueError:
        delay = 1.0
    last: dict[str, Any] | None = None
    last_state: str | None = None
    last_retryable_status: int | None = None
    ic = ctx.issuer_client()
    for i in range(attempts):
        try:
            r = ic.get_anoncreds_revocation_active_registry(cred_def_id)
        except requests.RequestException as exc:
            LOG.debug("active-registry attempt %s: %s", i + 1, exc)
            time.sleep(delay)
            continue
        if r.status_code == 404:
            LOG.debug("active-registry HTTP 404 (not ready), attempt %s", i + 1)
            time.sleep(delay)
            continue
        if _active_registry_http_retryable(r.status_code):
            last_retryable_status = r.status_code
            LOG.debug(
                "active-registry HTTP %s (retrying), attempt %s  %s",
                r.status_code,
                i + 1,
                r.text[:300],
            )
            time.sleep(delay)
            continue
        if r.status_code != 200:
            LOG.error(
                "GET /anoncreds/revocation/active-registry  HTTP %s  %s",
                r.status_code,
                r.text[:500],
            )
            return None
        try:
            body = r.json()
        except json.JSONDecodeError:
            time.sleep(delay)
            continue
        rec = body.get("result") if isinstance(body, dict) else None
        if not isinstance(rec, dict):
            time.sleep(delay)
            continue
        last = rec
        last_state = rec.get("state")
        if LOG.isEnabledFor(logging.DEBUG):
            LOG.debug("active-registry state=%r attempt %s", last_state, i + 1)
        if last_state in _REV_REG_LEDGER_READY_STATES:
            return rec
        time.sleep(delay)
    if last is not None:
        LOG.error(
            "Revocation registry not ledger-ready (want state in %s, last=%r)",
            sorted(_REV_REG_LEDGER_READY_STATES),
            last_state,
        )
    elif last_retryable_status is not None:
        LOG.error(
            "Revocation registry poll got only retryable HTTP errors from active-registry "
            "(last HTTP %s). Revocation may still be on the ledger; retry later or set "
            "WEBVH_REV_ACTIVE_SOFT_FAIL=1 to pass this phase without API confirmation.",
            last_retryable_status,
        )
    else:
        LOG.error("Revocation registry poll returned no record")
    return None


def phase_publish_schema(ctx: Context) -> bool:
    """POST /anoncreds/schema (AnonCreds) for **WebVH** ``issuerId``; same payload shape as Tenant UI for askar-anoncreds."""
    issuer_id = _anoncreds_issuer_id(ctx)
    if not issuer_id:
        LOG.error(
            "Schema needs issuerId: use the did:webvh from webvh-create (same run), "
            "or set WEBVH_SCHEMA_ISSUER_ID if create did not return a DID yet."
        )
        return False

    name = (os.environ.get("WEBVH_SCHEMA_NAME") or "webvh-e2e-preferences").strip()
    version = (os.environ.get("WEBVH_SCHEMA_VERSION") or "1.0").strip()
    attr_names = parse_schema_attr_names(os.environ.get("WEBVH_SCHEMA_ATTRS"))

    body: dict[str, Any] = {
        "schema": {
            "attrNames": attr_names,
            "issuerId": issuer_id,
            "name": name,
            "version": version,
        },
        "options": {},
    }
    LOG.info(
        "%s\n%s\n%s\n%s",
        headline_request("POST", "/anoncreds/schema", role="issuer"),
        detail_field_line("schema", f"{name} v{version}", emphasis=True),
        detail_field_line("attrs", repr(attr_names)),
        wrap_dim_block("issuer", issuer_id),
    )
    r = ctx.issuer_client().post_anoncreds_schema(body)
    if r.status_code not in (200, 201):
        LOG.error(
            "Schema publish failed  HTTP %s  %s",
            r.status_code,
            r.text[:800],
        )
        return False
    try:
        data = r.json()
    except json.JSONDecodeError:
        LOG.error("Schema response was not JSON")
        return False

    schema_state = (data.get("schema_state") or {}) if isinstance(data, dict) else {}
    state = schema_state.get("state")
    schema_id = schema_state.get("schema_id")
    job_id = data.get("job_id") if isinstance(data, dict) else None

    if state == "finished" and schema_id:
        ctx.anoncreds_schema_id = str(schema_id)
        LOG.info(
            "%s\n%s",
            party_headline("issuer", "Schema on ledger"),
            wrap_dim_block("schema_id", str(schema_id)),
        )
        return True

    LOG.error(
        "Schema incomplete  state=%r schema_id=%r job_id=%r  %s",
        state,
        schema_id,
        job_id,
        (r.text[:500] if r.text else ""),
    )
    return False


def phase_publish_cred_def(ctx: Context) -> bool:
    """POST /anoncreds/credential-definition with revocation (AnonCreds) on the **WebVH** schema."""
    if not ctx.anoncreds_schema_id:
        LOG.error(
            "Cred def needs schema_id from publish-schema-webvh in the same run "
            "(or run phases in order: … publish-schema-webvh publish-cred-def-webvh)."
        )
        return False
    issuer_id = _anoncreds_issuer_id(ctx)
    if not issuer_id:
        LOG.error(
            "Cred def needs issuerId (same did:webvh as schema / webvh-create, "
            "or WEBVH_SCHEMA_ISSUER_ID)."
        )
        return False

    tag = (os.environ.get("WEBVH_CRED_DEF_TAG") or "webvh-e2e").strip()
    raw_rr = (os.environ.get("WEBVH_REVOCATION_REGISTRY_SIZE") or "4").strip()
    try:
        revocation_registry_size = max(1, int(raw_rr))
    except ValueError:
        revocation_registry_size = 4

    body: dict[str, Any] = {
        "credential_definition": {
            "issuerId": issuer_id,
            "schemaId": ctx.anoncreds_schema_id,
            "tag": tag,
        },
        "options": {
            "support_revocation": True,
            "revocation_registry_size": revocation_registry_size,
        },
    }
    LOG.info(
        "%s\n%s\n%s\n%s",
        headline_request("POST", "/anoncreds/credential-definition", role="issuer"),
        detail_field_line("tag", tag, emphasis=True),
        detail_field_line(
            "revoke",
            f"on  (registry size {revocation_registry_size})",
        ),
        wrap_dim_block("schema", ctx.anoncreds_schema_id),
    )
    r = ctx.issuer_client().post_anoncreds_credential_definition(body)
    if r.status_code not in (200, 201):
        LOG.error(
            "Cred def publish failed  HTTP %s  %s",
            r.status_code,
            r.text[:800],
        )
        return False
    try:
        data = r.json()
    except json.JSONDecodeError:
        LOG.error("Cred def response was not JSON")
        return False

    cds = (data.get("credential_definition_state") or {}) if isinstance(data, dict) else {}
    state = cds.get("state")
    cred_def_id = cds.get("credential_definition_id")
    job_id = data.get("job_id") if isinstance(data, dict) else None

    if state == "finished" and cred_def_id:
        cid = str(cred_def_id)
        ctx.anoncreds_cred_def_id = cid
        LOG.info(
            "%s\n%s",
            party_headline("issuer", "Credential definition ready"),
            wrap_dim_block("cred_def_id", cid),
        )
        rev_rec = _wait_active_revocation_registry(ctx, cid)
        if not rev_rec:
            rev_rec = _try_revocation_record_via_cred_def_get(ctx, cid)
            if rev_rec:
                LOG.info(
                    "%s  ·  %s",
                    party_headline("issuer", "Revocation registry (fallback)"),
                    dim("GET /anoncreds/credential-definition — active-registry did not succeed"),
                )
        if not rev_rec:
            if env_flag("WEBVH_REV_ACTIVE_SOFT_FAIL"):
                LOG.warning(
                    "Could not read active revocation registry via tenant API "
                    "(active-registry may return 5xx for did:webvh cred def ids). "
                    "Continuing with WEBVH_REV_ACTIVE_SOFT_FAIL=1 — cred def is still "
                    "finished; confirm revocation on the ledger out of band if needed."
                )
                return True
            return False
        def_id, reg_id = _revocation_ids_from_issuer_record(rev_rec)
        if not def_id and not reg_id:
            LOG.error(
                "Active revocation record missing rev_reg_def.id and revoc_reg_id  %s",
                (json.dumps(rev_rec, default=str)[:800] if rev_rec else ""),
            )
            return False
        ctx.anoncreds_rev_reg_def_id = def_id or reg_id
        ctx.anoncreds_rev_reg_id = reg_id or def_id
        LOG.info(
            "%s\n%s\n%s\n%s",
            party_headline("issuer", "Revocation registry ready"),
            detail_field_line("state", str(rev_rec.get("state") or ""), emphasis=True),
            wrap_dim_block("rev_reg_def", def_id or reg_id or ""),
            wrap_dim_block("rev_reg_entry", reg_id or def_id or ""),
        )
        return True

    LOG.error(
        "Cred def incomplete  state=%r credential_definition_id=%r job_id=%r  %s",
        state,
        cred_def_id,
        job_id,
        (r.text[:500] if r.text else ""),
    )
    return False


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


PHASES: dict[str, Any] = {
    "smoke": phase_smoke,
    "upgrade-anoncreds-wallet": phase_upgrade_anoncreds_wallet,
    "configure-webvh-plugin": phase_configure_webvh_plugin,
    "webvh-create": phase_webvh_create,
    "publish-schema-webvh": phase_publish_schema,
    "publish-cred-def-webvh": phase_publish_cred_def,
    "oob-didexchange-webvh-didcomm": phase_oob_didexchange_webvh_didcomm,
    "issue-webvh": phase_issue_webvh,
    "verify-webvh": phase_verify_webvh,
    "revoke-webvh": phase_revoke_webvh,
    "verify-webvh-post-revoke": phase_verify_webvh_post_revoke,
    "issue-indy": phase_issue_indy,
}

# Curated path: new issuer, WebVH AnonCreds only (no Indy placeholder).
PROFILE_NEW_ISSUER_WEBVH: tuple[str, ...] = (
    "smoke",
    "upgrade-anoncreds-wallet",
    "configure-webvh-plugin",
    "webvh-create",
    "publish-schema-webvh",
    "publish-cred-def-webvh",
    "oob-didexchange-webvh-didcomm",
    "issue-webvh",
    "verify-webvh",
    "revoke-webvh",
    "verify-webvh-post-revoke",
)

# Every phase in PHASES, dependency order; profile ``all`` runs this tuple.
ALL_PHASES_ORDERED: tuple[str, ...] = PROFILE_NEW_ISSUER_WEBVH + ("issue-indy",)

PROFILES: dict[str, tuple[str, ...]] = {
    "all": ALL_PHASES_ORDERED,
    "new-issuer-webvh": PROFILE_NEW_ISSUER_WEBVH,
}

if set(ALL_PHASES_ORDERED) != set(PHASES.keys()):
    raise RuntimeError("ALL_PHASES_ORDERED must match PHASES keys exactly")


def _load_local_env() -> None:
    """Load ``scripts/webvh-e2e/.env`` if present (does not override existing OS env)."""
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.is_file():
        load_dotenv(env_file, override=False)


def main() -> int:
    _load_local_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=tuple(PROFILES.keys()),
        default="all",
        help=(
            "Phase bundle: ``all`` = every registered phase (default; includes ``issue-indy`` "
            "placeholder). ``new-issuer-webvh`` = smoke through revocation check "
            "(``verify-webvh-post-revoke``)."
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Debug logging",
    )
    parser.add_argument(
        "--witness",
        action="store_true",
        help=(
            "Include witnesses and witness threshold in POST /did/webvh/create "
            "(default: omit them for a no-witness create payload)"
        ),
    )
    args = parser.parse_args()
    setup_logging(verbose=args.verbose)

    try:
        ctx = build_context()
    except RuntimeError as e:
        LOG.error("%s", e)
        return 1
    ctx.use_witness = bool(args.witness)
    to_run = PROFILES[args.profile]
    run_desc = f"profile {args.profile}"

    LOG.info(
        "%s\n%s\n%s\n%s",
        bold("Run target"),
        wrap_dim_block("base_url", ctx.base_url),
        detail_field_line(
            "witness",
            "on" if ctx.use_witness else "off",
            emphasis=ctx.use_witness,
        ),
        detail_field_line("run", run_desc),
    )

    ok = True
    completed: list[str] = []
    failed_phase: str | None = None
    t0 = time.perf_counter()
    for name in to_run:
        phase_banner(name)
        fn = PHASES[name]
        try:
            if not fn(ctx):
                ok = False
                failed_phase = name
                break
        except RuntimeError as e:
            LOG.error("%s", e)
            ok = False
            failed_phase = name
            break
        except requests.RequestException as e:
            LOG.error("HTTP error in phase %r  %s", name, e)
            ok = False
            failed_phase = name
            break
        completed.append(name)

    run_summary_standout(
        ok=ok,
        base_url=ctx.base_url,
        witness=ctx.use_witness,
        n_done=len(completed),
        n_plan=len(to_run),
        elapsed_s=time.perf_counter() - t0,
        failed_phase=failed_phase,
        completed_phases=tuple(completed),
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
