"""Setup phases: issuer wallet upgrade and AnonCreds schema / credential-definition publish."""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from typing import Any

from context import Context
from constants import (
    E2E_CRED_DEF_POST_RETRY_TIMEOUT_SEC,
    E2E_CRED_DEF_TAG,
    E2E_INDY_CRED_DEF_TAG_PREFIX,
    E2E_INDY_CRED_DEF_PUBLISH_SETTLE_SEC,
    E2E_REVOCATION_REGISTRY_SIZE,
    E2E_REV_REG_ACTIVE_POLL_SEC,
    E2E_REV_REG_ACTIVE_TIMEOUT_SEC,
    E2E_REV_REG_WAIT_LOG_INTERVAL_SEC,
    E2E_SCHEMA_ATTR_NAMES,
    E2E_SCHEMA_NAME,
    E2E_SCHEMA_VERSION,
    WALLET_UPGRADE_POLL_SEC,
    WALLET_UPGRADE_TIMEOUT_SEC,
)
from helpers import (
    LOG,
    format_json_for_log,
    log_http_failed,
    poll_until,
    tenant_wallet_name,
    tenant_wallet_storage_type,
)


_CRED_DEF_LOG_OMIT_KEYS = frozenset({"value"})


def _omit_json_keys(data: Any, omit: frozenset[str]) -> Any:
    """Deep-copy JSON-like structures, dropping selected keys (e.g. cred-def ``value`` blobs)."""
    if isinstance(data, dict):
        return {
            k: _omit_json_keys(v, omit) for k, v in data.items() if k not in omit
        }
    if isinstance(data, list):
        return [_omit_json_keys(item, omit) for item in data]
    return data


def _log_http_response(
    label: str,
    status_code: int,
    text: str,
    *,
    redact_keys: frozenset[str] | None = None,
) -> None:
    """Log HTTP status at info/error; full body only at debug (default run stays quiet)."""
    raw = text or ""
    if status_code >= 400:
        LOG.error("%s (HTTP %s)", label, status_code)
    else:
        LOG.info("%s (HTTP %s)", label, status_code)
    try:
        parsed = json.loads(raw)
        if redact_keys:
            parsed = _omit_json_keys(parsed, redact_keys)
        LOG.debug("%s response body:\n%s", label, format_json_for_log(parsed))
    except (json.JSONDecodeError, TypeError):
        snippet = raw[:2000] if raw else "(empty body)"
        LOG.debug("%s response text:\n%s", label, snippet)


def phase_upgrade_anoncreds_wallet(context: Context) -> bool:
    """POST /anoncreds/wallet/upgrade + poll GET /tenant/wallet until askar-anoncreds (or skip if already)."""
    client = context.issuer_client()

    initial_wallet_response = client.get_tenant_wallet()
    if not initial_wallet_response.ok:
        log_http_failed(
            "GET /tenant/wallet failed", initial_wallet_response, max_body=500
        )
        return False
    try:
        wallet = initial_wallet_response.json()
    except json.JSONDecodeError:
        LOG.error("GET /tenant/wallet returned non-JSON")
        return False

    wallet_name = tenant_wallet_name(wallet)
    if not wallet_name:
        LOG.error(
            "GET /tenant/wallet missing settings.wallet.name; cannot upgrade wallet"
        )
        return False

    wallet_storage_type = tenant_wallet_storage_type(wallet)
    if wallet_storage_type == "askar-anoncreds":
        LOG.info("Issuer wallet already askar-anoncreds; skipping upgrade")
        return True

    LOG.info(
        "Upgrading issuer wallet to askar-anoncreds (current type=%s)",
        wallet_storage_type,
    )
    upgrade_response = client.post_anoncreds_wallet_upgrade(wallet_name)
    if not upgrade_response.ok:
        log_http_failed(
            "POST /anoncreds/wallet/upgrade failed", upgrade_response, max_body=500
        )
        return False

    deadline = time.monotonic() + WALLET_UPGRADE_TIMEOUT_SEC
    poll_interval_sec = WALLET_UPGRADE_POLL_SEC
    while time.monotonic() < deadline:
        poll_wallet_response = client.get_tenant_wallet()
        if not poll_wallet_response.ok:
            LOG.warning(
                "GET /tenant/wallet during poll failed: %s",
                poll_wallet_response.status_code,
            )
            time.sleep(poll_interval_sec)
            continue
        try:
            polled_wallet = poll_wallet_response.json()
        except json.JSONDecodeError:
            time.sleep(poll_interval_sec)
            continue
        if tenant_wallet_storage_type(polled_wallet) == "askar-anoncreds":
            LOG.info("Issuer wallet upgraded to askar-anoncreds")
            return True
        time.sleep(poll_interval_sec)

    LOG.error("Timed out waiting for wallet type askar-anoncreds")
    return False


