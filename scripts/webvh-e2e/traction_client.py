"""
HTTP client for the Traction **tenant proxy** (ACA-Py admin–style routes).

Each public method maps to a single REST call so the API surface is easy to scan.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests


def encode_anoncreds_path_segment(value: str) -> str:
    """URL-encode a cred_def_id / schema id for path segments."""
    return quote(value, safe="")


class TractionClient:
    """Bearer-authenticated tenant proxy client (issuer or holder session)."""

    def __init__(self, base_url: str, session: requests.Session) -> None:
        self._base = base_url.rstrip("/")
        self._session = session

    @property
    def base_url(self) -> str:
        return self._base

    @property
    def session(self) -> requests.Session:
        return self._session

    # --- Health / config ---

    def get_status_live(self, *, timeout: float = 30) -> requests.Response:
        """GET /status/live"""
        return self._session.get(f"{self._base}/status/live", timeout=timeout)

    def get_tenant_server_status_config(self, *, timeout: float = 60) -> requests.Response:
        """GET /tenant/server/status/config"""
        return self._session.get(f"{self._base}/tenant/server/status/config", timeout=timeout)

    # --- Wallet / settings ---

    def get_settings(self, *, timeout: float = 60) -> requests.Response:
        """GET /settings"""
        return self._session.get(f"{self._base}/settings", timeout=timeout)

    def get_tenant_wallet(self, *, timeout: float = 60) -> requests.Response:
        """GET /tenant/wallet"""
        return self._session.get(f"{self._base}/tenant/wallet", timeout=timeout)

    def post_anoncreds_wallet_upgrade(self, wallet_name: str, *, timeout: float = 120) -> requests.Response:
        """POST /anoncreds/wallet/upgrade?wallet_name=…"""
        q = quote(wallet_name, safe="")
        return self._session.post(
            f"{self._base}/anoncreds/wallet/upgrade",
            params={"wallet_name": q},
            json={},
            timeout=timeout,
        )

    # --- Connections / OOB ---

    def get_connection(self, connection_id: str, *, timeout: float = 60) -> requests.Response:
        """GET /connections/{id}"""
        return self._session.get(f"{self._base}/connections/{connection_id}", timeout=timeout)

    def get_connections(self, *, timeout: float = 60) -> requests.Response:
        """GET /connections"""
        return self._session.get(f"{self._base}/connections", timeout=timeout)

    def post_out_of_band_create_invitation(
        self,
        body: dict[str, Any],
        *,
        multi_use: bool,
        timeout: float = 120,
    ) -> requests.Response:
        """POST /out-of-band/create-invitation"""
        return self._session.post(
            f"{self._base}/out-of-band/create-invitation",
            params={"multi_use": str(bool(multi_use)).lower()},
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
        """POST /out-of-band/receive-invitation"""
        return self._session.post(
            f"{self._base}/out-of-band/receive-invitation",
            params={"alias": alias, "auto_accept": "true" if auto_accept else "false"},
            json=invitation,
            timeout=timeout,
        )

    # --- WebVH ---

    def post_did_webvh_configuration(self, body: dict[str, Any], *, timeout: float = 120) -> requests.Response:
        """POST /did/webvh/configuration"""
        return self._session.post(f"{self._base}/did/webvh/configuration", json=body, timeout=timeout)

    def post_did_webvh_create(self, body: dict[str, Any], *, timeout: float = 120) -> requests.Response:
        """POST /did/webvh/create"""
        return self._session.post(f"{self._base}/did/webvh/create", json=body, timeout=timeout)

    # --- AnonCreds governance ---

    def post_anoncreds_schema(self, body: dict[str, Any], *, timeout: float = 120) -> requests.Response:
        """POST /anoncreds/schema"""
        return self._session.post(f"{self._base}/anoncreds/schema", json=body, timeout=timeout)

    def post_anoncreds_credential_definition(
        self, body: dict[str, Any], *, timeout: float = 120
    ) -> requests.Response:
        """POST /anoncreds/credential-definition"""
        return self._session.post(
            f"{self._base}/anoncreds/credential-definition",
            json=body,
            timeout=timeout,
        )

    def get_anoncreds_credential_definition(self, cred_def_id: str, *, timeout: float = 60) -> requests.Response:
        """GET /anoncreds/credential-definition/{cred_def_id}"""
        enc = encode_anoncreds_path_segment(cred_def_id)
        return self._session.get(f"{self._base}/anoncreds/credential-definition/{enc}", timeout=timeout)

    def get_anoncreds_revocation_active_registry(self, cred_def_id: str, *, timeout: float = 60) -> requests.Response:
        """GET /anoncreds/revocation/active-registry/{cred_def_id}"""
        enc = encode_anoncreds_path_segment(cred_def_id)
        return self._session.get(
            f"{self._base}/anoncreds/revocation/active-registry/{enc}",
            timeout=timeout,
        )

    def post_anoncreds_revocation_revoke(self, body: dict[str, Any], *, timeout: float = 120) -> requests.Response:
        """POST /anoncreds/revocation/revoke"""
        return self._session.post(
            f"{self._base}/anoncreds/revocation/revoke",
            json=body,
            timeout=timeout,
        )

    def get_anoncreds_revocation_credential_record(
        self,
        *,
        cred_ex_id: str | None = None,
        rev_reg_id: str | None = None,
        cred_rev_id: str | None = None,
        timeout: float = 60,
    ) -> requests.Response:
        """GET /anoncreds/revocation/credential-record"""
        params: dict[str, str] = {}
        if cred_ex_id:
            params["cred_ex_id"] = cred_ex_id
        if rev_reg_id:
            params["rev_reg_id"] = rev_reg_id
        if cred_rev_id is not None and str(cred_rev_id).strip() != "":
            params["cred_rev_id"] = str(cred_rev_id).strip()
        return self._session.get(
            f"{self._base}/anoncreds/revocation/credential-record",
            params=params,
            timeout=timeout,
        )

    # --- Issue credential 2.0 ---

    def get_issue_credential_v20_records(
        self, params: dict[str, str] | None = None, *, timeout: float = 60
    ) -> requests.Response:
        """GET /issue-credential-2.0/records"""
        return self._session.get(
            f"{self._base}/issue-credential-2.0/records",
            params=params or {},
            timeout=timeout,
        )

    def get_issue_credential_v20_record(self, cred_ex_id: str, *, timeout: float = 60) -> requests.Response:
        """GET /issue-credential-2.0/records/{cred_ex_id}"""
        return self._session.get(
            f"{self._base}/issue-credential-2.0/records/{cred_ex_id}",
            timeout=timeout,
        )

    def post_issue_credential_v20_send_offer(self, body: dict[str, Any], *, timeout: float = 120) -> requests.Response:
        """POST /issue-credential-2.0/send-offer"""
        return self._session.post(
            f"{self._base}/issue-credential-2.0/send-offer",
            json=body,
            timeout=timeout,
        )

    def post_issue_credential_v20_send_request(self, holder_cred_ex_id: str, *, timeout: float = 120) -> requests.Response:
        """POST /issue-credential-2.0/records/{id}/send-request"""
        return self._session.post(
            f"{self._base}/issue-credential-2.0/records/{holder_cred_ex_id}/send-request",
            json={},
            timeout=timeout,
        )

    # --- Wallet credentials (holder) ---

    def get_wallet_credentials(self, *, timeout: float = 60) -> requests.Response:
        """GET /credentials"""
        return self._session.get(f"{self._base}/credentials", timeout=timeout)

    # --- Present proof 2.0 ---

    def get_present_proof_v20_records(
        self, params: dict[str, str] | None = None, *, timeout: float = 60
    ) -> requests.Response:
        """GET /present-proof-2.0/records"""
        return self._session.get(
            f"{self._base}/present-proof-2.0/records",
            params=params or {},
            timeout=timeout,
        )

    def get_present_proof_v20_record(self, pres_ex_id: str, *, timeout: float = 60) -> requests.Response:
        """GET /present-proof-2.0/records/{pres_ex_id}"""
        return self._session.get(
            f"{self._base}/present-proof-2.0/records/{pres_ex_id}",
            timeout=timeout,
        )

    def post_present_proof_v20_send_request(self, body: dict[str, Any], *, timeout: float = 120) -> requests.Response:
        """POST /present-proof-2.0/send-request"""
        return self._session.post(
            f"{self._base}/present-proof-2.0/send-request",
            json=body,
            timeout=timeout,
        )

    def post_present_proof_v20_send_presentation(
        self, holder_pres_ex_id: str, body: dict[str, Any], *, timeout: float = 120
    ) -> requests.Response:
        """POST /present-proof-2.0/records/{id}/send-presentation"""
        return self._session.post(
            f"{self._base}/present-proof-2.0/records/{holder_pres_ex_id}/send-presentation",
            json=body,
            timeout=timeout,
        )

    def post_present_proof_v20_verify_presentation(
        self, issuer_pres_ex_id: str, *, json_body: dict[str, Any] | None = None, timeout: float = 120
    ) -> requests.Response:
        """POST /present-proof-2.0/records/{id}/verify-presentation"""
        return self._session.post(
            f"{self._base}/present-proof-2.0/records/{issuer_pres_ex_id}/verify-presentation",
            json=json_body if json_body is not None else {},
            timeout=timeout,
        )
