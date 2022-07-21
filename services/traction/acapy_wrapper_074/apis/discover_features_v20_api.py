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
from acapy_wrapper_074.models.v20_discovery_exchange_list_result import (
    V20DiscoveryExchangeListResult,
)
from acapy_wrapper_074.models.v20_discovery_exchange_result import (
    V20DiscoveryExchangeResult,
)

from api import acapy_utils as au

router = APIRouter()


@router.get(
    "/discover-features-2.0/queries",
    responses={
        200: {"model": V20DiscoveryExchangeResult, "description": ""},
    },
    tags=["discover-features v2.0"],
    summary="Query supported features",
    response_model_by_alias=True,
)
async def discover_features20_queries_get(
    request: Request,
    connection_id: str = Query(
        None,
        description="Connection identifier, if none specified, then the query will provide features for this agent.",
    ),
    query_goal_code: str = Query(None, description="Goal-code feature-type query"),
    query_protocol: str = Query(None, description="Protocol feature-type query"),
) -> V20DiscoveryExchangeResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text


@router.get(
    "/discover-features-2.0/records",
    responses={
        200: {"model": V20DiscoveryExchangeListResult, "description": ""},
    },
    tags=["discover-features v2.0"],
    summary="Discover Features v2.0 records",
    response_model_by_alias=True,
)
async def discover_features20_records_get(
    request: Request,
    connection_id: str = Query(None, description="Connection identifier"),
) -> V20DiscoveryExchangeListResult:
    resp_text = await au.acapy_admin_request_from_request(request)
    return resp_text
