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
from api.endpoints.models.v1.messages import (
    SendMessagePayload,
    MessageItem,
    MessageListParameters,
    MessageStatusType,
    MessageStateType,
    MessageRole,
    MessageContact,
    MessageAcapy,
)
from sqlalchemy import select, func, desc
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
