"""Traction v1 API Messages Models.


These are the v1 API Models for managing a Tenant's (AcaPy) Messages.
The underlying data is a combination of Traction specific data stored in Message
table and Connection data in AcaPy.

"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.v1.base import (
    AcapyItem,
    ListResponse,
    GetResponse,
    ListAcapyItemParameters,
)


class MessageStatusType(str, Enum):
    sent = "Sent"
    received = "Received"
    deleted = "Deleted"


class MessageStateType(str, Enum):
    sent = "sent"
    received = "received"


class MessageRole(str, Enum):
    sender = "Sender"
    recipient = "Recipient"


class MessageContact(BaseModel):
    contact_id: UUID
    alias: str
    external_reference_id: str | None = None


class MessageAcapy(BaseModel):
    sent_time: datetime | None = None


class MessageItem(AcapyItem[MessageStatusType, MessageStateType, MessageAcapy]):
    """MessageItem.

    Inherits from AcapyItem.
    Representation for the Message database record and associated AcaPy data.

    Attributes:
      contact: Traction contact message was sent to/received from
      content: Actual content of the message
      role: Role tenant played in this message
    """

    contact: MessageContact
    content: str
    role: MessageRole


class MessageListParameters(
    ListAcapyItemParameters[MessageStatusType, MessageStateType]
):
    """InvitationListParameters.

    Inherits from ListAcapyItemParameters.
    Filters for fetching MessageItems

    Attributes:
      contact_id: Traction ID for other participant in message
      role: Message role (role this tenant played in the message exchange)
    """

    contact_id: UUID | None = None
    role: MessageRole | None = None


class MessageListResponse(ListResponse[MessageItem]):
    pass


class MessageGetResponse(GetResponse[MessageItem]):
    pass


class SendMessagePayload(BaseModel):
    """SendMessagePayload.

    Payload for Send Message API.

    Attributes:
      content: required, actual content of the message
      contact_id: Traction ID of recipient
      tags: list of tags for categorizing

    """

    content: str
    contact_id: UUID
    tags: Optional[List[str]] | None = None


class SendMessageResponse(GetResponse[MessageItem]):
    """SendMessageResponse.

    Response to Send Message API.
    """

    pass
