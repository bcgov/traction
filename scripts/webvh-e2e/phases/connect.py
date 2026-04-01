"""DIDComm connection phases (holder ↔ issuer over DIDComm)."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from context import Context
from polling import poll_until

LOG = logging.getLogger("webvh-e2e")

_CONNECTION_ALIAS_ISSUER = "webvh-e2e-issuer"
_CONNECTION_ALIAS_HOLDER = "webvh-e2e-holder"


def _connection_ids_before(client_response_json: dict[str, Any]) -> set[str]:
    results = client_response_json.get("results") or []
    return {str(r.get("connection_id")) for r in results if r.get("connection_id")}


def phase_oob_didexchange_webvh_didcomm(ctx: Context) -> bool:
    """
    Establish DIDComm between issuer (public ``did:webvh`` + service from create) and holder via OOB.

    1. Issuer: POST /wallet/did/public with the WebVH DID.
    2. Issuer: POST /out-of-band/create-invitation with ``use_public_did: true`` and DID Exchange 1.1.
    3. Holder: POST /out-of-band/receive-invitation with the invitation (``auto_accept``).
    4. Resolve issuer-side ``connection_id`` by polling GET /connections until a new active connection appears.
    """
    webvh_did = ctx.webvh_last_created_did
    if not webvh_did:
        LOG.error("No did:webvh on context; run webvh-create first")
        return False

    issuer = ctx.issuer_client()
    holder = ctx.holder_client()

    pub_response = issuer.post_wallet_did_public(webvh_did)
    if not pub_response.ok:
        LOG.error(
            "POST /wallet/did/public failed: %s %s",
            pub_response.status_code,
            (pub_response.text or "")[:600],
        )
        return False
    LOG.info("Set issuer public DID to %s", webvh_did)

    issuer_conns = issuer.get_connections()
    if not issuer_conns.ok:
        LOG.error("Issuer GET /connections failed: %s", issuer_conns.status_code)
        return False
    try:
        issuer_conns_before = _connection_ids_before(issuer_conns.json())
    except json.JSONDecodeError:
        issuer_conns_before = set()

    oob_body = {
        "accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"],
        "alias": _CONNECTION_ALIAS_ISSUER,
        "handshake_protocols": ["https://didcomm.org/didexchange/1.1"],
        "my_label": "WebVH E2E Issuer",
        "protocol_version": "1.1",
        "use_public_did": True,
    }
    create_oob = issuer.post_out_of_band_create_invitation(oob_body, multi_use=False)
    if not create_oob.ok:
        LOG.error(
            "POST /out-of-band/create-invitation failed: %s %s",
            create_oob.status_code,
            (create_oob.text or "")[:800],
        )
        return False
    try:
        oob_data = create_oob.json()
    except json.JSONDecodeError:
        LOG.error("OOB create returned non-JSON")
        return False

    invitation = oob_data.get("invitation")
    if not isinstance(invitation, dict):
        LOG.error("OOB create response missing invitation: %s", oob_data)
        return False

    holder_alias = (
        os.environ.get("WEBVH_E2E_HOLDER_CONNECTION_ALIAS") or _CONNECTION_ALIAS_HOLDER
    ).strip()

    recv = holder.post_out_of_band_receive_invitation(
        invitation,
        alias=holder_alias,
        auto_accept=True,
    )
    if not recv.ok:
        LOG.error(
            "Holder POST /out-of-band/receive-invitation failed: %s %s",
            recv.status_code,
            (recv.text or "")[:800],
        )
        return False
    try:
        oob_recv = recv.json()
    except json.JSONDecodeError:
        LOG.error("Holder receive-invitation returned non-JSON")
        return False

    holder_conn = oob_recv.get("connection_id")
    if not holder_conn:
        LOG.error("Holder OOB response missing connection_id: %s", oob_recv)
        return False
    ctx.holder_connection_id = str(holder_conn)
    LOG.info("Holder connection_id=%s", ctx.holder_connection_id)

    poll_sec = float(os.environ.get("WEBVH_E2E_CONNECTION_POLL_SEC", "2"))
    timeout_sec = float(os.environ.get("WEBVH_E2E_CONNECTION_TIMEOUT_SEC", "120"))

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

    issuer_cid = poll_until(
        issuer_connection_ready,
        timeout_sec=timeout_sec,
        interval_sec=poll_sec,
        description="issuer active DIDExchange connection",
    )
    if not issuer_cid:
        return False
    ctx.issuer_connection_id = issuer_cid
    LOG.info("Issuer connection_id=%s", ctx.issuer_connection_id)

    # Optional: wait until holder connection is active (helps later phases)
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        check = holder.get_connection(ctx.holder_connection_id)
        if check.ok:
            try:
                row = check.json()
            except json.JSONDecodeError:
                row = {}
            st = (row.get("state") or "").lower()
            if st == "active":
                break
        time.sleep(poll_sec)
    else:
        LOG.warning(
            "Holder connection %s not active before timeout; continuing anyway",
            ctx.holder_connection_id,
        )

    return True
