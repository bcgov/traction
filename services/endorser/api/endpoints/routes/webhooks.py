from enum import Enum
import logging

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN

from api.core.config import settings
import api.acapy_utils as au
from api.endpoints.models.webhooks import WebhookTopicType


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


@router.post("/topic/{topic}/", response_model=dict)
async def process_webhook(
    topic: WebhookTopicType, payload: dict, api_key: APIKey = Depends(get_api_key)
):
    """Called by aca-py agent."""
    logger.warn(f">>> Called webhook for endorser: {topic}")
    if topic == "connections":
        await setup_endorser_connection(payload)
    return {}


async def setup_endorser_connection(payload: dict):
    """Set endorser role on any connections we receive."""
    if payload["state"] == "active" or payload["state"] == "completed":
        params = {"transaction_my_job": "TRANSACTION_ENDORSER"}
        connection_id = payload["connection_id"]
        await au.acapy_POST(f"transactions/{connection_id}/set-endorser-role", params=params)
