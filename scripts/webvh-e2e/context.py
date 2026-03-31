"""Harness context: tenant base URL and issuer/holder tenant sessions."""

from __future__ import annotations

import os
from dataclasses import dataclass

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


@dataclass
class Context:
    base_url: str
    issuer_session: requests.Session
    holder_session: requests.Session

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
