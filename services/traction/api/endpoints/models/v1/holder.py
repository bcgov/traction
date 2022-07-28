from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.credentials import (
    CredentialStateType,
    CredPrecisForProof,
    CredPresentation,
)
from api.endpoints.models.v1.base import (
    ListAcapyItemParameters,
    AcapyItem,
    TimelineItem,
    ListResponse,
    GetTimelineResponse,
    GetResponse,
    ListItemParameters,
)
from api.endpoints.models.v1.verifier import AcapyPresentProofStateType


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


class HolderPresentationStatusType(str, Enum):
    # pending, nothing happened yet
    pending = "Pending"
    proposol_sent = "Proposal Sent"
    # offer received, waiting for action
    request_received = "Request Received"
    presentation_sent = "Presentation Sent"
    # we sent, they got it
    presentation_acked = "Presentation Received"
    # presentation request was rejected
    rejected = "Rejected"
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


class HolderPresentationListParameters(
    ListAcapyItemParameters[HolderPresentationStatusType, AcapyPresentProofStateType]
):
    contact_id: UUID | None = None
    external_reference_id: str | None = None


class HolderCredentialContact(BaseModel):
    contact_id: UUID
    alias: str
    external_reference_id: str | None = None


class HolderPresentationContact(BaseModel):
    contact_id: UUID
    alias: str
    external_reference_id: str | None = None


class HolderCredentialAcapy(BaseModel):
    credential_exchange_id: str | None = None
    revoc_reg_id: str | None = None
    revocation_id: str | None = None
    credential_exchange: dict | None = {}
    credential: dict | None = {}


class HolderPresentationAcapy(BaseModel):
    presentation_exchange_id: str | None = None
    presentation_exchange: dict | None = {}


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


class HolderPresentationItem(
    AcapyItem[
        HolderPresentationStatusType,
        AcapyPresentProofStateType,
        HolderPresentationAcapy,
    ]
):
    holder_presentation_id: UUID
    contact: HolderPresentationContact
    alias: str | None = None
    external_reference_id: str | None = None
    rejection_comment: str | None = None
    presentation: dict | None = {}


class HolderCredentialTimelineItem(
    TimelineItem[HolderCredentialStatusType, CredentialStateType]
):
    pass


class HolderPresentationTimelineItem(
    TimelineItem[HolderPresentationStatusType, AcapyPresentProofStateType]
):
    pass


class HolderCredentialListResponse(ListResponse[HolderCredentialItem]):
    pass


class HolderPresentationListResponse(ListResponse[HolderPresentationItem]):
    pass


class HolderCredentialGetResponse(
    GetTimelineResponse[HolderCredentialItem, HolderCredentialTimelineItem]
):
    pass


class HolderPresentationGetResponse(
    GetTimelineResponse[HolderPresentationItem, HolderPresentationTimelineItem]
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


class UpdateHolderPresentationPayload(BaseModel):
    holder_presentation_id: UUID | None = None
    alias: str | None = None
    external_reference_id: str | None = None
    tags: List[str] | None = []


class UpdateHolderCredentialResponse(GetResponse[HolderCredentialItem]):
    pass


class UpdateHolderPresentationResponse(GetResponse[HolderPresentationItem]):
    pass


class RejectCredentialOfferPayload(BaseModel):
    holder_credential_id: UUID
    rejection_comment: str | None = None


class HolderPresentationCredentialListParameters(ListItemParameters[None, None]):
    pass


class HolderPresentationCredentialItem(CredPrecisForProof):
    pass


class HolderPresentationCredentialListResponse(
    ListResponse[HolderPresentationCredentialItem]
):
    pass


class SendPresentationPayload(BaseModel):
    holder_presentation_id: UUID
    presentation: CredPresentation
    alias: str | None = None
    external_reference_id: str | None = None
    tags: List[str] | None = []


class RejectPresentationRequestPayload(BaseModel):
    holder_presentation_id: UUID
    rejection_comment: str | None = None
    alias: str | None = None
    external_reference_id: str | None = None
    tags: List[str] | None = []


class PresentationProposalAttribute(BaseModel):
    name: str | None = None
    cred_def_id: str | None = None
    mime_type: str | None = None
    referent: str | None = None
    value: str | None = None


class PresentationProposalPredicate(BaseModel):
    name: str | None = None
    predicate: str | None = None
    threshold: int | None = None
    cred_def_id: str | None = None


class PresentationProposal(BaseModel):
    attributes: List[PresentationProposalAttribute] | None = []
    predicates: List[PresentationProposalPredicate] | None = []


class HolderSendProposalPayload(BaseModel):
    contact_id: UUID
    comment: str | None = None
    presentation_proposal: PresentationProposal


class HolderSendProposalResponse(GetResponse[HolderPresentationItem]):
    pass
