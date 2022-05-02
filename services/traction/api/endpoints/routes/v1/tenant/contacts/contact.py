import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.v1.contacts import (
    ContactGetResponse,
    UpdateContactResponse,
    UpdateContactPayload,
)
from api.endpoints.routes.v1.link_utils import build_item_links
from api.services.v1 import contacts_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{contact_id}", status_code=status.HTTP_200_OK, response_model=ContactGetResponse
)
async def get_contact(
    request: Request,
    contact_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
    timeline: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> ContactGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await contacts_service.get_contact(
        db,
        tenant_id,
        wallet_id,
        contact_id=contact_id,
        acapy=acapy,
        deleted=deleted,
    )

    links = build_item_links(str(request.url), item)

    timeline_items = []
    if timeline:
        timeline_items = await contacts_service.get_contact_timeline(db, contact_id)

    return ContactGetResponse(item=item, links=links, timeline=timeline_items)


@router.put(
    "/{contact_id}",
    status_code=status.HTTP_200_OK,
    response_model=UpdateContactResponse,
)
async def update_contact(
    request: Request,
    contact_id: UUID,
    payload: UpdateContactPayload,
    db: AsyncSession = Depends(get_db),
) -> UpdateContactResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await contacts_service.update_contact(
        db, tenant_id, wallet_id, contact_id=contact_id, payload=payload
    )

    links = build_item_links(str(request.url), item)

    return UpdateContactResponse(item=item, link=links)


@router.delete(
    "/{contact_id}", status_code=status.HTTP_200_OK, response_model=ContactGetResponse
)
async def delete_contact(
    request: Request,
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ContactGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await contacts_service.delete_contact(
        db, tenant_id, wallet_id, contact_id=contact_id
    )

    links = build_item_links(str(request.url), item)

    return ContactGetResponse(item=item, link=links)
