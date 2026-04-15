"""Shared helpers for the WebVH E2E harness (wallet JSON, WebVH URLs, polling)."""

from __future__ import annotations

import base64
import json
import logging
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar
from urllib.parse import quote, urlsplit

import requests

LOG = logging.getLogger("webvh-e2e")

# Logging convention (default run = INFO, ``-v`` = DEBUG):
# - INFO: phase steps, HTTP method+path, status lines, outcomes.
# - DEBUG: request/response JSON and other large payloads (incl. ``TractionClient`` POST/PUT bodies).
# - ERROR/WARNING: failures and retries.

if TYPE_CHECKING:
    from context import Context

T = TypeVar("T")


def format_json_for_log(data: Any) -> str:
    """Pretty JSON for DEBUG logs by convention; non-fatal ``TypeError`` → ``str(data)``."""
    try:
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
    except TypeError:
        return str(data)


def http_json_dict(response: requests.Response) -> dict[str, Any] | None:
    """Parse a ``requests`` response body as a JSON object, or ``None``."""
    try:
        parsed = response.json()
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def v20_cred_ex_record_core(cred_ex_record: Any) -> dict[str, Any]:
    """
    ACA-Py often wraps the v2.0 credential exchange in ``cred_ex_record`` (``V20CredExRecordDetail``):
    applies to **list** ``GET /issue-credential-2.0/records`` and **single-record** GET by id.
    """
    if not isinstance(cred_ex_record, dict):
        return {}
    inner = cred_ex_record.get("cred_ex_record")
    if isinstance(inner, dict):
        return inner
    return cred_ex_record


def tenant_wallet_settings(tenant_wallet: dict[str, Any]) -> dict[str, Any]:
    """``settings`` object from ``GET /tenant/wallet`` JSON (multitenant ACA-Py)."""
    settings_value = tenant_wallet.get("settings")
    return settings_value if isinstance(settings_value, dict) else {}


