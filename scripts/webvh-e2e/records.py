"""ACA-Py v2 credential / presentation record parsing; list helpers using ``TractionClient``."""

from __future__ import annotations

import json
import os
import time
from typing import Any

from harness_log import LOG
from traction_client import TractionClient


def connections_results(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        return [x for x in data["results"] if isinstance(x, dict)]
    return []


def inner_cred_ex_record(payload: dict[str, Any]) -> dict[str, Any] | None:
    inner = payload.get("cred_ex_record")
    if isinstance(inner, dict):
        return inner
    if payload.get("cred_ex_id") is not None:
        return payload
    return None


def v20_cred_ex_list_results(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        return [x for x in data["results"] if isinstance(x, dict)]
    return []


def norm_cred_ex_state(state: Any) -> str:
    s = str(state or "").strip().lower().replace("_", "-")
    return s


def list_v20_cred_ex_records(c: TractionClient, *, role: str) -> list[dict[str, Any]]:
    r = c.get_issue_credential_v20_records({"role": role})
    if not r.ok:
        LOG.debug("GET /issue-credential-2.0/records role=%s HTTP %s", role, r.status_code)
        return []
    try:
        data = r.json()
    except json.JSONDecodeError:
        return []
    out: list[dict[str, Any]] = []
    for row in v20_cred_ex_list_results(data):
        inner = inner_cred_ex_record(row)
        if inner:
            out.append(inner)
    return out


def holder_cred_ex_inner_records(c: TractionClient) -> list[dict[str, Any]]:
    by_cex: dict[str, dict[str, Any]] = {}
    for use_role_query in (True, False):
        params: dict[str, str] = {"role": "holder"} if use_role_query else {}
        r = c.get_issue_credential_v20_records(params)
        if not r.ok:
            LOG.debug(
                "GET /issue-credential-2.0/records params=%r HTTP %s",
                params,
                r.status_code,
            )
            continue
        try:
            data = r.json()
        except json.JSONDecodeError:
            continue
        for row in v20_cred_ex_list_results(data):
            inner = inner_cred_ex_record(row)
            if not inner:
                continue
            role_f = str(inner.get("role") or "").strip().lower()
            if use_role_query:
                if role_f and role_f != "holder":
                    continue
            elif role_f != "holder":
                continue
            cxid = inner.get("cred_ex_id")
            if isinstance(cxid, str) and cxid:
                by_cex[cxid] = inner
    return list(by_cex.values())


def get_v20_cred_ex_inner(c: TractionClient, cred_ex_id: str) -> dict[str, Any] | None:
    r = c.get_issue_credential_v20_record(cred_ex_id)
    if not r.ok:
        return None
    try:
        data = r.json()
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return inner_cred_ex_record(data)


def issuer_thread_id_after_offer(c: TractionClient, issuer_cred_ex_id: str) -> str | None:
    deadline = time.time() + 15.0
    while time.time() < deadline:
        rec = get_v20_cred_ex_inner(c, issuer_cred_ex_id)
        if rec:
            tid = rec.get("thread_id")
            if isinstance(tid, str) and tid.strip():
                return tid.strip()
        time.sleep(0.3)
    return None


def cred_ex_id_from_send_offer_item(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None
    inner = inner_cred_ex_record(item) or item
    cid = inner.get("cred_ex_id")
    return str(cid) if cid else None


def inner_pres_ex_record(payload: dict[str, Any]) -> dict[str, Any] | None:
    inner = payload.get("pres_ex_record")
    if isinstance(inner, dict):
        return inner
    if payload.get("pres_ex_id") is not None:
        return payload
    return None


def v20_pres_ex_list_results(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        return [x for x in data["results"] if isinstance(x, dict)]
    return []


def get_v20_pres_ex_inner(c: TractionClient, pres_ex_id: str) -> dict[str, Any] | None:
    r = c.get_present_proof_v20_record(pres_ex_id)
    if not r.ok:
        return None
    try:
        data = r.json()
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return inner_pres_ex_record(data)


def pres_ex_id_from_send_request_item(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None
    inner = inner_pres_ex_record(item) or item
    pid = inner.get("pres_ex_id")
    return str(pid) if pid else None


def issuer_pres_thread_after_send(c: TractionClient, pres_ex_id: str) -> str | None:
    deadline = time.time() + 15.0
    while time.time() < deadline:
        rec = get_v20_pres_ex_inner(c, pres_ex_id)
        if rec:
            tid = rec.get("thread_id")
            if isinstance(tid, str) and tid.strip():
                return tid.strip()
        time.sleep(0.3)
    return None


def holder_prover_pres_ex_inner_records(c: TractionClient) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for use_role_query in (True, False):
        params: dict[str, str] = {"role": "prover"} if use_role_query else {}
        r = c.get_present_proof_v20_records(params)
        if not r.ok:
            LOG.debug(
                "GET /present-proof-2.0/records params=%r HTTP %s",
                params,
                r.status_code,
            )
            continue
        try:
            data = r.json()
        except json.JSONDecodeError:
            continue
        for row in v20_pres_ex_list_results(data):
            inner = inner_pres_ex_record(row)
            if not inner and isinstance(row.get("pres_ex_id"), str):
                inner = row
            if not inner:
                continue
            role_f = str(inner.get("role") or "").strip().lower()
            if use_role_query:
                if role_f and role_f != "prover":
                    continue
            elif role_f != "prover":
                continue
            pxid = inner.get("pres_ex_id")
            if isinstance(pxid, str) and pxid:
                by_id[pxid] = inner
    return list(by_id.values())


def holder_wallet_cred_referent_for_cred_def(c: TractionClient, cred_def_id: str) -> str | None:
    r = c.get_wallet_credentials()
    if not r.ok:
        LOG.debug("GET /credentials HTTP %s", r.status_code)
        return None
    try:
        data = r.json()
    except json.JSONDecodeError:
        return None
    rows = data.get("results") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        ci = row.get("cred_info")
        if isinstance(ci, dict):
            if str(ci.get("cred_def_id") or "") == cred_def_id:
                ref = ci.get("referent")
                if isinstance(ref, str) and ref:
                    return ref
        if str(row.get("cred_def_id") or "") == cred_def_id:
            ref = row.get("referent")
            if isinstance(ref, str) and ref:
                return ref
    return None


def presentation_record_verified(rec: dict[str, Any]) -> bool:
    v = rec.get("verified")
    if isinstance(v, bool) and v:
        return True
    if isinstance(v, str) and v.strip().lower() in ("true", "1", "yes"):
        return True
    return False


def issuer_cred_rev_ids_from_cred_ex(
    c: TractionClient,
    cred_ex_id: str,
    *,
    poll_s: float,
    timeout_s: float,
) -> tuple[str | None, str | None]:
    """Poll ``GET /anoncreds/revocation/credential-record`` until ``rev_reg_id`` / ``cred_rev_id`` exist."""
    deadline = time.time() + max(5.0, timeout_s)
    while time.time() < deadline:
        r = c.get_anoncreds_revocation_credential_record(cred_ex_id=cred_ex_id)
        if r.ok:
            try:
                data = r.json()
            except json.JSONDecodeError:
                pass
            else:
                result = data.get("result") if isinstance(data, dict) else None
                if isinstance(result, dict):
                    rr = result.get("rev_reg_id")
                    cr = result.get("cred_rev_id")
                    if isinstance(rr, str) and rr.strip():
                        cr_s = str(cr).strip() if cr is not None else ""
                        if cr_s:
                            return rr.strip(), cr_s
        time.sleep(max(0.25, poll_s))
    return None, None


def connection_active_state(state: str | None) -> bool:
    return (state or "").strip().lower() == "active"


def connection_dict(c: TractionClient, conn_id: str) -> dict[str, Any] | None:
    r = c.get_connection(conn_id)
    if not r.ok:
        return None
    try:
        body = r.json()
    except json.JSONDecodeError:
        return None
    return body if isinstance(body, dict) else None


def find_active_connection_id_by_alias(c: TractionClient, alias: str) -> str | None:
    r = c.get_connections()
    if not r.ok:
        return None
    try:
        data = r.json()
    except json.JSONDecodeError:
        return None
    for row in connections_results(data):
        if row.get("alias") == alias and connection_active_state(row.get("state")):
            cid = row.get("connection_id")
            return str(cid) if cid else None
    return None


def wait_connection_active(
    c: TractionClient,
    connection_id: str,
    *,
    party: str,
) -> bool:
    try:
        poll_s = max(0.25, float((os.environ.get("WEBVH_CONNECT_POLL_SEC") or "1").strip()))
    except ValueError:
        poll_s = 1.0
    try:
        timeout_s = max(10.0, float((os.environ.get("WEBVH_CONNECT_TIMEOUT_SEC") or "120").strip()))
    except ValueError:
        timeout_s = 120.0
    deadline = time.time() + timeout_s
    last_state: str | None = None
    while time.time() < deadline:
        rec = connection_dict(c, connection_id)
        if rec:
            last_state = rec.get("state")
            if isinstance(last_state, str) and connection_active_state(last_state):
                return True
        time.sleep(poll_s)
    LOG.error(
        "[%s] connection %s not active after %ss (last state=%r)",
        party,
        connection_id,
        int(timeout_s),
        last_state,
    )
    return False
