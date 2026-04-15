"""DIDComm connection phases (holder ↔ issuer over DIDComm)."""

from __future__ import annotations

import json
import time
from typing import Any

from context import Context
from constants import (
    E2E_CONNECTION_POLL_SEC,
    E2E_CONNECTION_TIMEOUT_SEC,
    E2E_HOLDER_CONNECTION_ALIAS,
    E2E_INDY_CONNECTION_POLL_SEC,
    E2E_INDY_CONNECTION_TIMEOUT_SEC,
    E2E_INDY_HOLDER_CONNECTION_ALIAS,
    E2E_INDY_ISSUER_OOB_ALIAS,
)
from helpers import LOG, format_json_for_log, log_http_failed, poll_until

_CONNECTION_ALIAS_ISSUER = "webvh-e2e-issuer"

# ACA-Py DID Exchange / connection records may report ``active`` or ``completed`` when ready.
_DIDEXCHANGE_READY_STATES = frozenset({"active", "completed"})


def _connection_ids_from_list_payload(payload: dict[str, Any]) -> set[str]:
    results = payload.get("results") or []
    return {
        str(connection_row.get("connection_id"))
        for connection_row in results
        if connection_row.get("connection_id")
    }


def _issuer_connection_ids_snapshot(issuer: Any) -> set[str] | None:
    """Return connection IDs before OOB; ``None`` if GET /connections failed."""
    issuer_conns = issuer.get_connections()
    if not issuer_conns.ok:
        log_http_failed("Issuer GET /connections failed", issuer_conns, max_body=800)
        return None
    try:
        return _connection_ids_from_list_payload(issuer_conns.json())
    except json.JSONDecodeError:
        return set()


def _oob_invitation_for_didexchange(
    issuer: Any,
    *,
    issuer_oob_alias: str,
    my_label: str,
    use_did: str | None = None,
    use_wallet_public_did: bool = False,
) -> tuple[dict[str, Any], str | None] | None:
    """
    POST OOB create-invitation; return ``(invitation, oob_id)`` or ``None``.

    **WebVH / arbitrary DID:** pass ``use_did`` (e.g. ``did:webvh:…``) and ``use_wallet_public_did=False``.

    **Indy ledger public DID:** set ``use_wallet_public_did=True`` and omit ``use_did`` (ACA-Py uses the
    wallet public DID; a short ``use_did`` produces invitations the holder rejects with **422**).
    """
    oob_body: dict[str, Any] = {
        "accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"],
        "alias": issuer_oob_alias,
        "handshake_protocols": ["https://didcomm.org/didexchange/1.1"],
        "my_label": my_label,
        "protocol_version": "1.1",
    }
    if use_wallet_public_did:
        oob_body["use_public_did"] = True
    else:
        if not use_did:
            LOG.error("OOB create-invitation requires use_did when not using wallet public DID")
            return None
        oob_body["use_did"] = use_did
        oob_body["use_public_did"] = False
    create_oob = issuer.post_out_of_band_create_invitation(oob_body, multi_use=False)
    if not create_oob.ok:
        log_http_failed("POST /out-of-band/create-invitation failed", create_oob)
        return None
    try:
        oob_data = create_oob.json()
    except json.JSONDecodeError:
        LOG.error("OOB create returned non-JSON")
        return None

    invitation = oob_data.get("invitation")
    if not isinstance(invitation, dict):
        LOG.error("OOB create response missing invitation object")
        LOG.debug("OOB create body:\n%s", format_json_for_log(oob_data))
        return None
    oob_id = oob_data.get("oob_id")
    if oob_id is not None:
        oob_id = str(oob_id)
    return invitation, oob_id


def _holder_receive_oob_and_connection_id(
    holder: Any, invitation: dict[str, Any], holder_alias: str
) -> str | None:
    """POST receive-invitation; return holder ``connection_id`` or ``None``."""
    receive_invitation_response = holder.post_out_of_band_receive_invitation(
        invitation,
        alias=holder_alias,
    )
    if not receive_invitation_response.ok:
        log_http_failed(
            "Holder POST /out-of-band/receive-invitation failed", receive_invitation_response
        )
        return None
    try:
        receive_invitation_payload = receive_invitation_response.json()
    except json.JSONDecodeError:
        LOG.error("Holder receive-invitation returned non-JSON")
        return None

    holder_connection_id = receive_invitation_payload.get("connection_id")
    if not holder_connection_id:
        LOG.error("Holder OOB response missing connection_id")
        LOG.debug("receive-invitation body:\n%s", format_json_for_log(receive_invitation_payload))
        return None
    return str(holder_connection_id)


