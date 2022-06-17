import logging
from uuid import UUID
from typing import List
from starlette import status

from api.endpoints.models.credentials import PresentCredentialProtocolType

from sqlalchemy import select, desc
from sqlalchemy.sql.functions import func

from api.db.session import async_session
from api.db.models.v1.contact import Contact
from api.endpoints.models.v1.verifier import (
    VerificationRequestItem,
    CreatePresentationRequestPayload,
    VerificationRequestListParameters,
    VerificationRequestStatusType,
    AcapyPresentProofStateType,
)

from api.db.models.v1.verification_request import VerificationRequest


logger = logging.getLogger(__name__)


def verification_request_to_item(
    db_item: VerificationRequest,
) -> VerificationRequestItem:
    """VerificationRequest to VerificationRequestItem.

    Transform a VerificationRequest Table record to a VerificationRequestItem object.

    Args:
      db_item: The Traction database VerificationRequest
      acapy: When True, populate the VerificationRequestItem acapy field.

    Returns: The Traction VerificationRequestItem

    """

    item = VerificationRequestItem(
        **db_item.dict(),
    )
    return item


async def make_verification_request(
    tenant_id: UUID,
    wallet_id: UUID,
    protocol: PresentCredentialProtocolType,
    payload: CreatePresentationRequestPayload,
) -> VerificationRequestItem:

    db_contact = None
    async with async_session() as db:
        if payload.contact_id:
            db_contact = await Contact.get_by_id(db, tenant_id, payload.contact_id)
        elif payload.connection_id:
            db_contact = await Contact.get_by_connection_id(
                db, tenant_id, payload.connection_id
            )

    if not db_contact:
        raise Exception(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            msg="no contact or connection found",
        )
    db_item = VerificationRequest(
        tenant_id=tenant_id,
        contact_id=db_contact.contact_id,
        status=VerificationRequestStatusType.PENDING,
        state=AcapyPresentProofStateType.PENDING,
        protocol=protocol,
        proof_request=payload.proof_request.dict(),
    )

    async with async_session() as db:
        db.add(db_item)
        await db.commit()

    return verification_request_to_item(db_item)


async def list_presentation_requests(
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: VerificationRequestListParameters,
) -> List[VerificationRequestItem]:

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        VerificationRequest.tenant_id == tenant_id,
    ]
    # handle simple filters
    # TODO: move this logic to central location
    for param, v in parameters.dict(exclude_none=True).items():
        logger.warning("filter parameter found: " + param)
        if param not in [
            "url",
            "page_num",
            "page_size",
            "acapy",
            "tenant_id",
            "tags",
        ]:  # special cases
            filters.append(getattr(VerificationRequest, param) == v)

    if parameters.tags:
        _filter_tags = [x.strip() for x in parameters.tags.split(",")]
        filters.append(VerificationRequest.tags.comparator.contains(_filter_tags))
    # build out a base query with all filters
    base_q = select(VerificationRequest).filter(*filters)

    # get a count of ALL records matching our base query
    count_q = select([func.count()]).select_from(base_q)

    async with async_session() as db:

        count_q_rec = await db.execute(count_q)
        total_count = count_q_rec.scalar()

        # TODO: should we raise an exception if paging is invalid?
        # ie. is negative, or starts after available records

        # add in our paging and ordering to get the result set
        results_q = (
            base_q.limit(limit)
            .offset(skip)
            .order_by(desc(VerificationRequest.updated_at))
        )

        results_q_recs = await db.execute(results_q)
        db_verification_requests = results_q_recs.scalars()

    items = []
    for db_verification_request in db_verification_requests:
        item = verification_request_to_item(db_verification_request, parameters.acapy)
        items.append(item)

    return items, total_count
