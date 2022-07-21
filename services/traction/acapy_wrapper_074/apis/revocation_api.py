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
from acapy_wrapper_074.models.clear_pending_revocations_request import (
    ClearPendingRevocationsRequest,
)
from acapy_wrapper_074.models.cred_rev_indy_records_result import (
    CredRevIndyRecordsResult,
)
from acapy_wrapper_074.models.cred_rev_record_details_result import (
    CredRevRecordDetailsResult,
)
from acapy_wrapper_074.models.cred_rev_record_result import CredRevRecordResult
from acapy_wrapper_074.models.publish_revocations import PublishRevocations
from acapy_wrapper_074.models.rev_reg_create_request import RevRegCreateRequest
from acapy_wrapper_074.models.rev_reg_issued_result import RevRegIssuedResult
from acapy_wrapper_074.models.rev_reg_result import RevRegResult
from acapy_wrapper_074.models.rev_reg_update_tails_file_uri import (
    RevRegUpdateTailsFileUri,
)
from acapy_wrapper_074.models.rev_reg_wallet_updated_result import (
    RevRegWalletUpdatedResult,
)
from acapy_wrapper_074.models.rev_regs_created import RevRegsCreated
from acapy_wrapper_074.models.revoke_request import RevokeRequest
from acapy_wrapper_074.models.txn_or_publish_revocations_result import (
    TxnOrPublishRevocationsResult,
)
from acapy_wrapper_074.models.txn_or_rev_reg_result import TxnOrRevRegResult

from api import acapy_utils as au

router = APIRouter()


