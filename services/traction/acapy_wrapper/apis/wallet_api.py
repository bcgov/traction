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
from acapy_wrapper.models.did_create import DIDCreate
from acapy_wrapper.models.did_endpoint import DIDEndpoint
from acapy_wrapper.models.did_endpoint_with_type import DIDEndpointWithType
from acapy_wrapper.models.did_list import DIDList
from acapy_wrapper.models.did_result import DIDResult
from acapy_wrapper.security_api import get_token_AuthorizationHeader

from api import acapy_utils as au


router = APIRouter()


@router.post(
    "/wallet/did/create",
    responses={
        200: {"model": DIDResult, "description": ""},
    },
    tags=["wallet"],
    summary="Create a local DID",
)
async def wallet_did_create_post(
    request: Request,
    body: DIDCreate = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> DIDResult:
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
    "/wallet/did",
    responses={
        200: {"model": DIDList, "description": ""},
    },
    tags=["wallet"],
    summary="List wallet DIDs",
)
async def wallet_did_get(
    request: Request,
    did: str = Query(
        None,
        description="DID of interest",
        regex=r"^did:key:z[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+$|^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
    key_type: str = Query(None, description="Key type to query for."),
    method: str = Query(
        None,
        description="DID method to query for. e.g. sov to only fetch indy/sov DIDs",
    ),
    posture: str = Query(
        None,
        description="Whether DID is current public DID, posted to ledger but current public DID, or local to the wallet",
    ),
    verkey: str = Query(
        None,
        description="Verification key of interest",
        regex=r"^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> DIDList:
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


@router.patch(
    "/wallet/did/local/rotate-keypair",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["wallet"],
    summary="Rotate keypair for a DID not posted to the ledger",
)
async def wallet_did_local_rotate_keypair_patch(
    request: Request,
    did: str = Query(
        None,
        description="DID of interest",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
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
    "/wallet/did/public",
    responses={
        200: {"model": DIDResult, "description": ""},
    },
    tags=["wallet"],
    summary="Fetch the current public DID",
)
async def wallet_did_public_get(
    request: Request,
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> DIDResult:
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
    "/wallet/did/public",
    responses={
        200: {"model": DIDResult, "description": ""},
    },
    tags=["wallet"],
    summary="Assign the current public DID",
)
async def wallet_did_public_post(
    request: Request,
    did: str = Query(
        None,
        description="DID of interest",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> DIDResult:
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
    "/wallet/get-did-endpoint",
    responses={
        200: {"model": DIDEndpoint, "description": ""},
    },
    tags=["wallet"],
    summary="Query DID endpoint in wallet",
)
async def wallet_get_did_endpoint_get(
    request: Request,
    did: str = Query(
        None,
        description="DID of interest",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> DIDEndpoint:
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
    "/wallet/set-did-endpoint",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["wallet"],
    summary="Update endpoint in wallet and on ledger if posted to it",
)
async def wallet_set_did_endpoint_post(
    request: Request,
    body: DIDEndpointWithType = Body(None, description=""),
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
