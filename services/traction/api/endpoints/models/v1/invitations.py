"""Traction v1 API Invitations Models.


These are the v1 API Models for managing a Tenant's Invitations.
The underlying data is a combination of Traction specific data stored in Invitation
table and Connection and Invitation data in AcaPy.

"""
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field

from api.endpoints.models.connections import (
    ConnectionStateType,
    ConnectionProtocolType,
)
from api.endpoints.models.v1.base import (
    AcapyItem,
    ListResponse,
    GetResponse,
    ListAcapyItemParameters,
)


class InvitationStatusType(str, Enum):
    active = "Active"
    deleted = "Deleted"


class InvitationAcapy(BaseModel):
    """InvitationAcapy.

    Representation for the InvitationItem acapy field.

    Attributes:
      connection: AcaPy connection record
      invitation: AcaPy invitation record
    """

    connection: dict = {}
    invitation: dict = {}


class InvitationItem(
    AcapyItem[InvitationStatusType, ConnectionStateType, InvitationAcapy]
):
    """InvitationItem.

    Inherits from AcapyItem.
    Representation for the Invitation database record and associated AcaPy data.

    Attributes:
      name: Name for the Invitation, used to find and add context to its purpose
      multi_use: when True, this is a multi_use invitation
      public: when True, this is a public invitation
      invitation_url: URL for consumers to "receive"
    """

    name: str
    multi_use: bool | None = False
    public: bool | None = False
    invitation_url: str


class InvitationListParameters(
    ListAcapyItemParameters[InvitationStatusType, ConnectionStateType]
):
    """InvitationListParameters.

    Inherits from ListAcapyItemParameters.
    Filters for fetching InvitationItems

    Attributes:
      name: return InvitationItems like name
      multi_use: when True, return InvitationItems marked multi_use
      public: when True, return InvitationItems marked public
      deleted: when True, return InvitationItems that are deleted

    """

    name: str | None = None
    deleted: bool | None = False


class InvitationListResponse(ListResponse[InvitationItem]):
    pass


class InvitationGetResponse(GetResponse[InvitationItem]):
    pass


class CreateMultiUseInvitationPayload(BaseModel):
    """CreateMultiUseInvitationPayload.

    Payload for Create MultiUse Invitation API.

    Attributes:
      name: required, must be unique. A name/label for the Invitation
      invitation_type: what type of invitation to create
      tags: list of tags added to any resulting connections

    """

    name: str = Field(...)
    invitation_type: ConnectionProtocolType = ConnectionProtocolType.Connections
    tags: Optional[List[str]] | None = None


class CreateMultiUseInvitationResponse(GetResponse[InvitationItem]):
    """CreateMultiUseInvitationResponse.

    Response to Create MultiUse Invitation API.

    Attributes:
      invitation_url: url to the MultiUse invitation.

    """

    invitation_url: str | None = None
