import logging
from uuid import UUID
from typing import List

from starlette import status, exceptions

from api.db.models.v1.presentation_request_template import PresentationRequestTemplate
from api.endpoints.models.v1.common import ProofRequest
from api.endpoints.models.v1.enumerated import PresentCredentialProtocolType

from sqlalchemy import select, desc
from sqlalchemy.sql.functions import func

from api.db.session import async_session
from api.db.models.v1.contact import Contact
from api.endpoints.models.v1.errors import IdNotMatchError
from api.endpoints.models.v1.governance import TemplateStatusType
from api.endpoints.models.v1.verifier import (
    VerifierPresentationItem,
    CreatePresentationRequestPayload,
    VerifierPresentationListParameters,
    VerifierPresentationStatusType,
    AcapyPresentProofStateType,
    PresentationExchangeAcapy,
    PresentationRequestTemplateListParameters,
    CreatePresentationRequestTemplatePayload,
    PresentationRequestTemplateItem,
    UpdatePresentationRequestTemplatePayload,
    PresentationRequestFromTemplatePayload,
    PresentationRequestTemplateStatusType,
)

from api.db.models.v1.verifier_presentation import VerifierPresentation
from api.api_client_utils import get_api_client
from acapy_client.api.present_proof_v1_0_api import PresentProofV10Api
from api.services.v1 import acapy_service

present_proof_api = PresentProofV10Api(api_client=get_api_client())


logger = logging.getLogger(__name__)


def verifier_presentation_to_item(
    db_item: VerifierPresentation, acapy: bool = False
) -> VerifierPresentationItem:
    """VerifierPresentation to VerifierPresentationItem.

    Transform a VerifierPresentation Table record to a VerifierPresentationItem object.

    Args:
      db_item: The Traction database VerifierPresentation
      acapy: When True, populate the VerifierPresentationItem acapy field.

    Returns: The Traction VerifierPresentationItem

    """
    acapy_item = None  # noqa: F841
    if acapy:
        presentation_exchange = acapy_service.get_presentation_exchange_json(
            db_item.pres_exch_id
        )
        acapy_item = PresentationExchangeAcapy(
            presentation_exchange=presentation_exchange
        )
    item = VerifierPresentationItem(**db_item.dict(), acapy=acapy_item)
    return item


async def make_verifier_presentation(
    tenant_id: UUID,
    wallet_id: UUID,
    protocol: PresentCredentialProtocolType,
    payload: CreatePresentationRequestPayload,
) -> VerifierPresentationItem:

    db_contact = None
    async with async_session() as db:
        if payload.contact_id:
            db_contact = await Contact.get_by_id(db, tenant_id, payload.contact_id)
        elif payload.connection_id:
            db_contact = await Contact.get_by_connection_id(
                db, tenant_id, payload.connection_id
            )

    if not db_contact:
        # TODO refactor this contact GET'ing (and error handling)
        raise exceptions.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="no contact or connection found",
        )
    db_item = VerifierPresentation(
        tenant_id=tenant_id,
        contact_id=db_contact.contact_id,
        status=VerifierPresentationStatusType.PENDING,
        state=AcapyPresentProofStateType.PENDING,
        protocol=protocol,
        proof_request=payload.proof_request.dict(),
        name=payload.name,
        version=payload.version,
        external_reference_id=payload.external_reference_id,
        comment=payload.comment,
        tags=payload.tags,
    )

    async with async_session() as db:
        db.add(db_item)
        await db.commit()

    return verifier_presentation_to_item(db_item)


async def list_presentation_requests(
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: VerifierPresentationListParameters,
) -> List[VerifierPresentationItem]:

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        VerifierPresentation.tenant_id == tenant_id,
    ]
    # handle simple filters
    # TODO: move this logic to central location
    for param, v in parameters.dict(exclude_none=True).items():
        logger.debug("filter parameter found: " + param)
        if param not in [
            "url",
            "page_num",
            "page_size",
            "acapy",
            "tenant_id",
            "tags",
            "comment",
            "name",
        ]:  # special cases
            filters.append(getattr(VerifierPresentation, param) == v)

    if parameters.name:
        filters.append(VerifierPresentation.name.contains(parameters.name))

    if parameters.comment:
        filters.append(VerifierPresentation.comment.contains(parameters.comment))

    if parameters.tags:
        _filter_tags = [x.strip() for x in parameters.tags.split(",")]
        filters.append(VerifierPresentation.tags.comparator.contains(_filter_tags))

    # build out a base query with all filters
    base_q = select(VerifierPresentation).filter(*filters)

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
            .order_by(desc(VerifierPresentation.updated_at))
        )

        results_q_recs = await db.execute(results_q)
        db_verifier_presentations = results_q_recs.scalars().all()

    items = []
    for db_verifier_presentation in db_verifier_presentations:
        item = verifier_presentation_to_item(db_verifier_presentation, parameters.acapy)
        items.append(item)

    return items, total_count


async def get_presentation_request(
    tenant_id: UUID,
    wallet_id: UUID,
    verifier_presentation_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
) -> VerifierPresentationItem:

    """Get Verifier Presentation.

    Find and return a Traction Issuer Credential by ID.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      issuer_credential_id: Traction ID of Issuer Credential
      acapy: When True, populate the Issuer Credential acapy field
      deleted: When True, return Issuer Credential if marked as deleted

    Returns: The Traction Issuer Credential

    Raises:
      NotFoundError: if the item cannot be found by ID and deleted flag
    """
    async with async_session() as db:
        db_item = await VerifierPresentation.get_by_id(
            db, tenant_id, verifier_presentation_id, deleted
        )

    item = verifier_presentation_to_item(db_item, acapy)

    return item


