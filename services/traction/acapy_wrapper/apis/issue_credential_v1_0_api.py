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
from acapy_wrapper.models.v10_credential_bound_offer_request import (
    V10CredentialBoundOfferRequest,
)
from acapy_wrapper.models.v10_credential_conn_free_offer_request import (
    V10CredentialConnFreeOfferRequest,
)
from acapy_wrapper.models.v10_credential_create import V10CredentialCreate
from acapy_wrapper.models.v10_credential_exchange import V10CredentialExchange
from acapy_wrapper.models.v10_credential_exchange_list_result import (
    V10CredentialExchangeListResult,
)
from acapy_wrapper.models.v10_credential_free_offer_request import (
    V10CredentialFreeOfferRequest,
)
from acapy_wrapper.models.v10_credential_issue_request import V10CredentialIssueRequest
from acapy_wrapper.models.v10_credential_problem_report_request import (
    V10CredentialProblemReportRequest,
)
from acapy_wrapper.models.v10_credential_proposal_request_mand import (
    V10CredentialProposalRequestMand,
)
from acapy_wrapper.models.v10_credential_proposal_request_opt import (
    V10CredentialProposalRequestOpt,
)
from acapy_wrapper.models.v10_credential_store_request import V10CredentialStoreRequest

from api import acapy_utils as au


router = APIRouter()


@router.post(
    "/issue-credential/create-offer",
    responses={
        200: {"model": V10CredentialExchange, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Create a credential offer, independent of any proposal or connection",
)
async def issue_credential_create_offer_post(
    request: Request,
    body: V10CredentialConnFreeOfferRequest = Body(None, description=""),
) -> V10CredentialExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/issue-credential/create",
    responses={
        200: {"model": V10CredentialExchange, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Send holder a credential, automating entire flow",
)
async def issue_credential_create_post(
    request: Request,
    body: V10CredentialCreate = Body(None, description=""),
) -> V10CredentialExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.delete(
    "/issue-credential/records/{cred_ex_id}",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Remove an existing credential exchange record",
)
async def issue_credential_records_cred_ex_id_delete(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/issue-credential/records/{cred_ex_id}",
    responses={
        200: {"model": V10CredentialExchange, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Fetch a single credential exchange record",
)
async def issue_credential_records_cred_ex_id_get(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
) -> V10CredentialExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/issue-credential/records/{cred_ex_id}/issue",
    responses={
        200: {"model": V10CredentialExchange, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Send holder a credential",
)
async def issue_credential_records_cred_ex_id_issue_post(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: V10CredentialIssueRequest = Body(None, description=""),
) -> V10CredentialExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/issue-credential/records/{cred_ex_id}/problem-report",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Send a problem report for credential exchange",
)
async def issue_credential_records_cred_ex_id_problem_report_post(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: V10CredentialProblemReportRequest = Body(None, description=""),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/issue-credential/records/{cred_ex_id}/send-offer",
    responses={
        200: {"model": V10CredentialExchange, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Send holder a credential offer in reference to a proposal with preview",
)
async def issue_credential_records_cred_ex_id_send_offer_post(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: V10CredentialBoundOfferRequest = Body(None, description=""),
) -> V10CredentialExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/issue-credential/records/{cred_ex_id}/send-request",
    responses={
        200: {"model": V10CredentialExchange, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Send issuer a credential request",
)
async def issue_credential_records_cred_ex_id_send_request_post(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
) -> V10CredentialExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/issue-credential/records/{cred_ex_id}/store",
    responses={
        200: {"model": V10CredentialExchange, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Store a received credential",
)
async def issue_credential_records_cred_ex_id_store_post(
    request: Request,
    cred_ex_id: str = Path(
        None,
        description="Credential exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: V10CredentialStoreRequest = Body(None, description=""),
) -> V10CredentialExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/issue-credential/records",
    responses={
        200: {"model": V10CredentialExchangeListResult, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Fetch all credential exchange records",
)
async def issue_credential_records_get(
    request: Request,
    connection_id: str = Query(None, description="Connection identifier"),
    role: str = Query(None, description="Role assigned in credential exchange"),
    state: str = Query(None, description="Credential exchange state"),
    thread_id: str = Query(None, description="Thread identifier"),
) -> V10CredentialExchangeListResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/issue-credential/send-offer",
    responses={
        200: {"model": V10CredentialExchange, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Send holder a credential offer, independent of any proposal",
)
async def issue_credential_send_offer_post(
    request: Request,
    body: V10CredentialFreeOfferRequest = Body(None, description=""),
) -> V10CredentialExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/issue-credential/send",
    responses={
        200: {"model": V10CredentialExchange, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Send holder a credential, automating entire flow",
)
async def issue_credential_send_post(
    request: Request,
    body: V10CredentialProposalRequestMand = Body(None, description=""),
) -> V10CredentialExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/issue-credential/send-proposal",
    responses={
        200: {"model": V10CredentialExchange, "description": ""},
    },
    tags=["issue-credential v1.0"],
    summary="Send issuer a credential proposal",
)
async def issue_credential_send_proposal_post(
    request: Request,
    body: V10CredentialProposalRequestOpt = Body(None, description=""),
) -> V10CredentialExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
