import logging

from fastapi import HTTPException

from api.api_client_utils import get_api_client
from api.endpoints.models.connections import (
    ConnectionProtocolType,
    Connection,
    Invitation,
)

from acapy_client.model_utils import model_to_dict
from acapy_client.api.basicmessage_api import BasicmessageApi
from acapy_client.api.connection_api import ConnectionApi
from acapy_client.api.did_exchange_api import DidExchangeApi
from acapy_client.api.out_of_band_api import OutOfBandApi
from acapy_client.model.conn_record import ConnRecord
from acapy_client.model.connection_list import ConnectionList
from acapy_client.model.invitation_create_request import InvitationCreateRequest
from acapy_client.model.invitation_message import InvitationMessage
from acapy_client.model.invitation_record import InvitationRecord
from acapy_client.model.invitation_result import InvitationResult
from acapy_client.model.receive_invitation_request import ReceiveInvitationRequest
from acapy_client.model.send_message import SendMessage


logger = logging.getLogger(__name__)

# TODO not sure if these should be global or per-request
basicmessage_api = BasicmessageApi(api_client=get_api_client())
connection_api = ConnectionApi(api_client=get_api_client())
did_exchange_api = DidExchangeApi(api_client=get_api_client())
out_of_band_api = OutOfBandApi(api_client=get_api_client())


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


def get_connections(params: dict) -> list[Connection]:
    """Fetch connections for the current tenant."""

    resp = connection_api.connections_get(**params)

    conn_list: ConnectionList = resp
    conns: list[ConnRecord] = conn_list.get("results")
    connections = []
    for conn in conns:
        connections.append(conn_record_to_connection(conn))

    return connections


def get_connection_with_alias(alias: str) -> Connection:
    params = {
        "alias": alias,
    }
    ret_connections = get_connections(params)
    # hack here because aca-py seems to match on alias.startswith(...)
    connections = []
    for conn in ret_connections:
        if conn.alias == alias:
            connections.append(conn)
    if 0 == len(connections):
        return None
    if 1 < len(connections):
        raise HTTPException(
            status_code=500,
            detail=f"Error multiple connections found with alias {alias}",
        )
    return connections[0]


def create_invitation(
    alias: str, invitation_type: ConnectionProtocolType
) -> Invitation:
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
        connection = get_connection_with_alias(alias)
        invitation = inv_record_to_invitation(inv, connection.connection_id)
    else:
        params = {"alias": alias}
        inv = connection_api.connections_create_invitation_post(**params)
        invitation = inv_result_to_invitation(inv)
    return invitation


def receive_invitation(
    alias: str, payload: dict = None, their_public_did: str = None
) -> Connection:
    if their_public_did:
        params = {"alias": alias}
        connection = did_exchange_api.didexchange_create_request_post(
            their_public_did, **params
        )
    elif "/out-of-band/" in payload.get("@type", ""):
        params = {"alias": alias, "body": InvitationMessage(**payload)}
        connection = out_of_band_api.out_of_band_receive_invitation_post(**params)
    else:
        params = {"alias": alias, "body": ReceiveInvitationRequest(**payload)}
        connection = connection_api.connections_receive_invitation_post(**params)
    return conn_record_to_connection(connection)


def send_basic_message(connection_id: str, content: str) -> dict:
    message = {"content": content}
    data = {"body": SendMessage(**message)}
    response = basicmessage_api.connections_conn_id_send_message_post(
        connection_id, **data
    )
    return response
