"""WebVH plugin configuration and DID create (issuer)."""

from __future__ import annotations

import json
import logging
import os
import secrets
import string
from typing import Any

import requests

from context import Context, get_plugin_webvh
from helpers import build_witness_invitation_didcomm

LOG = logging.getLogger("webvh-e2e")


def _witness_threshold_from_env() -> int:
    """``WEBVH_WITNESS_THRESHOLD`` when > 0: create ``options`` + configure ``parameter_options``."""
    try:
        return int(os.environ.get("WEBVH_WITNESS_THRESHOLD", "0"))
    except ValueError:
        return 0


def _random_webvh_alias(length: int) -> str:
    """URL-safe short id for ``options.identifier`` (lowercase letters + digits)."""
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _witness_oob_id(plugin: dict[str, Any]) -> str | None:
    """Fragment for ``/api/invitations?_oobid=`` (strip ``did:key:`` when present)."""
    wid = plugin.get("witness_id")
    if isinstance(wid, str) and wid:
        if wid.startswith("did:key:"):
            return wid.replace("did:key:", "", 1)
        return wid
    for w in plugin.get("witnesses") or []:
        if isinstance(w, str) and w.startswith("did:key:"):
            return w.replace("did:key:", "", 1)
    return None


def _read_webvh_plugin(ctx: Context) -> bool:
    r = ctx.issuer_client().get_tenant_server_status_config()
    if not r.ok:
        LOG.error(
            "GET /tenant/server/status/config failed: %s %s",
            r.status_code,
            r.text[:500],
        )
        return False
    try:
        cfg = r.json()
    except json.JSONDecodeError:
        LOG.error("GET /tenant/server/status/config returned non-JSON")
        return False

    plugin = get_plugin_webvh(cfg)
    if not plugin:
        LOG.error(
            "did:webvh plugin missing from controller config (plugin_config.webvh / did-webvh)"
        )
        return False

    ctx.plugin_webvh = plugin
    ctx.webvh_server_url = plugin.get("server_url")
    witnesses = plugin.get("witnesses")
    if isinstance(witnesses, list):
        ctx.webvh_witnesses = [w for w in witnesses if isinstance(w, str)]

    # Controller plugin_config only — tenant-stored config is logged on POST /did/webvh/configuration response.
    LOG.debug(
        "WebVH controller plugin_config (defaults): server_url=%s witness_id=%s witnesses=%s",
        ctx.webvh_server_url,
        plugin.get("witness_id"),
        ctx.webvh_witnesses,
    )
    return True