def tenant_wallet_name(tenant_wallet: dict[str, Any]) -> str | None:
    """
    Wallet name for ``POST /anoncreds/wallet/upgrade`` (``settings['wallet.name']`` on tenant wallet).
    """
    name = tenant_wallet_settings(tenant_wallet).get("wallet.name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return None


def tenant_wallet_storage_type(tenant_wallet: dict[str, Any]) -> str | None:
    """Storage type (e.g. ``askar`` / ``askar-anoncreds``) from ``GET /tenant/wallet``."""
    top_level = tenant_wallet.get("type")
    if isinstance(top_level, str) and top_level:
        return top_level
    from_settings = tenant_wallet_settings(tenant_wallet).get("wallet.type")
    return from_settings if isinstance(from_settings, str) else None


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


def _webvh_explorer_url(server_url: str, scid: str, *, path: str) -> str:
    """``/api/explorer/{path}?scid=…`` on the WebVH / BCVH server base."""
    base = server_url.strip().rstrip("/")
    return f"{base}/api/explorer/{path}?scid={quote(scid, safe='')}"


def webvh_explorer_dids_url(server_url: str, scid: str) -> str:
    """BCVH-style DID explorer (``/api/explorer/dids?scid=…``). ``server_url`` is the WebVH base."""
    return _webvh_explorer_url(server_url, scid, path="dids")


def webvh_explorer_resources_url(server_url: str, scid: str) -> str:
    """BCVH-style resources explorer (schemas, cred defs, revocation, etc.)."""
    return _webvh_explorer_url(server_url, scid, path="resources")


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
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        result = fetch()
        if result is not None:
            return result
        time.sleep(interval_sec)
    LOG.error("Timeout waiting for: %s", description)
    return None


def log_http_failed(
    what: str,
    response: Any,
    *,
    max_body: int = 4000,
    log_debug_body: bool = True,
) -> None:
    """Log a failed ``requests`` response: ERROR with status; optional DEBUG body (truncated)."""
    code = getattr(response, "status_code", "?")
    LOG.error("%s (HTTP %s)", what, code)
    if not log_debug_body:
        return
    text = (getattr(response, "text", None) or "")[:max_body]
    if text:
        LOG.debug("%s\n%s", what, text)


class HarnessLogger:
    """CLI setup, phase banners, run footer, summary (``LOG`` is the underlying logger)."""

    LOG = LOG
    _SUMMARY_LABEL_WIDTH = 22

    @classmethod
    def configure_cli_logging(cls, *, verbose: bool) -> None:
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format="%(message)s",
        )

    @classmethod
    def log_context_init_failed(cls, message: str) -> None:
        cls.LOG.error("%s", message)

    @classmethod
    def log_run_start(cls, traction_url: str, profile: str) -> None:
        cls.LOG.info("traction_url=%s profile=%s", traction_url, profile)
        cls.LOG.info("")

    @classmethod
    def log_phase_begin(cls, phase_name: str, *, is_first_phase: bool) -> None:
        if not is_first_phase:
            cls.LOG.info("")
        cls.LOG.info("-- %s --", phase_name)

    @classmethod
    def log_phase_uncaught_exception(cls, phase_name: str, exc: BaseException) -> None:
        cls.LOG.error("%s: %s", phase_name, exc)

    @classmethod
    def log_run_footer(
        cls,
        *,
        success: bool,
        phases_completed: int,
        phase_count: int,
        elapsed_seconds: float,
    ) -> None:
        cls.LOG.info("")
        cls.LOG.info(
            "%s  %s/%s phases  %.1fs",
            "ok" if success else "failed",
            phases_completed,
            phase_count,
            elapsed_seconds,
        )

    @classmethod
    def _log_summary_kv(cls, indent: str, label: str, value: object) -> None:
        cls.LOG.info("%s%-*s  %s", indent, cls._SUMMARY_LABEL_WIDTH, label, value)

    @classmethod
    def log_run_summary(
        cls, context: "Context", stop: str | None, plan: tuple[str, ...] | list[str]
    ) -> None:
        cls.LOG.info("")
        cls.LOG.info("=== summary ===")
        cls.LOG.info("")
        cls.LOG.info("  run")
        cls._log_summary_kv("    ", "traction_url", context.base_url)

        if context.webvh_last_create_namespace is not None:
            cls.LOG.info("")
            cls.LOG.info("  webvh (create)")
            if context.webvh_last_created_did:
                last_created_did = context.webvh_last_created_did
                cls._log_summary_kv("    ", "did", last_created_did)
                scid = webvh_scid_from_did(last_created_did)
                explorer_base = webvh_server_base_for_explorer(
                    context.webvh_last_create_server_url, last_created_did
                )
                if scid and explorer_base:
                    cls._log_summary_kv(
                        "    ",
                        "explorer (dids)",
                        webvh_explorer_dids_url(explorer_base, scid),
                    )
                    cls._log_summary_kv(
                        "    ",
                        "explorer (resources)",
                        webvh_explorer_resources_url(explorer_base, scid),
                    )
            elif stop is None:
                cls._log_summary_kv("    ", "did", "(not in create response yet)")

        elif context.webvh_server_url and "configure-webvh-plugin" in plan:
            cls.LOG.info("")
            cls.LOG.info("  webvh (controller)")
            cls._log_summary_kv("    ", "server_url", context.webvh_server_url)

        if context.indy_public_did or context.indy_endorser_connection_id:
            cls.LOG.info("")
            cls.LOG.info("  indy (bcovrin)")
            if context.indy_write_ledger_id:
                cls._log_summary_kv("    ", "write_ledger_id", context.indy_write_ledger_id)
            if context.indy_endorser_connection_id:
                cls._log_summary_kv(
                    "    ", "endorser_connection_id", context.indy_endorser_connection_id
                )
            if context.indy_public_did:
                cls._log_summary_kv("    ", "public_did", context.indy_public_did)
            if context.indy_schema_id:
                cls._log_summary_kv("    ", "schema_id", context.indy_schema_id)
            if context.indy_cred_def_id:
                cls._log_summary_kv(
                    "    ", "credential_definition_id", context.indy_cred_def_id
                )
