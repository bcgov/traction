"""DIDComm connection phases (holder ↔ issuer over DIDComm)."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from context import Context
from e2e_constants import (
    E2E_CONNECTION_POLL_SEC,
    E2E_CONNECTION_TIMEOUT_SEC,
    E2E_HOLDER_CONNECTION_ALIAS,
)
from helpers import poll_until

LOG = logging.getLogger("webvh-e2e")

_CONNECTION_ALIAS_ISSUER = "webvh-e2e-issuer"


def _connection_ids_from_list_payload(payload: dict[str, Any]) -> set[str]:
    results = payload.get("results") or []
    return {str(r.get("connection_id")) for r in results if r.get("connection_id")}


def _issuer_connection_ids_snapshot(issuer: Any) -> set[str] | None:
    """Return connection IDs before OOB; ``None`` if GET /connections failed."""
    issuer_conns = issuer.get_connections()
    if not issuer_conns.ok:
        LOG.error("Issuer GET /connections failed: %s", issuer_conns.status_code)
        return None
    try:
        return _connection_ids_from_list_payload(issuer_conns.json())
    except json.JSONDecodeError:
        return set()


def _oob_invitation_for_didexchange(issuer: Any, webvh_did: str) -> dict[str, Any] | None:
    """POST OOB create-invitation; return embedded ``invitation`` dict or ``None``."""
    oob_body = {
        "accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"],
        "alias": _CONNECTION_ALIAS_ISSUER,
        "handshake_protocols": ["https://didcomm.org/didexchange/1.1"],
        "my_label": "WebVH E2E Issuer",
        "protocol_version": "1.1",
        "use_did": webvh_did,
        "use_public_did": False,
    }
    create_oob = issuer.post_out_of_band_create_invitation(oob_body, multi_use=False)
    if not create_oob.ok:
        LOG.error(
            "POST /out-of-band/create-invitation failed (HTTP %s)",
            create_oob.status_code,
        )
        LOG.debug(
            "OOB create error body:\n%s",
            (create_oob.text or "")[:4000],
        )
        return None
    try:
        oob_data = create_oob.json()
    except json.JSONDecodeError:
        LOG.error("OOB create returned non-JSON")
        return None

    invitation = oob_data.get("invitation")
    if not isinstance(invitation, dict):
        LOG.error("OOB create response missing invitation object")
        LOG.debug("OOB create body:\n%s", json.dumps(oob_data, indent=2, default=str))
        return None
    return invitation


def _holder_receive_oob_and_connection_id(
    holder: Any, invitation: dict[str, Any], holder_alias: str
) -> str | None:
    """POST receive-invitation; return holder ``connection_id`` or ``None``."""
    recv = holder.post_out_of_band_receive_invitation(
        invitation,
        alias=holder_alias,
        auto_accept=True,
    )
    if not recv.ok:
        LOG.error(
            "Holder POST /out-of-band/receive-invitation failed (HTTP %s)",
            recv.status_code,
        )
        LOG.debug(
            "receive-invitation error body:\n%s",
            (recv.text or "")[:4000],
        )
        return None
    try:
        oob_recv = recv.json()
    except json.JSONDecodeError:
        LOG.error("Holder receive-invitation returned non-JSON")
        return None

    holder_conn = oob_recv.get("connection_id")
    if not holder_conn:
        LOG.error("Holder OOB response missing connection_id")
        LOG.debug("receive-invitation body:\n%s", json.dumps(oob_recv, indent=2, default=str))
        return None
    return str(holder_conn)


def _poll_issuer_new_active_connection(
    issuer: Any,
    issuer_conns_before: set[str],
    *,
    poll_sec: float,
    timeout_sec: float,
) -> str | None:
    """Poll until issuer has a new connection in ``active`` state."""

    def issuer_connection_ready() -> str | None:
        response = issuer.get_connections()
        if not response.ok:
            return None
        try:
            payload = response.json()
        except json.JSONDecodeError:
            return None
        for row in payload.get("results") or []:
            cid = row.get("connection_id")
            if not cid or str(cid) in issuer_conns_before:
                continue
            state = (row.get("state") or "").lower()
            if state == "active":
                return str(cid)
        return None

    return poll_until(
        issuer_connection_ready,
        timeout_sec=timeout_sec,
        interval_sec=poll_sec,
        description="issuer active DIDExchange connection",
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
        check = holder.get_connection(holder_connection_id)
        if check.ok:
            try:
                row = check.json()
            except json.JSONDecodeError:
                row = {}
            st = (row.get("state") or "").lower()
            if st == "active":
                return
        time.sleep(poll_sec)
    LOG.warning(
        "Holder connection %s not active before timeout; continuing anyway",
        holder_connection_id,
    )


def phase_oob_didexchange_webvh_didcomm(ctx: Context) -> bool:
    """
    Issuer (WebVH DID) ↔ holder via OOB + DID Exchange 1.1.

    Uses ``use_did`` on the invitation (no ``POST /wallet/did/public`` / Indy public DID).

    Steps: snapshot issuer connections → OOB create → holder receive → poll issuer new active
    connection → optionally wait for holder active.
    """
    webvh_did = ctx.webvh_last_created_did
    if not webvh_did:
        LOG.error("No did:webvh on context; run webvh-create first")
        return False

    issuer = ctx.issuer_client()
    holder = ctx.holder_client()

    issuer_conns_before = _issuer_connection_ids_snapshot(issuer)
    if issuer_conns_before is None:
        return False

    invitation = _oob_invitation_for_didexchange(issuer, webvh_did)
    if not invitation:
        return False

    holder_cid = _holder_receive_oob_and_connection_id(
        holder, invitation, E2E_HOLDER_CONNECTION_ALIAS
    )
    if not holder_cid:
        return False
    ctx.holder_connection_id = holder_cid
    LOG.info("Holder connection_id=%s", ctx.holder_connection_id)

    issuer_cid = _poll_issuer_new_active_connection(
        issuer,
        issuer_conns_before,
        poll_sec=E2E_CONNECTION_POLL_SEC,
        timeout_sec=E2E_CONNECTION_TIMEOUT_SEC,
    )
    if not issuer_cid:
        return False
    ctx.issuer_connection_id = issuer_cid
    LOG.info("Issuer connection_id=%s", ctx.issuer_connection_id)

    _wait_holder_connection_active(
        holder,
        ctx.holder_connection_id,
        poll_sec=E2E_CONNECTION_POLL_SEC,
        timeout_sec=E2E_CONNECTION_TIMEOUT_SEC,
    )
    return True