def _issuer_connection_id_if_ready(issuer: Any, connection_id: str) -> str | None:
    """Return ``connection_id`` if GET /connections/{id} is ``active`` or ``completed``."""
    connection_response = issuer.get_connection(connection_id)
    if not connection_response.ok:
        return None
    try:
        connection_record = connection_response.json()
    except json.JSONDecodeError:
        return None
    connection_state = (connection_record.get("state") or "").lower()
    if connection_state in _DIDEXCHANGE_READY_STATES:
        return connection_id
    return None


def _poll_issuer_didexchange_connection(
    issuer: Any,
    issuer_conns_before: set[str],
    *,
    oob_id: str | None,
    invitation_msg_id: str | None,
    poll_sec: float,
    timeout_sec: float,
) -> str | None:
    """
    Resolve issuer-side connection after holder receive-invitation.

    Prefer, in order: OOB record ``connection_id``; list row matching ``invitation_msg_id``; any new
    connection id (not in the pre-OOB snapshot) in a ready state. Some deployments report **completed**
    instead of **active**; Indy public-DID OOB may also update an existing connection row (same id as
    before), so the snapshot-only heuristic is not enough.
    """

    def issuer_connection_ready() -> str | None:
        if oob_id:
            oob_record_response = issuer.get_out_of_band_record(oob_id)
            if oob_record_response.ok:
                try:
                    oob_record = oob_record_response.json()
                except json.JSONDecodeError:
                    oob_record = {}
                oob_connection_id = oob_record.get("connection_id")
                if oob_connection_id:
                    ready_id = _issuer_connection_id_if_ready(issuer, str(oob_connection_id))
                    if ready_id:
                        return ready_id

        list_response = issuer.get_connections()
        if not list_response.ok:
            return None
        try:
            list_payload = list_response.json()
        except json.JSONDecodeError:
            return None
        connection_results = list_payload.get("results") or []

        if invitation_msg_id:
            for connection_row in connection_results:
                if str(connection_row.get("invitation_msg_id") or "") != invitation_msg_id:
                    continue
                row_connection_id = connection_row.get("connection_id")
                if not row_connection_id:
                    continue
                row_state = (connection_row.get("state") or "").lower()
                if row_state in _DIDEXCHANGE_READY_STATES:
                    return str(row_connection_id)
                ready_id = _issuer_connection_id_if_ready(issuer, str(row_connection_id))
                if ready_id:
                    return ready_id

        for connection_row in connection_results:
            row_connection_id = connection_row.get("connection_id")
            if not row_connection_id or str(row_connection_id) in issuer_conns_before:
                continue
            row_state = (connection_row.get("state") or "").lower()
            if row_state in _DIDEXCHANGE_READY_STATES:
                return str(row_connection_id)
            ready_id = _issuer_connection_id_if_ready(issuer, str(row_connection_id))
            if ready_id:
                return ready_id

        return None

    return poll_until(
        issuer_connection_ready,
        timeout_sec=timeout_sec,
        interval_sec=poll_sec,
        description="issuer DIDExchange connection (active or completed)",
    )


def _wait_holder_connection_active(
    holder: Any,
    holder_connection_id: str,
    *,
    poll_sec: float,
    timeout_sec: float,
) -> None:
    """Best-effort wait for holder connection ``active``; warn on timeout."""
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        holder_connection_check = holder.get_connection(holder_connection_id)
        if holder_connection_check.ok:
            try:
                holder_connection_record = holder_connection_check.json()
            except json.JSONDecodeError:
                holder_connection_record = {}
            holder_state = (holder_connection_record.get("state") or "").lower()
            if holder_state in _DIDEXCHANGE_READY_STATES:
                return
        time.sleep(poll_sec)
    LOG.warning(
        "Holder connection %s not active before timeout; continuing anyway",
        holder_connection_id,
    )


