"""API Services for Traction Contacts and their AcaPy related data.

Contacts Service encapsulates all data services needed for the Contacts API.
Service classes should not have any knowledge or dependence on Http Request, Response
or Sessions; nor should it return API response models directly.

"""
import json
import logging

from typing import List
from uuid import UUID

from sqlalchemy import select, update, desc
from sqlalchemy.sql.functions import func
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.v1.contact import Contact, ContactTimeline
from api.endpoints.models.connections import ConnectionStateType, ConnectionRoleType
from api.endpoints.routes.connections import create_invitation as v0_create_invitation
from api.endpoints.routes.connections import receive_invitation as v0_receive_invitation
from api.endpoints.models.v1.contacts import (
    CreateInvitationPayload,
    ReceiveInvitationPayload,
    ContactListParameters,
    ContactStatusType,
    ContactAcapy,
    ContactItem,
    UpdateContactPayload,
    ContactPing,
    ContactTimelineItem,
)
from api.endpoints.models.v1.errors import (
    AlreadyExistsError,
    IdNotMatchError,
)
from api.services import connections
from api.services.v1 import invitation_parser

logger = logging.getLogger(__name__)


async def create_invitation(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: CreateInvitationPayload,
) -> [ContactItem, str, dict]:
    """Create Invitation.

    Create an invitation and a Contact.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      payload: Invitation and contact data

    Returns:
      item: The Traction Contact
      invitation_url: Invitation on URL format
      invitation: Invitation block

    Raises:
        AlreadyExistsError: if the provided alias already exists in Traction OR AcaPy
    """
    # see if there is an existing connection with this alias (name)
    existing_connection = connections.get_connection_with_alias(payload.alias)
    if existing_connection is not None:
        raise AlreadyExistsError(
            code="contacts.create.invitation.existing.alias",
            title="Create Invitation alias in use",
            detail=f"Error alias {payload.alias} already in use.",
        )
    # This should get removed when v0 is phased out...
    # we need to do this to keep v0 working and kick off that connection workflow
    v0_tenant_invitation = await v0_create_invitation(
        tenant_id=tenant_id,
        wallet_id=wallet_id,
        alias=payload.alias,
        invitation_type=payload.invitation_type,
        db=db,
    )

    # we should be creating our own invitations and connections,
    # but they are done in the v0 code
    # invitation = connections.create_invitation(payload.alias, payload.invitation_type)
    invitation = json.loads(v0_tenant_invitation.connection.invitation)
    invitation_url = v0_tenant_invitation.connection.invitation_url
    connection = connections.get_connection_with_alias(payload.alias)

    # create a new contact record
    db_contact = Contact(
        alias=payload.alias,
        tenant_id=tenant_id,
        status=ContactStatusType.pending,
        state=ConnectionStateType.start,
        role=ConnectionRoleType.inviter,
        connection_id=connection.connection_id,
        connection_alias=connection.alias,
        invitation=invitation,
        connection=connection,
    )
    db.add(db_contact)
    await db.commit()

    item = contact_to_contact_item(db_contact, True)

    return item, invitation_url, invitation


async def receive_invitation(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: ReceiveInvitationPayload,
) -> ContactItem:
    """Receive Invitation.

    Receive an invitation from another Tenant or ARIES agent. An AcaPy
    connection will be created and a Traction Contact.
    The payload can represent many types of invitations: by URL, by
    Public DID, by a full invitation block. The payload alias is
    optional, but must be provided if the invitation's agent label cannot
    be parsed.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      payload: Invitation data

    Returns: The Traction Contact

    Raises:
        AlreadyExistsError: if the provided alias already exists in Traction OR AcaPy
    """

    # if invitation url, then we need to go get the invitation payload...
    if payload.invitation_url:
        check_invitation = await invitation_parser.check_invitation(
            payload.invitation_url
        )
        invitation = check_invitation.invitation
        label = check_invitation.label
    elif payload.invitation:
        invitation = payload.invitation
        label = invitation.get("label")

    if payload.alias:
        label = payload.alias

    # see if there is an existing connection with this label (name)
    existing_connection = connections.get_connection_with_alias(label)
    if existing_connection is not None:
        raise AlreadyExistsError(
            code="contacts.receive.invitation.existing.alias",
            title="Receive Invitation alias in use",
            detail=f"Error alias {label} already in use.",
        )

    # This should get removed when v0 is phased out...
    # we need to do this to keep v0 working and kick off that connection workflow
    await v0_receive_invitation(
        tenant_id=tenant_id,
        wallet_id=wallet_id,
        alias=label,
        payload=invitation,
        their_public_did=payload.their_public_did,
        db=db,
    )

    # connection = connections.receive_invitation(
    #     label,
    #     payload=invitation,
    #     their_public_did=payload.their_public_did,
    # )
    connection = connections.get_connection_with_alias(label)

    # create a new contact record
    db_contact = Contact(
        alias=label,
        tenant_id=tenant_id,
        status=ContactStatusType.pending,
        state=ConnectionStateType.start,
        role=ConnectionRoleType.invitee,
        connection_id=connection.connection_id,
        connection_alias=connection.alias,
        invitation=invitation,
        connection=connection,
        public_did=payload.their_public_did,
    )
    db.add(db_contact)
    await db.commit()

    item = contact_to_contact_item(db_contact, True)

    item.acapy = ContactAcapy(invitation=invitation, connection=connection)
    return item


