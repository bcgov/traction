"""Phase registry and profiles for the WebVH E2E harness."""

from __future__ import annotations

from typing import Any

from .connect import phase_oob_didexchange_indy_didcomm, phase_oob_didexchange_webvh_didcomm
from .smoke import phase_smoke
from .webvh import phase_configure_webvh_plugin, phase_webvh_create
from .issue import phase_issue_indy, phase_issue_webvh
from .revoke import phase_revoke_indy, phase_revoke_webvh
from .setup import (
    phase_publish_cred_def,
    phase_publish_cred_def_indy,
    phase_publish_schema,
    phase_publish_schema_indy,
    phase_upgrade_anoncreds_wallet,
)
from .verify import (
    phase_verify_indy,
    phase_verify_indy_post_revoke,
    phase_verify_webvh,
    phase_verify_webvh_post_revoke,
)
from .indy import (
    phase_indy_connect_endorser,
    phase_indy_register_public_did,
    phase_indy_set_write_ledger,
)

PHASES: dict[str, Any] = {
    "smoke": phase_smoke,
    "upgrade-anoncreds-wallet": phase_upgrade_anoncreds_wallet,
    "configure-webvh-plugin": phase_configure_webvh_plugin,
    "webvh-create": phase_webvh_create,
    "publish-schema-webvh": phase_publish_schema,
    "publish-cred-def-webvh": phase_publish_cred_def,
    "oob-didexchange-webvh-didcomm": phase_oob_didexchange_webvh_didcomm,
    "issue-webvh": phase_issue_webvh,
    "verify-webvh": phase_verify_webvh,
    "revoke-webvh": phase_revoke_webvh,
    "verify-webvh-post-revoke": phase_verify_webvh_post_revoke,
    "oob-didexchange-indy-didcomm": phase_oob_didexchange_indy_didcomm,
    "issue-indy": phase_issue_indy,
    "verify-indy": phase_verify_indy,
    "revoke-indy": phase_revoke_indy,
    "verify-indy-post-revoke": phase_verify_indy_post_revoke,
    "indy-set-write-ledger": phase_indy_set_write_ledger,
    "indy-connect-endorser": phase_indy_connect_endorser,
    "indy-register-public-did": phase_indy_register_public_did,
    "publish-schema-indy": phase_publish_schema_indy,
    "publish-cred-def-indy": phase_publish_cred_def_indy,
}

PROFILE_NEW_ISSUER_WEBVH: tuple[str, ...] = (
    "smoke",
    # Issuer wallet setup (askar-anoncreds); not part of WebVH plugin configuration.
    "upgrade-anoncreds-wallet",
    "configure-webvh-plugin",
    "webvh-create",
    "publish-schema-webvh",
    "publish-cred-def-webvh",
    "oob-didexchange-webvh-didcomm",
    "issue-webvh",
    "verify-webvh",
    "revoke-webvh",
    "verify-webvh-post-revoke",
)

PROFILE_INDY_BCOVRIN_E2E: tuple[str, ...] = (
    "smoke",
    "upgrade-anoncreds-wallet",
    "indy-set-write-ledger",
    "indy-connect-endorser",
    "indy-register-public-did",
    "publish-schema-indy",
    "publish-cred-def-indy",
    "oob-didexchange-indy-didcomm",
    "issue-indy",
    "verify-indy",
    "revoke-indy",
    "verify-indy-post-revoke",
)

PROFILES: dict[str, tuple[str, ...]] = {
    "all": PROFILE_NEW_ISSUER_WEBVH,
    "new-issuer-webvh": PROFILE_NEW_ISSUER_WEBVH,
    "indy-bcovrin-e2e": PROFILE_INDY_BCOVRIN_E2E,
    # Backward-compatible alias (was “setup” before issue/verify/revoke were in-profile).
    "indy-bcovrin-setup": PROFILE_INDY_BCOVRIN_E2E,
}

_PROFILE_PHASE_KEYS = {p for steps in PROFILES.values() for p in steps}
if _PROFILE_PHASE_KEYS != set(PHASES.keys()):
    raise RuntimeError(
        "Every phase must appear in at least one profile and PHASES must define each: "
        f"missing_from_profiles={set(PHASES.keys()) - _PROFILE_PHASE_KEYS} "
        f"undefined_phases={_PROFILE_PHASE_KEYS - set(PHASES.keys())}"
    )
