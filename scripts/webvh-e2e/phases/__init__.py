"""Phase registry and profiles for the WebVH E2E harness."""

from __future__ import annotations

from typing import Any

from .connect import (
    phase_configure_webvh_plugin,
    phase_oob_didexchange_webvh_didcomm,
    phase_smoke,
    phase_webvh_create,
)
from .issue import phase_issue_indy, phase_issue_webvh
from .verify_revoke import (
    phase_revoke_webvh,
    phase_verify_webvh,
    phase_verify_webvh_post_revoke,
)
from .setup import phase_publish_cred_def, phase_publish_schema
from .common import phase_upgrade_anoncreds_wallet

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
    "issue-indy": phase_issue_indy,
}

PROFILE_NEW_ISSUER_WEBVH: tuple[str, ...] = (
    "smoke",
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

ALL_PHASES_ORDERED: tuple[str, ...] = PROFILE_NEW_ISSUER_WEBVH + ("issue-indy",)

PROFILES: dict[str, tuple[str, ...]] = {
    "all": ALL_PHASES_ORDERED,
    "new-issuer-webvh": PROFILE_NEW_ISSUER_WEBVH,
}

if set(ALL_PHASES_ORDERED) != set(PHASES.keys()):
    raise RuntimeError("ALL_PHASES_ORDERED must match PHASES keys exactly")
