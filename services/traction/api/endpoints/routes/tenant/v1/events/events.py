import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.endpoints.models.v1.models import (
    TractionEventList,
    BulkUpdateTractionEventPayload,
    BulkDeleteTractionEventPayload,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=TractionEventList)
async def list_traction_events(
    limit: Optional[int],
    marker: Optional[UUID],
    event_type: Optional[str],
    acapy: Optional[bool],
    db: AsyncSession = Depends(get_db),
) -> TractionEventList:
    raise NotImplementedError


@router.put(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=TractionEventList,
)
async def bulk_update_traction_events(
    payload: BulkUpdateTractionEventPayload,
    db: AsyncSession = Depends(get_db),
) -> None:
    raise NotImplementedError


@router.delete(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=TractionEventList,
)
async def bulk_delete_traction_events(
    payload: BulkDeleteTractionEventPayload,
    db: AsyncSession = Depends(get_db),
) -> None:
    raise NotImplementedError
