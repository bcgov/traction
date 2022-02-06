# coding: utf-8

from typing import Dict, List  # noqa: F401

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Request,
    Response,
    Security,
    status,
)

from acapy_wrapper.models.extra_models import TokenModel  # noqa: F401
from acapy_wrapper.models.conn_record import ConnRecord
from acapy_wrapper.models.connection_list import ConnectionList
from acapy_wrapper.models.connection_metadata import ConnectionMetadata
from acapy_wrapper.models.connection_metadata_set_request import (
    ConnectionMetadataSetRequest,
)
from acapy_wrapper.models.connection_static_request import ConnectionStaticRequest
from acapy_wrapper.models.connection_static_result import ConnectionStaticResult
from acapy_wrapper.models.create_invitation_request import CreateInvitationRequest
from acapy_wrapper.models.endpoints_result import EndpointsResult
from acapy_wrapper.models.invitation_result import InvitationResult
from acapy_wrapper.models.receive_invitation_request import ReceiveInvitationRequest
from acapy_wrapper.security_api import get_token_AuthorizationHeader

from api import acapy_utils as au


router = APIRouter()


@router.post(
    "/connections/{conn_id}/accept-invitation",
    responses={
        200: {"model": ConnRecord, "description": ""},
    },
    tags=["connection"],
    summary="Accept a stored connection invitation",
)
async def connections_conn_id_accept_invitation_post(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    mediation_id: str = Query(
        None,
        description="Identifier for active mediation record to be used",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    my_endpoint: str = Query(
        None,
        description="My URL endpoint",
        regex=r"^[A-Za-z0-9\.\-\+]+:\/\/([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(\/[^?&amp;#]+)?$",
    ),
    my_label: str = Query(None, description="Label for connection"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> ConnRecord:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.post(
    "/connections/{conn_id}/accept-request",
    responses={
        200: {"model": ConnRecord, "description": ""},
    },
    tags=["connection"],
    summary="Accept a stored connection request",
)
async def connections_conn_id_accept_request_post(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    my_endpoint: str = Query(
        None,
        description="My URL endpoint",
        regex=r"^[A-Za-z0-9\.\-\+]+:\/\/([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(\/[^?&amp;#]+)?$",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> ConnRecord:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.delete(
    "/connections/{conn_id}",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["connection"],
    summary="Remove an existing connection record",
)
async def connections_conn_id_delete(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> dict:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.get(
    "/connections/{conn_id}/endpoints",
    responses={
        200: {"model": EndpointsResult, "description": ""},
    },
    tags=["connection"],
    summary="Fetch connection remote endpoint",
)
async def connections_conn_id_endpoints_get(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> EndpointsResult:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.post(
    "/connections/{conn_id}/establish-inbound/{ref_id}",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["connection"],
    summary="Assign another connection as the inbound connection",
)
async def connections_conn_id_establish_inbound_ref_id_post(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    ref_id: str = Path(None, description="Inbound connection identifier"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> dict:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.get(
    "/connections/{conn_id}",
    responses={
        200: {"model": ConnRecord, "description": ""},
    },
    tags=["connection"],
    summary="Fetch a single connection record",
)
async def connections_conn_id_get(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> ConnRecord:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.get(
    "/connections/{conn_id}/metadata",
    responses={
        200: {"model": ConnectionMetadata, "description": ""},
    },
    tags=["connection"],
    summary="Fetch connection metadata",
)
async def connections_conn_id_metadata_get(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    key: str = Query(None, description="Key to retrieve."),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> ConnectionMetadata:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.post(
    "/connections/{conn_id}/metadata",
    responses={
        200: {"model": ConnectionMetadata, "description": ""},
    },
    tags=["connection"],
    summary="Set connection metadata",
)
async def connections_conn_id_metadata_post(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    body: ConnectionMetadataSetRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> ConnectionMetadata:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.post(
    "/connections/create-invitation",
    responses={
        200: {"model": InvitationResult, "description": ""},
    },
    tags=["connection"],
    summary="Create a new connection invitation",
)
async def connections_create_invitation_post(
    request: Request,
    alias: str = Query(None, description="Alias"),
    auto_accept: bool = Query(
        None, description="Auto-accept connection (defaults to configuration)"
    ),
    multi_use: bool = Query(
        None, description="Create invitation for multiple use (default false)"
    ),
    public: bool = Query(
        None, description="Create invitation from public DID (default false)"
    ),
    body: CreateInvitationRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> InvitationResult:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.post(
    "/connections/create-static",
    responses={
        200: {"model": ConnectionStaticResult, "description": ""},
    },
    tags=["connection"],
    summary="Create a new static connection",
)
async def connections_create_static_post(
    request: Request,
    body: ConnectionStaticRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> ConnectionStaticResult:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.get(
    "/connections",
    responses={
        200: {"model": ConnectionList, "description": ""},
    },
    tags=["connection"],
    summary="Query agent-to-agent connections",
)
async def connections_get(
    request: Request,
    alias: str = Query(None, description="Alias"),
    connection_protocol: str = Query(None, description="Connection protocol used"),
    invitation_key: str = Query(
        None,
        description="invitation key",
        regex=r"^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$",
    ),
    my_did: str = Query(
        None,
        description="My DID",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
    state: str = Query(None, description="Connection state"),
    their_did: str = Query(
        None,
        description="Their DID",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
    their_role: str = Query(None, description="Their role in the connection protocol"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> ConnectionList:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.post(
    "/connections/receive-invitation",
    responses={
        200: {"model": ConnRecord, "description": ""},
    },
    tags=["connection"],
    summary="Receive a new connection invitation",
)
async def connections_receive_invitation_post(
    request: Request,
    alias: str = Query(None, description="Alias"),
    auto_accept: bool = Query(
        None, description="Auto-accept connection (defaults to configuration)"
    ),
    mediation_id: str = Query(
        None,
        description="Identifier for active mediation record to be used",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: ReceiveInvitationRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> ConnRecord:
    body = None
    try:
        body = await request.json()
    except:
        pass
    path = request.url.path.replace("/tenant_acapy/", "")
    resp_text = await au.acapy_admin_request(
        request.method,
        path,
        data=body,
        text=False,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text
