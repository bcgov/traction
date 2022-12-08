import logging
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.openapi.models import Response
from starlette import status

from api.core.config import settings
from api.endpoints.models.v1.messages import (
    SendMessagePayload,
    MessageRole,
)
from api.endpoints.routes.v1.tenant.deprecate import sunset_response

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/", status_code=status.HTTP_410_GONE, response_model=Response, deprecated=True
)
async def list_messages(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    contact_id: UUID | None = None,
    role: MessageRole | None = None,
    tags: str | None = None,
    deleted: bool | None = False,
) -> Response:
    return sunset_response


@router.post(
    "/send-message",
    status_code=status.HTTP_410_GONE,
    response_model=Response,
    deprecated=True,
)
async def send_message(
    payload: SendMessagePayload,
) -> Response:
    return sunset_response
