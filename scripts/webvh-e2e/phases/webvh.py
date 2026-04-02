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
    plugin_witness_id = plugin.get("witness_id")
    if isinstance(plugin_witness_id, str) and plugin_witness_id:
        if plugin_witness_id.startswith("did:key:"):
            return plugin_witness_id.replace("did:key:", "", 1)
        return plugin_witness_id
    for witness_did in plugin.get("witnesses") or []:
        if isinstance(witness_did, str) and witness_did.startswith("did:key:"):
            return witness_did.replace("did:key:", "", 1)
    return None


def _read_webvh_plugin(ctx: Context) -> bool:
    status_config_response = ctx.issuer_client().get_tenant_server_status_config()
    if not status_config_response.ok:
        LOG.error(
            "GET /tenant/server/status/config failed: %s %s",
            status_config_response.status_code,
            status_config_response.text[:500],
        )
        return False
    try:
        controller_config_json = status_config_response.json()
    except json.JSONDecodeError:
        LOG.error("GET /tenant/server/status/config returned non-JSON")
        return False

    plugin = get_plugin_webvh(controller_config_json)
    if not plugin:
        LOG.error(
            "did:webvh plugin missing from controller config (plugin_config.webvh / did-webvh)"
        )
        return False

    ctx.plugin_webvh = plugin
    ctx.webvh_server_url = plugin.get("server_url")
    witnesses = plugin.get("witnesses")
    if isinstance(witnesses, list):
        ctx.webvh_witnesses = [
            witness_did for witness_did in witnesses if isinstance(witness_did, str)
        ]

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
    witness_invitation_value = out.get("witness_invitation")
    if isinstance(witness_invitation_value, str) and witness_invitation_value:
        out["witness_invitation"] = f"<set, {len(witness_invitation_value)} chars>"
    if "scids" in out:
        out["scids"] = {}
    return out


def _format_webvh_config_json(data: Any) -> str:
    """Pretty JSON for logs (double quotes, indented)."""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def _fetch_stored_webvh_config(ctx: Context) -> dict[str, Any] | None:
    """GET /did/webvh/configuration (tenant-stored WebVH config)."""
    configuration_response = ctx.issuer_client().get_did_webvh_configuration()
    if not configuration_response.ok:
        LOG.warning(
            "GET /did/webvh/configuration failed: %s %s",
            configuration_response.status_code,
            configuration_response.text[:500],
        )
        return None
    try:
        stored_config = configuration_response.json()
    except json.JSONDecodeError:
        LOG.warning("GET /did/webvh/configuration returned non-JSON")
        return None
    return stored_config if isinstance(stored_config, dict) else None


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
        witness_oob_fragment = _witness_oob_id(plugin)
        if not witness_oob_fragment:
            LOG.error(
                "No witness_id or did:key witness in plugin; set WEBVH_WITNESS_INVITATION "
                "or ensure controller plugin_config lists a witness"
            )
            return False
        try:
            witness_invitation = build_witness_invitation_didcomm(
                server_url, witness_oob_fragment
            )
        except (requests.RequestException, OSError, ValueError) as err:
            LOG.error("Failed to build witness invitation: %s", err)
            return False

    body: dict[str, Any] = {
        "server_url": server_url,
        "witness": False,
        "witness_invitation": witness_invitation,
    }
    if ctx.use_witness:
        body["endorsement"] = True

    # Optional: persist witness_threshold under parameter_options when > 0 (merge with existing).
    parameter_options: dict[str, Any] = {}
    prior_stored_config = _fetch_stored_webvh_config(ctx)
    if isinstance(prior_stored_config, dict):
        existing_parameter_options = prior_stored_config.get("parameter_options")
        if isinstance(existing_parameter_options, dict):
            parameter_options.update(existing_parameter_options)
    witness_threshold = _witness_threshold_from_env()
    if witness_threshold > 0:
        parameter_options["witness_threshold"] = witness_threshold
    else:
        # Do not re-post a stale witness_threshold from GET merge when harness default is off.
        parameter_options.pop("witness_threshold", None)
    if parameter_options:
        body["parameter_options"] = parameter_options

    request_body_for_log = (
        _sanitized_webvh_config_for_log(body)
        if isinstance(body, dict)
        else body
    )

    post_configuration_response = ctx.issuer_client().post_did_webvh_configuration(
        body,
        log_body=request_body_for_log,
    )
    if not post_configuration_response.ok:
        response_text = post_configuration_response.text or ""
        LOG.error(
            "POST /did/webvh/configuration failed (HTTP %s)",
            post_configuration_response.status_code,
        )
        try:
            formatted_response_body = _format_webvh_config_json(json.loads(response_text))
        except (json.JSONDecodeError, TypeError):
            formatted_response_body = response_text[:2000] if response_text else "(empty body)"
        LOG.debug(
            "POST /did/webvh/configuration error response:\n%s",
            formatted_response_body,
        )
        return False

    try:
        response_body = post_configuration_response.json()
    except json.JSONDecodeError:
        LOG.error("POST /did/webvh/configuration returned non-JSON (HTTP 200)")
        LOG.debug(
            "POST /did/webvh/configuration raw text:\n%s",
            (post_configuration_response.text or "")[:4000],
        )
        return False

    if isinstance(response_body, dict) and response_body.get("status") == "error":
        LOG.error("POST /did/webvh/configuration returned status=error in JSON body")
        LOG.debug(
            "POST /did/webvh/configuration error body:\n%s",
            _format_webvh_config_json(response_body),
        )
        return False

    response_body_for_log = (
        _sanitized_webvh_config_for_log(response_body)
        if isinstance(response_body, dict)
        else response_body
    )
    LOG.info(
        "POST /did/webvh/configuration succeeded (HTTP %s)",
        post_configuration_response.status_code,
    )
    LOG.debug(
        "POST /did/webvh/configuration response:\n%s",
        _format_webvh_config_json(response_body_for_log),
    )
    return True


