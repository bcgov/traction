"""API Services for Traction Invitations and their AcaPy related data.

Invitations Service encapsulates all data services needed for the Invitations API.
Service classes should not have any knowledge or dependence on Http Request, Response
or Sessions; nor should it return API response models directly.

"""
import logging

from typing import List
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.sql.functions import func
from sqlmodel.ext.asyncio.session import AsyncSession

from api.endpoints.models.v1.errors import (
    AlreadyExistsError,
)
from api.services import connections
from api.db.models.v1.invitation import Invitation
from api.endpoints.models.v1.invitations import (
    CreateReusableInvitationPayload,
    CreateReusableInvitationResponse,
    InvitationListParameters,
    InvitationItem,
    InvitationAcapy,
    InvitationStatusType,
)
from api.endpoints.models.connections import ConnectionProtocolType

logger = logging.getLogger(__name__)


async def create_reusable_invitation(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: CreateReusableInvitationPayload,
) -> [InvitationItem, str]:
    """Create ReusableInvitation.

    Create a reusable Invitation, this can be called by many different agents each use
    of this invitation will result in a new Contact

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      payload: Reusable Invitation data

    Returns:
      item: The Traction Invitation
      invitation_url: Invitation in URL format

    Raises:
        AlreadyExistsError: if the provided name already exists
    """
    # see if there is an existing connection with this alias (name)
    existing_connection = connections.get_connection_with_alias(payload.name)
    if existing_connection is not None:
        raise AlreadyExistsError(
            code="invitation.create.reusable.invitation.existing.alias",
            title="Create Reusable Invitation alias in use",
            detail=f"Error alias {payload.name} already in use.",
        )

    acapy_invitation = connections.create_invitation(
        alias=payload.name,
        invitation_type=ConnectionProtocolType.DIDExchange,
        multi_use=True,
    )
    connection = connections.get_connection_with_alias(payload.name)
    invitation_url = acapy_invitation.invitation_url

    # create a new contact record
    db_invitation = Invitation(
        name=payload.name,
        tags=payload.tags,
        tenant_id=tenant_id,
        public=False,
        reusable=True,
        status=InvitationStatusType.active,
        state=connection.state,
        connection=connection,
        connection_id=connection.connection_id,
        connection_alias=connection.alias,
        invitation_key=connection.invitation_key,
        invitation=acapy_invitation.invitation,
        invitation_url=invitation_url,
    )
    db.add(db_invitation)
    await db.commit()

    item = invitation_to_invitation_item(db_invitation, True)

    return item, invitation_url


async def list_invitations(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: InvitationListParameters,
) -> [List[CreateReusableInvitationResponse], int]:
    """List Invitations.

    Return a page of invitations filtered by given parameters.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      parameters: filters for Invitations

    Returns:
      items: The page of contacts
      total_count: Total number of contacts matching criteria
    """

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        Invitation.tenant_id == tenant_id,
        Invitation.deleted == parameters.deleted,
    ]
    if parameters.status:
        filters.append(Invitation.status == parameters.status)
    if parameters.state:
        filters.append(Invitation.state == parameters.state)
    if parameters.name:
        filters.append(Invitation.name.contains(parameters.name))

    # build out a base query with all filters
    base_q = select(Invitation).filter(*filters)

    # get a count of ALL records matching our base query
    count_q = select([func.count()]).select_from(base_q)
    count_q_rec = await db.execute(count_q)
    total_count = count_q_rec.scalar()

    # TODO: should we raise an exception if paging is invalid?
    # ie. is negative, or starts after available records

    # add in our paging and ordering to get the result set
    results_q = base_q.limit(limit).offset(skip).order_by(desc(Invitation.created_at))

    results_q_recs = await db.execute(results_q)
    db_items = results_q_recs.scalars()

    items = []
    for db_item in db_items:
        item = invitation_to_invitation_item(db_item, parameters.acapy)
        items.append(item)

    return items, total_count


def invitation_to_invitation_item(
    db_rec: Invitation, acapy: bool | None = False
) -> InvitationItem:
    """Invitation to InvitationItem.

    Transform a Invitation Table record to a InvitationItem object.

    Args:
      db_rec: The Traction database Contact
      acapy: When True, populate the InvitationItem acapy field.

    Returns: The Traction InvitationItem

    Raises:
      NotFoundError: if the invitation cannot be found by ID and deleted flag
    """
    item = InvitationItem(**db_rec.dict())
    if acapy:
        item.acapy = InvitationAcapy(
            invitation=db_rec.invitation, connection=db_rec.connection
        )

    return item
