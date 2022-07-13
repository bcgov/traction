from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.credentials import CredentialStateType
from api.endpoints.models.v1.base import (
    ListAcapyItemParameters,
    AcapyItem,
    TimelineItem,
    ListResponse,
    GetTimelineResponse,
    GetResponse,
)


class HolderCredentialStatusType(str, Enum):
    # pending, nothing happened yet
    pending = "Pending"
    # offer received, waiting for action
    offer_received = "Offer Received"
    # offer received, action taken to accept, not in wallet
    offer_accepted = "Offer Accepted"
    # credential in holder's wallet
    accepted = "Accepted"
    # credential offer was rejected
    rejected = "Rejected"
    # this has been revoked by the issuer
    revoked = "Revoked"
    # item is soft deleted
    deleted = "Deleted"
    error = "Error"


class HolderCredentialListParameters(
    ListAcapyItemParameters[HolderCredentialStatusType, CredentialStateType]
):
    contact_id: UUID | None = None
    schema_id: str | None = None
    cred_def_id: str | None = None
    external_reference_id: str | None = None


class HolderCredentialContact(BaseModel):
    contact_id: UUID
    alias: str
    external_reference_id: str | None = None


class HolderCredentialAcapy(BaseModel):
    credential_exchange_id: str | None = None
    revoc_reg_id: str | None = None
    revocation_id: str | None = None
    credential_exchange: dict | None = {}
    credential: dict | None = {}


class HolderCredentialItem(
    AcapyItem[HolderCredentialStatusType, CredentialStateType, HolderCredentialAcapy]
):
    holder_credential_id: UUID
    contact: HolderCredentialContact
    alias: str | None = None
    revoked: bool
    revocation_comment: str | None = None
    rejection_comment: str | None = None
    external_reference_id: str | None = None


class HolderCredentialTimelineItem(
    TimelineItem[HolderCredentialStatusType, CredentialStateType]
):
    pass


class HolderCredentialListResponse(ListResponse[HolderCredentialItem]):
    pass


class HolderCredentialGetResponse(
    GetTimelineResponse[HolderCredentialItem, HolderCredentialTimelineItem]
):
    pass


class AcceptCredentialOfferPayload(BaseModel):
    holder_credential_id: UUID | None = None
    alias: str | None = None
    external_reference_id: str | None = None
    tags: List[str] | None = []


class AcceptCredentialOfferResponse(GetResponse[HolderCredentialItem]):
    pass


class UpdateHolderCredentialPayload(AcceptCredentialOfferPayload):
    pass


class UpdateHolderCredentialResponse(GetResponse[HolderCredentialItem]):
    pass


class RejectCredentialOfferPayload(BaseModel):
    holder_credential_id: UUID
    rejection_comment: str | None = None
