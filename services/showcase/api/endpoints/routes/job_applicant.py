import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.db.models.job_applicant import ApplicantRead
from api.endpoints.dependencies.db import get_db
from api.db.repositories.job_applicant import ApplicantRepository

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/applicants",
    status_code=status.HTTP_200_OK,
    response_model=List[ApplicantRead],
)
async def get_students(
    sandbox_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[ApplicantRead]:
    repo = ApplicantRepository(db_session=db)
    items = await repo.get_in_sandbox(sandbox_id)
    return items


@router.get(
    "/applicants/{applicant_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApplicantRead,
)
async def get_student(
    sandbox_id: UUID,
    applicant_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ApplicantRead:
    repo = ApplicantRepository(db_session=db)
    item = await repo.get_by_id_in_sandbox(sandbox_id, applicant_id)
    return item
