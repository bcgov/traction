import logging
from typing import List
from uuid import UUID

from sqlalchemy import select, func, desc, update
from sqlalchemy.orm import selectinload

from acapy_client.model.indy_pres_spec import IndyPresSpec
from acapy_client.model.indy_requested_creds_requested_attr import (
    IndyRequestedCredsRequestedAttr,
)
from acapy_client.model.indy_requested_creds_requested_pred import (
    IndyRequestedCredsRequestedPred,
)
from acapy_client.model.v10_credential_problem_report_request import (
    V10CredentialProblemReportRequest,
)
from acapy_client.model.v10_presentation_problem_report_request import (
    V10PresentationProblemReportRequest,
)

from api.db.models import Timeline
from api.db.models.v1.holder import HolderCredential, HolderPresentation
from api.db.session import async_session
from api.endpoints.models.credentials import CredentialStateType, CredPrecisForProof
from api.endpoints.models.v1.errors import (
    IdNotMatchError,
    NotFoundError,
    IncorrectStatusError,
)
from api.endpoints.models.v1.holder import (
    HolderCredentialListParameters,
    HolderCredentialItem,
    HolderCredentialContact,
    HolderCredentialAcapy,
    HolderCredentialTimelineItem,
    UpdateHolderCredentialPayload,
    HolderCredentialStatusType,
    AcceptCredentialOfferPayload,
    RejectCredentialOfferPayload,
    HolderPresentationListParameters,
    HolderPresentationItem,
    HolderPresentationContact,
    HolderPresentationTimelineItem,
    UpdateHolderPresentationPayload,
    HolderPresentationStatusType,
    HolderPresentationCredentialListParameters,
    HolderPresentationCredentialItem,
    SendPresentationPayload,
    RejectPresentationRequestPayload,
    HolderPresentationAcapy,
)
from api.endpoints.models.v1.verifier import AcapyPresentProofStateType
from api.services.v1 import acapy_service
from api.services.v1.acapy_service import (
    issue_cred_v10_api,
    credentials_api,
    present_proof_api,
)

logger = logging.getLogger(__name__)


def holder_credential_to_item(
    db_item: HolderCredential, acapy: bool | None = False
) -> HolderCredentialItem:
    """HolderCredential to HolderCredentialItem.

    Transform a HolderCredential Table record to a HolderCredentialItem object.

    Args:
      db_item: The Traction database HolderCredential
      acapy: When True, populate the HolderCredentialItem acapy field.

    Returns: The Traction HolderCredentialItem

    """
    contact = HolderCredentialContact(
        contact_id=db_item.contact.contact_id,
        alias=db_item.contact.alias,
        external_reference_id=db_item.contact.external_reference_id,
    )

    item = HolderCredentialItem(
        **db_item.dict(),
        contact=contact,
    )
    if acapy:
        item.acapy = HolderCredentialAcapy(
            credential_exchange_id=db_item.credential_exchange_id,
            revoc_reg_id=db_item.revoc_reg_id,
            revocation_id=db_item.revocation_id,
        )
        if db_item.credential_exchange_id:
            exch = acapy_service.get_credential_exchange_json(
                db_item.credential_exchange_id
            )
            item.acapy.credential_exchange = exch
        if db_item.credential_id:
            cred = acapy_service.get_credential_json(db_item.credential_id)
            item.acapy.credential = cred
    return item


def holder_presentation_to_item(
    db_item: HolderPresentation, acapy: bool | None = False
) -> HolderPresentationItem:
    """HolderPresentation to HolderPresentationItem.

    Transform a HolderPresentation Table record to a HolderPresentationItem object.

    Args:
      db_item: The Traction database HolderPresentation
      acapy: When True, populate the HolderPresentationItem acapy field.

    Returns: The Traction HolderPresentationItem

    """
    contact = HolderPresentationContact(
        contact_id=db_item.contact.contact_id,
        alias=db_item.contact.alias,
        external_reference_id=db_item.contact.external_reference_id,
    )

    item = HolderPresentationItem(
        **db_item.dict(),
        contact=contact,
    )
    if acapy:
        item.acapy = HolderPresentationAcapy(
            presentation_exchange_id=db_item.presentation_exchange_id,
        )
        if db_item.presentation_exchange_id:
            exch = acapy_service.get_presentation_exchange_json(
                db_item.presentation_exchange_id
            )
            item.acapy.presentation_exchange = exch

    return item


