from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.v1.base import (
    AcapyItem,
    ListResponse,
)
from api.endpoints.models.credentials import (
    IssueCredentialProtocolType,
    CredentialPreview,
)


class IssuerCredentialStatusType(str, Enum):
    # offer sent, waiting for response
    offer_sent = "Offer Sent"
    # successfully issuer into the holder's wallet
    issued = "Issued"
    # you revoked this previously
    revoked = "Revoked"


class CreateSchemaPayload(BaseModel):
    """CreateSchemaPayload.

    Payload for Create Schema as Traction Tenant with Issuer Permissions.

    Attributes:
      alias: required, must be unique. A name/label for the Contact
      invitation_type: what type of invitation to create

    """

    cred_protocol: IssueCredentialProtocolType
    credential: CredentialPreview
    cred_def_id: UUID
    contact_id: UUID


class CredentialAcapy(BaseModel):
    credential_exchange: dict = {}


# class CredentialItem(
#     AcapyItem[IssuerCredentialStatusType, ConnectionStateType, CredentialAcapy]
# ):
class CredentialItem(AcapyItem[str, str, CredentialAcapy]):  # v0
    contact_id: Optional[UUID]  # v0 :UUID
    credential_id: UUID
    alias: str
    external_reference_id: Optional[str]
    public_did: Optional[str]


class CredentialsListResponse(ListResponse[CredentialItem]):
    pass
