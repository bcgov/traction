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
      reusable: when True, this is a reusable invitation
      public: when True, this is a public invitation
      invitation_url: URL for consumers to "receive"
    """

    name: str
    reusable: bool | None = False
    public: bool | None = False
    invitation_url: str


class InvitationListParameters(
    ListAcapyItemParameters[InvitationStatusType, ConnectionStateType]
):
    """ContactListParameters.

    Inherits from ListAcapyItemParameters.
    Filters for fetching InvitationItems

    Attributes:
      name: return InvitationItems like name
      reusable: when True, return InvitationItems marked reusable
      public: when True, return InvitationItems marked public
      deleted: when True, return InvitationItems that are deleted

    """

    name: str | None = None
    deleted: bool | None = False


class InvitationListResponse(ListResponse[InvitationItem]):
    pass


class InvitationGetResponse(GetResponse[InvitationItem]):
    pass


class CreateReusableInvitationPayload(BaseModel):
    """CreateReusableInvitationPayload.

    Payload for Create Reusable Invitation API.

    Attributes:
      name: required, must be unique. A name/label for the Invitation
      tags: list of tags added to any resulting connections

    """

    name: str = Field(...)
    tags: Optional[List[str]] | None = None


class CreateReusableInvitationResponse(GetResponse[InvitationItem]):
    """CreateReusableInvitationResponse.

    Response to Create Reusable Invitation API.

    Attributes:
      invitation_url: url to the reusable invitation.

    """

    invitation_url: str | None = None
