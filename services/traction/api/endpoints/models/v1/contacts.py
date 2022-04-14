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
    connection: dict
    invitation: dict


class ContactPing(BaseModel):
    ping_enabled: bool
    last_response_at: datetime


class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str


class Contact(AcapyItem[ContactStatusType, ConnectionStateType, ContactAcapy]):
    contact_id: UUID
    name: str
    contact_info: ContactInfo
    external_reference_id: str
    ping: ContactPing
    public_did: str
    role: ConnectionRoleType


class ContactListParameters(
    ListAcapyItemParameters[ContactStatusType, ConnectionStateType]
):
    name: str | None = None
    external_reference_id: Optional[str] | None = None
    role: ConnectionRoleType | None = None


class ContactListResponse(ListResponse[Contact]):
    pass


class ContactGetResponse(GetResponse[Contact]):
    pass


class CreateInvitationPayload(BaseModel):
    name: str = Field(...)
    invitation_type: ConnectionProtocolType = ConnectionProtocolType.DIDExchange


class CreateInvitationResponse(GetResponse[Contact]):
    pass


class ReceiveInvitationPayload(BaseModel):
    name: str = Field(...)
    invitation: Union[None, InvitationMessage, ReceiveInvitationRequest] = None
    invitation_url: Optional[AnyUrl] = None
    their_public_did: Optional[str] = None


class ReceiveInvitationResponse(GetResponse[Contact]):
    pass
