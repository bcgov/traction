import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db


from api.endpoints.models.v1.models import (
    ProfileConfig,
    UpdateProfileConfigPayload,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/config", status_code=status.HTTP_200_OK, response_model=ProfileConfig)
async def get_profile_config(db: AsyncSession = Depends(get_db)) -> ProfileConfig:
    raise NotImplementedError


@router.put("/config", status_code=status.HTTP_200_OK, response_model=ProfileConfig)
async def update_profile_config(
    payload: UpdateProfileConfigPayload, db: AsyncSession = Depends(get_db)
) -> ProfileConfig:
    raise NotImplementedError
