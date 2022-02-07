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
from acapy_wrapper.models.sign_request import SignRequest
from acapy_wrapper.models.sign_response import SignResponse
from acapy_wrapper.models.verify_request import VerifyRequest
from acapy_wrapper.models.verify_response import VerifyResponse

from api import acapy_utils as au


router = APIRouter()


@router.post(
    "/jsonld/sign",
    responses={
        200: {"model": SignResponse, "description": ""},
    },
    tags=["jsonld"],
    summary="Sign a JSON-LD structure and return it",
)
async def jsonld_sign_post(
    request: Request,
    body: SignRequest = Body(None, description=""),
) -> SignResponse:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/jsonld/verify",
    responses={
        200: {"model": VerifyResponse, "description": ""},
    },
    tags=["jsonld"],
    summary="Verify a JSON-LD structure.",
)
async def jsonld_verify_post(
    request: Request,
    body: VerifyRequest = Body(None, description=""),
) -> VerifyResponse:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
