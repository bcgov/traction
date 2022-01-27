from enum import Enum
from typing import Optional

from fastapi import APIRouter, Header


router = APIRouter()


class WebhookTopicType(str, Enum):
    ping = "ping"
    connections = "connections"
    oob_invitation = "oob-invitation"
    connection_reuse = "connection-reuse"
    connection_reuse_accepted = "connection-reuse-accepted"
    basicmessages = "basicmessages"
    issue_credential = "issue-credential"
    issue_credential_v2_0 = "issue-credential-v2-0"
    issue_credential_v2_0_indy = "issue-credential-v2-0-indy"
    issue_credential_v2_0_ld_proof = "issue-credential-v2-0-ld-proof"
    issuer_cred_rev = "issuer-cred-rev"
    present_proof = "present-proof"
    present_proof_v2_0 = "present-proof-v2-0"
    endorse_transaction = "endorse-transaction"
    revocation_registry = "revocation-registry"
    revocation_notification = "revocation-notification"
    problem_report = "problem-report"


@router.post("/topic/{topic}/", response_model=dict)
async def process_webhook(topic: WebhookTopicType, payload: dict):
    """Called by aca-py agent."""
    print(">>> Called webhook for innkeeper:", topic)


@router.post("/tenant/topic/{topic}/", response_model=dict)
async def process_tenant_webhook(
    topic: str, payload: dict, x_wallet_id: Optional[str] = Header(None)
):
    """Called by aca-py agent."""
    print(">>> Called webhook for tenant:", x_wallet_id, topic)
