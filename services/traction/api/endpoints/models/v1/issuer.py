from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.v1.base import (
    AcapyItem,
    ListResponse,
)


class IssuerCredentialStatusType(str, Enum):
    # offer sent, waiting for response
    offer_sent = "Offer Sent"
    # successfully issuer into the holder's wallet
    issued = "Issued"
    # you revoked this previously
    revoked = "Revoked"


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
