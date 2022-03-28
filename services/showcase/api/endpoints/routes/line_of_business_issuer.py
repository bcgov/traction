import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.db.repositories.line_of_business import LobRepository
from api.db.repositories.student import StudentRepository

from api.services import traction

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
    # we will need some info for revoking this (rev_reg_id, cred_rev_id)
    logger.info("issue credential response")
    logger.info(resp)
    return resp


@router.post(
    "/students/{student_id}/revoke-degree",
    status_code=status.HTTP_200_OK,
)
async def revoke_degree(
    sandbox_id: UUID,
    lob_id: UUID,
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    s_repo = StudentRepository(db_session=db)
    lob_repo = LobRepository(db_session=db)

    student = await s_repo.get_by_id_in_sandbox(sandbox_id, student_id)
    issuer = await lob_repo.get_by_id_with_sandbox(sandbox_id, lob_id)

    issued_credentials = await traction.tenant_get_issued_credentials(
        issuer.wallet_id, issuer.wallet_key
    )
    # find the credential for this student's connection id
    # and the issuer's cred def id.
    cred = next(
        (
            x
            for x in issued_credentials
            if str(x["credential"]["connection_id"]) == str(student.connection_id)
            and str(x["credential"]["cred_def_id"]) == str(issuer.cred_def_id)
        ),
        None,
    )
    if cred:
        await traction.tenant_revoke_credential(
            issuer.wallet_id,
            issuer.wallet_key,
            cred["credential"]["rev_reg_id"],
            cred["credential"]["cred_rev_id"],
            f"Revoked by {issuer.name}.",
        )

    return


@router.get(
    "/issued-credentials",
    status_code=status.HTTP_200_OK,
)
async def get_issued_credentials(
    sandbox_id: UUID,
    lob_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    lob_repo = LobRepository(db_session=db)
    lob = await lob_repo.get_by_id_with_sandbox(sandbox_id, lob_id)

    # call traction to see what credentials we've issued.
    resp = await traction.tenant_get_issued_credentials(
        lob.wallet_id,
        lob.wallet_key,
    )

    return resp