def _extract_schema_id_from_post(body: dict[str, Any]) -> str | None:
    schema_state_block = body.get("schema_state") or body.get("sent") or {}
    schema_id_value = schema_state_block.get("schema_id")
    return str(schema_id_value) if schema_id_value else None


def _extract_cred_def_id_from_post(body: dict[str, Any]) -> str | None:
    cred_def_state_block = body.get("credential_definition_state") or body.get("sent") or {}
    credential_definition_id_value = cred_def_state_block.get("credential_definition_id")
    return str(credential_definition_id_value) if credential_definition_id_value else None


def _indy_unqualified_issuer_id(did: str | None) -> str | None:
    """
    Indy anoncreds list/write APIs on some deployments resolve ``issuerId`` / ``schema_issuer_id``
    only when the issuer is **unqualified** (no ``did:sov:`` prefix). Short public DID or
    ``did:sov:…`` both normalize to the ledger short form.
    """
    if not did:
        return None
    did_str = did.strip()
    if did_str.startswith("did:sov:"):
        return did_str[8:]
    return did_str


def _indy_strip_did_sov_prefix(resource_id: str | None) -> str | None:
    """Strip leading ``did:sov:`` so Indy ledger ids match unqualified anoncreds resolution."""
    if not resource_id:
        return None
    resource_id_str = resource_id.strip()
    if resource_id_str.startswith("did:sov:"):
        return resource_id_str[8:]
    return resource_id_str


_SCHEMA_DUP_PHRASES = (
    "already exists",
    "already exist",
    "duplicate",
    "schema already",
    "exists on",
)


def _phase_publish_anoncreds_schema(
    context: Context,
    *,
    issuer_did: str | None,
    schema_attr: str,
    log_label: str,
    indy_unqualified_ids: bool = False,
) -> bool:
    """POST /anoncreds/schema (idempotent list); store on context.<schema_attr>. Indy path strips did:sov:."""
    if not issuer_did:
        if log_label == "webvh":
            LOG.error("No did:webvh on context; run webvh-create first")
        else:
            LOG.error("No Indy public DID on context; run indy-register-public-did first")
        return False

    if indy_unqualified_ids:
        issuer_did = _indy_unqualified_issuer_id(issuer_did)
        if not issuer_did:
            LOG.error("[%s] Could not derive unqualified issuer id", log_label)
            return False

    name = E2E_SCHEMA_NAME
    version = E2E_SCHEMA_VERSION
    attr_names = E2E_SCHEMA_ATTR_NAMES
    client = context.issuer_client()
    list_query = {
        "schema_name": name,
        "schema_version": version,
        "schema_issuer_id": issuer_did,
    }

    def _schemas_get(note: str = "") -> Any:
        suffix = f" {note}" if note else ""
        LOG.info("[%s] GET /anoncreds/schemas%s", log_label, suffix)
        LOG.debug("[%s] GET /anoncreds/schemas query:\n%s", log_label, format_json_for_log(list_query))
        r = client.get_anoncreds_schemas(params=list_query)
        _log_http_response("GET /anoncreds/schemas", r.status_code, r.text or "")
        return r

    def _try_schema_reuse_from_list(resp: Any, *, after_dup_post: bool) -> bool:
        if not resp.ok:
            return False
        try:
            data = resp.json()
        except json.JSONDecodeError:
            data = {}
        ids = data.get("schema_ids") or []
        if ids:
            sid = (
                _indy_strip_did_sov_prefix(str(ids[0]))
                if indy_unqualified_ids
                else str(ids[0])
            )
            setattr(context, schema_attr, sid)
            if after_dup_post:
                LOG.info("[%s] Schema already exists; schema_id=%s", log_label, sid)
            else:
                LOG.info("[%s] Reusing existing schema_id=%s", log_label, sid)
            return True
        if after_dup_post and indy_unqualified_ids and issuer_did:
            sid = f"{issuer_did}:2:{name}:{version}"
            setattr(context, schema_attr, sid)
            LOG.info(
                "[%s] Schema already on ledger (list empty); using Indy schema_id=%s",
                log_label,
                sid,
            )
            return True
        return False

    if _try_schema_reuse_from_list(_schemas_get(), after_dup_post=False):
        return True

    post_body = {
        "schema": {
            "attrNames": attr_names,
            "issuerId": issuer_did,
            "name": name,
            "version": version,
        },
        "options": {},
    }
    create_response = client.post_anoncreds_schema(post_body)
    if not create_response.ok:
        text = create_response.text or ""
        _log_http_response("POST /anoncreds/schema", create_response.status_code, text)
        tl = text.lower()
        if create_response.status_code == 400 and any(p in tl for p in _SCHEMA_DUP_PHRASES):
            if _try_schema_reuse_from_list(
                _schemas_get("(after already-exists)"),
                after_dup_post=True,
            ):
                return True
        LOG.error("[%s] POST /anoncreds/schema failed", log_label)
        return False

    try:
        created = create_response.json()
    except json.JSONDecodeError:
        LOG.error("[%s] POST /anoncreds/schema returned non-JSON", log_label)
        return False

    LOG.debug("[%s] POST /anoncreds/schema response:\n%s", log_label, format_json_for_log(created))

    schema_id = _extract_schema_id_from_post(created)
    if not schema_id:
        LOG.error("[%s] Schema create response missing schema_id", log_label)
        LOG.debug("Schema create body:\n%s", format_json_for_log(created))
        return False
    if indy_unqualified_ids:
        schema_id = _indy_strip_did_sov_prefix(schema_id) or schema_id
    setattr(context, schema_attr, schema_id)
    LOG.info("[%s] Published schema_id=%s", log_label, schema_id)
    return True


