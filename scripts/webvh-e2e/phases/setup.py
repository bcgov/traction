"""Schema/credential-definition publication phases and revocation-registry checks."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import requests

from context import Context, env_flag
from harness_log import LOG, detail_field_line, dim, headline_request, party_headline, wrap_dim_block
from helpers import parse_schema_attr_names

def _anoncreds_issuer_id(ctx: Context) -> str | None:
    """Schema and cred-def ``issuerId``: WebVH DID from create, or ``WEBVH_SCHEMA_ISSUER_ID``."""
    v = (os.environ.get("WEBVH_SCHEMA_ISSUER_ID") or "").strip() or ctx.webvh_issuer_did
    return v or None


def _revocation_ids_from_issuer_record(rec: dict[str, Any]) -> tuple[str | None, str | None]:
    """``revoc_reg_def.id`` (definition) and ``revoc_reg_id`` (issuer registry / entry handle)."""
    rdef = rec.get("revoc_reg_def")
    def_id = rdef.get("id") if isinstance(rdef, dict) else None
    if def_id is not None:
        def_id = str(def_id)
    reg_id = rec.get("revoc_reg_id")
    if reg_id is not None:
        reg_id = str(reg_id)
    return def_id, reg_id


# IssuerRevRegRecord uses ``active``; some AnonCreds / resolver paths report ``finished`` when published.
_REV_REG_LEDGER_READY_STATES = frozenset({"active", "finished"})


def _active_registry_http_retryable(status: int) -> bool:
    """Treat rate-limit and server errors like \"not ready\" and keep polling."""
    return status == 429 or 500 <= status <= 599


def _issuer_rev_reg_record_like(d: dict[str, Any]) -> bool:
    """True if ``d`` looks like an ACA-Py IssuerRevRegRecord (not a random nested dict)."""
    rdef = d.get("revoc_reg_def")
    if isinstance(rdef, dict) and rdef.get("id"):
        return True
    def_id, reg_id = _revocation_ids_from_issuer_record(d)
    return bool(def_id and reg_id)


def _deep_find_issuer_rev_reg_record(obj: Any, depth: int = 0) -> dict[str, Any] | None:
    if depth > 12 or not isinstance(obj, (dict, list)):
        return None
    if isinstance(obj, dict):
        if _issuer_rev_reg_record_like(obj):
            return obj
        for v in obj.values():
            found = _deep_find_issuer_rev_reg_record(v, depth + 1)
            if found:
                return found
        return None
    for item in obj:
        found = _deep_find_issuer_rev_reg_record(item, depth + 1)
        if found:
            return found
    return None


def _try_revocation_record_via_cred_def_get(
    ctx: Context, cred_def_id: str
) -> dict[str, Any] | None:
    """If ``active-registry`` fails, try ``GET /anoncreds/credential-definition/...`` for embedded rev-reg data."""
    try:
        r = ctx.issuer_client().get_anoncreds_credential_definition(cred_def_id)
    except requests.RequestException as exc:
        LOG.debug("cred-def GET (rev fallback): %s", exc)
        return None
    if r.status_code != 200:
        LOG.debug("cred-def GET (rev fallback) HTTP %s", r.status_code)
        return None
    try:
        body = r.json()
    except json.JSONDecodeError:
        return None
    rec = _deep_find_issuer_rev_reg_record(body)
    if rec:
        st = rec.get("state")
        if st in _REV_REG_LEDGER_READY_STATES or st is None:
            return rec
        def_id, reg_id = _revocation_ids_from_issuer_record(rec)
        if def_id and reg_id:
            LOG.debug(
                "cred-def GET (rev fallback) accepting state=%r (have rev def + reg ids)",
                st,
            )
            return rec
        LOG.debug("cred-def GET (rev fallback) record state=%r (not ledger-ready)", st)
    return None


