import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.endpoints.models.v1.models import (
    TractionEvent,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[TractionEvent])
async def list_traction_events(
    db: AsyncSession = Depends(get_db),
) -> List[TractionEvent]:
    raise NotImplementedError


@router.put(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=List[TractionEvent],
)
async def bulk_update_traction_events(
    payload: List[TractionEvent],
    db: AsyncSession = Depends(get_db),
) -> None:
    raise NotImplementedError


@router.delete(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=List[TractionEvent],
)
async def bulk_delete_traction_events(
    payload: List[TractionEvent],
    db: AsyncSession = Depends(get_db),
) -> None:
    raise NotImplementedError
