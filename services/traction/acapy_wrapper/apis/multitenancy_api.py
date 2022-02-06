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
from acapy_wrapper.models.create_wallet_request import CreateWalletRequest
from acapy_wrapper.models.create_wallet_response import CreateWalletResponse
from acapy_wrapper.models.create_wallet_token_request import CreateWalletTokenRequest
from acapy_wrapper.models.create_wallet_token_response import CreateWalletTokenResponse
from acapy_wrapper.models.remove_wallet_request import RemoveWalletRequest
from acapy_wrapper.models.update_wallet_request import UpdateWalletRequest
from acapy_wrapper.models.wallet_list import WalletList
from acapy_wrapper.models.wallet_record import WalletRecord
from acapy_wrapper.security_api import get_token_AuthorizationHeader

from api import acapy_utils as au


router = APIRouter()


@router.post(
    "/multitenancy/wallet",
    responses={
        200: {"model": CreateWalletResponse, "description": ""},
    },
    tags=["multitenancy"],
    summary="Create a subwallet",
)
async def multitenancy_wallet_post(
    request: Request,
    body: CreateWalletRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> CreateWalletResponse:
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
    "/multitenancy/wallet/{wallet_id}",
    responses={
        200: {"model": WalletRecord, "description": ""},
    },
    tags=["multitenancy"],
    summary="Get a single subwallet",
)
async def multitenancy_wallet_wallet_id_get(
    request: Request,
    wallet_id: str = Path(None, description="Subwallet identifier"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> WalletRecord:
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


@router.put(
    "/multitenancy/wallet/{wallet_id}",
    responses={
        200: {"model": WalletRecord, "description": ""},
    },
    tags=["multitenancy"],
    summary="Update a subwallet",
)
async def multitenancy_wallet_wallet_id_put(
    request: Request,
    wallet_id: str = Path(None, description="Subwallet identifier"),
    body: UpdateWalletRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> WalletRecord:
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
    "/multitenancy/wallet/{wallet_id}/remove",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["multitenancy"],
    summary="Remove a subwallet",
)
async def multitenancy_wallet_wallet_id_remove_post(
    request: Request,
    wallet_id: str = Path(None, description="Subwallet identifier"),
    body: RemoveWalletRequest = Body(None, description=""),
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


@router.post(
    "/multitenancy/wallet/{wallet_id}/token",
    responses={
        200: {"model": CreateWalletTokenResponse, "description": ""},
    },
    tags=["multitenancy"],
    summary="Get auth token for a subwallet",
)
async def multitenancy_wallet_wallet_id_token_post(
    request: Request,
    wallet_id: str = Path(None, description=""),
    body: CreateWalletTokenRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> CreateWalletTokenResponse:
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
    "/multitenancy/wallets",
    responses={
        200: {"model": WalletList, "description": ""},
    },
    tags=["multitenancy"],
    summary="Query subwallets",
)
async def multitenancy_wallets_get(
    request: Request,
    wallet_name: str = Query(None, description="Wallet name"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> WalletList:
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