def _wait_active_revocation_registry(
    ctx: Context, cred_def_id: str
) -> dict[str, Any] | None:
    """Poll active-registry until revocation is ledger-ready (``active`` or ``finished``)."""
    try:
        attempts = max(1, int((os.environ.get("WEBVH_REV_ACTIVE_WAIT_ATTEMPTS") or "30").strip()))
    except ValueError:
        attempts = 30
    try:
        delay = max(0.1, float((os.environ.get("WEBVH_REV_ACTIVE_WAIT_SEC") or "1").strip()))
    except ValueError:
        delay = 1.0
    last: dict[str, Any] | None = None
    last_state: str | None = None
    last_retryable_status: int | None = None
    ic = ctx.issuer_client()
    for i in range(attempts):
        try:
            r = ic.get_anoncreds_revocation_active_registry(cred_def_id)
        except requests.RequestException as exc:
            LOG.debug("active-registry attempt %s: %s", i + 1, exc)
            time.sleep(delay)
            continue
        if r.status_code == 404:
            LOG.debug("active-registry HTTP 404 (not ready), attempt %s", i + 1)
            time.sleep(delay)
            continue
        if _active_registry_http_retryable(r.status_code):
            last_retryable_status = r.status_code
            LOG.debug(
                "active-registry HTTP %s (retrying), attempt %s  %s",
                r.status_code,
                i + 1,
                r.text[:300],
            )
            time.sleep(delay)
            continue
        if r.status_code != 200:
            LOG.error(
                "GET /anoncreds/revocation/active-registry  HTTP %s  %s",
                r.status_code,
                r.text[:500],
            )
            return None
        try:
            body = r.json()
        except json.JSONDecodeError:
            time.sleep(delay)
            continue
        rec = body.get("result") if isinstance(body, dict) else None
        if not isinstance(rec, dict):
            time.sleep(delay)
            continue
        last = rec
        last_state = rec.get("state")
        if LOG.isEnabledFor(logging.DEBUG):
            LOG.debug("active-registry state=%r attempt %s", last_state, i + 1)
        if last_state in _REV_REG_LEDGER_READY_STATES:
            return rec
        time.sleep(delay)
    if last is not None:
        LOG.error(
            "Revocation registry not ledger-ready (want state in %s, last=%r)",
            sorted(_REV_REG_LEDGER_READY_STATES),
            last_state,
        )
    elif last_retryable_status is not None:
        LOG.error(
            "Revocation registry poll got only retryable HTTP errors from active-registry "
            "(last HTTP %s). Revocation may still be on the ledger; retry later or set "
            "WEBVH_REV_ACTIVE_SOFT_FAIL=1 to pass this phase without API confirmation.",
            last_retryable_status,
        )
    else:
        LOG.error("Revocation registry poll returned no record")
    return None


def phase_publish_schema(ctx: Context) -> bool:
    """POST /anoncreds/schema (AnonCreds) for **WebVH** ``issuerId``; same payload shape as Tenant UI for askar-anoncreds."""
    issuer_id = _anoncreds_issuer_id(ctx)
    if not issuer_id:
        LOG.error(
            "Schema needs issuerId: use the did:webvh from webvh-create (same run), "
            "or set WEBVH_SCHEMA_ISSUER_ID if create did not return a DID yet."
        )
        return False

    name = (os.environ.get("WEBVH_SCHEMA_NAME") or "webvh-e2e-preferences").strip()
    version = (os.environ.get("WEBVH_SCHEMA_VERSION") or "1.0").strip()
    attr_names = parse_schema_attr_names(os.environ.get("WEBVH_SCHEMA_ATTRS"))

    body: dict[str, Any] = {
        "schema": {
            "attrNames": attr_names,
            "issuerId": issuer_id,
            "name": name,
            "version": version,
        },
        "options": {},
    }
    LOG.info(
        "%s\n%s\n%s\n%s",
        headline_request("POST", "/anoncreds/schema", role="issuer"),
        detail_field_line("schema", f"{name} v{version}", emphasis=True),
        detail_field_line("attrs", repr(attr_names)),
        wrap_dim_block("issuer", issuer_id),
    )
    r = ctx.issuer_client().post_anoncreds_schema(body)
    if r.status_code not in (200, 201):
        LOG.error(
            "Schema publish failed  HTTP %s  %s",
            r.status_code,
            r.text[:800],
        )
        return False
    try:
        data = r.json()
    except json.JSONDecodeError:
        LOG.error("Schema response was not JSON")
        return False

    schema_state = (data.get("schema_state") or {}) if isinstance(data, dict) else {}
    state = schema_state.get("state")
    schema_id = schema_state.get("schema_id")
    job_id = data.get("job_id") if isinstance(data, dict) else None

    if state == "finished" and schema_id:
        ctx.anoncreds_schema_id = str(schema_id)
        LOG.info(
            "%s\n%s",
            party_headline("issuer", "Schema on ledger"),
            wrap_dim_block("schema_id", str(schema_id)),
        )
        return True

    LOG.error(
        "Schema incomplete  state=%r schema_id=%r job_id=%r  %s",
        state,
        schema_id,
        job_id,
        (r.text[:500] if r.text else ""),
    )
    return False


