"""
HTTP client for the Traction tenant proxy (ACA-Py admin–style routes).

Add methods as phases need them; each public method should map to one REST call.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests


class TractionClient:
    """Bearer-authenticated tenant proxy client (issuer or holder session)."""

    def __init__(self, base_url: str, session: requests.Session) -> None:
        self._base = base_url.rstrip("/")
        self._session = session

    def get_status_live(self, *, timeout: float = 30) -> requests.Response:
        """GET /status/live"""
        return self._session.get(f"{self._base}/status/live", timeout=timeout)

    def get_tenant_wallet(self, *, timeout: float = 60) -> requests.Response:
        """GET /tenant/wallet"""
        return self._session.get(f"{self._base}/tenant/wallet", timeout=timeout)

    def get_settings(self, *, timeout: float = 60) -> requests.Response:
        """GET /settings"""
        return self._session.get(f"{self._base}/settings", timeout=timeout)

    def get_tenant_server_status_config(self, *, timeout: float = 60) -> requests.Response:
        """GET /tenant/server/status/config"""
        return self._session.get(f"{self._base}/tenant/server/status/config", timeout=timeout)

    def post_anoncreds_wallet_upgrade(self, wallet_name: str, *, timeout: float = 120) -> requests.Response:
        """POST /anoncreds/wallet/upgrade?wallet_name=…"""
        q = quote(wallet_name, safe="")
        return self._session.post(
            f"{self._base}/anoncreds/wallet/upgrade",
            params={"wallet_name": q},
            json={},
            timeout=timeout,
        )

    def get_did_webvh_configuration(self, *, timeout: float = 60) -> requests.Response:
        """GET /did/webvh/configuration (tenant-stored WebVH config)."""
        return self._session.get(f"{self._base}/did/webvh/configuration", timeout=timeout)

    def post_did_webvh_configuration(self, body: dict[str, Any], *, timeout: float = 120) -> requests.Response:
        """POST /did/webvh/configuration"""
        return self._session.post(f"{self._base}/did/webvh/configuration", json=body, timeout=timeout)

    def post_did_webvh_create(self, body: dict[str, Any], *, timeout: float = 180) -> requests.Response:
        """POST /did/webvh/create (body includes ``options`` for namespace, identifier, etc.)."""
        return self._session.post(f"{self._base}/did/webvh/create", json=body, timeout=timeout)
