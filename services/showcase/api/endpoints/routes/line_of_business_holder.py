import logging
from typing import List, Dict
from uuid import UUID
from pydantic import BaseModel

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.db.repositories.line_of_business import LobRepository

from api.services import sandbox, traction

router = APIRouter()
logger = logging.getLogger(__name__)


class CredentialsRead(BaseModel):
    attrs: Dict
    cred_def_id: str
    schema_id: str


class Credential(BaseModel):
    cred_type: str
    cred_protocol: str
    cred_def_id: str
    credential: str
    issue_state: str
    issue_role: str
    created_at: str
    updated_at: str
    id: str


class Workflow(BaseModel):
    workflow_state: str


class CredentialOfferRead(BaseModel):
    credential: Credential
    workflow: Workflow | None


# CREDENTIAL OFFERS


@router.get(
    "/credential-offer",
    status_code=status.HTTP_200_OK,
    response_model=List[CredentialOfferRead],
)
async def get_credential_offer(
    sandbox_id: UUID,
    lob_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CredentialOfferRead:
    # make sure lob is in this sandbox...
    lob_repo = LobRepository(db_session=db)
    lob = await lob_repo.get_by_id_with_sandbox(sandbox_id, lob_id)
    # go get all creds the lob holds
    creds = await traction.tenant_get_credential_offers(lob.wallet_id, lob.wallet_key)
    return creds


@router.post(
    "/credential-offer/{cred_issue_id}/accept",
    status_code=status.HTTP_200_OK,
)
async def accept_credential_offer(
    sandbox_id: UUID,
    lob_id: UUID,
    cred_issue_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    # make sure lob is in this sandbox...
    lob_repo = LobRepository(db_session=db)
    lob = await lob_repo.get_by_id_with_sandbox(sandbox_id, lob_id)
    # go get all creds the lob holds
    creds = await traction.tenant_accept_credential_offer(
        lob.wallet_id, lob.wallet_key, cred_issue_id
    )
    return creds


@router.post(
    "/credential-offer/{cred_issue_id}/reject",
    status_code=status.HTTP_200_OK,
)
async def reject_credential_offer(
    sandbox_id: UUID,
    lob_id: UUID,
    cred_issue_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    # make sure lob is in this sandbox...
    lob_repo = LobRepository(db_session=db)
    lob = await lob_repo.get_by_id_with_sandbox(sandbox_id, lob_id)
    # go get all creds the lob holds
    creds = await traction.tenant_reject_credential_offer(
        lob.wallet_id, lob.wallet_key, cred_issue_id
    )
    return creds


# CREDENTIALS


@router.get(
    "/credentials",
    status_code=status.HTTP_200_OK,
    response_model=List[CredentialsRead],
)
async def get_credentials(
    sandbox_id: UUID,
    lob_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CredentialsRead:
    # make sure lob is in this sandbox...
    lob_repo = LobRepository(db_session=db)
    lob = await lob_repo.get_by_id_with_sandbox(sandbox_id, lob_id)
    # go get all creds the lob holds
    creds = await traction.tenant_get_credentials(lob.wallet_id, lob.wallet_key)
    return creds


# PRESENTATION REQUESTS role=holder
@router.get(
    "/holder/presentation-requests",
    status_code=status.HTTP_200_OK,
)
async def get_presentation_requests(
    sandbox_id: UUID,
    lob_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    lob_repo = LobRepository(db_session=db)
    lob = await lob_repo.get_by_id_with_sandbox(sandbox_id, lob_id)

    creds = await traction.tenant_get_presentation_exchanges(
        lob.wallet_id, lob.wallet_key, role=traction.ARIES_PROTOCOL_ROLES.HOLDER
    )

    pass
