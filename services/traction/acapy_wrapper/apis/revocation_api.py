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
from acapy_wrapper.models.clear_pending_revocations_request import (
    ClearPendingRevocationsRequest,
)
from acapy_wrapper.models.cred_rev_record_result import CredRevRecordResult
from acapy_wrapper.models.publish_revocations import PublishRevocations
from acapy_wrapper.models.rev_reg_create_request import RevRegCreateRequest
from acapy_wrapper.models.rev_reg_issued_result import RevRegIssuedResult
from acapy_wrapper.models.rev_reg_result import RevRegResult
from acapy_wrapper.models.rev_reg_update_tails_file_uri import RevRegUpdateTailsFileUri
from acapy_wrapper.models.rev_regs_created import RevRegsCreated
from acapy_wrapper.models.revoke_request import RevokeRequest
from acapy_wrapper.models.txn_or_publish_revocations_result import (
    TxnOrPublishRevocationsResult,
)
from acapy_wrapper.models.txn_or_rev_reg_result import TxnOrRevRegResult
from acapy_wrapper.security_api import get_token_AuthorizationHeader

from api import acapy_utils as au


router = APIRouter()


@router.get(
    "/revocation/active-registry/{cred_def_id}",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Get current active revocation registry by credential definition id",
)
async def revocation_active_registry_cred_def_id_get(
    request: Request,
    cred_def_id: str = Path(
        None,
        description="Credential definition identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> RevRegResult:
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
    "/revocation/clear-pending-revocations",
    responses={
        200: {"model": PublishRevocations, "description": ""},
    },
    tags=["revocation"],
    summary="Clear pending revocations",
)
async def revocation_clear_pending_revocations_post(
    request: Request,
    body: ClearPendingRevocationsRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> PublishRevocations:
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
    "/revocation/create-registry",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Creates a new revocation registry",
)
async def revocation_create_registry_post(
    request: Request,
    body: RevRegCreateRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> RevRegResult:
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
    "/revocation/credential-record",
    responses={
        200: {"model": CredRevRecordResult, "description": ""},
    },
    tags=["revocation"],
    summary="Get credential revocation status",
)
async def revocation_credential_record_get(
    request: Request,
    cred_ex_id: str = Query(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    cred_rev_id: str = Query(
        None, description="Credential revocation identifier", regex=r"^[1-9][0-9]*$"
    ),
    rev_reg_id: str = Query(
        None,
        description="Revocation registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> CredRevRecordResult:
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
    "/revocation/publish-revocations",
    responses={
        200: {"model": TxnOrPublishRevocationsResult, "description": ""},
    },
    tags=["revocation"],
    summary="Publish pending revocations to ledger",
)
async def revocation_publish_revocations_post(
    request: Request,
    body: PublishRevocations = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> TxnOrPublishRevocationsResult:
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
    "/revocation/registries/created",
    responses={
        200: {"model": RevRegsCreated, "description": ""},
    },
    tags=["revocation"],
    summary="Search for matching revocation registries that current agent created",
)
async def revocation_registries_created_get(
    request: Request,
    cred_def_id: str = Query(
        None,
        description="Credential definition identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$",
    ),
    state: str = Query(None, description="Revocation registry state"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> RevRegsCreated:
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
    "/revocation/registry/{rev_reg_id}/definition",
    responses={
        200: {"model": TxnOrRevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Send revocation registry definition to ledger",
)
async def revocation_registry_rev_reg_id_definition_post(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
    conn_id: str = Query(None, description="Connection identifier"),
    create_transaction_for_endorser: bool = Query(
        None, description="Create Transaction For Endorser&#39;s signature"
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> TxnOrRevRegResult:
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
    "/revocation/registry/{rev_reg_id}/entry",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Send revocation registry entry to ledger",
)
async def revocation_registry_rev_reg_id_entry_post(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
    conn_id: str = Query(None, description="Connection identifier"),
    create_transaction_for_endorser: bool = Query(
        None, description="Create Transaction For Endorser&#39;s signature"
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> RevRegResult:
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
    "/revocation/registry/{rev_reg_id}",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Get revocation registry by revocation registry id",
)
async def revocation_registry_rev_reg_id_get(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> RevRegResult:
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
    "/revocation/registry/{rev_reg_id}/issued",
    responses={
        200: {"model": RevRegIssuedResult, "description": ""},
    },
    tags=["revocation"],
    summary="Get number of credentials issued against revocation registry",
)
async def revocation_registry_rev_reg_id_issued_get(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> RevRegIssuedResult:
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
    "/revocation/registry/{rev_reg_id}",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Update revocation registry with new public URI to its tails file",
)
async def revocation_registry_rev_reg_id_patch(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
    body: RevRegUpdateTailsFileUri = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> RevRegResult:
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
    "/revocation/registry/{rev_reg_id}/set-state",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Set revocation registry state manually",
)
async def revocation_registry_rev_reg_id_set_state_patch(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
    state: str = Query(None, description="Revocation registry state to set"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> RevRegResult:
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


"""
@router.get(
    "/revocation/registry/{rev_reg_id}/tails-file",
    responses={
        200: {"model": file, "description": "tails file"},
    },
    tags=["revocation"],
    summary="Download tails file",
)
async def revocation_registry_rev_reg_id_tails_file_get(
    rev_reg_id: str = Path(None, description="Revocation Registry identifier", regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)"),
    token_AuthorizationHeader: TokenModel = Security(
        get_token_AuthorizationHeader
    ),
) -> file:
    ...
"""


@router.put(
    "/revocation/registry/{rev_reg_id}/tails-file",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["revocation"],
    summary="Upload local tails file to server",
)
async def revocation_registry_rev_reg_id_tails_file_put(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
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


@router.post(
    "/revocation/revoke",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["revocation"],
    summary="Revoke an issued credential",
)
async def revocation_revoke_post(
    request: Request,
    body: RevokeRequest = Body(None, description=""),
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