def phase_configure_webvh_plugin(ctx: Context) -> bool:
    """Load WebVH defaults from server config and POST /did/webvh/configuration (issuer)."""
    if not _read_webvh_plugin(ctx):
        return False
    return _post_webvh_configuration(ctx)


def _webvh_did_from_create_response(response_data: Any) -> str | None:
    """Best-effort DID string from ``POST /did/webvh/create`` JSON."""
    if not isinstance(response_data, dict) or response_data.get("status") == "error":
        return None
    state_block = response_data.get("state")
    if isinstance(state_block, dict):
        webvh_did = state_block.get("id")
        if isinstance(webvh_did, str) and webvh_did.startswith("did:webvh:"):
            return webvh_did
    did_document = response_data.get("didDocument") or response_data.get("document")
    if isinstance(did_document, dict):
        webvh_did = did_document.get("id")
        if isinstance(webvh_did, str) and webvh_did.startswith("did:webvh:"):
            return webvh_did
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

    stored_webvh_config = _fetch_stored_webvh_config(ctx)
    if stored_webvh_config:
        stored_server_url = stored_webvh_config.get("server_url")
        if isinstance(stored_server_url, str) and stored_server_url.strip():
            options["server_url"] = stored_server_url.strip()
    if "server_url" not in options and ctx.webvh_server_url:
        options["server_url"] = ctx.webvh_server_url.strip()

    ctx.webvh_last_create_namespace = namespace
    ctx.webvh_last_create_alias = alias
    ctx.webvh_last_create_server_url = options.get("server_url")

    body = {"options": options}

    create_response = ctx.issuer_client().post_did_webvh_create(body)
    if not create_response.ok:
        response_text = create_response.text or ""
        LOG.error(
            "POST /did/webvh/create failed (HTTP %s)",
            create_response.status_code,
        )
        try:
            formatted_response_body = _format_webvh_config_json(json.loads(response_text))
        except (json.JSONDecodeError, TypeError):
            formatted_response_body = response_text[:2000] if response_text else "(empty body)"
        LOG.debug(
            "POST /did/webvh/create error response:\n%s",
            formatted_response_body,
        )
        return False

    try:
        create_response_body = create_response.json()
    except json.JSONDecodeError:
        LOG.error("POST /did/webvh/create returned non-JSON (HTTP 200)")
        LOG.debug(
            "POST /did/webvh/create raw text:\n%s",
            (create_response.text or "")[:4000],
        )
        return False

    if create_response_body is None:
        LOG.info("POST /did/webvh/create succeeded (empty JSON body)")
        return True

    if isinstance(create_response_body, dict) and create_response_body.get("status") == "error":
        LOG.error("POST /did/webvh/create returned status=error in JSON body")
        LOG.debug(
            "POST /did/webvh/create error body:\n%s",
            _format_webvh_config_json(create_response_body),
        )
        return False

    LOG.info(
        "POST /did/webvh/create succeeded (HTTP %s)",
        create_response.status_code,
    )
    LOG.debug(
        "POST /did/webvh/create response:\n%s",
        _format_webvh_config_json(create_response_body),
    )

    created_webvh_did = _webvh_did_from_create_response(create_response_body)
    if created_webvh_did:
        ctx.webvh_last_created_did = created_webvh_did
    else:
        LOG.debug(
            "No did:webvh id in create response yet (e.g. pending witness); see run summary"
        )

    return True
