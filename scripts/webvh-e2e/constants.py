"""Fixed tuning for the WebVH E2E harness — edit here instead of using env vars."""

from __future__ import annotations

# AnonCreds schema / cred-def (must match credential preview + proof request)
E2E_SCHEMA_NAME = "WebVHE2EHarness"
E2E_SCHEMA_VERSION = "1.0"
E2E_SCHEMA_ATTR_NAMES: list[str] = ["name", "score"]
E2E_CRED_DEF_TAG = E2E_SCHEMA_NAME
E2E_REVOCATION_REGISTRY_SIZE = 4

# Credential offer preview (attr names must be E2E_SCHEMA_ATTR_NAMES)
E2E_CREDENTIAL_PREVIEW_ATTRIBUTES: list[dict[str, str]] = [
    {"name": "name", "value": "WebVH E2E"},
    {"name": "score", "value": "42"},
]

# DIDComm (holder alias for receive-invitation)
E2E_HOLDER_CONNECTION_ALIAS = "webvh-e2e-holder"

# Polling intervals / timeouts (seconds)
WALLET_UPGRADE_POLL_SEC = 2.0
WALLET_UPGRADE_TIMEOUT_SEC = 120.0
E2E_CONNECTION_POLL_SEC = 2.0
E2E_CONNECTION_TIMEOUT_SEC = 120.0
E2E_ISSUE_POLL_SEC = 2.0
E2E_ISSUE_TIMEOUT_SEC = 300.0
E2E_PROOF_POLL_SEC = 2.0
E2E_PROOF_TIMEOUT_SEC = 180.0

# Revocation API
E2E_REVOKE_PUBLISH = True
E2E_REVOKE_NOTIFY = False
