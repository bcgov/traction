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
from acapy_wrapper.models.send_message import SendMessage

from api import acapy_utils as au


router = APIRouter()


@router.post(
    "/connections/{conn_id}/send-message",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["basicmessage"],
    summary="Send a basic message to a connection",
)
async def connections_conn_id_send_message_post(
    request: Request,
    conn_id: str = Path(None, description="Connection identifier"),
    body: SendMessage = Body(None, description=""),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