def _anoncreds_cred_def_tag_from_id(cred_def_id: str) -> str:
    """Last ``:`` segment of a cred def id (the publish ``tag``)."""
    parts = cred_def_id.rsplit(":", 1)
    return parts[-1] if parts else ""


def _rev_reg_record_from_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Unwrap ``{"result": IssuerRevRegRecord}`` or occasional double-wrapped responses."""
    top = payload.get("result")
    if isinstance(top, dict) and isinstance(top.get("result"), dict):
        return top["result"]
    if isinstance(top, dict):
        return top
    return None


# Issuable for issue-credential (Indy often active/posted; WebVH may use finished).
_REV_REG_READY_STATES = frozenset({"active", "finished"})
_REV_REG_TERMINAL_BAD = frozenset({"full", "decommissioned"})


def _active_registry_poll_step(
    client: Any,
    cred_def_id: str,
    log_label: str,
    emit_progress: Callable[[str], None],
) -> bool | None:
    """Single GET active-registry poll: ``True`` ready, ``False`` error, ``None`` keep waiting."""
    active_registry_response = client.get_anoncreds_revocation_active_registry(cred_def_id)
    if active_registry_response.status_code == 404:
        emit_progress(
            f"active-registry 404 (no record yet) cred_def_id={cred_def_id} — still waiting"
        )
        return None
    if not active_registry_response.ok:
        emit_progress(
            f"active-registry HTTP {active_registry_response.status_code} "
            f"cred_def_id={cred_def_id} — still waiting"
        )
        return None
    try:
        payload = active_registry_response.json()
    except json.JSONDecodeError:
        emit_progress("active-registry returned non-JSON — still waiting")
        return None
    if not isinstance(payload, dict):
        return None
    registry_record = _rev_reg_record_from_payload(payload)
    if registry_record is None:
        emit_progress(
            f"active-registry missing result object; keys={list(payload.keys())!r} — still waiting"
        )
        return None
    err = (registry_record.get("error_msg") or "").strip()
    if err:
        LOG.error(
            "[%s] Active revocation registry error for cred_def_id=%s: %s",
            log_label,
            cred_def_id,
            err,
        )
        return False
    state = (registry_record.get("state") or "").strip().lower()
    rev_reg_id = registry_record.get("revoc_reg_id") or registry_record.get("rev_reg_id")
    if state in _REV_REG_TERMINAL_BAD:
        LOG.error(
            "[%s] Revocation registry in terminal state %r (cred_def_id=%s rev_reg_id=%s)",
            log_label,
            state,
            cred_def_id,
            rev_reg_id,
        )
        return False
    if state in _REV_REG_READY_STATES:
        LOG.info(
            "[%s] Revocation registry ready state=%s (rev_reg_id=%s cred_def_id=%s)",
            log_label,
            state,
            rev_reg_id,
            cred_def_id,
        )
        return True
    if state == "posted" and rev_reg_id:
        LOG.info(
            "[%s] Revocation registry state=posted with rev_reg_id (treating as ready; "
            "cred_def_id=%s)",
            log_label,
            cred_def_id,
        )
        return True
    emit_progress(
        f"revocation registry state={state or '?'} rev_reg_id={rev_reg_id!r} — still waiting"
    )
    return None


def _wait_for_active_revocation_registry(client: Any, cred_def_id: str, log_label: str) -> bool:
    """Poll GET …/active-registry/{cred_def_id} until ready (active/finished/posted+rev_reg_id) or fail."""
    last_progress_log = 0.0

    def maybe_progress(msg: str) -> None:
        nonlocal last_progress_log
        now = time.monotonic()
        if now - last_progress_log >= E2E_REV_REG_WAIT_LOG_INTERVAL_SEC:
            last_progress_log = now
            LOG.info("[%s] %s", log_label, msg)

    LOG.info(
        "[%s] Checking revocation active-registry for cred_def_id=%s (timeout=%.0fs)",
        log_label,
        cred_def_id,
        E2E_REV_REG_ACTIVE_TIMEOUT_SEC,
    )

    def fetch() -> bool | None:
        return _active_registry_poll_step(client, cred_def_id, log_label, maybe_progress)

    registry_poll_result = poll_until(
        fetch,
        timeout_sec=E2E_REV_REG_ACTIVE_TIMEOUT_SEC,
        interval_sec=E2E_REV_REG_ACTIVE_POLL_SEC,
        description=f"{log_label} revocation registry active (cred_def_id={cred_def_id})",
    )
    if registry_poll_result is True:
        return True
    if registry_poll_result is False:
        return False
    LOG.error(
        "[%s] Timed out waiting for active revocation registry (cred_def_id=%s)",
        log_label,
        cred_def_id,
    )
    return False


def _phase_publish_anoncreds_cred_def(
    context: Context,
    *,
    issuer_did: str | None,
    schema_id: str | None,
    cred_def_attr: str,
    log_label: str,
    webvh_resource_retry: bool,
    indy_unqualified_ids: bool = False,
    cred_def_tag: str | None = None,
) -> bool:
    """POST anoncreds cred-def + rev reg; reuse from list; WebVH optional resolver retry; wait active-registry."""
    schema_phase = "publish-schema-webvh" if log_label == "webvh" else "publish-schema-indy"
    if not issuer_did or not schema_id:
        LOG.error(
            "[%s] Missing issuer DID or schema_id; run %s first",
            log_label,
            schema_phase,
        )
        return False

    if indy_unqualified_ids:
        issuer_did = _indy_unqualified_issuer_id(issuer_did)
        schema_id = _indy_strip_did_sov_prefix(schema_id)
        if not issuer_did or not schema_id:
            LOG.error("[%s] Missing unqualified issuer or schema_id after normalization", log_label)
            return False

    tag = cred_def_tag if cred_def_tag is not None else E2E_CRED_DEF_TAG
    reg_size = E2E_REVOCATION_REGISTRY_SIZE
    client = context.issuer_client()

    list_query = {"schema_id": schema_id, "issuer_id": issuer_did}
    list_response = client.get_anoncreds_credential_definitions(params=list_query)
    LOG.info("[%s] GET /anoncreds/credential-definitions", log_label)
    LOG.debug(
        "[%s] GET /anoncreds/credential-definitions query:\n%s",
        log_label,
        format_json_for_log(list_query),
    )
    _log_http_response(
        "GET /anoncreds/credential-definitions",
        list_response.status_code,
        list_response.text or "",
        redact_keys=_CRED_DEF_LOG_OMIT_KEYS,
    )

    if list_response.ok:
        try:
            data = list_response.json()
        except json.JSONDecodeError:
            data = {}
        ids = data.get("credential_definition_ids") or []
        if ids:
            chosen: str | None = None
            for raw in ids:
                candidate_cred_def_id = str(raw)
                if indy_unqualified_ids:
                    candidate_cred_def_id = (
                        _indy_strip_did_sov_prefix(candidate_cred_def_id) or candidate_cred_def_id
                    )
                if cred_def_tag is not None:
                    if _anoncreds_cred_def_tag_from_id(candidate_cred_def_id) == tag:
                        chosen = candidate_cred_def_id
                        break
                else:
                    chosen = candidate_cred_def_id
                    break
            if chosen:
                setattr(context, cred_def_attr, chosen)
                LOG.info("[%s] Reusing existing credential_definition_id=%s", log_label, chosen)
                if not _wait_for_active_revocation_registry(client, chosen, log_label):
                    return False
                return True

    body = {
        "credential_definition": {
            "issuerId": issuer_did,
            "schemaId": schema_id,
            "tag": tag,
        },
        "options": {
            "support_revocation": True,
            "revocation_registry_size": reg_size,
        },
    }

    deadline = time.monotonic() + E2E_CRED_DEF_POST_RETRY_TIMEOUT_SEC
    attempt = 0
    while time.monotonic() < deadline:
        create_response = client.post_anoncreds_credential_definition(body)
        if create_response.ok:
            try:
                created = create_response.json()
            except json.JSONDecodeError:
                LOG.error("[%s] POST /anoncreds/credential-definition returned non-JSON", log_label)
                return False
            LOG.debug(
                "[%s] POST /anoncreds/credential-definition response:\n%s",
                log_label,
                format_json_for_log(_omit_json_keys(created, _CRED_DEF_LOG_OMIT_KEYS)),
            )
            cred_def_id = _extract_cred_def_id_from_post(created)
            if not cred_def_id:
                LOG.error("[%s] Cred def create response missing credential_definition_id", log_label)
                LOG.debug(
                    "Cred def create body:\n%s",
                    format_json_for_log(_omit_json_keys(created, _CRED_DEF_LOG_OMIT_KEYS)),
                )
                return False
            if indy_unqualified_ids:
                cred_def_id = _indy_strip_did_sov_prefix(cred_def_id) or cred_def_id
            setattr(context, cred_def_attr, cred_def_id)
            LOG.info(
                "[%s] Published credential_definition_id=%s (revocation_registry_size=%s)",
                log_label,
                cred_def_id,
                reg_size,
            )
            if log_label == "indy" and E2E_INDY_CRED_DEF_PUBLISH_SETTLE_SEC > 0:
                LOG.info(
                    "[%s] Waiting %.0fs for revocation registry / endorser to settle before issue",
                    log_label,
                    E2E_INDY_CRED_DEF_PUBLISH_SETTLE_SEC,
                )
                time.sleep(E2E_INDY_CRED_DEF_PUBLISH_SETTLE_SEC)
            if not _wait_for_active_revocation_registry(client, cred_def_id, log_label):
                return False
            return True

        err_text = (create_response.text or "").lower()
        _log_http_response(
            "POST /anoncreds/credential-definition",
            create_response.status_code,
            create_response.text or "",
            redact_keys=_CRED_DEF_LOG_OMIT_KEYS,
        )
        if webvh_resource_retry and "resolving resource" in err_text:
            attempt += 1
            LOG.info(
                "[%s] Cred-def create retry (attempt %s) after WebVH resource lag…",
                log_label,
                attempt,
            )
            time.sleep(min(2.0 ** min(attempt, 5), 20.0))
            continue

        LOG.error("[%s] POST /anoncreds/credential-definition failed", log_label)
        return False

    LOG.error("[%s] Timed out publishing credential definition", log_label)
    return False


def phase_publish_schema(context: Context) -> bool:
    """WebVH issuer schema publish (idempotent)."""
    return _phase_publish_anoncreds_schema(
        context,
        issuer_did=context.webvh_last_created_did,
        schema_attr="webvh_schema_id",
        log_label="webvh",
    )


def phase_publish_cred_def(context: Context) -> bool:
    """WebVH cred-def + rev reg (needs webvh_schema_id + issuer DID)."""
    return _phase_publish_anoncreds_cred_def(
        context,
        issuer_did=context.webvh_last_created_did,
        schema_id=context.webvh_schema_id,
        cred_def_attr="webvh_cred_def_id",
        log_label="webvh",
        webvh_resource_retry=True,
    )


def phase_publish_schema_indy(context: Context) -> bool:
    """Indy issuer schema (unqualified issuer id for anoncreds/ledger)."""
    return _phase_publish_anoncreds_schema(
        context,
        issuer_did=_indy_unqualified_issuer_id(context.indy_public_did),
        schema_attr="indy_schema_id",
        log_label="indy",
        indy_unqualified_ids=True,
    )


def phase_publish_cred_def_indy(context: Context) -> bool:
    """POST /anoncreds/credential-definition with revocation (same options as WebVH E2E)."""
    issuer = _indy_unqualified_issuer_id(context.indy_public_did)
    tag = f"{E2E_INDY_CRED_DEF_TAG_PREFIX}-{uuid.uuid4().hex[:12]}"
    LOG.info("[indy] Publishing credential definition with unique tag=%s", tag)
    return _phase_publish_anoncreds_cred_def(
        context,
        issuer_did=issuer,
        schema_id=context.indy_schema_id,
        cred_def_attr="indy_cred_def_id",
        log_label="indy",
        webvh_resource_retry=False,
        indy_unqualified_ids=True,
        cred_def_tag=tag,
    )