def presentation_request_template_to_item(
    db_item: PresentationRequestTemplate,
) -> PresentationRequestTemplateItem:
    if db_item:
        return PresentationRequestTemplateItem(**db_item.dict())

    return None


async def list_presentation_request_templates(
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: PresentationRequestTemplateListParameters,
) -> List[PresentationRequestTemplateItem]:

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        PresentationRequestTemplate.tenant_id == tenant_id,
    ]
    # handle simple filters
    # TODO: move this logic to central location
    for param, v in parameters.dict(exclude_none=True).items():
        logger.debug("filter parameter found: " + param)
        if param not in [
            "url",
            "page_num",
            "page_size",
            "tags",
            "name",
        ]:  # special cases
            filters.append(getattr(PresentationRequestTemplate, param) == v)

    if parameters.name:
        filters.append(PresentationRequestTemplate.name.contains(parameters.name))

    if parameters.tags:
        _filter_tags = [x.strip() for x in parameters.tags.split(",")]
        filters.append(
            PresentationRequestTemplate.tags.comparator.contains(_filter_tags)
        )

    # build out a base query with all filters
    base_q = select(PresentationRequestTemplate).filter(*filters)

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
            .order_by(desc(PresentationRequestTemplate.updated_at))
        )

        results_q_recs = await db.execute(results_q)
        db_items = results_q_recs.scalars().all()

    items = []
    for db_item in db_items:
        item = presentation_request_template_to_item(db_item)
        items.append(item)

    return items, total_count


async def create_presentation_request_template(
    tenant_id: UUID,
    wallet_id: UUID,
    payload: CreatePresentationRequestTemplatePayload,
) -> PresentationRequestTemplateItem:
    db_item = PresentationRequestTemplate(
        tenant_id=tenant_id,
        status=TemplateStatusType.active,
        state=PresentationRequestTemplateStatusType.none,
        name=payload.name,
        external_reference_id=payload.external_reference_id,
        tags=payload.tags,
        comment=payload.comment,
        presentation_request=payload.presentation_request.dict(),
    )

    async with async_session() as db:
        db.add(db_item)
        await db.commit()

    return await get_presentation_request_template(
        tenant_id, wallet_id, db_item.presentation_request_template_id
    )


async def get_presentation_request_template(
    tenant_id: UUID,
    wallet_id: UUID,
    presentation_request_template_id: UUID,
    deleted: bool | None = False,
) -> PresentationRequestTemplateItem:
    async with async_session() as db:
        db_item = await PresentationRequestTemplate.get_by_id(
            db, tenant_id, presentation_request_template_id, deleted
        )

    item = presentation_request_template_to_item(db_item)

    return item


async def update_presentation_request_template(
    tenant_id: UUID,
    wallet_id: UUID,
    presentation_request_template_id: UUID,
    payload: UpdatePresentationRequestTemplatePayload,
) -> PresentationRequestTemplateItem:
    # verify this item exists and is not deleted...
    async with async_session() as db:
        await PresentationRequestTemplate.get_by_id(
            db, tenant_id, presentation_request_template_id, False
        )

    # payload id must match parameter
    if presentation_request_template_id != payload.presentation_request_template_id:
        raise IdNotMatchError(
            code="presentation_request_template.update.id-not-match",
            title="Presentation Request Template ID mismatch",
            detail=f"Presentation Request Template ID in payload <{payload.presentation_request_template_id}> does not match Presentation Request Template ID requested <{presentation_request_template_id}>",  # noqa: E501
        )

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["presentation_request_template_id"]

    await PresentationRequestTemplate.update_by_id(
        presentation_request_template_id, payload_dict
    )
    return await get_presentation_request_template(
        tenant_id, wallet_id, presentation_request_template_id
    )


async def delete_presentation_request_template(
    tenant_id: UUID,
    wallet_id: UUID,
    presentation_request_template_id: UUID,
):
    values = {"deleted": True, "status": TemplateStatusType.deleted}
    await PresentationRequestTemplate.update_by_id(
        presentation_request_template_id, values
    )

    return await get_presentation_request_template(
        tenant_id, wallet_id, presentation_request_template_id, True
    )


async def make_verifier_presentation_from_template(
    tenant_id: UUID,
    wallet_id: UUID,
    presentation_request_template_id: UUID,
    payload: PresentationRequestFromTemplatePayload,
) -> [VerifierPresentationItem, ProofRequest]:
    # verify this item exists and is not deleted...
    async with async_session() as db:
        db_item = await PresentationRequestTemplate.get_by_id(
            db, tenant_id, presentation_request_template_id, False
        )

    # payload id must match parameter
    if presentation_request_template_id != payload.presentation_request_template_id:
        raise IdNotMatchError(
            code="presentation_request_template.send-request.id-not-match",
            title="Presentation Request Template ID mismatch",
            detail=f"Presentation Request Template ID in payload <{payload.presentation_request_template_id}> does not match Presentation Request Template ID requested <{presentation_request_template_id}>",  # noqa: E501
        )

    # set up the payload for make_verifier_presentation
    if not payload.name:
        payload.name = db_item.name

    proof_request = ProofRequest(**db_item.presentation_request)

    create_payload = CreatePresentationRequestPayload(
        proof_request=proof_request,
        **payload.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True),
    )

    item = await make_verifier_presentation(
        tenant_id, wallet_id, PresentCredentialProtocolType.v10, create_payload
    )

    return item, create_payload.proof_request
