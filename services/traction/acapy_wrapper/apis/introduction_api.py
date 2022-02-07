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

from api import acapy_utils as au


router = APIRouter()


@router.post(
    "/connections/{conn_id}/start-introduction",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["introduction"],
    summary="Start an introduction between two connections",
)
async def connections_conn_id_start_introduction_post(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    target_connection_id: str = Query(None, description="Target connection identifier"),
    message: str = Query(None, description="Message"),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
