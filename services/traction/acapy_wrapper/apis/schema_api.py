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
from acapy_wrapper.models.schema_get_result import SchemaGetResult
from acapy_wrapper.models.schema_send_request import SchemaSendRequest
from acapy_wrapper.models.schemas_created_result import SchemasCreatedResult
from acapy_wrapper.models.txn_or_schema_send_result import TxnOrSchemaSendResult
from acapy_wrapper.security_api import get_token_AuthorizationHeader

from api import acapy_utils as au


router = APIRouter()


@router.get(
    "/schemas/created",
    responses={
        200: {"model": SchemasCreatedResult, "description": ""},
    },
    tags=["schema"],
    summary="Search for matching schema that agent originated",
)
async def schemas_created_get(
    request: Request,
    schema_id: str = Query(
        None,
        description="Schema identifier",
        regex=r"^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$",
    ),
    schema_issuer_did: str = Query(
        None,
        description="Schema issuer DID",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
    schema_name: str = Query(None, description="Schema name"),
    schema_version: str = Query(None, description="Schema version", regex=r"^[0-9.]+$"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> SchemasCreatedResult:
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
    "/schemas",
    responses={
        200: {"model": TxnOrSchemaSendResult, "description": ""},
    },
    tags=["schema"],
    summary="Sends a schema to the ledger",
)
async def schemas_post(
    request: Request,
    conn_id: str = Query(None, description="Connection identifier"),
    create_transaction_for_endorser: bool = Query(
        None, description="Create Transaction For Endorser&#39;s signature"
    ),
    body: SchemaSendRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> TxnOrSchemaSendResult:
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
    "/schemas/{schema_id}",
    responses={
        200: {"model": SchemaGetResult, "description": ""},
    },
    tags=["schema"],
    summary="Gets a schema from the ledger",
)
async def schemas_schema_id_get(
    request: Request,
    schema_id: str = Path(
        None,
        description="Schema identifier",
        regex=r"^[1-9][0-9]*|[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> SchemaGetResult:
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
    "/schemas/{schema_id}/write_record",
    responses={
        200: {"model": SchemaGetResult, "description": ""},
    },
    tags=["schema"],
    summary="Writes a schema non-secret record to the wallet",
)
async def schemas_schema_id_write_record_post(
    request: Request,
    schema_id: str = Path(
        None,
        description="Schema identifier",
        regex=r"^[1-9][0-9]*|[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> SchemaGetResult:
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
