import logging
from typing import List
from uuid import UUID


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db

# https://github.com/hyperledger/aries-rfcs/blob/main/features/0036-issue-credential/README.md
# https://github.com/hyperledger/aries-rfcs/blob/main/features/0453-issue-credential-v2/README.md
from api.endpoints.models.v1.models import (
    Credential,
    OfferCredentialResponse,
    OfferCredentialPayload,
    IssueCredentialResponse,
    AbandonCredentialResponse,
    RevokeCredentialResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[Credential])
async def list_issued_credentials(
    db: AsyncSession = Depends(get_db),
) -> List[Credential]:
    raise NotImplementedError


@router.post(
    "/offer-credential",
    status_code=status.HTTP_200_OK,
    response_model=OfferCredentialResponse,
)
async def offer_credential_to_holder(
    payload: OfferCredentialPayload,
    db: AsyncSession = Depends(get_db),
) -> OfferCredentialResponse:
    raise NotImplementedError


@router.post(
    "/{credential_id}/issue-credential",
    status_code=status.HTTP_200_OK,
    response_model=IssueCredentialResponse,
)
async def issue_credential(
    credential_id: UUID, db: AsyncSession = Depends(get_db)
) -> IssueCredentialResponse:
    raise NotImplementedError


@router.post(
    "/{credential_id}/abandon-credential",
    status_code=status.HTTP_200_OK,
    response_model=AbandonCredentialResponse,
)
async def abandon_credential(
    credential_id: UUID, db: AsyncSession = Depends(get_db)
) -> AbandonCredentialResponse:
    raise NotImplementedError


@router.post(
    "/{credential_id}/revoke-credential",
    status_code=status.HTTP_200_OK,
    response_model=RevokeCredentialResponse,
)
async def revoke_credential(
    credential_id: UUID, db: AsyncSession = Depends(get_db)
) -> RevokeCredentialResponse:
    raise NotImplementedError


@router.delete(
    "/{credential_id}",
    status_code=status.HTTP_200_OK,
    response_model=Credential,
)
async def delete_credential(
    credential_id: UUID, db: AsyncSession = Depends(get_db)
) -> Credential:
    raise NotImplementedError