def _oob_didexchange_with_issuer_did(
    context: Context,
    *,
    issuer_oob_alias: str,
    holder_alias: str,
    my_label: str,
    log_label: str,
    use_did: str | None = None,
    use_wallet_public_did: bool = False,
    poll_sec: float = E2E_CONNECTION_POLL_SEC,
    timeout_sec: float = E2E_CONNECTION_TIMEOUT_SEC,
) -> bool:
    """
    Issuer ↔ holder via OOB + DID Exchange 1.1.

    Either ``use_did`` (WebVH ``did:webvh:…``) or ``use_wallet_public_did`` (Indy public DID on ledger).

    Steps: snapshot issuer connections → OOB create → holder receive → poll issuer new active
    connection → optionally wait for holder active.
    """
    if not use_wallet_public_did:
        if not (use_did or "").strip():
            LOG.error("[%s] Missing use_did for OOB", log_label)
            return False
        use_did = use_did.strip()

    issuer = context.issuer_client()
    holder = context.holder_client()

    issuer_conns_before = _issuer_connection_ids_snapshot(issuer)
    if issuer_conns_before is None:
        return False

    oob_created = _oob_invitation_for_didexchange(
        issuer,
        issuer_oob_alias=issuer_oob_alias,
        my_label=my_label,
        use_did=use_did,
        use_wallet_public_did=use_wallet_public_did,
    )
    if not oob_created:
        return False
    invitation, oob_id = oob_created
    invitation_msg_id = invitation.get("@id")
    if invitation_msg_id is not None:
        invitation_msg_id = str(invitation_msg_id)

    resolved_holder_connection_id = _holder_receive_oob_and_connection_id(
        holder, invitation, holder_alias
    )
    if not resolved_holder_connection_id:
        return False
    context.holder_connection_id = resolved_holder_connection_id
    LOG.info("Holder connection_id=%s", context.holder_connection_id)

    resolved_issuer_connection_id = _poll_issuer_didexchange_connection(
        issuer,
        issuer_conns_before,
        oob_id=oob_id,
        invitation_msg_id=invitation_msg_id,
        poll_sec=poll_sec,
        timeout_sec=timeout_sec,
    )
    if not resolved_issuer_connection_id:
        return False
    context.issuer_connection_id = resolved_issuer_connection_id
    LOG.info("Issuer connection_id=%s", context.issuer_connection_id)

    _wait_holder_connection_active(
        holder,
        context.holder_connection_id,
        poll_sec=poll_sec,
        timeout_sec=timeout_sec,
    )
    LOG.info(
        "[%s] DIDComm ready (issuer_conn=%s holder_conn=%s)",
        log_label,
        resolved_issuer_connection_id,
        resolved_holder_connection_id,
    )
    return True


def phase_oob_didexchange_webvh_didcomm(context: Context) -> bool:
    """Issuer (``did:webvh``) ↔ holder; ``use_did`` = WebVH issuer DID."""
    webvh_did = context.webvh_last_created_did
    if not webvh_did:
        LOG.error("No did:webvh on context; run webvh-create first")
        return False
    return _oob_didexchange_with_issuer_did(
        context,
        issuer_oob_alias=_CONNECTION_ALIAS_ISSUER,
        holder_alias=E2E_HOLDER_CONNECTION_ALIAS,
        my_label="WebVH E2E Issuer",
        log_label="webvh",
        use_did=webvh_did,
        use_wallet_public_did=False,
    )


def phase_oob_didexchange_indy_didcomm(context: Context) -> bool:
    """
    Issuer (Indy public DID) ↔ holder.

    Uses ``use_public_did: true`` on create-invitation (wallet’s ledger public DID). Do not pass a short
    ``use_did`` — that yields invalid ``services`` and **422** on receive-invitation.
    """
    if not (context.indy_public_did or "").strip():
        LOG.error("No Indy public DID on context; run indy-register-public-did first")
        return False
    return _oob_didexchange_with_issuer_did(
        context,
        issuer_oob_alias=E2E_INDY_ISSUER_OOB_ALIAS,
        holder_alias=E2E_INDY_HOLDER_CONNECTION_ALIAS,
        my_label="Indy E2E Issuer",
        log_label="indy",
        use_did=None,
        use_wallet_public_did=True,
        poll_sec=E2E_INDY_CONNECTION_POLL_SEC,
        timeout_sec=E2E_INDY_CONNECTION_TIMEOUT_SEC,
    )
