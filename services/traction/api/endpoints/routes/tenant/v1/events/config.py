import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db


from api.endpoints.models.v1.models import (
    TractionEventConfig,
    UpdateTractionEventConfigPayload,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/config", status_code=status.HTTP_200_OK, response_model=TractionEventConfig
)
async def get_traction_event_config(
    db: AsyncSession = Depends(get_db),
) -> TractionEventConfig:
    raise NotImplementedError


@router.put(
    "/config", status_code=status.HTTP_200_OK, response_model=TractionEventConfig
)
async def update_traction_event_config(
    payload: UpdateTractionEventConfigPayload, db: AsyncSession = Depends(get_db)
) -> TractionEventConfig:
    raise NotImplementedError
