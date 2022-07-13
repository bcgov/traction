import logging
from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.v1.holder import (
    HolderCredentialGetResponse,
    RejectCredentialOfferPayload,
    AcceptCredentialOfferPayload,
    UpdateHolderCredentialResponse,
    UpdateHolderCredentialPayload,
)

from api.endpoints.routes.v1.link_utils import build_item_links
from api.services.v1 import holder_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{holder_credential_id}",
    status_code=status.HTTP_200_OK,
    response_model=HolderCredentialGetResponse,
)
async def get_holder_credential(
    request: Request,
    holder_credential_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
    timeline: bool | None = False,
) -> HolderCredentialGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.get_holder_credential(
        tenant_id,
        wallet_id,
        holder_credential_id=holder_credential_id,
        acapy=acapy,
        deleted=deleted,
    )

    links = build_item_links(str(request.url), item)

    timeline_items = []
    if timeline:
        timeline_items = await holder_service.get_holder_credential_timeline(
            holder_credential_id
        )

    return HolderCredentialGetResponse(item=item, links=links, timeline=timeline_items)


@router.put(
    "/{holder_credential_id}",
    status_code=status.HTTP_200_OK,
    response_model=UpdateHolderCredentialResponse,
)
async def update_holder_credential(
    request: Request,
    holder_credential_id: UUID,
    payload: UpdateHolderCredentialPayload,
) -> UpdateHolderCredentialResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.update_holder_credential(
        tenant_id,
        wallet_id,
        holder_credential_id=holder_credential_id,
        payload=payload,
    )

    links = build_item_links(str(request.url), item)

    return UpdateHolderCredentialResponse(item=item, link=links)


@router.delete(
    "/{holder_credential_id}",
    status_code=status.HTTP_200_OK,
    response_model=HolderCredentialGetResponse,
)
async def delete_holder_credential(
    request: Request,
    holder_credential_id: UUID,
    hard: bool | None = False,
) -> HolderCredentialGetResponse | JSONResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.delete_holder_credential(
        tenant_id,
        wallet_id,
        holder_credential_id=holder_credential_id,
        hard=hard,
    )
    if item:
        links = build_item_links(str(request.url), item)
        return HolderCredentialGetResponse(item=item, link=links)
    else:
        return JSONResponse(content={"item": None, "links": []})


@router.post(
    "/{holder_credential_id}/accept-offer",
    status_code=status.HTTP_200_OK,
    response_model=HolderCredentialGetResponse,
)
async def accept_credential_offer(
    request: Request,
    holder_credential_id: UUID,
    payload: AcceptCredentialOfferPayload,
) -> HolderCredentialGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.accept_credential_offer(
        tenant_id,
        wallet_id,
        holder_credential_id=holder_credential_id,
        payload=payload,
    )

    links = build_item_links(str(request.url), item)

    return HolderCredentialGetResponse(item=item, link=links)


@router.post(
    "/{holder_credential_id}/reject-offer",
    status_code=status.HTTP_200_OK,
    response_model=HolderCredentialGetResponse,
)
async def reject_credential_offer(
    request: Request,
    holder_credential_id: UUID,
    payload: RejectCredentialOfferPayload,
) -> HolderCredentialGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.reject_credential_offer(
        tenant_id,
        wallet_id,
        holder_credential_id=holder_credential_id,
        payload=payload,
    )

    links = build_item_links(str(request.url), item)

    return HolderCredentialGetResponse(item=item, link=links)
