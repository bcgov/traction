"""Traction v1 API Verifier Models.


These are the v1 API Models for managing a Tenant's Verification Actions.
The underlying data is a combination of Traction specific data stored in Invitation
table and Connection and Invitation data in AcaPy.

"""
from typing import Optional, List
from uuid import UUID
from enum import Enum

from pydantic import BaseModel

from api.endpoints.models.v1.base import (
    AcapyItem,
    ListResponse,
    GetResponse,
    ListAcapyItemParameters,
)
from api.endpoints.models.credentials import ProofRequest


# Enums
class VerifierPresentationStatusType(str, Enum):
    PENDING = "pending"  # in event queue
    STARTING = "starting"  # being processed in event queue
    RECEIVED = "received"  # Verification has been received but not verified
    VERIFIED = "verified"  # Verified and proven to be correct
    REJECTED = "rejected"  # request was rejected/abandoned
    ERROR = "Error"  # why is this capitalized?


class AcapyPresentProofStateType(str, Enum):
    PENDING = "pending"  # added for traction event queue
    # from https://github.com/hyperledger/aries-cloudagent-python/blob/4240fa9b192ea4cdb4026211ea4bec694aec5506/aries_cloudagent/protocols/present_proof/v1_0/models/presentation_exchange.py#L49  # noqa: E501
    PROPOSAL_SENT = "proposal_sent"
    PROPOSAL_RECEIVED = "proposal_received"
    REQUEST_SENT = "request_sent"
    REQUEST_RECEIVED = "request_received"
    PRESENTATION_SENT = "presentation_sent"
    PRESENTATION_RECEIVED = "presentation_received"
    VERIFIED = "verified"
    PRESENTATION_ACKED = "presentation_acked"
    ABANDONED = "abandoned"


# Request Payloads
class CreatePresentationRequestPayload(BaseModel):
    contact_id: Optional[UUID]
    connection_id: Optional[UUID]
    proof_request: ProofRequest
    name: str
    version: str | None = "1.0.0"
    external_reference_id: str | None = None
    comment: str | None = None
    tags: Optional[List[str]] | None = []


class VerifierPresentationListParameters(
    ListAcapyItemParameters[VerifierPresentationStatusType, AcapyPresentProofStateType]
):
    contact_id: Optional[UUID]
    name: Optional[str]
    version: Optional[str]  # eg. '1.0.0'
    external_reference_id: Optional[str]
    comment: Optional[str]
    tags: Optional[List[str]]


# Response Models


class PresentationExchangeAcapy(BaseModel):
    presentation_exchange: dict = {}


class VerifierPresentationItem(
    AcapyItem[
        VerifierPresentationStatusType,
        AcapyPresentProofStateType,
        PresentationExchangeAcapy,
    ]
):
    verifier_presentation_id: UUID
    contact_id: UUID
    proof_request: ProofRequest
    name: str
    version: str
    comment: Optional[str]
    external_reference_id: Optional[str]


class VerifierPresentationListResponse(ListResponse[VerifierPresentationItem]):
    pass


class GetVerifierPresentationResponse(GetResponse[VerifierPresentationItem]):
    pass
