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
        encoded_wallet_name = quote(wallet_name, safe="")
        return self._session.post(
            f"{self._base}/anoncreds/wallet/upgrade",
            params={"wallet_name": encoded_wallet_name},
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

    def post_wallet_did_public(self, did: str, *, timeout: float = 60) -> requests.Response:
        """POST /wallet/did/public?did=… (set tenant public DID, e.g. did:webvh:…)."""
        encoded_did = quote(did, safe="")
        return self._session.post(
            f"{self._base}/wallet/did/public?did={encoded_did}",
            json={},
            timeout=timeout,
        )

    def get_connections(self, *, params: dict[str, Any] | None = None, timeout: float = 60) -> requests.Response:
        """GET /connections"""
        return self._session.get(f"{self._base}/connections", params=params or {}, timeout=timeout)

    def get_connection(self, connection_id: str, *, timeout: float = 60) -> requests.Response:
        """GET /connections/{connection_id}"""
        return self._session.get(
            f"{self._base}/connections/{connection_id}",
            timeout=timeout,
        )

    def post_out_of_band_create_invitation(
        self,
        body: dict[str, Any],
        *,
        multi_use: bool = False,
        timeout: float = 120,
    ) -> requests.Response:
        """POST /out-of-band/create-invitation"""
        return self._session.post(
            f"{self._base}/out-of-band/create-invitation",
            params={"multi_use": "true" if multi_use else "false"},
            json=body,
            timeout=timeout,
        )

    def post_out_of_band_receive_invitation(
        self,
        invitation: dict[str, Any],
        *,
        alias: str,
        auto_accept: bool = True,
        timeout: float = 120,
    ) -> requests.Response:
        """POST /out-of-band/receive-invitation (body is the invitation message)."""
        return self._session.post(
            f"{self._base}/out-of-band/receive-invitation",
            params={"alias": alias, "auto_accept": "true" if auto_accept else "false"},
            json=invitation,
            timeout=timeout,
        )

    def post_anoncreds_schema(self, body: dict[str, Any], *, timeout: float = 120) -> requests.Response:
        """POST /anoncreds/schema"""
        return self._session.post(f"{self._base}/anoncreds/schema", json=body, timeout=timeout)

    def get_anoncreds_schemas(self, *, params: dict[str, Any] | None = None, timeout: float = 60) -> requests.Response:
        """GET /anoncreds/schemas"""
        return self._session.get(f"{self._base}/anoncreds/schemas", params=params or {}, timeout=timeout)

    def get_anoncreds_schema(self, schema_id: str, *, timeout: float = 60) -> requests.Response:
        """GET /anoncreds/schema/{schema_id}"""
        encoded = quote(schema_id, safe="")
        return self._session.get(f"{self._base}/anoncreds/schema/{encoded}", timeout=timeout)

    def post_anoncreds_credential_definition(
        self, body: dict[str, Any], *, timeout: float = 120
    ) -> requests.Response:
        """POST /anoncreds/credential-definition"""
        return self._session.post(
            f"{self._base}/anoncreds/credential-definition",
            json=body,
            timeout=timeout,
        )

    def get_anoncreds_credential_definitions(
        self, *, params: dict[str, Any] | None = None, timeout: float = 60
    ) -> requests.Response:
        """GET /anoncreds/credential-definitions"""
        return self._session.get(
            f"{self._base}/anoncreds/credential-definitions",
            params=params or {},
            timeout=timeout,
        )

    def post_issue_credential_v2_send_offer(
        self, body: dict[str, Any], *, timeout: float = 120
    ) -> requests.Response:
        """POST /issue-credential-2.0/send-offer"""
        return self._session.post(
            f"{self._base}/issue-credential-2.0/send-offer",
            json=body,
            timeout=timeout,
        )

    def get_issue_credential_v2_records(
        self, *, params: dict[str, Any] | None = None, timeout: float = 60
    ) -> requests.Response:
        """GET /issue-credential-2.0/records"""
        return self._session.get(
            f"{self._base}/issue-credential-2.0/records",
            params=params or {},
            timeout=timeout,
        )

    def post_issue_credential_v2_send_request(
        self, cred_ex_id: str, *, timeout: float = 120
    ) -> requests.Response:
        """POST /issue-credential-2.0/records/{cred_ex_id}/send-request"""
        return self._session.post(
            f"{self._base}/issue-credential-2.0/records/{cred_ex_id}/send-request",
            json={},
            timeout=timeout,
        )

    def get_issue_credential_v2_record(self, cred_ex_id: str, *, timeout: float = 60) -> requests.Response:
        """GET /issue-credential-2.0/records/{cred_ex_id}"""
        return self._session.get(
            f"{self._base}/issue-credential-2.0/records/{cred_ex_id}",
            timeout=timeout,
        )

    def post_present_proof_v2_send_request(
        self, body: dict[str, Any], *, timeout: float = 120
    ) -> requests.Response:
        """POST /present-proof-2.0/send-request"""
        return self._session.post(
            f"{self._base}/present-proof-2.0/send-request",
            json=body,
            timeout=timeout,
        )

    def get_present_proof_v2_records(
        self, *, params: dict[str, Any] | None = None, timeout: float = 60
    ) -> requests.Response:
        """GET /present-proof-2.0/records"""
        return self._session.get(
            f"{self._base}/present-proof-2.0/records",
            params=params or {},
            timeout=timeout,
        )

    def get_present_proof_v2_record(self, pres_ex_id: str, *, timeout: float = 60) -> requests.Response:
        """GET /present-proof-2.0/records/{pres_ex_id}"""
        return self._session.get(
            f"{self._base}/present-proof-2.0/records/{pres_ex_id}",
            timeout=timeout,
        )

    def post_present_proof_v2_send_presentation(
        self,
        pres_ex_id: str,
        body: dict[str, Any] | None = None,
        *,
        timeout: float = 120,
    ) -> requests.Response:
        """POST /present-proof-2.0/records/{pres_ex_id}/send-presentation"""
        return self._session.post(
            f"{self._base}/present-proof-2.0/records/{pres_ex_id}/send-presentation",
            json=body if body is not None else {},
            timeout=timeout,
        )

    def post_anoncreds_revocation_revoke(
        self, body: dict[str, Any], *, timeout: float = 120
    ) -> requests.Response:
        """POST /anoncreds/revocation/revoke"""
        return self._session.post(
            f"{self._base}/anoncreds/revocation/revoke",
            json=body,
            timeout=timeout,
        )
