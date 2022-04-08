import logging
from typing import Optional
from uuid import UUID


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db

# https://github.com/hyperledger/aries-rfcs/blob/main/features/0036-issue-credential/README.md
# https://github.com/hyperledger/aries-rfcs/blob/main/features/0453-issue-credential-v2/README.md
from api.endpoints.models.v1.models import (
    Credential,
    CredentialList,
    AcceptCredentialResponse,
    RejectCredentialResponse,
    ProposeCredentialResponse,
    ProposeCredentialPayload,
    RequestCredentialResponse,
    RequestCredentialPayload,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=CredentialList)
async def list_held_credentials(
    limit: Optional[int],
    marker: Optional[UUID],
    contact_id: Optional[UUID],
    tags: Optional[str],
    acapy: Optional[bool],
    db: AsyncSession = Depends(get_db),
) -> CredentialList:
    raise NotImplementedError


@router.post(
    "/propose-credential",
    status_code=status.HTTP_200_OK,
    response_model=ProposeCredentialResponse,
)
async def propose_credential_to_issuer(
    payload: ProposeCredentialPayload,
    db: AsyncSession = Depends(get_db),
) -> ProposeCredentialResponse:
    raise NotImplementedError


@router.post(
    "/request-credential",
    status_code=status.HTTP_200_OK,
    response_model=RequestCredentialResponse,
)
async def request_credential_from_issuer(
    payload: RequestCredentialPayload,
    db: AsyncSession = Depends(get_db),
) -> RequestCredentialResponse:
    raise NotImplementedError


@router.post(
    "/{credential_id}/accept-credential",
    status_code=status.HTTP_200_OK,
    response_model=AcceptCredentialResponse,
)
async def accept_offered_credential(
    credential_id: UUID, db: AsyncSession = Depends(get_db)
) -> AcceptCredentialResponse:
    raise NotImplementedError


@router.post(
    "/{credential_id}/reject-credential",
    status_code=status.HTTP_200_OK,
    response_model=RejectCredentialResponse,
)
async def reject_offered_credential(
    credential_id: UUID, db: AsyncSession = Depends(get_db)
) -> RejectCredentialResponse:
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
