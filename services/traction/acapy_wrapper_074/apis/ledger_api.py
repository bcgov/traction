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
from acapy_wrapper_074.models.get_did_endpoint_response import GetDIDEndpointResponse
from acapy_wrapper_074.models.get_did_verkey_response import GetDIDVerkeyResponse
from acapy_wrapper_074.models.get_nym_role_response import GetNymRoleResponse
from acapy_wrapper_074.models.ledger_config_list import LedgerConfigList
from acapy_wrapper_074.models.taa_accept import TAAAccept
from acapy_wrapper_074.models.taa_result import TAAResult
from acapy_wrapper_074.models.txn_or_register_ledger_nym_response import (
    TxnOrRegisterLedgerNymResponse,
)
from acapy_wrapper_074.models.write_ledger_request import WriteLedgerRequest

from api import acapy_utils as au

router = APIRouter()


@router.get(
    "/ledger/did-endpoint",
    responses={
        200: {"model": GetDIDEndpointResponse, "description": ""},
    },
    tags=["ledger"],
    summary="Get the endpoint for a DID from the ledger.",
    response_model_by_alias=True,
)
async def ledger_did_endpoint_get(
    request: Request,
    did: str = Query(
        None,
        description="DID of interest",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
    endpoint_type: str = Query(
        None, description="Endpoint type of interest (default &#39;Endpoint&#39;)"
    ),
) -> GetDIDEndpointResponse:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/ledger/did-verkey",
    responses={
        200: {"model": GetDIDVerkeyResponse, "description": ""},
    },
    tags=["ledger"],
    summary="Get the verkey for a DID from the ledger.",
    response_model_by_alias=True,
)
async def ledger_did_verkey_get(
    request: Request,
    did: str = Query(
        None,
        description="DID of interest",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
) -> GetDIDVerkeyResponse:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/ledger/get-nym-role",
    responses={
        200: {"model": GetNymRoleResponse, "description": ""},
    },
    tags=["ledger"],
    summary="Get the role from the NYM registration of a public DID.",
    response_model_by_alias=True,
)
async def ledger_get_nym_role_get(
    request: Request,
    did: str = Query(
        None,
        description="DID of interest",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
) -> GetNymRoleResponse:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/ledger/multiple/config",
    responses={
        200: {"model": LedgerConfigList, "description": ""},
    },
    tags=["ledger"],
    summary="Fetch the multiple ledger configuration currently in use",
    response_model_by_alias=True,
)
async def ledger_multiple_config_get(
    request: Request,
) -> LedgerConfigList:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/ledger/multiple/get-write-ledger",
    responses={
        200: {"model": WriteLedgerRequest, "description": ""},
    },
    tags=["ledger"],
    summary="Fetch the current write ledger",
    response_model_by_alias=True,
)
async def ledger_multiple_get_write_ledger_get(
    request: Request,
) -> WriteLedgerRequest:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/ledger/register-nym",
    responses={
        200: {"model": TxnOrRegisterLedgerNymResponse, "description": ""},
    },
    tags=["ledger"],
    summary="Send a NYM registration to the ledger.",
    response_model_by_alias=True,
)
async def ledger_register_nym_post(
    request: Request,
    did: str = Query(
        None,
        description="DID to register",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
    verkey: str = Query(
        None,
        description="Verification key",
        regex=r"^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$",
    ),
    alias: str = Query(None, description="Alias"),
    conn_id: str = Query(None, description="Connection identifier"),
    create_transaction_for_endorser: bool = Query(
        None, description="Create Transaction For Endorser&#39;s signature"
    ),
    role: str = Query(None, description="Role"),
) -> TxnOrRegisterLedgerNymResponse:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.patch(
    "/ledger/rotate-public-did-keypair",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["ledger"],
    summary="Rotate key pair for public DID.",
    response_model_by_alias=True,
)
async def ledger_rotate_public_did_keypair_patch(
    request: Request,
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/ledger/taa/accept",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["ledger"],
    summary="Accept the transaction author agreement",
    response_model_by_alias=True,
)
async def ledger_taa_accept_post(
    request: Request,
    body: TAAAccept = Body(None, description=""),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/ledger/taa",
    responses={
        200: {"model": TAAResult, "description": ""},
    },
    tags=["ledger"],
    summary="Fetch the current transaction author agreement, if any",
    response_model_by_alias=True,
)
async def ledger_taa_get(
    request: Request,
) -> TAAResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
