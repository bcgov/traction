from enum import Enum
from typing import Optional
import logging
import uuid

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN

from api.core.config import settings
from api.core.profile import Profile
from api.endpoints.dependencies.db import get_db
from api.endpoints.models.webhooks import WEBHOOK_EVENT_PREFIX
from api.services.webhooks import post_tenant_webhook


logger = logging.getLogger(__name__)

router = APIRouter()

api_key_header = APIKeyHeader(
    name=settings.ACAPY_WEBHOOK_URL_API_KEY_NAME, auto_error=False
)


async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    if api_key_header == settings.ACAPY_WEBHOOK_URL_API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


def get_webhookapp() -> FastAPI:
    application = FastAPI(
        title="WebHooks",
        description="Endpoints for Aca-Py WebHooks",
        debug=settings.DEBUG,
        middleware=None,
    )
    application.include_router(router, prefix="")
    return application


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
async def process_webhook(
    topic: WebhookTopicType, payload: dict, api_key: APIKey = Depends(get_api_key)
):
    """Called by aca-py agent."""
    logger.warn(f">>> Called webhook for innkeeper: {topic}")
    return {}


@router.post("/tenant/topic/{topic}/", response_model=dict)
async def process_tenant_webhook(
    topic: str,
    payload: dict,
    api_key: APIKey = Depends(get_api_key),
    x_wallet_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Called by aca-py agent."""
    wallet_id = uuid.UUID(str(x_wallet_id))

    # emit an event for any interested listeners
    profile = Profile(wallet_id)
    event_topic = WEBHOOK_EVENT_PREFIX + topic
    logger.warn(f">>> calling notify() with {event_topic}")
    await profile.notify(event_topic, {"topic": topic, "payload": payload})

    # TODO move this to an event handler?
    await post_tenant_webhook(topic, payload, wallet_id, db)

    return {}
