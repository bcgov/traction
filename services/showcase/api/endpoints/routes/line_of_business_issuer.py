import logging
from typing import List, Dict
from uuid import UUID
from pydantic import BaseModel

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.db.repositories.line_of_business import LobRepository
from api.db.repositories.student import StudentRepository

from api.services import sandbox, traction

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/students/{student_id}/issue-degree",
    status_code=status.HTTP_200_OK,
)
async def issue_degree(
    sandbox_id: UUID,
    lob_id: UUID,
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    s_repo = StudentRepository(db_session=db)
    lob_repo = LobRepository(db_session=db)

    student = await s_repo.get_by_id_in_sandbox(sandbox_id, student_id)
    faber = await lob_repo.get_by_id_with_sandbox(sandbox_id, lob_id)

    attrs = [
        {"name": "student_id", "value": student.student_id},
        {"name": "name", "value": student.name},
        {"name": "date", "value": student.date.date().strftime("%d-%m-%Y")},
        {"name": "degree", "value": student.degree},
        {"name": "age", "value": student.age},
    ]

    resp = await traction.tenant_issue_credential(
        faber.wallet_id,
        faber.wallet_key,
        str(student.connection_id),
        alias="degree",
        cred_def_id=str(faber.cred_def_id),
        attributes=attrs,
    )

    return resp
