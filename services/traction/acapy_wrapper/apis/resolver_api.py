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
from acapy_wrapper.models.resolution_result import ResolutionResult

from api import acapy_utils as au


router = APIRouter()


@router.get(
    "/resolver/resolve/{did}",
    responses={
        200: {"model": ResolutionResult, "description": "null"},
    },
    tags=["resolver"],
    summary="Retrieve doc for requested did",
)
async def resolver_resolve_did_get(
    request: Request,
    did: str = Path(
        None,
        description="DID",
        regex=r"^did:([a-z0-9]+):((?:[a-zA-Z0-9._%-]*:)*[a-zA-Z0-9._%-]+)$",
    ),
) -> ResolutionResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
