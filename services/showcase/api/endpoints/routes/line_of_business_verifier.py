import logging
from typing import List, Dict
from uuid import UUID
from pydantic import BaseModel

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.db.repositories.line_of_business import LobRepository
from api.db.repositories.job_applicant import ApplicantRepository

from api.services import traction

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/lobs/{lob_id}/applicants/{applicant_id}/request-degree",
    status_code=status.HTTP_200_OK,
)
async def request_degree(
    sandbox_id: UUID,
    lob_id: UUID,
    applicant_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    a_repo = ApplicantRepository(db_session=db)
    lob_repo = LobRepository(db_session=db)

    applicant = await a_repo.get_by_id_in_sandbox(sandbox_id, applicant_id)
    acme = await lob_repo.get_by_id_with_sandbox(sandbox_id, lob_id)
    # going to get faber, so we can use their cred def id
    faber = await lob_repo.get_by_name_with_sandbox(sandbox_id, "Faber")

    proof_req = {
        "requested_attributes": [
            {
                "name": "degree",
                "restrictions": [{"cred_def_id": faber.cred_def_id}],
            },
            {
                "name": "date",
                "restrictions": [{"cred_def_id": faber.cred_def_id}],
            },
        ],
        "requested_predicates": [
            {
                "name": "age",
                "p_type": ">",
                "p_value": 18,
                "restrictions": [{"cred_def_id": faber.cred_def_id}],
            }
        ],
    }

    resp = await traction.tenant_request_credential_presentation(
        acme.wallet_id,
        acme.wallet_key,
        str(applicant.connection_id),
        alias=applicant.alias,
        proof_req=proof_req,
    )

    return resp
