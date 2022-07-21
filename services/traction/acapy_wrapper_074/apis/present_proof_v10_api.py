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
from acapy_wrapper_074.models.indy_pres_spec import IndyPresSpec
from acapy_wrapper_074.models.v10_presentation_create_request_request import (
    V10PresentationCreateRequestRequest,
)
from acapy_wrapper_074.models.v10_presentation_exchange import V10PresentationExchange
from acapy_wrapper_074.models.v10_presentation_exchange_list import (
    V10PresentationExchangeList,
)
from acapy_wrapper_074.models.v10_presentation_problem_report_request import (
    V10PresentationProblemReportRequest,
)
from acapy_wrapper_074.models.v10_presentation_proposal_request import (
    V10PresentationProposalRequest,
)
from acapy_wrapper_074.models.v10_presentation_send_request_request import (
    V10PresentationSendRequestRequest,
)
from acapy_wrapper_074.models.v10_presentation_send_request_to_proposal import (
    V10PresentationSendRequestToProposal,
)

from api import acapy_utils as au

router = APIRouter()


@router.post(
    "/present-proof/create-request",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Creates a presentation request not bound to any proposal or connection",
    response_model_by_alias=True,
)
async def present_proof_create_request_post(
    request: Request,
    body: V10PresentationCreateRequestRequest = Body(None, description=""),
) -> V10PresentationExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/present-proof/records",
    responses={
        200: {"model": V10PresentationExchangeList, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Fetch all present-proof exchange records",
    response_model_by_alias=True,
)
async def present_proof_records_get(
    request: Request,
    connection_id: str = Query(None, description="Connection identifier"),
    role: str = Query(None, description="Role assigned in presentation exchange"),
    state: str = Query(None, description="Presentation exchange state"),
    thread_id: str = Query(None, description="Thread identifier"),
) -> V10PresentationExchangeList:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/present-proof/records/{pres_ex_id}/credentials",
    responses={
        200: {"model": List[IndyCredPrecis], "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Fetch credentials for a presentation request from wallet",
    response_model_by_alias=True,
)
async def present_proof_records_pres_ex_id_credentials_get(
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
    "/present-proof/records/{pres_ex_id}",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Remove an existing presentation exchange record",
    response_model_by_alias=True,
)
async def present_proof_records_pres_ex_id_delete(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/present-proof/records/{pres_ex_id}",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Fetch a single presentation exchange record",
    response_model_by_alias=True,
)
async def present_proof_records_pres_ex_id_get(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
) -> V10PresentationExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof/records/{pres_ex_id}/problem-report",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Send a problem report for presentation exchange",
    response_model_by_alias=True,
)
async def present_proof_records_pres_ex_id_problem_report_post(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
    body: V10PresentationProblemReportRequest = Body(None, description=""),
) -> dict:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof/records/{pres_ex_id}/send-presentation",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Sends a proof presentation",
    response_model_by_alias=True,
)
async def present_proof_records_pres_ex_id_send_presentation_post(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
    body: IndyPresSpec = Body(None, description=""),
) -> V10PresentationExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof/records/{pres_ex_id}/send-request",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Sends a presentation request in reference to a proposal",
    response_model_by_alias=True,
)
async def present_proof_records_pres_ex_id_send_request_post(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
    body: V10PresentationSendRequestToProposal = Body(None, description=""),
) -> V10PresentationExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof/records/{pres_ex_id}/verify-presentation",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Verify a received presentation",
    response_model_by_alias=True,
)
async def present_proof_records_pres_ex_id_verify_presentation_post(
    request: Request,
    pres_ex_id: str = Path(None, description="Presentation exchange identifier"),
) -> V10PresentationExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof/send-proposal",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Sends a presentation proposal",
    response_model_by_alias=True,
)
async def present_proof_send_proposal_post(
    request: Request,
    body: V10PresentationProposalRequest = Body(None, description=""),
) -> V10PresentationExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.post(
    "/present-proof/send-request",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Sends a free presentation request not bound to any proposal",
    response_model_by_alias=True,
)
async def present_proof_send_request_post(
    request: Request,
    body: V10PresentationSendRequestRequest = Body(None, description=""),
) -> V10PresentationExchange:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
