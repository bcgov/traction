import logging
from typing import List
from uuid import UUID


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db

# https://github.com/hyperledger/aries-rfcs/blob/main/features/0037-present-proof/README.md
# https://github.com/hyperledger/aries-rfcs/blob/main/features/0454-present-proof-v2/README.md
from api.endpoints.models.v1.models import (
    Presentation,
    SendPresentationResponse,
    SendPresentationPayload,
    SendPresentationProposalResponse,
    SendPresentationProposalPayload,
    AbandonPresentationResponse,
    AbandonPresentationPayload, PresentationCredentialList,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[Presentation])
async def list_presentations(db: AsyncSession = Depends(get_db)) -> List[Presentation]:
    raise NotImplementedError


@router.get(
    "/{presentation_id}/matching-credentials",
    status_code=status.HTTP_200_OK,
    response_model=PresentationCredentialList,
)
async def list_matching_credentials_for_presentation(
    presentation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PresentationCredentialList:
    raise NotImplementedError


@router.post(
    "/{presentation_id}/send-presentation",
    status_code=status.HTTP_200_OK,
    response_model=SendPresentationResponse,
)
async def send_presentation_to_verifier(
    presentation_id: UUID,
    payload: SendPresentationPayload,
    db: AsyncSession = Depends(get_db),
) -> SendPresentationResponse:
    raise NotImplementedError


@router.post(
    "/{presentation_id}/send-proposal",
    status_code=status.HTTP_200_OK,
    response_model=SendPresentationProposalResponse,
)
async def send_presentation_proposal_to_verifier(
    presentation_id: UUID,
    payload: SendPresentationProposalPayload,
    db: AsyncSession = Depends(get_db),
) -> SendPresentationProposalResponse:
    raise NotImplementedError


@router.post(
    "/{presentation_id}/abandon-presentation",
    status_code=status.HTTP_200_OK,
    response_model=AbandonPresentationResponse,
)
async def abandon_presentation(
    presentation_id: UUID,
    payload: AbandonPresentationPayload,
    db: AsyncSession = Depends(get_db),
) -> AbandonPresentationResponse:
    raise NotImplementedError
