import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.core.config import settings
from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.connections import ConnectionRoleType

from api.endpoints.models.v1.contacts import (
    ContactListResponse,
    CreateInvitationResponse,
    CreateInvitationPayload,
    ReceiveInvitationPayload,
    ReceiveInvitationResponse,
    ContactListParameters,
)
from api.endpoints.routes.v1.link_utils import build_list_links
from api.services.v1 import contacts_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=ContactListResponse)
async def list_contacts(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    acapy: bool | None = False,
    alias: str | None = None,
    role: ConnectionRoleType | None = None,
    deleted: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> ContactListResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    parameters = ContactListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
        acapy=acapy,
        alias=alias,
        role=role,
        deleted=deleted,
    )
    items, total_count = await contacts_service.list_contacts(
        db, tenant_id, wallet_id, parameters
    )

    links = build_list_links(total_count, parameters)

    return ContactListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post(
    "/create-invitation",
    status_code=status.HTTP_200_OK,
    response_model=CreateInvitationResponse,
)
async def contact_create_invitation(
    payload: CreateInvitationPayload,
    db: AsyncSession = Depends(get_db),
) -> CreateInvitationResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    item, invitation_url, invitation = await contacts_service.create_invitation(
        db, tenant_id, wallet_id, payload=payload
    )
    links = []  # TODO
    return CreateInvitationResponse(
        item=item, invitation=invitation, invitation_url=invitation_url, links=links
    )


@router.post(
    "/receive-invitation",
    status_code=status.HTTP_200_OK,
    response_model=ReceiveInvitationResponse,
)
async def contact_receive_invitation(
    payload: ReceiveInvitationPayload,
    db: AsyncSession = Depends(get_db),
) -> ReceiveInvitationResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    item = await contacts_service.receive_invitation(
        db, tenant_id, wallet_id, payload=payload
    )
    links = []  # TODO
    return ReceiveInvitationResponse(item=item, links=links)
