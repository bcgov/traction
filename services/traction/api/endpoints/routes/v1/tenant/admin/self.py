import logging

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from api.endpoints.dependencies.tenant_security import get_from_context

from api.endpoints.models.v1.tenant import TenantGetResponse
from api.services.v1 import tenant_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{self}", status_code=status.HTTP_200_OK, response_model=TenantGetResponse)
async def get_tenant(
    request: Request,
) -> TenantGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await tenant_service.get_tenant(
        tenant_id,
        wallet_id,
    )

    links = []  # TODO: determine useful links for /self

    return TenantGetResponse(item=item, links=links)
