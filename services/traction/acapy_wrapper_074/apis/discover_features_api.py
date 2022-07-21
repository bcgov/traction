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
from acapy_wrapper_074.models.v10_discovery_exchange_list_result import (
    V10DiscoveryExchangeListResult,
)
from acapy_wrapper_074.models.v10_discovery_exchange_result import (
    V10DiscoveryExchangeResult,
)

from api import acapy_utils as au

router = APIRouter()


@router.get(
    "/discover-features/query",
    responses={
        200: {"model": V10DiscoveryExchangeResult, "description": ""},
    },
    tags=["discover-features"],
    summary="Query supported features",
    response_model_by_alias=True,
)
async def discover_features_query_get(
    request: Request,
    comment: str = Query(None, description="Comment"),
    connection_id: str = Query(
        None,
        description="Connection identifier, if none specified, then the query will provide features for this agent.",
    ),
    query: str = Query(None, description="Protocol feature query"),
) -> V10DiscoveryExchangeResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/discover-features/records",
    responses={
        200: {"model": V10DiscoveryExchangeListResult, "description": ""},
    },
    tags=["discover-features"],
    summary="Discover Features records",
    response_model_by_alias=True,
)
async def discover_features_records_get(
    request: Request,
    connection_id: str = Query(None, description="Connection identifier"),
) -> V10DiscoveryExchangeListResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
