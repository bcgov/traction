import logging
from typing import List
from uuid import UUID


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db

from api.endpoints.models.v1.models import (
    TractionMessage,
    SendTractionMessageResponse,
    SendTractionMessagePayload,
    UpdateTractionMessagePayload,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[TractionMessage])
async def list_messages(
    db: AsyncSession = Depends(get_db),
) -> List[TractionMessage]:
    raise NotImplementedError


@router.put(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=List[TractionMessage],
)
async def bulk_update_messages(
    payload: List[TractionMessage],
    db: AsyncSession = Depends(get_db),
) -> None:
    raise NotImplementedError


@router.delete(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=List[TractionMessage],
)
async def bulk_delete_messages(
    payload: List[TractionMessage],
    db: AsyncSession = Depends(get_db),
) -> None:
    raise NotImplementedError


@router.post(
    "/send-message",
    status_code=status.HTTP_200_OK,
    response_model=SendTractionMessageResponse,
)
async def send_message(
    payload: SendTractionMessagePayload,
    db: AsyncSession = Depends(get_db),
) -> SendTractionMessageResponse:
    raise NotImplementedError


@router.get(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=TractionMessage,
)
async def get_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TractionMessage:
    raise NotImplementedError


@router.put(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=TractionMessage,
)
async def update_message(
    message_id: UUID,
    payload: UpdateTractionMessagePayload,
    db: AsyncSession = Depends(get_db),
) -> TractionMessage:
    raise NotImplementedError


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=TractionMessage,
)
async def delete_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TractionMessage:
    raise NotImplementedError
