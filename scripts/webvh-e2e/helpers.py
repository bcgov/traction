"""Shared helpers for the WebVH E2E harness (pure utilities and WebVH host HTTP)."""

from __future__ import annotations

import base64
import json
from typing import Any

import requests

# Unauthenticated WebVH host (witness invitations — no tenant Bearer).
_WEBVH_HTTP = requests.Session()


def build_witness_invitation(server_url: str, witness_did: str) -> str:
    """GET ``{server}/api/invitations?_oobid=…``; return ``didcomm://?oob=…``."""
    oobid = witness_did.removeprefix("did:key:")
    if not oobid or oobid == witness_did or "/" in oobid:
        raise ValueError(f"Unexpected witness DID format: {witness_did!r}")
    url = f"{server_url.rstrip('/')}/api/invitations"
    r = _WEBVH_HTTP.get(url, params={"_oobid": oobid}, timeout=60)
    r.raise_for_status()
    raw = json.dumps(r.json(), separators=(",", ":")).encode("utf-8")
    return f"didcomm://?oob={base64.standard_b64encode(raw).decode('ascii')}"


def did_str(value: Any) -> str | None:
    if isinstance(value, str) and value.startswith("did:"):
        return value
    return None


def did_from_webvh_create_body(data: Any) -> str | None:
    """Best-effort DID from POST /did/webvh/create JSON (plugin returns server log state, not ResolutionResult)."""
    if not isinstance(data, dict):
        return None
    for candidate in (
        data.get("did"),
        (data.get("did_document") or {}).get("id"),
        (data.get("document") or {}).get("id"),
        (data.get("state") or {}).get("id"),
    ):
        d = did_str(candidate)
        if d:
            return d
    doc = data.get("document")
    if isinstance(doc, dict):
        d = did_str((doc.get("state") or {}).get("id"))
        if d:
            return d
    return None


def parse_schema_attr_names(raw: str | None) -> list[str]:
    if raw is None or not str(raw).strip():
        return ["name", "score"]
    parts = [x.strip() for x in str(raw).split(",") if x.strip()]
    return parts if parts else ["name", "score"]
