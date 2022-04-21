import logging

from fastapi import APIRouter, Depends
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
from api.services.v1 import contacts_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=ContactListResponse)
async def list_contacts(
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
        page_num=page_num,
        page_size=page_size,
        acapy=acapy,
        alias=alias,
        role=role,
        deleted=deleted,
    )
    return await contacts_service.list_contacts(
        db, tenant_id, wallet_id, parameters=parameters
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
    return await contacts_service.create_invitation(
        db, tenant_id, wallet_id, payload=payload
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
    return await contacts_service.receive_invitation(
        db, tenant_id, wallet_id, payload=payload
    )
