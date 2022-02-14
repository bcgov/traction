from enum import Enum
import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.api_client_utils import get_api_client

from acapy_client.api.basicmessage_api import BasicmessageApi
from acapy_client.api.connection_api import ConnectionApi
from acapy_client.api.out_of_band_api import OutOfBandApi
from acapy_client.model.conn_record import ConnRecord
from acapy_client.model.connection_list import ConnectionList
from acapy_client.model.invitation_create_request import InvitationCreateRequest
from acapy_client.model.invitation_message import InvitationMessage
from acapy_client.model.invitation_record import InvitationRecord
from acapy_client.model.invitation_result import InvitationResult
from acapy_client.model.receive_invitation_request import ReceiveInvitationRequest
from acapy_client.model.send_message import SendMessage
from acapy_client.model_utils import model_to_dict


logger = logging.getLogger(__name__)

router = APIRouter()


# TODO not sure if these should be global or per-request
basicmessage_api = BasicmessageApi(api_client=get_api_client())
connection_api = ConnectionApi(api_client=get_api_client())
out_of_band_api = OutOfBandApi(api_client=get_api_client())


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


def conn_record_to_connection(conn: ConnRecord) -> Connection:
    return Connection(
        accept=conn.get("accept"),
        alias=conn.get("alias"),
        connection_id=conn.connection_id,
        connection_protocol=conn.connection_protocol,
        created_at=conn.created_at,
        error_msg=conn.get("error_msg"),
        inbound_connection_id=conn.get("inbound_connection_id"),
        invitation_key=conn.get("invitation_key"),
        invitation_mode=conn.get("invitation_mode"),
        invitation_msg_id=conn.get("invitation_msg_id"),
        my_did=conn.get("my_did"),
        request_id=conn.get("request_id"),
        rfc23_state=conn.get("rfc23_state"),
        routing_state=conn.get("routing_state"),
        state=conn.state,
        their_did=conn.get("their_did"),
        their_label=conn.get("their_label"),
        their_public_did=conn.get("their_public_did"),
        their_role=conn.get("their_role"),
        updated_at=conn.updated_at,
    )


def inv_record_to_invitation(inv: InvitationRecord, connection_id: str) -> Invitation:
    return Invitation(
        connection_id=connection_id,
        invitation=inv.invitation,
        invitation_url=inv.invitation_url,
    )


def inv_result_to_invitation(inv: InvitationResult) -> Invitation:
    return Invitation(
        connection_id=inv.connection_id,
        invitation=model_to_dict(inv.invitation),
        invitation_url=inv.invitation_url,
    )


@router.get("/", response_model=list[Connection])
async def get_connections(
    alias: Optional[str] = None,
    connection_protocol: Optional[ConnectionProtocolType] = None,
    invitation_key: Optional[str] = None,
    my_did: Optional[str] = None,
    connection_state: Optional[ConnectionStateType] = None,
    their_did: Optional[str] = None,
    their_role: Optional[ConnectionRoleType] = None,
    preload_content: bool = True,
):
    # "preload_content" is just a demo ...
    params = {
        "_preload_content": preload_content,
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
    # note this is a synchronous call (if we make it async we lose the context,
    # ... which contains our tenant Bearer token)
    resp = connection_api.connections_get(**params)

    if preload_content:
        # if we set `"_preload_content": True` then the result is deserialized into
        # an array of ConnRecord, which can't be serialized as a response, so
        # we need to convert to our exposed Connection class
        conn_list: ConnectionList = resp
        conns: list[ConnRecord] = conn_list.get("results")
        connections = []
        for conn in conns:
            connections.append(conn_record_to_connection(conn))

    else:
        # if we set `"_preload_content": False` then we get the bare HTTP response
        # ... and we have to deserialize ourselves
        resp_text = resp.data
        result = json.loads(resp_text)
        logger.warn(f"Returns: {result}")
        connections = result["results"]

    return connections


async def get_connection_with_alias(alias: str):
    params = {
        "alias": alias,
    }
    connections = connection_api.connections_get(**params)
    if 0 == len(connections.get("results")):
        return None
    if 1 < len(connections.get("results")):
        raise HTTPException(
            status_code=500,
            detail=f"Error multiple connections found with alias {alias}",
        )
    return conn_record_to_connection(connections.get("results")[0])


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
        inv = out_of_band_api.out_of_band_create_invitation_post(
            body=InvitationCreateRequest(**data)
        )
        connection = await get_connection_with_alias(alias)
        invitation = inv_record_to_invitation(inv, connection.connection_id)
    else:
        params = {"alias": alias}
        inv = connection_api.connections_create_invitation_post(**params)
        invitation = inv_result_to_invitation(inv)

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
        params = {"alias": alias, "body": InvitationMessage(**payload)}
        connection = out_of_band_api.out_of_band_receive_invitation_post(**params)
    else:
        params = {"alias": alias, "body": ReceiveInvitationRequest(**payload)}
        connection = connection_api.connections_receive_invitation_post(**params)

    return conn_record_to_connection(connection)


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
        connection_id = existing_connection.connection_id
    message = {"content": payload.content}
    data = {"body": SendMessage(**message)}
    response = basicmessage_api.connections_conn_id_send_message_post(
        connection_id, **data
    )
    return response