def _sanitized_webvh_config_for_log(cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Copy WebVH config for logging only: shorten ``witness_invitation``; clear ``scids`` mapping
    (SCID → DID can be sensitive / noisy in CI logs).
    """
    out: dict[str, Any] = dict(cfg)
    inv = out.get("witness_invitation")
    if isinstance(inv, str) and inv:
        out["witness_invitation"] = f"<set, {len(inv)} chars>"
    if "scids" in out:
        out["scids"] = {}
    return out


def _format_webvh_config_json(data: Any) -> str:
    """Pretty JSON for logs (double quotes, indented)."""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def _fetch_stored_webvh_config(ctx: Context) -> dict[str, Any] | None:
    """GET /did/webvh/configuration (tenant-stored WebVH config)."""
    r = ctx.issuer_client().get_did_webvh_configuration()
    if not r.ok:
        LOG.warning(
            "GET /did/webvh/configuration failed: %s %s",
            r.status_code,
            r.text[:500],
        )
        return None
    try:
        stored = r.json()
    except json.JSONDecodeError:
        LOG.warning("GET /did/webvh/configuration returned non-JSON")
        return None
    return stored if isinstance(stored, dict) else None


def _post_webvh_configuration(ctx: Context) -> bool:
    plugin = ctx.plugin_webvh
    if not plugin:
        LOG.error("Internal error: plugin_webvh not set")
        return False

    server_url = (ctx.webvh_server_url or plugin.get("server_url") or "").strip()
    if not server_url:
        LOG.error("WebVH server_url missing from plugin config")
        return False

    inv_env = (os.environ.get("WEBVH_WITNESS_INVITATION") or "").strip()
    if inv_env:
        witness_invitation = inv_env
    else:
        oob = _witness_oob_id(plugin)
        if not oob:
            LOG.error(
                "No witness_id or did:key witness in plugin; set WEBVH_WITNESS_INVITATION "
                "or ensure controller plugin_config lists a witness"
            )
            return False
        try:
            witness_invitation = build_witness_invitation_didcomm(server_url, oob)
        except (requests.RequestException, OSError, ValueError) as e:
            LOG.error("Failed to build witness invitation: %s", e)
            return False

    body: dict[str, Any] = {
        "server_url": server_url,
        "witness": False,
        "witness_invitation": witness_invitation,
    }
    if ctx.use_witness:
        body["endorsement"] = True

    # Optional: persist witness_threshold under parameter_options when > 0 (merge with existing).
    po: dict[str, Any] = {}
    prior_cfg = _fetch_stored_webvh_config(ctx)
    if isinstance(prior_cfg, dict):
        existing_po = prior_cfg.get("parameter_options")
        if isinstance(existing_po, dict):
            po.update(existing_po)
    wt = _witness_threshold_from_env()
    if wt > 0:
        po["witness_threshold"] = wt
    else:
        # Do not re-post a stale witness_threshold from GET merge when harness default is off.
        po.pop("witness_threshold", None)
    if po:
        body["parameter_options"] = po

    req_log = (
        _sanitized_webvh_config_for_log(body)
        if isinstance(body, dict)
        else body
    )
    LOG.info(
        "POST /did/webvh/configuration\nrequest:\n%s",
        _format_webvh_config_json(req_log),
    )

    r = ctx.issuer_client().post_did_webvh_configuration(body)
    if not r.ok:
        raw = r.text or ""
        try:
            resp_fmt = _format_webvh_config_json(json.loads(raw))
        except (json.JSONDecodeError, TypeError):
            resp_fmt = raw[:2000] if raw else "(empty body)"
        LOG.error(
            "POST /did/webvh/configuration (HTTP %s)\nresponse:\n%s",
            r.status_code,
            resp_fmt,
        )
        return False

    try:
        data = r.json()
    except json.JSONDecodeError:
        LOG.error(
            "POST /did/webvh/configuration\nresponse (non-JSON):\n%s",
            (r.text or "")[:2000],
        )
        return False

    if isinstance(data, dict) and data.get("status") == "error":
        LOG.error(
            "POST /did/webvh/configuration\nresponse:\n%s",
            _format_webvh_config_json(data),
        )
        return False

    resp_log = (
        _sanitized_webvh_config_for_log(data)
        if isinstance(data, dict)
        else data
    )
    LOG.info(
        "POST /did/webvh/configuration\nresponse:\n%s",
        _format_webvh_config_json(resp_log),
    )
    return True


def phase_configure_webvh_plugin(ctx: Context) -> bool:
    """Load WebVH defaults from server config and POST /did/webvh/configuration (issuer)."""
    if not _read_webvh_plugin(ctx):
        return False
    return _post_webvh_configuration(ctx)


def _webvh_did_from_create_response(data: Any) -> str | None:
    """Best-effort DID string from ``POST /did/webvh/create`` JSON."""
    if not isinstance(data, dict) or data.get("status") == "error":
        return None
    state = data.get("state")
    if isinstance(state, dict):
        did = state.get("id")
        if isinstance(did, str) and did.startswith("did:webvh:"):
            return did
    doc = data.get("didDocument") or data.get("document")
    if isinstance(doc, dict):
        did = doc.get("id")
        if isinstance(did, str) and did.startswith("did:webvh:"):
            return did
    return None


def phase_webvh_create(ctx: Context) -> bool:
    """
    ``POST /did/webvh/create`` with ``options`` (issuer).

    Expects tenant WebVH configuration from a prior ``configure-webvh-plugin`` run (same process)
    or from stored config on the agent. The path segment is sent as ``options.identifier``
    (ACA-Py / did-webvh field name). Default: random 8-character id; override with
    ``WEBVH_CREATE_ALIAS`` or ``WEBVH_CREATE_IDENTIFIER``. Auto-generated segment length is fixed (8).

    ``witness_threshold`` is sent only when ``WEBVH_WITNESS_THRESHOLD`` is a positive integer.
    Sends ``didcomm: true`` so the plugin adds a DIDComm service to the preliminary document.
    With ``apply_policy: true`` (default here, matching ACA-Py), options are merged with the
    WebVH server's identifier policy. Set ``WEBVH_CREATE_APPLY_POLICY=false`` to skip that merge.
    """
    namespace = (os.environ.get("WEBVH_CREATE_NAMESPACE") or "traction-e2e").strip() or "traction-e2e"
    alias = (
        (os.environ.get("WEBVH_CREATE_ALIAS") or os.environ.get("WEBVH_CREATE_IDENTIFIER") or "")
        .strip()
    )
    if not alias:
        alias = _random_webvh_alias(8)
    witness_threshold = _witness_threshold_from_env()

    apply_policy_env = (os.environ.get("WEBVH_CREATE_APPLY_POLICY") or "").strip().lower()
    apply_policy = apply_policy_env not in ("0", "false", "no", "off")

    options: dict[str, Any] = {
        "namespace": namespace,
        "identifier": alias,
        "apply_policy": apply_policy,
        "didcomm": True,
    }
    if witness_threshold > 0:
        options["witness_threshold"] = witness_threshold

    stored = _fetch_stored_webvh_config(ctx)
    if stored:
        su = stored.get("server_url")
        if isinstance(su, str) and su.strip():
            options["server_url"] = su.strip()
    if "server_url" not in options and ctx.webvh_server_url:
        options["server_url"] = ctx.webvh_server_url.strip()

    ctx.webvh_last_create_namespace = namespace
    ctx.webvh_last_create_alias = alias
    ctx.webvh_last_create_server_url = options.get("server_url")

    body = {"options": options}
    LOG.info(
        "POST /did/webvh/create\nrequest:\n%s",
        _format_webvh_config_json(body),
    )

    r = ctx.issuer_client().post_did_webvh_create(body)
    if not r.ok:
        raw = r.text or ""
        try:
            resp_fmt = _format_webvh_config_json(json.loads(raw))
        except (json.JSONDecodeError, TypeError):
            resp_fmt = raw[:2000] if raw else "(empty body)"
        LOG.error(
            "POST /did/webvh/create (HTTP %s)\nresponse:\n%s",
            r.status_code,
            resp_fmt,
        )
        return False

    try:
        data = r.json()
    except json.JSONDecodeError:
        LOG.error(
            "POST /did/webvh/create\nresponse (non-JSON):\n%s",
            (r.text or "")[:2000],
        )
        return False

    if data is None:
        LOG.info("POST /did/webvh/create\nresponse:\nnull")
        return True

    if isinstance(data, dict) and data.get("status") == "error":
        LOG.error(
            "POST /did/webvh/create\nresponse:\n%s",
            _format_webvh_config_json(data),
        )
        return False

    LOG.info(
        "POST /did/webvh/create\nresponse:\n%s",
        _format_webvh_config_json(data),
    )

    did = _webvh_did_from_create_response(data)
    if did:
        ctx.webvh_last_created_did = did
    else:
        LOG.debug(
            "No did:webvh id in create response yet (e.g. pending witness); see run summary"
        )

    return True
