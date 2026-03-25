"""Harness context: tenant base URL, issuer/holder sessions, flow state."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import requests

from traction_client import TractionClient

DEFAULT_BASE = "http://localhost:8032"


def normalize_base(url: str) -> str:
    return url.rstrip("/")


def env_flag(name: str) -> bool:
    v = (os.environ.get(name) or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def issuer_tenant_token() -> str:
    tok = (os.environ.get("TRACTION_ISSUER_TENANT_TOKEN") or "").strip()
    if not tok:
        raise RuntimeError("Issuer tenant token required: set TRACTION_ISSUER_TENANT_TOKEN.")
    return tok


def holder_tenant_token() -> str:
    tok = (os.environ.get("TRACTION_HOLDER_TENANT_TOKEN") or "").strip()
    if not tok:
        raise RuntimeError(
            "Holder tenant token required for this phase: set TRACTION_HOLDER_TENANT_TOKEN."
        )
    return tok


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {issuer_tenant_token()}"}


def get_plugin_webvh(config_json: dict[str, Any]) -> dict[str, Any] | None:
    cfg = (config_json or {}).get("config") or {}
    plugin = cfg.get("plugin_config") or {}
    return plugin.get("webvh") or plugin.get("did-webvh")


@dataclass
class Context:
    base_url: str
    session: requests.Session
    webvh_server_url: str | None = None
    webvh_witnesses: list[str] = field(default_factory=list)
    plugin_webvh: dict[str, Any] | None = None
    webvh_issuer_did: str | None = None
    anoncreds_schema_id: str | None = None
    anoncreds_cred_def_id: str | None = None
    anoncreds_rev_reg_def_id: str | None = None
    anoncreds_rev_reg_id: str | None = None
    use_witness: bool = False
    holder_session: requests.Session | None = None
    oob_issuer_connection_id: str | None = None
    oob_holder_connection_id: str | None = None
    issuer_cred_ex_id: str | None = None
    holder_cred_ex_id: str | None = None
    issuer_pres_ex_id: str | None = None
    holder_pres_ex_id: str | None = None

    def issuer_client(self) -> TractionClient:
        return TractionClient(self.base_url, self.session)

    def holder_client(self) -> TractionClient:
        if self.holder_session is None:
            raise RuntimeError("Holder session not attached.")
        return TractionClient(self.base_url, self.holder_session)


def build_context() -> Context:
    issuer_tenant_token()
    base = normalize_base(os.environ.get("TRACTION_TENANT_PROXY_BASE", DEFAULT_BASE).strip())
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **auth_headers(),
        }
    )
    return Context(base_url=base, session=session)
