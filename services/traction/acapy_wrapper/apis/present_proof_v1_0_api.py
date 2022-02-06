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
from acapy_wrapper.models.admin_api_message_tracing import AdminAPIMessageTracing
from acapy_wrapper.models.indy_cred_precis import IndyCredPrecis
from acapy_wrapper.models.indy_pres_spec import IndyPresSpec
from acapy_wrapper.models.v10_presentation_create_request_request import (
    V10PresentationCreateRequestRequest,
)
from acapy_wrapper.models.v10_presentation_exchange import V10PresentationExchange
from acapy_wrapper.models.v10_presentation_exchange_list import (
    V10PresentationExchangeList,
)
from acapy_wrapper.models.v10_presentation_problem_report_request import (
    V10PresentationProblemReportRequest,
)
from acapy_wrapper.models.v10_presentation_proposal_request import (
    V10PresentationProposalRequest,
)
from acapy_wrapper.models.v10_presentation_send_request_request import (
    V10PresentationSendRequestRequest,
)
from acapy_wrapper.security_api import get_token_AuthorizationHeader

from api import acapy_utils as au


router = APIRouter()


@router.post(
    "/present-proof/create-request",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Creates a presentation request not bound to any proposal or connection",
)
async def present_proof_create_request_post(
    request: Request,
    body: V10PresentationCreateRequestRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V10PresentationExchange:
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
    "/present-proof/records",
    responses={
        200: {"model": V10PresentationExchangeList, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Fetch all present-proof exchange records",
)
async def present_proof_records_get(
    request: Request,
    connection_id: str = Query(None, description="Connection identifier"),
    role: str = Query(None, description="Role assigned in presentation exchange"),
    state: str = Query(None, description="Presentation exchange state"),
    thread_id: str = Query(None, description="Thread identifier"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V10PresentationExchangeList:
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
    "/present-proof/records/{pres_ex_id}/credentials",
    responses={
        200: {"model": List[IndyCredPrecis], "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Fetch credentials for a presentation request from wallet",
)
async def present_proof_records_pres_ex_id_credentials_get(
    request: Request,
    pres_ex_id: str = Path(
        None,
        description="Presentation exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    count: str = Query(
        None, description="Maximum number to retrieve", regex=r"^[1-9][0-9]*$"
    ),
    extra_query: str = Query(
        None,
        description="(JSON) dict mapping referents to extra WQL queries",
        regex=r"^{\s*&quot;.*?&quot;\s*:\s*{.*?}\s*(,\s*&quot;.*?&quot;\s*:\s*{.*?}\s*)*\s*}$",
    ),
    referent: str = Query(
        None, description="Proof request referents of interest, comma-separated"
    ),
    start: str = Query(None, description="Start index", regex=r"^[0-9]*$"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> List[IndyCredPrecis]:
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
    "/present-proof/records/{pres_ex_id}",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Remove an existing presentation exchange record",
)
async def present_proof_records_pres_ex_id_delete(
    request: Request,
    pres_ex_id: str = Path(
        None,
        description="Presentation exchange identifier",
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
    "/present-proof/records/{pres_ex_id}",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Fetch a single presentation exchange record",
)
async def present_proof_records_pres_ex_id_get(
    request: Request,
    pres_ex_id: str = Path(
        None,
        description="Presentation exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V10PresentationExchange:
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
    "/present-proof/records/{pres_ex_id}/problem-report",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Send a problem report for presentation exchange",
)
async def present_proof_records_pres_ex_id_problem_report_post(
    request: Request,
    pres_ex_id: str = Path(
        None,
        description="Presentation exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: V10PresentationProblemReportRequest = Body(None, description=""),
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
    "/present-proof/records/{pres_ex_id}/send-presentation",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Sends a proof presentation",
)
async def present_proof_records_pres_ex_id_send_presentation_post(
    request: Request,
    pres_ex_id: str = Path(
        None,
        description="Presentation exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: IndyPresSpec = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V10PresentationExchange:
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
    "/present-proof/records/{pres_ex_id}/send-request",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Sends a presentation request in reference to a proposal",
)
async def present_proof_records_pres_ex_id_send_request_post(
    request: Request,
    pres_ex_id: str = Path(
        None,
        description="Presentation exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    body: AdminAPIMessageTracing = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V10PresentationExchange:
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
    "/present-proof/records/{pres_ex_id}/verify-presentation",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Verify a received presentation",
)
async def present_proof_records_pres_ex_id_verify_presentation_post(
    request: Request,
    pres_ex_id: str = Path(
        None,
        description="Presentation exchange identifier",
        regex=r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V10PresentationExchange:
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
    "/present-proof/send-proposal",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Sends a presentation proposal",
)
async def present_proof_send_proposal_post(
    request: Request,
    body: V10PresentationProposalRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V10PresentationExchange:
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
    "/present-proof/send-request",
    responses={
        200: {"model": V10PresentationExchange, "description": ""},
    },
    tags=["present-proof v1.0"],
    summary="Sends a free presentation request not bound to any proposal",
)
async def present_proof_send_request_post(
    request: Request,
    body: V10PresentationSendRequestRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> V10PresentationExchange:
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
