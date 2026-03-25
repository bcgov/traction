"""Shared helpers for WebVH E2E phases."""

from __future__ import annotations

import json
import os
import secrets
import time
from typing import Any

import requests

from context import Context, holder_tenant_token
from harness_log import LOG, detail_field_line, party_headline, wrap_dim_block
from helpers import parse_schema_attr_names
from traction_client import TractionClient

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
