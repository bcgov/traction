"""Indy ledger setup: BCovrin test endorser connection and public DID (issuer tenant)."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from context import Context
from constants import (
    E2E_INDY_CONNECTION_POLL_SEC,
    E2E_INDY_CONNECTION_TIMEOUT_SEC,
    E2E_INDY_TXN_POLL_SEC,
    E2E_INDY_TXN_TIMEOUT_SEC,
)
from helpers import LOG, http_json_dict, log_http_failed, poll_until

if TYPE_CHECKING:
    from traction_client import TractionClient


def _endorser_connection_poll_once(issuer: "TractionClient", connection_id: str) -> bool | None:
    """One GET /connections/{id} poll: active → True, abandoned/deleted → False, else keep waiting."""
    poll_response = issuer.get_connection(connection_id)
    if not poll_response.ok:
        return None
    poll_payload = http_json_dict(poll_response) or {}
    poll_state = (poll_payload.get("state") or "").lower()
    if poll_state == "active":
        return True
    if poll_state in ("abandoned", "deleted"):
        LOG.error("Endorser connection entered failure state: %s", poll_state)
        return False
    LOG.info(
        "Waiting for endorser connection (connection_id=%s state=%s)",
        connection_id,
        poll_state or "?",
    )
    return None


def _endorser_verify_active_connection_row(
    issuer: "TractionClient",
    context: Context,
    connection_id: str,
) -> tuple[bool, str | None]:
    """
    Confirm ``GET /connections/{id}`` when the endorser summary already reported ``active``.

    Returns ``(True, None)`` if the row is active (context updated). Otherwise ``(False, fold)``
    where ``fold`` is a terminal connection state to merge into the summary ``state``, or ``None``.
    """
    verify_connection_response = issuer.get_connection(connection_id)
    if not verify_connection_response.ok:
        LOG.warning(
            "GET /tenant/endorser-connection reported active but GET /connections/%s HTTP %s; waiting",
            connection_id,
            verify_connection_response.status_code,
        )
        return False, None
    verify_connection_payload = http_json_dict(verify_connection_response) or {}
    verify_connection_state = (verify_connection_payload.get("state") or "").lower()
    if verify_connection_state == "active":
        LOG.info(
            "Endorser connection active (connection_id=%s); verified GET /connections, skipping POST",
            connection_id,
        )
        context.indy_endorser_connection_id = connection_id
        return True, None
    if verify_connection_state in ("abandoned", "deleted"):
        return False, verify_connection_state
    LOG.info(
        "GET /tenant/endorser-connection reported active but GET /connections/%s state=%s; waiting",
        connection_id,
        verify_connection_state or "?",
    )
    return False, None


def _parse_public_did_from_get_public_payload(body: dict[str, Any]) -> str | None:
    """Parse ``GET /wallet/did/public`` JSON — ACA-Py / proxies use ``result.did``, ``result`` string, or top-level ``did``."""
    result = body.get("result")
    if isinstance(result, dict) and result.get("did"):
        return str(result["did"]).strip()
    if isinstance(result, str) and result.strip():
        return result.strip()
    if body.get("did"):
        return str(body["did"]).strip()
    return None


def _parse_public_did_from_wallet_did_list(body: dict[str, Any]) -> str | None:
    """Pick a public Indy DID from ``GET /wallet/did`` results (fallback)."""
    rows = body.get("results")
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        posture = (row.get("posture") or "").lower()
        method = (row.get("method") or "").lower()
        if posture == "public" and method in ("", "sov", "indy"):
            did = row.get("did")
            if did:
                return str(did).strip()
    return None


def _issuer_existing_public_did_short(issuer: "TractionClient") -> str | None:
    """
    Return existing public DID if already assigned (idempotent re-runs).

    Tries ``GET /wallet/did/public``, then ``GET /wallet/did`` for a public posture row.
    """
    pub = issuer.get_wallet_did_public()
    if pub.ok:
        parsed = _parse_public_did_from_get_public_payload(http_json_dict(pub) or {})
        if parsed:
            return parsed
    listed = issuer.get_wallet_dids()
    if listed.ok:
        return _parse_public_did_from_wallet_did_list(http_json_dict(listed) or {})
    return None


def phase_indy_set_write_ledger(context: Context) -> bool:
    """
    Issuer: PUT /ledger/{ledger_id}/set-write-ledger for the Indy write ledger (default bcovrin-test).

    Uses ``context.indy_write_ledger_id`` (from ``E2E_INDY_WRITE_LEDGER_ID`` or default in constants).
    """
    ledger_id = (context.indy_write_ledger_id or "").strip()
    if not ledger_id:
        LOG.error("Missing indy_write_ledger_id; set E2E_INDY_WRITE_LEDGER_ID or Context default")
        return False

    issuer = context.issuer_client()
    set_ledger_response = issuer.put_ledger_set_write_ledger(ledger_id)
    if not set_ledger_response.ok:
        log_http_failed(
            f"PUT /ledger/{ledger_id}/set-write-ledger failed", set_ledger_response, max_body=800
        )
        return False
    set_ledger_body = http_json_dict(set_ledger_response) or {}
    write_ledger = set_ledger_body.get("write_ledger") or ledger_id
    LOG.info("Write ledger set to %s", write_ledger)
    return True


def phase_indy_connect_endorser(context: Context) -> bool:
    """
    Issuer: GET /tenant/endorser-info, then connect to configured Indy endorser.

    Reuses an existing connection from GET /tenant/endorser-connection when present.
    Treats the connection as ready only when GET /connections/{id} reports ``active`` (even if
    the endorser summary already says ``active``). Otherwise POST /tenant/endorser-connection and
    polls GET /connections/{id} until ``active``.
    """
    issuer = context.issuer_client()

    info_resp = issuer.get_tenant_endorser_info()
    if not info_resp.ok:
        log_http_failed("GET /tenant/endorser-info failed", info_resp, max_body=800)
        return False
    info = http_json_dict(info_resp) or {}
    endorser_did = info.get("endorser_did")
    endorser_name = info.get("endorser_name")
    LOG.info("Configured endorser: name=%s did=%s", endorser_name, endorser_did)

    existing = issuer.get_tenant_endorser_connection()
    connection_id: str | None = None
    if not existing.ok and existing.status_code != 404:
        log_http_failed(
            "GET /tenant/endorser-connection failed", existing, max_body=800
        )
        return False

    if existing.ok:
        endorser_summary = http_json_dict(existing) or {}
        state = (endorser_summary.get("state") or "").lower()
        connection_id = endorser_summary.get("connection_id")
        if connection_id:
            connection_id = str(connection_id)
            if state == "active":
                verified, fold_state = _endorser_verify_active_connection_row(
                    issuer, context, connection_id
                )
                if verified:
                    return True
                if fold_state:
                    state = fold_state
        if state in ("abandoned", "deleted"):
            LOG.warning(
                "Existing endorser connection %s is %s; creating a new connection",
                connection_id or "(no id)",
                state,
            )
        elif connection_id:
            LOG.info(
                "Endorser connection exists (connection_id=%s state=%s); waiting for active (no duplicate POST)",
                connection_id,
                state or "?",
            )

            existing_connection_poll_result = poll_until(
                lambda: _endorser_connection_poll_once(issuer, connection_id),
                timeout_sec=E2E_INDY_CONNECTION_TIMEOUT_SEC,
                interval_sec=E2E_INDY_CONNECTION_POLL_SEC,
                description="existing endorser connection active",
            )
            if existing_connection_poll_result is True:
                context.indy_endorser_connection_id = connection_id
                LOG.info("Endorser connection active (connection_id=%s)", connection_id)
                return True
            return False
        else:
            LOG.info(
                "GET /tenant/endorser-connection has no connection_id (state=%s); POST to create one",
                state or "?",
            )

    if not existing.ok:
        LOG.info("No existing endorser connection (HTTP %s); POST to create one", existing.status_code)

    post = issuer.post_tenant_endorser_connection()
    if not post.ok:
        log_http_failed(
            "POST /tenant/endorser-connection failed", post, max_body=1200
        )
        return False
    create_endorser_payload = http_json_dict(post) or {}
    connection_id = create_endorser_payload.get("connection_id")
    if not connection_id:
        LOG.error("POST /tenant/endorser-connection response missing connection_id")
        return False
    connection_id = str(connection_id)
    LOG.info(
        "Endorser connection created connection_id=%s state=%s",
        connection_id,
        create_endorser_payload.get("state"),
    )

    endorser_connection_poll_result = poll_until(
        lambda: _endorser_connection_poll_once(issuer, connection_id),
        timeout_sec=E2E_INDY_CONNECTION_TIMEOUT_SEC,
        interval_sec=E2E_INDY_CONNECTION_POLL_SEC,
        description="endorser connection active",
    )
    if endorser_connection_poll_result is not True:
        return False

    context.indy_endorser_connection_id = connection_id
    LOG.info("Endorser connection active (connection_id=%s)", connection_id)
    return True


def _register_nym_alias(context: Context) -> str:
    env_alias = os.environ.get("E2E_INDY_REGISTER_NYM_ALIAS", "").strip()
    if env_alias:
        return env_alias
    issuer = context.issuer_client()
    tenant_self_response = issuer.get_tenant_self()
    if tenant_self_response.ok:
        body = http_json_dict(tenant_self_response) or {}
        name = body.get("tenant_name") or body.get("wallet_id")
        if name:
            return str(name)
    return "webvh-e2e-indy"


def phase_indy_register_public_did(context: Context) -> bool:
    """
    Issuer: create an Indy DID, POST /ledger/register-nym (endorsed), wait for transaction,
    verify on ledger, POST /wallet/did/public, PUT /tenant/config/set-ledger-id.

    Skips registration if GET /wallet/did/public already returns a DID (idempotent for re-runs).
    """
    ledger_id = (context.indy_write_ledger_id or "").strip()
    if not ledger_id:
        LOG.error("Missing indy_write_ledger_id")
        return False

    issuer = context.issuer_client()

    existing_did = _issuer_existing_public_did_short(issuer)
    if existing_did:
        LOG.info("Wallet already has public DID %s; skipping register-nym flow", existing_did)
        context.indy_public_did = existing_did
        return True

    create = issuer.post_wallet_did_create(
        {"method": "sov", "options": {"key_type": "ed25519"}},
    )
    if not create.ok:
        log_http_failed("POST /wallet/did/create failed", create, max_body=1200)
        return False
    create_did_payload = http_json_dict(create) or {}
    did_create_result = (
        create_did_payload.get("result")
        if isinstance(create_did_payload.get("result"), dict)
        else create_did_payload
    )
    if not isinstance(did_create_result, dict):
        LOG.error("Unexpected /wallet/did/create response shape")
        return False
    wallet_did = did_create_result.get("did")
    issuer_verkey = did_create_result.get("verkey")
    if not wallet_did or not issuer_verkey:
        LOG.error("create DID response missing did or verkey")
        return False
    wallet_did, issuer_verkey = str(wallet_did), str(issuer_verkey)
    LOG.info("Created wallet DID %s (registering on ledger %s)", wallet_did, ledger_id)

    alias = _register_nym_alias(context)
    reg = issuer.post_ledger_register_nym(did=wallet_did, verkey=issuer_verkey, alias=alias)
    if not reg.ok:
        log_http_failed("POST /ledger/register-nym failed", reg, max_body=1200)
        return False
    reg_body = http_json_dict(reg) or {}
    txn = reg_body.get("txn") if isinstance(reg_body.get("txn"), dict) else {}
    txn_id = txn.get("transaction_id") if isinstance(txn, dict) else None
    if not txn_id:
        LOG.error("register-nym response missing txn.transaction_id")
        return False
    txn_id = str(txn_id)
    LOG.info("Register-nym transaction_id=%s; waiting for endorsement", txn_id)

    def txn_acked() -> bool | None:
        transaction_response = issuer.get_transaction(txn_id)
        if not transaction_response.ok:
            return None
        transaction_record = http_json_dict(transaction_response) or {}
        transaction_state = (transaction_record.get("state") or "").lower()
        if transaction_state == "transaction_acked":
            return True
        if transaction_state in (
            "transaction_cancelled",
            "transaction_rejected",
            "transaction_abandoned",
        ):
            LOG.error("Transaction %s failed state=%s", txn_id, transaction_state)
            return False
        LOG.info(
            "Waiting for transaction (transaction_id=%s state=%s)",
            txn_id,
            transaction_state or "?",
        )
        return None

    transaction_poll_result = poll_until(
        txn_acked,
        timeout_sec=E2E_INDY_TXN_TIMEOUT_SEC,
        interval_sec=E2E_INDY_TXN_POLL_SEC,
        description="register-nym transaction endorsed",
    )
    if transaction_poll_result is not True:
        return False

    ledger_verkey_response = issuer.get_ledger_did_verkey(wallet_did)
    if not ledger_verkey_response.ok:
        log_http_failed(
            "GET /ledger/did-verkey failed", ledger_verkey_response, max_body=800
        )
        return False
    ledger_verkey_body = http_json_dict(ledger_verkey_response) or {}
    if not ledger_verkey_body.get("verkey"):
        LOG.error("DID %s not found on ledger after endorsement", wallet_did)
        return False
    posted_ledger = ledger_verkey_body.get("ledger_id")
    if posted_ledger and str(posted_ledger) != ledger_id:
        LOG.warning(
            "DID posted on ledger_id=%s (expected %s); continuing",
            posted_ledger,
            ledger_id,
        )

    pub_post = issuer.post_wallet_did_public(wallet_did)
    if not pub_post.ok:
        log_http_failed("POST /wallet/did/public failed", pub_post, max_body=800)
        return False

    cfg = issuer.put_tenant_config_set_ledger_id(ledger_id)
    if not cfg.ok:
        LOG.warning(
            "PUT /tenant/config/set-ledger-id failed (HTTP %s); public DID may still be set",
            cfg.status_code,
        )

    context.indy_public_did = wallet_did
    LOG.info("Indy public DID registered: %s (ledger=%s)", wallet_did, ledger_id)
    return True
