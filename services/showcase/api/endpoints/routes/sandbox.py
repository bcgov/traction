import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.db.models.sandbox import SandboxReadWithTenants, SandboxCreate
from api.endpoints.dependencies.db import get_db
from api.db.repositories.sandboxes import SandboxesRepository
from api.services.sandbox import create_new_sandbox

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/sandboxes",
    status_code=status.HTTP_201_CREATED,
    response_model=SandboxReadWithTenants,
)
async def create_sandbox(
    payload: SandboxCreate, db: AsyncSession = Depends(get_db)
) -> SandboxReadWithTenants:
    return await create_new_sandbox(payload, db)


@router.get(
    "/sandboxes",
    status_code=status.HTTP_200_OK,
    response_model=List[SandboxReadWithTenants],
)
async def get_sandboxes(
    db: AsyncSession = Depends(get_db),
) -> List[SandboxReadWithTenants]:
    # this should take some query params, sorting and paging params...
    repo = SandboxesRepository(db_session=db)
    items = await repo.find()
    return items
