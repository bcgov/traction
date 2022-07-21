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
from acapy_wrapper_074.models.admin_config import AdminConfig
from acapy_wrapper_074.models.admin_modules import AdminModules
from acapy_wrapper_074.models.admin_status import AdminStatus
from acapy_wrapper_074.models.admin_status_liveliness import AdminStatusLiveliness
from acapy_wrapper_074.models.admin_status_readiness import AdminStatusReadiness

from api import acapy_utils as au

router = APIRouter()


@router.get(
    "/plugins",
    responses={
        200: {"model": AdminModules, "description": ""},
    },
    tags=["server"],
    summary="Fetch the list of loaded plugins",
    response_model_by_alias=True,
)
async def plugins_get(
    request: Request,
) -> AdminModules:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/shutdown",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["server"],
    summary="Shut down server",
    response_model_by_alias=True,
)
async def shutdown_get(
    request: Request,
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/status/config",
    responses={
        200: {"model": AdminConfig, "description": ""},
    },
    tags=["server"],
    summary="Fetch the server configuration",
    response_model_by_alias=True,
)
async def status_config_get(
    request: Request,
) -> AdminConfig:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/status",
    responses={
        200: {"model": AdminStatus, "description": ""},
    },
    tags=["server"],
    summary="Fetch the server status",
    response_model_by_alias=True,
)
async def status_get(
    request: Request,
) -> AdminStatus:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/status/live",
    responses={
        200: {"model": AdminStatusLiveliness, "description": ""},
    },
    tags=["server"],
    summary="Liveliness check",
    response_model_by_alias=True,
)
async def status_live_get(
    request: Request,
) -> AdminStatusLiveliness:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/status/ready",
    responses={
        200: {"model": AdminStatusReadiness, "description": ""},
    },
    tags=["server"],
    summary="Readiness check",
    response_model_by_alias=True,
)
async def status_ready_get(
    request: Request,
) -> AdminStatusReadiness:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/status/reset",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["server"],
    summary="Reset statistics",
    response_model_by_alias=True,
)
async def status_reset_post(
    request: Request,
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
