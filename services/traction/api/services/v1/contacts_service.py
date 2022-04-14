from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from api.endpoints.models.v1.contacts import (
    CreateInvitationPayload,
    CreateInvitationResponse,
    ReceiveInvitationPayload,
    ReceiveInvitationResponse,
    ContactListParameters,
    ContactListResponse,
)
from api.endpoints.models.v1.errors import MethodNotImplementedError


async def create_invitation(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: CreateInvitationPayload,
) -> CreateInvitationResponse:
    raise MethodNotImplementedError(
        code="contacts.create.invitation.not.implemented",
        title="Create Invitation has not been implemented",
    )


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
) -> ContactListResponse:
    raise MethodNotImplementedError(
        code="contact.get.not.implemented",
        title="Get Contact has not been implemented",
    )
