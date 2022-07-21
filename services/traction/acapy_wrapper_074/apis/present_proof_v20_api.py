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
from acapy_wrapper_074.models.indy_cred_precis import IndyCredPrecis
from acapy_wrapper_074.models.v20_pres_create_request_request import (
    V20PresCreateRequestRequest,
)
from acapy_wrapper_074.models.v20_pres_ex_record import V20PresExRecord
from acapy_wrapper_074.models.v20_pres_ex_record_list import V20PresExRecordList
from acapy_wrapper_074.models.v20_pres_problem_report_request import (
    V20PresProblemReportRequest,
)
from acapy_wrapper_074.models.v20_pres_proposal_request import V20PresProposalRequest
from acapy_wrapper_074.models.v20_pres_send_request_request import (
    V20PresSendRequestRequest,
)
from acapy_wrapper_074.models.v20_pres_spec_by_format_request import (
    V20PresSpecByFormatRequest,
)
from acapy_wrapper_074.models.v20_presentation_send_request_to_proposal import (
    V20PresentationSendRequestToProposal,
)

from api import acapy_utils as au

router = APIRouter()


@router.post(
    "/present-proof-2.0/create-request",
    responses={
        200: {"model": V20PresExRecord, "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Creates a presentation request not bound to any proposal or connection",
    response_model_by_alias=True,
)
async def present_proof20_create_request_post(
    request: Request,
    body: V20PresCreateRequestRequest = Body(None, description=""),
) -> V20PresExRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/present-proof-2.0/records",
    responses={
        200: {"model": V20PresExRecordList, "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Fetch all present-proof exchange records",
    response_model_by_alias=True,
)
async def present_proof20_records_get(
    request: Request,
    connection_id: str = Query(None, description="Connection identifier"),
    role: str = Query(None, description="Role assigned in presentation exchange"),
    state: str = Query(None, description="Presentation exchange state"),
    thread_id: str = Query(None, description="Thread identifier"),
) -> V20PresExRecordList:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/present-proof-2.0/records/{pres_ex_id}/credentials",
    responses={
        200: {"model": List[IndyCredPrecis], "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Fetch credentials from wallet for presentation request",
    response_model_by_alias=True,
)
async def present_proof20_records_pres_ex_id_credentials_get(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
    count: str = Query(
        None, description="Maximum number to retrieve", regex=r"^[1-9][0-9]*$"
    ),
    extra_query: str = Query(
        None, description="(JSON) object mapping referents to extra WQL queries"
    ),
    referent: str = Query(
        None, description="Proof request referents of interest, comma-separated"
    ),
    start: str = Query(None, description="Start index", regex=r"^[0-9]*$"),
) -> List[IndyCredPrecis]:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.delete(
    "/present-proof-2.0/records/{pres_ex_id}",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Remove an existing presentation exchange record",
    response_model_by_alias=True,
)
async def present_proof20_records_pres_ex_id_delete(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/present-proof-2.0/records/{pres_ex_id}",
    responses={
        200: {"model": V20PresExRecord, "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Fetch a single presentation exchange record",
    response_model_by_alias=True,
)
async def present_proof20_records_pres_ex_id_get(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
) -> V20PresExRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof-2.0/records/{pres_ex_id}/problem-report",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Send a problem report for presentation exchange",
    response_model_by_alias=True,
)
async def present_proof20_records_pres_ex_id_problem_report_post(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
    body: V20PresProblemReportRequest = Body(None, description=""),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof-2.0/records/{pres_ex_id}/send-presentation",
    responses={
        200: {"model": V20PresExRecord, "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Sends a proof presentation",
    response_model_by_alias=True,
)
async def present_proof20_records_pres_ex_id_send_presentation_post(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
    body: V20PresSpecByFormatRequest = Body(None, description=""),
) -> V20PresExRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof-2.0/records/{pres_ex_id}/send-request",
    responses={
        200: {"model": V20PresExRecord, "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Sends a presentation request in reference to a proposal",
    response_model_by_alias=True,
)
async def present_proof20_records_pres_ex_id_send_request_post(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
    body: V20PresentationSendRequestToProposal = Body(None, description=""),
) -> V20PresExRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof-2.0/records/{pres_ex_id}/verify-presentation",
    responses={
        200: {"model": V20PresExRecord, "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Verify a received presentation",
    response_model_by_alias=True,
)
async def present_proof20_records_pres_ex_id_verify_presentation_post(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
) -> V20PresExRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof-2.0/send-proposal",
    responses={
        200: {"model": V20PresExRecord, "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Sends a presentation proposal",
    response_model_by_alias=True,
)
async def present_proof20_send_proposal_post(
    request: Request,
    body: V20PresProposalRequest = Body(None, description=""),
) -> V20PresExRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof-2.0/send-request",
    responses={
        200: {"model": V20PresExRecord, "description": ""},
    },
    tags=["present-proof v2.0"],
    summary="Sends a free presentation request not bound to any proposal",
    response_model_by_alias=True,
)
async def present_proof20_send_request_post(
    request: Request,
    body: V20PresSendRequestRequest = Body(None, description=""),
) -> V20PresExRecord:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
