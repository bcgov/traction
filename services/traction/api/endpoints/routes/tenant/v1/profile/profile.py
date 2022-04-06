import logging


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db


from api.endpoints.models.v1.models import (
    Profile,
    UpdateProfilePayload,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=Profile)
async def get_profile(db: AsyncSession = Depends(get_db)) -> Profile:
    raise NotImplementedError


@router.put("/", status_code=status.HTTP_200_OK, response_model=Profile)
async def update_profile(
    payload: UpdateProfilePayload, db: AsyncSession = Depends(get_db)
) -> Profile:
    raise NotImplementedError
