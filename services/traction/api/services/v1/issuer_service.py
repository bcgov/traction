import logging
from uuid import UUID
from typing import List

from sqlalchemy import select, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.services.v1.governance_service import get_public_did

from acapy_client.api.issue_credential_v1_0_api import IssueCredentialV10Api
from acapy_client.model.cred_attr_spec import CredAttrSpec
from acapy_client.model.credential_preview import CredentialPreview
from acapy_client.model.v10_credential_free_offer_request import (
    V10CredentialFreeOfferRequest,
)
from api.db.models.v1.contact import Contact
from api.db.models.v1.governance import CredentialTemplate
from api.db.models.v1.issuer import IssuedCredential, IssuedCredentialTimeline

from api.endpoints.models.credentials import CredentialStateType
from api.endpoints.models.v1.errors import NotFoundError, IdNotMatchError

from api.endpoints.models.v1.issuer import (
    IssuedCredentialListParameters,
    IssuedCredentialItem,
    IssuedCredentialContact,
    IssuedCredentialAcapy,
    IssuedCredentialTemplate,
    OfferNewCredentialPayload,
    IssuerCredentialStatusType,
    IssuedCredentialTimelineItem,
    UpdateIssuedCredentialPayload,
)
from api.api_client_utils import get_api_client

issue_cred_v10_api = IssueCredentialV10Api(api_client=get_api_client())


logger = logging.getLogger(__name__)


def issued_credential_to_item(
    db_item: IssuedCredential, acapy: bool | None = False
) -> IssuedCredentialItem:
    """IssuedCredential to IssuedCredentialItem.

    Transform a IssuedCredential Table record to a IssuedCredentialItem object.

    Args:
      db_rec: The Traction database IssuedCredential
      acapy: When True, populate the IssuedCredentialItem acapy field.

    Returns: The Traction IssuedCredentialItem

    """
    credential_template = IssuedCredentialTemplate(
        credential_template_id=db_item.credential_template.credential_template_id,
        name=db_item.credential_template.name,
        cred_def_id=db_item.credential_template.cred_def_id,
    )
    contact = IssuedCredentialContact(
        contact_id=db_item.contact.contact_id,
        alias=db_item.contact.alias,
        external_reference_id=db_item.contact.external_reference_id,
    )

    item = IssuedCredentialItem(
        **db_item.dict(),
        credential_template=credential_template,
        contact=contact,
    )
    if acapy:
        item.acapy = IssuedCredentialAcapy(
            credential_exchange_id=db_item.credential_exchange_id,
            revoc_reg_id=db_item.revoc_reg_id,
            revocation_id=db_item.revocation_id,
        )

    return item


async def send_credential_offer_task(
    db: AsyncSession, tenant_id: UUID, issued_credential_id: UUID
):
    public_did = await get_public_did(db, tenant_id)
    if not public_did:
        return
    try:
        item = await IssuedCredential.get_by_id(db, tenant_id, issued_credential_id)
        cred_preview = credential_preview_conversion(item)

        cred_offer = V10CredentialFreeOfferRequest(
            connection_id=str(item.contact.connection_id),
            cred_def_id=item.credential_template.cred_def_id,
            credential_preview=cred_preview,
            comment=item.comment,
            auto_issue=True,
            auto_remove=False,
        )
        data = {"body": cred_offer}
        cred_response = issue_cred_v10_api.issue_credential_send_offer_post(**data)

        values = {"credential_exchange_id": cred_response.credential_exchange_id}
        if not item.credential_persisted:
            # remove the preview/attributes...
            values["credential_preview"] = {}

        logger.info(values)
        q = (
            update(IssuedCredential)
            .where(IssuedCredential.issued_credential_id == item.issued_credential_id)
            .values(values)
        )
        await db.execute(q)
        await db.commit()

    except NotFoundError:
        logger.error(
            f"No Issued Credential found for id<{issued_credential_id}>. Cannot offer credential."  # noqa: E501
        )


