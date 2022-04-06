import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db


from api.endpoints.models.v1.models import (
    Contact,
    CreateContactPayload,
    UpdateContactPayload,
    Credential,
    Presentation,
    PresentationRequest,
    TractionMessage,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Contact)
async def create_contact(
    payload: CreateContactPayload, db: AsyncSession = Depends(get_db)
) -> Contact:
    raise NotImplementedError


@router.get("/{contact_id}", status_code=status.HTTP_200_OK, response_model=Contact)
async def get_contact(contact_id: UUID, db: AsyncSession = Depends(get_db)) -> Contact:
    raise NotImplementedError


@router.put("/{contact_id}", status_code=status.HTTP_200_OK, response_model=Contact)
async def update_contact(
    contact_id: UUID, payload: UpdateContactPayload, db: AsyncSession = Depends(get_db)
) -> Contact:
    raise NotImplementedError


@router.delete("/{contact_id}", status_code=status.HTTP_200_OK, response_model=Contact)
async def delete_contact(
    contact_id: UUID, db: AsyncSession = Depends(get_db)
) -> Contact:
    raise NotImplementedError


@router.get(
    "/{contact_id}/credentials/",
    status_code=status.HTTP_200_OK,
    response_model=List[Credential],
)
async def list_credentials_exchanged_with_contact(
    contact_id: UUID, db: AsyncSession = Depends(get_db)
) -> List[Credential]:
    raise NotImplementedError


@router.get(
    "/{contact_id}/presentations/",
    status_code=status.HTTP_200_OK,
    response_model=List[Presentation],
)
async def list_presentations_exchanged_with_contact(
    contact_id: UUID, db: AsyncSession = Depends(get_db)
) -> List[Presentation]:
    raise NotImplementedError


@router.get(
    "/{contact_id}/presentation-requests/",
    status_code=status.HTTP_200_OK,
    response_model=List[PresentationRequest],
)
async def list_presentation_requests_exchanged_with_contact(
    contact_id: UUID, db: AsyncSession = Depends(get_db)
) -> List[PresentationRequest]:
    raise NotImplementedError


@router.get(
    "/{contact_id}/messages/",
    status_code=status.HTTP_200_OK,
    response_model=List[TractionMessage],
)
async def list_messages_exchanged_with__contact(
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[TractionMessage]:
    raise NotImplementedError
