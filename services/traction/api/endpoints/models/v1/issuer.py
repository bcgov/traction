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


class IssueCredentialPayload(BaseModel):
    """CreateSchemaPayload.

    Payload for Create Schema as Traction Tenant with Issuer Permissions.

    Attributes:
      cred_protocol: required
      credential:
      cred_def_id:
      contact_id:
    """

    cred_protocol: IssueCredentialProtocolType
    credential: CredentialPreview
    cred_def_id: str
    contact_id: UUID


class RevokeSchemaPayload(BaseModel):
    """RevokeSchemaPayload.

    Payload for Create Schema as Traction Tenant with Issuer Permissions.

    Attributes:
      cred_issue_id:
      rev_reg_id:
      cred_rev_id:
      comment:

    """

    cred_issue_id: UUID
    rev_reg_id: UUID
    cred_rev_id: UUID
    comment: str


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
