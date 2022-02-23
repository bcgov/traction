from typing import Optional
import logging
import uuid

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from api.core.config import settings
from api.core.profile import Profile
from api.endpoints.dependencies.db import get_db
from api.endpoints.models.webhooks import (
    WEBHOOK_EVENT_PREFIX,
    WebhookTopicType,
)

from api.services.webhooks import post_tenant_webhook
from api.endpoints.dependencies.tenant_security import (
    JWTTFetchingMiddleware,
)


logger = logging.getLogger(__name__)

router = APIRouter()

middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    ),
    Middleware(JWTTFetchingMiddleware),
]

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
        middleware=middleware,
    )
    application.include_router(router, prefix="")
    return application


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
    profile = Profile(wallet_id, db)
    event_topic = WEBHOOK_EVENT_PREFIX + topic
    await profile.notify(event_topic, {"topic": topic, "payload": payload})

    # TODO move this to an event handler?
    try:
        await post_tenant_webhook(topic, payload, wallet_id, db)
    except Exception:
        logger.exception("Error posting webhook to tenant LOB app")

    return {}
