import logging
from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from api.endpoints.dependencies.tenant_context import get_from_context
from api.endpoints.models.v1.messages import (
    MessageGetResponse,
    UpdateMessageResponse,
    UpdateMessagePayload,
)
from api.endpoints.routes.v1.link_utils import build_item_links
from api.services.v1 import messages_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=MessageGetResponse,
)
async def get_message(
    request: Request,
    message_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
) -> MessageGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await messages_service.get_message(
        tenant_id,
        wallet_id,
        message_id=message_id,
        acapy=acapy,
        deleted=deleted,
    )

    links = build_item_links(str(request.url), item)

    return MessageGetResponse(item=item, links=links)


@router.put(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=UpdateMessageResponse,
)
async def update_message(
    request: Request,
    message_id: UUID,
    payload: UpdateMessagePayload,
) -> UpdateMessageResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await messages_service.update_message(
        tenant_id,
        wallet_id,
        message_id=message_id,
        payload=payload,
    )

    links = build_item_links(str(request.url), item)

    return UpdateMessageResponse(item=item, link=links)


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=MessageGetResponse,
)
async def delete_message(
    request: Request,
    message_id: UUID,
) -> MessageGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await messages_service.delete_message(
        tenant_id,
        wallet_id,
        message_id=message_id,
    )

    links = build_item_links(str(request.url), item)

    return MessageGetResponse(item=item, link=links)