async def list_holder_credentials(
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: HolderCredentialListParameters,
) -> [List[HolderCredentialItem], int]:
    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        HolderCredential.tenant_id == tenant_id,
        HolderCredential.deleted == parameters.deleted,
    ]
    if parameters.status:
        filters.append(HolderCredential.status == parameters.status)
    if parameters.state:
        filters.append(HolderCredential.state == parameters.state)
    if parameters.contact_id:
        filters.append(HolderCredential.contact_id == parameters.contact_id)
    if parameters.schema_id:
        filters.append(HolderCredential.schema_id == parameters.schema_id)
    if parameters.cred_def_id:
        filters.append(HolderCredential.cred_def_id == parameters.cred_def_id)
    if parameters.external_reference_id:
        filters.append(
            HolderCredential.external_reference_id == parameters.external_reference_id
        )

    if parameters.tags:
        _filter_tags = [x.strip() for x in parameters.tags.split(",")]
        filters.append(HolderCredential.tags.comparator.contains(_filter_tags))

    # build out a base query with all filters
    base_q = select(HolderCredential).filter(*filters)

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
        .options(
            selectinload(HolderCredential.contact),
        )
        .order_by(desc(HolderCredential.updated_at))
    )

    async with async_session() as db:
        results_q_recs = await db.execute(results_q)
        db_items = results_q_recs.scalars().all()

    items = []
    for db_item in db_items:
        item = holder_credential_to_item(db_item, parameters.acapy)
        items.append(item)

    return items, total_count


async def get_holder_credential(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_credential_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
) -> HolderCredentialItem:
    async with async_session() as db:
        db_item = await HolderCredential.get_by_id(
            db, tenant_id, holder_credential_id, deleted
        )

    item = holder_credential_to_item(db_item, acapy)

    return item


async def get_holder_credential_timeline(
    holder_credential_id: UUID,
) -> List[HolderCredentialTimelineItem]:
    async with async_session() as db:
        db_items = await Timeline.list_by_item_id(db, holder_credential_id)

    results = []
    for db_item in db_items:
        results.append(HolderCredentialTimelineItem(**db_item.dict()))
    return results


async def update_holder_credential(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_credential_id: UUID,
    payload: UpdateHolderCredentialPayload,
) -> HolderCredentialItem:
    # verify this item exists and is not deleted...
    async with async_session() as db:
        await HolderCredential.get_by_id(db, tenant_id, holder_credential_id, False)

    # payload id must match parameter
    if holder_credential_id != payload.holder_credential_id:
        raise IdNotMatchError(
            code="holder_credential.update.id-not-match",
            title="Holder Credential ID mismatch",
            detail=f"Holder Credential ID in payload <{payload.holder_credential_id}> does not match Holder Credential ID requested <{holder_credential_id}>",  # noqa: E501
        )

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["holder_credential_id"]

    await HolderCredential.update_by_id(holder_credential_id, payload_dict)
    return await get_holder_credential(tenant_id, wallet_id, holder_credential_id, True)


async def delete_holder_credential(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_credential_id: UUID,
    hard: bool | None = False,
):
    if hard:
        await hard_delete_holder_credential(tenant_id, holder_credential_id)
        return None
    else:
        await soft_delete_holder_credential(tenant_id, holder_credential_id)
        return await get_holder_credential(
            tenant_id, wallet_id, holder_credential_id, True, True
        )


async def soft_delete_holder_credential(tenant_id, holder_credential_id):
    q = (
        update(HolderCredential)
        .where(HolderCredential.tenant_id == tenant_id)
        .where(HolderCredential.holder_credential_id == holder_credential_id)
        .values(
            deleted=True,
            status=HolderCredentialStatusType.deleted,
            state=CredentialStateType.abandoned,
        )
    )
    async with async_session() as db:
        await db.execute(q)
        await db.commit()


