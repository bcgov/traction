import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from api.endpoints.models.connections import (
    ConnectionProtocolType,
    ConnectionStateType,
    ConnectionRoleType,
    Connection,
    Invitation,
    BasicMessage,
)
from api.services.connections import (
    get_connections,
    get_connection_with_alias,
    create_invitation,
    receive_invitation,
    send_basic_message,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[Connection])
async def get_tenant_connections(
    alias: Optional[str] = None,
    connection_protocol: Optional[ConnectionProtocolType] = None,
    invitation_key: Optional[str] = None,
    my_did: Optional[str] = None,
    connection_state: Optional[ConnectionStateType] = None,
    their_did: Optional[str] = None,
    their_role: Optional[ConnectionRoleType] = None,
):
    params = {}
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

    connections = get_connections(params)

    return connections


@router.post("/create-invitation", response_model=Invitation)
async def create_tenant_invitation(
    alias: str,
    invitation_type: ConnectionProtocolType = ConnectionProtocolType.DIDExchange,
):
    existing_connection = get_connection_with_alias(alias)
    if existing_connection is not None:
        raise HTTPException(
            status_code=500,
            detail=f"Error alias {alias} already in use: {existing_connection}",
        )

    invitation = create_invitation(alias, invitation_type)

    return invitation


@router.post("/receive-invitation", response_model=Connection)
async def receive_tenant_invitation(
    alias: str,
    payload: dict | None = None,
    their_public_did: str | None = None,
):
    existing_connection = get_connection_with_alias(alias)
    if existing_connection is not None:
        raise HTTPException(
            status_code=500, detail=f"Error alias {alias} already in use"
        )

    connection = receive_invitation(
        alias, payload=payload, their_public_did=their_public_did
    )

    return connection


@router.post("/send-message", response_model=dict)
async def send_tenant_message(
    payload: BasicMessage,
    connection_id: str | None = None,
    alias: str | None = None,
):
    if not connection_id:
        existing_connection = get_connection_with_alias(alias)
        if not existing_connection:
            raise HTTPException(
                status_code=404, detail=f"Error alias {alias} does not exist"
            )
        connection_id = existing_connection.connection_id

    response = send_basic_message(connection_id, payload.content)

    return response
