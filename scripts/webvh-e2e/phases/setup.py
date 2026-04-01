"""Setup phases: issuer wallet upgrade and AnonCreds publish placeholders."""

from __future__ import annotations

import json
import logging
import os
import time

from typing import Any

from context import Context

LOG = logging.getLogger(__name__)


def _wallet_settings_blob(wallet: dict[str, Any]) -> dict[str, Any]:
    settings_value = wallet.get("settings")
    return settings_value if isinstance(settings_value, dict) else {}


def _wallet_name_from_response(wallet: dict[str, Any]) -> str | None:
    """
    Multitenant wallet name for ``POST /anoncreds/wallet/upgrade``.

    ACA-Py ``GET /settings`` does not return ``wallet.name`` (filtered dict); use
    ``GET /tenant/wallet`` → ``settings['wallet.name']``.
    """
    name = _wallet_settings_blob(wallet).get("wallet.name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return None


def _wallet_type_from_response(wallet: dict[str, Any]) -> str | None:
    """Wallet storage type (e.g. askar / askar-anoncreds) from tenant wallet payload."""
    top_level = wallet.get("type")
    if isinstance(top_level, str) and top_level:
        return top_level
    from_settings = _wallet_settings_blob(wallet).get("wallet.type")
    return from_settings if isinstance(from_settings, str) else None


def _wallet_upgrade_poll_sec() -> float:
    return float(os.environ.get("WEBVH_WALLET_UPGRADE_POLL_SEC", "2"))


def _wallet_upgrade_timeout_sec() -> float:
    return float(os.environ.get("WEBVH_WALLET_UPGRADE_TIMEOUT_SEC", "120"))


def phase_upgrade_anoncreds_wallet(ctx: Context) -> bool:
    """
    Ensure issuer wallet is upgraded to askar-anoncreds (POST /anoncreds/wallet/upgrade, poll GET /tenant/wallet).

    Requires issuer bearer token. Skips if already askar-anoncreds.
    """
    client = ctx.issuer_client()

    initial_wallet_response = client.get_tenant_wallet()
    if not initial_wallet_response.ok:
        LOG.error(
            "GET /tenant/wallet failed: %s %s",
            initial_wallet_response.status_code,
            initial_wallet_response.text[:500],
        )
        return False
    try:
        wallet = initial_wallet_response.json()
    except json.JSONDecodeError:
        LOG.error("GET /tenant/wallet returned non-JSON")
        return False

    wallet_name = _wallet_name_from_response(wallet)
    if not wallet_name:
        LOG.error(
            "GET /tenant/wallet missing settings.wallet.name; cannot upgrade wallet"
        )
        return False

    wallet_storage_type = _wallet_type_from_response(wallet)
    if wallet_storage_type == "askar-anoncreds":
        LOG.info("Issuer wallet already askar-anoncreds; skipping upgrade")
        return True

    LOG.info(
        "Upgrading issuer wallet to askar-anoncreds (current type=%s)",
        wallet_storage_type,
    )
    upgrade_response = client.post_anoncreds_wallet_upgrade(wallet_name)
    if not upgrade_response.ok:
        LOG.error(
            "POST /anoncreds/wallet/upgrade failed: %s %s",
            upgrade_response.status_code,
            upgrade_response.text[:500],
        )
        return False

    deadline = time.monotonic() + _wallet_upgrade_timeout_sec()
    poll_interval_sec = _wallet_upgrade_poll_sec()
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
        if _wallet_type_from_response(polled_wallet) == "askar-anoncreds":
            LOG.info("Issuer wallet upgraded to askar-anoncreds")
            return True
        time.sleep(poll_interval_sec)

    LOG.error("Timed out waiting for wallet type askar-anoncreds")
    return False


def _schema_attr_names_from_env() -> list[str]:
    raw = os.environ.get("WEBVH_E2E_SCHEMA_ATTRS", "name,score")
    return [part.strip() for part in raw.split(",") if part.strip()]


def _e2e_schema_name() -> str:
    return (os.environ.get("WEBVH_E2E_SCHEMA_NAME") or "WebVHE2EHarness").strip()


def _e2e_schema_version() -> str:
    return (os.environ.get("WEBVH_E2E_SCHEMA_VERSION") or "1.0").strip()


def _e2e_cred_def_tag() -> str:
    return (os.environ.get("WEBVH_E2E_CRED_DEF_TAG") or _e2e_schema_name()).strip()


def _revocation_registry_size() -> int:
    try:
        return max(1, int(os.environ.get("WEBVH_E2E_REVOCATION_REGISTRY_SIZE", "4")))
    except ValueError:
        return 4


def _extract_schema_id_from_post(body: dict[str, Any]) -> str | None:
    state = body.get("schema_state") or body.get("sent") or {}
    sid = state.get("schema_id")
    return str(sid) if sid else None


def _extract_cred_def_id_from_post(body: dict[str, Any]) -> str | None:
    state = body.get("credential_definition_state") or body.get("sent") or {}
    cid = state.get("credential_definition_id")
    return str(cid) if cid else None


def phase_publish_schema(ctx: Context) -> bool:
    """
    POST /anoncreds/schema for the WebVH issuer DID (``ctx.webvh_last_created_did``).

    Idempotent: if a matching schema exists (name, version, issuer), reuse it.
    """
    issuer_did = ctx.webvh_last_created_did
    if not issuer_did:
        LOG.error("No did:webvh on context; run webvh-create first")
        return False

    name = _e2e_schema_name()
    version = _e2e_schema_version()
    attr_names = _schema_attr_names_from_env()
    client = ctx.issuer_client()

    list_response = client.get_anoncreds_schemas(
        params={
            "schema_name": name,
            "schema_version": version,
            "schema_issuer_id": issuer_did,
        }
    )
    if list_response.ok:
        try:
            data = list_response.json()
        except json.JSONDecodeError:
            data = {}
        ids = data.get("schema_ids") or []
        if ids:
            ctx.webvh_schema_id = str(ids[0])
            LOG.info("Reusing existing schema_id=%s", ctx.webvh_schema_id)
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
        if create_response.status_code == 400 and "already exists" in text.lower():
            list_response = client.get_anoncreds_schemas(
                params={
                    "schema_name": name,
                    "schema_version": version,
                    "schema_issuer_id": issuer_did,
                }
            )
            if list_response.ok:
                data = list_response.json()
                ids = data.get("schema_ids") or []
                if ids:
                    ctx.webvh_schema_id = str(ids[0])
                    LOG.info("Schema already exists; schema_id=%s", ctx.webvh_schema_id)
                    return True
        LOG.error(
            "POST /anoncreds/schema failed: %s %s",
            create_response.status_code,
            text[:800],
        )
        return False

    try:
        created = create_response.json()
    except json.JSONDecodeError:
        LOG.error("POST /anoncreds/schema returned non-JSON")
        return False

    schema_id = _extract_schema_id_from_post(created)
    if not schema_id:
        LOG.error("Schema create response missing schema_id: %s", created)
        return False
    ctx.webvh_schema_id = schema_id
    LOG.info("Published schema_id=%s", schema_id)
    return True


def phase_publish_cred_def(ctx: Context) -> bool:
    """
    POST /anoncreds/credential-definition with revocation (default registry size 4).

    Requires ``ctx.webvh_schema_id`` and WebVH issuer DID.
    """
    issuer_did = ctx.webvh_last_created_did
    schema_id = ctx.webvh_schema_id
    if not issuer_did or not schema_id:
        LOG.error("Missing issuer DID or schema_id; run publish-schema-webvh first")
        return False

    tag = _e2e_cred_def_tag()
    reg_size = _revocation_registry_size()
    client = ctx.issuer_client()

    list_response = client.get_anoncreds_credential_definitions(
        params={"schema_id": schema_id, "issuer_id": issuer_did}
    )
    if list_response.ok:
        try:
            data = list_response.json()
        except json.JSONDecodeError:
            data = {}
        ids = data.get("credential_definition_ids") or []
        if ids:
            ctx.webvh_cred_def_id = str(ids[0])
            LOG.info("Reusing existing credential_definition_id=%s", ctx.webvh_cred_def_id)
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

    deadline = time.monotonic() + 120.0
    attempt = 0
    while time.monotonic() < deadline:
        create_response = client.post_anoncreds_credential_definition(body)
        if create_response.ok:
            try:
                created = create_response.json()
            except json.JSONDecodeError:
                LOG.error("POST /anoncreds/credential-definition returned non-JSON")
                return False
            cred_def_id = _extract_cred_def_id_from_post(created)
            if not cred_def_id:
                LOG.error("Cred def create missing id: %s", created)
                return False
            ctx.webvh_cred_def_id = cred_def_id
            LOG.info(
                "Published credential_definition_id=%s (revocation_registry_size=%s)",
                cred_def_id,
                reg_size,
            )
            return True

        err_text = (create_response.text or "").lower()
        if "resolving resource" in err_text:
            attempt += 1
            time.sleep(min(2.0 ** min(attempt, 5), 20.0))
            continue

        LOG.error(
            "POST /anoncreds/credential-definition failed: %s %s",
            create_response.status_code,
            (create_response.text or "")[:800],
        )
        return False

    LOG.error("Timed out publishing credential definition (WebVH resource lag)")
    return False