async def hard_delete_holder_credential(tenant_id: UUID, holder_credential_id: UUID):
    previously_soft_deleted = False
    async with async_session() as db:
        try:
            hc = await HolderCredential.get_by_id(
                db, tenant_id, holder_credential_id, previously_soft_deleted
            )
        except NotFoundError:
            # this may have been soft deleted...
            previously_soft_deleted = True
            hc = await HolderCredential.get_by_id(
                db, tenant_id, holder_credential_id, previously_soft_deleted
            )

    # remove from wallet
    if hc.credential_id:
        cred_response = credentials_api.credential_credential_id_delete(
            credential_id=hc.credential_id
        )
        logger.info(f"delete credential response = {cred_response}")

    async with async_session() as db:
        hc = await HolderCredential.get_by_id(
            db, tenant_id, holder_credential_id, previously_soft_deleted
        )
        await db.delete(hc)
        await db.commit()


async def accept_credential_offer(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_credential_id: UUID,
    payload: AcceptCredentialOfferPayload,
) -> HolderCredentialItem:
    async with async_session() as db:
        hc = await HolderCredential.get_by_id(
            db, tenant_id, holder_credential_id, False
        )

    # payload id must match parameter
    if holder_credential_id != payload.holder_credential_id:
        raise IdNotMatchError(
            code="holder_credential.accept-offer.id-not-match",
            title="Holder Credential ID mismatch",
            detail=f"Holder Credential ID in payload <{payload.holder_credential_id}> does not match Holder Credential ID requested <{holder_credential_id}>",  # noqa: E501
        )

    if hc.status != HolderCredentialStatusType.offer_received:
        raise IncorrectStatusError(
            code="holder_credential.status.not-offer-received",
            title="Holder Credential - Invalid status to accept",
            detail=f"Holder Credential must be have status '{HolderCredentialStatusType.offer_received}' to be accepted. Current status is '{hc.status}'",  # noqa: E501
        )

    cred_response = (
        issue_cred_v10_api.issue_credential_records_cred_ex_id_send_request_post(
            str(hc.credential_exchange_id)
        )
    )
    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["holder_credential_id"]

    payload_dict["state"] = cred_response.state

    await HolderCredential.update_by_id(holder_credential_id, payload_dict)
    return await get_holder_credential(tenant_id, wallet_id, holder_credential_id, True)


async def reject_credential_offer(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_credential_id: UUID,
    payload: RejectCredentialOfferPayload,
):
    async with async_session() as db:
        hc = await HolderCredential.get_by_id(
            db, tenant_id, holder_credential_id, False
        )

    # payload id must match parameter
    if holder_credential_id != payload.holder_credential_id:
        raise IdNotMatchError(
            code="holder_credential.reject-offer.id-not-match",
            title="Holder Credential ID mismatch",
            detail=f"Holder Credential ID in payload <{payload.holder_credential_id}> does not match Holder Credential ID requested <{holder_credential_id}>",  # noqa: E501
        )

    if hc.status != HolderCredentialStatusType.offer_received:
        raise IncorrectStatusError(
            code="holder_credential.status.not-offer-received",
            title="Holder Credential - Invalid status to reject",
            detail=f"Holder Credential must be have status '{HolderCredentialStatusType.offer_received}' to be rejected. Current status is '{hc.status}'",  # noqa: E501
        )

    problem_description = (
        payload.rejection_comment
        if payload.rejection_comment
        else "Credential Offer rejected."
    )
    problem_report = V10CredentialProblemReportRequest(
        description=problem_description,
    )
    data = {"body": problem_report}
    issue_cred_v10_api.issue_credential_records_cred_ex_id_problem_report_post(
        str(hc.credential_exchange_id),
        **data,
    )

    values = {
        "status": HolderCredentialStatusType.rejected,
        "rejection_comment": payload.rejection_comment,
    }
    await HolderCredential.update_by_id(holder_credential_id, values)
    return await get_holder_credential(tenant_id, wallet_id, holder_credential_id, True)