def credential_preview_conversion(item):
    if item.credential_preview and "attributes" in item.credential_preview:
        attrs = item.credential_preview["attributes"]
        cred_attrs = []
        for a in attrs:
            cred_attr = CredAttrSpec(**a)
            cred_attrs.append(cred_attr)
        return CredentialPreview(attributes=cred_attrs)

    return None


async def list_issued_credentials(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: IssuedCredentialListParameters,
) -> [List[IssuedCredentialItem], int]:
    """List Issued Credentials.

    Return a page of issued credentials filtered by given parameters.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      parameters: filters for Items

    Returns:
      items: The page of items
      total_count: Total number of items matching criteria
    """

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        IssuedCredential.tenant_id == tenant_id,
        IssuedCredential.deleted == parameters.deleted,
    ]
    if parameters.status:
        filters.append(IssuedCredential.status == parameters.status)
    if parameters.state:
        filters.append(IssuedCredential.state == parameters.state)
    if parameters.contact_id:
        filters.append(IssuedCredential.contact_id == parameters.contact_id)
    if parameters.cred_def_id:
        filters.append(IssuedCredential.cred_def_id == parameters.cred_def_id)
    if parameters.credential_template_id:
        filters.append(
            IssuedCredential.credential_template_id == parameters.credential_template_id
        )
    if parameters.external_reference_id:
        filters.append(
            IssuedCredential.external_reference_id == parameters.external_reference_id
        )

    # build out a base query with all filters
    base_q = select(IssuedCredential).filter(*filters)

    # get a count of ALL records matching our base query
    count_q = select([func.count()]).select_from(base_q)
    count_q_rec = await db.execute(count_q)
    total_count = count_q_rec.scalar()

    # TODO: should we raise an exception if paging is invalid?
    # ie. is negative, or starts after available records

    # add in our paging and ordering to get the result set
    results_q = (
        base_q.limit(limit)
        .offset(skip)
        .options(
            selectinload(IssuedCredential.contact),
            selectinload(IssuedCredential.credential_template),
        )
        .order_by(desc(IssuedCredential.updated_at))
    )

    results_q_recs = await db.execute(results_q)
    db_items = results_q_recs.scalars()

    items = []
    for db_item in db_items:
        item = issued_credential_to_item(db_item, parameters.acapy)
        items.append(item)

    return items, total_count


async def offer_new_credential(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: OfferNewCredentialPayload,
    credential_persisted: bool | None = False,
) -> IssuedCredentialItem:
    """Offer new Credential.

    Create an Credential and Offer it.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      payload: Credential offer payload
      credential_persisted: when True, store credential data in Traction
    Returns:
      item: The Traction Issued Credential

    Raises:

    """
    # see if we are an issuer...
    await get_public_did(db, tenant_id)

    # need to find the contact/connection
    # need to find the credential template/cred def
    db_contact = None
    db_credential_template = None

    if payload.contact_id:
        db_contact = await Contact.get_by_id(db, tenant_id, payload.contact_id)
    elif payload.connection_id:
        db_contact = await Contact.get_by_connection_id(
            db, tenant_id, payload.connection_id
        )

    if payload.credential_template_id:
        db_credential_template = await CredentialTemplate.get_by_id(
            db, tenant_id, payload.credential_template_id
        )
    elif payload.cred_def_id:
        db_credential_template = await CredentialTemplate.get_by_cred_def_id(
            db, tenant_id, payload.cred_def_id
        )

    # convert list of name/value tuples to an object
    attributes = {}
    credential_preview = {"attributes": []}
    for attr in payload.attributes:
        attributes[attr.name] = attr.value
        credential_preview["attributes"].append(
            {"name": attr.name, "value": attr.value}
        )

    # TODO: verify attributes match the cred def

    # create a new "issued" credential record
    db_item = IssuedCredential(
        tenant_id=tenant_id,
        credential_template_id=db_credential_template.credential_template_id,
        cred_def_id=db_credential_template.cred_def_id,
        contact_id=db_contact.contact_id,
        status=IssuerCredentialStatusType.pending,
        state=CredentialStateType.pending,
        external_reference_id=payload.external_reference_id,
        tags=payload.tags,
        comment=payload.comment,
        credential_persisted=credential_persisted,
        credential_preview=credential_preview,
    )
    db.add(db_item)
    await db.commit()
    db_item = await IssuedCredential.get_by_id(
        db, tenant_id, db_item.issued_credential_id
    )
    item = issued_credential_to_item(db_item, True)

    return item


