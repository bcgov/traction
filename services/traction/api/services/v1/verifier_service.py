import logging
from uuid import UUID
from typing import List
from api.endpoints.models.credentials import PresentCredentialProtocolType

from sqlalchemy import select, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.endpoints.models.v1.governance import TemplateStatusType

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


logger = logging.getLogger(__name__)


def v_presentation_request_to_item(
    db_item: PresentationRequestItem,
) -> PresentationRequestItem:
    """IssuerCredential to IssuerCredentialItem.

    Transform a IssuerCredential Table record to a IssuerCredentialItem object.

    Args:
      db_item: The Traction database IssuerCredential
      acapy: When True, populate the IssuerCredentialItem acapy field.

    Returns: The Traction IssuerCredentialItem

    """

    logger.warn(db_item.__dict__)
    item = PresentationRequestItem(
        **db_item.dict(),
    )
    logger.warn(item)
    return item


async def make_presentation_request(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    protocol: PresentCredentialProtocolType,
    payload: CreatePresentationRequestPayload,
) -> PresentationRequestItem:
    logger.warning(payload.proof_request.dict())
    db_item = VerifierPresentationRequest(
        tenant_id=tenant_id,
        contact_id=payload.contact_id,
        status="pending",
        state="pending",
        protocol=protocol,
        role="verifier",
        proof_request=payload.proof_request.dict(),
    )
    db.add(db_item)
    await db.commit()

    return v_presentation_request_to_item(db_item)


async def list_presentation_requests(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
) -> List[PresentationRequestItem]:

    items = await VerifierPresentationRequest.list_by_tenant_id(db, tenant_id)

    return items, len(items)
