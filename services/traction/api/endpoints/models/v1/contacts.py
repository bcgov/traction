from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, AnyUrl

from api.endpoints.models.connections import (
    ConnectionStateType,
    ConnectionRoleType,
    ConnectionProtocolType,
)
from api.endpoints.models.v1.base import (
    AcapyItem,
    ListResponse,
    GetResponse,
    ListAcapyItemParameters,
    TimelineItem,
    GetTimelineResponse,
)


class ContactStatusType(str, Enum):
    active = "Active"
    approved = "Approved"
    pending = "Pending"
    deleted = "Deleted"


class ContactAcapy(BaseModel):
    connection: dict = {}
    invitation: dict = {}


class ContactPing(BaseModel):
    ping_enabled: bool = False
    last_response_at: Optional[datetime] = None


class ContactItem(AcapyItem[ContactStatusType, ConnectionStateType, ContactAcapy]):
    contact_id: UUID
    alias: str
    external_reference_id: Optional[str]
    ping: ContactPing = ContactPing()
    public_did: Optional[str]
    role: ConnectionRoleType


class ContactTimelineItem(TimelineItem[ContactStatusType, ConnectionStateType]):
    pass


class ContactListParameters(
    ListAcapyItemParameters[ContactStatusType, ConnectionStateType]
):
    alias: str | None = None
    external_reference_id: Optional[str] | None = None
    role: ConnectionRoleType | None = None
    deleted: bool | None = False


class ContactListResponse(ListResponse[ContactItem]):
    pass


class ContactGetResponse(GetTimelineResponse[ContactItem, ContactTimelineItem]):
    pass


class CreateInvitationPayload(BaseModel):
    alias: str = Field(...)
    invitation_type: ConnectionProtocolType = ConnectionProtocolType.DIDExchange


class CreateInvitationResponse(GetResponse[ContactItem]):
    invitation: dict | None = {}
    invitation_url: str | None = None


class ReceiveInvitationPayload(BaseModel):
    alias: Optional[str] = None
    invitation: Optional[dict] = None
    invitation_url: Optional[AnyUrl] = None
    their_public_did: Optional[str] = None


class ReceiveInvitationResponse(GetResponse[ContactItem]):
    pass


class UpdateContactPayload(BaseModel):
    contact_id: UUID
    alias: str | None = None
    status: ContactStatusType | None = None
    external_reference_id: str | None = None
    ping: ContactPing | None = None
    public_did: str | None = None
    tags: List[str] | None = []


class UpdateContactResponse(GetResponse[ContactItem]):
    pass
