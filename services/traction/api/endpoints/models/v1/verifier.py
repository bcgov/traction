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
    ACTIVE = "active"  # happy state waiting for next event
    RECEIVED = "received"  # Verification has been received but not verified
    VERIFIED = "verified"  # Verified and proven to be correct
    ERROR = "error"


class AcapyPresentProofStateType(str, Enum):
    PENDING = "pending"  # added for traction event queue
    # from https://github.com/hyperledger/aries-cloudagent-python/blob/4240fa9b192ea4cdb4026211ea4bec694aec5506/aries_cloudagent/protocols/present_proof/v1_0/models/presentation_exchange.py#L49 #E501
    STATE_PROPOSAL_SENT = "proposal_sent"
    STATE_PROPOSAL_RECEIVED = "proposal_received"
    STATE_REQUEST_SENT = "request_sent"
    STATE_REQUEST_RECEIVED = "request_received"
    STATE_PRESENTATION_SENT = "presentation_sent"
    STATE_PRESENTATION_RECEIVED = "presentation_received"
    STATE_VERIFIED = "verified"
    STATE_PRESENTATION_ACKED = "presentation_acked"
    STATE_ABANDONED = "abandoned"


# Request Payloads
class CreatePresentationRequestPayload(BaseModel):
    contact_id: Optional[UUID]
    connection_id: Optional[UUID]

    proof_request: ProofRequest
    # TODO: support GET'ing by the following attributes
    comment: Optional[str]
    tags: Optional[List[str]]
    external_reference_id: Optional[str]
    name: Optional[str]
    version: Optional[str]  # eg. '1.0.0'


class VerifierPresentationListParameters(
    ListAcapyItemParameters[VerifierPresentationStatusType, AcapyPresentProofStateType]
):
    contact_id: Optional[UUID]
    comment: Optional[str]
    tags: Optional[List[str]]
    external_reference_id: Optional[str]
    name: Optional[str]
    version: Optional[str]  # eg. '1.0.0'


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


class VerifierPresentationListResponse(ListResponse[VerifierPresentationItem]):
    pass


class GetVerifierPresentationResponse(GetResponse[VerifierPresentationItem]):
    pass
