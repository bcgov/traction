import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db


from api.endpoints.models.v1.models import (
    TractionEvent,
    UpdateTractionEventPayload,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{traction_event_id}", status_code=status.HTTP_200_OK, response_model=TractionEvent
)
async def get_traction_event(
    traction_event_id: UUID, db: AsyncSession = Depends(get_db)
) -> TractionEvent:
    raise NotImplementedError


@router.put(
    "/{traction_event_id}", status_code=status.HTTP_200_OK, response_model=TractionEvent
)
async def update_traction_event(
    traction_event_id: UUID,
    payload: UpdateTractionEventPayload,
    db: AsyncSession = Depends(get_db),
) -> TractionEvent:
    raise NotImplementedError


@router.delete(
    "/{traction_event_id}", status_code=status.HTTP_200_OK, response_model=TractionEvent
)
async def delete_traction_event(
    traction_event_id: UUID, db: AsyncSession = Depends(get_db)
) -> TractionEvent:
    raise NotImplementedError
