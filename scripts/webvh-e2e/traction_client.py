"""
HTTP client for the Traction tenant proxy (ACA-Py admin–style routes).

Add methods as phases need them; each public method should map to one REST call.
"""

from __future__ import annotations

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
