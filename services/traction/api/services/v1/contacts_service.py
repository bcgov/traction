from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.v1.contact import Contact
from api.endpoints.models.connections import ConnectionStateType, ConnectionRoleType
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
    MethodNotImplementedError,
    AlreadyExistsError,
    NotFoundError,
)
from api.services import connections


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

    invitation = connections.create_invitation(payload.alias, payload.invitation_type)
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
    return CreateInvitationResponse(item=item)


async def receive_invitation(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: ReceiveInvitationPayload,
) -> ReceiveInvitationResponse:
    raise MethodNotImplementedError(
        code="contacts.receive.invitation.not.implemented",
        title="Receive Invitation has not been implemented",
    )


async def list_contacts(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: ContactListParameters,
) -> ContactListResponse:
    raise MethodNotImplementedError(
        code="contacts.list.not.implemented",
        title="List Contacts has not been implemented",
    )


async def get_contact(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    contact_id: UUID,
    acapy: bool | None = False,
) -> ContactGetResponse:
    db_contact = await db.get(Contact, contact_id)

    if not db_contact:
        raise NotFoundError(
            code="contact.id_not_found",
            title="Contact does not exist",
            detail=f"Contact does not exist for id<{contact_id}>",
        )

    item = ContactItem(**db_contact.dict())
    if acapy:
        item.acapy = ContactAcapy(
            invitation=db_contact.invitation, connection=db_contact.connection
        )
    else:
        item.acapy = None

    return ContactGetResponse(item=item)
