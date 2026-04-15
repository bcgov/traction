"""Harness context: tenant base URL and issuer/holder tenant sessions."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import requests

from constants import E2E_INDY_WRITE_LEDGER_ID
from traction_client import TractionClient

DEFAULT_BASE = "https://traction-sandbox-tenant-proxy.apps.silver.devops.gov.bc.ca"


def _env_token(env_var: str, *, missing_message: str) -> str:
    token = os.environ.get(env_var, "").strip()
    if not token:
        raise RuntimeError(missing_message)
    return token


def _json_session(bearer_token: str) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }
    )
    return session


def get_plugin_webvh(config_json: dict[str, Any]) -> dict[str, Any] | None:
    """``plugin_config.webvh`` or ``plugin_config.did-webvh`` from tenant server config."""
    plugin_config = ((config_json or {}).get("config") or {}).get("plugin_config") or {}
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
    # Indy (BCovrin test) — issuer endorser + public DID
    indy_write_ledger_id: str | None = None
    indy_endorser_connection_id: str | None = None
    indy_public_did: str | None = None
    indy_schema_id: str | None = None
    indy_cred_def_id: str | None = None

    def issuer_client(self) -> TractionClient:
        return TractionClient(self.base_url, self.issuer_session)

    def holder_client(self) -> TractionClient:
        return TractionClient(self.base_url, self.holder_session)


def build_context(*, use_witness: bool = False) -> Context:
    base = os.environ.get("TRACTION_TENANT_PROXY_BASE", DEFAULT_BASE).strip().rstrip("/")
    indy_ledger = os.environ.get("E2E_INDY_WRITE_LEDGER_ID", "").strip()
    return Context(
        base_url=base,
        issuer_session=_json_session(
            _env_token(
                "TRACTION_ISSUER_TENANT_TOKEN",
                missing_message="Issuer tenant token required: set TRACTION_ISSUER_TENANT_TOKEN.",
            )
        ),
        holder_session=_json_session(
            _env_token(
                "TRACTION_HOLDER_TENANT_TOKEN",
                missing_message="Holder tenant token required: set TRACTION_HOLDER_TENANT_TOKEN.",
            )
        ),
        use_witness=use_witness,
        indy_write_ledger_id=indy_ledger or E2E_INDY_WRITE_LEDGER_ID,
    )
