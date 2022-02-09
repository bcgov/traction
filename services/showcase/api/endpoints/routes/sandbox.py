import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.db.models.sandbox import SandboxCreate
from api.db.models.related import SandboxReadPopulated
from api.endpoints.dependencies.db import get_db
from api.db.repositories.sandbox import SandboxRepository
from api.services.sandbox import create_new_sandbox

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/sandboxes",
    status_code=status.HTTP_201_CREATED,
    response_model=SandboxReadPopulated,
)
async def create_sandbox(
    payload: SandboxCreate, db: AsyncSession = Depends(get_db)
) -> SandboxReadPopulated:
    return await create_new_sandbox(payload, db)


@router.get(
    "/sandboxes",
    status_code=status.HTTP_200_OK,
    response_model=List[SandboxReadPopulated],
)
async def get_sandboxes(
    db: AsyncSession = Depends(get_db),
) -> List[SandboxReadPopulated]:
    # this should take some query params, sorting and paging params...
    repo = SandboxRepository(db_session=db)
    items = await repo.find_populated()
    return items
