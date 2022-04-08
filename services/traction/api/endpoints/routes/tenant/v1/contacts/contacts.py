import logging

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.endpoints.models.v1.models import (
    CreateInvitationResponse,
    CreateInvitationPayload,
    ReceiveInvitationPayload,
    ReceiveInvitationResponse,
    ContactList,
)

# /contacts
router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=ContactList)
async def list_contacts(
    limit: Optional[int],
    marker: Optional[UUID],
    tags: Optional[str],
    acapy: Optional[bool],
    db: AsyncSession = Depends(get_db),
) -> ContactList:
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