def phase_publish_cred_def(ctx: Context) -> bool:
    """POST /anoncreds/credential-definition with revocation (AnonCreds) on the **WebVH** schema."""
    if not ctx.anoncreds_schema_id:
        LOG.error(
            "Cred def needs schema_id from publish-schema-webvh in the same run "
            "(or run phases in order: … publish-schema-webvh publish-cred-def-webvh)."
        )
        return False
    issuer_id = _anoncreds_issuer_id(ctx)
    if not issuer_id:
        LOG.error(
            "Cred def needs issuerId (same did:webvh as schema / webvh-create, "
            "or WEBVH_SCHEMA_ISSUER_ID)."
        )
        return False

    tag = (os.environ.get("WEBVH_CRED_DEF_TAG") or "webvh-e2e").strip()
    raw_rr = (os.environ.get("WEBVH_REVOCATION_REGISTRY_SIZE") or "4").strip()
    try:
        revocation_registry_size = max(1, int(raw_rr))
    except ValueError:
        revocation_registry_size = 4

    body: dict[str, Any] = {
        "credential_definition": {
            "issuerId": issuer_id,
            "schemaId": ctx.anoncreds_schema_id,
            "tag": tag,
        },
        "options": {
            "support_revocation": True,
            "revocation_registry_size": revocation_registry_size,
        },
    }
    LOG.info(
        "%s\n%s\n%s\n%s",
        headline_request("POST", "/anoncreds/credential-definition", role="issuer"),
        detail_field_line("tag", tag, emphasis=True),
        detail_field_line(
            "revoke",
            f"on  (registry size {revocation_registry_size})",
        ),
        wrap_dim_block("schema", ctx.anoncreds_schema_id),
    )
    r = ctx.issuer_client().post_anoncreds_credential_definition(body)
    if r.status_code not in (200, 201):
        LOG.error(
            "Cred def publish failed  HTTP %s  %s",
            r.status_code,
            r.text[:800],
        )
        return False
    try:
        data = r.json()
    except json.JSONDecodeError:
        LOG.error("Cred def response was not JSON")
        return False

    cds = (data.get("credential_definition_state") or {}) if isinstance(data, dict) else {}
    state = cds.get("state")
    cred_def_id = cds.get("credential_definition_id")
    job_id = data.get("job_id") if isinstance(data, dict) else None

    if state == "finished" and cred_def_id:
        cid = str(cred_def_id)
        ctx.anoncreds_cred_def_id = cid
        LOG.info(
            "%s\n%s",
            party_headline("issuer", "Credential definition ready"),
            wrap_dim_block("cred_def_id", cid),
        )
        rev_rec = _wait_active_revocation_registry(ctx, cid)
        if not rev_rec:
            rev_rec = _try_revocation_record_via_cred_def_get(ctx, cid)
            if rev_rec:
                LOG.info(
                    "%s  ·  %s",
                    party_headline("issuer", "Revocation registry (fallback)"),
                    dim("GET /anoncreds/credential-definition — active-registry did not succeed"),
                )
        if not rev_rec:
            if env_flag("WEBVH_REV_ACTIVE_SOFT_FAIL"):
                LOG.warning(
                    "Could not read active revocation registry via tenant API "
                    "(active-registry may return 5xx for did:webvh cred def ids). "
                    "Continuing with WEBVH_REV_ACTIVE_SOFT_FAIL=1 — cred def is still "
                    "finished; confirm revocation on the ledger out of band if needed."
                )
                return True
            return False
        def_id, reg_id = _revocation_ids_from_issuer_record(rev_rec)
        if not def_id and not reg_id:
            LOG.error(
                "Active revocation record missing rev_reg_def.id and revoc_reg_id  %s",
                (json.dumps(rev_rec, default=str)[:800] if rev_rec else ""),
            )
            return False
        ctx.anoncreds_rev_reg_def_id = def_id or reg_id
        ctx.anoncreds_rev_reg_id = reg_id or def_id
        LOG.info(
            "%s\n%s\n%s\n%s",
            party_headline("issuer", "Revocation registry ready"),
            detail_field_line("state", str(rev_rec.get("state") or ""), emphasis=True),
            wrap_dim_block("rev_reg_def", def_id or reg_id or ""),
            wrap_dim_block("rev_reg_entry", reg_id or def_id or ""),
        )
        return True

    LOG.error(
        "Cred def incomplete  state=%r credential_definition_id=%r job_id=%r  %s",
        state,
        cred_def_id,
        job_id,
        (r.text[:500] if r.text else ""),
    )
    return False
