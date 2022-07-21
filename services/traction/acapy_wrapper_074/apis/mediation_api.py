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
    Response,
    Request,
    Security,
    status,
)

from acapy_wrapper_074.models.extra_models import TokenModel  # noqa: F401
from acapy_wrapper_074.models.admin_mediation_deny import AdminMediationDeny
from acapy_wrapper_074.models.keylist import Keylist
from acapy_wrapper_074.models.keylist_query import KeylistQuery
from acapy_wrapper_074.models.keylist_query_filter_request import (
    KeylistQueryFilterRequest,
)
from acapy_wrapper_074.models.keylist_update import KeylistUpdate
from acapy_wrapper_074.models.keylist_update_request import KeylistUpdateRequest
from acapy_wrapper_074.models.mediation_create_request import MediationCreateRequest
from acapy_wrapper_074.models.mediation_deny import MediationDeny
from acapy_wrapper_074.models.mediation_grant import MediationGrant
from acapy_wrapper_074.models.mediation_list import MediationList
from acapy_wrapper_074.models.mediation_record import MediationRecord

from api import acapy_utils as au

router = APIRouter()


@router.delete(
    "/mediation/default-mediator",
    responses={
        201: {"model": MediationRecord, "description": ""},
    },
    tags=["mediation"],
    summary="Clear default mediator",
    response_model_by_alias=True,
)
async def mediation_default_mediator_delete(
    request: Request,
) -> MediationRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/mediation/default-mediator",
    responses={
        200: {"model": MediationRecord, "description": ""},
    },
    tags=["mediation"],
    summary="Get default mediator",
    response_model_by_alias=True,
)
async def mediation_default_mediator_get(
    request: Request,
) -> MediationRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/mediation/keylists",
    responses={
        200: {"model": Keylist, "description": ""},
    },
    tags=["mediation"],
    summary="Retrieve keylists by connection or role",
    response_model_by_alias=True,
)
async def mediation_keylists_get(
    request: Request,
    conn_id: str = Query(None, description="Connection identifier (optional)"),
    role: str = Query(
        "server",
        description="Filer on role, &#39;client&#39; for keys         mediated by other agents, &#39;server&#39; for keys         mediated by this agent",
    ),
) -> Keylist:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/mediation/keylists/{mediation_id}/send-keylist-query",
    responses={
        201: {"model": KeylistQuery, "description": ""},
    },
    tags=["mediation"],
    summary="Send keylist query to mediator",
    response_model_by_alias=True,
)
async def mediation_keylists_mediation_id_send_keylist_query_post(
    request: Request,
    mediation_id: str = Path(None, description="Mediation record identifier"),
    paginate_limit: int = Query(-1, description="limit number of results"),
    paginate_offset: int = Query(0, description="offset to use in pagination"),
    body: KeylistQueryFilterRequest = Body(None, description=""),
) -> KeylistQuery:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/mediation/keylists/{mediation_id}/send-keylist-update",
    responses={
        201: {"model": KeylistUpdate, "description": ""},
    },
    tags=["mediation"],
    summary="Send keylist update to mediator",
    response_model_by_alias=True,
)
async def mediation_keylists_mediation_id_send_keylist_update_post(
    request: Request,
    mediation_id: str = Path(None, description="Mediation record identifier"),
    body: KeylistUpdateRequest = Body(None, description=""),
) -> KeylistUpdate:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.put(
    "/mediation/{mediation_id}/default-mediator",
    responses={
        201: {"model": MediationRecord, "description": ""},
    },
    tags=["mediation"],
    summary="Set default mediator",
    response_model_by_alias=True,
)
async def mediation_mediation_id_default_mediator_put(
    request: Request,
    mediation_id: str = Path(None, description="Mediation record identifier"),
) -> MediationRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/mediation/request/{conn_id}",
    responses={
        201: {"model": MediationRecord, "description": ""},
    },
    tags=["mediation"],
    summary="Request mediation from connection",
    response_model_by_alias=True,
)
async def mediation_request_conn_id_post(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    body: MediationCreateRequest = Body(None, description=""),
) -> MediationRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/mediation/requests",
    responses={
        200: {"model": MediationList, "description": ""},
    },
    tags=["mediation"],
    summary="Query mediation requests, returns list of all mediation records",
    response_model_by_alias=True,
)
async def mediation_requests_get(
    request: Request,
    conn_id: str = Query(None, description="Connection identifier (optional)"),
    mediator_terms: List[str] = Query(
        None, description="List of mediator rules for recipient"
    ),
    recipient_terms: List[str] = Query(
        None, description="List of recipient rules for mediation"
    ),
    state: str = Query(None, description="Mediation state (optional)"),
) -> MediationList:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.delete(
    "/mediation/requests/{mediation_id}",
    responses={
        200: {"model": MediationRecord, "description": ""},
    },
    tags=["mediation"],
    summary="Delete mediation request by ID",
    response_model_by_alias=True,
)
async def mediation_requests_mediation_id_delete(
    request: Request,
    mediation_id: str = Path(None, description="Mediation record identifier"),
) -> MediationRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/mediation/requests/{mediation_id}/deny",
    responses={
        201: {"model": MediationDeny, "description": ""},
    },
    tags=["mediation"],
    summary="Deny a stored mediation request",
    response_model_by_alias=True,
)
async def mediation_requests_mediation_id_deny_post(
    request: Request,
    mediation_id: str = Path(None, description="Mediation record identifier"),
    body: AdminMediationDeny = Body(None, description=""),
) -> MediationDeny:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/mediation/requests/{mediation_id}",
    responses={
        200: {"model": MediationRecord, "description": ""},
    },
    tags=["mediation"],
    summary="Retrieve mediation request record",
    response_model_by_alias=True,
)
async def mediation_requests_mediation_id_get(
    request: Request,
    mediation_id: str = Path(None, description="Mediation record identifier"),
) -> MediationRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/mediation/requests/{mediation_id}/grant",
    responses={
        201: {"model": MediationGrant, "description": ""},
    },
    tags=["mediation"],
    summary="Grant received mediation",
    response_model_by_alias=True,
)
async def mediation_requests_mediation_id_grant_post(
    request: Request,
    mediation_id: str = Path(None, description="Mediation record identifier"),
) -> MediationGrant:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
