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


class AcapyCredentialExchangeStateType(str, Enum):
    # from https://github.com/hyperledger/aries-cloudagent-python/blob/db6b7699e603ecb335165a79459fbab7b6587a70/aries_cloudagent/protocols/issue_credential/v1_0/models/credential_exchange.py#L44
    STATE_PROPOSAL_SENT = "proposal_sent"
    STATE_PROPOSAL_RECEIVED = "proposal_received"
    STATE_OFFER_SENT = "offer_sent"
    STATE_OFFER_RECEIVED = "offer_received"
    STATE_REQUEST_SENT = "request_sent"
    STATE_REQUEST_RECEIVED = "request_received"
    STATE_ISSUED = "credential_issued"
    STATE_CREDENTIAL_RECEIVED = "credential_received"
    STATE_ACKED = "credential_acked"
    STATE_CREDENTIAL_REVOKED = "credential_revoked"
    STATE_ABANDONED = "abandoned"


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
#     AcapyItem[IssuerCredentialStatusType, AcapyCredentialExchangeStateType, CredentialAcapy]
# ):
class CredentialItem(AcapyItem[str, AcapyCredentialExchangeStateType, CredentialAcapy]):
    contact_id: UUID
    credential_id: UUID
    external_reference_id: Optional[str]
    public_did: Optional[str]


class CredentialsListResponse(ListResponse[CredentialItem]):
    pass
