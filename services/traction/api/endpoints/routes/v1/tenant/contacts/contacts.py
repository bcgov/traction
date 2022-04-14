import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context

from api.endpoints.models.v1.contacts import (
    ContactListResponse,
    CreateInvitationResponse,
    CreateInvitationPayload,
    ReceiveInvitationPayload,
    ReceiveInvitationResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=ContactListResponse)
async def list_contacts(
    skip: int = 0,
    limit: int | None = None,
    acapy: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> ContactListResponse:
    raise NotImplementedError


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
    logger.debug(f"tenant id = {tenant_id}, wallet id = {wallet_id}")
    raise NotImplementedError


@router.post(
    "/receive-invitation",
    status_code=status.HTTP_200_OK,
    response_model=ReceiveInvitationResponse,
)
async def contact_receive_invitation(
    payload: ReceiveInvitationPayload,
    db: AsyncSession = Depends(get_db),
) -> ReceiveInvitationResponse:
    raise NotImplementedError
