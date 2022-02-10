from enum import Enum
import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api import acapy_utils as au
from api.core.config import settings

from acapy_client.api_client import ApiClient
from acapy_client.api.connection_api import ConnectionApi
from acapy_client.configuration import Configuration
from acapy_client.model.conn_record import ConnRecord


logger = logging.getLogger(__name__)

router = APIRouter()

configuration = Configuration(host=settings.ACAPY_ADMIN_URL)
api_client = ApiClient(configuration=configuration)
connection_api = ConnectionApi(api_client=api_client)  # noqa: E501


class ConnectionProtocolType(str, Enum):
    Connections = "connections/1.0"
    DIDExchange = "didexchange/1.0"


class ConnectionStateType(str, Enum):
    start = "start"
    init = "init"
    invitation = "invitation"
    request = "request"
    response = "response"
    active = "active"
    completed = "completed"
    abandoned = "abandoned"
    error = "error"


class ConnectionRoleType(str, Enum):
    inviter = "inviter"
    invitee = "invitee"
    requester = "requester"
    responder = "responder"


class Connection(BaseModel):
    endpoint: str | None = None
    accept: str
    alias: str | None = None
    connection_id: str
    connection_protocol: str
    created_at: str
    error_msg: str | None = None
    inbound_connection_id: str | None = None
    invitation_key: str
    invitation_mode: str
    invitation_msg_id: str | None = None
    my_did: str | None = None
    request_id: str | None = None
    rfc23_state: str
    routing_state: str | None = None
    state: str
    their_did: str | None = None
    their_label: str | None = None
    their_public_did: str | None = None
    their_role: str | None = None
    updated_at: str


class Invitation(BaseModel):
    connection_id: str
    invitation: dict
    invitation_url: str


class BasicMessage(BaseModel):
    content: str


@router.get("/", response_model=list[Connection])
async def get_connections(
    alias: Optional[str] = None,
    connection_protocol: Optional[ConnectionProtocolType] = None,
    invitation_key: Optional[str] = None,
    my_did: Optional[str] = None,
    connection_state: Optional[ConnectionStateType] = None,
    their_did: Optional[str] = None,
    their_role: Optional[ConnectionRoleType] = None,
):
    params = {
        "_preload_content": False,
    }
    if alias:
        params["alias"] = alias
    if connection_protocol:
        params["connection_protocol"] = connection_protocol
    if invitation_key:
        params["invitation_key"] = invitation_key
    if my_did:
        params["my_did"] = my_did
    if connection_state:
        params["state"] = connection_state
    if their_did:
        params["their_did"] = their_did
    if their_role:
        params["their_role"] = their_role

    # connections = await au.acapy_GET("connections", params=params)
    # note this is a synchronous call (if we make it async we lose the context, which contains our tenant Bearer token)
    resp = connection_api.connections_get(**params)

    # if we set `"_preload_content": True` then the result is deserialized into an array of ConnRecord,
    #  ... which can't be serialized as a response, so we need to convert to our exposed Connection class
    # if we set `"_preload_content": False` then we get the bare HTTP response and re have to deserialize ourselves
    resp_text = resp.data
    result = json.loads(resp_text)
    logger.warn(f"Returns: {result}")

    return result["results"]


async def get_connection_with_alias(alias: str):
    params = {
        "alias": alias,
    }
    connections = await au.acapy_GET("connections", params=params)
    if 0 == len(connections["results"]):
        return None
    if 1 < len(connections["results"]):
        raise HTTPException(
            status_code=500,
            detail=f"Error multiple connections found with alias {alias}",
        )
    return connections["results"][0]


@router.post("/create-invitation", response_model=Invitation)
async def create_invitation(
    alias: str,
    invitation_type: ConnectionProtocolType = ConnectionProtocolType.DIDExchange,
):
    existing_connection = await get_connection_with_alias(alias)
    if existing_connection:
        raise HTTPException(
            status_code=500,
            detail=f"Error alias {alias} already in use: {existing_connection}",
        )
    if invitation_type == ConnectionProtocolType.DIDExchange:
        data = {
            "alias": alias,
            "handshake_protocols": [
                "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/didexchange/1.0",
            ],
        }
        invitation = await au.acapy_POST(
            "out-of-band/create-invitation", data=data, params=None
        )
        connection = await get_connection_with_alias(alias)
        invitation["connection_id"] = connection["connection_id"]
    else:
        params = {"alias": alias}
        invitation = await au.acapy_POST(
            "connections/create-invitation", data={}, params=params
        )
    return invitation


@router.post("/receive-invitation", response_model=Connection)
async def receive_invitation(
    payload: dict,
    alias: str,
):
    existing_connection = await get_connection_with_alias(alias)
    if existing_connection:
        raise HTTPException(
            status_code=500, detail=f"Error alias {alias} already in use"
        )
    if "/out-of-band/" in payload.get("@type", ""):
        params = {"alias": alias}
        connection = await au.acapy_POST(
            "out-of-band/receive-invitation", data=payload, params=params
        )
    else:
        params = {"alias": alias}
        connection = await au.acapy_POST(
            "connections/receive-invitation", data=payload, params=params
        )
    return connection


@router.post("/send-message", response_model=dict)
async def send_message(
    payload: BasicMessage,
    connection_id: str | None = None,
    alias: str | None = None,
):
    if not connection_id:
        existing_connection = await get_connection_with_alias(alias)
        if not existing_connection:
            raise HTTPException(
                status_code=404, detail=f"Error alias {alias} does not exist"
            )
        connection_id = existing_connection["connection_id"]
    message = {"content": payload.content}
    response = await au.acapy_POST(
        f"connections/{connection_id}/send-message", data=message
    )
    return response