async def list_holder_presentations(
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: HolderPresentationListParameters,
) -> [List[HolderPresentationItem], int]:
    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        HolderPresentation.tenant_id == tenant_id,
        HolderPresentation.deleted == parameters.deleted,
    ]
    if parameters.status:
        filters.append(HolderPresentation.status == parameters.status)
    if parameters.state:
        filters.append(HolderPresentation.state == parameters.state)
    if parameters.contact_id:
        filters.append(HolderPresentation.contact_id == parameters.contact_id)
    if parameters.external_reference_id:
        filters.append(
            HolderPresentation.external_reference_id == parameters.external_reference_id
        )

    if parameters.tags:
        _filter_tags = [x.strip() for x in parameters.tags.split(",")]
        filters.append(HolderPresentation.tags.comparator.contains(_filter_tags))

    # build out a base query with all filters
    base_q = select(HolderPresentation).filter(*filters)

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
        .options(
            selectinload(HolderPresentation.contact),
        )
        .order_by(desc(HolderPresentation.updated_at))
    )

    async with async_session() as db:
        results_q_recs = await db.execute(results_q)
        db_items = results_q_recs.scalars().all()

    items = []
    for db_item in db_items:
        item = holder_presentation_to_item(db_item, parameters.acapy)
        items.append(item)

    return items, total_count


async def get_holder_presentation(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_presentation_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
) -> HolderPresentationItem:
    async with async_session() as db:
        db_item = await HolderPresentation.get_by_id(
            db, tenant_id, holder_presentation_id, deleted
        )

    item = holder_presentation_to_item(db_item, acapy)

    return item


async def get_holder_presentation_timeline(
    holder_presentation_id: UUID,
) -> List[HolderPresentationTimelineItem]:
    async with async_session() as db:
        db_items = await Timeline.list_by_item_id(db, holder_presentation_id)

    results = []
    for db_item in db_items:
        results.append(HolderPresentationTimelineItem(**db_item.dict()))
    return results


async def update_holder_presentation(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_presentation_id: UUID,
    payload: UpdateHolderPresentationPayload,
) -> HolderPresentationItem:
    # verify this item exists and is not deleted...
    async with async_session() as db:
        await HolderPresentation.get_by_id(db, tenant_id, holder_presentation_id, False)

    # payload id must match parameter
    if holder_presentation_id != payload.holder_presentation_id:
        raise IdNotMatchError(
            code="holder_presentation.update.id-not-match",
            title="Holder Presentation ID mismatch",
            detail=f"Holder Presentation ID in payload <{payload.holder_presentation_id}> does not match Holder Presentation ID requested <{holder_presentation_id}>",  # noqa: E501
        )

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["holder_presentation_id"]

    await HolderPresentation.update_by_id(holder_presentation_id, payload_dict)
    return await get_holder_presentation(
        tenant_id, wallet_id, holder_presentation_id, True
    )


async def delete_holder_presentation(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_presentation_id: UUID,
):
    q = (
        update(HolderPresentation)
        .where(HolderPresentation.tenant_id == tenant_id)
        .where(HolderPresentation.holder_presentation_id == holder_presentation_id)
        .values(
            deleted=True,
            status=HolderPresentationStatusType.deleted,
            state=AcapyPresentProofStateType.ABANDONED,
        )
    )
    async with async_session() as db:
        await db.execute(q)
        await db.commit()

    return await get_holder_presentation(
        tenant_id, wallet_id, holder_presentation_id, True, True
    )


async def list_credentials_for_request(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_presentation_id: UUID,
    parameters: HolderPresentationCredentialListParameters,
) -> [List[HolderPresentationCredentialItem], int]:
    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit
    async with async_session() as db:
        try:
            item = await HolderPresentation.get_by_id(
                db, tenant_id, holder_presentation_id, False
            )
        except NotFoundError:
            pass

    if item:
        creds = present_proof_api.present_proof_records_pres_ex_id_credentials_get(
            item.presentation_exchange_id
        )
        all_creds = []
        for cred in creds:
            all_creds.append(
                CredPrecisForProof(
                    cred_info=cred.get("cred_info"),
                    interval=cred.get("interval"),
                    presentation_referents=cred.get("presentation_referents"),
                )
            )
        return all_creds[skip : (skip + limit)], len(all_creds)
    else:
        return [], 0


