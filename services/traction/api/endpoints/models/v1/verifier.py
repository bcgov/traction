"""Traction v1 API Invitations Models.


These are the v1 API Models for managing a Tenant's Invitations.
The underlying data is a combination of Traction specific data stored in Invitation
table and Connection and Invitation data in AcaPy.

"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.v1.base import (
    AcapyItem,
    ListResponse,
    GetResponse,
)
from api.endpoints.models.credentials import ProofRequest


class CreatePresentationRequestPayload(BaseModel):
    contact_id: UUID
    proof_request: ProofRequest


class PresentationExchangeAcapy(BaseModel):
    presentation_exchange: dict = {}


class PresentationRequestItem(AcapyItem[str, str, PresentationExchangeAcapy]):
    v_presentation_request_id: UUID
    contact_id: UUID
    pres_exch_id: Optional[UUID]
    proof_request: ProofRequest


class PresentationRequestListResponse(ListResponse[PresentationRequestItem]):
    pass


class GetPresentationRequestResponse(GetResponse[PresentationRequestItem]):
    pass
