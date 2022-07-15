import logging
from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.core.config import settings
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.v1.holder import (
    HolderPresentationGetResponse,
    UpdateHolderPresentationPayload,
    UpdateHolderPresentationResponse,
    HolderPresentationCredentialListResponse,
    HolderPresentationCredentialListParameters,
    SendPresentationPayload,
    RejectPresentationRequestPayload,
)

from api.endpoints.routes.v1.link_utils import build_item_links, build_list_links
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


@router.get(
    "/{holder_presentation_id}/credentials-for-request",
    response_model=HolderPresentationCredentialListResponse,
)
async def get_credentials_for_presentation_request(
    request: Request,
    holder_presentation_id: UUID,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
) -> HolderPresentationCredentialListResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    parameters = HolderPresentationCredentialListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
    )
    items, total_count = await holder_service.list_credentials_for_request(
        tenant_id, wallet_id, holder_presentation_id, parameters
    )

    links = build_list_links(total_count, parameters)

    return HolderPresentationCredentialListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post(
    "/{holder_presentation_id}/send-presentation",
    status_code=status.HTTP_200_OK,
    response_model=HolderPresentationGetResponse,
)
async def send_presentation(
    request: Request,
    holder_presentation_id: UUID,
    payload: SendPresentationPayload,
) -> HolderPresentationGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.send_presentation(
        tenant_id,
        wallet_id,
        holder_presentation_id=holder_presentation_id,
        payload=payload,
    )

    links = build_item_links(str(request.url), item)

    return HolderPresentationGetResponse(item=item, link=links)


@router.post(
    "/{holder_presentation_id}/reject-request",
    status_code=status.HTTP_200_OK,
    response_model=HolderPresentationGetResponse,
)
async def reject_presentation_request(
    request: Request,
    holder_presentation_id: UUID,
    payload: RejectPresentationRequestPayload,
) -> HolderPresentationGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.reject_presentation_request(
        tenant_id,
        wallet_id,
        holder_presentation_id=holder_presentation_id,
        payload=payload,
    )

    links = build_item_links(str(request.url), item)

    return HolderPresentationGetResponse(item=item, link=links)
