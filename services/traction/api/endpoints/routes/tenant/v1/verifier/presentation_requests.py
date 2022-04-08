import logging
from typing import Optional
from uuid import UUID


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db

# https://github.com/hyperledger/aries-rfcs/blob/main/features/0037-present-proof/README.md
# https://github.com/hyperledger/aries-rfcs/blob/main/features/0454-present-proof-v2/README.md
from api.endpoints.models.v1.models import (
    PresentationRequestList,
    SendPresentationRequestResponse,
    SendPresentationRequestPayload,
    AcceptProposalResponse,
    RejectProposalResponse,
    AcceptPresentationResponse,
    RejectPresentationResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=PresentationRequestList)
async def list_presentation_requests(
    limit: Optional[int],
    marker: Optional[UUID],
    contact_id: Optional[UUID],
    tags: Optional[str],
    acapy: Optional[bool],
    db: AsyncSession = Depends(get_db),
) -> PresentationRequestList:
    raise NotImplementedError


@router.post(
    "/send-presentation-request",
    status_code=status.HTTP_200_OK,
    response_model=SendPresentationRequestResponse,
)
async def send_presentation_request_to_holder(
    payload: SendPresentationRequestPayload,
    db: AsyncSession = Depends(get_db),
) -> SendPresentationRequestResponse:
    raise NotImplementedError


@router.post(
    "/{presentation_request_id}/accept-presentation",
    status_code=status.HTTP_200_OK,
    response_model=AcceptPresentationResponse,
)
async def accept_presentation_from_holder(
    presentation_request_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AcceptPresentationResponse:
    raise NotImplementedError


@router.post(
    "/{presentation_request_id}/reject-presentation",
    status_code=status.HTTP_200_OK,
    response_model=RejectPresentationResponse,
)
async def reject_presentation_from_holder(
    presentation_request_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> RejectPresentationResponse:
    raise NotImplementedError


@router.post(
    "/{presentation_request_id}/accept-proposal",
    status_code=status.HTTP_200_OK,
    response_model=AcceptProposalResponse,
)
async def accept_presentation_proposal_from_holder(
    presentation_request_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AcceptProposalResponse:
    raise NotImplementedError


@router.post(
    "/{presentation_request_id}/reject-proposal",
    status_code=status.HTTP_200_OK,
    response_model=RejectProposalResponse,
)
async def reject_presentation_proposal_from_holder(
    presentation_request_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> RejectProposalResponse:
    raise NotImplementedError
