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
from acapy_wrapper.models.v20_cred_bound_offer_request import V20CredBoundOfferRequest
from acapy_wrapper.models.v20_cred_ex_free import V20CredExFree
from acapy_wrapper.models.v20_cred_ex_record import V20CredExRecord
from acapy_wrapper.models.v20_cred_ex_record_detail import V20CredExRecordDetail
from acapy_wrapper.models.v20_cred_ex_record_list_result import (
    V20CredExRecordListResult,
)
from acapy_wrapper.models.v20_cred_issue_problem_report_request import (
    V20CredIssueProblemReportRequest,
)
from acapy_wrapper.models.v20_cred_issue_request import V20CredIssueRequest
from acapy_wrapper.models.v20_cred_offer_conn_free_request import (
    V20CredOfferConnFreeRequest,
)
from acapy_wrapper.models.v20_cred_offer_request import V20CredOfferRequest
from acapy_wrapper.models.v20_cred_request_free import V20CredRequestFree
from acapy_wrapper.models.v20_cred_request_request import V20CredRequestRequest
from acapy_wrapper.models.v20_cred_store_request import V20CredStoreRequest
from acapy_wrapper.models.v20_issue_cred_schema_core import V20IssueCredSchemaCore
from acapy_wrapper.security_api import get_token_AuthorizationHeader

from api import acapy_utils as au


router = APIRouter()


@router.post(
    "/issue-credential-2.0/create-offer",
    responses={
        200: {"model": V20CredExRecord, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Create a credential offer, independent of any proposal or connection",
)
async def issue_credential20_create_offer_post(
    request: Request,
    body: V20CredOfferConnFreeRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecord:
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
    "/issue-credential-2.0/create",
    responses={
        200: {"model": V20CredExRecord, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Create credential from attribute values",
)
async def issue_credential20_create_post(
    request: Request,
    body: V20IssueCredSchemaCore = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecord:
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


@router.delete(
    "/issue-credential-2.0/records/{cred_ex_id}",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Remove an existing credential exchange record",
)
async def issue_credential20_records_cred_ex_id_delete(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
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
    "/issue-credential-2.0/records/{cred_ex_id}",
    responses={
        200: {"model": V20CredExRecordDetail, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Fetch a single credential exchange record",
)
async def issue_credential20_records_cred_ex_id_get(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecordDetail:
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
    "/issue-credential-2.0/records/{cred_ex_id}/issue",
    responses={
        200: {"model": V20CredExRecordDetail, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Send holder a credential",
)
async def issue_credential20_records_cred_ex_id_issue_post(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: V20CredIssueRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecordDetail:
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
    "/issue-credential-2.0/records/{cred_ex_id}/problem-report",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Send a problem report for credential exchange",
)
async def issue_credential20_records_cred_ex_id_problem_report_post(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: V20CredIssueProblemReportRequest = Body(None, description=""),
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
    "/issue-credential-2.0/records/{cred_ex_id}/send-offer",
    responses={
        200: {"model": V20CredExRecord, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Send holder a credential offer in reference to a proposal with preview",
)
async def issue_credential20_records_cred_ex_id_send_offer_post(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: V20CredBoundOfferRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecord:
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
    "/issue-credential-2.0/records/{cred_ex_id}/send-request",
    responses={
        200: {"model": V20CredExRecord, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Send issuer a credential request",
)
async def issue_credential20_records_cred_ex_id_send_request_post(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: V20CredRequestRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecord:
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
    "/issue-credential-2.0/records/{cred_ex_id}/store",
    responses={
        200: {"model": V20CredExRecordDetail, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Store a received credential",
)
async def issue_credential20_records_cred_ex_id_store_post(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: V20CredStoreRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecordDetail:
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
    "/issue-credential-2.0/records",
    responses={
        200: {"model": V20CredExRecordListResult, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Fetch all credential exchange records",
)
async def issue_credential20_records_get(
    request: Request,
    connection_id: str = Query(None, description="Connection identifier"),
    role: str = Query(None, description="Role assigned in credential exchange"),
    state: str = Query(None, description="Credential exchange state"),
    thread_id: str = Query(None, description="Thread identifier"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecordListResult:
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
    "/issue-credential-2.0/send-offer",
    responses={
        200: {"model": V20CredExRecord, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Send holder a credential offer, independent of any proposal",
)
async def issue_credential20_send_offer_post(
    request: Request,
    body: V20CredOfferRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecord:
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
    "/issue-credential-2.0/send",
    responses={
        200: {"model": V20CredExRecord, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Send holder a credential, automating entire flow",
)
async def issue_credential20_send_post(
    request: Request,
    body: V20CredExFree = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecord:
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
    "/issue-credential-2.0/send-proposal",
    responses={
        200: {"model": V20CredExRecord, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Send issuer a credential proposal",
)
async def issue_credential20_send_proposal_post(
    request: Request,
    body: V20CredExFree = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecord:
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
    "/issue-credential-2.0/send-request",
    responses={
        200: {"model": V20CredExRecord, "description": ""},
    },
    tags=["issue-credential v2.0"],
    summary="Send issuer a credential request not bound to an existing thread. Indy credentials cannot start at a request",
)
async def issue_credential20_send_request_post(
    request: Request,
    body: V20CredRequestFree = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V20CredExRecord:
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
