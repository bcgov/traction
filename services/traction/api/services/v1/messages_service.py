"""API Services for Traction Messages and their AcaPy related data.

Messages Service encapsulates all data services needed for the Messages API.
Service classes should not have any knowledge or dependence on Http Request, Response
or Sessions; nor should it return API response models directly.

"""
import logging

from typing import List
from uuid import UUID

from acapy_client.api.basicmessage_api import BasicmessageApi
from acapy_client.model.send_message import SendMessage
from api.api_client_utils import get_api_client
from api.db.models.v1.contact import Contact
from api.db.models.v1.message import Message
from api.db.session import async_session
from api.endpoints.models.v1.contacts import ContactStatusType
from api.endpoints.models.v1.errors import IdNotMatchError
from api.endpoints.models.v1.messages import (
    SendMessagePayload,
    MessageItem,
    MessageListParameters,
    MessageStatusType,
    MessageStateType,
    MessageRole,
    MessageContact,
    MessageAcapy,
    UpdateMessagePayload,
)
from sqlalchemy import select, func, desc, update
from sqlalchemy.orm import selectinload

basicmessage_api = BasicmessageApi(api_client=get_api_client())

logger = logging.getLogger(__name__)


def message_to_item(db_item: Message, acapy: bool | None = False) -> MessageItem:
    """Message to MessageItem.

    Transform a Message Table record to a MessageItem object.

    Args:
      db_item: The Traction database Message
      acapy: When True, populate the MessageItem acapy field.

    Returns: The Traction MessageItem

    """
    contact = MessageContact(
        contact_id=db_item.contact.contact_id,
        alias=db_item.contact.alias,
        external_reference_id=db_item.contact.external_reference_id,
    )

    item = MessageItem(
        **db_item.dict(),
        contact=contact,
    )
    if acapy:
        item.acapy = MessageAcapy(
            sent_time=db_item.sent_time,
        )

    return item


async def send_message(
    tenant_id: UUID,
    wallet_id: UUID,
    payload: SendMessagePayload,
) -> MessageItem:
    async with async_session() as db:
        db_contact = await Contact.get_by_id(db, tenant_id, payload.contact_id)

    if db_contact.status is not ContactStatusType.active:
        # raise error
        pass

    body = SendMessage(content=payload.content)
    basicmessage_api.connections_conn_id_send_message_post(
        str(db_contact.connection_id), body=body
    )
    async with async_session() as db:
        db_item = Message(
            tenant_id=tenant_id,
            contact_id=db_contact.contact_id,
            status=MessageStatusType.sent,
            state=MessageStateType.sent,
            role=MessageRole.sender,
            tags=payload.tags,
            content=payload.content,
        )
        db.add(db_item)
        await db.commit()
        db_item = await Message.get_by_id(db, tenant_id, db_item.message_id)
    item = message_to_item(db_item, True)

    return item


async def list_messages(
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: MessageListParameters,
) -> [List[MessageItem], int]:
    """List Messages.

    Return a page of messages filtered by given parameters.

    Args:
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      parameters: filters for Messages

    Returns:
      items: The page of messages
      total_count: Total number of messages matching criteria
    """

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        Message.tenant_id == tenant_id,
        Message.deleted == parameters.deleted,
    ]
    if parameters.status:
        filters.append(Message.status == parameters.status)
    if parameters.state:
        filters.append(Message.state == parameters.state)
    if parameters.contact_id:
        filters.append(Message.contact_id == parameters.contact_id)
    if parameters.role:
        filters.append(Message.role == parameters.role)

    # build out a base query with all filters
    base_q = select(Message).filter(*filters)

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
            selectinload(Message.contact),
        )
        .order_by(desc(Message.updated_at))
    )

    async with async_session() as db:
        results_q_recs = await db.execute(results_q)
    db_items = results_q_recs.scalars()

    items = []
    for db_item in db_items:
        item = message_to_item(db_item, parameters.acapy)
        items.append(item)

    return items, total_count


async def get_message(
    tenant_id: UUID,
    wallet_id: UUID,
    message_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
) -> MessageItem:
    """Get Message.

    Find and return a Traction Message by ID.

    Args:
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      message_id: Traction ID of Message
      acapy: When True, populate the Message acapy field
      deleted: When True, return Message if marked as deleted

    Returns: The Traction MessageItem

    Raises:
      NotFoundError: if the item cannot be found by ID and deleted flag
    """
    async with async_session() as db:
        db_item = await Message.get_by_id(db, tenant_id, message_id, deleted)

    item = message_to_item(db_item, acapy)
    return item


async def update_message(
    tenant_id: UUID,
    wallet_id: UUID,
    message_id: UUID,
    payload: UpdateMessagePayload,
) -> MessageItem:
    """Update Message.

    Update a Traction Message.

    Note that not all fields can be modified. If they are present in the payload,
    they will be ignored.

    Args:
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      message_id: Traction ID of Message
      payload: Message data fields to update.

    Returns: The Traction MessageItem

    Raises:
      NotFoundError: if the record cannot be found by ID and deleted flag
      IdNotMatchError: if the message id parameter and in payload do not
        match
    """
    # verify this contact exists and is not deleted...
    async with async_session() as db:
        await Message.get_by_id(db, tenant_id, message_id, False)

    # payload contact id must match parameter
    if message_id != payload.message_id:
        raise IdNotMatchError(
            code="message.update.id-not-match",
            title="Message ID mismatch",
            detail=f"Message ID in payload <{payload.message_id}> does not match Message ID requested <{message_id}>",  # noqa: E501
        )

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["message_id"]

    q = (
        update(Message)
        .where(Message.tenant_id == tenant_id)
        .where(Message.message_id == message_id)
        .values(payload_dict)
    )
    async with async_session() as db:
        await db.execute(q)
        await db.commit()

    return await get_message(tenant_id, wallet_id, message_id, True, False)


async def delete_message(
    tenant_id: UUID, wallet_id: UUID, message_id: UUID
) -> MessageItem:
    """Delete Message.

    Delete a Traction Message.
    Note that deletes are "soft" in Traction. The Message will still exist but must be
    explicitly asked for using deleted=True parameters for Get or List.

    Args:
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      message_id: Traction ID of Message

    Returns: The Traction MessageItem

    Raises:
      NotFoundError: if the item cannot be found by ID and deleted flag
    """
    q = (
        update(Message)
        .where(Message.tenant_id == tenant_id)
        .where(Message.message_id == message_id)
        .values(
            deleted=True,
            status=MessageStatusType.deleted,
        )
    )

    async with async_session() as db:
        await db.execute(q)
        await db.commit()

    return await get_message(tenant_id, wallet_id, message_id, True, True)
