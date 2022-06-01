import logging
from uuid import UUID
from typing import List

from sqlalchemy import select, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from acapy_client.api.present_proof_v1_0_api import PresentProofV10Api
from api.endpoints.models.v1.governance import TemplateStatusType
from api.services.v1.governance_service import get_public_did

from acapy_client.api.issue_credential_v1_0_api import IssueCredentialV10Api

from api.endpoints.models.v1.errors import (
    IdNotMatchError,
    IncorrectStatusError,
)

from api.endpoints.models.v1.verifier import (
    PresentationRequestListResponse,
    GetPresentationRequestResponse,
    PresentationRequestItem,
    CreatePresentationRequestPayload,
)


from api.db.models.v1.presentation_requests import VerifierPresentationRequest

from api.api_client_utils import get_api_client

present_proof_api = PresentProofV10Api(api_client=get_api_client())


async def make_presentation_request(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: CreatePresentationRequestPayload,
) -> PresentationRequestItem:
    present_proof_api.present_proof_send_request_post_endpoint()

    db_item = VerifierPresentationRequest()


async def list_presentation_requests(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
) -> List[PresentationRequestItem]:

    items = await VerifierPresentationRequest.list_by_tenant_id(db, tenant_id)

    return items, len(items)
