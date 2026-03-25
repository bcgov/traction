#!/usr/bin/env python3
"""
Traction WebVH E2E harness — HTTP checks against the tenant proxy.

See README.md for environment variables and phase list.
"""

from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

DEFAULT_BASE = "http://localhost:8032"
LOG = logging.getLogger("webvh-e2e")


@dataclass
class Context:
    base_url: str
    session: requests.Session
    webvh_server_url: str | None = None
    webvh_witnesses: list[str] = field(default_factory=list)
    plugin_webvh: dict[str, Any] | None = None
    #: When True, POST /did/webvh/create includes witnesses + witness threshold (Tenant UI style).
    use_witness: bool = False


def _normalize_base(url: str) -> str:
    return url.rstrip("/")


def _auth_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    api_key = os.environ.get("TRACTION_TENANT_API_KEY")
    token = os.environ.get("TRACTION_TENANT_TOKEN") or os.environ.get(
        "TRACTION_BEARER_TOKEN"
    )
    if api_key:
        headers["X-API-Key"] = api_key.strip()
    elif token:
        headers["Authorization"] = f"Bearer {token.strip()}"
    return headers


def build_context() -> Context:
    base = _normalize_base(
        os.environ.get("TRACTION_TENANT_PROXY_BASE", DEFAULT_BASE).strip()
    )
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **_auth_headers(),
        }
    )
    return Context(base_url=base, session=session)


def _require_tenant_auth() -> None:
    if not _auth_headers():
        raise RuntimeError(
            "Set TRACTION_TENANT_TOKEN (Bearer) or TRACTION_TENANT_API_KEY for this phase."
        )


def _get_plugin_webvh(config_json: dict[str, Any]) -> dict[str, Any] | None:
    cfg = (config_json or {}).get("config") or {}
    plugin = cfg.get("plugin_config") or {}
    return plugin.get("webvh") or plugin.get("did-webvh")