@router.get(
    "/revocation/active-registry/{cred_def_id}",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Get current active revocation registry by credential definition id",
    response_model_by_alias=True,
)
async def revocation_active_registry_cred_def_id_get(
    request: Request,
    cred_def_id: str = Path(
        None,
        description="Credential definition identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$",
    ),
) -> RevRegResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/revocation/clear-pending-revocations",
    responses={
        200: {"model": PublishRevocations, "description": ""},
    },
    tags=["revocation"],
    summary="Clear pending revocations",
    response_model_by_alias=True,
)
async def revocation_clear_pending_revocations_post(
    request: Request,
    body: ClearPendingRevocationsRequest = Body(None, description=""),
) -> PublishRevocations:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/revocation/create-registry",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Creates a new revocation registry",
    response_model_by_alias=True,
)
async def revocation_create_registry_post(
    request: Request,
    body: RevRegCreateRequest = Body(None, description=""),
) -> RevRegResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/revocation/credential-record",
    responses={
        200: {"model": CredRevRecordResult, "description": ""},
    },
    tags=["revocation"],
    summary="Get credential revocation status",
    response_model_by_alias=True,
)
async def revocation_credential_record_get(
    request: Request,
    cred_ex_id: str = Query(None, description="Credential exchange identifier"),
    cred_rev_id: str = Query(
        None, description="Credential revocation identifier", regex=r"^[1-9][0-9]*$"
    ),
    rev_reg_id: str = Query(
        None,
        description="Revocation registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
) -> CredRevRecordResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/revocation/publish-revocations",
    responses={
        200: {"model": TxnOrPublishRevocationsResult, "description": ""},
    },
    tags=["revocation"],
    summary="Publish pending revocations to ledger",
    response_model_by_alias=True,
)
async def revocation_publish_revocations_post(
    request: Request,
    body: PublishRevocations = Body(None, description=""),
) -> TxnOrPublishRevocationsResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/revocation/registries/created",
    responses={
        200: {"model": RevRegsCreated, "description": ""},
    },
    tags=["revocation"],
    summary="Search for matching revocation registries that current agent created",
    response_model_by_alias=True,
)
async def revocation_registries_created_get(
    request: Request,
    cred_def_id: str = Query(
        None,
        description="Credential definition identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$",
    ),
    state: str = Query(None, description="Revocation registry state"),
) -> RevRegsCreated:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/revocation/registry/{rev_reg_id}/definition",
    responses={
        200: {"model": TxnOrRevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Send revocation registry definition to ledger",
    response_model_by_alias=True,
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
) -> TxnOrRevRegResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/revocation/registry/{rev_reg_id}/entry",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Send revocation registry entry to ledger",
    response_model_by_alias=True,
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
) -> RevRegResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.put(
    "/revocation/registry/{rev_reg_id}/fix-revocation-entry-state",
    responses={
        200: {"model": RevRegWalletUpdatedResult, "description": ""},
    },
    tags=["revocation"],
    summary="Fix revocation state in wallet and return number of updated entries",
    response_model_by_alias=True,
)
async def revocation_registry_rev_reg_id_fix_revocation_entry_state_put(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
    apply_ledger_update: bool = Query(
        None, description="Apply updated accumulator transaction to ledger"
    ),
) -> RevRegWalletUpdatedResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/revocation/registry/{rev_reg_id}",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Get revocation registry by revocation registry id",
    response_model_by_alias=True,
)
async def revocation_registry_rev_reg_id_get(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
) -> RevRegResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/revocation/registry/{rev_reg_id}/issued/details",
    responses={
        200: {"model": CredRevRecordDetailsResult, "description": ""},
    },
    tags=["revocation"],
    summary="Get details of credentials issued against revocation registry",
    response_model_by_alias=True,
)
async def revocation_registry_rev_reg_id_issued_details_get(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
) -> CredRevRecordDetailsResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/revocation/registry/{rev_reg_id}/issued",
    responses={
        200: {"model": RevRegIssuedResult, "description": ""},
    },
    tags=["revocation"],
    summary="Get number of credentials issued against revocation registry",
    response_model_by_alias=True,
)
async def revocation_registry_rev_reg_id_issued_get(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
) -> RevRegIssuedResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/revocation/registry/{rev_reg_id}/issued/indy_recs",
    responses={
        200: {"model": CredRevIndyRecordsResult, "description": ""},
    },
    tags=["revocation"],
    summary="Get details of revoked credentials from ledger",
    response_model_by_alias=True,
)
async def revocation_registry_rev_reg_id_issued_indy_recs_get(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
) -> CredRevIndyRecordsResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.patch(
    "/revocation/registry/{rev_reg_id}",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Update revocation registry with new public URI to its tails file",
    response_model_by_alias=True,
)
async def revocation_registry_rev_reg_id_patch(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
    body: RevRegUpdateTailsFileUri = Body(None, description=""),
) -> RevRegResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.patch(
    "/revocation/registry/{rev_reg_id}/set-state",
    responses={
        200: {"model": RevRegResult, "description": ""},
    },
    tags=["revocation"],
    summary="Set revocation registry state manually",
    response_model_by_alias=True,
)
async def revocation_registry_rev_reg_id_set_state_patch(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
    state: str = Query(None, description="Revocation registry state to set"),
) -> RevRegResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


"""
@router.get(
    "/revocation/registry/{rev_reg_id}/tails-file",
    responses={
        200: {"model": file, "description": "tails file"},
    },
    tags=["revocation"],
    summary="Download tails file",
    response_model_by_alias=True,
)
async def revocation_registry_rev_reg_id_tails_file_get(
    request: Request,
    rev_reg_id: str = Path(None, description="Revocation Registry identifier", regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)"),

) -> file:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text

"""


@router.put(
    "/revocation/registry/{rev_reg_id}/tails-file",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["revocation"],
    summary="Upload local tails file to server",
    response_model_by_alias=True,
)
async def revocation_registry_rev_reg_id_tails_file_put(
    request: Request,
    rev_reg_id: str = Path(
        None,
        description="Revocation Registry identifier",
        regex=r"^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)",
    ),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/revocation/revoke",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["revocation"],
    summary="Revoke an issued credential",
    response_model_by_alias=True,
)
async def revocation_revoke_post(
    request: Request,
    body: RevokeRequest = Body(None, description=""),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
