"""Small helpers for WebVH harness (WebVH server calls, explorer URLs, polling)."""

from __future__ import annotations

import base64
import json
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar
from urllib.parse import quote, urlsplit

import requests

LOG = logging.getLogger(__name__)

T = TypeVar("T")


def v20_cred_ex_record_core(row: Any) -> dict[str, Any]:
    """
    ACA-Py often wraps the v2.0 credential exchange in ``cred_ex_record`` (``V20CredExRecordDetail``):
    applies to **list** ``GET /issue-credential-2.0/records`` and **single-record** GET by id.
    """
    if not isinstance(row, dict):
        return {}
    inner = row.get("cred_ex_record")
    if isinstance(inner, dict):
        return inner
    return row


def fetch_witness_invitation_json(server_url: str, witness_did_fragment: str) -> dict[str, Any]:
    """
    GET the OOB invitation JSON from the WebVH server (unauthenticated).

    ``witness_did_fragment`` is the key material after ``did:key:`` (used as ``_oobid``).
    """
    base = server_url.rstrip("/")
    url = f"{base}/api/invitations?_oobid={witness_did_fragment}"
    LOG.debug("Fetching witness invitation: %s", url)
    invitation_response = requests.get(url, timeout=30)
    invitation_response.raise_for_status()
    return invitation_response.json()


def witness_invitation_to_didcomm(invitation: dict[str, Any]) -> str:
    """Match Tenant UI: base64 JSON + ``didcomm://?oob=`` prefix."""
    invitation_json = json.dumps(invitation)
    base64_invitation = base64.b64encode(invitation_json.encode()).decode("ascii")
    return f"didcomm://?oob={base64_invitation}"


def build_witness_invitation_didcomm(server_url: str, witness_did_fragment: str) -> str:
    """Fetch invitation from WebVH server and encode for ``POST /did/webvh/configuration``."""
    invitation_payload = fetch_witness_invitation_json(server_url, witness_did_fragment)
    return witness_invitation_to_didcomm(invitation_payload)


def sanitized_webvh_config_for_log(cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Copy WebVH configuration JSON for logging only: shorten ``witness_invitation``;
    clear ``scids`` (SCID → DID can be sensitive / noisy in CI logs).
    """
    out: dict[str, Any] = dict(cfg)
    witness_invitation_value = out.get("witness_invitation")
    if isinstance(witness_invitation_value, str) and witness_invitation_value:
        out["witness_invitation"] = f"<set, {len(witness_invitation_value)} chars>"
    if "scids" in out:
        out["scids"] = {}
    return out


def _webvh_did_segments(did: str) -> tuple[str, str, str, str] | None:
    """``(scid, host, namespace, path_segment)`` for ``did:webvh:…`` or ``None``."""
    parts = did.split(":")
    if len(parts) >= 6 and parts[0] == "did" and parts[1] == "webvh":
        return parts[2], parts[3], parts[4], parts[5]
    return None


def webvh_scid_from_did(did: str) -> str | None:
    """SCID component of a ``did:webvh`` string."""
    segments = _webvh_did_segments(did)
    return segments[0] if segments else None


def webvh_explorer_dids_url(server_url: str, scid: str) -> str:
    """
    BCVH-style DID explorer query (see server ``/api/explorer/dids?scid=…``).

    ``server_url`` is the WebVH server base (e.g. ``https://sandbox.bcvh.vonx.io``).
    """
    base = server_url.strip().rstrip("/")
    encoded_scid = quote(scid, safe="")
    return f"{base}/api/explorer/dids?scid={encoded_scid}"


def webvh_explorer_resources_url(server_url: str, scid: str) -> str:
    """
    BCVH-style attested resources explorer (schemas, cred defs, revocation, status lists).

    Path: ``/api/explorer/resources?scid=…`` on the WebVH server base.
    """
    base = server_url.strip().rstrip("/")
    encoded_scid = quote(scid, safe="")
    return f"{base}/api/explorer/resources?scid={encoded_scid}"


def webvh_server_base_for_explorer(server_url: str | None, did: str | None) -> str | None:
    """Prefer configured ``server_url``; else ``https://<host>`` from ``did`` if parseable."""
    if server_url and server_url.strip():
        normalized_base = server_url.strip().rstrip("/")
        if not urlsplit(normalized_base).scheme:
            return f"https://{normalized_base}"
        return normalized_base
    if did:
        segments = _webvh_did_segments(did)
        if segments:
            return f"https://{segments[1]}"
    return None


def poll_until(
    fetch: Callable[[], T | None],
    *,
    timeout_sec: float,
    interval_sec: float,
    description: str,
) -> T | None:
    """
    Call ``fetch()`` until it returns a non-None value or timeout.

    ``fetch`` should return None while waiting (e.g. ACA-Py / DIDComm not ready yet).
    """
    e2e_log = logging.getLogger("webvh-e2e")
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        result = fetch()
        if result is not None:
            return result
        time.sleep(interval_sec)
    e2e_log.error("Timeout waiting for: %s", description)
    return None
