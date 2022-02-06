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
from acapy_wrapper.models.admin_config import AdminConfig
from acapy_wrapper.models.admin_modules import AdminModules
from acapy_wrapper.models.admin_status import AdminStatus
from acapy_wrapper.models.admin_status_liveliness import AdminStatusLiveliness
from acapy_wrapper.models.admin_status_readiness import AdminStatusReadiness
from acapy_wrapper.models.query_result import QueryResult
from acapy_wrapper.security_api import get_token_AuthorizationHeader

from api import acapy_utils as au


router = APIRouter()


@router.get(
    "/features",
    responses={
        200: {"model": QueryResult, "description": ""},
    },
    tags=["server"],
    summary="Query supported features",
)
async def features_get(
    request: Request,
    query: str = Query(None, description="Query"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> QueryResult:
    body = await request.body()
    resp_text = await au.acapy_admin_request(
        request.method,
        request.url.path,
        data=body,
        text=True,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.get(
    "/plugins",
    responses={
        200: {"model": AdminModules, "description": ""},
    },
    tags=["server"],
    summary="Fetch the list of loaded plugins",
)
async def plugins_get(
    request: Request,
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> AdminModules:
    body = await request.body()
    resp_text = await au.acapy_admin_request(
        request.method,
        request.url.path,
        data=body,
        text=True,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.get(
    "/shutdown",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["server"],
    summary="Shut down server",
)
async def shutdown_get(
    request: Request,
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> dict:
    body = await request.body()
    resp_text = await au.acapy_admin_request(
        request.method,
        request.url.path,
        data=body,
        text=True,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.get(
    "/status/config",
    responses={
        200: {"model": AdminConfig, "description": ""},
    },
    tags=["server"],
    summary="Fetch the server configuration",
)
async def status_config_get(
    request: Request,
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> AdminConfig:
    body = await request.body()
    resp_text = await au.acapy_admin_request(
        request.method,
        request.url.path,
        data=body,
        text=True,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.get(
    "/status",
    responses={
        200: {"model": AdminStatus, "description": ""},
    },
    tags=["server"],
    summary="Fetch the server status",
)
async def status_get(
    request: Request,
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> AdminStatus:
    body = await request.body()
    resp_text = await au.acapy_admin_request(
        request.method,
        request.url.path,
        data=body,
        text=True,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.get(
    "/status/live",
    responses={
        200: {"model": AdminStatusLiveliness, "description": ""},
    },
    tags=["server"],
    summary="Liveliness check",
)
async def status_live_get(
    request: Request,
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> AdminStatusLiveliness:
    body = await request.body()
    resp_text = await au.acapy_admin_request(
        request.method,
        request.url.path,
        data=body,
        text=True,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.get(
    "/status/ready",
    responses={
        200: {"model": AdminStatusReadiness, "description": ""},
    },
    tags=["server"],
    summary="Readiness check",
)
async def status_ready_get(
    request: Request,
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> AdminStatusReadiness:
    body = await request.body()
    resp_text = await au.acapy_admin_request(
        request.method,
        request.url.path,
        data=body,
        text=True,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text


@router.post(
    "/status/reset",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["server"],
    summary="Reset statistics",
)
async def status_reset_post(
    request: Request,
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> dict:
    body = await request.body()
    resp_text = await au.acapy_admin_request(
        request.method,
        request.url.path,
        data=body,
        text=True,
        params=request.query_params,
        headers=None,
        tenant=True,
    )
    return resp_text
