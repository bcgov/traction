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


class IssuerCredentialStatusType(str, Enum):
    # offer sent, waiting for response
    offer_sent = "Offer Sent"
    # successfully issuer into the holder's wallet
    issued = "Issued"
    # you revoked this previously
    revoked = "Revoked"


class HolderCredentialStatusType(str, Enum):
    # offer received needs response
    offer_received = "Offer Received"
    # successfully issued into your wallet
    active = "Active"
    # revoked by issuer
    revoked = "Revoked"


class CredentialAcapy(BaseModel):
    credential_exchange: dict = {}


# class CredentialItem(
#     AcapyItem[IssuerCredentialStatusType, ConnectionStateType, CredentialAcapy]
# ):
class CredentialItem(AcapyItem[str, str, CredentialAcapy]):  # v0
    contact_id: Optional[UUID]  # v0 :UUID
    alias: str
    external_reference_id: Optional[str]
    public_did: Optional[str]


class CredentialsListResponse(ListResponse[CredentialItem]):
    pass
