from aiohttp import (
    ClientResponse,
)
from enum import Enum
import json
from typing import Optional

from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from starlette_context import context

from api import acapy_utils as au
from config import Config


router = APIRouter()


class DIDEndpoint(BaseModel):
    endpoint: str

class DIDEndpointType(str, Enum):
    Endpoint = "Endpoint"
    Profile = "Profile"
    LinkedDomains = "LinkedDomains"


@router.get("/did-endpoint", response_model=DIDEndpoint)
async def get_did_endpoint(did: str, endpoint_type: Optional[DIDEndpointType] = None):
    params = {"did": did}
    if endpoint_type:
        params["endpoint_type"] = endpoint_type.value
    endpoint = await au.acapy_GET("/ledger/did-endpoint", params=params)
    return endpoint

