import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.db.models.sandbox import SandboxCreate
from api.db.models.related import SandboxReadPopulated, OutOfBandReadPopulated
from api.db.repositories.out_of_band import OutOfBandRepository
from api.endpoints.dependencies.db import get_db
from api.db.repositories.sandbox import SandboxRepository
from api.services.sandbox import create_new_sandbox

from api.endpoints.routes.student import router as students_router
from api.endpoints.routes.job_applicant import router as applicants_router
from api.endpoints.routes.line_of_business import router as lobs_router
from api.endpoints.routes.line_of_business_issuer import router as lobs_issuer_router
from api.endpoints.routes.line_of_business_holder import router as lobs_holder_router
from api.endpoints.routes.line_of_business_verifier import (
    router as lobs_verifier_router,
)

router = APIRouter()
logger = logging.getLogger(__name__)

router.include_router(
    students_router, tags=["students"], prefix="/sandboxes/{sandbox_id}"
)
router.include_router(
    applicants_router, tags=["applicants"], prefix="/sandboxes/{sandbox_id}"
)
router.include_router(
    lobs_router, tags=["line_of_business"], prefix="/sandboxes/{sandbox_id}"
)
router.include_router(
    lobs_issuer_router,
    tags=["line_of_business/issuer"],
    prefix="/sandboxes/{sandbox_id}/lobs/{lob_id}",
)
router.include_router(
    lobs_holder_router,
    tags=["line_of_business/holder"],
    prefix="/sandboxes/{sandbox_id}/lobs/{lob_id}",
)
router.include_router(
    lobs_verifier_router,
    tags=["line_of_business/verifier"],
    prefix="/sandboxes/{sandbox_id}/lobs/{lob_id}",
)


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


@router.get(
    "/sandboxes/{sandbox_id}",
    status_code=status.HTTP_200_OK,
    response_model=SandboxReadPopulated,
)
async def get_sandbox(
    sandbox_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SandboxReadPopulated:
    repo = SandboxRepository(db_session=db)
    item = await repo.get_by_id_populated(sandbox_id)
    return item


@router.get(
    "/sandboxes/{sandbox_id}/out-of-band-msgs",
    status_code=status.HTTP_200_OK,
    response_model=List[OutOfBandReadPopulated],
)
async def get_out_of_band_messages(
    sandbox_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> OutOfBandReadPopulated:
    repo = OutOfBandRepository(db_session=db)
    items = await repo.get_in_sandbox(sandbox_id)
    return items
