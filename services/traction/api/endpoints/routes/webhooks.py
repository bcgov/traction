from enum import Enum
from typing import Optional
import logging

from fastapi import APIRouter, FastAPI, Header
from starlette.middleware import Middleware
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from api.core.config import settings


logger = logging.getLogger(__name__)

router = APIRouter()


class TokenCheckingMiddleware(BaseHTTPMiddleware):
    """Middleware to check for webhook API token."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # check the webhook api token, if set
        if 0 < len(settings.ACAPY_WEBHOOK_URL_API_KEY):
            auth_header = request.headers.get("x-api-key")
            if not auth_header:
                raise Exception("No WebHook API token supplied")
            if not auth_header == settings.ACAPY_WEBHOOK_URL_API_KEY:
                raise Exception("Invalid WebHook API token supplied")

        response = await call_next(request)
        return response


webhook_middleware = [
    Middleware(TokenCheckingMiddleware),
]


def get_webhookapp() -> FastAPI:
    application = FastAPI(
        title="WebHooks",
        description="Endpoints for Aca-Py WebHooks",
        debug=settings.DEBUG,
        middleware=webhook_middleware,
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
async def process_webhook(topic: WebhookTopicType, payload: dict):
    """Called by aca-py agent."""
    logger.warn(f">>> Called webhook for innkeeper: {topic}")


@router.post("/tenant/topic/{topic}/", response_model=dict)
async def process_tenant_webhook(
    topic: str, payload: dict, x_wallet_id: Optional[str] = Header(None)
):
    """Called by aca-py agent."""
    logger.warn(f">>> Called webhook for tenant: {x_wallet_id} {topic}")
