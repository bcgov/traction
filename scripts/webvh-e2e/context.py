"""Harness context: tenant base URL and issuer/holder tenant sessions."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import requests

from traction_client import TractionClient

DEFAULT_BASE = "https://traction-sandbox-tenant-proxy.apps.silver.devops.gov.bc.ca"


def normalize_base(url: str) -> str:
    return url.rstrip("/")


def issuer_tenant_token() -> str:
    token = os.environ.get("TRACTION_ISSUER_TENANT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Issuer tenant token required: set TRACTION_ISSUER_TENANT_TOKEN.")
    return token


def holder_tenant_token() -> str:
    token = os.environ.get("TRACTION_HOLDER_TENANT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Holder tenant token required for this phase: set TRACTION_HOLDER_TENANT_TOKEN."
        )
    return token


def _session_headers(bearer_token: str) -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}",
    }


def get_plugin_webvh(config_json: dict[str, Any]) -> dict[str, Any] | None:
    """``plugin_config.webvh`` or ``plugin_config.did-webvh`` from tenant server config."""
    config_section = (config_json or {}).get("config") or {}
    plugin_config = config_section.get("plugin_config") or {}
    return plugin_config.get("webvh") or plugin_config.get("did-webvh")


@dataclass
class Context:
    base_url: str
    issuer_session: requests.Session
    holder_session: requests.Session
    plugin_webvh: dict[str, Any] | None = None
    webvh_server_url: str | None = None
    webvh_witnesses: list[str] = field(default_factory=list)
    use_witness: bool = False
    webvh_last_created_did: str | None = None
    webvh_last_create_namespace: str | None = None
    webvh_last_create_alias: str | None = None
    webvh_last_create_server_url: str | None = None
    # AnonCreds governance (WebVH issuer DID)
    webvh_schema_id: str | None = None
    webvh_cred_def_id: str | None = None
    # DIDComm (issuer ↔ holder; IDs differ per tenant)
    issuer_connection_id: str | None = None
    holder_connection_id: str | None = None
    # Issue-credential-2.0 (issuer role record after offer / issue)
    issuer_cred_ex_id: str | None = None

    def issuer_client(self) -> TractionClient:
        return TractionClient(self.base_url, self.issuer_session)

    def holder_client(self) -> TractionClient:
        return TractionClient(self.base_url, self.holder_session)


def build_context() -> Context:
    issuer_token = issuer_tenant_token()
    holder_token = holder_tenant_token()
    base = normalize_base(os.environ.get("TRACTION_TENANT_PROXY_BASE", DEFAULT_BASE).strip())

    issuer_session = requests.Session()
    issuer_session.headers.update(_session_headers(issuer_token))

    holder_session = requests.Session()
    holder_session.headers.update(_session_headers(holder_token))

    return Context(base_url=base, issuer_session=issuer_session, holder_session=holder_session)