async def get_issued_credential(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    issued_credential_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
) -> IssuedCredentialItem:
    """Get Issued Credential.

    Find and return a Traction Issued Credential by ID.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      issued_credential_id: Traction ID of Issued Credential
      acapy: When True, populate the Issued Credential acapy field
      deleted: When True, return Issued Credential if marked as deleted

    Returns: The Traction Issued Credential

    Raises:
      NotFoundError: if the item cannot be found by ID and deleted flag
    """
    db_contact = await IssuedCredential.get_by_id(
        db, tenant_id, issued_credential_id, deleted
    )

    item = issued_credential_to_item(db_contact, acapy)

    return item


async def get_issued_credential_timeline(
    db: AsyncSession,
    issued_credential_id: UUID,
) -> List[IssuedCredentialTimelineItem]:
    """Get Issued Credential Timeline items.

    Find and return the Traction Issued Credential Timeline items. Timeline items
    represent history of changes to Status and/or State. They will be sorted in
    descending order of creation (newest first).

    Args:
      db: database session
      issued_credential_id: Traction ID of Issued Credential

    Returns: List of Issued Credential Timeline items
    """
    db_items = await IssuedCredentialTimeline.list_by_issued_credential_id(
        db, issued_credential_id
    )

    results = []
    for db_item in db_items:
        results.append(IssuedCredentialTimeline(**db_item.dict()))
    return results


async def update_issued_credential(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    issued_credential_id: UUID,
    payload: UpdateIssuedCredentialPayload,
) -> IssuedCredentialItem:
    """Update Issued Credential.

    Update a Traction Issued Credential.
    Note that not all fields can be modified. If they are present in the payload, they
    will be ignored.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      issued_credential_id: Traction ID of item
      payload: data fields to update.

    Returns: The Traction IssuedCredentialItem

    Raises:
      NotFoundError: if the item cannot be found by ID and deleted flag
      IdNotMatchError: if the item id parameter and in payload do not match
    """
    # verify this contact exists and is not deleted...
    await IssuedCredential.get_by_id(db, tenant_id, issued_credential_id, False)

    # payload id must match parameter
    if issued_credential_id != payload.issued_credential_id:
        raise IdNotMatchError(
            code="issued_credential.update.id-not-match",
            title="Issued Credential ID mismatch",
            detail=f"Issued Credential ID in payload <{payload.issued_credential_id}> does not match Issued Credential ID requested <{issued_credential_id}>",  # noqa: E501
        )

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["issued_credential_id"]

    if not payload.status:
        del payload_dict["status"]

    q = (
        update(IssuedCredential)
        .where(IssuedCredential.tenant_id == tenant_id)
        .where(Contact.issued_credential_id == issued_credential_id)
        .values(payload_dict)
    )
    await db.execute(q)
    await db.commit()

    return await get_issued_credential(db, tenant_id, wallet_id, issued_credential_id)


async def delete_issued_credential(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    issued_credential_id: UUID,
) -> IssuedCredentialItem:
    """Delete Issued Credential.

    Delete a Traction Issued Credential.
    Note that deletes are "soft" in Traction.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      issued_credential_id: Traction ID of item

    Returns: The Traction IssuedCredentialItem

    Raises:
      NotFoundError: if the item cannot be found by ID and deleted flag
    """
    q = (
        update(IssuedCredential)
        .where(IssuedCredential.tenant_id == tenant_id)
        .where(IssuedCredential.issued_credential_id == issued_credential_id)
        .values(
            deleted=True,
            status=IssuerCredentialStatusType.deleted,
            state=CredentialStateType.abandoned,
        )
    )
    await db.execute(q)
    await db.commit()

    return await get_issued_credential(
        db, tenant_id, wallet_id, issued_credential_id, acapy=False, deleted=True
    )
