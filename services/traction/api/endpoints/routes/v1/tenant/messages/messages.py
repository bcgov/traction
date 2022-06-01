import logging
from uuid import UUID

from fastapi import APIRouter, Request
from starlette import status

from api.core.config import settings
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.v1.messages import (
    MessageListResponse,
    MessageListParameters,
    SendMessageResponse,
    SendMessagePayload,
)

from api.endpoints.routes.v1.link_utils import build_list_links
from api.services.v1 import messages_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=MessageListResponse)
async def list_messages(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    contact_id: UUID | None = None,
    deleted: bool | None = False,
) -> MessageListResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    parameters = MessageListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
        contact_id=contact_id,
        deleted=deleted,
    )
    items, total_count = await messages_service.list_messages(
        tenant_id, wallet_id, parameters
    )

    links = build_list_links(total_count, parameters)

    return MessageListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post(
    "/send-message",
    status_code=status.HTTP_200_OK,
    response_model=SendMessageResponse,
)
async def send_message(
    payload: SendMessagePayload,
) -> SendMessageResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    item = await messages_service.send_message(tenant_id, wallet_id, payload=payload)
    links = []  # TODO
    return SendMessageResponse(item=item, links=links)