def fetch_server_config(ctx: Context) -> dict[str, Any]:
    r = ctx.session.get(
        f"{ctx.base_url}/tenant/server/status/config",
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def build_witness_invitation(server_url: str, witness_did: str) -> str:
    """Match Tenant UI: fetch OOB invitation, base64 JSON, didcomm://?oob=…"""
    key = witness_did.replace("did:key:", "", 1)
    if not key or "/" in key:
        raise ValueError(f"Unexpected witness DID format: {witness_did!r}")
    base = server_url.rstrip("/")
    url = f"{base}/api/invitations"
    r = requests.get(url, params={"_oobid": key}, timeout=60)
    r.raise_for_status()
    invitation = r.json()
    raw = json.dumps(invitation, separators=(",", ":")).encode("utf-8")
    b64 = base64.standard_b64encode(raw).decode("ascii")
    return f"didcomm://?oob={b64}"


def phase_smoke(ctx: Context) -> bool:
    LOG.info("Phase smoke: GET /status/live")
    r = ctx.session.get(f"{ctx.base_url}/status/live", timeout=30)
    if r.status_code != 200:
        LOG.error("status/live -> %s %s", r.status_code, r.text[:500])
        return False
    LOG.info("status/live OK")

    if _auth_headers():
        LOG.info("Phase smoke: GET /tenant/server/status/config (authenticated)")
        try:
            data = fetch_server_config(ctx)
            LOG.info(
                "server config keys: %s",
                list(data.keys())[:12],
            )
        except requests.HTTPError as e:
            LOG.error("server config failed: %s", e)
            return False
    else:
        LOG.info("Skipping authenticated smoke (no tenant token / API key)")
    return True


def phase_webvh_plugin(ctx: Context) -> bool:
    _require_tenant_auth()
    LOG.info("Phase webvh-plugin: read plugin_config.webvh / did-webvh")
    try:
        data = fetch_server_config(ctx)
    except requests.HTTPError as e:
        LOG.error("GET server config failed: %s", e)
        return False

    entry = _get_plugin_webvh(data)
    if not entry:
        LOG.error("No webvh or did-webvh entry in plugin_config")
        return False
    if not entry.get("server_url"):
        LOG.error("plugin_config webvh missing server_url")
        return False

    ctx.plugin_webvh = entry
    ctx.webvh_server_url = os.environ.get("WEBVH_SERVER_URL") or entry.get(
        "server_url"
    )
    witnesses = entry.get("witnesses")
    if isinstance(witnesses, list) and witnesses:
        ctx.webvh_witnesses = [str(w) for w in witnesses]
    elif entry.get("witness_id"):
        ctx.webvh_witnesses = [str(entry["witness_id"])]
    LOG.info(
        "WebVH defaults: server_url=%s witnesses=%s",
        ctx.webvh_server_url,
        ctx.webvh_witnesses,
    )
    return True


def phase_webvh_configure(ctx: Context) -> bool:
    _require_tenant_auth()
    mode = (os.environ.get("WEBVH_CONFIGURE_MODE") or "invitation").strip().lower()

    if not ctx.plugin_webvh:
        if not phase_webvh_plugin(ctx):
            return False

    preset = os.environ.get("WEBVH_WITNESS_INVITATION")
    if preset:
        payload: dict[str, Any] = {"witness_invitation": preset.strip()}
        LOG.info("POST /did/webvh/configuration (WEBVH_WITNESS_INVITATION)")
    elif mode in ("invitation", "auto"):
        try:
            inv = build_witness_invitation(
                str(ctx.webvh_server_url),
                ctx.webvh_witnesses[0] if ctx.webvh_witnesses else "",
            )
        except Exception as e:
            if mode == "auto":
                LOG.warning("Invitation fetch failed (%s); trying simple payload", e)
                inv = None
            else:
                LOG.error("Invitation fetch failed: %s", e)
                return False
        if inv:
            payload = {"witness_invitation": inv}
            LOG.info("POST /did/webvh/configuration (fetched witness invitation)")
        else:
            payload = {
                "server_url": ctx.webvh_server_url,
                "witness": True,
                "witnesses": ctx.webvh_witnesses,
            }
            LOG.info("POST /did/webvh/configuration (simple fallback)")
    else:
        payload = {
            "server_url": ctx.webvh_server_url,
            "witness": True,
            "witnesses": ctx.webvh_witnesses,
        }
        LOG.info("POST /did/webvh/configuration (simple)")

    if (
        "witness_invitation" not in payload
        and not ctx.webvh_witnesses
    ):
        LOG.error("No witnesses available for simple WebVH configuration")
        return False

    r = ctx.session.post(
        f"{ctx.base_url}/did/webvh/configuration",
        json=payload,
        timeout=120,
    )
    if r.status_code not in (200, 201):
        LOG.error("configure -> %s %s", r.status_code, r.text[:800])
        return False
    LOG.info("WebVH tenant configuration stored (%s)", r.status_code)
    return True


def phase_webvh_create(ctx: Context) -> bool:
    _require_tenant_auth()
    if not ctx.webvh_server_url and not phase_webvh_plugin(ctx):
        return False
    server_url = os.environ.get("WEBVH_SERVER_URL") or ctx.webvh_server_url
    alias = os.environ.get("WEBVH_DID_ALIAS") or f"webvh-e2e-{uuid.uuid4().hex[:8]}"
    namespace = (os.environ.get("WEBVH_NAMESPACE") or "default").strip()

    options: dict[str, Any] = {
        "identifier": alias,
        "namespace": namespace,
        "server_url": server_url,
    }
    if ctx.use_witness and ctx.webvh_witnesses:
        options["witnesses"] = ctx.webvh_witnesses
        options["witness"] = {"threshold": 1}

    body = {"options": options}
    LOG.info(
        "POST /did/webvh/create alias=%r namespace=%r witness=%s",
        alias,
        namespace,
        ctx.use_witness,
    )
    r = ctx.session.post(
        f"{ctx.base_url}/did/webvh/create",
        json=body,
        timeout=120,
    )
    if r.status_code not in (200, 201):
        LOG.error("create -> %s %s", r.status_code, r.text[:800])
        return False
    try:
        data = r.json()
    except json.JSONDecodeError:
        data = {}
    did = data.get("did") or (data.get("did_document") or {}).get("id")
    LOG.info("Create accepted; did=%s (may be pending until witness attests)", did)
    return True


def phase_issue_webvh(_ctx: Context) -> bool:
    LOG.warning("Phase issue-webvh not implemented yet (DITP#136)")
    return True


def phase_issue_indy(_ctx: Context) -> bool:
    LOG.warning("Phase issue-indy not implemented yet (DITP#136)")
    return True


def phase_verify(_ctx: Context) -> bool:
    LOG.warning("Phase verify not implemented yet (DITP#136)")
    return True


PHASES: dict[str, Any] = {
    "smoke": phase_smoke,
    "webvh-plugin": phase_webvh_plugin,
    "webvh-configure": phase_webvh_configure,
    "webvh-create": phase_webvh_create,
    "issue-webvh": phase_issue_webvh,
    "issue-indy": phase_issue_indy,
    "verify": phase_verify,
}

ALL_DEFAULT = (
    "smoke",
    "webvh-plugin",
    "webvh-configure",
    "webvh-create",
)


def _load_local_env() -> None:
    """Load ``scripts/webvh-e2e/.env`` if present (does not override existing OS env)."""
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.is_file():
        load_dotenv(env_file, override=False)


def main() -> int:
    _load_local_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=list(PHASES.keys()) + ["all"],
        default="all",
        help="Phase to run (default: all)",
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
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    ctx = build_context()
    ctx.use_witness = bool(args.witness)
    to_run: tuple[str, ...]
    if args.phase == "all":
        to_run = ALL_DEFAULT
    else:
        to_run = (args.phase,)

    ok = True
    for name in to_run:
        fn = PHASES[name]
        LOG.info("=== %s ===", name)
        try:
            if not fn(ctx):
                ok = False
                break
        except RuntimeError as e:
            LOG.error("%s", e)
            ok = False
            break
        except requests.RequestException as e:
            LOG.error("HTTP error in %s: %s", name, e)
            ok = False
            break

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
