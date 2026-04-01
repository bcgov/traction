"""Small helpers for WebVH harness (unauthenticated WebVH server calls)."""

from __future__ import annotations

import base64
import json
import logging
from typing import Any
from urllib.parse import quote, urlsplit

import requests

LOG = logging.getLogger(__name__)


def fetch_witness_invitation_json(server_url: str, witness_did_fragment: str) -> dict[str, Any]:
    """
    GET the OOB invitation JSON from the WebVH server (unauthenticated).

    ``witness_did_fragment`` is the key material after ``did:key:`` (used as ``_oobid``).
    """
    base = server_url.rstrip("/")
    url = f"{base}/api/invitations?_oobid={witness_did_fragment}"
    LOG.debug("Fetching witness invitation: %s", url)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def witness_invitation_to_didcomm(invitation: dict[str, Any]) -> str:
    """Match Tenant UI: base64 JSON + ``didcomm://?oob=`` prefix."""
    raw = json.dumps(invitation)
    b64 = base64.b64encode(raw.encode()).decode("ascii")
    return f"didcomm://?oob={b64}"


def build_witness_invitation_didcomm(server_url: str, witness_did_fragment: str) -> str:
    """Fetch invitation from WebVH server and encode for ``POST /did/webvh/configuration``."""
    inv = fetch_witness_invitation_json(server_url, witness_did_fragment)
    return witness_invitation_to_didcomm(inv)


def _webvh_did_segments(did: str) -> tuple[str, str, str, str] | None:
    """``(scid, host, namespace, path_segment)`` for ``did:webvh:…`` or ``None``."""
    parts = did.split(":")
    if len(parts) >= 6 and parts[0] == "did" and parts[1] == "webvh":
        return parts[2], parts[3], parts[4], parts[5]
    return None


def webvh_scid_from_did(did: str) -> str | None:
    """SCID component of a ``did:webvh`` string."""
    seg = _webvh_did_segments(did)
    return seg[0] if seg else None


def webvh_explorer_dids_url(server_url: str, scid: str) -> str:
    """
    BCVH-style DID explorer query (see server ``/api/explorer/dids?scid=…``).

    ``server_url`` is the WebVH server base (e.g. ``https://sandbox.bcvh.vonx.io``).
    """
    base = server_url.strip().rstrip("/")
    q = quote(scid, safe="")
    return f"{base}/api/explorer/dids?scid={q}"


def webvh_server_base_for_explorer(server_url: str | None, did: str | None) -> str | None:
    """Prefer configured ``server_url``; else ``https://<host>`` from ``did`` if parseable."""
    if server_url and server_url.strip():
        u = server_url.strip().rstrip("/")
        if not urlsplit(u).scheme:
            return f"https://{u}"
        return u
    if did:
        seg = _webvh_did_segments(did)
        if seg:
            return f"https://{seg[1]}"
    return None
