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
from acapy_wrapper.models.credential_definition_get_result import (
    CredentialDefinitionGetResult,
)
from acapy_wrapper.models.credential_definition_send_request import (
    CredentialDefinitionSendRequest,
)
from acapy_wrapper.models.credential_definitions_created_result import (
    CredentialDefinitionsCreatedResult,
)
from acapy_wrapper.models.txn_or_credential_definition_send_result import (
    TxnOrCredentialDefinitionSendResult,
)

from api import acapy_utils as au


router = APIRouter()


@router.get(
    "/credential-definitions/created",
    responses={
        200: {"model": CredentialDefinitionsCreatedResult, "description": ""},
    },
    tags=["credential-definition"],
    summary="Search for matching credential definitions that agent originated",
)
async def credential_definitions_created_get(
    request: Request,
    cred_def_id: str = Query(
        None,
        description="Credential definition id",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$",
    ),
    issuer_did: str = Query(
        None,
        description="Issuer DID",
        regex=r"^(did:sov:)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$",
    ),
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
) -> CredentialDefinitionsCreatedResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/credential-definitions/{cred_def_id}",
    responses={
        200: {"model": CredentialDefinitionGetResult, "description": ""},
    },
    tags=["credential-definition"],
    summary="Gets a credential definition from the ledger",
)
async def credential_definitions_cred_def_id_get(
    request: Request,
    cred_def_id: str = Path(
        None,
        description="Credential definition identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$",
    ),
) -> CredentialDefinitionGetResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/credential-definitions/{cred_def_id}/write_record",
    responses={
        200: {"model": CredentialDefinitionGetResult, "description": ""},
    },
    tags=["credential-definition"],
    summary="Writes a credential definition non-secret record to the wallet",
)
async def credential_definitions_cred_def_id_write_record_post(
    request: Request,
    cred_def_id: str = Path(
        None,
        description="Credential definition identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$",
    ),
) -> CredentialDefinitionGetResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/credential-definitions",
    responses={
        200: {"model": TxnOrCredentialDefinitionSendResult, "description": ""},
    },
    tags=["credential-definition"],
    summary="Sends a credential definition to the ledger",
)
async def credential_definitions_post(
    request: Request,
    conn_id: str = Query(None, description="Connection identifier"),
    create_transaction_for_endorser: bool = Query(
        None, description="Create Transaction For Endorser&#39;s signature"
    ),
    body: CredentialDefinitionSendRequest = Body(None, description=""),
) -> TxnOrCredentialDefinitionSendResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
