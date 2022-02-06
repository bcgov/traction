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
from acapy_wrapper.models.attribute_mime_types_result import AttributeMimeTypesResult
from acapy_wrapper.models.cred_info_list import CredInfoList
from acapy_wrapper.models.cred_revoked_result import CredRevokedResult
from acapy_wrapper.models.indy_cred_info import IndyCredInfo
from acapy_wrapper.models.vc_record import VCRecord
from acapy_wrapper.models.vc_record_list import VCRecordList
from acapy_wrapper.models.w3_c_credentials_list_request import W3CCredentialsListRequest
from acapy_wrapper.security_api import get_token_AuthorizationHeader

from api import acapy_utils as au


router = APIRouter()


@router.delete(
    "/credential/{credential_id}",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["credentials"],
    summary="Remove credential from wallet by id",
)
async def credential_credential_id_delete(
    request: Request,
    credential_id: str = Path(None, description="Credential identifier"),
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
    "/credential/{credential_id}",
    responses={
        200: {"model": IndyCredInfo, "description": ""},
    },
    tags=["credentials"],
    summary="Fetch credential from wallet by id",
)
async def credential_credential_id_get(
    request: Request,
    credential_id: str = Path(None, description="Credential identifier"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> IndyCredInfo:
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
    "/credential/mime-types/{credential_id}",
    responses={
        200: {"model": AttributeMimeTypesResult, "description": ""},
    },
    tags=["credentials"],
    summary="Get attribute MIME types from wallet",
)
async def credential_mime_types_credential_id_get(
    request: Request,
    credential_id: str = Path(None, description="Credential identifier"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> AttributeMimeTypesResult:
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
    "/credential/revoked/{credential_id}",
    responses={
        200: {"model": CredRevokedResult, "description": ""},
    },
    tags=["credentials"],
    summary="Query credential revocation status by id",
)
async def credential_revoked_credential_id_get(
    request: Request,
    credential_id: str = Path(None, description="Credential identifier"),
    _from: str = Query(
        None,
        description="Earliest epoch of revocation status interval of interest",
        regex=r"^[0-9]*$",
    ),
    to: str = Query(
        None,
        description="Latest epoch of revocation status interval of interest",
        regex=r"^[0-9]*$",
    ),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> CredRevokedResult:
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
    "/credential/w3c/{credential_id}",
    responses={
        200: {"model": dict, "description": ""},
    },
    tags=["credentials"],
    summary="Remove W3C credential from wallet by id",
)
async def credential_w3c_credential_id_delete(
    request: Request,
    credential_id: str = Path(None, description="Credential identifier"),
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
    "/credential/w3c/{credential_id}",
    responses={
        200: {"model": VCRecord, "description": ""},
    },
    tags=["credentials"],
    summary="Fetch W3C credential from wallet by id",
)
async def credential_w3c_credential_id_get(
    request: Request,
    credential_id: str = Path(None, description="Credential identifier"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> VCRecord:
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
    "/credentials",
    responses={
        200: {"model": CredInfoList, "description": ""},
    },
    tags=["credentials"],
    summary="Fetch credentials from wallet",
)
async def credentials_get(
    request: Request,
    count: str = Query(
        None, description="Maximum number to retrieve", regex=r"^[1-9][0-9]*$"
    ),
    start: str = Query(None, description="Start index", regex=r"^[0-9]*$"),
    wql: str = Query(None, description="(JSON) WQL query", regex=r"^{.*}$"),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> CredInfoList:
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
    "/credentials/w3c",
    responses={
        200: {"model": VCRecordList, "description": ""},
    },
    tags=["credentials"],
    summary="Fetch W3C credentials from wallet",
)
async def credentials_w3c_post(
    request: Request,
    count: str = Query(
        None, description="Maximum number to retrieve", regex=r"^[1-9][0-9]*$"
    ),
    start: str = Query(None, description="Start index", regex=r"^[0-9]*$"),
    wql: str = Query(None, description="(JSON) WQL query", regex=r"^{.*}$"),
    body: W3CCredentialsListRequest = Body(None, description=""),
    token_AuthorizationHeader: TokenModel = Security(get_token_AuthorizationHeader),
) -> VCRecordList:
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
