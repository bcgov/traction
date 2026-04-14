"""
HTTP client for the Traction tenant proxy (ACA-Py admin–style routes).

Most ``get_*`` / ``post_*`` wrappers are registered from tables in ``_install_generated_routes``;
non-uniform calls (path templates, extra query params, redacted logs) stay as explicit methods.

Request bodies and query params log at **DEBUG**; each ``POST``/``PUT`` emits one **INFO** line
(``POST /path`` / ``PUT /path``) so default runs stay readable (see ``helpers.LOG`` convention).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import quote

import requests

from helpers import LOG, format_json_for_log, sanitized_webvh_config_for_log


def _enc(segment: str) -> str:
    return quote(segment, safe="")


def _issue_cred_ex_path(cred_ex_id: str) -> str:
    return f"/issue-credential-2.0/records/{_enc(cred_ex_id)}"


def _pres_ex_path(pres_ex_id: str) -> str:
    return f"/present-proof-2.0/records/{_enc(pres_ex_id)}"


class TractionClient:
    """Bearer-authenticated tenant proxy client (issuer or holder session)."""

    def __init__(self, base_url: str, session: requests.Session) -> None:
        self._base = base_url.rstrip("/")
        self._session = session

    def _url(self, path: str) -> str:
        return f"{self._base}{path}" if path.startswith("/") else f"{self._base}/{path}"

    def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: float = 60,
    ) -> requests.Response:
        return self._session.get(self._url(path), params=params or {}, timeout=timeout)

    def _put(
        self,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        timeout: float = 60,
    ) -> requests.Response:
        body = json_body if json_body is not None else {}
        LOG.info("PUT %s", path)
        if body:
            LOG.debug("PUT %s request body:\n%s", path, format_json_for_log(body))
        return self._session.put(self._url(path), json=body, timeout=timeout)

    def _post_json(
        self,
        path: str,
        *,
        json_body: Any | None = None,
        params: dict[str, Any] | None = None,
        timeout: float = 60,
        log_body: Any | None = None,
    ) -> requests.Response:
        if json_body is None:
            json_body = {}
        shown = log_body if log_body is not None else json_body
        LOG.info("POST %s", path)
        if params:
            LOG.debug("POST %s query params:\n%s", path, format_json_for_log(params))
        LOG.debug("POST %s request body:\n%s", path, format_json_for_log(shown))
        return self._session.post(
            self._url(path),
            json=json_body,
            params=params or {},
            timeout=timeout,
        )

    # --- routes that do not fit the tables below ---

    def get_connection(self, connection_id: str, *, timeout: float = 60) -> requests.Response:
        return self._get(f"/connections/{connection_id}", timeout=timeout)

    def get_ledger_did_verkey(self, did: str, *, timeout: float = 60) -> requests.Response:
        return self._get(f"/ledger/did-verkey?did={_enc(did)}", timeout=timeout)

    def put_tenant_config_set_ledger_id(self, ledger_id: str, *, timeout: float = 60) -> requests.Response:
        return self._put(
            "/tenant/config/set-ledger-id",
            json_body={"ledger_id": ledger_id},
            timeout=timeout,
        )

    def post_did_webvh_configuration(self, body: dict[str, Any], *, timeout: float = 120) -> requests.Response:
        path = "/did/webvh/configuration"
        for_log = sanitized_webvh_config_for_log(body) if isinstance(body, dict) else body
        return self._post_json(path, json_body=body, log_body=for_log, timeout=timeout)

    def post_wallet_did_create(
        self, body: dict[str, Any] | None = None, *, timeout: float = 120
    ) -> requests.Response:
        return self._post_json(
            "/wallet/did/create",
            json_body=body if body is not None else {},
            timeout=timeout,
        )

    def post_wallet_did_public(self, did: str, *, timeout: float = 60) -> requests.Response:
        return self._post_json(f"/wallet/did/public?did={_enc(did)}", json_body={}, timeout=timeout)

    def post_anoncreds_wallet_upgrade(self, wallet_name: str, *, timeout: float = 120) -> requests.Response:
        return self._post_json(
            "/anoncreds/wallet/upgrade",
            json_body={},
            params={"wallet_name": _enc(wallet_name)},
            timeout=timeout,
        )

    def put_ledger_set_write_ledger(self, ledger_id: str, *, timeout: float = 60) -> requests.Response:
        return self._put(f"/ledger/{_enc(ledger_id)}/set-write-ledger", json_body={}, timeout=timeout)

    def post_ledger_register_nym(
        self, *, did: str, verkey: str, alias: str, timeout: float = 120
    ) -> requests.Response:
        return self._post_json(
            "/ledger/register-nym",
            json_body={},
            params={"did": did, "verkey": verkey, "alias": alias},
            timeout=timeout,
        )

    def post_out_of_band_create_invitation(
        self, body: dict[str, Any], *, multi_use: bool = False, timeout: float = 120
    ) -> requests.Response:
        return self._post_json(
            "/out-of-band/create-invitation",
            json_body=body,
            params={"multi_use": "true" if multi_use else "false"},
            timeout=timeout,
        )

    def post_out_of_band_receive_invitation(
        self, invitation: dict[str, Any], *, alias: str, timeout: float = 120
    ) -> requests.Response:
        return self._post_json(
            "/out-of-band/receive-invitation",
            json_body=invitation,
            params={"alias": alias, "auto_accept": "true"},
            timeout=timeout,
        )

    def post_issue_credential_v2_send_request(
        self, cred_ex_id: str, *, timeout: float = 120
    ) -> requests.Response:
        return self._post_json(
            f"{_issue_cred_ex_path(cred_ex_id)}/send-request",
            json_body={},
            timeout=timeout,
        )

    def post_issue_credential_v2_issue(
        self,
        cred_ex_id: str,
        *,
        body: dict[str, Any] | None = None,
        timeout: float = 120,
    ) -> requests.Response:
        return self._post_json(
            f"{_issue_cred_ex_path(cred_ex_id)}/issue",
            json_body=body if body is not None else {},
            timeout=timeout,
        )

    def get_present_proof_v2_credentials(
        self,
        pres_ex_id: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: float = 60,
    ) -> requests.Response:
        return self._get(f"{_pres_ex_path(pres_ex_id)}/credentials", params=params, timeout=timeout)

    def post_present_proof_v2_send_presentation(
        self,
        pres_ex_id: str,
        body: dict[str, Any] | None = None,
        *,
        timeout: float = 120,
    ) -> requests.Response:
        return self._post_json(
            f"{_pres_ex_path(pres_ex_id)}/send-presentation",
            json_body=body,
            timeout=timeout,
        )


def _make_get(path: str, default_timeout: float) -> Callable[..., Any]:
    def GET(self: TractionClient, *, timeout: float = default_timeout) -> requests.Response:
        return self._get(path, timeout=timeout)

    return GET


def _make_get_params(path: str, default_timeout: float = 60) -> Callable[..., Any]:
    def GET(
        self: TractionClient,
        *,
        params: dict[str, Any] | None = None,
        timeout: float = default_timeout,
    ) -> requests.Response:
        return self._get(path, params=params, timeout=timeout)

    return GET


def _make_get_seg(prefix: str, suffix: str = "", default_timeout: float = 60) -> Callable[..., Any]:
    def GET(self: TractionClient, segment: str, *, timeout: float = default_timeout) -> requests.Response:
        return self._get(f"{prefix}{_enc(segment)}{suffix}", timeout=timeout)

    return GET


def _make_get_path(path_fn: Callable[[str], str], default_timeout: float = 60) -> Callable[..., Any]:
    def GET(self: TractionClient, record_id: str, *, timeout: float = default_timeout) -> requests.Response:
        return self._get(path_fn(record_id), timeout=timeout)

    return GET


def _make_post_body(path: str, default_timeout: float) -> Callable[..., Any]:
    def POST(self: TractionClient, body: dict[str, Any], *, timeout: float = default_timeout) -> requests.Response:
        return self._post_json(path, json_body=body, timeout=timeout)

    return POST


def _make_post_empty(path: str, default_timeout: float) -> Callable[..., Any]:
    def POST(self: TractionClient, *, timeout: float = default_timeout) -> requests.Response:
        return self._post_json(path, json_body={}, timeout=timeout)

    return POST


def _attach_route(cls: type[TractionClient], name: str, fn: Callable[..., Any]) -> None:
    fn.__name__ = name
    fn.__qualname__ = f"{cls.__name__}.{name}"
    setattr(cls, name, fn)


def _install_generated_routes() -> None:
    simple_gets: list[tuple[str, Callable[..., Any]]] = [
        ("get_status_live", _make_get("/status/live", 30)),
        *[
            (n, _make_get(p, 60))
            for n, p in (
                ("get_tenant_wallet", "/tenant/wallet"),
                ("get_settings", "/settings"),
                ("get_tenant_server_status_config", "/tenant/server/status/config"),
                ("get_tenant_self", "/tenant"),
                ("get_tenant_endorser_info", "/tenant/endorser-info"),
                ("get_tenant_endorser_connection", "/tenant/endorser-connection"),
                ("get_did_webvh_configuration", "/did/webvh/configuration"),
                ("get_wallet_did_public", "/wallet/did/public"),
                ("get_ledger_write_ledger", "/ledger/get-write-ledger"),
            )
        ],
    ]
    for name, m in simple_gets:
        _attach_route(TractionClient, name, m)

    for name, path in (
        ("get_connections", "/connections"),
        ("get_anoncreds_schemas", "/anoncreds/schemas"),
        ("get_anoncreds_credential_definitions", "/anoncreds/credential-definitions"),
        ("get_issue_credential_v2_records", "/issue-credential-2.0/records"),
        ("get_present_proof_v2_records", "/present-proof-2.0/records"),
        ("get_wallet_dids", "/wallet/did"),
    ):
        _attach_route(TractionClient, name, _make_get_params(path))

    for name, prefix, suffix in (
        ("get_out_of_band_record", "/out-of-band/records/", ""),
        ("get_anoncreds_schema", "/anoncreds/schema/", ""),
        ("get_anoncreds_revocation_active_registry", "/anoncreds/revocation/active-registry/", ""),
        ("get_transaction", "/transactions/", ""),
        (
            "get_anoncreds_revocation_registry_issued_indy_recs",
            "/anoncreds/revocation/registry/",
            "/issued/indy_recs",
        ),
    ):
        _attach_route(TractionClient, name, _make_get_seg(prefix, suffix))

    for name, fn in (
        ("get_issue_credential_v2_record", _issue_cred_ex_path),
        ("get_present_proof_v2_record", _pres_ex_path),
    ):
        _attach_route(TractionClient, name, _make_get_path(fn))

    for name, path, dt in (
        ("post_anoncreds_schema", "/anoncreds/schema", 120),
        ("post_anoncreds_credential_definition", "/anoncreds/credential-definition", 120),
        ("post_issue_credential_v2_send_offer", "/issue-credential-2.0/send-offer", 120),
        ("post_present_proof_v2_send_request", "/present-proof-2.0/send-request", 120),
        ("post_did_webvh_create", "/did/webvh/create", 180),
        ("post_anoncreds_revocation_revoke", "/anoncreds/revocation/revoke", 120),
    ):
        _attach_route(TractionClient, name, _make_post_body(path, dt))

    _attach_route(TractionClient, "post_tenant_endorser_connection", _make_post_empty("/tenant/endorser-connection", 120))


_install_generated_routes()
