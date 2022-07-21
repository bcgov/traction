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
from acapy_wrapper_074.models.resolution_result import ResolutionResult

from api import acapy_utils as au

router = APIRouter()


@router.get(
    "/resolver/resolve/{did}",
    responses={
        200: {"model": ResolutionResult, "description": ""},
    },
    tags=["resolver"],
    summary="Retrieve doc for requested did",
    response_model_by_alias=True,
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
