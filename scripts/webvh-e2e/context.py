"""Harness context: tenant base URL and authenticated issuer session."""

from __future__ import annotations

import os
from dataclasses import dataclass

import requests

from traction_client import TractionClient

DEFAULT_BASE = "http://localhost:8032"


def normalize_base(url: str) -> str:
    return url.rstrip("/")


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


@dataclass
class Context:
    base_url: str
    session: requests.Session

    def issuer_client(self) -> TractionClient:
        return TractionClient(self.base_url, self.session)


def build_context() -> Context:
    issuer_token = issuer_tenant_token()
    holder_tenant_token()
    base = normalize_base(os.environ.get("TRACTION_TENANT_PROXY_BASE", DEFAULT_BASE).strip())
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {issuer_token}",
    }
    session.headers.update(headers)
    return Context(base_url=base, session=session)
