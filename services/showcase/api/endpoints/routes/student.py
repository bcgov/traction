import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.db.models.student import StudentRead
from api.endpoints.dependencies.db import get_db
from api.db.repositories.student import StudentRepository

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/students",
    status_code=status.HTTP_200_OK,
    response_model=List[StudentRead],
)
async def get_students(
    sandbox_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[StudentRead]:
    repo = StudentRepository(db_session=db)
    items = await repo.get_in_sandbox(sandbox_id)
    return items


@router.get(
    "/students/{student_id}",
    status_code=status.HTTP_200_OK,
    response_model=StudentRead,
)
async def get_student(
    sandbox_id: UUID,
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> StudentRead:
    repo = StudentRepository(db_session=db)
    item = await repo.get_by_id_in_sandbox(sandbox_id, student_id)
    return item
