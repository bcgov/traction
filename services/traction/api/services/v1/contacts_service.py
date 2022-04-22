import json
import logging

from typing import List
from uuid import UUID

from sqlalchemy import select, update, desc
from sqlalchemy.sql.functions import func
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.v1.contact import Contact
from api.endpoints.models.connections import ConnectionStateType, ConnectionRoleType
from api.endpoints.models.v1.base import Link, build_list_links
from api.endpoints.routes.connections import create_invitation as v0_create_invitation
from api.endpoints.routes.connections import receive_invitation as v0_receive_invitation
from api.endpoints.models.v1.contacts import (
    CreateInvitationPayload,
    CreateInvitationResponse,
    ReceiveInvitationPayload,
    ReceiveInvitationResponse,
    ContactListParameters,
    ContactListResponse,
    ContactStatusType,
    ContactAcapy,
    ContactItem,
    ContactGetResponse,
)
from api.endpoints.models.v1.errors import (
    AlreadyExistsError,
    NotFoundError,
)
from api.services import connections
from api.services.v1 import invitation_parser

logger = logging.getLogger(__name__)


async def create_invitation(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: CreateInvitationPayload,
) -> CreateInvitationResponse:

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

    item = ContactItem(**db_contact.dict())
    item.acapy = ContactAcapy(invitation=invitation, connection=connection)
    return CreateInvitationResponse(
        item=item,
        invitation=invitation,
        invitation_url=invitation_url,
    )


async def receive_invitation(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: ReceiveInvitationPayload,
) -> ReceiveInvitationResponse:

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

    item = ContactItem(**db_contact.dict())

    item.acapy = ContactAcapy(invitation=invitation, connection=connection)
    return ReceiveInvitationResponse(item=item)


async def list_contacts(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: ContactListParameters,
) -> ContactListResponse:

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

    # add in our paging and ordering to get the result set
    results_q = base_q.limit(limit).offset(skip).order_by(desc(Contact.created_at))

    results_q_recs = await db.execute(results_q)
    db_contacts = results_q_recs.scalars()

    items = []
    for db_contact in db_contacts:
        item = contact_to_contact_item(db_contact, parameters.acapy)
        items.append(item)

    links = contacts_list_links(total_count, parameters)

    return ContactListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


async def get_contact(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    contact_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
) -> ContactGetResponse:
    q = (
        select(Contact)
        .where(Contact.tenant_id == tenant_id)
        .where(Contact.contact_id == contact_id)
        .where(Contact.deleted == deleted)
    )
    q_result = await db.execute(q)
    db_contact = q_result.scalar_one_or_none()

    if not db_contact:
        raise NotFoundError(
            code="contact.id_not_found",
            title="Contact does not exist",
            detail=f"Contact does not exist for id<{contact_id}>",
        )

    item = contact_to_contact_item(db_contact, acapy)

    return ContactGetResponse(item=item)


async def delete_contact(
    db: AsyncSession, tenant_id: UUID, wallet_id: UUID, contact_id: UUID
) -> ContactGetResponse:
    q = (
        update(Contact)
        .where(Contact.tenant_id == tenant_id)
        .where(Contact.contact_id == contact_id)
        .values(deleted=True, status=ContactStatusType.deleted)
    )
    await db.execute(q)
    await db.commit()

    return await get_contact(
        db, tenant_id, wallet_id, contact_id, acapy=False, deleted=True
    )


def contact_to_contact_item(
    db_contact: Contact, acapy: bool | None = False
) -> ContactItem:
    item = ContactItem(**db_contact.dict())
    if acapy:
        item.acapy = ContactAcapy(
            invitation=db_contact.invitation, connection=db_contact.connection
        )

    return item


def contacts_list_links(
    total_record_count: int,
    parameters: ContactListParameters,
) -> List[Link]:
    return build_list_links(total_record_count, parameters)