async def list_contacts(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: ContactListParameters,
) -> [List[ContactItem], int]:
    """List Contacts.

    Return a page of contacts filtered by given parameters.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      parameters: filters for Contacts

    Returns:
      items: The page of contacts
      total_count: Total number of contacts matching criteria
    """

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [Contact.tenant_id == tenant_id, Contact.deleted == parameters.deleted]
    if parameters.status:
        filters.append(Contact.status == parameters.status)
    if parameters.state:
        filters.append(Contact.state == parameters.state)
    if parameters.role:
        filters.append(Contact.role == parameters.role)
    if parameters.external_reference_id:
        filters.append(
            Contact.external_reference_id == parameters.external_reference_id
        )
    if parameters.alias:
        filters.append(Contact.alias.contains(parameters.alias))

    # build out a base query with all filters
    base_q = select(Contact).filter(*filters)

    # get a count of ALL records matching our base query
    count_q = select([func.count()]).select_from(base_q)
    count_q_rec = await db.execute(count_q)
    total_count = count_q_rec.scalar()

    # TODO: should we raise an exception if paging is invalid?
    # ie. is negative, or starts after available records

    # add in our paging and ordering to get the result set
    results_q = base_q.limit(limit).offset(skip).order_by(desc(Contact.created_at))

    results_q_recs = await db.execute(results_q)
    db_contacts = results_q_recs.scalars()

    items = []
    for db_contact in db_contacts:
        item = contact_to_contact_item(db_contact, parameters.acapy)
        items.append(item)

    return items, total_count


async def get_contact(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    contact_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
) -> ContactItem:
    """Get  Contact.

    Find and return a Traction Contact by ID.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      contact_id: Traction ID of Contact
      acapy: When True, populate the Contact acapy field
      deleted: When True, return Contact if marked as deleted

    Returns: The Traction Contact

    Raises:
      NotFoundError: if the contact cannot be found by ID and deleted flag
    """
    db_contact = await Contact.get_by_id(db, tenant_id, contact_id, deleted)

    item = contact_to_contact_item(db_contact, acapy)

    return item


async def update_contact(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    contact_id: UUID,
    payload: UpdateContactPayload,
) -> ContactItem:
    """Update  Contact.

    Update a Traction Contact.
    Note that not all fields can be modified. If they are present in the payload, they
    will be ignored.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      contact_id: Traction ID of Contact
      payload: Contact data fields to update.

    Returns: The Traction Contact

    Raises:
      NotFoundError: if the contact cannot be found by ID and deleted flag
      IdNotMatchError: if the contact id parameter and in payload do not match
    """
    # verify this contact exists and is not deleted...
    await Contact.get_by_id(db, tenant_id, contact_id, False)

    # payload contact id must match parameter
    if contact_id != payload.contact_id:
        raise IdNotMatchError(
            code="contact.update.id-not-match",
            title="Contact ID mismatch",
            detail=f"Contact ID in payload <{payload.contact_id}> does not match Contact ID requested <{contact_id}>",  # noqa: E501
        )

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["contact_id"]

    if not payload.status:
        del payload_dict["status"]

    if not payload.alias:
        del payload_dict["alias"]

    if payload.ping:
        ping_enabled = payload.ping.ping_enabled
        payload_dict["ping_enabled"] = ping_enabled
    del payload_dict["ping"]

    q = (
        update(Contact)
        .where(Contact.tenant_id == tenant_id)
        .where(Contact.contact_id == contact_id)
        .values(payload_dict)
    )
    await db.execute(q)
    await db.commit()

    return await get_contact(db, tenant_id, wallet_id, contact_id)


async def delete_contact(
    db: AsyncSession, tenant_id: UUID, wallet_id: UUID, contact_id: UUID
) -> ContactItem:
    """Delete  Contact.

    Delete a Traction Contact.
    Note that deletes are "soft" in Traction. The Contact will still exist but must be
    explicitly asked for using deleted=True parameters for Get or List.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      contact_id: Traction ID of Contact

    Returns: The Traction Contact

    Raises:
      NotFoundError: if the contact cannot be found by ID and deleted flag
    """
    q = (
        update(Contact)
        .where(Contact.tenant_id == tenant_id)
        .where(Contact.contact_id == contact_id)
        .values(
            deleted=True,
            status=ContactStatusType.deleted,
            state=ConnectionStateType.abandoned,
        )
    )

    await db.execute(q)
    await db.commit()

    return await get_contact(
        db, tenant_id, wallet_id, contact_id, acapy=False, deleted=True
    )


def contact_to_contact_item(
    db_contact: Contact, acapy: bool | None = False
) -> ContactItem:
    """Contact to ContactItem.

    Transform a Contact Table record to a ContactItem object.

    Args:
      db_contact: The Traction database Contact
      acapy: When True, populate the ContactItem acapy field.

    Returns: The Traction ContactItem

    Raises:
      NotFoundError: if the contact cannot be found by ID and deleted flag
    """
    item = ContactItem(**db_contact.dict())
    item.ping = ContactPing(
        ping_enabled=db_contact.ping_enabled,
        last_response_at=db_contact.last_response_at,
    )
    if acapy:
        item.acapy = ContactAcapy(
            invitation=db_contact.invitation, connection=db_contact.connection
        )

    return item


async def get_contact_timeline(
    db: AsyncSession,
    contact_id: UUID,
) -> List[ContactTimelineItem]:
    """Get Contact Timeline items.

    Find and return the Traction Contact Timeline items. Timeline items represent
    history of changes to Status and/or State. They will be sorted in descending order
    of creation (newest first).

    Args:
      db: database session
      contact_id: Traction ID of Contact

    Returns: List of Contact Timeline items
    """
    db_items = await ContactTimeline.list_by_contact_id(db, contact_id)

    results = []
    for db_item in db_items:
        results.append(ContactTimelineItem(**db_item.dict()))
    return results
