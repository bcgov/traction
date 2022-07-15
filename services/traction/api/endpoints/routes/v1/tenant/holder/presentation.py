import logging
from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.v1.holder import (
    HolderPresentationGetResponse,
    UpdateHolderPresentationPayload,
    UpdateHolderPresentationResponse,
)

from api.endpoints.routes.v1.link_utils import build_item_links
from api.services.v1 import holder_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{holder_presentation_id}",
    status_code=status.HTTP_200_OK,
    response_model=HolderPresentationGetResponse,
)
async def get_holder_presentation(
    request: Request,
    holder_presentation_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
    timeline: bool | None = False,
) -> HolderPresentationGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.get_holder_presentation(
        tenant_id,
        wallet_id,
        holder_presentation_id=holder_presentation_id,
        acapy=acapy,
        deleted=deleted,
    )

    links = build_item_links(str(request.url), item)

    timeline_items = []
    if timeline:
        timeline_items = await holder_service.get_holder_presentation_timeline(
            holder_presentation_id
        )

    return HolderPresentationGetResponse(
        item=item, links=links, timeline=timeline_items
    )


@router.put(
    "/{holder_presentation_id}",
    status_code=status.HTTP_200_OK,
    response_model=UpdateHolderPresentationResponse,
)
async def update_holder_presentation(
    request: Request,
    holder_presentation_id: UUID,
    payload: UpdateHolderPresentationPayload,
) -> UpdateHolderPresentationResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.update_holder_presentation(
        tenant_id,
        wallet_id,
        holder_presentation_id=holder_presentation_id,
        payload=payload,
    )

    links = build_item_links(str(request.url), item)

    return UpdateHolderPresentationResponse(item=item, link=links)


@router.delete(
    "/{holder_presentation_id}",
    status_code=status.HTTP_200_OK,
    response_model=HolderPresentationGetResponse,
)
async def delete_holder_presentation(
    request: Request,
    holder_presentation_id: UUID,
) -> HolderPresentationGetResponse | JSONResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.delete_holder_presentation(
        tenant_id,
        wallet_id,
        holder_presentation_id=holder_presentation_id,
    )
    links = build_item_links(str(request.url), item)
    return HolderPresentationGetResponse(item=item, link=links)
