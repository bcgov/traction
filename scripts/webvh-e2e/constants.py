"""
Harness tuning — single place to edit waits, schema, and flags.

Phases import these names directly; keep names stable. ``E2E_INDY_WRITE_LEDGER_ID`` is also read from
the environment in ``context.build_context`` when set.

**Timeouts** default toward a **~1–2 minute** full profile on a healthy sandbox; raise values locally if
a slow endorser or migration causes flaky failures.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# AnonCreds schema / credential definition (must match preview + proof request)
# ---------------------------------------------------------------------------
E2E_SCHEMA_NAME = "WebVHE2EHarness"
E2E_SCHEMA_VERSION = "1.0"
E2E_SCHEMA_ATTR_NAMES: list[str] = ["name", "score"]
E2E_CRED_DEF_TAG = E2E_SCHEMA_NAME
# Indy: random tag suffix per run (``phase_publish_cred_def_indy``) avoids duplicate-tag 400.
E2E_INDY_CRED_DEF_TAG_PREFIX = f"{E2E_SCHEMA_NAME}-indy-e2e"
E2E_REVOCATION_REGISTRY_SIZE = 4
# After cred-def publish/reuse with revocation, poll GET …/active-registry (``setup.py``).
E2E_REV_REG_ACTIVE_POLL_SEC = 2.0
E2E_REV_REG_ACTIVE_TIMEOUT_SEC = 90.0
E2E_REV_REG_WAIT_LOG_INTERVAL_SEC = 10.0
# Transient WebVH pool errors: retry POST cred-def until success (``setup.py``).
E2E_CRED_DEF_POST_RETRY_TIMEOUT_SEC = 90.0

# ---------------------------------------------------------------------------
# Credential offer (attribute names must match ``E2E_SCHEMA_ATTR_NAMES``)
# ---------------------------------------------------------------------------
E2E_CREDENTIAL_PREVIEW_ATTRIBUTES: list[dict[str, str]] = [
    {"name": "name", "value": "WebVH E2E"},
    {"name": "score", "value": "42"},
]

# ---------------------------------------------------------------------------
# DIDComm connection aliases (issuer OOB + holder receive-invitation)
# ---------------------------------------------------------------------------
E2E_HOLDER_CONNECTION_ALIAS = "webvh-e2e-holder"
E2E_INDY_ISSUER_OOB_ALIAS = "webvh-e2e-issuer-indy"
E2E_INDY_HOLDER_CONNECTION_ALIAS = "webvh-e2e-holder-indy"

# ---------------------------------------------------------------------------
# Polling / timeouts (seconds)
# ---------------------------------------------------------------------------

# Issuer wallet upgrade to askar-anoncreds (``setup.py``)
WALLET_UPGRADE_POLL_SEC = 2.0
WALLET_UPGRADE_TIMEOUT_SEC = 90.0

# Smoke: ``GET /tenant/wallet`` during migration (``phases/smoke.py``)
E2E_SMOKE_WALLET_READY_POLL_SEC = 3.0
E2E_SMOKE_WALLET_READY_TIMEOUT_SEC = 90.0
# Post-ready settle (0 = off). Skipped when both wallets already askar-anoncreds.
E2E_SMOKE_WALLET_POST_READY_SETTLE_SEC = 5.0

# DID Exchange (default WebVH path; ``phases/connect.py``)
E2E_CONNECTION_POLL_SEC = 2.0
E2E_CONNECTION_TIMEOUT_SEC = 60.0

# Issue-credential-2.0 (``phases/issue.py``)
E2E_ISSUE_POLL_SEC = 2.0
E2E_ISSUE_TIMEOUT_SEC = 120.0

# Present-proof-2.0 (``phases/verify.py``)
E2E_PROOF_POLL_SEC = 2.0
E2E_PROOF_TIMEOUT_SEC = 90.0
E2E_PROOF_HOLDER_CRED_MATCH_TIMEOUT_SEC = 45.0

# ---------------------------------------------------------------------------
# Revocation (``phases/revoke.py``)
# ---------------------------------------------------------------------------
E2E_REVOKE_PUBLISH = True
E2E_REVOKE_NOTIFY = False
# Indy: wait for ledger ``…/issued/indy_recs`` after publish=True revoke.
E2E_REVOKE_LEDGER_POLL_SEC = 2.0
E2E_REVOKE_LEDGER_TIMEOUT_SEC = 90.0
E2E_REVOKE_LEDGER_LOG_INTERVAL_SEC = 10.0

# ---------------------------------------------------------------------------
# Indy / BCovrin (``phases/indy.py``, ``context.py``)
# ---------------------------------------------------------------------------
E2E_INDY_WRITE_LEDGER_ID = "bcovrin-test"
E2E_INDY_CONNECTION_POLL_SEC = 2.0
E2E_INDY_CONNECTION_TIMEOUT_SEC = 90.0
E2E_INDY_CRED_DEF_PUBLISH_SETTLE_SEC = 0.0
E2E_INDY_TXN_POLL_SEC = 1.0
E2E_INDY_TXN_TIMEOUT_SEC = 120.0
