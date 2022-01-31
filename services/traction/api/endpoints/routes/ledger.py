from enum import Enum
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from api import acapy_utils as au

router = APIRouter()


class DIDEndpoint(BaseModel):
    endpoint: str


class DIDEndpointType(str, Enum):
    Endpoint = "Endpoint"
    Profile = "Profile"
    LinkedDomains = "LinkedDomains"


@router.get("/did-endpoint", response_model=DIDEndpoint)
async def get_did_endpoint(
    did: str,
    endpoint_type: Optional[DIDEndpointType] = None,
):
    params = {"did": did}
    if endpoint_type:
        params["endpoint_type"] = endpoint_type.value
    endpoint = await au.acapy_GET("ledger/did-endpoint", params=params)
    return endpoint
