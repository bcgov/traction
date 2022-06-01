"""Traction v1 API Invitations Models.


These are the v1 API Models for managing a Tenant's Invitations.
The underlying data is a combination of Traction specific data stored in Invitation
table and Connection and Invitation data in AcaPy.

"""
from enum import Enum
from typing import Optional, List
from uuid import UUID
from api.endpoints.models.credentials import PresentCredentialProtocolType

from pydantic import BaseModel, Field

from api.endpoints.models.connections import (
    ConnectionStateType,
    ConnectionProtocolType,
)
from api.endpoints.models.v1.base import (
    AcapyItem,
    ListResponse,
    GetResponse,
    ListAcapyItemParameters,
)
from api.endpoints.models.credentials import ProofRequest


class CreatePresentationRequestPayload(BaseModel):
    # pres_protocol: built into path, different endpoints for different protocols6
    proof_req: ProofRequest
    contact_id: UUID


class PresentationExchangeAcapy(BaseModel):
    presentation_exchange: dict = {}


class PresentationRequestItem(AcapyItem[str, str, PresentationExchangeAcapy]):
    pres_exch_id: UUID


class PresentationRequestListResponse(ListResponse[PresentationRequestItem]):
    pass


class GetPresentationRequestResponse(GetResponse[PresentationRequestItem]):
    pass
