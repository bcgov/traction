from datetime import datetime
from enum import Enum
from typing import Union, Optional
from uuid import UUID

from pydantic import BaseModel, Field, AnyUrl

from acapy_wrapper.models.invitation_message import InvitationMessage
from acapy_wrapper.models.receive_invitation_request import ReceiveInvitationRequest
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
)


class ContactStatusType(str, Enum):
    active = "Active"
    approved = "Approved"
    pending = "Pending"


class ContactAcapy(BaseModel):
    connection: dict = {}
    invitation: dict = {}


class ContactPing(BaseModel):
    ping_enabled: bool = False
    last_response_at: Optional[datetime] = None


class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ContactItem(AcapyItem[ContactStatusType, ConnectionStateType, ContactAcapy]):
    contact_id: UUID
    alias: str
    contact_info: ContactInfo = ContactInfo()
    external_reference_id: Optional[str]
    ping: ContactPing = ContactPing()
    public_did: Optional[str]
    role: ConnectionRoleType


class ContactListParameters(
    ListAcapyItemParameters[ContactStatusType, ConnectionStateType]
):
    alias: str | None = None
    external_reference_id: Optional[str] | None = None
    role: ConnectionRoleType | None = None


class ContactListResponse(ListResponse[ContactItem]):
    pass


class ContactGetResponse(GetResponse[ContactItem]):
    pass


class CreateInvitationPayload(BaseModel):
    alias: str = Field(...)
    invitation_type: ConnectionProtocolType = ConnectionProtocolType.DIDExchange


class CreateInvitationResponse(GetResponse[ContactItem]):
    pass


class ReceiveInvitationPayload(BaseModel):
    alias: str = Field(...)
    invitation: Union[None, InvitationMessage, ReceiveInvitationRequest] = None
    invitation_url: Optional[AnyUrl] = None
    their_public_did: Optional[str] = None


class ReceiveInvitationResponse(GetResponse[ContactItem]):
    pass