async def send_presentation(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_presentation_id: UUID,
    payload: SendPresentationPayload,
) -> HolderPresentationItem:
    async with async_session() as db:
        item = await HolderPresentation.get_by_id(
            db, tenant_id, holder_presentation_id, False
        )

    # payload id must match parameter
    if holder_presentation_id != payload.holder_presentation_id:
        raise IdNotMatchError(
            code="holder_presentation.accept-offer.id-not-match",
            title="Holder Presentation ID mismatch",
            detail=f"Holder Presentation ID in payload <{payload.holder_presentation_id}> does not match Holder Presentation ID requested <{holder_presentation_id}>",  # noqa: E501
        )

    if item.status != HolderPresentationStatusType.request_received:
        raise IncorrectStatusError(
            code="holder_presentation.status.not-request-received",
            title="Holder Presentation - Invalid status to accept",
            detail=f"Holder Presentation must be have status '{HolderPresentationStatusType.request_received}' to be accepted. Current status is '{item.status}'",  # noqa: E501
        )

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["holder_presentation_id"]
    # first, update/store the presentation we are going to send
    item = await HolderPresentation.update_by_id(holder_presentation_id, payload_dict)

    # now send the presentation
    pres_response = send_presentation_to_acapy(item)

    # update the state...
    payload_dict["state"] = pres_response.state
    await HolderPresentation.update_by_id(holder_presentation_id, payload_dict)
    return await get_holder_presentation(
        tenant_id, wallet_id, holder_presentation_id, True
    )


async def reject_presentation_request(
    tenant_id: UUID,
    wallet_id: UUID,
    holder_presentation_id: UUID,
    payload: RejectPresentationRequestPayload,
) -> HolderPresentationItem:
    async with async_session() as db:
        hp = await HolderPresentation.get_by_id(
            db, tenant_id, holder_presentation_id, False
        )

    # payload id must match parameter
    if holder_presentation_id != payload.holder_presentation_id:
        raise IdNotMatchError(
            code="holder_presentation_id.reject-offer.id-not-match",
            title="Holder Presentation ID mismatch",
            detail=f"Holder Presentation ID in payload <{payload.holder_presentation_id}> does not match Holder Presentation ID requested <{holder_presentation_id}>",  # noqa: E501
        )

    if hp.status != HolderPresentationStatusType.request_received:
        raise IncorrectStatusError(
            code="holder_presentation.status.not-request-received",
            title="Holder Presentation - Invalid status to reject",
            detail=f"Holder Presentation must be have status '{HolderPresentationStatusType.request_received}' to be rejected. Current status is '{hp.status}'",  # noqa: E501
        )

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["holder_presentation_id"]
    # first, update/store the presentation metadata
    item = await HolderPresentation.update_by_id(holder_presentation_id, payload_dict)

    # send the rejection
    send_rejection_to_acapy(item, payload)

    values = {
        "status": HolderPresentationStatusType.rejected,
    }
    await HolderPresentation.update_by_id(holder_presentation_id, values)
    return await get_holder_presentation(
        tenant_id, wallet_id, holder_presentation_id, True
    )


def send_presentation_to_acapy(item: HolderPresentation):
    # TODO: should this be a task?
    indy_pres = IndyPresSpec(
        requested_attributes={},
        requested_predicates={},
        self_attested_attributes={},
    )
    provided_pres = item.presentation

    for attr in provided_pres["requested_attributes"]:
        value = provided_pres["requested_attributes"][attr]
        indy_pres.requested_attributes[attr] = IndyRequestedCredsRequestedAttr(
            cred_id=value["cred_id"],
            revealed=value.get("revealed") if value.get("revealed") else True,
        )

    for pred in provided_pres["requested_predicates"]:
        value = provided_pres["requested_predicates"][pred]
        indy_pres.requested_predicates[pred] = IndyRequestedCredsRequestedPred(
            cred_id=value["cred_id"],
        )
        if value.get("timestamp"):
            indy_pres.requested_predicates[pred]["timestamp"] = value.get("timestamp")

    for attr in provided_pres["self_attested_attributes"]:
        value = provided_pres["self_attested_attributes"][attr]
        indy_pres.requested_predicates[attr] = value

    data = {"body": indy_pres}
    pres_resp = (
        present_proof_api.present_proof_records_pres_ex_id_send_presentation_post(
            item.presentation_exchange_id, **data
        )
    )
    return pres_resp


def send_rejection_to_acapy(item, payload):
    # TODO: should this be a task?
    problem_description = (
        payload.rejection_comment
        if payload.rejection_comment
        else "Presentation Request rejected."
    )
    problem_report = V10PresentationProblemReportRequest(
        description=problem_description,
    )
    data = {"body": problem_report}
    present_proof_api.present_proof_records_pres_ex_id_problem_report_post(
        item.presentation_exchange_id,
        **data,
    )
