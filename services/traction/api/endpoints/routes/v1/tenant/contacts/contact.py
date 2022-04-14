import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{contact_id}", status_code=status.HTTP_200_OK)
async def get_contact(contact_id: UUID, db: AsyncSession = Depends(get_db)):
    raise NotImplementedError
