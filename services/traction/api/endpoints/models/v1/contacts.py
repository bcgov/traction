"""Traction v1 API Contact Models.


These are the v1 API Models for managing a Tenant's Contacts.
The underlying data is a combination of Traction specific data stored in Contact table
and Connection and Invitation data in AcaPy.

"""
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
    """ContactAcapy.

    Representation for the ContactItem acapy field.

    Attributes:
      connection: AcaPy connection record
    """

    connection: dict = {}


class ContactPing(BaseModel):
    """ContactPing.

    Attributes:
      ping_enabled: whether our agent is set to auto-ping this Contact's agent
      last_response_at: last time any interaction was made with this Contact
    """

    ping_enabled: bool = False
    last_response_at: Optional[datetime] = None


class ContactItem(AcapyItem[ContactStatusType, ConnectionStateType, ContactAcapy]):
    """ContactItem.

    Inherits from AcapyItem.
    Representation for the Contact database record and associated AcaPy data.

    Attributes:
      contact_id: Traction Contact ID
      alias: Label or Name for the Contact, does not have to match the AcaPy Connection
        alias
      ping: ContactPing object
      external_reference_id: Set by tenant to correlate this Contact with entity in
        external system
      public_did: Represents the Contact's agent's Public DID (if any)
      role: Our role in relation to this Contact

    """

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
    """ContactListParameters.

    Inherits from ListAcapyItemParameters.
    Filters for fetching ContactItems

    Attributes:
      alias: return ContactItems like alias
      external_reference_id: return ContactItems like external_reference_id
      role: return ContactItems with exact role match
      deleted: when True, return ContactItems that are deleted

    """

    alias: str | None = None
    external_reference_id: Optional[str] | None = None
    role: ConnectionRoleType | None = None
    deleted: bool | None = False


class ContactListResponse(ListResponse[ContactItem]):
    pass


class ContactGetResponse(GetTimelineResponse[ContactItem, ContactTimelineItem]):
    pass


class CreateInvitationPayload(BaseModel):
    """CreateInvitationPayload.

    Payload for Create Invitation API.

    Attributes:
      alias: required, must be unique. A name/label for the Contact
      invitation_type: what type of invitation to create

    """

    alias: str = Field(...)
    invitation_type: ConnectionProtocolType = ConnectionProtocolType.Connections


class CreateInvitationResponse(GetResponse[ContactItem]):
    """CreateInvitationResponse.

    Response to Create Invitation API.
    The results of Create Invitation are to be shared with the Contact, and they will
    determine how they want to use them.

    Attributes:
      invitation: dict, exact contents will be determined by invitation_type
      invitation_url: url to the invitation.

    """

    invitation: dict | None = {}
    invitation_url: str | None = None


class ReceiveInvitationPayload(BaseModel):
    """ReceiveInvitationPayload.

    Payload for Receive Invitation API.
    This contains data from another Contact (see CreateInvitationResponse) or AcaPy
    agent that this Tenant will consume to create a Contact and Connection.

    All fields are optional, but at least one of invitation, invitation_url or
    their_public_did must be populated. Alias will override any labels in the
    invitation.

    Attributes:
      alias: name or label for our new Contact.
      invitation: dict, exact contents will be determined by invitation_type
      invitation_url: url to the invitation.
      their_public_did: a Public DID for the inviter.

    """

    alias: Optional[str] = None
    invitation: Optional[dict] = None
    invitation_url: Optional[AnyUrl] = None
    their_public_did: Optional[str] = None


class ReceiveInvitationResponse(GetResponse[ContactItem]):
    pass


class UpdateContactPayload(BaseModel):
    """UpdateContactPayload.

    Payload for Contact API update.
    Additional fields may be in the payload, but they will be ignored. Only these fields
     will be updated.


    Attributes:
      contact_id: Traction Contact ID, contact we are updating.
      status: update Status to this value
      external_reference_id: update the Contacts's external reference id
      ping: update the contact's ping_enabled flag (last_response_at will be ignored)
      public_did: update the contact's Public DID
      tags: list of tags will be replaced with this list
    """

    contact_id: UUID
    alias: str | None = None
    status: ContactStatusType | None = None
    external_reference_id: str | None = None
    ping: ContactPing | None = None
    public_did: str | None = None
    tags: List[str] | None = []


class UpdateContactResponse(GetResponse[ContactItem]):
    pass
